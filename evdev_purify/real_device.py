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
        logger.info(f'Created: {str(self)}')

    def __str__(self):
        return f"RealDevice('{self.path}', name='{self.name}')"

    def __enter__(self) -> Self:
        if self._grab:
            try:
                self.grab()
                logger.info(f'Grabbed {str(self)}')
            except OSError as e:
                logger.error(f'Failed to grab {str(self)}')
                raise e
        return self

    def __exit__(self, *_) -> None:
        if self._grab:
            try:
                self.ungrab()
                logger.info(f'Ungrabbed {str(self)}')
            except OSError as e:
                logger.error(f'Failed to ungrab {str(self)}')
                raise e

    @property
    def packages(self) -> Iterator[Package]:
        try:
            package = Package()
            for e in self.read_loop():
                # append as custom Event type
                package.append(Event(e))
                if e.type == EV_SYN:
                    yield package
                    package = Package()
        except OSError:
            logger.info(f'Disconnected: {str(self)}')
        except Exception as e:
            logger.error(e)

    @classmethod
    def find_or_wait_for(
        cls,
        name: str,
        is_targeted_device: Callable[[InputDevice[str]], bool],
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
                    if item.device_node is not None:
                        dev = InputDevice(item.device_node)
                        if is_targeted_device(dev):
                            logger.info(f'Found existing device: {name} at {item.device_node}')
                            return cls(item.device_node, grab=grab)
                except Exception:
                    continue
            # then block until any device is added, and check if this is the targeted device
            logger.info(f'Waiting for device: {name}')
            for item in iter(monitor.poll, None):
                try:
                    if item.device_node is not None and item.action == 'add':
                        dev = InputDevice(item.device_node)
                        if is_targeted_device(dev):
                            logger.info(f'Found newly added device: {name} at {item.device_node}')
                            return cls(item.device_node, grab=grab)
                except Exception:
                    continue
