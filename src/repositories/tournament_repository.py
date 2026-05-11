from sqlalchemy import select, desc, and_
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import Sequence
from .abstract_repository import SqlAlchemyRepository
from models import Tournament
from models import TeamTournament
from models import Team
from models import PlayerTeam
from models import Player
from models import Match
from models import TournamentStatus

class SqlAlchemyTournamentRepository(SqlAlchemyRepository[Tournament, int]):
    
    def get_top_players(self, tournament_id: int, limit: int = 10) -> Sequence[Player]:
        """
        Busca los jugadores de los equipos inscritos en un torneo, 
        ordenados por los puntos que su equipo ha obtenido.
        """
        statement = (
            select(Player)
            .join(PlayerTeam, Player.id_player == PlayerTeam.id_player)
            .join(Team, PlayerTeam.id_team == Team.id_team)
            .join(TeamTournament, Team.id_team == TeamTournament.id_team)
            .where(TeamTournament.id_tournament == tournament_id)
            .order_by(desc(TeamTournament.points_obtained))
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def get_active_tournaments(self, status_name: str = "En curso") -> Sequence[Tournament]:
        """
        Filtra los torneos por su estado actual cruzando con la tabla TournamentStatus.
        """
        statement = (
            select(Tournament)
            .join(TournamentStatus, Tournament.id_tournament_status == TournamentStatus.id_tournament_status)
            # Filtramos por el nombre del estado (puedes ajustar el string según tu DB)
            .where(TournamentStatus.name == status_name)
            .order_by(Tournament.start_date.desc())
        )
        return self.session.scalars(statement).all()

    def get_upcoming_matches(self, tournament_id: int) -> Sequence[Match]:
        """
        Trae los partidos del torneo que aún no tienen un ganador asignado.
        Ordena por fecha para mostrar los más inminentes primero.
        """
        statement = (
            select(Match)
            .where(
                and_(
                    Match.id_tournament == tournament_id,
                    Match.id_team_winner.is_(None)  # Asumimos que si no hay ganador, no ha terminado
                )
            )
            # Orden ascendente: los partidos más cercanos en fecha salen primero
            .order_by(Match.match_date.asc())
        )
        return self.session.scalars(statement).all()

    def get_leaderboard(self, tournament_id: int) -> Sequence[TeamTournament]:
        """
        Clasificación de los equipos basada en los puntos obtenidos.
        Trae la relación 'team' precargada para poder mostrar el nombre fácilmente.
        """
        statement = (
            select(TeamTournament)
            # Usamos joinedload para traer los datos del equipo en la misma consulta
            .options(joinedload(TeamTournament.team))
            .where(TeamTournament.id_tournament == tournament_id)
            # Ordenamos por puntos (mayor a menor)
            .order_by(desc(TeamTournament.points_obtained))
        )
        return self.session.scalars(statement).all()