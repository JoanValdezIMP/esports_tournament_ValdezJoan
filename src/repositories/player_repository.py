from sqlalchemy import select, desc
from typing import Sequence, Optional
from .abstract_repository import SqlAlchemyRepository

# Asegúrate de importar tus modelos correctamente según tu estructura
from models import Player
from models import PlayerProfile
from models import PlayerTeam
from models import Team

class SqlAlchemyPlayerRepository(SqlAlchemyRepository[Player, int]):
    
    def get_paginated(self, page: int, page_size: int) -> Sequence[Player]:
        """Requisito PAC: Paginación para la entidad más grande."""
        offset_value = (page - 1) * page_size
        statement = select(Player).offset(offset_value).limit(page_size)
        return self.session.scalars(statement).all()

    def add_player_to_team_direct(self, player_id: int, team_id: int) -> None:
        """Requisito PAC: Operación de dominio concreta sin actualizar todo el objeto."""
        from models import PlayerTeam
        from datetime import date
        nuevo_vinculo = PlayerTeam(id_player=player_id, id_team=team_id, join_date=date.today())
        self.session.add(nuevo_vinculo)


    def get_by_nickname(self, nickname: str) -> Optional[Player]:
        """
        Busca un jugador por su apodo exacto.
        Devuelve el jugador o None si no existe.
        """
        statement = select(Player).where(Player.nickname == nickname)
        # Usamos scalar() porque esperamos un único resultado o None
        return self.session.scalar(statement)

    def get_global_ranking(self, limit: int = 50) -> Sequence[Player]:
        """
        Devuelve los mejores jugadores ordenados por su posición en el ranking.
        Cruza la tabla Player con PlayerProfile para poder ordenar.
        """
        statement = (
            select(Player)
            .join(PlayerProfile, Player.id_player == PlayerProfile.id_player)
            # Ordenamos ascendentemente (el rango 1 es el mejor)
            .order_by(PlayerProfile.ranking_position) 
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def get_player_team_history(self, player_id: int) -> Sequence[PlayerTeam]:
        """
        Devuelve el historial de equipos de un jugador, ordenado del más reciente al más antiguo.
        Nota: Devolvemos la entidad asociativa 'PlayerTeam' porque así mantienes 
        el dato de 'join_date' (cuándo se unió).
        """
        statement = (
            select(PlayerTeam)
            .where(PlayerTeam.id_player == player_id)
            .order_by(desc(PlayerTeam.join_date))
        )
        return self.session.scalars(statement).all()

    def get_players_by_region(self, region_id: int) -> Sequence[Player]:
        """
        Filtra todos los jugadores que pertenecen a una región específica.
        """
        statement = select(Player).where(Player.id_region == region_id)
        return self.session.scalars(statement).all()