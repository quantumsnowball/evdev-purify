import logging

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def run(self) -> None:
        logger.info(f'Starting Purifier on {self._src_dev_path} ...')
