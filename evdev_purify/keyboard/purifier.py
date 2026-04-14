import logging
import time
from collections import defaultdict
from typing import Iterator

import evdev
from evdev import InputDevice, UInput
from evdev.ecodes import EV, EV_SYN, bytype

from evdev_purify.package import Package

logger = logging.getLogger(__file__)


class Purifier:
    def __init__(
        self,
        name: str,
        *,
        max_event_interval: float,
    ) -> None:
        self._max_event_interval = max_event_interval
        paths = {InputDevice(path).name: path for path in evdev.list_devices()}
        self._src_dev_path = paths[name]
        self._src_dev = InputDevice(self._src_dev_path)
        self._dst_dev = UInput.from_device(self._src_dev, name=f'Purifier: {name}')
        self._last_timestamp: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))

    @property
    def _packages(self) -> Iterator[Package]:
        p = Package()
        for e in self._src_dev.read_loop():
            p.append(e)
            if e.type == EV_SYN:
                yield p
                p = Package()

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
            # use the first event as the comparison target
            e = p[0]

            # intercept for non EV_SYN keydown event
            if e.type != EV_SYN and e.value == 1:
                # calc the time interval from the last event with the same type and code
                interval = e.timestamp() - self._last_timestamp[e.type][e.code]
                # move the timestamp to new position
                self._last_timestamp[e.type][e.code] = e.timestamp()
                # if interval is too short, discard the packet
                if interval < self._max_event_interval:
                    logger.info(f'DROP: time={interval*1000:.2f}ms, {EV[e.type]}, {bytype[e.type][e.code]}, {e.value=}')
                    continue

            # passthrough all other irrelevant events
            p.send(self._dst_dev)
