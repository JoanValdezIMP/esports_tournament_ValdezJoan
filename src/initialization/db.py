from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from .config import DB_URL

engine = create_engine(DB_URL) 


class Base(DeclarativeBase):
    ...