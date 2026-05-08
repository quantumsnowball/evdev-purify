import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_KEY, EV_MSC

from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop
from evdev_purify.virtual_device import VirtualDevice

from .layer import Layer, LayerManager
from .remapper import remap
from .translator import translate

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        layer_activation: float,
        log_threshold: int,
    ) -> None:
        super().__init__(name)
        self._layer_threshold = layer_activation * 65535
        self._log_threshold = log_threshold
        # state
        self._layer = Layer.BASE
        self._dpad: tuple[int, int] = (0, 0)

    def _is_target(self, path: str | None) -> bool:
        if path is None:
            return False
        dev = InputDevice(path)
        caps = dev.capabilities()
        return (
            dev.name == self._name and
            EV_ABS in caps and
            EV_FF in caps
        )

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
    )
    def run(self) -> None:
        with (
            RealDevice.find_or_wait_for(self._name, self._is_target, grab=False) as real_dev,
            VirtualDevice(name=f'Pure: {self._name} - Keyboard') as virtual_dev,
            LayerManager(virtual_dev) as layer_manager,
        ):
            # look at all src events and process them
            for package in real_dev.packages(drop=(EV_MSC, )):
                # see if L2 or R2 is pressed, should activate the layer states
                self._layer = layer_manager.decide_layer(package, layer=self._layer, threshold=self._layer_threshold)

                # translate dpad into custom key events and update dpad state
                self._dpad = translate(package, dpad=self._dpad)

                # if a package contains more than one EV_KEY event, consider these noise
                if package.count(EV_KEY) > 1:
                    # only log very high event count package for debug purpose
                    if len(package) >= self._log_threshold:
                        logger.info(f'BIG: {package}')
                    # skip to next
                    continue

                # only interested in single event key-press package
                if package.count(EV_KEY) == 1:
                    # modify the package according to keymaps
                    remapped_package = remap(package, layer=self._layer)
                    # record key state
                    recorded_package = layer_manager.record_keys(remapped_package, layer=self._layer)
                    # then send the package to new device
                    virtual_dev.send(recorded_package)
