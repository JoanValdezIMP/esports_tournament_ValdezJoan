from uuid import uuid4

import pytest

from domain.db import Base, engine, get_uow
from models import (
    Match,
    Region,
    Team,
    TeamTournament,
    Tournament,
    TournamentMode,
    TournamentStatus,
    VideoGameType,
)
from services.errors import NotFoundError, ValidationError
from services.match_service import MatchService
from services.team_service import TeamService
from services.tournament_service import TournamentService


def test_match_and_tournament_services_manage_serializable_data():
    Base.metadata.create_all(engine)
    suffix = uuid4().hex
    with get_uow() as uow:
        region = Region(name=f"Region-{suffix}", country_code="TST")
        mode = TournamentMode(name=f"Mode-{suffix}", description=None)
        status = TournamentStatus(name=f"Status-{suffix}", description=None)
        game_type = VideoGameType(name=f"Game-{suffix}", description=None)
        uow.session.add_all([region, mode, status, game_type])
        uow.session.flush()
        region_id = region.id
        mode_id = mode.id
        status_id = status.id
        game_type_id = game_type.id

    team_service = TeamService(get_uow)
    tournament_service = TournamentService(get_uow)
    match_service = MatchService(get_uow)
    team_ids = []
    tournament_id = None
    match_id = None
    try:
        team_one = team_service.create_team(f"TeamA-{suffix}", region_id)
        team_two = team_service.create_team(f"TeamB-{suffix}", region_id)
        team_ids.extend([team_one["id"], team_two["id"]])

        tournament = tournament_service.create_tournament(
            f"Tournament-{suffix}",
            "2026-10-19",
            None,
            "1250.50",
            1,
            region_id,
            game_type_id,
            mode_id,
            status_id,
        )
        tournament_id = tournament["id"]
        assert tournament["prize_pool"] == 1250.5
        assert tournament_service.get_tournament(tournament_id) == tournament
        assert tournament_service.list_tournaments() == [tournament]

        assert tournament_service.register_team(
            tournament_id, team_one["id"]
        ) == {"registered": True}
        with pytest.raises(ValidationError, match="already registered"):
            tournament_service.register_team(tournament_id, team_one["id"])
        with pytest.raises(ValidationError, match="team limit"):
            tournament_service.register_team(tournament_id, team_two["id"])

        updated = tournament_service.update_tournament(
            tournament_id,
            f"Updated-{suffix}",
            "2026-10-20",
            "2026-10-21",
            900,
            3,
        )
        assert updated["name"] == f"Updated-{suffix}"
        assert updated["end_date"] == "2026-10-21"
        assert updated["max_teams"] == 3
        assert tournament_service.register_team(
            tournament_id, team_two["id"]
        ) == {"registered": True}

        match = match_service.create_match(
            tournament_id,
            team_one["id"],
            team_two["id"],
            1,
            45,
        )
        match_id = match["id"]
        assert match["score_team_one"] == 0
        assert match_service.list_matches() == [match]

        result = match_service.update_result(match_id, 2, 1)
        assert result["winner_id"] == team_one["id"]
        draw = match_service.update_result(match_id, 1, 1)
        assert draw["winner_id"] is None
        assert match_service.delete_match(match_id) == {"deleted": True}
        match_id = None

        with pytest.raises(ValidationError, match="registered teams"):
            tournament_service.delete_tournament(tournament_id)
        with get_uow() as uow:
            uow.session.query(TeamTournament).filter_by(
                id_tournament=tournament_id
            ).delete(synchronize_session=False)
        assert tournament_service.delete_tournament(tournament_id) == {
            "deleted": True
        }
        tournament_id = None
        with pytest.raises(NotFoundError, match="Match not found"):
            match_service.update_result(99999999, 0, 0)
    finally:
        with get_uow() as uow:
            if match_id is not None:
                match = uow.session.get(Match, match_id)
                if match is not None:
                    uow.session.delete(match)
            if tournament_id is not None:
                uow.session.query(TeamTournament).filter_by(
                    id_tournament=tournament_id
                ).delete(synchronize_session=False)
                uow.session.flush()
                tournament = uow.session.get(Tournament, tournament_id)
                if tournament is not None:
                    uow.session.delete(tournament)
            for team_id in team_ids:
                team = uow.session.get(Team, team_id)
                if team is not None:
                    uow.session.delete(team)
            for model, item_id in (
                (VideoGameType, game_type_id),
                (TournamentMode, mode_id),
                (TournamentStatus, status_id),
                (Region, region_id),
            ):
                item = uow.session.get(model, item_id)
                if item is not None:
                    uow.session.delete(item)


@pytest.mark.parametrize(
    ("method", "args", "message"),
    [
        ("create_match", (1, 2, 2, 1, 30), "different teams"),
        ("create_match", (1, 2, 3, 0, 30), "round_number"),
        ("update_result", (1, -1, 0), "score_team_one"),
    ],
)
def test_match_service_rejects_invalid_values(method, args, message):
    service = MatchService(get_uow)
    with pytest.raises(ValidationError, match=message):
        getattr(service, method)(*args)


def test_tournament_service_rejects_invalid_dates_and_amounts():
    service = TournamentService(get_uow)
    with pytest.raises(ValidationError, match="start_date"):
        service.create_tournament("Cup", "19-10-2026", None, 0, 4, 1, 1, 1, 1)
    with pytest.raises(ValidationError, match="decimal places"):
        service.create_tournament(
            "Cup", "2026-10-19", None, "2.345", 4, 1, 1, 1, 1
        )
