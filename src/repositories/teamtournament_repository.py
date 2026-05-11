from sqlalchemy import select, and_
from typing import Sequence, Optional
from .abstract_repository import SqlAlchemyRepository
from models import TeamTournament

class SqlAlchemyTeamTournamentRepository(SqlAlchemyRepository[TeamTournament, tuple[int, int]]):
    
    def get_registration(self, team_id: int, tournament_id: int) -> Optional[TeamTournament]:
        """
        Obtiene los detalles específicos de la inscripción de un equipo en un torneo.
        Permite consultar puntos actuales, posición final y fecha de registro.
        """
        statement = (
            select(TeamTournament)
            .where(
                and_(
                    TeamTournament.id_team == team_id,
                    TeamTournament.id_tournament == tournament_id
                )
            )
        )
        return self.session.scalar(statement)

    def list_registered_teams(self, tournament_id: int) -> Sequence[TeamTournament]:
        """
        Lista todos los equipos inscritos en un torneo específico.
        Ordenamos por puntos obtenidos para tener una clasificación en tiempo real.
        """
        statement = (
            select(TeamTournament)
            .where(TeamTournament.id_tournament == tournament_id)
            .order_by(TeamTournament.points_obtained.desc())
        )
        return self.session.scalars(statement).all()

    def update_points(self, team_id: int, tournament_id: int, points_to_add: int) -> Optional[TeamTournament]:
        """
        Método rápido para actualizar los puntos de un equipo tras un partido.
        Busca el registro, suma los puntos y devuelve el objeto actualizado.
        """
        registration = self.get_registration(team_id, tournament_id)
        
        if registration:
            # Actualizamos el estado del objeto en la sesión
            registration.points_obtained += points_to_add
            # No hacemos commit() aquí; de eso se encarga el Unit of Work al final.
            return registration
        
        return None