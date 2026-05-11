from sqlalchemy import select, or_, and_, desc
from typing import Sequence
from models import Match
from .abstract_repository import SqlAlchemyRepository

class SqlAlchemyMatchRepository(SqlAlchemyRepository[Match, int]):
    
    def get_head_to_head(self, team_a_id: int, team_b_id: int) -> Sequence[Match]:
        """
        Historial de enfrentamientos directos entre dos equipos.
        Busca partidos donde (A vs B) O (B vs A).
        """
        statement = (
            select(Match)
            .where(
                or_(
                    and_(Match.id_team_one == team_a_id, Match.id_team_two == team_b_id),
                    and_(Match.id_team_one == team_b_id, Match.id_team_two == team_a_id)
                )
            )
            .order_by(desc(Match.match_date))
        )
        return self.session.scalars(statement).all()

    def get_recent_results(self, limit: int = 20) -> Sequence[Match]:
        """
        Los últimos partidos finalizados. 
        Asumimos que un partido ha finalizado si tiene un ganador asignado.
        """
        statement = (
            select(Match)
            .where(Match.id_team_winner.is_not(None))
            .order_by(desc(Match.match_date))
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def get_tournament_bracket(self, tournament_id: int) -> Sequence[Match]:
        """
        Retorna los partidos de un torneo específico ordenados por ronda.
        Útil para visualizar el progreso del torneo (Brackets).
        """
        statement = (
            select(Match)
            .where(Match.id_tournament == tournament_id)
            .order_by(Match.round_number, Match.match_date)
        )
        return self.session.scalars(statement).all()