from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload
from typing import Sequence, Optional, Dict
from .abstract_repository import SqlAlchemyRepository
from models import Team
from models import TeamTournament
from models import Tournament
from models import Match
from models import PlayerTeam

class SqlAlchemyTeamRepository(SqlAlchemyRepository[Team, int]):
    
    def get_full_roster(self, team_id: int) -> Optional[Team]:
        """
        Trae el equipo junto con los datos de todos sus jugadores en una sola consulta.
        """
        statement = (
            select(Team)
            # Usamos joinedload para decirle a SQLAlchemy que no solo traiga el equipo,
            # sino que "precargue" (Eager Loading) las relaciones en memoria.
            .options(
                joinedload(Team.team_players).joinedload(PlayerTeam.player)
            )
            .where(Team.id_team == team_id)
        )
        return self.session.scalar(statement)

    def get_teams_by_game_type(self, game_type_id: int) -> Sequence[Team]:
        """
        Devuelve los equipos que participan o han participado en torneos 
        de un videojuego específico (ej: buscar todos los equipos de "League of Legends").
        """
        statement = (
            select(Team)
            # Saltamos de Team -> TeamTournament -> Tournament
            .join(TeamTournament, Team.id_team == TeamTournament.id_team)
            .join(Tournament, TeamTournament.id_tournament == Tournament.id_tournament)
            .where(Tournament.id_video_game_type == game_type_id)
            # Usamos distinct() porque un equipo puede haber jugado varios torneos 
            # del mismo juego y no queremos que salga duplicado en la lista.
            .distinct()
        )
        return self.session.scalars(statement).all()

    def get_win_loss_ratio(self, team_id: int) -> Dict[str, float | int]:
        """
        Calcula las victorias, derrotas y el 'win ratio' del equipo en sus partidos.
        """
        # 1. Contamos las victorias (es el id_team_winner)
        stmt_wins = select(func.count(Match.id_match)).where(Match.id_team_winner == team_id)
        wins = self.session.scalar(stmt_wins) or 0

        # 2. Contamos TODOS los partidos finalizados en los que jugó el equipo
        stmt_total = (
            select(func.count(Match.id_match))
            .where(
                or_(Match.id_team_one == team_id, Match.id_team_two == team_id)
            )
            # Solo partidos terminados (tienen un ganador definido)
            .where(Match.id_team_winner.is_not(None)) 
        )
        total_matches = self.session.scalar(stmt_total) or 0

        # 3. Calculamos derrotas y el ratio
        losses = total_matches - wins
        # Evitamos el error de división por cero si el equipo nunca ha perdido
        ratio = round(wins / losses, 2) if losses > 0 else float(wins)

        return {
            "wins": wins,
            "losses": losses,
            "total_matches": total_matches,
            "win_ratio": ratio
        }