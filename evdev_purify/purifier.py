import logging
from abc import ABC, abstractmethod
from typing import Iterator

import pyudev
from evdev import InputDevice
from evdev.ecodes import EV_SYN

from evdev_purify.package import Event, Package

logger = logging.getLogger(__file__)


class Purifier(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._src_dev_instance: InputDevice | None = None

    def _src_dev_lookup(self) -> InputDevice:
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
                        if self._is_targeted_device(dev):
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
                        if self._is_targeted_device(dev):
                            logger.info(f'Found newly added device: {self._name} at {item.device_node}')
                            return dev
                except Exception:
                    continue

    @property
    def _src_dev(self) -> InputDevice:
        try:
            # ensure instance exists
            assert self._src_dev_instance is not None
            # test the fd
            _ = self._src_dev_instance.fd
        except Exception:
            # failed the test, lookup again
            self._src_dev_instance = self._src_dev_lookup()
        # return the cached instance
        return self._src_dev_instance

    @_src_dev.setter
    def _src_dev(self, val: InputDevice | None) -> None:
        self._src_dev_instance = val

    @property
    def _packages(self) -> Iterator[Package]:
        try:
            package = Package()
            for e in self._src_dev.read_loop():
                # append as custom Event type
                package.append(Event(e))
                if e.type == EV_SYN:
                    yield package
                    package = Package()
        except OSError:
            logger.info('Event loop failed, resetting device...')
        except Exception as e:
            logger.error(e)
        finally:
            # if read_loop() ever quit, reset src dev to force lookup again in next retry
            self._src_dev = None

    @abstractmethod
    def _is_targeted_device(self, dev: InputDevice) -> bool:
        ...

    @abstractmethod
    def run(self) -> None:
        ...
