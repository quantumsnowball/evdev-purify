import logging
import threading

from evdev import InputDevice, UInput

logger = logging.getLogger(__file__)


class FFBEffectManager:
    def __init__(
        self,
        src_dev: InputDevice,
        dst_dev: UInput,
    ) -> None:
        self._src_dev = src_dev
        self._dst_dev = dst_dev
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self) -> None:
        logger.info('ffb effect manager starting monitoring game effect events ...')
        try:
            for event in self._dst_dev.read_loop():

                # do all ffb related event and passthrough to src_dev
                pass
        except Exception:
            logger.info('dst_dev closed, breaking loop ...')
        finally:
            logger.info('ffb effect manager has stopped, exiting ...')
