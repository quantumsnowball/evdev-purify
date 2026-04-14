import logging
from abc import ABC, abstractmethod
from typing import Iterator

import evdev
from evdev import InputDevice, UInput
from evdev.ecodes import EV_SYN

from evdev_purify.package import Event, Package

logger = logging.getLogger(__file__)


class Purifier(ABC):
    def __init__(
        self,
        name: str,
        *,
        max_event_interval: float,
    ) -> None:
        self._max_event_interval = max_event_interval
        paths = {InputDevice(path).name: path for path in evdev.list_devices()}
        self._src_dev_path = paths[name]
        self._src_dev = InputDevice(self._src_dev_path)
        self._dst_dev = UInput.from_device(self._src_dev, name=f'Purifier: {name}')

    @property
    def _packages(self) -> Iterator[Package]:
        package = Package()
        for e in self._src_dev.read_loop():
            # append as custom Event type
            package.append(Event(e))
            if e.type == EV_SYN:
                yield package
                package = Package()

    @abstractmethod
    def run(self) -> None:
        ...
