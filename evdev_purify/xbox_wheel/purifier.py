import logging

from evdev import AbsInfo, InputDevice
from evdev.ecodes import ABS_X, EV_ABS, EV_FF, EV_KEY, EV_MSC, EV_SYN

from evdev_purify.purifier import Purifier as Base
from evdev_purify.real_device import RealDevice
from evdev_purify.retry import retry_loop
from evdev_purify.virtual_device import VirtualDevice

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

    def _is_target(self, path: str | None) -> bool:
        if path is None:
            return False
        dev = InputDevice(path)
        return dev.name == self._name

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
    )
    def run(self) -> None:
        with (
            RealDevice.find_or_wait_for(self._name, self._is_target, grab=True) as real_dev,
            # VirtualDevice.from_device(real_dev, name=f'Pure: {self._name}') as virtual_dev,
        ):
            virtual_caps = dict(real_dev.capabilities())
            virtual_caps[EV_ABS] = [
                (ABS_X, AbsInfo(128, 0, 255, 0, 15, 0)) if itm[0] == ABS_X else itm
                for itm in virtual_caps[EV_ABS]
            ]
            for ev in (EV_SYN, EV_FF):
                if ev in virtual_caps:
                    del virtual_caps[ev]
            with VirtualDevice(events=virtual_caps, name=f'Pure: {self._name}') as virtual_dev:
                # then process all src events
                for package in real_dev.packages(drop=(EV_MSC, )):
                    # scale the wheel into 0 to 255 low resolutio thumb stick events
                    for e in package:
                        if e.type == EV_ABS and e.code == ABS_X:
                            e.value = (e.value + 32768) // 256
                    # if a package contains more than one EV_KEY event, consider these noise
                    if package.count(EV_KEY) > 1:
                        # only log very high event count package for debug purpose
                        if package.items_count >= self._log_threshold:
                            logger.info(f'BIG: {package}')
                        # skip to next
                        continue
                    # passthrough all other irrelevant events
                    virtual_dev.send(package)
