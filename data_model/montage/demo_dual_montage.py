from typing import List
import numpy as np
from data_model.waveform import WaveformModel
from data_model.axes import ChannelDef
from data_model.montage.base_montage import Montage, MontageBlock

# 定义一个用于处理波形数据块的类
class DemoDualMontageBlock(MontageBlock):

    def __init__(self, waveform: WaveformModel, indices: list[int]):
        # 初始化波形和通道索引
        self._waveform = waveform
        self._indices = indices

    @property
    def num_channels(self):
        # 返回通道数量
        return len(self._indices)

    @property
    def channels(self) -> List[ChannelDef]:
        # 返回指定索引的通道列表
        return [channel for i, channel in enumerate(self._waveform.channels) if i in self._indices]

    def get_standard_slice(self, from_sec: float, to_sec: float, num_points: float) -> np.ndarray:
        # 获取指定时间范围内的标准切片数据，并按通道堆叠
        return np.stack(self._waveform.get_standard_slice(
            from_sec=from_sec, to_sec=to_sec, num_points=num_points, channel_indices=self._indices), axis=1)

# 定义一个用于管理波形数据块的类
class DemoDualMontage(Montage):

    def __init__(self):
        # 初始化时将_blocks设置为None
        self._blocks = None

    def set_waveform(self, waveform: WaveformModel):
        # 确保波形有多个通道
        assert waveform.num_channels > 1
        # 计算通道的中间索引
        mid = waveform.num_channels // 2
        # 将波形分成两部分，并创建两个DemoDualMontageBlock对象
        self._blocks = [
            DemoDualMontageBlock(waveform, list(range(mid))),
            DemoDualMontageBlock(waveform, list(range(mid, waveform.num_channels)))
        ]

    def get_block_counts(self) -> int:
        # 返回块的数量
        return 2

    def get_block_at(self, index: int):
        # 返回指定索引的块
        return self._blocks[index]