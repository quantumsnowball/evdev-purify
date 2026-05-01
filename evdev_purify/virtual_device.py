import logging
import os
import select
from typing import Any, Iterator, Self, override

from evdev import InputDevice, InputEvent, UInput
from evdev.ecodes import EV_FF, EV_SYN

logger = logging.getLogger(__file__)


class VirtualDevice(UInput):
    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.info(f'Created {self}')

    def __str__(self):
        return f"VirtualDevice('{self.device.path}', '{self.device.name}')"

    def __enter__(self) -> Self:
        self._pipe_r, self._pipe_w = os.pipe()
        logger.info(f'os.pipe created (read={self._pipe_r}, write={self._pipe_w})')
        return self

    def __exit__(self, *_) -> None:
        # stop signal
        self.stop()
        # cleanup pipes
        try:
            os.close(self._pipe_r)
            os.close(self._pipe_w)
            logger.info(f'os.pipe closed')
        except OSError:
            pass
        # parent close
        super().close()

    def stop(self) -> None:
        # signal stop
        try:
            os.write(self._pipe_w, b'\x01')
            logger.info('Stop bytes sent')
        except OSError:
            pass

    @override
    def read_loop(self) -> Iterator[InputEvent]:
        ''' overrided version of read_loop that can receive a stop signal and return'''
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
                    logger.info('Stop signal received')
                    # break both for loop and while loop at once
                    return

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
