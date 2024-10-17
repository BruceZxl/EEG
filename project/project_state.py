from typing import Any

from utils.json_utils import json_write

_k_position = "position"


class ProjectState:

    def __init__(self, save_action):
        self._position = 0
        self._save_action = save_action
        self.is_clean = False

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float):
        self._position = value
        self.is_clean = False
        self._save_action()

    def set_loaded_value(self, key: str, value):
        setattr(self, f"_{key}", value)

    def load(self, obj: dict[str:Any]):
        for k, v in obj.items():
            setattr(self, f"_{k}", v)
        self.is_clean = True

    def save(self, full=False):
        if self.is_clean and not full:
            return None
        self.is_clean = True
        return {
            _k_position: self._position
        }
