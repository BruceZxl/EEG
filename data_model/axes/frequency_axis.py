from typing import Optional, Tuple

from .real_axis import RealAxis


class FrequencyAxis(RealAxis):
    def __init__(self, name='frequency_axis', from_to: Optional[Tuple[float, float]] = None):
        super(FrequencyAxis, self).__init__(name, from_to)
        self.from_to = from_to
