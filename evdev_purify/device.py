import logging
import os
import select
from typing import Iterator, Self, override

from evdev import InputDevice, InputEvent, UInput
from evdev.ecodes import EV_FF, EV_SYN

logger = logging.getLogger(__file__)


class VirtualDevice(UInput):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pipe_r, self._pipe_w = os.pipe()

    @override
    def read_loop(self) -> Iterator[InputEvent]:
        ''' overrided version of read_loop that can receive a stop signal and return'''
        try:
            while True:
                # this should return if any one of the files is ready
                rlist, _, _ = select.select([self.fd, self._pipe_r], [], [])

                # watch for manual exit event
                for fd in rlist:
                    if fd == self.fd:
                        # normal device event pipe
                        for event in self.read():
                            yield event
                    elif fd == self._pipe_r:
                        # pop the signal byte from the pipe
                        os.read(self._pipe_r, 1)
                        logger.info('VirtualDevice: Stop signal received.')
                        # break both for loop and while loop at once
                        return
        finally:
            try:
                os.close(self._pipe_r)
                os.close(self._pipe_w)
            except OSError:
                pass

    def stop(self):
        # Write a 'kick' byte to wake up select.select
        try:
            os.write(self._pipe_w, b'\x01')
        except OSError:
            pass

    @override
    def close(self):
        # overrides UInput.close to ensure the loop stops and pipe is cleaned
        self.stop()
        self.close()

    @override
    @classmethod
    def from_device(
        cls,
        *devices: InputDevice | str | bytes | os.PathLike,
        filtered_types: tuple[int, ...] = (EV_SYN, EV_FF),
        **kwargs,
    ) -> Self:
        # reuse the parent from_device logics to create a VirtualDevice instance
        return super(VirtualDevice, cls).from_device(
            *devices,
            filtered_types=filtered_types,  # type: ignore
            **kwargs
        )
