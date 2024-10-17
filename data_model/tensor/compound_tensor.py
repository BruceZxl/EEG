from pathlib import Path
from typing import Sequence, List, Any

from data_model.axes import Axis
from data_model.tensor.tensor import ShapeDefType, Tensor, TensorDataType


def _get_component_filename(name: str, i: int, id_length: int):
    return f"{name}-{str(i).zfill(id_length)}"


class CompoundTensor(Tensor):

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return [x[item[1:]] for x in self._data[item[0]]]
        return self._data[item]

    def append(self, data):
        assert len(data) == len(self._data)
        for new_component, component in zip(data, self._data):
            component: Tensor
            component.append(new_component)

    def check_axes(self, targets: Sequence[type]):
        target_axes = [[] for _ in range(len(targets) + 1)]
        for i_axis, axis in enumerate(self._shape_def):
            confirmed = False
            for i_target, target in enumerate(targets):
                if isinstance(axis, target) or isinstance(axis, list) and isinstance(axis[0], target):
                    target_axes[i_target].append(i_axis)
                    confirmed = True
                    break
            if not confirmed:
                target_axes[-1].append(i_axis)
        return target_axes

    def _save_data(self, directory: Path, name: str, full: bool) -> bool:
        id_length = len(str(len(self._data)))
        changed = False
        for i, component in enumerate(self._data):
            component: Tensor
            changed = component.save_to(directory, _get_component_filename(name, i, id_length), full=full) or changed
        return changed

    @classmethod
    def _load_data(cls, directory: Path, name: str, shape_def: ShapeDefType, custom: dict[str:Any]):
        num_components = len(shape_def[1])
        tail_shape_def = list(shape_def[2:])
        id_length = len(str(num_components))
        components = []
        for i in range(num_components):
            component = Tensor.load_from(
                directory, _get_component_filename(name, i, id_length),
                shape_def=tuple([shape_def[1][i]] + tail_shape_def))
            components.append(component)
        return components

    def _validate_shape(self):
        # Ensure all components having same rank and are consistent with shape def.
        data: list[Tensor]
        for component in self._data:
            assert isinstance(component, Tensor)
            assert component.ndim == len(self._shape_def) - 1
        # Ensure axes of shape def:
        # Axis #0 shall be scalar.
        # Other axes can be vectors or scalars.
        # Lengths of vector axes shall be equal to the number of components.
        assert isinstance(self._shape_def[0], Axis)
        for i in range(1, len(self._shape_def)):
            axes = self._shape_def[i]
            if isinstance(axes, list):
                assert len(axes) == len(self._data)
                assert len(set(type(axis) for axis in axes)) == 1
                # Components' axes shall be identical to the compound tensor's.
                for j, component in enumerate(self._data):
                    assert id(component.shape_def[i - 1]) == id(axes[j])
            else:
                for component in self._data:
                    assert id(component.shape_def[i - 1]) == id(axes)
