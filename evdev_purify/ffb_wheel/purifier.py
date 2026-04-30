import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_SYN

from evdev_purify.device import VirtualDevice
from evdev_purify.purifier import Purifier as Base
from evdev_purify.retry import retry_loop

from .ffb_effect import FFBEffectManager

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name)
        self._dst_dev = VirtualDevice.from_device(
            self._src_dev,
            name=f'Purifier: {name}',
            filtered_types=(EV_SYN, ),
        )
        self._ffb_effect_manager = FFBEffectManager(self, self._dst_dev)

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
        # intercept all src events
        self._grab()

        # then process all src events
        for p in self._packages:
            # TODO: filtering and remapping here

            # passthrough all other irrelevant events
            p.send(self._dst_dev)
