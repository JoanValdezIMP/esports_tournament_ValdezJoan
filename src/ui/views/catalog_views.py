from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from client.tcp_client import ProtocolError, ServerConnectionError
from ui.context import UIContext


def catalog_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Catàlegs del Sistema")

        ctx.console.print("[bold cyan]1.[/bold cyan] Veure Regions")
        ctx.console.print(
            "[bold cyan]2.[/bold cyan] Gestionar Modes de Torneig"
        )
        ctx.console.print(
            "[bold cyan]3.[/bold cyan] Gestionar Estats de Torneig"
        )
        ctx.console.print(
            "[bold cyan]4.[/bold cyan] Gestionar Tipus de Videojoc"
        )
        ctx.console.print("[bold cyan]5.[/bold cyan] Veure Perfils de Jugador")
        ctx.console.print("[bold cyan]6.[/bold cyan] Afegir Regió")
        ctx.console.print(
            "[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n"
        )

        option = Prompt.ask(
            "[bold green]Tria un catàleg[/bold green]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
        )

        if option == "1":
            list_regions(ctx)
        elif option == "2":
            tournament_mode_menu(ctx)
        elif option == "3":
            tournament_status_menu(ctx)
        elif option == "4":
            video_game_type_menu(ctx)
        elif option == "5":
            list_player_profiles(ctx)
        elif option == "6":
            create_region(ctx)
        elif option == "0":
            break


def list_regions(ctx: UIContext) -> None:
    ctx.print_header("Llista de Regions")
    regions = _request(ctx, "regions.list", {})
    if regions is not None:
        _render_table(
            ctx,
            regions,
            (
                ("id", "ID"),
                ("name", "Nom de la Regió"),
                ("country_code", "Codi ISO"),
            ),
            "No hi ha regions registrades.",
        )
    Prompt.ask("\nPrem Enter per tornar")


def create_region(ctx: UIContext) -> None:
    ctx.print_header("Crear Regió")
    name = Prompt.ask("Nom de la regió")
    country_code = Prompt.ask("Codi ISO")
    result = _request(
        ctx,
        "regions.create",
        {"name": name, "country_code": country_code},
    )
    if result is not None:
        ctx.print_success(f"Regió '{name}' creada correctament.")
    Prompt.ask("Prem Enter per continuar")


def list_tournament_statuses(ctx: UIContext) -> None:
    ctx.print_header("Llista d'Estats de Torneig")
    statuses = _request(ctx, "tournament_statuses.list", {})
    if statuses is not None:
        _render_table(
            ctx,
            statuses,
            (("id", "ID"), ("name", "Estat"), ("description", "Descripció")),
            "No hi ha estats de torneig registrats.",
            header_style="bold yellow",
        )
    Prompt.ask("\nPrem Enter per tornar")


def create_tournament_status(ctx: UIContext) -> None:
    ctx.print_header("Crear Estat de Torneig")
    name = Prompt.ask("Nom de l'estat")
    description = Prompt.ask("Descripció (opcional)").strip()
    result = _request(
        ctx,
        "tournament_statuses.create",
        {"name": name, "description": description or None},
    )
    if result is not None:
        ctx.print_success(f"Estat '{name}' creat correctament.")
    Prompt.ask("Prem Enter per continuar")


def tournament_status_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió d'Estats de Torneig")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Estats")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Estat")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar\n")
        option = Prompt.ask("Tria una opció", choices=["0", "1", "2"])
        if option == "1":
            list_tournament_statuses(ctx)
        elif option == "2":
            create_tournament_status(ctx)
        elif option == "0":
            break


def list_tournament_modes(ctx: UIContext) -> None:
    ctx.print_header("Llista de Modes de Torneig")
    modes = _request(ctx, "tournament_modes.list", {})
    if modes is not None:
        _render_table(
            ctx,
            modes,
            (
                ("id", "ID"),
                ("name", "Nom del Mode"),
                ("description", "Descripció"),
            ),
            "No hi ha modes de torneig registrats.",
            header_style="bold magenta",
        )
    Prompt.ask("\nPrem Enter per tornar")


def create_tournament_mode(ctx: UIContext) -> None:
    ctx.print_header("Crear Mode de Torneig")
    name = Prompt.ask("Nom del mode (ex. 1vs1, 5vs5)").strip()
    description = Prompt.ask("Descripció (opcional)").strip()
    result = _request(
        ctx,
        "tournament_modes.create",
        {"name": name, "description": description or None},
    )
    if result is not None:
        ctx.print_success("Mode de torneig creat amb èxit.")
    Prompt.ask("Prem Enter per continuar")


def update_tournament_mode(ctx: UIContext) -> None:
    _update_named_catalog(
        ctx,
        operation_prefix="tournament_modes",
        title="Actualitzar Mode de Torneig",
        not_found="Mode no trobat.",
        success="Mode actualitzat correctament.",
    )


def delete_tournament_mode(ctx: UIContext) -> None:
    _delete_named_catalog(
        ctx,
        operation_prefix="tournament_modes",
        title="Eliminar Mode de Torneig",
        not_found="Mode no trobat.",
        confirmation="Segur que vols eliminar el mode '{name}'?",
        success="Mode eliminat del sistema.",
        in_use_message="No es pot eliminar perquè està en ús per un torneig.",
    )


def tournament_mode_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Modes de Torneig")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Modes")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Mode")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Mode")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Mode")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar\n")
        option = Prompt.ask(
            "Tria una opció", choices=["0", "1", "2", "3", "4"]
        )
        if option == "1":
            list_tournament_modes(ctx)
        elif option == "2":
            create_tournament_mode(ctx)
        elif option == "3":
            update_tournament_mode(ctx)
        elif option == "4":
            delete_tournament_mode(ctx)
        elif option == "0":
            break


def list_video_game_types(ctx: UIContext) -> None:
    ctx.print_header("Llista de Tipus de Videojoc")
    game_types = _request(ctx, "video_game_types.list", {})
    if game_types is not None:
        _render_table(
            ctx,
            game_types,
            (
                ("id", "ID"),
                ("name", "Gènere / Tipus"),
                ("description", "Descripció"),
            ),
            "No hi ha tipus de videojoc registrats.",
            header_style="bold green",
        )
    Prompt.ask("\nPrem Enter per tornar")


def create_video_game_type(ctx: UIContext) -> None:
    ctx.print_header("Crear Tipus de Videojoc")
    name = Prompt.ask("Nom del tipus (ex. MOBA, Shooter)").strip()
    description = Prompt.ask("Descripció (opcional)").strip()
    result = _request(
        ctx,
        "video_game_types.create",
        {"name": name, "description": description or None},
    )
    if result is not None:
        ctx.print_success("Tipus de videojoc creat amb èxit.")
    Prompt.ask("Prem Enter per continuar")


def update_video_game_type(ctx: UIContext) -> None:
    _update_named_catalog(
        ctx,
        operation_prefix="video_game_types",
        title="Actualitzar Tipus de Videojoc",
        not_found="Tipus de joc no trobat.",
        success="Tipus de joc actualitzat correctament.",
    )


def delete_video_game_type(ctx: UIContext) -> None:
    _delete_named_catalog(
        ctx,
        operation_prefix="video_game_types",
        title="Eliminar Tipus de Videojoc",
        not_found="Tipus de joc no trobat.",
        confirmation="Segur que vols eliminar el tipus '{name}'?",
        success="Tipus de videojoc eliminat del sistema.",
        in_use_message="No es pot eliminar perquè està en ús per un torneig.",
    )


def video_game_type_menu(ctx: UIContext) -> None:
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Tipus de Videojoc")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Tipus")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Tipus")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Tipus")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Tipus")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar\n")
        option = Prompt.ask(
            "Tria una opció", choices=["0", "1", "2", "3", "4"]
        )
        if option == "1":
            list_video_game_types(ctx)
        elif option == "2":
            create_video_game_type(ctx)
        elif option == "3":
            update_video_game_type(ctx)
        elif option == "4":
            delete_video_game_type(ctx)
        elif option == "0":
            break


def list_player_profiles(ctx: UIContext) -> None:
    ctx.print_header("Catàleg: Perfils de Jugadors")
    profiles = _request(ctx, "player_profiles.list", {})
    if profiles is not None:
        _render_table(
            ctx,
            profiles,
            (
                ("nickname", "Nickname"),
                ("ranking_position", "Rànquing"),
                ("total_matches", "Partides Jugades"),
                ("total_points", "Punts Totals"),
            ),
            "No hi ha perfils registrats al sistema.",
            header_style="bold blue",
            empty_values={"ranking_position": "-"},
        )
    Prompt.ask("\nPrem Enter per tornar")


def _update_named_catalog(
    ctx: UIContext,
    operation_prefix: str,
    title: str,
    not_found: str,
    success: str,
) -> None:
    ctx.print_header(title)
    item_id = _prompt_id(ctx, "Introdueix l'ID a actualitzar")
    if item_id is None:
        return

    items = _request(ctx, f"{operation_prefix}.list", {})
    if items is None:
        Prompt.ask("Prem Enter per tornar")
        return
    item = _find_item(items, item_id)
    if item is None:
        ctx.print_error(not_found)
        Prompt.ask("Prem Enter per tornar")
        return

    name = Prompt.ask(f"Nou nom (actual: {item['name']})").strip()
    description = Prompt.ask(
        f"Nova descripció (actual: {item.get('description') or ''})"
    ).strip()
    result = _request(
        ctx,
        f"{operation_prefix}.update",
        {
            "id": item_id,
            "name": name or item["name"],
            "description": description or item.get("description"),
        },
    )
    if result is not None:
        ctx.print_success(success)
    Prompt.ask("Prem Enter per continuar")


def _delete_named_catalog(
    ctx: UIContext,
    operation_prefix: str,
    title: str,
    not_found: str,
    confirmation: str,
    success: str,
    in_use_message: str,
) -> None:
    ctx.print_header(title)
    item_id = _prompt_id(ctx, "Introdueix l'ID a eliminar")
    if item_id is None:
        return

    items = _request(ctx, f"{operation_prefix}.list", {})
    if items is None:
        Prompt.ask("Prem Enter per tornar")
        return
    item = _find_item(items, item_id)
    if item is None:
        ctx.print_error(not_found)
        Prompt.ask("Prem Enter per tornar")
        return

    if Confirm.ask(confirmation.format(name=item["name"])):
        result = _request(ctx, f"{operation_prefix}.delete", {"id": item_id})
        if result is not None:
            ctx.print_success(success)
        elif getattr(ctx, "last_error_code", None) == "validation_error":
            ctx.print_error(in_use_message)
    Prompt.ask("Prem Enter per continuar")


def _prompt_id(ctx: UIContext, prompt: str) -> int | None:
    value = Prompt.ask(prompt)
    if not value.isdigit() or int(value) <= 0:
        ctx.print_error("L'ID ha de ser un número positiu.")
        Prompt.ask("Prem Enter per tornar")
        return None
    return int(value)


def _find_item(items: object, item_id: int) -> dict | None:
    if not isinstance(items, list):
        return None
    return next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        None,
    )


def _request(ctx: UIContext, operation: str, data: dict) -> object | None:
    try:
        response = ctx.tcp_client.request(operation, data)
    except (ProtocolError, ServerConnectionError, ValueError) as error:
        ctx.print_error(str(error))
        return None

    if not response["ok"]:
        error = response["error"]
        ctx.last_error_code = error["code"] if error else None
        ctx.print_error(error["message"] if error else "Error de servidor.")
        return None
    ctx.last_error_code = None
    return response["data"]


def _render_table(
    ctx: UIContext,
    rows: object,
    columns: tuple[tuple[str, str], ...],
    empty_message: str,
    header_style: str = "bold cyan",
    empty_values: dict[str, str] | None = None,
) -> None:
    if not isinstance(rows, list) or any(
        not isinstance(row, dict) for row in rows
    ):
        ctx.print_error("El servidor devolvió datos de catálogo no válidos.")
        return
    if not rows:
        ctx.console.print(f"[yellow]{empty_message}[/yellow]")
        return

    table = Table(show_header=True, header_style=header_style)
    for key, label in columns:
        table.add_column(label)
    replacements = empty_values or {}
    for row in rows:
        if any(key not in row for key, _ in columns):
            ctx.print_error(
                "El servidor devolvió datos de catálogo incompletos."
            )
            return
        table.add_row(
            *[
                str(row[key])
                if row[key] is not None
                else replacements.get(key, "")
                for key, _ in columns
            ]
        )
    ctx.console.print(table)
