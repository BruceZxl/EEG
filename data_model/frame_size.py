import enum

from data_model.time_delta import TimeDelta


class FrameSize(enum.Enum):
    OneSec = TimeDelta(seconds=1)
    TwoSec = TimeDelta(seconds=2)
    FourSec = TimeDelta(seconds=4)
    FiveSec = TimeDelta(seconds=5)
    TenSec = TimeDelta(seconds=10)
    ThirtySec = TimeDelta(seconds=30)
    OneMin = TimeDelta(minutes=1)
    TwoMin = TimeDelta(minutes=2)
    FiveMin = TimeDelta(minutes=5)
    HalfHour = TimeDelta(minutes=30)
