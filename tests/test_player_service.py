from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from domain.db import Base, engine, get_uow
from models import Player, PlayerProfile, Region
from services.player_service import (
    PlayerNotFoundError,
    PlayerService,
    PlayerValidationError,
)


def test_list_players_returns_client_safe_dictionaries():
    players = [
        SimpleNamespace(
            id=1,
            nickname="PlayerOne",
            id_region=3,
            region=SimpleNamespace(name="Europe"),
            profile=SimpleNamespace(ranking_position=7),
        ),
        SimpleNamespace(
            id=2,
            nickname="PlayerTwo",
            id_region=4,
            region=None,
            profile=None,
        ),
    ]
    uow = MagicMock()
    uow_factory = MagicMock()
    uow_factory.return_value.__enter__.return_value = uow
    repository = MagicMock()
    repository.get_all.return_value = players

    with patch(
        "services.player_service.PlayerRepository",
        return_value=repository,
    ) as repository_class:
        result = PlayerService(uow_factory).list_players()

    assert result == [
        {
            "id": 1,
            "nickname": "PlayerOne",
            "region": "Europe",
            "has_profile": True,
        },
        {
            "id": 2,
            "nickname": "PlayerTwo",
            "region": "4",
            "has_profile": False,
        },
    ]
    assert all(isinstance(player, dict) for player in result)
    repository_class.assert_called_once()
    repository.get_all.assert_called_once_with()
    uow_factory.assert_called_once_with()


def test_player_service_crud_lifecycle_in_memory():
    Base.metadata.create_all(engine)
    service = PlayerService(get_uow)
    region_name = f"Region-{uuid4().hex}"
    with get_uow() as uow:
        region = Region(name=region_name, country_code="TST")
        uow.session.add(region)
        uow.session.flush()
        region_id = region.id

    player_id = None
    try:
        created = service.create_player(
            "PlayerOne",
            "player@example.com",
            region_id,
            ranking_position=12,
        )
        player_id = created["id"]
        assert created["nickname"] == "PlayerOne"
        assert created["region"] == region_name
        assert created["has_profile"] is True

        assert service.get_player(player_id) == created
        updated = service.update_player(player_id, "PlayerUpdated")
        assert updated["nickname"] == "PlayerUpdated"
        assert service.search_players("Updated") == [updated]

        assert service.delete_player(player_id) == {"deleted": True}
        with get_uow() as uow:
            assert uow.session.get(PlayerProfile, player_id) is None
        with pytest.raises(PlayerNotFoundError):
            service.get_player(player_id)
    finally:
        with get_uow() as uow:
            if player_id is not None:
                player = uow.session.get(Player, player_id)
                if player is not None:
                    uow.session.delete(player)
            region = uow.session.get(Region, region_id)
            if region is not None:
                uow.session.delete(region)


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        (("", "a@example.com", 1), "nickname"),
        (("Player", "", 1), "email"),
        (("Player", "a@example.com", 0), "region_id"),
    ],
)
def test_create_player_rejects_invalid_fields(arguments, field):
    service = PlayerService(MagicMock())

    with pytest.raises(PlayerValidationError, match=field):
        service.create_player(*arguments)
