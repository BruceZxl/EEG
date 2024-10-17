from functools import cached_property
from typing import List

from PySide6 import QtCore
from PySide6.QtCore import QObject

from data_model.frame_size import FrameSize
from viewmodel.time_delta_viewmodel import TimeDeltaViewModel


class FrameSizes(QObject):
    # QML has no memory mgmt over QObjects passed as pointer.
    # It prevents not Python's GC or C++'s memory leak.
    # Heard that internally they use only singletons.
    # For python, we'd use singletons, python-managed objects,
    # fields of them, static fields, and sometimes globals.

    _instance = None

    def __init__(self):
        if FrameSizes._instance is not None:
            return
        QObject.__init__(self)
        FrameSizes._instance, FrameSizes.__new__ = self, _new

    @QtCore.Slot(result="QVariantList")
    def get_all(self) -> List[TimeDeltaViewModel]:
        return self.all

    @cached_property
    def all(self) -> List[TimeDeltaViewModel]:
        return list(map(TimeDeltaViewModel, [x.value for x in FrameSize]))

    def lookup(self, frame_size: FrameSize):
        for i, j in enumerate(self.all):
            if j.model == frame_size.value:
                return i
        raise RuntimeError()


def _new(_):
    return FrameSizes._instance
