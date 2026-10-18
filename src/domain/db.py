# src/domain/db.py
from sqlalchemy import create_engine, DateTime

# Keep the in-memory database available for the application's lifetime.
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from datetime import datetime
from .config import DB_URL

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=True
    )


_uow_factory = None


def get_uow():
    """
    Create a unit of work backed by the shared in-memory database engine.
    """
    global _uow_factory

    if _uow_factory is None:
        from repositories.unit_of_work import UnitOfWorkFactory

        _uow_factory = UnitOfWorkFactory(engine)

    return _uow_factory.create()
