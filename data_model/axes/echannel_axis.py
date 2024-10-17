from typing import Optional, List, Dict, Any, cast
from mne.io.constants import FIFF
from mne.utils._bunch import NamedInt
from pyedflib import EdfReader

from utils.mitertools import apply, do_assert
from .axis import JsonObjectType
from .channel_axis import ChannelDef, ChannelAxis

_UNIT = FIFF.FIFF_UNIT_V


class EChannelDef(ChannelDef):
    def __init__(self, name: str, *, unit_m: NamedInt):
        super().__init__(name, unit=_UNIT, unit_m=unit_m)

    @staticmethod
    def from_mne_channel_info(channel_info: Dict[str, Any]) -> "EChannelDef":
        assert channel_info["unit"] == _UNIT
        return EChannelDef(name=channel_info["ch_name"], unit_m=channel_info["unit_mul"])

    @staticmethod
    def from_pyedflib_info(edf: EdfReader, channel: int) -> "EChannelDef":
        if (unit := edf.getPhysicalDimension(channel)) == "uV":
            unit_m = FIFF.FIFF_UNITM_MU
        elif unit == "mV":
            unit_m = FIFF.FIFF_UNITM_M
        elif unit == "V":
            unit_m = FIFF.FIFF_UNITM_NONE
        else:
            raise RuntimeError(f"Unsupported unit: {unit}.")
        return EChannelDef(name=edf.getLabel(channel), unit_m=unit_m)

    @classmethod
    def from_json(cls, obj: JsonObjectType) -> "EChannelDef":
        return cast(EChannelDef, super().from_json(apply(
            obj, lambda x: do_assert(x.pop(ChannelDef.k_unit) == _UNIT)
        )))


class EChannelAxis(ChannelAxis):
    def __init__(self, name: str = 'channel_axis', *, kind: Optional[str] = None, channels: List[EChannelDef]):
        super(EChannelAxis, self).__init__(name, kind=kind, channels=channels)
