from unittest.mock import MagicMock, patch

from rich.table import Table

from ui.views.catalog_views import list_regions


def test_list_regions_uses_tcp_client_and_displays_remote_data():
    context = MagicMock()
    context.tcp_client.request.return_value = {
        "ok": True,
        "data": [{"id": 7, "name": "Europe", "country_code": "EU"}],
        "error": None,
    }

    with patch("ui.views.catalog_views.Prompt.ask"):
        list_regions(context)

    context.tcp_client.request.assert_called_once_with("regions.list", {})
    context.uow_factory.assert_not_called()
    rendered_table = context.console.print.call_args.args[0]
    assert isinstance(rendered_table, Table)
