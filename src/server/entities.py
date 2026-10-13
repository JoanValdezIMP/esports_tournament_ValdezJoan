"""Server-only allowlist of entities exposed through the protocol."""

def get_entity_models():
    """Return the public entity names and their persistence models."""
    from models import (
        Match,
        Player,
        PlayerProfile,
        PlayerTeam,
        Region,
        Team,
        TeamTournament,
        Tournament,
        TournamentMode,
        TournamentStatus,
        VideoGameType,
    )

    return {
        "regions": Region,
        "video_game_types": VideoGameType,
        "tournament_modes": TournamentMode,
        "tournament_statuses": TournamentStatus,
        "players": Player,
        "player_profiles": PlayerProfile,
        "player_teams": PlayerTeam,
        "teams": Team,
        "tournaments": Tournament,
        "team_tournaments": TeamTournament,
        "matches": Match,
    }
