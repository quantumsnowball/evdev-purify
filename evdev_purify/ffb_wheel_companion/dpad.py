from typing import Self

from evdev.ecodes import (
    ABS_HAT0X,
    ABS_HAT0Y,
    BTN_DPAD_DOWN,
    BTN_DPAD_LEFT,
    BTN_DPAD_RIGHT,
    BTN_DPAD_UP,
    EV_ABS,
    EV_KEY,
)

from evdev_purify.package import Package


class DpadManager:
    def __init__(self) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        pass

    def translate(
        self,
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
                        # right pressed, translate to dpad right
                        e.type, e.code, e.value = EV_KEY, BTN_DPAD_RIGHT, 1
                        dpad_x = +1
                    elif e.value == -1:
                        # left pressed, translate to dpad left
                        e.type, e.code, e.value = EV_KEY, BTN_DPAD_LEFT, 1
                        dpad_x = -1
                    else:
                        # release, translate to previous direction release
                        e.type, e.value = EV_KEY, 0
                        e.code = BTN_DPAD_RIGHT if dpad_x == 1 else BTN_DPAD_LEFT
                        dpad_x = 0
                # on dpad left/right axis
                elif e.code == ABS_HAT0Y:
                    if e.value == +1:
                        # down pressed, translate to dpad down
                        e.type, e.code, e.value = EV_KEY, BTN_DPAD_DOWN, 1
                        dpad_y = +1
                    elif e.value == -1:
                        # up pressed, translate to dpad up
                        e.type, e.code, e.value = EV_KEY, BTN_DPAD_UP, 1
                        dpad_y = -1
                    else:
                        # release, translate to previous direction release
                        e.type, e.value = EV_KEY, 0
                        e.code = BTN_DPAD_DOWN if dpad_y == 1 else BTN_DPAD_UP
                        dpad_y = 0

        # return new state
        return dpad_x, dpad_y
