from sqlalchemy import select, desc, and_
from typing import Sequence, Optional
from datetime import date
from .abstract_repository import SqlAlchemyRepository
from models import PlayerTeam

class SqlAlchemyPlayerTeamRepository(SqlAlchemyRepository[PlayerTeam, tuple[int, int]]):
    
    def list(self):
        """Lista todos los registros de la tabla intermedia."""
        return self.session.query(PlayerTeam).all()

    def add_player_to_team(self, team_id: int, player_id: int, join_date: date) -> None:
        """
        Operación de dominio: Añade un jugador al equipo directamente.
        Se mapea el parámetro 'join_date' al campo 'registered_at' del modelo.
        """
        """
        Registra la unión de un jugador a un equipo en la tabla asociativa.
        
        Realiza una importación local para evitar dependencias circulares, 
        instancia el vínculo mapeando la fecha al campo 'registered_at' 
        y lo añade a la sesión para su posterior persistencia.
        """
        from models import PlayerTeam # Evita importaciones circulares
        new_link = PlayerTeam(
            id_player=player_id, 
            id_team=team_id, 
            registered_at=join_date # Cambiado de join_date a registered_at
        )
        self.session.add(new_link)

    def get_current_team(self, player_id: int) -> Optional[PlayerTeam]:
        """
        Busca el último equipo al que se unió el jugador.
        Ordenamos por 'registered_at' de forma descendente.
        """
        statement = (
            select(PlayerTeam)
            .where(PlayerTeam.id_player == player_id)
            .order_by(desc(PlayerTeam.registered_at)) # Cambiado a registered_at
            .limit(1) 
        )
        return self.session.scalar(statement)

    def list_players_in_team(self, team_id: int) -> Sequence[PlayerTeam]:
        """
        Saca el roster de un equipo ordenado por veteranía (los primeros en unirse primero).
        """
        statement = (
            select(PlayerTeam)
            .where(PlayerTeam.id_team == team_id)
            .order_by(PlayerTeam.registered_at.asc()) # Cambiado a registered_at
        )
        return self.session.scalars(statement).all()

    def is_player_in_team(self, player_id: int, team_id: int) -> bool:
        """
        Validador booleano rápido para comprobar pertenencia.
        """
        statement = (
            select(PlayerTeam)
            .where(
                and_(
                    PlayerTeam.id_player == player_id,
                    PlayerTeam.id_team == team_id
                )
            )
            .limit(1)
        )
        resultado = self.session.scalar(statement)
        return resultado is not None