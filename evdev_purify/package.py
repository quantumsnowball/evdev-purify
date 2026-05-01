import logging
from datetime import datetime
from typing import Iterator

from evdev.ecodes import EV, EV_SYN, bytype
from evdev.events import InputEvent

logger = logging.getLogger(__file__)


class Event:
    __slots__ = ('type', 'code', 'value', 'old_value', 'timestamp')

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
    __slots__ = ('_events',)

    def __init__(self) -> None:
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

    def count(self, event_type: int) -> int:
        return sum(1 for e in self._events if e.type == event_type)

    def drop(self, event_type: int, *, log_threshold: int = 1) -> None:
        # filter as new event list
        clean_events = [e for e in self._events if e.type != event_type]

        # log
        def event_repr(events: list[Event]) -> str:
            data = tuple(str(EV.get(e.type, e.type)) for e in events if e.type != EV_SYN)
            return f"({','.join(data)})"
        drop_count = len(self._events) - len(clean_events)
        if drop_count >= log_threshold:
            logger.info(f'DROP {drop_count}: {event_repr(self._events)} -> {event_repr(clean_events)}')

        # replace the original list as new list
        self._events = clean_events

    def append(self, e: Event) -> None:
        self._events.append(e)
