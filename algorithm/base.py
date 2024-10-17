import abc
from typing import Tuple, Optional

from data_model.tensor import Tensor
from data_model.axes import Axis


class BaseAlgorithm(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def is_applicable(shape_def: Tuple[Axis]) -> bool:
        """Check if this algorithm can handle input data with
        given shape defination."""

    @abc.abstractmethod
    def infer_output_shape_def(self, shape_def: Tuple[Axis]) -> Optional[Tuple[Axis]]:
        """Given shape defination of input tensor, infer the shape
         defination of the output.

         Returns null if not applicable."""

    @abc.abstractmethod
    def call(self, inputs: Tensor) -> Tensor:
        """apply this algorithm to the input tensor."""
