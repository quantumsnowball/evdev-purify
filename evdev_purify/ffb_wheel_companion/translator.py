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
    dpad: tuple[int, int],
) -> tuple[int, int]:
    # create a copy of current state
    dpad_x, dpad_y = dpad
    # loop though each event
    for e in package:
        # focus on EV_ABS
        if e.type == EV_ABS:
            # on dpad left/right axis
            if e.code == ABS_HAT0X:
                if e.value == +1:
                    # right pressed, translate to east
                    e.type, e.code, e.value = EV_KEY, BTN_EAST, 1
                    dpad_x = +1
                elif e.value == -1:
                    # left pressed, translate to west
                    e.type, e.code, e.value = EV_KEY, BTN_WEST, 1
                    dpad_x = -1
                else:
                    # release, translate to previous direction release
                    e.type, e.value = EV_KEY, 0
                    e.code = BTN_EAST if dpad_x == 1 else BTN_WEST
                    dpad_x = 0
            # on dpad left/right axis
            elif e.code == ABS_HAT0Y:
                if e.value == +1:
                    # down pressed, translate to south
                    e.type, e.code, e.value = EV_KEY, BTN_SOUTH, 1
                    dpad_y = +1
                elif e.value == -1:
                    # up pressed, translate to north
                    e.type, e.code, e.value = EV_KEY, BTN_NORTH, 1
                    dpad_y = -1
                else:
                    # release, translate to previous direction release
                    e.type, e.value = EV_KEY, 0
                    e.code = BTN_SOUTH if dpad_y == 1 else BTN_NORTH
                    dpad_y = 0

    # return new state
    return dpad_x, dpad_y
