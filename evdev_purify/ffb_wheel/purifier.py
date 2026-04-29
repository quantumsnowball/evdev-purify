import logging

from evdev import InputDevice, UInput
from evdev.ecodes import EV_ABS, EV_FF, EV_SYN

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name)
        self._dst_dev = UInput.from_device(
            self._src_dev,
            name=f'Purifier: {name}',
            filtered_types=(EV_SYN, ),
        )

    def _is_targeted_device(self, dev: InputDevice) -> bool:
        caps = dev.capabilities()
        return (
            dev.name == self._name and
            EV_ABS in caps and
            EV_FF in caps
        )

    def run(self) -> None:
        logger.info(f'Starting Purifier ...')
        logger.info(f'{self._src_dev.capabilities()}')
        logger.info(f'{self._dst_dev.capabilities()}')
        logger.info(f'TODO: should start the loop(s)')
