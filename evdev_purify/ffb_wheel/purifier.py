import logging

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        max_event_interval: float,
    ) -> None:
        super().__init__(name, max_event_interval=max_event_interval)

    def run(self) -> None:
        logger.info(f'Starting Purifier on {self._src_dev_path} ...')
