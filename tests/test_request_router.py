import logging
from unittest.mock import MagicMock

import pytest

from server.router import RequestRouter


def test_router_dispatches_players_list_to_service():
    player_service = MagicMock()
    player_service.list_players.return_value = [
        {
            "id": 1,
            "nickname": "PlayerOne",
            "region": "Europe",
            "has_profile": True,
        }
    ]

    response = RequestRouter(player_service).route(
        {"operation": "players.list", "data": {}}
    )

    assert response == {
        "ok": True,
        "data": [
            {
                "id": 1,
                "nickname": "PlayerOne",
                "region": "Europe",
                "has_profile": True,
            }
        ],
        "error": None,
    }
    player_service.list_players.assert_called_once_with()


@pytest.mark.parametrize(
    ("operation", "data", "method", "arguments"),
    [
        ("players.search", {"nickname": "One"}, "search_players", ("One",)),
        ("players.read", {"id": 3}, "get_player", (3,)),
        (
            "players.create",
            {
                "nickname": "One",
                "email": "one@example.com",
                "region_id": 2,
                "ranking_position": 4,
            },
            "create_player",
            (),
        ),
        (
            "players.update",
            {"id": 3, "nickname": "Two"},
            "update_player",
            (),
        ),
        ("players.delete", {"id": 3}, "delete_player", (3,)),
    ],
)
def test_router_dispatches_player_operations(
    operation, data, method, arguments
):
    player_service = MagicMock()
    getattr(player_service, method).return_value = {"result": "ok"}

    response = RequestRouter(player_service).route(
        {"operation": operation, "data": data}
    )

    assert response == {"ok": True, "data": {"result": "ok"}, "error": None}
    getattr(player_service, method).assert_called_once()
    if arguments:
        getattr(player_service, method).assert_called_once_with(*arguments)


@pytest.mark.parametrize(
    ("operation", "data", "method"),
    [
        ("teams.list", {}, "list_teams"),
        ("teams.read", {"id": 2}, "get_team"),
        ("teams.create", {"name": "Falcons", "region_id": 1}, "create_team"),
        ("teams.update", {"id": 2, "name": "Falcons"}, "update_team"),
        ("teams.delete", {"id": 2}, "delete_team"),
        (
            "teams.assign_player",
            {"team_id": 2, "player_id": 4, "points_obtained": 10},
            "assign_player",
        ),
    ],
)
def test_router_dispatches_team_operations(operation, data, method):
    player_service = MagicMock()
    team_service = MagicMock()
    getattr(team_service, method).return_value = {"result": "ok"}
    router = RequestRouter(player_service, team_service)

    response = router.route({"operation": operation, "data": data})

    assert response == {"ok": True, "data": {"result": "ok"}, "error": None}
    getattr(team_service, method).assert_called_once()


@pytest.mark.parametrize(
    ("operation", "data", "method"),
    [
        ("regions.list", {}, "list_regions"),
        (
            "regions.create",
            {"name": "Europe", "country_code": "EU"},
            "create_region",
        ),
        ("tournament_statuses.list", {}, "list_tournament_statuses"),
        (
            "tournament_statuses.create",
            {"name": "Ready", "description": None},
            "create_tournament_status",
        ),
        ("tournament_modes.list", {}, "list_tournament_modes"),
        (
            "tournament_modes.create",
            {"name": "1vs1", "description": None},
            "create_tournament_mode",
        ),
        (
            "tournament_modes.update",
            {"id": 1, "name": "2vs2", "description": None},
            "update_tournament_mode",
        ),
        ("tournament_modes.delete", {"id": 1}, "delete_tournament_mode"),
        ("video_game_types.list", {}, "list_video_game_types"),
        (
            "video_game_types.create",
            {"name": "MOBA", "description": None},
            "create_video_game_type",
        ),
        (
            "video_game_types.update",
            {"id": 1, "name": "Shooter", "description": None},
            "update_video_game_type",
        ),
        ("video_game_types.delete", {"id": 1}, "delete_video_game_type"),
        ("player_profiles.list", {}, "list_player_profiles"),
    ],
)
def test_router_dispatches_catalog_operations(operation, data, method):
    catalog_service = MagicMock()
    getattr(catalog_service, method).return_value = {"result": "ok"}
    router = RequestRouter(MagicMock(), catalog_service=catalog_service)

    response = router.route({"operation": operation, "data": data})

    assert response == {"ok": True, "data": {"result": "ok"}, "error": None}
    getattr(catalog_service, method).assert_called_once()


@pytest.mark.parametrize(
    ("operation", "data", "method"),
    [
        ("matches.list", {}, "list_matches"),
        (
            "matches.create",
            {
                "tournament_id": 1,
                "team_one_id": 2,
                "team_two_id": 3,
                "round_number": 1,
                "duration_minutes": 30,
            },
            "create_match",
        ),
        (
            "matches.update_result",
            {"id": 4, "score_team_one": 2, "score_team_two": 1},
            "update_result",
        ),
        ("matches.delete", {"id": 4}, "delete_match"),
        ("tournaments.list", {}, "list_tournaments"),
        ("tournaments.read", {"id": 1}, "get_tournament"),
        (
            "tournaments.create",
            {
                "name": "Cup",
                "start_date": "2026-10-19",
                "end_date": None,
                "prize_pool": 100,
                "max_teams": 4,
                "region_id": 1,
                "video_game_type_id": 1,
                "tournament_mode_id": 1,
                "tournament_status_id": 1,
            },
            "create_tournament",
        ),
        (
            "tournaments.update",
            {
                "id": 1,
                "name": "Cup 2",
                "start_date": "2026-10-19",
                "end_date": None,
                "prize_pool": 100,
                "max_teams": 4,
            },
            "update_tournament",
        ),
        ("tournaments.delete", {"id": 1}, "delete_tournament"),
        (
            "tournaments.register_team",
            {"tournament_id": 1, "team_id": 2},
            "register_team",
        ),
    ],
)
def test_router_dispatches_match_and_tournament_operations(
    operation, data, method
):
    service = MagicMock()
    getattr(service, method).return_value = {"result": "ok"}
    if operation.startswith("matches."):
        router = RequestRouter(MagicMock(), match_service=service)
    else:
        router = RequestRouter(MagicMock(), tournament_service=service)

    response = router.route({"operation": operation, "data": data})

    assert response == {"ok": True, "data": {"result": "ok"}, "error": None}
    getattr(service, method).assert_called_once()


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ([], "invalid_request"),
        ({}, "invalid_request"),
        ({"operation": 1, "data": {}}, "invalid_request"),
        ({"operation": "players.list"}, "invalid_request"),
        ({"operation": "players.list", "data": []}, "invalid_request"),
        (
            {"operation": "players.list", "data": {"unexpected": True}},
            "validation_error",
        ),
        (
            {"operation": "teams.list", "data": {}},
            "unknown_operation",
        ),
    ],
)
def test_router_returns_errors_for_invalid_or_unsupported_requests(
    payload, code
):
    player_service = MagicMock()

    response = RequestRouter(player_service).route(payload)

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["code"] == code
    assert response["error"]["message"]
    player_service.list_players.assert_not_called()


def test_router_logs_service_error_and_returns_safe_response(caplog):
    player_service = MagicMock()
    player_service.list_players.side_effect = RuntimeError("database details")

    with caplog.at_level(logging.ERROR):
        response = RequestRouter(player_service).route(
            {"operation": "players.list", "data": {}}
        )

    assert response == {
        "ok": False,
        "data": None,
        "error": {
            "code": "internal_error",
            "message": "An internal server error occurred",
        },
    }
    assert "database details" not in response["error"]["message"]
    assert "Failed to process operation players.list" in caplog.text
