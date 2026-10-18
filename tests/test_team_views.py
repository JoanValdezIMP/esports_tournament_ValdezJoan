from unittest.mock import MagicMock, patch

from rich.table import Table

from ui.views.team_views import list_teams


def test_list_teams_uses_tcp_client_and_displays_remote_data():
    context = MagicMock()
    context.tcp_client.request.return_value = {
        "ok": True,
        "data": [{"id": 5, "name": "Falcons", "region": "Europe"}],
        "error": None,
    }

    with patch("ui.views.team_views.Prompt.ask"):
        list_teams(context)

    context.tcp_client.request.assert_called_once_with("teams.list", {})
    context.uow_factory.assert_not_called()
    rendered_table = context.console.print.call_args.args[0]
    assert isinstance(rendered_table, Table)
