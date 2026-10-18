from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from ui.context import UIContext
from client.tcp_client import ProtocolError, ServerConnectionError


def player_menu(ctx: UIContext):
    """Submenú principal per a Jugadors"""
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Jugadors")

        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Jugadors")
        ctx.console.print(
            "[bold cyan]2.[/bold cyan] Afegir Jugador (Demostrar Relació 1:1)"
        )
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Jugador")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Jugador")
        ctx.console.print("[bold cyan]5.[/bold cyan] Cercar Jugador")
        ctx.console.print(
            "[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n"
        )

        option = Prompt.ask(
            "[bold green]Tria una opció[/bold green]",
            choices=["0", "1", "2", "3", "4", "5"],
        )

        if option == "1":
            list_players(ctx)
        elif option == "2":
            create_player(ctx)
        elif option == "3":
            update_player(ctx)
        elif option == "4":
            delete_player(ctx)
        elif option == "5":
            search_players(ctx)
        elif option == "0":
            break


def list_players(ctx: UIContext):
    ctx.print_header("Llista de Jugadors")
    players = _request(ctx, "players.list", {})
    if players is None:
        Prompt.ask("Prem Enter per tornar")
        return

    _display_players(ctx, players)

    Prompt.ask("\nPrem Enter per tornar")


def create_player(ctx: UIContext):
    ctx.print_header("Afegir Nou Jugador")
    nickname = Prompt.ask("Nickname")
    email = Prompt.ask("Email")
    region_id = IntPrompt.ask("ID de la Regió")

    create_profile = Confirm.ask(
        "Vols crear el seu Perfil de Jugador ara mateix?"
    )
    request_data = {
        "nickname": nickname,
        "email": email,
        "region_id": region_id,
    }
    if create_profile:
        request_data["ranking_position"] = IntPrompt.ask(
            "Rànquing inicial", default=0
        )

    if _request(ctx, "players.create", request_data) is not None:
        ctx.print_success(f"Jugador '{nickname}' creat correctament.")

    Prompt.ask("Prem Enter per continuar")


def update_player(ctx: UIContext):
    ctx.print_header("Actualitzar Jugador")
    id_text = Prompt.ask("Introdueix l'ID del jugador a actualitzar")

    if not id_text.isdigit():
        ctx.print_error("L'ID ha de ser un número.")
        Prompt.ask("Prem Enter per tornar")
        return

    player = _request(ctx, "players.read", {"id": int(id_text)})
    if player is None:
        Prompt.ask("Prem Enter per tornar")
        return

    if not isinstance(player, dict) or not isinstance(
        player.get("nickname"), str
    ):
        ctx.print_error("El servidor devolvió datos de jugador no válidos.")
        Prompt.ask("Prem Enter per tornar")
        return

    new_nickname = Prompt.ask(f"Nou nickname (actual: {player['nickname']})")
    if new_nickname:
        updated_player = _request(
            ctx,
            "players.update",
            {"id": int(id_text), "nickname": new_nickname},
        )
        if updated_player is not None:
            ctx.print_success("Jugador actualitzat.")

    Prompt.ask("Prem Enter per continuar")


def delete_player(ctx: UIContext):
    ctx.print_header("Eliminar Jugador")
    id_text = Prompt.ask("Introdueix l'ID del jugador a eliminar")

    if not id_text.isdigit():
        ctx.print_error("L'ID ha de ser un número.")
        Prompt.ask("Prem Enter per tornar")
        return

    player = _request(ctx, "players.read", {"id": int(id_text)})
    if player is None:
        Prompt.ask("Prem Enter per tornar")
        return

    nickname = (
        player.get("nickname", "aquest jugador")
        if isinstance(player, dict)
        else "aquest jugador"
    )
    confirmation = Confirm.ask(f"Segur que vols eliminar a {nickname}?")
    if confirmation:
        deleted = _request(ctx, "players.delete", {"id": int(id_text)})
        if deleted is not None:
            ctx.print_success("Jugador eliminat.")

    Prompt.ask("Prem Enter per continuar")


def search_players(ctx: UIContext):
    ctx.print_header("Cercar Jugador")
    search_term = Prompt.ask("Introdueix part del nickname a cercar")
    players = _request(ctx, "players.search", {"nickname": search_term})
    if players is None:
        Prompt.ask("Prem Enter per tornar")
        return
    _display_players(
        ctx,
        players,
        empty_message="No s'han trobat jugadors amb aquest nom.",
    )

    Prompt.ask("\nPrem Enter per tornar")


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


def _display_players(
    ctx: UIContext,
    players: object,
    empty_message: str = "Encara no hi ha jugadors registrats.",
) -> None:
    if not isinstance(players, list) or any(
        not isinstance(player, dict)
        or not isinstance(player.get("id"), int)
        or not isinstance(player.get("nickname"), str)
        or not isinstance(player.get("region"), str)
        or not isinstance(player.get("has_profile"), bool)
        for player in players
    ):
        ctx.print_error(
            "El servidor devolvió una lista de jugadores no válida."
        )
        return

    if not players:
        ctx.console.print(f"[yellow]{empty_message}[/yellow]\n")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Nickname")
    table.add_column("Regió")
    table.add_column("Perfil")
    for player in players:
        profile = "Sí" if player["has_profile"] else "No"
        table.add_row(
            str(player["id"]),
            player["nickname"],
            player["region"],
            profile,
        )
    ctx.console.print(table)
