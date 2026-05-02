import logging

from evdev import InputDevice
from evdev.ecodes import EV_ABS, EV_FF, EV_KEY, EV_MSC

from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop
from evdev_purify.virtual_device import VirtualDevice

from .remapper import Layer, remap
from .translator import translate

logger = logging.getLogger(__file__)


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        log_threshold: int,
    ) -> None:
        super().__init__(name)
        self._log_threshold = log_threshold
        self._layer = Layer.BASE
        self._dpadX = 0
        self._dpadY = 0

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
        ):
            # look at all src events and process them
            for package in real_dev.packages(drop=(EV_MSC, )):
                # see if L2 or R2 is pressed, should activate the layer states
                if package[0].is_L2:
                    self._layer = Layer.LEFT if package[0].value >= 32768 else Layer.BASE
                if package[0].is_R2:
                    self._layer = Layer.RIGHT if package[0].value >= 32768 else Layer.BASE

                # translate dpad into custom key events and update dpad state
                self._dpadX, self._dpadY = translate(package, dpadX=self._dpadX, dpadY=self._dpadY)

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
                    # then send the package to new device
                    virtual_dev.send(remapped_package)
