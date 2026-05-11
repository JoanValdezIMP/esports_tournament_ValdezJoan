# src/repositories/__init__.py

# 1. Importamos las implementaciones de SQLAlchemy y las renombramos para el Notebook
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

# 2. Asegúrate de que el UnitOfWorkFactory también esté aquí
# (Si lo tienes en esta carpeta, si no, impórtalo de donde esté)
from .unit_of_work import UnitOfWorkFactory

# Esto hace que al hacer 'from repositories import *' se traiga todo esto
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
    "UnitOfWorkFactory"
]