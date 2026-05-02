import logging
from enum import Enum

from evdev import ecodes as ec

from evdev_purify.event import SyncEvent
from evdev_purify.package import Package

logger = logging.getLogger(__file__)


class Layer(Enum):
    BASE = 0
    LEFT = 1
    RIGHT = 2


KEYMAP = {
    # L1
    292: (ec.KEY_Q, None, None),
    # R1
    293: (ec.KEY_E, None, None),

    # X
    290: (ec.KEY_F, ec.KEY_5, None),
    # Y
    291: (ec.KEY_G, ec.KEY_6, None),
    # A
    288: (ec.KEY_ENTER, None, None),
    # B
    289: (ec.KEY_ESC, None, None),

    # L3
    298: (ec.KEY_Z, None, None),
    # R3
    299: (ec.KEY_X, None, None),

    # Task
    296: (ec.KEY_C, None, None),
    # Function
    301: (ec.KEY_V, None, None),
    # Menu
    297: (ec.KEY_B, None, None),

    # Home
    300: (ec.KEY_H, None, None),
}


def update(
    package: Package,
    *,
    layer: Layer,
) -> None:
    # check new code from map for every event in the package
    for e in package:
        try:
            # replace if new code is defined
            if (new_code := KEYMAP[e.code][layer.value]) is not None:
                e.code = new_code
        except KeyError:
            pass
