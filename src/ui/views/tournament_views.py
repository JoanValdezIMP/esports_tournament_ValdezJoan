from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from ui.context import UIContext
from datetime import date, datetime

from models import Team, TeamTournament
from repositories import TeamRepository


from models import Tournament, Region, VideoGameType, TournamentMode, TournamentStatus
from repositories import (
    TournamentRepository,
    RegionRepository,
    VideoGameTypeRepository,
    TournamentModeRepository,
    TournamentStatusRepository,
)
# menu
# llistar tornejos
# crear/actualitzar/eliminar torneig
# inscriure equip a torneig


def tournament_menu(ctx: UIContext):
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Tornejos")

        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Tornejos")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Torneig")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Torneig")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Torneig")
        ctx.console.print("[bold cyan]5.[/bold cyan] Inscriure Equip a Torneig")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n")

        opcion = Prompt.ask("[bold green]Tria una opció[/bold green]", choices=["0", "1", "2", "3", "4", "5"])

        if opcion == "1": listar_torneos(ctx)
        elif opcion == "2": crear_torneo(ctx)
        elif opcion == "3": actualizar_torneo(ctx)
        elif opcion == "4": eliminar_torneo(ctx)
        elif opcion == "5": inscriure_equip_a_torneig(ctx)
        elif opcion == "0": break






# Funcions auxiliars per a cada opció del menú de tornejos
# parse date function per validar i convertir les dates d'entrada
def parse_date(value: str, field_name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"El camp {field_name} ha de tenir el format YYYY-MM-DD.")


def listar_torneos(ctx: UIContext):
    ctx.print_header("Llista de Tornejos")

    with ctx.uow_factory() as uow:
        repo = TournamentRepository(uow, Tournament)
        torneos = repo.get_all()

        if not torneos:
            ctx.console.print("[yellow]Actualment no hi ha tornejos registrats.[/yellow]\n")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Nom del Torneig")
        table.add_column("Regió", justify="center")
        table.add_column("Videojoc", justify="center")
        table.add_column("Mode", justify="center")
        table.add_column("Estat", justify="center")
        table.add_column("Inici", justify="center")
        table.add_column("Fi", justify="center")
        table.add_column("Equips", justify="center")
        table.add_column("Premi", justify="center")

        for t in torneos:
            region_name = getattr(t.region, "name", str(getattr(t, "id_region", "-")))
            videogame_name = getattr(t.video_game_type, "name", str(getattr(t, "id_video_game_type", "-")))
            mode_name = getattr(t.tournament_mode, "name", str(getattr(t, "id_tournament_mode", "-")))
            status_name = getattr(t.tournament_status, "name", str(getattr(t, "id_tournament_status", "-")))

            table.add_row(
                str(t.id),
                t.name,
                region_name,
                videogame_name,
                mode_name,
                status_name,
                str(t.start_date),
                str(t.end_date) if t.end_date else "-",
                str(t.max_teams),
                f"{t.prize_pool:.2f}"
            )

        ctx.console.print(table)

    Prompt.ask("\nPrem Enter per tornar")


def crear_torneo(ctx: UIContext):
    ctx.print_header("Crear Nou Torneig")
    nombre = Prompt.ask("Nom del Torneig")

    inicio_str = Prompt.ask("Data d'inici (YYYY-MM-DD)")
    fin_str = Prompt.ask("Data de fi (YYYY-MM-DD) (deixar buit si no aplica)", default="")
    premio_str = Prompt.ask("Prize pool")
    max_teams_str = Prompt.ask("Nombre màxim d'equips")
    region_id = IntPrompt.ask("ID de la Regió")
    videogame_type_id = IntPrompt.ask("ID del Tipus de Videojoc")
    torneo_mode_id = IntPrompt.ask("ID del Mode de Torneig")
    status_id = IntPrompt.ask("ID de l'Estat del Torneig")

    try:
        inicio = parse_date(inicio_str, "Data d'inici")
        fin = parse_date(fin_str, "Data de fi") if fin_str else None
        premio = float(premio_str)
        max_teams = int(max_teams_str)
    except ValueError as e:
        ctx.print_error(str(e))
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        region_repo = RegionRepository(uow, Region)
        videogame_repo = VideoGameTypeRepository(uow, VideoGameType)
        mode_repo = TournamentModeRepository(uow, TournamentMode)
        status_repo = TournamentStatusRepository(uow, TournamentStatus)

        region = region_repo.get(region_id)
        videogame = videogame_repo.get(videogame_type_id)
        mode = mode_repo.get(torneo_mode_id)
        status = status_repo.get(status_id)

        if not region or not videogame or not mode or not status:
            ctx.print_error("Un o més IDs de relació no existeixen. Revisa els catàlegs de regions, videojocs, modes i estats.")
            Prompt.ask("Prem Enter per tornar")
            return

        nuevo_torneo = Tournament(
            name=nombre,
            start_date=inicio,
            end_date=fin,
            prize_pool=premio,
            max_teams=max_teams,
            id_region=region_id,
            id_video_game_type=videogame_type_id,
            id_tournament_mode=torneo_mode_id,
            id_tournament_status=status_id,
        )

        repo = TournamentRepository(uow, Tournament)
        try:
            repo.add(nuevo_torneo)
            uow.commit()
            ctx.print_success(f"Torneig '{nombre}' creat amb èxit.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en crear el torneig: {e}")

    Prompt.ask("Prem Enter per continuar")


def actualizar_torneo(ctx: UIContext):
    ctx.print_header("Actualitzar Dades del Torneig")
    id_str = Prompt.ask("Introdueix l'ID del torneig a actualitzar")

    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = TournamentRepository(uow, Tournament)
        torneo = repo.get(int(id_str))

        if not torneo:
            ctx.print_error("Torneig no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return

        nuevo_nombre = Prompt.ask(f"Nou nom (actual: {torneo.name})", default=torneo.name)
        nuevo_inicio = Prompt.ask(
            f"Data d'inici (YYYY-MM-DD, actual: {torneo.start_date})",
            default=str(torneo.start_date),
        )
        nuevo_fin = Prompt.ask(
            f"Data de fi (YYYY-MM-DD, actual: {torneo.end_date or 'buit'})",
            default=str(torneo.end_date) if torneo.end_date else "",
        )
        nuevo_premio = Prompt.ask(f"Prize pool (actual: {torneo.prize_pool})", default=str(torneo.prize_pool))
        nuevo_max = Prompt.ask(f"Màx. equips (actual: {torneo.max_teams})", default=str(torneo.max_teams))

        try:
            inicio = parse_date(nuevo_inicio, "Data d'inici")
            fin = parse_date(nuevo_fin, "Data de fi") if nuevo_fin else None
            premio = float(nuevo_premio)
            max_teams = int(nuevo_max)
        except ValueError as e:
            ctx.print_error(str(e))
            Prompt.ask("Prem Enter per tornar")
            return

        torneo.name = nuevo_nombre
        torneo.start_date = inicio
        torneo.end_date = fin
        torneo.prize_pool = premio
        torneo.max_teams = max_teams
        uow.commit()
        ctx.print_success("Torneig actualitzat correctament.")

    Prompt.ask("Prem Enter per continuar")


def eliminar_torneo(ctx: UIContext):
    ctx.print_header("Eliminar Torneig")
    id_str = Prompt.ask("Introdueix l'ID del torneig a eliminar")

    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = TournamentRepository(uow, Tournament)
        torneo = repo.get(int(id_str))

        if not torneo:
            ctx.print_error("Torneig no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return

        nombre_torneo = getattr(torneo, "name", str(torneo.id))
        confirmacion = Confirm.ask(
            f"Segur que vols eliminar el torneig [bold red]{nombre_torneo}[/bold red]? Tots els partits associats es podrien perdre."
        )
        if confirmacion:
            try:
                repo.delete(torneo)
                uow.commit()
                ctx.print_success("Torneig eliminat del sistema.")
            except Exception as e:
                uow.rollback()
                ctx.print_error(f"Error en eliminar el torneig: {e}")

    Prompt.ask("Prem Enter per continuar")




def inscriure_equip_a_torneig(ctx: UIContext):
    ctx.print_header("Inscriure Equip a Torneig")
    id_torneig = IntPrompt.ask("ID del Torneig")
    id_equip = IntPrompt.ask("ID de l'Equip")
    
    with ctx.uow_factory() as uow:
        tour_repo = TournamentRepository(uow, Tournament)
        team_repo = TeamRepository(uow, Team)
        
        if not tour_repo.get(id_torneig) or not team_repo.get(id_equip):
            ctx.print_error("El Torneig o l'Equip no existeixen.")
            Prompt.ask("Prem Enter per tornar")
            return

        # Creem la inscripció
        inscripcio = TeamTournament(id_team=id_equip, id_tournament=id_torneig)
        
        try:
            uow.session.add(inscripcio)
            uow.commit()
            ctx.print_success("Equip inscrit al torneig correctament.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en inscriure l'equip: {e}")
            
    Prompt.ask("Prem Enter per continuar")






