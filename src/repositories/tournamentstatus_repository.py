from sqlalchemy import select
from typing import Optional
from .abstract_repository import SqlAlchemyRepository
from models import TournamentStatus

class SqlAlchemyTournamentStatusRepository(SqlAlchemyRepository[TournamentStatus, int]):
    
    def get_by_name(self, name: str) -> Optional[TournamentStatus]:
        """
        Busca un estado de torneo por su nombre (ej: 'En curso', 'Finalizado', 'Cancelado').
        Útil para validaciones antes de crear o actualizar un torneo.
        """
        statement = select(TournamentStatus).where(TournamentStatus.name == name)
        return self.session.scalar(statement)