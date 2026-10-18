from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from client.tcp_client import ProtocolError, ServerConnectionError
from ui.context import UIContext


def tournament_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Tornejos")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Tornejos")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Torneig")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Torneig")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Torneig")
        ctx.console.print(
            "[bold cyan]5.[/bold cyan] Inscriure Equip a Torneig"
        )
        ctx.console.print(
            "[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n"
        )
        option = Prompt.ask(
            "[bold green]Tria una opció[/bold green]",
            choices=["0", "1", "2", "3", "4", "5"],
        )
        if option == "1":
            list_tournaments(ctx)
        elif option == "2":
            create_tournament(ctx)
        elif option == "3":
            update_tournament(ctx)
        elif option == "4":
            delete_tournament(ctx)
        elif option == "5":
            register_team_in_tournament(ctx)
        elif option == "0":
            break


def list_tournaments(ctx: UIContext) -> None:
    ctx.print_header("Llista de Tornejos")
    tournaments = _request(ctx, "tournaments.list", {})
    if tournaments is None:
        Prompt.ask("Prem Enter per tornar")
        return
    if not isinstance(tournaments, list) or any(
        not isinstance(tournament, dict)
        or any(
            field not in tournament
            for field in (
                "id",
                "name",
                "region",
                "video_game_type",
                "tournament_mode",
                "tournament_status",
                "start_date",
                "end_date",
                "max_teams",
                "prize_pool",
            )
        )
        for tournament in tournaments
    ):
        ctx.print_error(
            "El servidor ha retornat una llista de tornejos no vàlida."
        )
    elif not tournaments:
        ctx.console.print(
            "[yellow]Actualment no hi ha tornejos registrats.[/yellow]\n"
        )
    else:
        table = Table(show_header=True, header_style="bold magenta")
        for heading in (
            "ID",
            "Nom",
            "Regió",
            "Videojoc",
            "Mode",
            "Estat",
            "Inici",
            "Fi",
            "Equips",
            "Premi",
        ):
            table.add_column(heading)
        for tournament in tournaments:
            table.add_row(
                str(tournament["id"]),
                str(tournament["name"]),
                str(tournament["region"]),
                str(tournament["video_game_type"]),
                str(tournament["tournament_mode"]),
                str(tournament["tournament_status"]),
                str(tournament["start_date"]),
                str(tournament["end_date"] or "-"),
                str(tournament["max_teams"]),
                f"{float(tournament['prize_pool']):.2f}",
            )
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")


def create_tournament(ctx: UIContext) -> None:
    ctx.print_header("Crear Nou Torneig")
    request_data = {
        "name": Prompt.ask("Nom del Torneig"),
        "start_date": Prompt.ask("Data d'inici (YYYY-MM-DD)"),
        "end_date": Prompt.ask(
            "Data de fi (YYYY-MM-DD), buit si no aplica", default=""
        )
        or None,
        "prize_pool": Prompt.ask("Prize pool"),
        "max_teams": IntPrompt.ask("Nombre màxim d'equips"),
        "region_id": IntPrompt.ask("ID de la Regió"),
        "video_game_type_id": IntPrompt.ask("ID del Tipus de Videojoc"),
        "tournament_mode_id": IntPrompt.ask("ID del Mode de Torneig"),
        "tournament_status_id": IntPrompt.ask("ID de l'Estat del Torneig"),
    }
    if _request(ctx, "tournaments.create", request_data) is not None:
        ctx.print_success(f"Torneig '{request_data['name']}' creat amb èxit.")
    Prompt.ask("Prem Enter per continuar")


def update_tournament(ctx: UIContext) -> None:
    ctx.print_header("Actualitzar Dades del Torneig")
    tournament_id = _prompt_id(
        ctx, "Introdueix l'ID del torneig a actualitzar"
    )
    if tournament_id is None:
        return
    tournament = _request(ctx, "tournaments.read", {"id": tournament_id})
    if not isinstance(tournament, dict):
        Prompt.ask("Prem Enter per tornar")
        return

    updated = {
        "id": tournament_id,
        "name": Prompt.ask("Nou nom", default=tournament["name"]),
        "start_date": Prompt.ask(
            "Data d'inici (YYYY-MM-DD)", default=tournament["start_date"]
        ),
        "end_date": Prompt.ask(
            "Data de fi (YYYY-MM-DD), buit si no aplica",
            default=tournament["end_date"] or "",
        )
        or None,
        "prize_pool": Prompt.ask(
            "Prize pool", default=str(tournament["prize_pool"])
        ),
        "max_teams": _prompt_int("Màxim d'equips", tournament["max_teams"]),
    }
    if _request(ctx, "tournaments.update", updated) is not None:
        ctx.print_success("Torneig actualitzat correctament.")
    Prompt.ask("Prem Enter per continuar")


def delete_tournament(ctx: UIContext) -> None:
    ctx.print_header("Eliminar Torneig")
    tournament_id = _prompt_id(ctx, "Introdueix l'ID del torneig a eliminar")
    if tournament_id is None:
        return
    tournament = _request(ctx, "tournaments.read", {"id": tournament_id})
    if not isinstance(tournament, dict):
        Prompt.ask("Prem Enter per tornar")
        return
    if Confirm.ask(
        f"Segur que vols eliminar el torneig [bold red]{
            tournament['name']
        }[/bold red]?"
    ):
        if (
            _request(ctx, "tournaments.delete", {"id": tournament_id})
            is not None
        ):
            ctx.print_success("Torneig eliminat del sistema.")
    Prompt.ask("Prem Enter per continuar")


def register_team_in_tournament(ctx: UIContext) -> None:
    ctx.print_header("Inscriure Equip a Torneig")
    result = _request(
        ctx,
        "tournaments.register_team",
        {
            "tournament_id": IntPrompt.ask("ID del Torneig"),
            "team_id": IntPrompt.ask("ID de l'Equip"),
        },
    )
    if result is not None:
        ctx.print_success("Equip inscrit al torneig correctament.")
    Prompt.ask("Prem Enter per continuar")


def _prompt_id(ctx: UIContext, message: str) -> int | None:
    value = Prompt.ask(message)
    if not value.isdigit() or int(value) <= 0:
        ctx.print_error("L'ID ha de ser un número positiu.")
        Prompt.ask("Prem Enter per tornar")
        return None
    return int(value)


def _prompt_int(message: str, default: int) -> int:
    return IntPrompt.ask(message, default=default)


def _request(ctx: UIContext, operation: str, data: dict) -> object | None:
    try:
        response = ctx.tcp_client.request(operation, data)
    except (ProtocolError, ServerConnectionError, ValueError) as error:
        ctx.print_error(str(error))
        return None
    if not response["ok"]:
        error = response["error"]
        ctx.print_error(error["message"] if error else "Error de servidor.")
        return None
    return response["data"]
