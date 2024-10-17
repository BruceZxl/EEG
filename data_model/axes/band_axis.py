from typing import Optional, List

from .channel_axis import ChannelAxis, ChannelDef


class BandDef(ChannelDef):
    def __init__(self, name: str, *, unit: str, amplifier: float = 1.0):
        super().__init__(name, unit=unit, amplifier=amplifier)


class BandAxis(ChannelAxis):
    def __init__(self, name: str = 'band_axis', *, kind: Optional[str] = None, bands: List[ChannelDef]):
        super(BandAxis, self).__init__(name, kind=kind, channels=bands)
