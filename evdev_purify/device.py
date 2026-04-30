import logging
import os
import select
from typing import Iterator

from evdev import InputEvent, UInput

logger = logging.getLogger(__file__)


class VirtualDevice(UInput):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pipe_r, self._pipe_w = os.pipe()

    def read_loop_stoppable(self) -> Iterator[InputEvent]:
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

    def stop_loop(self):
        # Write a 'kick' byte to wake up select.select
        try:
            os.write(self._pipe_w, b'\x01')
        except OSError:
            pass

    def close(self):
        # overrides UInput.close to ensure the loop stops and pipe is cleaned
        self.stop_loop()
        super().close()
