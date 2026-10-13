"""Public repository exports, loaded only when a repository is requested."""

from importlib import import_module


_EXPORTS = {
    "RegionRepository": (".region_repository", "SqlAlchemyRegionRepository"),
    "VideoGameTypeRepository": (
        ".videogametype_repository",
        "SqlAlchemyVideoGameTypeRepository",
    ),
    "TournamentModeRepository": (
        ".tournamentmode_repository",
        "SqlAlchemyTournamentModeRepository",
    ),
    "TournamentStatusRepository": (
        ".tournamentstatus_repository",
        "SqlAlchemyTournamentStatusRepository",
    ),
    "PlayerRepository": (".player_repository", "SqlAlchemyPlayerRepository"),
    "TeamRepository": (".team_repository", "SqlAlchemyTeamRepository"),
    "TournamentRepository": (
        ".tournament_repository",
        "SqlAlchemyTournamentRepository",
    ),
    "MatchRepository": (".match_repository", "SqlAlchemyMatchRepository"),
    "PlayerTeamRepository": (
        ".playerteam_repository",
        "SqlAlchemyPlayerTeamRepository",
    ),
    "TeamTournamentRepository": (
        ".teamtournament_repository",
        "SqlAlchemyTeamTournamentRepository",
    ),
    "PlayerProfileRepository": (
        ".playerprofile_repository",
        "SqlAlchemyPlayerProfileRepository",
    ),
    "SqlAlchemyUnitOfWork": (".unit_of_work", "SqlAlchemyUnitOfWork"),
    "UnitOfWorkFactory": (".unit_of_work", "UnitOfWorkFactory"),
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    """Import only the requested implementation to avoid loading all models."""
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = _EXPORTS[name]
    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value
