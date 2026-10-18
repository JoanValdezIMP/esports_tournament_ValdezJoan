from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from client.tcp_client import ProtocolError, ServerConnectionError
from ui.context import UIContext


def match_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Partits (Matches)")
        ctx.console.print("[bold cyan]1.[/bold cyan] Calendari i Resultats")
        ctx.console.print("[bold cyan]2.[/bold cyan] Registrar Nou Partit")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Resultat")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Partit")
        ctx.console.print(
            "[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n"
        )
        option = Prompt.ask(
            "[bold green]Tria una opció[/bold green]",
            choices=["0", "1", "2", "3", "4"],
        )
        if option == "1":
            list_matches(ctx)
        elif option == "2":
            create_match(ctx)
        elif option == "3":
            update_match_result(ctx)
        elif option == "4":
            delete_match(ctx)
        elif option == "0":
            break


def list_matches(ctx: UIContext) -> None:
    ctx.print_header("Historial i Calendari de Partits")
    matches = _request(ctx, "matches.list", {})
    if matches is None:
        Prompt.ask("Prem Enter per tornar")
        return
    if not isinstance(matches, list) or any(
        not isinstance(match, dict)
        or any(
            field not in match
            for field in (
                "id",
                "match_date",
                "tournament_id",
                "team_one_id",
                "team_two_id",
                "score_team_one",
                "score_team_two",
                "round_number",
            )
        )
        for match in matches
    ):
        ctx.print_error(
            "El servidor ha retornat una llista de partits no vàlida."
        )
    elif not matches:
        ctx.console.print(
            "[yellow]Encara no hi ha partits registrats.[/yellow]\n"
        )
    else:
        table = Table(show_header=True, header_style="bold green")
        for heading in (
            "ID",
            "Data",
            "Torneig",
            "Equip A",
            "Equip B",
            "Resultat",
            "Ronda",
        ):
            table.add_column(heading)
        for match in matches:
            table.add_row(
                str(match["id"]),
                str(match["match_date"]),
                str(match["tournament_id"]),
                str(match["team_one_id"]),
                str(match["team_two_id"]),
                f"{match['score_team_one']} - {match['score_team_two']}",
                str(match["round_number"]),
            )
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")


def create_match(ctx: UIContext) -> None:
    ctx.print_header("Registrar Nou Partit")
    result = _request(
        ctx,
        "matches.create",
        {
            "tournament_id": IntPrompt.ask("ID del Torneig"),
            "team_one_id": IntPrompt.ask("ID de l'Equip A (Local)"),
            "team_two_id": IntPrompt.ask("ID de l'Equip B (Visitant)"),
            "round_number": IntPrompt.ask("Ronda del partit"),
            "duration_minutes": IntPrompt.ask("Durada en minuts"),
        },
    )
    if result is not None:
        ctx.print_success("El partit s'ha registrat al calendari.")
    Prompt.ask("Prem Enter per continuar")


def update_match_result(ctx: UIContext) -> None:
    ctx.print_header("Actualitzar Resultat del Partit")
    match_id = _prompt_id(ctx, "Introdueix l'ID del partit")
    if match_id is None:
        return
    matches = _request(ctx, "matches.list", {})
    match = _find_match(matches, match_id)
    if match is None:
        ctx.print_error("Partit no trobat.")
        Prompt.ask("Prem Enter per tornar")
        return
    team_one_score = IntPrompt.ask(
        f"Puntuació de l'Equip A (actual: {match['score_team_one']})",
        default=match["score_team_one"],
    )
    team_two_score = IntPrompt.ask(
        f"Puntuació de l'Equip B (actual: {match['score_team_two']})",
        default=match["score_team_two"],
    )
    if (
        _request(
            ctx,
            "matches.update_result",
            {
                "id": match_id,
                "score_team_one": team_one_score,
                "score_team_two": team_two_score,
            },
        )
        is not None
    ):
        ctx.print_success("Resultat actualitzat amb èxit.")
    Prompt.ask("Prem Enter per continuar")


def delete_match(ctx: UIContext) -> None:
    ctx.print_header("Cancel·lar / Eliminar Partit")
    match_id = _prompt_id(ctx, "Introdueix l'ID del partit a eliminar")
    if match_id is None:
        return
    if _find_match(_request(ctx, "matches.list", {}), match_id) is None:
        ctx.print_error("Partit no trobat.")
        Prompt.ask("Prem Enter per tornar")
        return
    if Confirm.ask(f"Segur que vols cancel·lar el partit ID {match_id}?"):
        if _request(ctx, "matches.delete", {"id": match_id}) is not None:
            ctx.print_success("Partit eliminat del calendari.")
    Prompt.ask("Prem Enter per continuar")


def _find_match(matches: object, match_id: int) -> dict | None:
    if not isinstance(matches, list):
        return None
    return next(
        (
            match
            for match in matches
            if isinstance(match, dict) and match.get("id") == match_id
        ),
        None,
    )


def _prompt_id(ctx: UIContext, message: str) -> int | None:
    value = Prompt.ask(message)
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
