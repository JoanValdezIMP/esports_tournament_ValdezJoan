from unittest.mock import MagicMock, call, patch

from ui.cli import main_menu


def test_full_application_navigation_flow():
    mock_context = MagicMock()
    user_inputs = ["1", "2", "3", "4", "5", "0"]

    with (
        patch("rich.prompt.Prompt.ask", side_effect=user_inputs),
        patch("ui.cli.team_menu") as team_menu,
        patch("ui.cli.player_menu") as player_menu,
        patch("ui.cli.catalog_menu") as catalog_menu,
        patch("ui.cli.match_menu") as match_menu,
        patch("ui.cli.tournament_menu") as tournament_menu,
    ):
        main_menu(mock_context)

    assert team_menu.call_args_list == [call(mock_context)]
    assert player_menu.call_args_list == [call(mock_context)]
    assert catalog_menu.call_args_list == [call(mock_context)]
    assert match_menu.call_args_list == [call(mock_context)]
    assert tournament_menu.call_args_list == [call(mock_context)]
    assert mock_context.console.clear.called
