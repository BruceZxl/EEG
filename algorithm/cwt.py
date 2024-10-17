import numpy as np
from scipy import signal
from algorithm.base import BaseAlgorithm
from data_model.axes.axis import Axis
from typing import Tuple, Optional
from data_model.axes.time_axis import TimeAxis
from data_model.tensor import Tensor
class cwt(BaseAlgorithm):
    """ 参数：
        data： (N,) 数组
        执行转换的数据。
        wavelet： 函数
        小波函数，它应该有 2 个参数。第一个参数是返回向量将具有的点数 (len(wavelet(length,width)) == length)。第二个是宽度参数，定义小波的大小(例如高斯的标准偏差)。请参阅满足这些要求的 ricker 。
        widths： (M,) 序列
        用于变换的宽度。
        dtype： 数据类型，可选
        所需的输出数据类型。默认为float64如果输出小波是真实的并且complex128如果它很复杂。
        kwargs：
        传递给小波函数的关键字参数。
        返回：
        cwt：(M，N)ndarray
        将具有 (len(widths), len(data)) 的形状。
    """
    def is_applicable(shape_def: Tuple[Axis]) -> bool:
        pass


    def infer_output_shape_def(self, shape_def: Tuple[Axis]) -> Tuple[Axis]:
        pass

    def call(inputs: Tensor):
        time_axis_list = inputs.shape_def[inputs.check_axes(targets=[TimeAxis])[0][0]]
        cwt_axes = []
        for time_axis, channel in zip(time_axis_list, inputs.data):
            time_axis: TimeAxis
            import matplotlib.pyplot as plt
            channel = channel[:1000]
            cwtmatr = signal.cwt(channel,signal.ricker,np.arange(1, 31))
            cwt_axes.append(cwtmatr)
        return cwt_axes