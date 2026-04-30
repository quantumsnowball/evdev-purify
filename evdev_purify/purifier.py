import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__file__)


class Purifier(ABC):
    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def _is_target(self, path: str | None) -> bool:
        ...

    @abstractmethod
    def run(self) -> None:
        ...
