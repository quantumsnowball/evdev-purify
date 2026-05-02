import logging
import time
from dataclasses import dataclass, field
from typing import Self

from evdev.ecodes import ABS_RX, ABS_RY, EV, EV_ABS, EV_KEY, bytype
from evdev.events import InputEvent

logger = logging.getLogger(__file__)


@dataclass(kw_only=True, slots=True)
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

    @property
    def is_L2(self) -> bool:
        return self.type == EV_ABS and self.code == ABS_RX

    @property
    def is_R2(self) -> bool:
        return self.type == EV_ABS and self.code == ABS_RY

    @classmethod
    def from_input_event(cls, e: InputEvent) -> Self:
        return cls(
            type=e.type,
            code=e.code,
            value=e.value,
            timestamp=e.timestamp()
        )


@dataclass(kw_only=True, slots=True)
class KeyEvent(Event):
    type: int = EV_KEY


@dataclass(kw_only=True, slots=True)
class KeyDownEvent(KeyEvent):
    value: int = 1  # pressed


@dataclass(kw_only=True, slots=True)
class KeyUpEvent(KeyEvent):
    value: int = 0  # released


@dataclass(kw_only=True, slots=True)
class SyncEvent(Event):
    type: int = 0
    code: int = 0
    value: int = 0
