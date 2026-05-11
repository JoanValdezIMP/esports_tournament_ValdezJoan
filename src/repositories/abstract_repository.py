from abc import ABC, abstractmethod
from importlib.metadata.diagnose import inspect
from typing import Optional, Sequence
from typing import Generic, TypeVar, Optional, Sequence
from sqlalchemy import select, inspect, String

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
    def get_all(self) -> Sequence[T]:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass

class SqlAlchemyRepository(AbstractRepository[T, ID]):
    def __init__(self, unit_of_work: SqlAlchemyUnitOfWork, model_class: type[T]):
        self.model_class = model_class

        self.session = unit_of_work.session
    
    def _validate_against_mapping(self, entity: T) -> None:
            """
            Inspecciona dinámicamente el modelo y valida SOLO las restricciones 
            definidas en el mapeo (Nullabilidad y Longitud de Strings).
            """
            mapper = inspect(self.model_class)
            
            for column_prop in mapper.column_attrs:
                column = column_prop.columns[0]
                value = getattr(entity, column.key, None)

                # 1. Validación de Nullabilidad (nullable=False)
                if not column.nullable and value is None:
                    # Ignoramos la validación si la columna es una Primary Key (se autogenera)
                    # o si tiene un default definido en el modelo (ej: default=True, default=0)
                    if not column.primary_key and column.default is None and column.server_default is None:
                        raise ValueError(
                            f"Error en {self.model_class.__name__}: El campo '{column.key}' "
                            f"está marcado como 'nullable=False' y no puede ser nulo."
                        )

                # 2. Validación de Longitud de Cadenas (String(X))
                if isinstance(column.type, String) and column.type.length and value is not None:
                    if len(str(value)) > column.type.length:
                        raise ValueError(
                            f"Error en {self.model_class.__name__}: El campo '{column.key}' "
                            f"excede la longitud máxima permitida de {column.type.length} caracteres "
                            f"(Recibido: {len(str(value))} caracteres)."
                        )


    def add(self, entity: T):
        self.session.add(entity)

    def get(self, id: ID) -> Optional[T]:
        return self.session.get(self.model_class, id)
    
    def update(self, entity: T) -> None:
        # En SQLAlchemy, si la entidad ya está en la sesión, los cambios 
        # se detectan automáticamente. 'merge' es útil para re-adjuntar
        # objetos que vienen de fuera de la sesión.
        self.session.merge(entity)

    def get_all(self) -> Sequence[T]: 
        statement = select(self.model_class)
        return self.session.scalars(statement).all()
    

    def delete(self, entity: T) -> None: 
        self.session.delete(entity)