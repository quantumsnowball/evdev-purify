import logging

from evdev import UInput

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._dst_dev = UInput(name=f'Purifier: {name}')

    def run(self) -> None:
        logger.info(f'Starting Purifier on {self._src_dev_path} ...')

        # intercept all src events and process them
        for p in self._packages:
            logger.info(p)
