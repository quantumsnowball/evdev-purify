# /// script
# dependencies = [
#   "typer",
#   "evdev",
# ]
# ///
import logging
import statistics
import threading
import time
from collections import deque

from evdev import InputDevice
from evdev.ecodes import EV_REL, REL_WHEEL, REL_WHEEL_HI_RES
from evdev.events import InputEvent

from evdev_purify.package import Package
from evdev_purify.purifier import Purifier as Base

logger = logging.getLogger(__file__)


class WheelBuffer:
    def __init__(
        self,
        dst_dev: InputDevice,
        *,
        delay: float,
        min_history_len: int,
        max_event_interval: float,
    ) -> None:
        self._dst_dev = dst_dev
        self._delay = delay
        self._history = deque[Package]()
        self._last_timestamp = 0.0
        self._min_history_len = min_history_len
        self._max_event_interval = max_event_interval

    def _fire(self) -> None:
        # pop value
        package = self._history.popleft()
        # write to dst dev
        package.send(self._dst_dev)
        # debug
        logger.info(f"{'     |---->' if package[0].value > 0 else '<----|     '}")

    def append(self, package: Package) -> None:
        # choose the first event
        e = package[0]
        # reject too frequent event as noise
        interval = e.timestamp() - self._last_timestamp
        self._last_timestamp = e.timestamp()
        if interval < self._max_event_interval:
            logger.info('     X     ')
            return
        # follow vote if already have enough history
        if len(self._history) > self._min_history_len:
            # pick high res version as stats
            window = tuple(e.value for e in package if e.code == REL_WHEEL_HI_RES)
            # modify the sign of the events
            sign = +1 if sum(window) > 0 else -1
            for e in package:
                if e.value != 0:
                    e.value = sign*abs(e.value)
        # append the event to history
        self._history.append(package)
        # timer schedule the event
        t = threading.Timer(self._delay, self._fire)
        t.start()


class Purifier(Base):
    def __init__(
        self,
        name: str,
        *,
        delay: float,
        min_history_len: int,
        max_event_interval: float,
    ) -> None:
        super().__init__(name, max_event_interval=max_event_interval)
        self._wheel_buffer = WheelBuffer(
            self._dst_dev,
            delay=delay,
            min_history_len=min_history_len,
            max_event_interval=max_event_interval,
        )

    def run(self) -> None:
        logger.info(f'Starting Purifier on {self._src_dev_path} ...')
        # small delay befoe grab, avoid command Enter release being capped
        # NOTE: please press enter key quickly
        time.sleep(0.5)
        # intercept all src events
        logger.info(f'Grabbed {self._src_dev_path}')
        self._src_dev.grab()

        # then process all src events
        for p in self._packages:
            # use the first event as to classify package
            e = p[0]
            # filter out wheel scroll relevant events
            if e.type == EV_REL and (e.code == REL_WHEEL or e.code == REL_WHEEL_HI_RES):
                self._wheel_buffer.append(p)
                # debug
                # print(f"src_dev: {' |-' if e.value > 0 else '-| '}")
                continue

            # passthrough all other irrelevant events
            p.send(self._dst_dev)
