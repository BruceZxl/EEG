from pathlib import Path
from typing import Sequence, List, Any

import numpy as np

from data_model.axes import Axis
from data_model.tensor.tensor import ShapeDefType, Tensor, TensorDataType


def _get_fragment_filename(name: str, i: int):
    return f"{name}-part-{i}.npy"


class FragmentedTensor(Tensor):
    k_fragment_size = "fragment_size"
    k_num_fragments = "num_fragments"
    k_length = "length"

    def __init__(self, data: TensorDataType, shape_def: ShapeDefType, fragment_size: int, length: int):
        self._length = length
        self._fragment_size = fragment_size
        super().__init__(data, shape_def)
        self._clean_table = [True for _ in self._data]

    def append(self, data):
        left = len(self._data) * self._fragment_size - self._length
        used_in_last = self._fragment_size - left
        self._length += len(data)
        if left > 0:
            piece, data = data[:left], data[left:]
            self._data[-1][used_in_last:used_in_last + len(piece)] = piece
            self._clean_table[-1] = False
        while len(data) > 0:
            piece, data = data[:self._fragment_size], data[self._fragment_size:]
            piece, tmp = np.zeros(tuple([self._fragment_size] + list(piece.shape[1:])), dtype=np.float32), piece
            piece[:len(tmp)] = tmp
            self._data.append(piece)
            self._clean_table.append(False)

    @property
    def length(self):
        return self._length

    def __len__(self):
        return self._length

    def _get_bounded_block(self, blk):
        return self._data[blk][:(self._length - self._fragment_size * blk)]

    def __getitem__(self, item):
        if isinstance(item, tuple):
            first, rest = item[0], item[1:]
        else:
            first, rest = item, None
        if isinstance(first, slice):
            l = first.start if first.start is not None else 0
            if l < 0:
                l += self._length
            if l >= self._length:
                return []
            r = first.stop if first.stop is not None else self._length
            if r < 0:
                r += self._length
            s = first.step if first.step is not None else 1
            lb, lr = divmod(l, self._fragment_size)
            rb, rr = divmod(r, self._fragment_size)
            sliced = []
            if lb == rb:
                sliced.append(self._get_bounded_block(lb)[lr:rr])
            else:
                if lr > 0:
                    sliced.append(self._get_bounded_block(lb)[lr:])
                    lb += 1
                while lb < rb:
                    sliced.append(self._get_bounded_block(lb))
                    lb += 1
                if rr > 0:
                    sliced.append(self._get_bounded_block(0)[:rr])
            sliced = np.concatenate(sliced, axis=0)[::s]
        else:
            h, m = divmod(first, self._fragment_size)
            sliced = self._data[h][m]
        if rest is not None:
            sliced = sliced[rest]
        return sliced

    def check_axes(self, targets: Sequence[type]):
        from data_model.tensor import PureTensor
        return PureTensor.do_check_axes(targets, self._shape_def)

    def _save_data(self, directory: Path, name: str, full: bool) -> bool:
        changed = False
        for i, (fragment, clean) in enumerate(zip(self._data, self._clean_table)):
            if full or not clean:
                np.save(str(directory / _get_fragment_filename(name, i)), fragment)
                self._clean_table[i] = True
                changed = True
        return changed

    @classmethod
    def _load_data(cls, directory: Path, name: str, shape_def: ShapeDefType, custom: dict[str:Any]):
        num_fragments = custom.pop(FragmentedTensor.k_num_fragments)
        fragments = []
        for i in range(num_fragments):
            fragments.append(np.load(str(directory / _get_fragment_filename(name, i))))
        return fragments

    def _save_custom(self) -> dict[str, Any]:
        return {
            FragmentedTensor.k_fragment_size: self._fragment_size,
            FragmentedTensor.k_num_fragments: len(self._data),
            FragmentedTensor.k_length: self._length
        }

    def _validate_shape(self):
        # Ensure all fragments having same rank and are consistent with shape def.
        self._data: list[np.ndarray]
        for fragment in self._data:
            assert isinstance(fragment, np.ndarray)
            assert fragment.ndim == len(self._shape_def)
            assert len(fragment) == self._fragment_size
        for axis in self._shape_def:
            assert isinstance(axis, Axis)
