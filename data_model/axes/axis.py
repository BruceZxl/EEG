import abc
from typing import Union

JsonValueType = Union[str, int, float, bool, None, "JsonType"]
JsonObjectType = dict[str, JsonValueType]


class Axis(abc.ABC):
    k_name = "name"

    def __init__(self, name: str = 'axis'):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    def to_json(self) -> JsonObjectType:
        from data_model.axes.deserialization_helper import add_kind
        return add_kind(self, {Axis.k_name: self.name})

    @classmethod
    def from_json(cls, obj: JsonObjectType) -> "Axis":
        return cls(**obj)
