import logging
from abc import ABC, abstractmethod

from evdev import InputDevice

logger = logging.getLogger(__file__)


class Purifier(ABC):
    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def _is_targeted_device(self, dev: InputDevice) -> bool:
        ...

    @abstractmethod
    def run(self) -> None:
        ...
