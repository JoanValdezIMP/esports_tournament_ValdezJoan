# src/domain/db.py
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from datetime import datetime
from .config import DB_URL

# ❌ ATENCIÓN: NO importamos UnitOfWorkFactory aquí arriba.

if DB_URL is None:
    raise ValueError("DB_URL must be set")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    last_update: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now, 
        nullable=True
    )

# 1. Declaramos la variable vacía
_uow_factory = None

def get_uow():
    """
    Fábrica del Unit of Work con inicialización perezosa (Lazy).
    Evita importaciones circulares al no cargar los repositorios hasta que se usa.
    """
    global _uow_factory
    
    # 2. La primera vez que alguien llame a la función, importamos y creamos la fábrica
    if _uow_factory is None:
        # ✅ AQUÍ ADENTRO ES DONDE VA LA IMPORTACIÓN
        from repositories.unit_of_work import UnitOfWorkFactory
        _uow_factory = UnitOfWorkFactory(DB_URL)
        
    return _uow_factory.create()