from typing import Optional, Tuple

from .axis import JsonObjectType
from .real_axis import RealAxis


class TimeAxis(RealAxis):
    k_sampling_rate = "sampling_rate"

    def __init__(
            self,
            name: str = 'time_axis',
            from_to: Optional[Tuple[float, float]] = None,
            sampling_rate: float = 1.0):
        super(TimeAxis, self).__init__(name, from_to)
        self.sampling_rate = sampling_rate

    def to_json(self) -> JsonObjectType:
        return super().to_json() | {TimeAxis.k_sampling_rate: self.sampling_rate}
