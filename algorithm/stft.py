from algorithm import base
from scipy import signal

from algorithm.base import BaseAlgorithm
from data_model.axes.axis import Axis
from typing import Tuple, Optional
from data_model.axes.time_axis import TimeAxis
from data_model.tensor import Tensor


class stft(BaseAlgorithm):


    """x： STFT变换的时域信号
    fs： 时域信号的采样频率
    window： 时域信号分割需要的窗函数，可以自定义窗函数（但是这个方面没有尝试，需要自定义的话请自己尝试）
    nperseg： 窗函数长度
    noverlap： 窗函数重叠数，默认为50%。
    nfft： FFT的长度，默认为nperseg。如大于nperseg会自动进行零填充
    return_oneside ： True返回复数实部，None返回复数。
    """
    def is_applicable(shape_def: Tuple[Axis]) -> bool:
        if len(shape_def) == 3:
            return True
        else:
            return False


    def infer_output_shape_def(self, shape_def: Tuple[Axis]) -> Tuple[Axis]:
        pass

    def call(inputs: Tensor):
        time_axis_list = inputs.shape_def[inputs.check_axes(targets=[TimeAxis])[0][0]]
        stft_axes = []
        for time_axis, channel in zip(time_axis_list,inputs.data):
            time_axis: TimeAxis
            (f, t, Zxx) = signal.stft(channel, time_axis.sampling_rate,nperseg=1000)
            stft_axes.append([f, t, Zxx])
        return stft_axes



