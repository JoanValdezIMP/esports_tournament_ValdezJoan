from sqlalchemy import select
from typing import Sequence, Optional
from models import VideoGameType
from .abstract_repository import SqlAlchemyRepository

class SqlAlchemyVideoGameTypeRepository(SqlAlchemyRepository[VideoGameType, int]):
    
    def get_by_name(self, name: str) -> Optional[VideoGameType]:
        """
        Busca un tipo de videojuego por su nombre.
        Usamos ilike() para que 'moba', 'Moba' y 'MOBA' devuelvan el mismo resultado.
        """
        statement = select(VideoGameType).where(VideoGameType.name.ilike(name))
        return self.session.scalar(statement)
