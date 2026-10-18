from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from client.tcp_client import ProtocolError, ServerConnectionError
from ui.context import UIContext


def team_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió d'Equips")

        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Equips")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Equip")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Equip")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Equip")
        ctx.console.print("[bold cyan]5.[/bold cyan] Assignar Jugador a Equip")
        ctx.console.print(
            "[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n"
        )

        option = Prompt.ask(
            "[bold green]Tria una opció[/bold green]",
            choices=["0", "1", "2", "3", "4", "5"],
        )

        if option == "1":
            list_teams(ctx)
        elif option == "2":
            create_team(ctx)
        elif option == "3":
            update_team(ctx)
        elif option == "4":
            delete_team(ctx)
        elif option == "5":
            assign_player_to_team(ctx)
        elif option == "0":
            break


def list_teams(ctx: UIContext) -> None:
    ctx.print_header("Llista d'Equips")
    teams = _request(ctx, "teams.list", {})
    if teams is None:
        Prompt.ask("Prem Enter per tornar")
        return
    _display_teams(ctx, teams)
    Prompt.ask("\nPrem Enter per tornar")


def create_team(ctx: UIContext) -> None:
    ctx.print_header("Fundar Nou Equip")
    name = Prompt.ask("Nom de l'equip")
    region_id = IntPrompt.ask("ID de la Regió")

    if (
        _request(ctx, "teams.create", {"name": name, "region_id": region_id})
        is not None
    ):
        ctx.print_success(f"Equip '{name}' fundat correctament.")
    Prompt.ask("Prem Enter per continuar")


def update_team(ctx: UIContext) -> None:
    ctx.print_header("Actualitzar Dades de l'Equip")
    team_id = _prompt_id(ctx, "Introdueix l'ID de l'equip a actualitzar")
    if team_id is None:
        return

    team = _request(ctx, "teams.read", {"id": team_id})
    if team is None:
        Prompt.ask("Prem Enter per tornar")
        return
    if not isinstance(team, dict) or not isinstance(team.get("name"), str):
        ctx.print_error("El servidor devolvió datos de equipo no válidos.")
        Prompt.ask("Prem Enter per tornar")
        return

    name = Prompt.ask(f"Nou nom (actual: {team['name']})")
    if name:
        updated = _request(ctx, "teams.update", {"id": team_id, "name": name})
        if updated is not None:
            ctx.print_success("Equip actualitzat amb èxit.")
    Prompt.ask("Prem Enter per continuar")


def delete_team(ctx: UIContext) -> None:
    ctx.print_header("Dissoldre Equip")
    team_id = _prompt_id(
        ctx, "Introdueix l'ID de l'equip a dissoldre (eliminar)"
    )
    if team_id is None:
        return

    team = _request(ctx, "teams.read", {"id": team_id})
    if team is None:
        Prompt.ask("Prem Enter per tornar")
        return
    name = (
        team.get("name", "aquest equip")
        if isinstance(team, dict)
        else "aquest equip"
    )
    if Confirm.ask(
        f"Segur que vols dissoldre l'equip [bold red]{name}[/bold red]?"
    ):
        if _request(ctx, "teams.delete", {"id": team_id}) is not None:
            ctx.print_success("Equip eliminat del sistema.")
    Prompt.ask("Prem Enter per continuar")


def assign_player_to_team(ctx: UIContext) -> None:
    ctx.print_header("Assignar Jugador a Equip")
    team_id = IntPrompt.ask("ID de l'Equip")
    player_id = IntPrompt.ask("ID del Jugador")
    points = IntPrompt.ask("Punts obtinguts (o posició)", default=0)

    result = _request(
        ctx,
        "teams.assign_player",
        {
            "team_id": team_id,
            "player_id": player_id,
            "points_obtained": points,
        },
    )
    if result is not None:
        ctx.print_success("Jugador assignat a l'equip correctament.")
    Prompt.ask("Prem Enter per continuar")


def _prompt_id(ctx: UIContext, prompt: str) -> int | None:
    value = Prompt.ask(prompt)
    if not value.isdigit() or int(value) <= 0:
        ctx.print_error("L'ID ha de ser un número positiu.")
        Prompt.ask("Prem Enter per tornar")
        return None
    return int(value)


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


def _display_teams(
    ctx: UIContext,
    teams: object,
) -> None:
    if not isinstance(teams, list) or any(
        not isinstance(team, dict)
        or not isinstance(team.get("id"), int)
        or not isinstance(team.get("name"), str)
        or not isinstance(team.get("region"), str)
        for team in teams
    ):
        ctx.print_error("El servidor devolvió una lista de equipos no válida.")
        return
    if not teams:
        ctx.console.print(
            "[yellow]No hi ha equips registrats a la base de dades.[/yellow]\n"
        )
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", justify="right", style="dim", width=5)
    table.add_column("Nom de l'Equip")
    table.add_column("Regió", justify="center")
    for team in teams:
        table.add_row(str(team["id"]), team["name"], team["region"])
    ctx.console.print(table)
