import math
import weakref
from functools import lru_cache, cache
from typing import Optional

import numpy as np
import mne
from PySide6 import QtCore
from PySide6.QtCore import QObject, QRectF
from scipy.signal import butter, sosfiltfilt
from scipy import signal
from data_model.montage.base_montage import MontageBlock
from viewmodel.montage_block_viewmodel import MontageBlockViewModel
from viewmodel.waveform_page_viewmodel import WaveformPageViewModel


class WaveformAreaViewModel(QObject):
    scaleChanged = QtCore.Signal()
    canvasInvalidated = QtCore.Signal()
    nopSignal = QtCore.Signal()


    def __init__(self, *, page_viewmodel: WaveformPageViewModel, montage_block: MontageBlock, parent=None):
        super().__init__(parent)
        self._page_viewmodel = weakref.proxy(page_viewmodel)
        self._montage_block = montage_block
        self._scale = 1
        self._user_amplifier: Optional[np.ndarray] = None
        self._render_time = 0
        self._cache_block_seconds = 0

    # noinspection PyTypeChecker,PyCallingNonCallable
    @QtCore.Property(float, notify=scaleChanged)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value: float):
        self._scale = value
        self.scaleChanged.emit()

    # noinspection PyCallingNonCallable
    @QtCore.Property(float)
    def render_time(self):
        return self._render_time

    def record_render_time(self, millis: float):
        self._render_time = self._render_time * .8 + millis * .2

    def reset(self):
        self._scale, secs = 100, self._page_viewmodel.seconds // 2
        lo, hi = (0, secs * 2) if secs <= 50 else (secs - 50, secs + 50)
        self._user_amplifier = self._page_viewmodel.channel_height / 4 / np.array([
            max(channel.mean(), channel.std()) + np.finfo(np.float32).eps
            if len(channel) > 100 else 1
            for channel in self._montage_block.get_standard_slice(lo, hi, 100 * (hi - lo)).T])
        self.canvasInvalidated.emit()

    def get_channel(self):
        x1, x2, y1, y2 = self._page_viewmodel.get_selection()
        time=x2-x1
        channel_index = int(y1 / self._page_viewmodel.channel_height)
        x1, x2 = map(lambda x: x * self._scale, [x1, x2])
        return channel_index, x1, x2,time

    def scroll(self, scroll):
        """ (Horizontal) scrolling."""
        self._page_viewmodel.seek(self._page_viewmodel.position + scroll / self._scale)

    def zoom(self, i_channel: int, value: float):
        if not self._page_viewmodel.loaded:
            return
        self._user_amplifier[i_channel] = math.e ** max(min(math.log(self._user_amplifier[i_channel]) + value, 15), -10)
        self._page_viewmodel.canvasInvalidated.emit()

    @QtCore.Slot(float, float, bool)  # 选坐标
    def set_selection_point(self, x: float, y: float, end_point=False):
        self._page_viewmodel.set_selection_point(x / self._scale, y, end_point=end_point)

    def get_selection(self):
        x1, x2, y1, y2 = self._page_viewmodel.get_selection()
        x1, x2 = map(lambda x: x * self._scale, [x1, x2])
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def get_standard_fraction(self, logical_width: int):
        length_seconds = logical_width / self._scale
        if self._cache_block_seconds == 0 or self._cache_block_seconds > length_seconds * 4 \
                or self._cache_block_seconds < length_seconds * 1.5:
            self._cache_block_seconds = round(length_seconds * 2)

        position = max(0, min(self._page_viewmodel.position, self._page_viewmodel.seconds - length_seconds))
        scale, cache_block_seconds = self._scale, self._cache_block_seconds
        # If upper bound is already lower than the least possible, or __, disable filtering.


        if self._page_viewmodel.hipass >= scale or self._page_viewmodel.lowpass <= 1 / cache_block_seconds:
            hipass = lowpass = None
        else:
            hipass = self._page_viewmodel.hipass if self._page_viewmodel.hipass > 1 / cache_block_seconds else None
            lowpass = self._page_viewmodel.lowpass if self._page_viewmodel.lowpass < scale else None

        hipass = self._page_viewmodel.hipass
        lowpass = self._page_viewmodel.lowpass

        notch = self._page_viewmodel.notch # self._page_viewmodel.notch
        #测试陷波器，注释maomao
        # notch = 0  # self._page_viewmodel.notch maomao
        # if lowpass is not None and notch <= lowpass or hipass is not None and notch >= hipass:
        #     notch = None

        aligned_offset = int(position // self._cache_block_seconds) * self._cache_block_seconds
        data = np.concatenate([self._get_block(
            offset, self._cache_block_seconds,
            # When the data get appended, the last block get updated every 1/4 seconds.
            int(min(offset + self._cache_block_seconds, self._page_viewmodel.seconds) * 4),
            scale, lowpass, hipass, notch
        ) for
            offset in range(
                aligned_offset, math.ceil(position + length_seconds), self._cache_block_seconds
            )], axis=0)
        
        points_offset = round((position - aligned_offset) * self._scale)
        points_count = round(length_seconds * self._scale)
        data = data[points_offset:points_offset + points_count]
        
        # Amplifiers can continuously change via zoom actions, so not caching them.
        data *= self._user_amplifier

        if self._page_viewmodel._reference != None and self._page_viewmodel._reference < data.shape[1]:
            for channel in range(data.shape[1]):
                data[:,channel] = data[:,channel] - data[:,self._page_viewmodel._reference]

        return data.astype(np.int32),data

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property("QVariant", notify=nopSignal)
    @cache
    def montage_block_viewmodel(self):
        return MontageBlockViewModel(self._montage_block)

    @lru_cache(maxsize=4)
    def _get_block(
            self, offset: int, length: int, ends: int, scale: float, lowpass: float, hipass: float,
            notch: float):
        # logger.debug("{} - {}", offset, length)
        premble = max(2, length // 8)
        pre_offset = max(0, offset - premble)
        if offset + length >= self._page_viewmodel.seconds:
            post_offset = offset + length
        else:
            post_offset = min(offset + length + premble, math.floor(self._page_viewmodel.seconds))
        hires = scale * 2
        data = self._montage_block.get_standard_slice(
            from_sec=pre_offset, to_sec=post_offset, num_points=(post_offset - pre_offset) * hires
        )

        if len(data) == 0:
            return data
        
        mode = None
        if hipass != 0 and lowpass != 0 and hipass < lowpass:
            band, mode = [hipass, lowpass], 'band'
        elif hipass != 0 and lowpass == 0:
            band, mode = hipass, "high"
        elif hipass == 0 and lowpass != 0 :
            band, mode = lowpass, "low"
        if mode:
            param = butter(5, band, mode, output='sos', fs=hires)
            data = sosfiltfilt(param, data, axis=0)

        if notch != 0:
            # w0 = 2 * notch / hires
            # print(w0)
            # print(hires)
            # b, a = signal.iirnotch(notch, 50, hires)
            # data=signal.lfilter(b,a,data)
            band, mode = notch, "low"
            param = butter(5, band, mode, output='sos', fs=hires)
            data = sosfiltfilt(param, data, axis=0)

        hires = int(hires)
        data = data[(offset - pre_offset) * hires:(offset + length - pre_offset) * hires:2]
        # if self._page_viewmodel._eeg_client is not None:
        #     data *= 0.00001

        return data
