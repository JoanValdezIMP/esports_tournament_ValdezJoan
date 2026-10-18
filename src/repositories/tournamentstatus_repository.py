from sqlalchemy import select
from typing import Optional
from .abstract_repository import SqlAlchemyRepository
from models import TournamentStatus


class SqlAlchemyTournamentStatusRepository(
    SqlAlchemyRepository[TournamentStatus, int]
):
    def get_by_name(self, name: str) -> Optional[TournamentStatus]:
        """
        Find a tournament status by its name.
        """
        statement = select(TournamentStatus).where(
            TournamentStatus.name == name
        )
        return self.session.scalar(statement)
