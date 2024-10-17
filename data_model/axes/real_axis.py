from typing import Optional, Tuple

from .axis import Axis, JsonObjectType


class RealAxis(Axis):
    k_from_to = "from_to"

    def __init__(
            self,
            name: str = 'real_axis',
            from_to: Optional[Tuple[float, float]] = None):
        super(RealAxis, self).__init__(name)
        self.from_to = from_to

    def to_json(self) -> JsonObjectType:
        return super().to_json() | {RealAxis.k_from_to: self.from_to}
