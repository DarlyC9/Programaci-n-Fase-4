from abc import ABC, abstractmethod


class Entity(ABC):
    def __init__(self, identifier: str, name: str) -> None:
        self._identifier = identifier.strip()
        self._name = name.strip()

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def summary(self) -> str:
        """Return a short human-readable description of the entity."""
