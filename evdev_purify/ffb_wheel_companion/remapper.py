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
    # L1, code 292
    ec.BTN_TOP2: (ec.KEY_Q, ec.KEY_N, ec.KEY_I),
    # R1, code 293
    ec.BTN_PINKIE: (ec.KEY_E, ec.KEY_P, ec.KEY_O),

    # Down, code 304
    ec.BTN_SOUTH: (ec.KEY_DOWN, ec.KEY_J, ec.KEY_S),
    # Up, code 307
    ec.BTN_NORTH: (ec.KEY_UP, ec.KEY_K, ec.KEY_W),
    # Right, code 305
    ec.BTN_EAST: (ec.KEY_RIGHT, ec.KEY_L, ec.KEY_D),
    # Left, code 308
    ec.BTN_WEST: (ec.KEY_LEFT, ec.KEY_H, ec.KEY_A),

    # X, code 290
    ec.BTN_THUMB2: (ec.KEY_F, ec.KEY_R, ec.KEY_COMMA),
    # Y, code 291
    ec.BTN_TOP: (ec.KEY_G, ec.KEY_T, ec.KEY_DOT),
    # A, code 288
    ec.BTN_TRIGGER: (ec.KEY_ENTER, ec.KEY_Y, ec.KEY_SLASH),
    # B, code 289
    ec.BTN_THUMB: (ec.KEY_ESC, ec.KEY_U, ec.KEY_SEMICOLON),

    # L3, code 298
    ec.BTN_BASE5: (ec.KEY_Z, ec.KEY_1, ec.KEY_2),
    # R3, code 299
    ec.BTN_BASE6: (ec.KEY_X, ec.KEY_3, ec.KEY_4),

    # Task, code 296
    ec.BTN_BASE3: (ec.KEY_C, ec.KEY_5, ec.KEY_6),
    # Menu, code 297
    ec.BTN_BASE4: (ec.KEY_B, ec.KEY_7, ec.KEY_8),
    # Function, code 301
    301: (ec.KEY_V, ec.KEY_9, ec.KEY_0),

    # Home, code 300
    300: (ec.KEY_M, ec.KEY_TAB, ec.KEY_SPACE),
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
