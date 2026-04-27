import logging
from abc import ABC, abstractmethod
from typing import Iterator

import pyudev
from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_SYN

from evdev_purify.package import Event, Package

logger = logging.getLogger(__file__)


class Purifier(ABC):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def _src_dev(self) -> InputDevice:
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
                        caps = dev.capabilities()
                        if dev.name == self._name and EV_ABS in caps and EV_FF in caps:
                            logger.info(f'Found existing device: {self._name} at {item.device_node}')
                            return dev
                except Exception:
                    continue
            # then block until any device is added, and check if this is the targeted device
            logger.info(f'Waiting for device: {self._name}')
            for item in iter(monitor.poll, None):
                try:
                    if item.device_node is not None and item.action == 'add':
                        dev = InputDevice(item.device_node)
                        caps = dev.capabilities()
                        if dev.name == self._name and EV_ABS in caps and EV_FF in caps:
                            logger.info(f'Found newly added device: {self._name} at {item.device_node}')
                            return dev
                except Exception:
                    continue

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
