import logging

from evdev import UInput
from evdev import ecodes as ec
from evdev.ecodes import EV_KEY

from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)

KEYMAPS = {
    # L1
    292: ec.KEY_Z,
    # R1
    293: ec.KEY_X,

    # X
    290: None,
    # Y
    291: None,
    # A
    288: ec.KEY_ENTER,
    # B
    289: ec.KEY_ESC,

    # L3
    298: None,
    # R3
    299: None,

    # Task
    296: ec.KEY_C,
    # Function
    301: ec.KEY_L,
    # Menu
    297: None,

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

    def run(self) -> None:
        logger.info(f'Starting Purifier ...')

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
