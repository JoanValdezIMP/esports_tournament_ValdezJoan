from unittest.mock import MagicMock, patch

from rich.table import Table

from ui.views.player_views import list_players


def test_list_players_uses_tcp_client_and_displays_remote_data():
    context = MagicMock()
    context.tcp_client.request.return_value = {
        "ok": True,
        "data": [
            {
                "id": 7,
                "nickname": "PlayerOne",
                "region": "Europe",
                "has_profile": True,
            }
        ],
        "error": None,
    }

    with patch("ui.views.player_views.Prompt.ask"):
        list_players(context)

        context.tcp_client.request.assert_called_once_with("players.list", {})
        context.uow_factory.assert_not_called()
        rendered_table = context.console.print.call_args.args[0]
        assert isinstance(rendered_table, Table)
