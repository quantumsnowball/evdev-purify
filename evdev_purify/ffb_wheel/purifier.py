import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF

from evdev_purify.purifier import Purifier as Base

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

    def run(self) -> None:
        logger.info(f'Starting Purifier ...')
        logger.info(f'TODO: should start the loop(s)')
