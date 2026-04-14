import logging
from typing import Iterator

from evdev import UInput
from evdev.ecodes import EV, EV_MSC, bytype
from evdev.events import InputEvent

logger = logging.getLogger(__file__)


class Package:
    def __init__(
        self,
        skip_list: tuple[int] = (EV_MSC,),
    ) -> None:
        self._skip_list = skip_list
        self._events = list[InputEvent]()

    def __getitem__(self, key) -> InputEvent:
        return self._events[key]

    def __iter__(self) -> Iterator[InputEvent]:
        yield from self._events

    def append(self, e: InputEvent) -> None:
        if e.type in self._skip_list:
            return
        self._events.append(e)

    def send(self, dev: UInput) -> None:
        for e in self._events:
            dev.write(e.type, e.code, e.value)
            logger.debug(f'SENT: {e.timestamp()}, {EV[e.type]}, {bytype[e.type][e.code]}, {e.value=}')
