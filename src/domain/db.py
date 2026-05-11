from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from datetime import datetime
from .config import DB_URL


# print(f"Intentando conectar a la base de datos con URL: {DB_URL}")

if DB_URL is None:
    raise ValueError("DB_URL must be set")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    # Al añadirlo aquí, todas las clases que heredan de Base lo tendrán
    last_update: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now, 
        nullable=True
    )
# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, sessionmaker

# # Pegamos la URL aquí directamente
# DB_URL = "postgresql+psycopg2://avnadmin:AVNS_RbP8a8oY-xsdJz4LhUc@pg-250affac-joan1234.d.aivencloud.com:14173/esports_torunament?sslmode=require"
# # src/domain/db.py
# engine = create_engine(DB_URL, echo=True)
# # engine = create_engine(DB_URL)
# Session = sessionmaker(bind=engine)

# class Base(DeclarativeBase):
#     pass