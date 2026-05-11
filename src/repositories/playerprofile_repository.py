from sqlalchemy import select, desc
from typing import Sequence, Optional
from .abstract_repository import SqlAlchemyRepository
from models import PlayerProfile

class SqlAlchemyPlayerProfileRepository(SqlAlchemyRepository[PlayerProfile, int]):
    
    def get_by_player_id(self, player_id: int) -> Optional[PlayerProfile]:
        """
        Obtiene el perfil de estadísticas de un jugador específico.
        Ideal para mostrar la 'Tarjeta del Jugador' o su Dashboard personal.
        """
        statement = select(PlayerProfile).where(PlayerProfile.id_player == player_id)
        return self.session.scalar(statement)

    def get_top_ranked(self, limit: int = 10) -> Sequence[PlayerProfile]:
        """
        Obtiene los perfiles con mejor posición en el ranking global.
        Ordenamos de forma ascendente (posición 1 es la mejor).
        """
        statement = (
            select(PlayerProfile)
            # nullslast() es un salvavidas: si un jugador es nuevo y su 
            # ranking es nulo/None, lo mandará al final de la lista 
            # en lugar de ponerlo en el top 1 por error.
            .order_by(PlayerProfile.ranking_position.asc().nullslast())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def get_most_active(self, limit: int = 10) -> Sequence[PlayerProfile]:
        """
        Obtiene los perfiles ordenados por mayor cantidad de partidas jugadas.
        Perfecto para detectar a los usuarios más hardcore de tu plataforma.
        """
        statement = (
            select(PlayerProfile)
            # Aquí sí usamos desc() porque queremos el número MÁS ALTO de partidas primero
            .order_by(desc(PlayerProfile.total_matches))
            .limit(limit)
        )
        return self.session.scalars(statement).all()