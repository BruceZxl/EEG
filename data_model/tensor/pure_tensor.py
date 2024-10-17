from pathlib import Path
from typing import Sequence, Optional, List, Any

import numpy as np

from data_model.tensor import Tensor, ShapeDefType, TensorDataType


class PureTensor(Tensor):

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def append(self, data):
        raise RuntimeError("Pure tensor supports not modification.")

    def check_axes(self, targets: Sequence[type]) -> List[List[int]]:
        return PureTensor.do_check_axes(targets, self._shape_def)

    @staticmethod
    def do_check_axes(targets: Sequence[type], shape_def: ShapeDefType) -> List[List[int]]:
        target_axes = [[] for _ in range(len(targets) + 1)]
        for i_axis, axis in enumerate(shape_def):
            confirmed = False
            for i_target, target in enumerate(targets):
                if isinstance(axis, target):
                    target_axes[i_target].append(i_axis)
                    confirmed = True
                    break
            if not confirmed:
                target_axes[-1].append(i_axis)
        return target_axes

    def _save_data(self, directory: Path, name: str, full: bool) -> bool:
        if not full:
            return False
        np.save(str(directory / (name + Tensor.k_ext_data)), self._data)
        return True

    @classmethod
    def _load_data(cls, directory: Path, name: str, shape_def: ShapeDefType, custom: dict[str:Any]):
        return np.load(str(directory / (name + Tensor.k_ext_data)))

    def _validate_shape(self):
        assert self._data.ndim == len(self._shape_def)
