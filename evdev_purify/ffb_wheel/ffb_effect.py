import logging
import threading

from evdev import InputDevice, UInput
from evdev.ecodes import EV_FF, EV_UINPUT, UI_FF_ERASE, UI_FF_UPLOAD

logger = logging.getLogger(__file__)


class FFBEffectManager:
    def __init__(
        self,
        src_dev: InputDevice,
        dst_dev: UInput,
    ) -> None:
        self._src_dev = src_dev
        self._dst_dev = dst_dev
        self._effects = set[int]()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self) -> None:
        logger.info('ffb effect manager starting monitoring game effect events ...')
        try:
            for event in self._dst_dev.read_loop():
                # Handle the special uinput events
                if event.type == EV_UINPUT:
                    # ff upload
                    if event.code == UI_FF_UPLOAD:
                        upload = self._dst_dev.begin_upload(event.value)

                        # Checks if this is a new effect
                        if upload.effect.id not in self._effects:
                            self._effects.add(upload.effect.id)
                            # Setting id to 1 indicates that a new effect must be allocated
                            upload.effect.id = -1

                        self._src_dev.upload_effect(upload.effect)
                        upload.retval = 0
                        self._dst_dev.end_upload(upload)
                    # ff erase
                    elif event.code == UI_FF_ERASE:
                        erase = self._dst_dev.begin_erase(event.value)
                        erase.retval = 0
                        self._src_dev.erase_effect(erase.effect_id)
                        self._effects.remove(erase.effect_id)
                        self._dst_dev.end_erase(erase)
                # Forward writes to actual rumble device.
                elif event.type == EV_FF:
                    self._src_dev.write(event.type, event.code, event.value)
        except Exception:
            logger.info('dst_dev closed, breaking loop ...')
        finally:
            logger.info('ffb effect manager has stopped, exiting ...')
