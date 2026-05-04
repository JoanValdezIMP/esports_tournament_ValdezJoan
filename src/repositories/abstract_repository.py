from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Sequence

T = TypeVar("T")       # Entity type
ID = TypeVar("ID")     # Identifier type


class AbstractRepository(ABC, Generic[T, ID]):
    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        pass

    @abstractmethod
    def get(self, id: ID) -> Optional[T]:
        pass

    @abstractmethod
    def list(self) -> Sequence[T]:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass


