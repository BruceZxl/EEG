from typing import Optional, List, cast

from utils.mitertools import apply
from .axis import Axis, JsonObjectType


class ComponentDef:
    k_name = "name"

    def __init__(self, name: str):
        self.name = name

    def to_json(self) -> JsonObjectType:
        from data_model.axes.deserialization_helper import add_kind
        return add_kind(self, {ComponentDef.k_name: self.name})

    @classmethod
    def from_json(cls, obj: JsonObjectType) -> "ComponentDef":
        return cls(**obj)


class ComponentAxis(Axis):
    k_components = "components"

    def __init__(self, name: str = 'component_axis', *, kind: Optional[str] = None, components: List[ComponentDef]):
        super(ComponentAxis, self).__init__(name)
        self.kind = kind
        self.components = components

    def to_json(self) -> JsonObjectType:
        return super().to_json() | {ComponentAxis.k_components: [
            component.to_json() for component in self.components
        ]}
