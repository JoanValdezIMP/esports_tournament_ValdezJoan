from sqlalchemy import select
from typing import Sequence, Optional

from models import TournamentMode
from .abstract_repository import SqlAlchemyRepository


class SqlAlchemyTournamentModeRepository(SqlAlchemyRepository[TournamentMode, int]):
    
    def get_by_name(self, name: str) -> Optional[TournamentMode]:
        """
        Busca un modo de torneo (ej: '1vs1', '5vs5') por su nombre.
        """
        statement = select(TournamentMode).where(TournamentMode.name.ilike(name))
        return self.session.scalar(statement)

    def list_active_modes(self) -> Sequence[TournamentMode]:
        """
        Actualmente funciona igual que el list() genérico trayendo todos los registros.
        En el futuro, podríamos agregar un campo 'active' a TournamentMode y filtrar por eso.
        """
        statement = select(TournamentMode)
        return self.session.scalars(statement).all()