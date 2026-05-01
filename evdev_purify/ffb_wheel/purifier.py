import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_KEY, EV_MSC, EV_SYN

from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop
from evdev_purify.virtual_device import VirtualDevice

from .ffb_effect import FFBEffectManager

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        log_threshold: int,
    ) -> None:
        super().__init__(name)
        self._log_threshold = log_threshold

    def _is_target(self, path: str | None) -> bool:
        if path is None:
            return False
        dev = InputDevice(path)
        caps = dev.capabilities()
        return (
            dev.name == self._name and
            EV_ABS in caps and
            EV_FF in caps
        )

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
    )
    def run(self) -> None:
        with (
            RealDevice.find_or_wait_for(self._name, self._is_target, grab=True) as real_dev,
            VirtualDevice.from_device(real_dev, name=f'Purifier: {self._name}', filtered_types=(EV_SYN, ),) as virtual_dev,
            FFBEffectManager(real_dev, virtual_dev),
        ):
            # then process all src events
            for package in real_dev.packages(drop=(EV_MSC, )):

                # if a package contains more than one EV_KEY event, consider these noise
                if package.count(EV_KEY) > 1:
                    # modify the packet, drop all the EV_KEY events, leave other event untouched
                    package.drop(EV_KEY)

                # passthrough all other irrelevant events
                package.send(virtual_dev)
