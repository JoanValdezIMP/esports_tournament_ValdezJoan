from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class AbstractUnitOfWork(ABC):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Session):
        self.session: Session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

class UnitOfWorkFactory:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.session_class = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def create(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_class())