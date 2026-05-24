import pytest
from unittest.mock import MagicMock, patch
from ui.cli import main_menu
def test_full_application_navigation_flow():
    mock_context = MagicMock()
    
    # Cada "0" o "1" debe coincidir con cada Prompt.ask en el código
    user_inputs = [
        "1", "1", "0",          # Equipos: 1(menu) -> 1(listar) -> 0(Enter/volver)
        "2", "1", "0",          # Jugadores: 2(menu) -> 1(listar) -> 0(Enter/volver)
        "3", "1", "1", "0", "0",# Catálogos: 3(menu) -> 1(Region) -> 1(listar) -> 0(Enter) -> 0(atrás)
        "4", "1", "0",          # Partidos: 4(menu) -> 1(listar) -> 0(Enter/volver)
        "5", "1", "0",          # Torneos: 5(menu) -> 1(listar) -> 0(Enter/volver)
        "0"                     # Salir del menu principal
    ]
    
    with patch("rich.prompt.Prompt.ask", side_effect=user_inputs), \
         patch("rich.prompt.Confirm.ask", return_value=True):
        
        main_menu(mock_context)
        
    assert mock_context.console.clear.called