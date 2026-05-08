from enum import Enum
from typing import Iterator, Self

from evdev.ecodes import ABS_RX, ABS_RY, EV_ABS, EV_KEY

from evdev_purify.event import Event
from evdev_purify.package import Package
from evdev_purify.virtual_device import VirtualDevice


class Layer(Enum):
    BASE = 0
    LEFT = 1
    RIGHT = 2


class LayerManager:
    def __init__(self, virtual_dev: VirtualDevice) -> None:
        self._virtual_dev = virtual_dev
        self._keydown_list: dict[Layer, set[int]] = {
            Layer.BASE: set(),
            Layer.LEFT: set(),
            Layer.RIGHT: set(),
        }

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        pass

    def clear_layer(self, layer: Layer) -> None:
        # send keyup events
        for key in self._keydown_list[layer]:
            self._virtual_dev.send_keyup(key)
        # clear the state
        self._keydown_list[layer].clear()

    def decide_layer(self, package: Package, *, layer: Layer, threshold: float) -> Layer:
        # choose which layer based on the first event
        new_layer = (
            layer if package[0].type != EV_ABS else
            Layer.LEFT if package[0].code == ABS_RX and package[0].value >= threshold else
            Layer.RIGHT if package[0].code == ABS_RY and package[0].value >= threshold else
            Layer.BASE
        )

        # if layer changed, clear previous layer
        if new_layer != layer:
            self.clear_layer(layer)

        # return new state
        return new_layer

    def record_keys(self, package: Iterator[Event], *, layer: Layer) -> Iterator[Event]:
        for e in package:
            # record any key up event in the package
            if e.type == EV_KEY and e.value == 1:
                self._keydown_list[layer].add(e.code)
            # yield back all event
            yield e
