from rich.prompt import Prompt
from ui.context import UIContext
from ui.views.catalog_views import catalog_menu
from ui.views.player_views import player_menu
from ui.views.team_views import team_menu
from ui.views.match_views import match_menu
from ui.views.tournament_views import tournament_menu
from ui.components import welcome_panel


def main_menu(ctx: UIContext):
    """Display the main menu and route user selections."""
    while True:
        ctx.console.clear()
        ctx.console.print(welcome_panel())
        ctx.print_header("E-SPORTS TOURNAMENT - BACK OFFICE")

        ctx.console.print("[bold cyan]1.[/bold cyan] Gestió d'Equips")
        ctx.console.print("[bold cyan]2.[/bold cyan] Gestió de Jugadors")
        ctx.console.print("[bold cyan]3.[/bold cyan] Catàlegs")
        ctx.console.print("[bold cyan]4.[/bold cyan] Gestió de Partits")
        ctx.console.print("[bold cyan]5.[/bold cyan] Gestió de Tornejos")
        ctx.console.print("[bold cyan]0.[/bold cyan] Sortir\n")

        option = Prompt.ask(
            "[bold green]Tria una opció[/bold green]",
            choices=["0", "1", "2", "3", "4", "5"],
        )

        if option == "1":
            team_menu(ctx)
        elif option == "2":
            player_menu(ctx)
        elif option == "3":
            catalog_menu(ctx)
        elif option == "4":
            match_menu(ctx)
        elif option == "5":
            tournament_menu(ctx)
        elif option == "0":
            ctx.console.print(
                "\n[bold yellow]Fins aviat! Sortint de forma segura..."
                "[/bold yellow]"
            )
            break
