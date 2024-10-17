from functools import cache

from PySide6 import QtCore
from PySide6.QtCore import QObject

from data_model.montage.base_montage import MontageBlock
from viewmodel.channel_def_viewmodel import ChannelDefViewModel


class MontageBlockViewModel(QObject):
    nopSignal = QtCore.Signal()

    def __init__(self, montage_block: MontageBlock):
        super().__init__()
        self._montage_block = montage_block

    # noinspection PyCallingNonCallable
    @QtCore.Property(int)
    def num_channels(self):
        return self._montage_block.num_channels

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property("QVariantList", notify=nopSignal)
    @cache
    def channels(self) -> list[ChannelDefViewModel]:
        return [ChannelDefViewModel(channel_def) for channel_def in self._montage_block.channels]
