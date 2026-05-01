import logging
from collections import defaultdict

from evdev import InputDevice
from evdev.ecodes import EV, EV_MSC, EV_SYN, bytype

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
        max_event_interval: float,
    ) -> None:
        super().__init__(name)
        self._max_event_interval = max_event_interval
        self._last_timestamp: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))

    def _is_target(self, path: str | None) -> bool:
        if path is None:
            return False
        dev = InputDevice(path)
        return dev.name == self._name

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
        init_delay=0.5,
    )
    def run(self) -> None:
        with (
            RealDevice.find_or_wait_for(self._name, self._is_target, grab=True) as real_dev,
            VirtualDevice.from_device(real_dev, name=f'Purifier: {self._name}') as virtual_dev,
        ):
            # then process all src events
            for p in real_dev.packages(drop=(EV_MSC, )):
                # use the first event as the comparison target
                e = p[0]

                # intercept for non EV_SYN keydown event
                if e.type != EV_SYN and e.value == 1:
                    # calc the time interval from the last event with the same type and code
                    interval = e.timestamp - self._last_timestamp[e.type][e.code]
                    # move the timestamp to new position
                    self._last_timestamp[e.type][e.code] = e.timestamp
                    # if interval is too short, discard the packet
                    if interval < self._max_event_interval:
                        logger.info(f'DROP: time={interval*1000:.2f}ms, {EV[e.type]}, {bytype[e.type][e.code]}, {e.value=}')
                        continue

                # passthrough all other irrelevant events
                p.send(virtual_dev)
