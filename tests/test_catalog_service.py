from uuid import uuid4

import pytest

from domain.db import Base, engine, get_uow
from models import (
    Player,
    PlayerProfile,
    Region,
    TournamentMode,
    TournamentStatus,
    VideoGameType,
)
from services.catalog_service import CatalogService
from services.errors import NotFoundError, ValidationError
from services.player_service import PlayerService


def test_catalog_service_lists_and_manages_catalogs_in_memory():
    Base.metadata.create_all(engine)
    service = CatalogService(get_uow)
    player_service = PlayerService(get_uow)
    suffix = uuid4().hex
    region_id = None
    player_id = None
    status_id = None
    mode_id = None
    game_type_id = None

    try:
        region = service.create_region(f"Region-{suffix}", "TST")
        region_id = region["id"]
        assert region in service.list_regions()

        status = service.create_tournament_status(
            f"Status-{suffix}",
            "  Ready to play  ",
        )
        status_id = status["id"]
        assert status in service.list_tournament_statuses()
        assert status["description"] == "Ready to play"

        mode = service.create_tournament_mode(f"Mode-{suffix}", None)
        mode_id = mode["id"]
        assert mode in service.list_tournament_modes()
        updated_mode = service.update_tournament_mode(
            mode_id,
            f"Updated-{suffix}",
            " Updated description ",
        )
        assert updated_mode == {
            "id": mode_id,
            "name": f"Updated-{suffix}",
            "description": "Updated description",
        }
        assert service.delete_tournament_mode(mode_id) == {"deleted": True}
        mode_id = None
        with pytest.raises(NotFoundError, match="Tournament mode not found"):
            service.update_tournament_mode(mode["id"], "Missing", None)

        game_type = service.create_video_game_type(f"Type-{suffix}", None)
        game_type_id = game_type["id"]
        assert game_type in service.list_video_game_types()
        updated_game_type = service.update_video_game_type(
            game_type_id,
            f"UpdatedType-{suffix}",
            None,
        )
        assert updated_game_type["name"] == f"UpdatedType-{suffix}"
        assert service.delete_video_game_type(game_type_id) == {
            "deleted": True
        }
        game_type_id = None

        player = player_service.create_player(
            f"Profile-{suffix}",
            f"{suffix}@example.com",
            region_id,
            ranking_position=12,
        )
        player_id = player["id"]
        profile = next(
            item
            for item in service.list_player_profiles()
            if item["nickname"] == f"Profile-{suffix}"
        )
        assert profile == {
            "nickname": f"Profile-{suffix}",
            "ranking_position": 12,
            "total_matches": 0,
            "total_points": 0,
        }
    finally:
        with get_uow() as uow:
            if player_id is not None:
                profile_record = (
                    uow.session.query(PlayerProfile)
                    .filter_by(id_player=player_id)
                    .one_or_none()
                )
                if profile_record is not None:
                    uow.session.delete(profile_record)
            for model, item_id in (
                (Player, player_id),
                (TournamentMode, mode_id),
                (TournamentStatus, status_id),
                (VideoGameType, game_type_id),
            ):
                if item_id is not None:
                    item = uow.session.get(model, item_id)
                    if item is not None:
                        uow.session.delete(item)
            if region_id is not None:
                region_record = uow.session.get(Region, region_id)
                if region_record is not None:
                    uow.session.delete(region_record)


@pytest.mark.parametrize(
    ("method", "arguments", "message"),
    [
        ("create_region", (" ", "TST"), "name"),
        ("create_region", ("Europe", " "), "country_code"),
        ("create_tournament_mode", (" ", None), "name"),
        ("update_tournament_mode", (0, "Mode", None), "id"),
        ("create_video_game_type", ("Type", 4), "description"),
        ("update_video_game_type", (99999999, "Type", None), "not found"),
    ],
)
def test_catalog_service_validates_input_and_missing_items(
    method, arguments, message
):
    service = CatalogService(get_uow)
    with pytest.raises((ValidationError, NotFoundError), match=message):
        getattr(service, method)(*arguments)
