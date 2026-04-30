import logging
from datetime import datetime
from typing import Iterator

from evdev.ecodes import EV, EV_MSC, EV_SYN, bytype
from evdev.events import InputEvent

from .virtual_device import VirtualDevice

logger = logging.getLogger(__file__)


class Event:
    def __init__(self, event: InputEvent) -> None:
        self.type = event.type
        self.code = event.code
        self.value = event.value
        self.old_value = event.value
        self.timestamp = event.timestamp()

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


class Package:
    def __init__(
        self,
        skip_list: tuple[int] = (EV_MSC,),
    ) -> None:
        self._skip_list = skip_list
        self._events = list[Event]()

    def __len__(self) -> int:
        # len count exclude SYN event
        return len(self._events[:-1])

    def __getitem__(self, key) -> Event:
        return self._events[key]

    def __iter__(self) -> Iterator[Event]:
        yield from self._events

    def __repr__(self) -> str:
        return f'Package{tuple(self)}'

    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self._events[0].timestamp).isoformat(timespec='milliseconds').replace('T', '_')
        return f'Package(time={dt}, len={len(self)}, types={self.type_names})'

    @property
    def types(self) -> set[int]:
        return {e.type for e in self._events if e.type != EV_SYN}

    @property
    def type_names(self) -> set[str]:
        return {str(EV[t]) for t in self.types}

    def append(self, e: Event) -> None:
        if e.type in self._skip_list:
            return
        self._events.append(e)

    def send(self, dev: VirtualDevice) -> None:
        for e in self._events:
            # write
            dev.write(e.type, e.code, e.value)

            # log
            dt = datetime.fromtimestamp(e.timestamp).isoformat(timespec='milliseconds').replace('T', '_')
            try:
                type_name = EV[e.type]
            except Exception:
                type_name = str(e.type)
            try:
                code_name = bytype[e.type][e.code]
            except Exception:
                code_name = str(e.code)
            logger.debug(f'SENT: {dt}, {type_name}, {code_name}, {e.value=}')
