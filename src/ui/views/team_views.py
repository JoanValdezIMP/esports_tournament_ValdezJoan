# src/ui/views/team_views.py
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from ui.context import UIContext
from datetime import date
# Ajusta estas importaciones a los nombres exactos de tus modelos y repos
from models import Team, Region, PlayerTeam, Player
from repositories import TeamRepository, RegionRepository, PlayerRepository

# menu
# llistar equips
# crear/actualitzar/eliminar equip
# assignar jugador a equip

def team_menu(ctx: UIContext):
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió d'Equips")
        
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Equips")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Equip")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Equip")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Equip")
        ctx.console.print("[bold cyan]5.[/bold cyan] Assignar Jugador a Equip")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n")
        
        opcion = Prompt.ask("[bold green]Tria una opció[/bold green]", choices=["0", "1", "2", "3", "4", "5"])
        
        if opcion == "1": listar_equipos(ctx)
        elif opcion == "2": crear_equipo(ctx)
        elif opcion == "3": actualizar_equipo(ctx)
        elif opcion == "4": eliminar_equipo(ctx)
        elif opcion == "5": assignar_jugador_a_equip(ctx)
        elif opcion == "0": break





def listar_equipos(ctx: UIContext):
    ctx.print_header("Llista d'Equips")
    
    with ctx.uow_factory() as uow:
        # Si tienes un TeamRepository, úsalo. Si usas uno genérico, pásale el modelo Team.
        repo = TeamRepository(uow, Team) 
        equipos = repo.get_all()
        
        if not equipos:
            ctx.console.print("[yellow]No hi ha equips registrats a la base de dades.[/yellow]\n")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Nom de l'Equip")
        table.add_column("Regió", justify="center")

        for eq in equipos:
            region_name = getattr(eq.region, "name", None) or str(getattr(eq, "id_region", "-"))
            table.add_row(str(eq.id), eq.name, region_name)

        ctx.console.print(table)
    
    Prompt.ask("\nPrem Enter per tornar")

def crear_equipo(ctx: UIContext):
    ctx.print_header("Fundar Nou Equip")
    nombre = Prompt.ask("Nom de l'equip")
    if not nombre:
        ctx.print_error("El nom de l'equip no pot estar buit.")
        Prompt.ask("Prem Enter per tornar")
        return
    region_id = IntPrompt.ask("ID de la Regió")
    
    with ctx.uow_factory() as uow:
        # 1. VALIDACIÓN PREVIA: Comprobamos si la región existe
        region_repo = RegionRepository(uow, Region)
        region = region_repo.get(region_id)
        
        if not region:
            ctx.print_error(f"Error: La regió amb ID {region_id} no existeix. Si us plau, revisa el catàleg.")
            Prompt.ask("Prem Enter per tornar")
            return # Salimos de la función sin intentar guardar nada

        # 2. GUARDADO SEGURO
        nuevo_equipo = Team(
            name=nombre, 
            id_region=region_id, 
            creation_date=date.today(), 
            active=True
        )
        
        team_repo = TeamRepository(uow, Team)
        try:
            team_repo.add(nuevo_equipo)
            uow.commit()
            ctx.print_success(f"Equip '{nombre}' fundat amb èxit a la regió {region.name}.")
        except Exception as e:
            # Si algo falla inesperadamente, hacemos rollback y mostramos el error
            uow.rollback() 
            ctx.print_error(f"Error crític en desar: {e}")
            
    Prompt.ask("Prem Enter per continuar")


def actualizar_equipo(ctx: UIContext):
    ctx.print_header("Actualitzar Dades de l'Equip")
    id_str = Prompt.ask("Introdueix l'ID de l'equip a actualitzar")
    
    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = TeamRepository(uow, Team)
        equipo = repo.get(int(id_str))
        
        if not equipo:
            ctx.print_error("Equip no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        nuevo_nombre = Prompt.ask(f"Nou nom (actual: {equipo.name})")
        if nuevo_nombre:
            equipo.name = nuevo_nombre
            uow.commit()
            ctx.print_success("Equip actualitzat amb èxit.")
            
    Prompt.ask("Prem Enter per continuar")

def eliminar_equipo(ctx: UIContext):
    ctx.print_header("Dissoldre Equip")
    id_str = Prompt.ask("Introdueix l'ID de l'equip a dissoldre (eliminar)")
    
    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = TeamRepository(uow, Team)
        equipo = repo.get(int(id_str))
        
        if not equipo:
            ctx.print_error("Equip no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        confirmacion = Confirm.ask(f"Segur que vols dissoldre l'equip [bold red]{equipo.name}[/bold red]?")
        if confirmacion:
            repo.delete(equipo)
            try:
                uow.commit()
                ctx.print_success("Equip eliminat del sistema.")
            except Exception as e:
                uow.rollback()
                ctx.print_error(f"Error en eliminar: {e}")
            
    Prompt.ask("Prem Enter per continuar")



def assignar_jugador_a_equip(ctx: UIContext):
    ctx.print_header("Assignar Jugador a Equip")
    id_equip = IntPrompt.ask("ID de l'Equip")
    id_jugador = IntPrompt.ask("ID del Jugador")
    punts = IntPrompt.ask("Punts obtinguts (o posició)", default=0)

    with ctx.uow_factory() as uow:
        team_repo = TeamRepository(uow, Team)
        player_repo = PlayerRepository(uow, Player)
        
        if not team_repo.get(id_equip) or not player_repo.get(id_jugador):
            ctx.print_error("L'Equip o el Jugador no existeixen.")
            Prompt.ask("Prem Enter per tornar")
            return

        # Creem la relació
        relacio = PlayerTeam(id_player=id_jugador, id_team=id_equip, points_obtained=punts)
        
        try:
            uow.session.add(relacio)
            uow.commit()
            ctx.print_success("Jugador assignat a l'equip correctament.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en assignar: {e}")
            
    Prompt.ask("Prem Enter per continuar")