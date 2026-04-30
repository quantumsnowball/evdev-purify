import logging
from collections import deque

from evdev import InputDevice
from evdev.ecodes import EV_REL, REL_WHEEL, REL_WHEEL_HI_RES

from evdev_purify.device import VirtualDevice
from evdev_purify.package import Package
from evdev_purify.purifier import Purifier as Base
from evdev_purify.retry import retry_loop

from .scheduler import Scheduler

logger = logging.getLogger(__file__)


class WheelBuffer:
    def __init__(
        self,
        dst_dev: VirtualDevice,
        *,
        delay: float,
        min_history_len: int,
        max_event_interval: float,
    ) -> None:
        self._dst_dev = dst_dev
        self._history = deque[Package]()
        self._last_timestamp = 0.0
        self._min_history_len = min_history_len
        self._max_event_interval = max_event_interval
        self._scheduler = Scheduler(delay=delay)

    def _fire(self) -> None:
        # pop value
        package = self._history.popleft()
        # write to dst dev
        package.send(self._dst_dev)
        # debug
        bd = '====' if package[0].is_modified else '    '
        logger.info(f"{f'     |{bd}>' if package[0].value > 0 else f'<{bd}|     '}")

    def append(self, package: Package) -> None:
        # choose the first event
        e = package[0]
        # reject too frequent event as noise
        interval = e.timestamp - self._last_timestamp
        self._last_timestamp = e.timestamp
        if interval < self._max_event_interval:
            self._scheduler.add_task(lambda: logger.info('     X     '))
            return
        # follow vote if already have enough history
        if len(self._history) > self._min_history_len:
            # pick high res version as stats
            window = tuple(e.value for p in self._history for e in p
                           if e.code == REL_WHEEL_HI_RES)
            # modify the sign of the events
            sign = +1 if sum(window) >= 0 else -1
            for e in package:
                if e.value != 0:
                    e.value = sign*abs(e.value)
                    # print(f'{sign=} {e.value=} {e.old_value=}')
        # append the event to history
        self._history.append(package)
        # schedule the event
        self._scheduler.add_task(self._fire)


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        delay: float,
        min_history_len: int,
        max_event_interval: float,
    ) -> None:
        super().__init__(name)
        self._delay = delay
        self._min_history_len = min_history_len
        self._max_event_interval = max_event_interval

    def _is_targeted_device(self, dev: InputDevice) -> bool:
        return dev.name == self._name

    @retry_loop(
        welcome_message='Starting Purifier ...',
        oserror_message='Device disconnected, retrying ...',
        init_delay=0.5,
    )
    def run(self) -> None:
        # intercept all src events
        self._grab()

        with VirtualDevice.from_device(self._src_dev, name=f'Purifier: {self._name}') as dst_dev:
            # buffer for each dst_dev created
            wheel_buffer = WheelBuffer(
                dst_dev,
                delay=self._delay,
                min_history_len=self._min_history_len,
                max_event_interval=self._max_event_interval,
            )
            # then process all src events
            for p in self._packages:
                # use the first event as to classify package
                e = p[0]
                # filter out wheel scroll relevant events
                if e.type == EV_REL and (e.code == REL_WHEEL or e.code == REL_WHEEL_HI_RES):
                    wheel_buffer.append(p)
                    # debug
                    # print(f"src_dev: {' |-' if e.value > 0 else '-| '}")
                    continue

                # passthrough all other irrelevant events
                p.send(dst_dev)
