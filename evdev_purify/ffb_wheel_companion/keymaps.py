import logging
from enum import Enum

from evdev import ecodes as ec

from evdev_purify.package import Package

logger = logging.getLogger(__file__)


class Layer(Enum):
    BASE = 0
    LEFT = 1
    RIGHT = 2


class Keymap:
    base = {
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


def update(
    package: Package,
    *,
    layer: Layer,
) -> None:
    logger.info(f'{layer=}')
    # check new code from map for every event in the package
    for e in package:
        try:
            # replace if new code is defined
            if (new_code := Keymap.base[e.code]) is not None:
                e.code = new_code
        except KeyError:
            pass
