import logging
from typing import Any, Callable, Iterator, Self, override

import pyudev
from evdev import InputDevice
from evdev.ecodes import EV_SYN

from .package import Event, Package

logger = logging.getLogger(__file__)


class RealDevice(InputDevice):
    @override
    def __init__(self, *args: Any, grab: bool, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._grab = grab
        logger.info(f'Created {self}')

    def __str__(self):
        return f"RealDevice('{self.path}', '{self.name}')"

    def __enter__(self) -> Self:
        if self._grab:
            try:
                self.grab()
                logger.info(f'Grabbed {self}')
            except OSError as e:
                logger.error(f'Failed to grab {self}')
                raise e
        return self

    def __exit__(self, *_) -> None:
        if self._grab:
            try:
                self.ungrab()
                logger.info(f'Ungrabbed {self}')
            except OSError as e:
                raise e

    def packages(self, *, drop: tuple[int, ...]) -> Iterator[Package]:
        try:
            package = Package()
            for e in self.read_loop():
                # skip appending event on drop list
                if e.type in drop:
                    continue
                # append as an Event type
                package.append(Event(e))
                # yield a package on a SYN REPORT event
                if e.type == EV_SYN:
                    yield package
                    package = Package()
        except OSError:
            logger.info(f'Disconnected {self}')
        except Exception as e:
            logger.error(e)

    @classmethod
    def find_or_wait_for(
        cls,
        name: str,
        is_target: Callable[[str | None], bool],
        *,
        grab: bool,
    ) -> Self:
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='input')

        # retry loop for device connection
        while True:
            # try to find and return the device if it already connected
            for item in context.list_devices(subsystem='input'):
                try:
                    if is_target(item.device_node):
                        logger.info(f"Found existing device ('{item.device_node}', '{name}')")
                        return cls(item.device_node, grab=grab)
                except Exception:
                    continue
            # then block until any device is added, and check if this is the targeted device
            logger.info(f"Waiting for device '{name}'")
            for item in iter(monitor.poll, None):
                try:
                    if item.action == 'add' and is_target(item.device_node):
                        logger.info(f"Found new device ('{item.device_node}', '{name}')")
                        return cls(item.device_node, grab=grab)
                except Exception:
                    continue
