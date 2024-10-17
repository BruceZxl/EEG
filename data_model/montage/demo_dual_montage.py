from typing import List

import numpy as np

from data_model.waveform import WaveformModel
from data_model.axes import ChannelDef
from data_model.montage.base_montage import Montage, MontageBlock


class DemoDualMontageBlock(MontageBlock):

    def __init__(self, waveform: WaveformModel, indices: list[int]):
        self._waveform = waveform
        self._indices = indices

    @property
    def num_channels(self):
        return len(self._indices)

    @property
    def channels(self) -> List[ChannelDef]:
        return [channel for i, channel in enumerate(self._waveform.channels) if i in self._indices]

    def get_standard_slice(self, from_sec: float, to_sec: float, num_points: float) -> np.ndarray:
        return np.stack(self._waveform.get_standard_slice(
            from_sec=from_sec, to_sec=to_sec, num_points=num_points, channel_indices=self._indices), axis=1)


class DemoDualMontage(Montage):

    def __init__(self):
        self._blocks = None

    def set_waveform(self, waveform: WaveformModel):
        assert waveform.num_channels > 1
        mid = waveform.num_channels // 2
        self._blocks = [
            DemoDualMontageBlock(waveform, list(range(mid))),
            DemoDualMontageBlock(waveform, list(range(mid, waveform.num_channels)))
        ]

    def get_block_counts(self) -> int:
        return 2

    def get_block_at(self, index: int):
        return self._blocks[index]
