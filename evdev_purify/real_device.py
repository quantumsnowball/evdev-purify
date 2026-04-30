import logging
from typing import Any, Iterator, Self, override

from evdev import InputDevice
from evdev.ecodes import EV_SYN

from .package import Event, Package

logger = logging.getLogger(__file__)


class RealDevice(InputDevice):
    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.info(f'Created: {str(self)}')

    def __str__(self):
        return f"RealDevice('{self.device.path}', name='{self.device.name}')"

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        pass

    @property
    def packages(self) -> Iterator[Package]:
        try:
            package = Package()
            for e in self.read_loop():
                # append as custom Event type
                package.append(Event(e))
                if e.type == EV_SYN:
                    yield package
                    package = Package()
        except OSError:
            logger.info(f'Disconnected: {str(self)}')
        except Exception as e:
            logger.error(e)
