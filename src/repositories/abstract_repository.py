from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Sequence
from sqlalchemy import select

from .unit_of_work import SqlAlchemyUnitOfWork

T = TypeVar("T")
ID = TypeVar("ID")

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

class SqlAlchemyRepository(AbstractRepository[T, ID]):
    def __init__(self, unit_of_work: SqlAlchemyUnitOfWork, model_class: type[T]):
        self.model_class = model_class

        self.session = unit_of_work.session
    
    def add(self, entity: T):
        self.session.add(entity)

    def get(self, id: ID) -> Optional[T]:
        return self.session.get(self.model_class, id)
    
    def update(self, entity: T) -> None:
        # En SQLAlchemy, si la entidad ya está en la sesión, los cambios 
        # se detectan automáticamente. 'merge' es útil para re-adjuntar
        # objetos que vienen de fuera de la sesión.
        self.session.merge(entity)

    def list(self) -> Sequence[T]:
        # Usando la sintaxis moderna de SQLAlchemy 2.0
        statement = select(self.model_class)
        return self.session.scalars(statement).all()

    def delete(self, entity: T) -> None:
        self.session.delete(entity)