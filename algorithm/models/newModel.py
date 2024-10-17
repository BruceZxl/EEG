import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.signal import stft

########################################################################################

class SELayer(nn.Module):
    def __init__(self, channel, reduction=16):
        super(SELayer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Sigmoid()
        )
    def forward(self, x):
        b, c, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1)
        return x * y.expand_as(x)

class SERN(nn.Module):
    def __init__(self, input_size, output_size):
        super(SERN, self).__init__()
        self.conv1 = nn.Conv1d(input_size, output_size, 1)
        self.bn1 = nn.BatchNorm1d(output_size)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv1d(output_size, output_size, 1)
        self.bn2 = nn.BatchNorm1d(output_size)
        self.se = SELayer(output_size, reduction=16)
        self.downsample = nn.Sequential(
            nn.Conv1d(input_size, output_size, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm1d(output_size),
        )
    def forward(self, x):
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.se(out)
        residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out

# Multi Modal Frequency CNN Attention
class MMFCA(nn.Module):
    def __init__(self, after_se):
        super(MMFCA, self).__init__()
        drate = 0.5
        size = 64
        self.eog = nn.Sequential(
            nn.Conv2d(1, size, kernel_size=8, stride=3, bias=False, padding=4),
            nn.BatchNorm2d(size),
            nn.GELU(),
            nn.MaxPool2d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv2d(size, size * 2, kernel_size=7, stride=2, bias=False, padding=3),
            nn.BatchNorm2d(size * 2),
            nn.GELU(),

            nn.Conv2d(size * 2, size * 2, kernel_size=7, stride=1, bias=False, padding=3),
            nn.BatchNorm2d(size * 2),
            nn.GELU(),

            nn.MaxPool2d(kernel_size=2, stride=2, padding=1)
        )
        self.eeg10 = nn.Sequential(
            nn.Conv1d(1, size, kernel_size=10, stride=4, bias=False, padding=5),
            nn.BatchNorm1d(size),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv1d(size, size * 2, kernel_size=7, stride=3, bias=False, padding=3),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv1d(size * 2, size * 2, kernel_size=7, stride=3, bias=False, padding=3),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=2, stride=2, padding=1)
        )

        self.eeg1 = nn.Sequential(
            nn.Conv1d(1, size, kernel_size=100, stride=12, bias=False, padding=50),
            nn.BatchNorm1d(size),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv1d(size, size * 2, kernel_size=7, stride=2, bias=False, padding=3),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv1d(size * 2, size * 2, kernel_size=7, stride=1, bias=False, padding=3),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=2, stride=2, padding=1)
        )
        # 2Hz
        self.features1 = nn.Sequential(
            nn.Conv1d(1, size, kernel_size=50, stride=6, bias=False, padding=24),
            nn.BatchNorm1d(size),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=8, stride=2, padding=4),
            nn.Dropout(drate),

            nn.Conv1d(size, size * 2, kernel_size=16, stride=2, bias=False, padding=8),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=2),
            nn.Dropout(drate),

            nn.Conv1d(size * 2, size * 2, kernel_size=12, stride=2, bias=False, padding=6),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=4, stride=4, padding=2)
        )
        # EMG
        self.emg = nn.Sequential(
            nn.Conv1d(1, size, kernel_size=10, stride=3, bias=False, padding=5),
            nn.BatchNorm1d(size),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=8, stride=2, padding=4),
            nn.Dropout(drate),

            nn.Conv1d(size, size * 2, kernel_size=8, stride=3, bias=False, padding=4),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=6, stride=3, padding=3),
            nn.Dropout(drate),

            nn.Conv1d(size * 2, size * 2, kernel_size=8, stride=3, bias=False, padding=4),
            nn.BatchNorm1d(size * 2),
            nn.GELU(),

            nn.MaxPool1d(kernel_size=4, stride=4, padding=2)
        )

        self.dropout = nn.Dropout(drate)
        self.SE = SERN(input_size=128, output_size=after_se)
        # self.SE = SELayer

    def forward(self, x):
        f, t, xo = stft(x[:, 1, :].unsqueeze(1).float().cpu(), fs=100, window='hann', nperseg=100)  # ,noverlap=100
        xo = torch.tensor(np.abs(xo))
        xo = self.eog(xo)
        xo = xo.reshape(xo.shape[0], xo.shape[1], -1)

        xm = self.emg(x[:, 2, :].unsqueeze(1).float())

        xe = x[:, 0, :].unsqueeze(1).float()
        x1 = self.eeg1(xe)
        x2 = self.features1(xe)
        # x0 = self.eeg0(xe)
        # x2 = self.features2(xe)
        x10 = self.eeg10(xe)
        # print("xm:",xm.shape)
        # print("x1:",x1.shape)
        # print("x2:",x2.shape)
        # print("x10:",x10.shape)
        # print("xo:",xo.shape)
        # print('x8:', x8.shape)

        x_concat = torch.cat((x1, x2, x10, xo, xm), dim=2)
        # x_concat = torch.cat((x1, x2, x10), dim=2)
        x_concat = self.dropout(x_concat)

        # print('x_concat:',x_concat.shape)
        x_concat = self.SE(x_concat)
        # print('x_SE:', x_concat.shape)

        return x_concat


class SleepClass(nn.Module):
    def __init__(self):
        super(SleepClass, self).__init__()
        num_classes = 5
        afr_reduced_cnn_size = 30
        d_model = 56
        # d_model = 38
        hidden_size = d_model // 2

        self.mmfca = MMFCA(afr_reduced_cnn_size)
        self.rnn1 = nn.LSTM(d_model, hidden_size, num_layers=2, dropout=0.5, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(d_model * afr_reduced_cnn_size, num_classes)

    def forward(self, x):
        x_feat = self.mmfca(x)
        self.rnn1.flatten_parameters()
        recurrent, _ = self.rnn1(x_feat)
        # print("before lstm:",x_feat.shape)
        # print("after lstm:",recurrent.shape)
        # exit()
        encoded_features = recurrent.contiguous().view(recurrent.shape[0], -1)
        final_output = self.fc(encoded_features)
        return final_output, encoded_features
