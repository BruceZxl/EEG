import abc
from typing import List

import numpy as np

from data_model.waveform import WaveformModel
from data_model.axes import ChannelDef


class MontageBlock(abc.ABC):

    @property
    @abc.abstractmethod
    def num_channels(self): ...

    @property
    @abc.abstractmethod
    def channels(self) -> List[ChannelDef]: ...

    @abc.abstractmethod
    def get_standard_slice(self, from_sec: float, to_sec: float, num_points: float) -> np.ndarray: ...


class Montage(abc.ABC):

    @abc.abstractmethod
    def set_waveform(self, waveform: WaveformModel): ...

    @abc.abstractmethod
    def get_block_counts(self) -> int: ...

    @abc.abstractmethod
    def get_block_at(self, index: int) -> MontageBlock: ...
