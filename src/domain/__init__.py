# src/domain/__init__.py
from .config import ENVIRONMENT, DB_URL
from .db import Base, engine, Session

# IMPORTANTE: Importamos todos los modelos aquí para que Base.metadata los registre
from .models import (
    Region, 
    VideoGameType, 
    TournamentMode, 
    TournamentStatus,
    Player, 
    PlayerProfile, 
    Team, 
    PlayerTeam, 
    Tournament, 
    TeamTournament, 
    Match
)

from .repositories import (
    VideoGameTypeRepository,
    RegionRepository
)