from typing import Optional, Tuple
from .time_axis import TimeAxis


class ContinuousTimeAxis(TimeAxis):
    def __init__(
            self,
            name: str = 'continuous_time_axis',
            from_to: Optional[Tuple[float, float]] = None,
            sampling_rate: int = 1):
        super(ContinuousTimeAxis, self).__init__(name, from_to, sampling_rate)
