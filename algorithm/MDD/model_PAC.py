import argparse
import torch.nn.functional as F
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch
from torch import nn
from torch.nn.parameter import Parameter
from numpy import pad
import torch
import math


class eca_layer(nn.Module):
    """Constructs a ECA module.

    Args:
        channel: Number of channels of the input feature map
        k_size: Adaptive selection of kernel size
    """

    def __init__(self, channel, k_size=3):
        super(eca_layer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=k_size, padding=(k_size - 1) // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # feature descriptor on the global spatial information
        y = self.avg_pool(x)
        # Two different branches of ECA module
        y = self.conv(y.squeeze(-1).transpose(-1, -2)).transpose(-1, -2).unsqueeze(-1)
        # Multi-scale information fusion
        y = self.sigmoid(y)
        return x * y.expand_as(x)




"""
    ECA注意力机制，和SE注意力主要的区别是避免降维，减少了参数数量的增加。
    提出了一种自适应卷积核的1D卷积。在通道之间进行信息交互，获取信息。

    步骤：全局平均池化-》1D卷积-》Sigmoid激活-》输出
    # model = ECA(8)
    # model = model.cuda()
    # input = torch.randn(1, 8, 12, 12).cuda()
    # output = model(input)
    # print(output.shape)  # (1, 8, 12, 12)
"""
class ECA(nn.Module):
    def __init__(self, channel, gamma=2, b=1):
        super(ECA, self).__init__()
        # 计算卷积核大小
        kernel_size = int(abs((math.log(channel, 2) + b) / gamma))
        kernel_size = kernel_size if kernel_size % 2 else kernel_size + 1
        # 计算padding
        padding = kernel_size // 2
        self.avg = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(
            1, 1, kernel_size=kernel_size, padding=padding, bias=False
        )
        self.sig = nn.Sigmoid()

    def forward(self, x):
        b, c, h, w = x.size()
        y = self.avg(x).view([b, 1, c])  # avg后：(1,16,1,1)   view后：(1,1,16)
        y = self.conv(y)   # conv后：(1,1,16)
        y = self.sig(y).view([b, c, 1, 1])
        out = x * y
        return out, y.squeeze()

def data_normal(orign_data):
    d_min = orign_data.min()
    if d_min < 0:
        orign_data+=torch.abs(d_min)
        d_min = orign_data.min()
    d_max=orign_data.max()
    dst=d_max-d_min
    norm_data=(orign_data-d_min).true_divide(dst)
    return norm_data



class connect_attention(nn.Module):
    def __init__(self, num_inputs, score_limit, kernel_size):
        super(connect_attention, self).__init__()

        self.num_inputs = num_inputs
        self.score_limit = int(score_limit * num_inputs)
        self.attention = nn.Linear(num_inputs, num_inputs)
        self.kernel_size = kernel_size
        self.kernel_size = self.kernel_size if self.kernel_size % 2 else self.kernel_size + 1
        # 计算padding
        padding = self.kernel_size // 2
        self.conv = nn.Conv1d(
            1, 1, kernel_size=self.kernel_size, padding=padding, bias=False
        )
        self.sig = nn.Sigmoid()

    def forward(self, x):
        # x shape (batch_size,length)

        y=x.view(1,1,128*128)
        # y = x.view(1, 1, 68 * 68)

        #y=x.view(1,1,21*21)
        y=self.conv(y).squeeze()
        attention_score=self.sig(y)
        # attention_score = torch.softmax(self.attention(x), dim=0)
        attention_index = torch.argsort(attention_score)  # 从小到大
        #print("after score")
        new_x = torch.zeros_like(x)
        # simple_score = attention_score[attention_index[:self.score_limit]]
        simple_score = attention_score[attention_index[:self.score_limit]] + 1
        new_x[attention_index[:self.score_limit]] = x[attention_index[:self.score_limit]] * simple_score
        new_x[attention_index[self.score_limit:]] = 0
        return new_x, attention_score

class connect_attention2(nn.Module):
    def __init__(self, num_inputs, score_limit, kernel_size):
        super(connect_attention2, self).__init__()

        self.num_inputs = num_inputs
        self.limit_num = int(score_limit * num_inputs)
        self.attention = nn.Linear(num_inputs, num_inputs)
        self.kernel_size = kernel_size
        self.kernel_size = self.kernel_size if self.kernel_size % 2 else self.kernel_size + 1
        # 计算padding
        padding = self.kernel_size // 2
        self.conv = nn.Conv1d(
            1, 1, kernel_size=self.kernel_size, padding=padding, bias=False
        )
        self.sig = nn.Sigmoid()

    def forward(self, x):
        # x shape (batch_size,length)

        y=x.view(1,1,128*128)
        # y = x.view(1, 1, 68 * 68)
        # y = x.view(1, 1, 22 * 22)

        # y=x.view(1,1,21*21)
        y=self.conv(y).squeeze()
        attention_score=self.sig(y)
        # attention_score = torch.softmax(self.attention(x), dim=0)
        attention_index = torch.argsort(attention_score)  # 从小到大排列
        #print("after score")
        new_x = torch.zeros_like(x)
        baoliuindex=attention_index[-self.limit_num:]
        baoliu_score = attention_score[baoliuindex] + 1
        new_x[baoliuindex]=x[baoliuindex]*baoliu_score
        return new_x, attention_score


class EcaSparseAttention(nn.Module):
    def __init__(self, nclasses, cross_band_num, channel_num,  attention_lim, dropout):
        """Dense version of GAT."""
        super(EcaSparseAttention, self).__init__()
        self.dropout=dropout
        self.eca = ECA(cross_band_num)
        self.attention1 = connect_attention2(channel_num * channel_num, attention_lim, kernel_size=2)
        self.attention2 = connect_attention2(channel_num * channel_num, attention_lim, kernel_size=6)
        self.attention3 = connect_attention2(channel_num * channel_num, attention_lim, kernel_size=12)
        # 池化   (128,133)   经过(2,2)的池化后为(64,66)
        #                   经过(3,3)的池化后为(42,44)
        # self.pool = nn.AdaptiveAvgPool2d((64, 9))
        self.fc_encoder = nn.Sequential(

            nn.Linear(16384, 6000),#原始
            # nn.Linear(4624, 6000),#溯源
            # nn.Linear(484, 242),#BCI2a

            # nn.Linear(441, 6000),
            nn.Linear(6000, 4914)#溯源
            # nn.Linear(242, 121)#BCI2a
        )
        # self.fc_encoder = nn.Sequential(
        #     nn.Linear(16384, 8000)
        # )

        self.connect1 = nn.Linear(in_features=4914*1, out_features=32, bias=False)#溯源
        # self.connect1 = nn.Linear(in_features=121*1, out_features=32, bias=False)#BCI2a
        self.connect2 = nn.Linear(in_features=32, out_features=nclasses, bias=False)

        # self.r1 = nn.ReLU()
        # self.r1 = nn.Sigmoid()
        # self.d1 = nn.Dropout(self.dropout1)
        # self.rt1 = nn.ReLU()

    def forward(self, adj):
        # adj:(batchsize,low,high,128,128)
        result_list = []
        # arr = np.ones((128, 128))
        # arr_ind = np.triu_indices_from(arr, 1)
        out_list = []
        band_attention_list=[]
        att_list1 = []
        att_list2 = []
        att_list3 = []
        for i in range(adj.shape[0]):
            att_list = []
            # y = F.dropout(x[i, :, :], self.dropout1, training=self.training)
            # 1.细分 adj:(batchsize,low,high,128,128)
            y = adj[i, :, :, :, :]
            y = y.view(1, y.size(0)*y.size(1), y.size(2), y.size(3))  # (1,low*high,128,128)

            # # 2.不细分 adj:(batchsize,low,128,128)
            # y = adj[i, :, :, :]
            # y = y.view(1, y.size(0) , y.size(1), y.size(2))  # (1,low*high,128,128)

            y = F.dropout(y, self.dropout, training=self.training)
            # 频带注意力
            y, band_attention = self.eca(y)                              # 输出：(1,low*high,128,128)
            band_attention_list.append(band_attention)
            y = y.sum(axis=1)                                         # 第二维相加
            y = y.squeeze(dim=0)                                    # 输出 (128,128)
            # 归一化
            y = data_normal(y)
            # 稀疏编码1
            # y1, attention_score1 = self.attention1(y.view(-1))
            # y1 = self.fc_encoder(y1.view(-1))
            # y1 = self.r1(y1)
            # 稀疏编码2
            # y2, attention_score2 = self.attention2(y.view(-1))
            # y2 = self.fc_encoder(y2.view(-1))
            # y2 = self.r1(y2)
            # # 稀疏编码3
            y3, attention_score3 = self.attention3(y.view(-1))
            y3 = self.fc_encoder(y3.view(-1))
            # y3 = self.r1(y3)
            # 拼接
            # y4 = torch.cat((y1,y2,y3),dim=0)
            # y4 = F.dropout(y4, 0.5)
            # 全连接
            y4 = self.connect1(y3)
            y4 = self.connect2(y4)
            out = F.log_softmax(y4, dim=0)
            out_list.append(out)
            # att_list1.append(attention_score1)
            # att_list2.append(attention_score2)
            # att_list3.append(attention_score3)
        result = torch.stack(out_list)
        # att_score1 = torch.stack(att_list1)
        # att_score2 = torch.stack(att_list2)
        # att_score3 = torch.stack(att_list3)
        band_score = torch.stack(band_attention_list)

        return result, band_score
