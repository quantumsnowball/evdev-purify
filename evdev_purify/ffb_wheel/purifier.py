import logging
import time

from evdev import InputDevice, UInput
from evdev.ecodes import EV_ABS, EV_FF, EV_SYN

from evdev_purify.purifier import Purifier as Base

from .ffb_effect import FFBEffectManager

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
        self._ffb_effect_manager = FFBEffectManager(self, self._dst_dev)

    def _is_targeted_device(self, dev: InputDevice) -> bool:
        caps = dev.capabilities()
        return (
            dev.name == self._name and
            EV_ABS in caps and
            EV_FF in caps
        )

    def run(self) -> None:
        logger.info(f'Starting Purifier ...')

        # retry loop
        while True:
            try:
                # intercept all src events
                self._grab()

                # then process all src events
                for p in self._packages:
                    # TODO: filtering and remapping here

                    # passthrough all other irrelevant events
                    p.send(self._dst_dev)
            except OSError:
                logger.info('Device disconnected, retrying ...')
            except Exception as e:
                logger.error(e)
            # retry delay
            time.sleep(1)
