import logging

from evdev import UInput
from evdev.ecodes import EV_KEY

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
            # skip and log multiple events packages
            if len(p) > 1:
                logger.info(f'Multi-event package: {p}')
                continue

            # only interested in single event key-press package
            if p.types == {EV_KEY, }:
                # TODO: you can then safely remap your key into any keyboard code and use it in your game
                logger.info(p)
