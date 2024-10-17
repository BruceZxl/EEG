from PySide6 import QtCore
from PySide6.QtCore import QObject
from PySide6.QtGui  import QColor

from utils.qutils import os_accent_color

class OSColors(QObject):
    _instance = None

    def __init__(self):
        if OSColors._instance is not None:
            return
        QObject.__init__(self)
        OSColors._instance, OSColors.__new__ = self, lambda _: OSColors._instance

    @QtCore.Slot(result=QColor)
    def accent(self) -> QColor:
        return QColor.fromRgba(os_accent_color())
    
    @QtCore.Slot(result=bool)
    def is_accent_dark(self) -> bool:
        return self.accent().lightness() < 128
    