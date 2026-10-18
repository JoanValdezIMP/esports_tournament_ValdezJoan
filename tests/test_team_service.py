from uuid import uuid4

import pytest

from domain.db import Base, engine, get_uow
from models import Player, PlayerTeam, Region, Team
from services.errors import NotFoundError, ValidationError
from services.player_service import PlayerService
from services.team_service import TeamService


def test_team_service_crud_and_player_assignment_in_memory():
    Base.metadata.create_all(engine)
    region_name = f"TeamRegion-{uuid4().hex}"
    with get_uow() as uow:
        region = Region(name=region_name, country_code="TST")
        uow.session.add(region)
        uow.session.flush()
        region_id = region.id

    player_service = PlayerService(get_uow)
    team_service = TeamService(get_uow)
    player_id = None
    team_id = None
    try:
        player = player_service.create_player(
            "TeamMember",
            f"{uuid4().hex}@example.com",
            region_id,
        )
        player_id = player["id"]
        created = team_service.create_team("Falcons", region_id)
        team_id = created["id"]

        assert created == {
            "id": team_id,
            "name": "Falcons",
            "region": region_name,
        }
        assert team_service.list_teams() == [created]
        assert team_service.get_team(team_id) == created
        updated = team_service.update_team(team_id, "Falcons Pro")
        assert updated["name"] == "Falcons Pro"
        assert team_service.assign_player(team_id, player_id, 8) == {
            "assigned": True
        }

        with pytest.raises(ValidationError, match="already assigned"):
            team_service.assign_player(team_id, player_id, 8)
        with pytest.raises(ValidationError, match="cannot be deleted"):
            team_service.delete_team(team_id)

        with get_uow() as uow:
            association = uow.session.get(PlayerTeam, (player_id, team_id))
            uow.session.delete(association)
        assert team_service.delete_team(team_id) == {"deleted": True}
        team_id = None

        with pytest.raises(NotFoundError, match="Team not found"):
            team_service.get_team(created["id"])
    finally:
        with get_uow() as uow:
            if team_id is not None:
                team = uow.session.get(Team, team_id)
                if team is not None:
                    uow.session.delete(team)
            if player_id is not None:
                player = uow.session.get(Player, player_id)
                if player is not None:
                    uow.session.delete(player)
            region = uow.session.get(Region, region_id)
            if region is not None:
                uow.session.delete(region)


def test_team_service_rejects_invalid_team_data():
    service = TeamService(get_uow)

    with pytest.raises(ValidationError, match="name"):
        service.create_team(" ", 1)
    with pytest.raises(ValidationError, match="region_id"):
        service.create_team("Falcons", 0)
