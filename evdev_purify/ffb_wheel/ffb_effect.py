import logging
import threading
from typing import Self

from evdev.ecodes import EV_FF, EV_UINPUT, UI_FF_ERASE, UI_FF_UPLOAD

from evdev_purify.device import VirtualDevice
from evdev_purify.real_device import RealDevice

logger = logging.getLogger(__file__)


class FFBEffectManager:
    def __init__(
        self,
        real_dev: RealDevice,
        virtual_dev: VirtualDevice,
    ) -> None:
        self._real_dev = real_dev
        self._virtual_dev = virtual_dev
        self._effects = set[int]()
        self._thread = threading.Thread(target=self._worker, daemon=True)

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *_) -> None:
        self._virtual_dev.stop()

    def _worker(self) -> None:
        try:
            for event in self._virtual_dev.read_loop():
                # Handle the special uinput events
                if event.type == EV_UINPUT:
                    # ff upload
                    if event.code == UI_FF_UPLOAD:
                        upload = self._virtual_dev.begin_upload(event.value)

                        # Checks if this is a new effect
                        if upload.effect.id not in self._effects:
                            self._effects.add(upload.effect.id)
                            # Setting id to 1 indicates that a new effect must be allocated
                            upload.effect.id = -1

                        self._real_dev.upload_effect(upload.effect)
                        upload.retval = 0
                        self._virtual_dev.end_upload(upload)
                    # ff erase
                    elif event.code == UI_FF_ERASE:
                        erase = self._virtual_dev.begin_erase(event.value)
                        erase.retval = 0
                        self._real_dev.erase_effect(erase.effect_id)
                        self._effects.remove(erase.effect_id)
                        self._virtual_dev.end_erase(erase)
                # Forward writes to actual rumble device.
                elif event.type == EV_FF:
                    self._real_dev.write(event.type, event.code, event.value)
        except OSError:
            logger.info(f'read_loop is broken, exiting loop ...')
        except Exception as e:
            logger.error(e)
