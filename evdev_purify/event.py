import logging
import time
from dataclasses import dataclass, field
from typing import Self

from evdev.ecodes import EV, bytype
from evdev.events import InputEvent

logger = logging.getLogger(__file__)


@dataclass(slots=True)
class Event:
    type: int
    code: int
    value: int
    timestamp: float = field(default_factory=time.time)
    old_value: int = field(init=False)

    def __post_init__(self) -> None:
        self.old_value = self.value

    def __repr__(self) -> str:
        try:
            type_name = EV[self.type]
        except Exception:
            type_name = str(self.type)
        try:
            code_name = bytype[self.type][self.code]
        except Exception:
            code_name = str(self.code)
        return f'Event({type_name}, {code_name}, {self.value})'

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def is_modified(self) -> bool:
        return self.value != self.old_value

    @classmethod
    def from_input_event(cls, e: InputEvent) -> Self:
        return cls(e.type, e.code, e.value, e.timestamp())
