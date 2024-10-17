from typing import Optional, List, cast

from mne.utils._bunch import NamedInt

from utils.mitertools import apply, rename_dict_value
from .axis import JsonObjectType
from .component_axis import ComponentAxis, ComponentDef


class ChannelDef(ComponentDef):
    k_unit = "unit"
    k_unit_m = "unit_m"

    def __init__(self, name: str, *, unit: NamedInt, unit_m: NamedInt):
        super().__init__(name)
        self.unit = unit
        self.unit_m = unit_m

    def to_json(self) -> JsonObjectType:
        return super().to_json() | {ChannelDef.k_unit: self.unit, ChannelDef.k_unit_m: self.unit_m}


class ChannelAxis(ComponentAxis):
    k_channels = "channels"

    def __init__(self, name: str = 'channel_axis', *, kind: Optional[str] = None, channels: List[ChannelDef]):
        super(ChannelAxis, self).__init__(name, kind=kind, components=channels)

    @property
    def channels(self) -> List[ChannelDef]:
        return cast(List[ChannelDef], self.components)

    def to_json(self) -> JsonObjectType:
        return apply(
            super().to_json(),
            lambda x: rename_dict_value(x, ComponentAxis.k_components, ChannelAxis.k_channels)
        )
