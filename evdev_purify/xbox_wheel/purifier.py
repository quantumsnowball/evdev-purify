import logging

from evdev import InputDevice
from evdev.ecodes import EV_MSC

from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop
from evdev_purify.virtual_device import VirtualDevice

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name)

    def _is_target(self, path: str | None) -> bool:
        if path is None:
            return False
        dev = InputDevice(path)
        return dev.name == self._name

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
    )
    def run(self) -> None:
        with (
            RealDevice.find_or_wait_for(self._name, self._is_target, grab=True) as real_dev,
            VirtualDevice.from_device(real_dev, name=f'Pure: {self._name}') as virtual_dev,
        ):
            # then process all src events
            for package in real_dev.packages(drop=(EV_MSC, )):
                # passthrough all other irrelevant events
                virtual_dev.send(package)
