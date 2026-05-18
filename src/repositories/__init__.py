# src/repositories/__init__.py

# 1. Importaciones con Alias (para comodidad en el Notebook)
from .region_repository import SqlAlchemyRegionRepository as RegionRepository
from .videogametype_repository import SqlAlchemyVideoGameTypeRepository as VideoGameTypeRepository
from .tournamentmode_repository import SqlAlchemyTournamentModeRepository as TournamentModeRepository
from .tournamentstatus_repository import SqlAlchemyTournamentStatusRepository as TournamentStatusRepository
from .player_repository import SqlAlchemyPlayerRepository as PlayerRepository
from .team_repository import SqlAlchemyTeamRepository as TeamRepository
from .tournament_repository import SqlAlchemyTournamentRepository as TournamentRepository
from .match_repository import SqlAlchemyMatchRepository as MatchRepository
from .playerteam_repository import SqlAlchemyPlayerTeamRepository as PlayerTeamRepository
from .teamtournament_repository import SqlAlchemyTeamTournamentRepository as TeamTournamentRepository

# --- ESTE ES EL QUE FALTABA ---
from .playerprofile_repository import SqlAlchemyPlayerProfileRepository as PlayerProfileRepository

# 2. Infraestructura
from .unit_of_work import SqlAlchemyUnitOfWork 
from .unit_of_work import UnitOfWorkFactory

# 3. Exportación pública
__all__ = [
    "RegionRepository",
    "VideoGameTypeRepository",
    "TournamentModeRepository",
    "TournamentStatusRepository",
    "PlayerRepository",
    "TeamRepository",
    "TournamentRepository",
    "MatchRepository",
    "PlayerTeamRepository",
    "TeamTournamentRepository",
    "PlayerProfileRepository",  # <--- No olvides añadirlo aquí
    "UnitOfWorkFactory"
]