from enum import Enum
from typing import Self

from evdev.ecodes import ABS_RX, ABS_RY, EV_ABS, EV_KEY

from evdev_purify.package import Package
from evdev_purify.virtual_device import VirtualDevice


class Layer(Enum):
    BASE = 0
    LEFT = 1
    RIGHT = 2


class Counter:
    def __init__(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def tap(self) -> None:
        self._count += 1

    def reset(self) -> None:
        self._count = 0


class LayerCounter:
    def __init__(self, watermark: int = 5) -> None:
        self._watermark = watermark
        self._left = Counter()
        self._right = Counter()

    def tap_left(self) -> Layer:
        self._left.tap()
        self._right.reset()
        return Layer.LEFT if self._left.count >= self._watermark else Layer.BASE

    def tap_right(self) -> Layer:
        self._right.tap()
        self._left.reset()
        return Layer.RIGHT if self._right.count >= self._watermark else Layer.BASE

    def reset(self) -> Layer:
        self._left.reset()
        self._right.reset()
        return Layer.BASE


class LayerManager:
    def __init__(self, virtual_dev: VirtualDevice) -> None:
        self._virtual_dev = virtual_dev
        self._keydown_list: dict[Layer, set[int]] = {
            Layer.BASE: set(),
            Layer.LEFT: set(),
            Layer.RIGHT: set(),
        }
        # state
        self._layer = Layer.BASE
        self._layer_counter = LayerCounter()
        # self._layer_left_event_count = 0
        # self._layer_right_event_count = 0

    def __enter__(self) -> Self:
        self._layer = Layer.BASE
        return self

    def __exit__(self, *_) -> None:
        for layer in Layer:
            self.clear_layer(layer)

    @property
    def layer(self) -> Layer:
        return self._layer

    def clear_layer(self, layer: Layer) -> None:
        # send keyup events
        for key in self._keydown_list[layer]:
            self._virtual_dev.send_keyup(key)
        # clear the state
        self._keydown_list[layer].clear()

    def decide_layer(self, package: Package, *, threshold: float) -> None:
        # choose which layer based on the first event
        e = package[0]
        # new_layer = (
        #     # non axis signal, stay on the same level
        #     self._layer if e.type != EV_ABS else
        #     # axis signal except L2 or R2 axis signal, stay on the same level
        #     self._layer if e.code not in (ABS_RX, ABS_RY) else
        #     # L2 and larger than threshold, switch to left layer
        #     Layer.LEFT if e.code == ABS_RX and e.value >= threshold else
        #     # R2 and larger than threshold, switch to right layer
        #     Layer.RIGHT if e.code == ABS_RY and e.value >= threshold else
        #     # otherwise
        #     Layer.BASE
        # )

        # change state and choose a layer
        if e.type != EV_ABS:
            new_layer = self._layer
        elif e.code not in (ABS_RX, ABS_RY):
            new_layer = self._layer
        elif e.code == ABS_RX and e.value >= threshold:
            # self._layer_left_event_count += 1
            # new_layer = Layer.LEFT if self._layer_left_event_count >= 5 else Layer.BASE
            # self._layer_right_event_count = 0
            new_layer = self._layer_counter.tap_left()
        elif e.code == ABS_RY and e.value >= threshold:
            # self._layer_right_event_count += 1
            # new_layer = Layer.RIGHT if self._layer_right_event_count >= 5 else Layer.BASE
            # self._layer_left_event_count = 0
            new_layer = self._layer_counter.tap_right()
        else:
            # new_layer = Layer.BASE
            # self._layer_left_event_count = 0
            # self._layer_right_event_count = 0
            new_layer = self._layer_counter.reset()

        # if layer changed, clear previous layer
        if new_layer != self._layer:
            self.clear_layer(self._layer)
        # return new state
        self._layer = new_layer

    def record_keys(self, package: Package, *, layer: Layer) -> Package:
        for e in package:
            # record any key up event in the package
            if e.type == EV_KEY and e.value == 1:
                self._keydown_list[layer].add(e.code)
        # return package
        return package
