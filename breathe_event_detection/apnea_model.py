import math
import os
# import sys
import pickle
import warnings

import numpy as np

warnings.filterwarnings("ignore")

import time
import random
from typing import *

from scipy.interpolate import splev, splrep

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import PackedSequence
from torch.autograd import Variable

# from contrastive_loss import SupConLoss_clear


def reduce_fn_avg(vals):
    # take average
    return sum(vals) / len(vals)


def reduce_fn_sum(vals):
    # take average
    return sum(vals)


def lr_schedule(epoch, lr):
    if epoch > 70 and (epoch - 1) % 10 == 0:
        lr *= 0.1
    return lr


def weightedSquaredHingeLoss(inp, tar, device, w_1_class=1):
    return torch.sum(torch.mean(
        (torch.max(tar, torch.zeros(inp.shape[1], dtype=torch.float32).to(device)) * (w_1_class - 1) + 1) * torch.max(
            1. - tar * inp, torch.zeros(inp.shape[1], dtype=torch.float32).to(device)) ** 2, dim=-1))


class VariationalDropout(nn.Module):
    def __init__(self, dropout: float, batch_first: Optional[bool] = False):
        super().__init__()
        self.dropout = dropout
        self.batch_first = batch_first

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training or self.dropout <= 0.:
            return x

        is_packed = isinstance(x, PackedSequence)
        if is_packed:
            x, batch_sizes = x
            max_batch_size = int(batch_sizes[0])
        else:
            batch_sizes = None
            max_batch_size = x.size(0)

        # Drop same mask across entire sequence
        if self.batch_first:
            m = x.new_empty(max_batch_size, 1, x.size(2), requires_grad=False).bernoulli_(1 - self.dropout)
        else:
            m = x.new_empty(1, max_batch_size, x.size(2), requires_grad=False).bernoulli_(1 - self.dropout)
        x = x.masked_fill(m == 0, 0) / (1 - self.dropout)

        if is_packed:
            return PackedSequence(x, batch_sizes)
        else:
            return x


class LSTM(nn.LSTM):
    def __init__(self, *args, dropouti: float = 0., dropoutw: float = 0., dropouto: float = 0.,
                 batch_first=True, unit_forget_bias=True, bidirectional=True, **kwargs):
        super().__init__(*args, **kwargs, batch_first=batch_first, bidirectional=bidirectional)
        self.unit_forget_bias = unit_forget_bias
        self.dropoutw = dropoutw
        self.input_drop = VariationalDropout(dropouti, batch_first=batch_first)
        self.output_drop = VariationalDropout(dropouto, batch_first=batch_first)
        self._init_weights()

    def _init_weights(self):
        for name, param in self.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param.data)
            elif "weight_ih" in name:
                nn.init.xavier_uniform_(param.data)
            elif "bias" in name and self.unit_forget_bias:
                nn.init.zeros_(param.data)
                param.data[self.hidden_size:2 * self.hidden_size] = 1

    def _drop_weights(self):
        for name, param in self.named_parameters():
            if "weight_hh" in name:
                getattr(self, name).data = \
                    torch.nn.functional.dropout(param.data, p=self.dropoutw, training=self.training).contiguous()

    def forward(self, input, hx=None):
        self._drop_weights()
        input = self.input_drop(input)
        seq, state = super().forward(input, hx=hx)
        return self.output_drop(seq), state


class TCSConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation, padding):
        super(TCSConv1d, self).__init__()
        self.depthwise = nn.Conv1d(in_channels=in_channels, out_channels=in_channels,
                                   kernel_size=kernel_size, dilation=dilation, padding=padding,
                                   groups=in_channels, bias=False)
        self.pointwise = nn.Conv1d(in_channels, out_channels, kernel_size=(1,), bias=False)

    def forward(self, x):
        x = self.depthwise(x)
        x = self.pointwise(x)
        return x


class SACNN(nn.Module):

    def __init__(self):
        super(SACNN, self).__init__()

        filter_size = 16
        kernel_size_var = 3

        # W:input volume size
        # F:kernel size
        # S:stride
        # P:amount of padding
        # size of output volume = (W-F+2P)/S+1

        # to keep the same size, padding = dilation * (kernel - 1) / 2

        self.skip = TCSConv1d(in_channels=2, out_channels=filter_size, kernel_size=1,
                              dilation=1, padding=int((1 - 1) / 2))

        self.conv_1 = TCSConv1d(in_channels=2, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=1,
                                padding=int((kernel_size_var - 1) / 2))

        self.bn_1 = nn.BatchNorm1d(filter_size)

        self.drop_1 = nn.Dropout2d(0.2)

        self.conv_2 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=2,
                                padding=int(2 * (kernel_size_var - 1) / 2))

        self.bn_2 = nn.BatchNorm1d(filter_size)

        self.drop_2 = nn.Dropout2d(0.2)

        self.conv_3 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=4,
                                padding=int(4 * (kernel_size_var - 1) / 2))

        self.bn_3 = nn.BatchNorm1d(filter_size)

        self.drop_3 = nn.Dropout2d(0.2)

        self.conv_4 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=8,
                                padding=int(8 * (kernel_size_var - 1) / 2))

        self.bn_4 = nn.BatchNorm1d(filter_size)

        self.drop_4 = nn.Dropout2d(0.2)

        self.avgPool_a = nn.AvgPool1d(kernel_size=4)

        self.conv_5 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=1,
                                padding=int((kernel_size_var - 1) / 2))

        self.bn_5 = nn.BatchNorm1d(filter_size)

        self.drop_5 = nn.Dropout2d(0.1)

        self.conv_6 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=3,
                                padding=int(3 * (kernel_size_var - 1) / 2))

        self.bn_6 = nn.BatchNorm1d(filter_size)

        self.drop_6 = nn.Dropout2d(0.1)

        self.conv_7 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=5,
                                padding=int(5 * (kernel_size_var - 1) / 2))

        self.bn_7 = nn.BatchNorm1d(filter_size)

        self.drop_7 = nn.Dropout2d(0.1)

        self.conv_8 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=9,
                                padding=int(9 * (kernel_size_var - 1) / 2))

        self.bn_8 = nn.BatchNorm1d(filter_size)

        self.drop_8 = nn.Dropout2d(0.1)

        self.avgPool_b = nn.AvgPool1d(kernel_size=4)

        self.conv_9 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                kernel_size=kernel_size_var, dilation=1,
                                padding=int((kernel_size_var - 1) / 2))

        self.bn_9 = nn.BatchNorm1d(filter_size)

        self.drop_9 = nn.Dropout2d(0.3)

        self.conv_10 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=3,
                                 padding=int(3 * (kernel_size_var - 1) / 2))

        self.bn_10 = nn.BatchNorm1d(filter_size)

        self.drop_10 = nn.Dropout2d(0.3)

        self.conv_11 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=5,
                                 padding=int(5 * (kernel_size_var - 1) / 2))

        self.bn_11 = nn.BatchNorm1d(filter_size)

        self.drop_11 = nn.Dropout2d(0.3)

        self.conv_12 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=9,
                                 padding=int(9 * (kernel_size_var - 1) / 2))

        self.bn_12 = nn.BatchNorm1d(filter_size)

        self.drop_12 = nn.Dropout2d(0.3)

        self.avgPool_c = nn.AvgPool1d(kernel_size=5)

        self.conv_13 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=1,
                                 padding=int((kernel_size_var - 1) / 2))

        self.bn_13 = nn.BatchNorm1d(filter_size)

        self.drop_13 = nn.Dropout2d(0.3)

        self.conv_14 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=2,
                                 padding=int(2 * (kernel_size_var - 1) / 2))

        self.bn_14 = nn.BatchNorm1d(filter_size)

        self.drop_14 = nn.Dropout2d(0.3)

        self.conv_15 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=4,
                                 padding=int(4 * (kernel_size_var - 1) / 2))

        self.bn_15 = nn.BatchNorm1d(filter_size)

        self.drop_15 = nn.Dropout2d(0.3)

        self.conv_16 = TCSConv1d(in_channels=filter_size, out_channels=filter_size,
                                 kernel_size=kernel_size_var, dilation=8,
                                 padding=int(8 * (kernel_size_var - 1) / 2))

        self.bn_16 = nn.BatchNorm1d(filter_size)

        self.drop_16 = nn.Dropout2d(0.3)

        self.lstm_1 = LSTM(input_size=filter_size, hidden_size=128, num_layers=1, bidirectional=True, batch_first=True,
                           dropouti=0.1)

    def forward(self, x):
        skip_conn = self.skip(x)

        x = self.drop_1(F.relu(self.bn_1(self.conv_1(x))))
        skip_conn = skip_conn.add(x)

        x = self.drop_2(F.relu(self.bn_2(self.conv_2(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_3(F.relu(self.bn_3(self.conv_3(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_4(F.relu(self.bn_4(self.conv_4(skip_conn))))
        skip_conn = skip_conn.add(x)

        skip_conn = self.avgPool_a(skip_conn)

        x = self.drop_5(F.relu(self.bn_5(self.conv_5(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_6(F.relu(self.bn_6(self.conv_6(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_7(F.relu(self.bn_7(self.conv_7(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_8(F.relu(self.bn_8(self.conv_8(skip_conn))))
        skip_conn = skip_conn.add(x)

        skip_conn = self.avgPool_b(skip_conn)

        x = self.drop_9(F.relu(self.bn_9(self.conv_9(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_10(F.relu(self.bn_10(self.conv_10(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_11(F.relu(self.bn_11(self.conv_11(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_12(F.relu(self.bn_12(self.conv_12(skip_conn))))
        skip_conn = skip_conn.add(x)

        skip_conn = self.avgPool_c(skip_conn)

        x = self.drop_13(F.relu(self.bn_13(self.conv_13(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_14(F.relu(self.bn_14(self.conv_14(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_15(F.relu(self.bn_15(self.conv_15(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = self.drop_16(F.relu(self.bn_16(self.conv_16(skip_conn))))
        skip_conn = skip_conn.add(x)

        x = skip_conn.permute(0, 2, 1)

        x, states = self.lstm_1(x)
        x = x[:, -1, :]

        return x


class PositionalEncoding(nn.Module):
    """Implement the PE function."""

    def __init__(self, d_model=2, dropout=0.2, max_len=900):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Compute the positional encodings once in log space.
        pe = torch.zeros(128, max_len, d_model)
        position = torch.arange(0., max_len).unsqueeze(1)
        div_term = torch.exp(((torch.arange(0., d_model) / 2).floor() * 2) * -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position[0::2] * div_term)
        pe[:, 1::2] = torch.cos(position[1::2] * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + Variable(self.pe[:x.size(0), :, :], requires_grad=False)
        return self.dropout(x)


class Apnea_net(nn.Module):

    def __init__(self):
        super(Apnea_net, self).__init__()

        self.SACNN_1 = SACNN()

        self.SACNN_2 = SACNN()

        self.SACNN_3 = SACNN()

        self.position_multi = PositionalEncoding(d_model=3, dropout=0.1, max_len=256)
        encoder_layer_multi = nn.TransformerEncoderLayer(d_model=256, nhead=8, dim_feedforward=256, dropout=0.5,
                                                         batch_first=True)
        # self.transformer_encoder_multi = nn.TransformerEncoder(encoder_layer_multi, num_layers=4)
        self.transformer_encoder_multi = nn.TransformerEncoder(encoder_layer_multi, num_layers=4)

        self.layer_norm = nn.LayerNorm(256 * 3)

        self.fc1 = nn.Sequential(
            nn.Linear(256 * 3, 256),
            nn.ReLU(),
            nn.Dropout(p=0.5)
        )
        self.fc2 = nn.Sequential(
            nn.Linear(256, 2)
        )
        self.s1 = nn.Linear(256, 2)
        self.s2 = nn.Linear(256, 2)
        self.s3 = nn.Linear(256, 2)

    def forward(self, x):
        x1 = x  # 5-minute-long segment

        x2 = x[:, :, 180:720]  # 3-minute-long segment

        x3 = x[:, :, 360:540]  # 1-minute-long segment

        x1 = self.SACNN_1(x1)

        x2 = self.SACNN_2(x2)

        x3 = self.SACNN_3(x3)

        c = torch.cat((x1, x2, x3), 1).contiguous()

        residual = c

        c = c.view(-1, 256, 3)
        c = self.position_multi(c)
        c = c.permute(0, 2, 1)
        c = self.transformer_encoder_multi(c)
        c = c.view(-1, 256 * 3)

        c = self.layer_norm(c + residual)

        c = self.fc1(c)
        c = F.softmax(self.fc2(c))

        return c, x3
