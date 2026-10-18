from unittest.mock import MagicMock, patch

from rich.table import Table

from ui.views.match_views import list_matches
from ui.views.tournament_views import list_tournaments


def test_list_matches_uses_tcp_client():
    context = MagicMock()
    context.tcp_client.request.return_value = {
        "ok": True,
        "data": [
            {
                "id": 1,
                "match_date": "2026-10-19T12:00",
                "tournament_id": 2,
                "team_one_id": 3,
                "team_two_id": 4,
                "winner_id": 3,
                "score_team_one": 2,
                "score_team_two": 1,
                "round_number": 1,
                "duration_minutes": 30,
            }
        ],
        "error": None,
    }

    with patch("ui.views.match_views.Prompt.ask"):
        list_matches(context)

    context.tcp_client.request.assert_called_once_with("matches.list", {})
    context.uow_factory.assert_not_called()
    assert isinstance(context.console.print.call_args.args[0], Table)


def test_list_tournaments_uses_tcp_client():
    context = MagicMock()
    context.tcp_client.request.return_value = {
        "ok": True,
        "data": [
            {
                "id": 1,
                "name": "Winter Cup",
                "region": "Europe",
                "video_game_type": "MOBA",
                "tournament_mode": "5vs5",
                "tournament_status": "Planned",
                "start_date": "2026-10-19",
                "end_date": None,
                "max_teams": 8,
                "prize_pool": 1200.5,
            }
        ],
        "error": None,
    }

    with patch("ui.views.tournament_views.Prompt.ask"):
        list_tournaments(context)

    context.tcp_client.request.assert_called_once_with("tournaments.list", {})
    context.uow_factory.assert_not_called()
    assert isinstance(context.console.print.call_args.args[0], Table)
