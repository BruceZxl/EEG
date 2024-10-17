from typing import List

import numpy as np

from data_model.waveform import WaveformModel
from data_model.axes import ChannelDef
from data_model.montage.base_montage import Montage, MontageBlock


class OriginalMontageBlock(MontageBlock):

    def __init__(self, waveform: WaveformModel):
        self._waveform = waveform

    @property
    def num_channels(self):
        return self._waveform.num_channels

    @property
    def channels(self) -> List[ChannelDef]:
        return self._waveform.channels

    def get_standard_slice(self, from_sec: float, to_sec: float, num_points: float) -> np.ndarray:
        return np.stack(self._waveform.get_standard_slice(
            from_sec=from_sec, to_sec=to_sec, num_points=num_points, channel_indices=None), axis=1)


class OriginalMontage(Montage):

    def __init__(self):
        self._block = None

    def set_waveform(self, waveform: WaveformModel):
        self._block = OriginalMontageBlock(waveform)

    def get_block_counts(self) -> int:
        return 1

    def get_block_at(self, index: int):
        return self._block
