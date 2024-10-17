from typing import cast, List, Optional

import mne
import numpy as np
import pyedflib
from loguru import logger
from mne.io.constants import FIFF
from scipy.interpolate import interp1d

from data_model.axes import BatchAxis
from data_model.axes import ChannelAxis, ChannelDef
from data_model.axes import TimeAxis
from data_model.tensor.pure_tensor import Tensor, PureTensor

mne.set_log_level(False)


class WaveformModel:
    AllChannels = type('AllChannels', (object,), {'__contains__': (lambda self, x: True)})()

    def __init__(self, tensor: Tensor):
        checked_axes = tensor.check_axes(targets=[TimeAxis, ChannelAxis, BatchAxis])
        assert len(checked_axes[0]) == 1 and len(checked_axes[1]) == 1 \
               and len(checked_axes[2]) <= 1 and len(checked_axes[3]) == 0
        self.index_time_axis = checked_axes[0][0]
        self.index_channel_axis = checked_axes[1][0]
        self.index_batch_axis = checked_axes[2][0] if len(checked_axes[2]) == 1 else None
        self._tensor = tensor
        self._seconds = 0
        self.on_data_changed()

    @property
    def tensor(self) -> Optional[Tensor]:
        return self._tensor

    def on_data_changed(self):
        if isinstance(self._tensor, PureTensor):
            time_axis: TimeAxis = self._tensor.shape_def[self.index_time_axis]
            self._seconds = self._tensor.data.shape[self.index_time_axis] / time_axis.sampling_rate
        else:
            assert self.index_channel_axis == 0 and self.index_time_axis == 1
            self._seconds = None
            for time_axis, channel in zip(self._tensor.shape_def[1], self._tensor.data):
                time_axis: TimeAxis
                channel_seconds = len(channel) / time_axis.sampling_rate
                if self._seconds is None:
                    self._seconds = channel_seconds
                else:
                    assert np.isclose(self._seconds, channel_seconds)

    @property
    def seconds(self):
        return self._seconds

    @property
    def channels(self) -> List[ChannelDef]:
        return cast(ChannelAxis, self._tensor.shape_def[self.index_channel_axis]).channels

    @property
    def num_channels(self) -> int:
        return self._tensor.data.shape[self.index_channel_axis] \
            if isinstance(self._tensor, PureTensor) else len(self._tensor.data)

    def get_standard_slice(self, from_sec: float, to_sec: float, num_points: float,
                           channel_indices: Optional[list[int]]) -> list[np.ndarray]:
        time_axes = self.tensor.shape_def[self.index_time_axis]
        channels = self.tensor.data
        if channel_indices is None:
            channel_indices = WaveformModel.AllChannels
        if isinstance(self.tensor, PureTensor):
            channels = channels.transpose([self.index_channel_axis, self.index_time_axis])
            time_axes = [time_axes] * len(channels)
        channels = [self._get_standardized_channel(
            channel, time_axis=time_axis, from_sec=from_sec, to_sec=to_sec,
            num_points=num_points) for i, (channel, time_axis) in
            enumerate(zip(channels, time_axes)) if i in channel_indices]
        num_points = max(len(channel) for channel in channels)
        if num_points == 0:
            return channels
        return [np.pad(channel, (0, num_points - len(channel)), 'edge') for channel in channels]

    @staticmethod
    def _get_standardized_channel(
            data: np.ndarray, time_axis: TimeAxis, from_sec: float,
            to_sec: float, num_points: float) -> np.ndarray:
        from_point, to_point = int(from_sec * time_axis.sampling_rate), int(to_sec * time_axis.sampling_rate)
        data = data[from_point: to_point]
        if len(data) == 0:
            return np.ndarray((0,), dtype=np.float32)
        expected_points = to_point - from_point
        if expected_points > len(data):
            num_points = round(num_points * len(data) / expected_points)
        if len(data) < num_points:
            # Low sampling rate: 0-th order upsampling
            fx = interp1d(np.linspace(0, 1, len(data)), data, kind='zero', axis=0)
            data = fx(np.linspace(0, 1, int(num_points)))
        else:
            # High sampling rate: Time-frequential resampling
            up, down = 1, len(data) / num_points
            # noinspection PyTypeChecker
            data: np.ndarray = mne.filter.resample(data.astype(np.float64), up=up, down=down, axis=0)
        return data
