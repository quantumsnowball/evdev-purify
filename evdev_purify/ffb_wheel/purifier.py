import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_SYN

from evdev_purify.device import VirtualDevice
from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop

from .ffb_effect import FFBEffectManager

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name)

    def _is_targeted_device(self, dev: InputDevice) -> bool:
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
            RealDevice.find_or_wait_for(self._name, self._is_targeted_device, grab=True) as real_dev,
            VirtualDevice.from_device(real_dev, name=f'Purifier: {self._name}', filtered_types=(EV_SYN, ),) as virtual_dev,
            FFBEffectManager(real_dev, virtual_dev),
        ):
            # then process all src events
            for p in real_dev.packages:
                # TODO: filtering and remapping here

                # passthrough all other irrelevant events
                p.send(virtual_dev)
