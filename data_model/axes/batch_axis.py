from .axis import Axis


class BatchAxis(Axis):
    def __init__(self, name='batch_axis'):
        super(BatchAxis, self).__init__(name)
