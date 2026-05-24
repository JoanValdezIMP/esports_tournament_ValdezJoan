# src/ui/views/catalog_views.py
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from ui.context import UIContext

from models import Region, TournamentMode, TournamentStatus, VideoGameType, PlayerProfile
from repositories import (
    RegionRepository, 
    TournamentModeRepository, 
    TournamentStatusRepository, 
    VideoGameTypeRepository,
    PlayerProfileRepository
)

# menu
# llistar regions
# lliar estats de torneig
# llistar modes de torneig

# crear/actualitzar/eliminar modes de torneig
# menu de modes torneig

# llistar tipus de joc
# crear/actualitzar/eliminar tipus de joc
# munenu tipus de joc

# llistar perfils de jugador



# ==========================================
# ORQUESTADOR PRINCIPAL DE CATÀLEGS
# ==========================================
def catalog_menu(ctx: UIContext):
    """Submenú principal per a Catàlegs"""
    while True:
        ctx.console.clear()
        ctx.print_header("Catàlegs del Sistema")
        
        ctx.console.print("[bold cyan]1.[/bold cyan] Veure Regions")
        ctx.console.print("[bold cyan]2.[/bold cyan] Gestionar Modes de Torneig")
        ctx.console.print("[bold cyan]3.[/bold cyan] Veure Estats de Torneig")
        ctx.console.print("[bold cyan]4.[/bold cyan] Gestionar Tipus de Videojoc")
        ctx.console.print("[bold cyan]5.[/bold cyan] Veure Perfils de Jugador")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n")
        
        opcion = Prompt.ask("[bold green]Tria un catàleg[/bold green]", choices=["0", "1", "2", "3", "4", "5"])
        
        if opcion == "1": listar_regiones(ctx)
        elif opcion == "2": menu_modos(ctx)
        elif opcion == "3": listar_estados(ctx)
        elif opcion == "4": menu_tipos_juego(ctx)
        elif opcion == "5": listar_perfiles(ctx)
        elif opcion == "0": break




# ==========================================
# 1. REGIONS I ESTATS (Només Lectura)
# ==========================================
def listar_regiones(ctx: UIContext):
    ctx.print_header("Llista de Regions")
    with ctx.uow_factory() as uow:
        repo = RegionRepository(uow, Region)
        regiones = repo.get_all()
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Nom de la Regió")
        table.add_column("Codi ISO")
        for r in regiones:
            table.add_row(str(r.id), r.name, r.country_code)
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")

def listar_estados(ctx: UIContext):
    ctx.print_header("Llista d'Estats de Torneig")
    with ctx.uow_factory() as uow:
        repo = TournamentStatusRepository(uow, TournamentStatus)
        estados = repo.get_all()
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Estat")
        for e in estados:
            table.add_row(str(e.id), e.name)
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")


# ==========================================
# 2. CRUD: MODES DE TORNEIG
# ==========================================
def listar_modos(ctx: UIContext):
    ctx.print_header("Llista de Modes de Torneig")
    with ctx.uow_factory() as uow:
        repo = TournamentModeRepository(uow, TournamentMode)
        modos = repo.get_all()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Nom del Mode")
        table.add_column("Descripció")
        for m in modos:
            desc = m.description if m.description else "Sense descripció"
            table.add_row(str(m.id), m.name, desc)
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")

def crear_modo(ctx: UIContext):
    ctx.print_header("Crear Mode de Torneig")
    nombre = Prompt.ask("Nom del mode (ex. 1vs1, 5vs5)").strip()
    if not nombre:
        ctx.print_error("El nom no pot estar buit.")
        Prompt.ask("Prem Enter per tornar")
        return
    
    descripcion = Prompt.ask("Descripció (opcional)").strip()
    nuevo_modo = TournamentMode(name=nombre, description=descripcion if descripcion else None)
    
    with ctx.uow_factory() as uow:
        repo = TournamentModeRepository(uow, TournamentMode)
        try:
            repo.add(nuevo_modo)
            uow.commit()
            ctx.print_success("Mode de torneig creat amb èxit.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en desar: {e}")
    Prompt.ask("Prem Enter per continuar")

def actualizar_modo(ctx: UIContext):
    ctx.print_header("Actualitzar Mode de Torneig")
    id_modo = IntPrompt.ask("ID del mode a actualitzar")
    with ctx.uow_factory() as uow:
        repo = TournamentModeRepository(uow, TournamentMode)
        modo = repo.get(id_modo)
        if not modo:
            ctx.print_error("Mode no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        nuevo_nombre = Prompt.ask(f"Nou nom (actual: {modo.name})").strip()
        nueva_desc = Prompt.ask(f"Nova descripció (actual: {modo.description})").strip()
        
        if nuevo_nombre: modo.name = nuevo_nombre
        if nueva_desc: modo.description = nueva_desc
        
        try:
            uow.commit()
            ctx.print_success("Mode actualitzat correctament.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error: {e}")
    Prompt.ask("Prem Enter per continuar")

def eliminar_modo(ctx: UIContext):
    ctx.print_header("Eliminar Mode de Torneig")
    id_modo = IntPrompt.ask("ID del mode a eliminar")
    with ctx.uow_factory() as uow:
        repo = TournamentModeRepository(uow, TournamentMode)
        modo = repo.get(id_modo)
        if not modo:
            ctx.print_error("Mode no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
        
        if Confirm.ask(f"Segur que vols eliminar el mode '{modo.name}'?"):
            try:
                repo.delete(modo)
                uow.commit()
                ctx.print_success("Mode eliminat del sistema.")
            except Exception as e:
                uow.rollback()
                ctx.print_error("No es pot eliminar perquè està en ús per un torneig.")
    Prompt.ask("Prem Enter per continuar")

def menu_modos(ctx: UIContext):
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Modes de Torneig")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Modes")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Mode")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Mode")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Mode")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar\n")
        
        opcion = Prompt.ask("Tria una opció", choices=["0", "1", "2", "3", "4"])
        if opcion == "1": listar_modos(ctx)
        elif opcion == "2": crear_modo(ctx)
        elif opcion == "3": actualizar_modo(ctx)
        elif opcion == "4": eliminar_modo(ctx)
        elif opcion == "0": break


# ==========================================
# 3. CRUD: TIPUS DE VIDEOJOC
# ==========================================
def listar_tipos_juego(ctx: UIContext):
    ctx.print_header("Llista de Tipus de Videojoc")
    with ctx.uow_factory() as uow:
        repo = VideoGameTypeRepository(uow, VideoGameType)
        tipos = repo.get_all()
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Gènere / Tipus")
        table.add_column("Descripció")
        for t in tipos:
            desc = t.description if t.description else "Sense descripció"
            table.add_row(str(t.id), t.name, desc)
        ctx.console.print(table)
    Prompt.ask("\nPrem Enter per tornar")

def crear_tipo_juego(ctx: UIContext):
    ctx.print_header("Crear Tipus de Videojoc")
    nombre = Prompt.ask("Nom del tipus (ex. MOBA, Shooter)").strip()
    if not nombre:
        ctx.print_error("El nom no pot estar buit.")
        Prompt.ask("Prem Enter per tornar")
        return
    
    descripcion = Prompt.ask("Descripció (opcional)").strip()
    nuevo_tipo = VideoGameType(name=nombre, description=descripcion if descripcion else None)
    
    with ctx.uow_factory() as uow:
        repo = VideoGameTypeRepository(uow, VideoGameType)
        try:
            repo.add(nuevo_tipo)
            uow.commit()
            ctx.print_success("Tipus de videojoc creat amb èxit.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error en desar: {e}")
    Prompt.ask("Prem Enter per continuar")

def actualizar_tipo_juego(ctx: UIContext):
    ctx.print_header("Actualitzar Tipus de Videojoc")
    id_tipo = IntPrompt.ask("ID del tipus a actualitzar")
    with ctx.uow_factory() as uow:
        repo = VideoGameTypeRepository(uow, VideoGameType)
        tipo = repo.get(id_tipo)
        if not tipo:
            ctx.print_error("Tipus de joc no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        nuevo_nombre = Prompt.ask(f"Nou nom (actual: {tipo.name})").strip()
        nueva_desc = Prompt.ask(f"Nova descripció (actual: {tipo.description})").strip()
        
        if nuevo_nombre: tipo.name = nuevo_nombre
        if nueva_desc: tipo.description = nueva_desc
        
        try:
            uow.commit()
            ctx.print_success("Tipus de joc actualitzat correctament.")
        except Exception as e:
            uow.rollback()
            ctx.print_error(f"Error: {e}")
    Prompt.ask("Prem Enter per continuar")

def eliminar_tipo_juego(ctx: UIContext):
    ctx.print_header("Eliminar Tipus de Videojoc")
    id_tipo = IntPrompt.ask("ID del tipus a eliminar")
    with ctx.uow_factory() as uow:
        repo = VideoGameTypeRepository(uow, VideoGameType)
        tipo = repo.get(id_tipo)
        if not tipo:
            ctx.print_error("Tipus de joc no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
        
        if Confirm.ask(f"Segur que vols eliminar el tipus '{tipo.name}'?"):
            try:
                repo.delete(tipo)
                uow.commit()
                ctx.print_success("Tipus de joc eliminat del sistema.")
            except Exception as e:
                uow.rollback()
                ctx.print_error("No es pot eliminar perquè està en ús per un torneig.")
    Prompt.ask("Prem Enter per continuar")

def menu_tipos_juego(ctx: UIContext):
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Tipus de Videojoc")
        ctx.console.print("[bold cyan]1.[/bold cyan] Llistar Tipus")
        ctx.console.print("[bold cyan]2.[/bold cyan] Crear Tipus")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Tipus")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Tipus")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar\n")
        
        opcion = Prompt.ask("Tria una opció", choices=["0", "1", "2", "3", "4"])
        if opcion == "1": listar_tipos_juego(ctx)
        elif opcion == "2": crear_tipo_juego(ctx)
        elif opcion == "3": actualizar_tipo_juego(ctx)
        elif opcion == "4": eliminar_tipo_juego(ctx)
        elif opcion == "0": break

# ==========================================
# 4. LLISTAT DE PERFILS DE JUGADOR
# ==========================================
def listar_perfiles(ctx: UIContext):
    ctx.print_header("Catàleg: Perfils de Jugadors")
    
    with ctx.uow_factory() as uow:
        repo = PlayerProfileRepository(uow, PlayerProfile)
        perfiles = repo.get_all()

        if not perfiles:
            ctx.console.print("[yellow]No hi ha perfils registrats al sistema.[/yellow]")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Nickname", style="bold")
        table.add_column("Rànquing", justify="center")
        table.add_column("Partides Jugades", justify="center")
        table.add_column("Punts Totals", justify="right")

        for p in perfiles:
            nickname = getattr(p.player, "nickname", "Desconegut")
            table.add_row(
                nickname, 
                str(p.ranking_position) if p.ranking_position else "-",
                str(p.total_matches),
                str(p.total_points)
            )

        ctx.console.print(table)
    
    Prompt.ask("\nPrem Enter per tornar")

