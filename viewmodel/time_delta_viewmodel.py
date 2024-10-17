from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QObject

from data_model.time_delta import TimeDelta


class TimeDeltaViewModel(QObject):
    nop = QtCore.Signal()
    timeChanged = QtCore.Signal()

    def __init__(self, model: Optional[TimeDelta] = None):
        super().__init__()
        if model is None:
            model = TimeDelta()
        self.model = model

    @QtCore.Property(str, notify=nop)
    def text(self):
        return self.model.to_readable()

    @QtCore.Property(int, notify=nop)
    def value(self):
        return self.model.total_ms

    @QtCore.Property(int, notify=timeChanged)
    def total_ms(self):
        return self.model.total_ms

    @total_ms.setter
    def total_ms(self, value: int):
        if value != self.model.total_ms:
            self.model.total_ms = value
            self.timeChanged.emit()

    @QtCore.Slot()
    def normalize(self):
        self.model.normalize()

    @QtCore.Slot("QVariant", bool, result=str)
    def to_readable(self, reference: "TimeDeltaViewModel" = None, truncate_lowers: bool = False):
        """ See `TimeDelta.to_readable()`. """
        return self.model.to_readable(reference=reference.model, truncate_lowers=truncate_lowers)
