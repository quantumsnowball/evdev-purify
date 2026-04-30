import logging
import time

from evdev import InputDevice, UInput
from evdev import ecodes as ec
from evdev.ecodes import EV_ABS, EV_FF, EV_KEY

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)

KEYMAPS = {
    # L1
    292: ec.KEY_Q,
    # R1
    293: ec.KEY_E,

    # X
    290: ec.KEY_F,
    # Y
    291: ec.KEY_G,
    # A
    288: ec.KEY_ENTER,
    # B
    289: ec.KEY_ESC,

    # L3
    298: ec.KEY_Z,
    # R3
    299: ec.KEY_X,

    # Task
    296: ec.KEY_C,
    # Function
    301: ec.KEY_V,
    # Menu
    297: ec.KEY_B,

    # Home
    300: ec.KEY_H,
}


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        log_threshold: int,
    ) -> None:
        super().__init__(name)
        self._log_threshold = log_threshold
        self._dst_dev = UInput(name=f'Purifier: {name}')

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
                # intercept all src events and process them
                for p in self._packages:
                    # skip and log multiple events packages
                    if len(p) > 1:
                        # only log very high event count package for debug purpose
                        if len(p) >= self._log_threshold:
                            logger.info(f'BIG: {p}')
                        # skip to next
                        continue

                    # only interested in single event key-press package
                    if p.types == {EV_KEY, }:
                        # check new code from map
                        if (new_code := KEYMAPS[p[0].code]) is not None:
                            # replace if new code is defined
                            p[0].code = new_code
                            # then send the code to new device
                            p.send(self._dst_dev)
            except OSError:
                logger.info('Device disconnected, retrying ...')
            except Exception as e:
                logger.error(e)
            # retry delay
            time.sleep(1)
