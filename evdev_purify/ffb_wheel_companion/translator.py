from evdev.ecodes import (
    ABS_HAT0X,
    ABS_HAT0Y,
    BTN_EAST,
    BTN_NORTH,
    BTN_SOUTH,
    BTN_WEST,
    EV_ABS,
    EV_KEY,
)

from evdev_purify.package import Package


def translate(
    package: Package,
    *,
    dpadX: int,
    dpadY: int,
) -> tuple[int, int]:
    # copy of current state
    new_dpadX, new_dpadY = dpadX, dpadY
    # loop though each event
    for e in package:
        # focus on EV_ABS
        if e.type == EV_ABS:
            # on dpad left/right axis
            if e.code == ABS_HAT0X:
                if e.value == +1:
                    # right pressed, translate to east
                    e.type, e.code, e.value = EV_KEY, BTN_EAST, 1
                    new_dpadX = +1
                elif e.value == -1:
                    # left pressed, translate to west
                    e.type, e.code, e.value = EV_KEY, BTN_WEST, 1
                    new_dpadX = -1
                else:
                    # release, translate to previous direction release
                    e.type, e.value = EV_KEY, 0
                    e.code = BTN_EAST if dpadX == 1 else BTN_WEST
                    new_dpadX = 0
            # on dpad left/right axis
            elif e.code == ABS_HAT0Y:
                if e.value == +1:
                    # down pressed, translate to south
                    e.type, e.code, e.value = EV_KEY, BTN_SOUTH, 1
                    new_dpadY = +1
                elif e.value == -1:
                    # up pressed, translate to north
                    e.type, e.code, e.value = EV_KEY, BTN_NORTH, 1
                    new_dpadY = -1
                else:
                    # release, translate to previous direction release
                    e.type, e.value = EV_KEY, 0
                    e.code = BTN_SOUTH if dpadY == 1 else BTN_NORTH
                    new_dpadY = 0

    # return new state
    return new_dpadX, new_dpadY
