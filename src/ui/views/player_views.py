from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from ui.context import UIContext
from models import Player, PlayerProfile
from repositories import PlayerRepository
from datetime import datetime
# menu
# llistar jugadors
# crear jugador
# actualitzar jugador
# eliminar jugador
# cercar jugador


def player_menu(ctx: UIContext):
    """Submenú principal per a Jugadors"""
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Jugadors")

        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Jugadors")
        ctx.console.print("[bold cyan]2.[/bold cyan] Afegir Jugador (Demostrar Relació 1:1)")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Jugador")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Jugador")
        ctx.console.print("[bold cyan]5.[/bold cyan] Cercar Jugador")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n")

        opcion = Prompt.ask("[bold green]Tria una opció[/bold green]", choices=["0", "1", "2", "3", "4", "5"])

        if opcion == "1":
            listar_jugadores(ctx)
        elif opcion == "2":
            crear_jugador(ctx)
        elif opcion == "3":
            actualizar_jugador(ctx)
        elif opcion == "4":
            eliminar_jugador(ctx)
        elif opcion == "5":
            cercar_jugador(ctx)
        elif opcion == "0":
            break


def listar_jugadores(ctx: UIContext):
    ctx.print_header("Llista de Jugadors")

    with ctx.uow_factory() as uow:
        repo = PlayerRepository(uow, Player)
        jugadores = repo.get_all()

        if not jugadores:
            ctx.console.print("[yellow]Encara no hi ha jugadors registrats.[/yellow]\n")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Nickname")
        table.add_column("Regió")
        table.add_column("Perfil")

        for j in jugadores:
            region_name = getattr(j.region, "name", None) or str(getattr(j, "id_region", "-"))
            tiene_perfil = "Sí" if getattr(j, "profile", None) else "No"
            table.add_row(str(j.id), j.nickname, region_name, tiene_perfil)

        ctx.console.print(table)

    Prompt.ask("\nPrem Enter per tornar")


def crear_jugador(ctx: UIContext):
    ctx.print_header("Afegir Nou Jugador")
    nickname = Prompt.ask("Nickname")
    email = Prompt.ask("Email")
    region_id = IntPrompt.ask("ID de la Regió")

    hoy = datetime.now()

    nuevo_jugador = Player(
        nickname=nickname,
        email=email,
        birth_date=hoy,
        registration_date=hoy,
        id_region=region_id,
        active=True
    )

    crear_perfil = Confirm.ask("Vols crear el seu Perfil de Jugador ara mateix?")
    if crear_perfil:
        ranking = IntPrompt.ask("Rànquing inicial", default=0)
        nuevo_jugador.profile = PlayerProfile(ranking_position=ranking)

    with ctx.uow_factory() as uow:
        repo = PlayerRepository(uow, Player)
        try:
            repo.add(nuevo_jugador)
            uow.commit()
            ctx.print_success(f"Jugador '{nickname}' creat correctament.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en desar: {e}")

    Prompt.ask("Prem Enter per continuar")


def actualizar_jugador(ctx: UIContext):
    ctx.print_header("Actualitzar Jugador")
    id_str = Prompt.ask("Introdueix l'ID del jugador a actualitzar")

    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser un número.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = PlayerRepository(uow, Player)
        jugador = repo.get(int(id_str))

        if not jugador:
            ctx.print_error("Jugador no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return

        nuevo_nick = Prompt.ask(f"Nou nickname (actual: {jugador.nickname})")
        if nuevo_nick:
            jugador.nickname = nuevo_nick
            uow.commit()
            ctx.print_success("Jugador actualitzat.")

    Prompt.ask("Prem Enter per continuar")


def eliminar_jugador(ctx: UIContext):
    ctx.print_header("Eliminar Jugador")
    id_str = Prompt.ask("Introdueix l'ID del jugador a eliminar")

    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser un número.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = PlayerRepository(uow, Player)
        jugador = repo.get(int(id_str))

        if not jugador:
            ctx.print_error("Jugador no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return

        confirmacion = Confirm.ask(f"Segur que vols eliminar a {jugador.nickname}?")
        if confirmacion:
            if getattr(jugador, "profile", None):
                uow.session.delete(jugador.profile)
            repo.delete(jugador)
            try:
                uow.commit()
                ctx.print_success("Jugador eliminat.")
            except Exception as e:
                uow.rollback()
                ctx.print_error(f"Error en eliminar el jugador: {e}")

    Prompt.ask("Prem Enter per continuar")




def cercar_jugador(ctx: UIContext):
    ctx.print_header("Cercar Jugador")
    cerca = Prompt.ask("Introdueix part del nickname a cercar")
    
    with ctx.uow_factory() as uow:
        repo = PlayerRepository(uow, Player)
        jugadors = repo.search_by_nickname(cerca) # Cridem al nou mètode del repo

        if not jugadors:
            ctx.console.print("[yellow]No s'han trobat jugadors amb aquest nom.[/yellow]")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Nickname")
        table.add_column("Regió")
        table.add_column("Perfil")

        for j in jugadors:
            region_name = getattr(j.region, "name", None) or str(getattr(j, "id_region", "-"))
            tiene_perfil = "Sí" if getattr(j, "profile", None) else "No"
            table.add_row(str(j.id), j.nickname, region_name, tiene_perfil)

        ctx.console.print(table)
    
    Prompt.ask("\nPrem Enter per tornar")