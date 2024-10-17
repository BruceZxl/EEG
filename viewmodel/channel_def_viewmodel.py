from PySide6 import QtCore
from PySide6.QtCore import QObject

from data_model.axes import ChannelDef


class ChannelDefViewModel(QObject):
    channelChanged = QtCore.Signal()

    def __init__(self, channel_def: ChannelDef):
        super().__init__()
        self._channel_def = channel_def

    # noinspection PyCallingNonCallable,PyTypeChecker
    @QtCore.Property(str, notify=channelChanged)
    def name(self):
        return self._channel_def.name
