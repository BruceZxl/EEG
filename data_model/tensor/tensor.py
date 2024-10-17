import abc
import json
from pathlib import Path
from typing import Tuple, Sequence, Union, List, Any

import numpy as np

from data_model.axes import Axis
from data_model.axes.deserialization_helper import resolve_nested

_k_ext_manifest = ".json"

""" Data can be either NumPy array (for pure tensor),
list af arrays (for fragmented tensor), or list of tensors
(for compound tensor). """
TensorDataType = Union[np.ndarray, List[np.ndarray], List["Tensor"]]
ShapeDefType = Tuple[Union[Axis, List[Axis]], ...]


class Tensor(abc.ABC):
    k_kind = "_kind"
    k_shape_def = "shape_def"
    k_ext_data = ".npy"
    _kinds = None

    def __init__(
            self,
            data: TensorDataType,
            shape_def: ShapeDefType):
        self._data = data
        self._shape_def = shape_def
        self._validate_shape()

    @abc.abstractmethod
    def __len__(self):
        ...

    @abc.abstractmethod
    def __getitem__(self, item):
        ...

    @property
    def data(self) -> TensorDataType:
        return self._data

    @property
    def shape_def(self) -> ShapeDefType:
        return self._shape_def

    @property
    def ndim(self) -> int:
        return len(self._shape_def)

    @abc.abstractmethod
    def append(self, data):
        ...

    @abc.abstractmethod
    def check_axes(self, targets: Sequence[type]) -> List[List[int]]:
        ...

    @abc.abstractmethod
    def _validate_shape(self):
        raise NotImplementedError("?")

    @abc.abstractmethod
    def _save_data(self, directory: Path, name: str, full: bool) -> bool:
        ...

    @classmethod
    @abc.abstractmethod
    def _load_data(cls, directory: Path, name: str, shape_def: ShapeDefType, custom: dict[str:Any]):
        ...

    def _save_custom(self) -> dict[str, Any]:
        return {}

    def save_to(self, directory: Path, name: str, full=False) -> bool:
        changed = self._save_data(directory, name, full)
        if not (changed or full):
            return False
        obj = {
                  Tensor.k_kind: type(self).__qualname__,
                  Tensor.k_shape_def: [
                      axis.to_json() if isinstance(axis, Axis) else [
                          ax.to_json() for ax in axis
                      ] for axis in self._shape_def
                  ]
              } | self._save_custom()
        with open(directory / (name + _k_ext_manifest), 'w') as fp:
            json.dump(obj, fp, indent=2, ensure_ascii=False)
        return True

    @staticmethod
    def load_from(directory: Path, name: str, shape_def=None):
        if Tensor._kinds is None:
            from data_model.tensor.fragmented_tensor import FragmentedTensor
            from data_model.tensor.compound_tensor import CompoundTensor
            from data_model.tensor.pure_tensor import PureTensor
            Tensor._kinds = {
                kind.__name__: kind for kind in [PureTensor, CompoundTensor, FragmentedTensor]}
        with open(directory / (name + _k_ext_manifest), 'r') as fp:
            obj = json.load(fp)
        cls = Tensor._kinds[obj.pop(Tensor.k_kind)]
        loaded_shape_def = tuple(
            [
                resolve_nested(ax) for ax in axis
            ] if isinstance(axis, list) else resolve_nested(axis)
            for axis in obj.pop(Tensor.k_shape_def)
        )
        if shape_def is None:
            shape_def = loaded_shape_def
        else:
            assert len(shape_def) == len(loaded_shape_def)
            for shape, another in zip(shape_def, loaded_shape_def):
                if isinstance(shape, list):
                    assert len(shape) == len(another)
                # TODO: check for equality
                # else:
                #     assert shape == another
        data = cls._load_data(directory, name, shape_def=shape_def, custom=obj)
        return cls(data=data, shape_def=shape_def, **obj)
