import logging
from enum import Enum
from typing import Iterator

from evdev import ecodes as ec

from evdev_purify.event import Event
from evdev_purify.package import Package

logger = logging.getLogger(__file__)


class Layer(Enum):
    BASE = 0
    LEFT = 1
    RIGHT = 2


BindingSource = int
BindingTarget = int | None
BindingTargets = tuple[BindingTarget, BindingTarget, BindingTarget]

BINDINGS: dict[BindingSource, BindingTargets] = {
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


def remap(
    package: Package,
    *,
    layer: Layer,
) -> Iterator[Event]:
    # check new code from map for every event in the package
    for e in package:
        # yield non key press events
        if e.type != ec.EV_KEY:
            yield e
            continue
        # yield and continue if binding targets is not defined
        code_map = BINDINGS.get(e.code, None)
        if code_map is None:
            yield e
            continue
        # try to replace a if code is defined in KEYMAP
        new_code = code_map[layer.value]
        if new_code is not None:
            e.code = new_code
            yield e
        # keymap is None, skip yield
        pass
