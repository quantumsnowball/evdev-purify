import logging
from typing import Any, override

from evdev import InputDevice

logger = logging.getLogger(__file__)


class RealDevice(InputDevice):
    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.info(f'Created: {str(self)}')

    def __str__(self):
        return f"RealDevice('{self.device.path}', name='{self.device.name}')"
