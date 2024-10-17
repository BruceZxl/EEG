from PySide6 import QtCore
from PySide6.QtCore import QObject

from data_model.montage.demo_dual_montage import DemoDualMontage
from data_model.montage.original_montage import OriginalMontage


class MontageRegistry(QObject):
    _instance = None

    def __init__(self):
        if MontageRegistry._instance is not None:
            return
        QObject.__init__(self)
        MontageRegistry._instance, MontageRegistry.__new__ = self, lambda _: MontageRegistry._instance
        self.all = [
            ("原始数据", OriginalMontage),
            ("示例双区域", DemoDualMontage)
        ]
        self._index = {k: v for k, v in self.all}
        self._keys = [k for k, v in self.all]

    # noinspection PyTypeChecker
    @QtCore.Slot(result=list)
    def get_names(self) -> list[str]:
        return self._keys
