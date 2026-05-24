# src/ui/views/match_views.py
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from ui.context import UIContext
from datetime import datetime

from models import Match
from repositories import MatchRepository

# menu
# llistar partits
# crear partit
# actualitzar resultat
# eliminar partit

def match_menu(ctx: UIContext):
    """Submenú principal para Partidos"""
    while True:
        ctx.console.clear()
        ctx.print_header("Gestió de Partits (Matches)")
        
        ctx.console.print("[bold cyan]1.[/bold cyan] Calendari i Resultats (Llistar)")
        ctx.console.print("[bold cyan]2.[/bold cyan] Registrar Nou Partit")
        ctx.console.print("[bold cyan]3.[/bold cyan] Actualitzar Resultat")
        ctx.console.print("[bold cyan]4.[/bold cyan] Eliminar Partit")
        ctx.console.print("[bold cyan]0.[/bold cyan] Tornar al Menú Principal\n")
        
        opcion = Prompt.ask("[bold green]Tria una opció[/bold green]", choices=["0", "1", "2", "3", "4"])
        
        if opcion == "1":
            listar_partidos(ctx)
        elif opcion == "2":
            registrar_partido(ctx)
        elif opcion == "3":
            actualizar_resultado(ctx)
        elif opcion == "4":
            eliminar_partido(ctx)
        elif opcion == "0":
            break



def listar_partidos(ctx: UIContext):
    ctx.print_header("Historial i Calendari de Partits")
    
    with ctx.uow_factory() as uow:
        repo = MatchRepository(uow, Match)
        partidos = repo.get_all()
        
        if not partidos:
            ctx.console.print("[yellow]Encara no hi ha partits registrats al sistema.[/yellow]\n")
            Prompt.ask("Prem Enter per tornar")
            return

        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", justify="right", style="dim", width=5)
        table.add_column("Data")
        table.add_column("Torneig", justify="center")
        table.add_column("Equip A", justify="center")
        table.add_column("Equip B", justify="center")
        table.add_column("Resultat", justify="center", style="bold yellow")
        table.add_column("Ronda", justify="center")

        for p in partidos:
            fecha = p.match_date.strftime("%Y-%m-%d %H:%M") if getattr(p, "match_date", None) else "N/A"
            resultado = f"{p.score_team_one} - {p.score_team_two}"
            table.add_row(
                str(p.id),
                fecha,
                str(getattr(p, "id_tournament", "N/A")),
                str(getattr(p, "id_team_one", "N/A")),
                str(getattr(p, "id_team_two", "N/A")),
                resultado,
                str(getattr(p, "round_number", "N/A"))
            )

        ctx.console.print(table)
    
    Prompt.ask("\nPrem Enter per tornar")

def registrar_partido(ctx: UIContext):
    ctx.print_header("Registrar Nou Partit")
    ctx.console.print("[dim]Afegeix un partit al calendari (els resultats es poden afegir després)[/dim]\n")

    torneo_id = Prompt.ask("ID del Torneig al qual pertany")
    eq_a_id = Prompt.ask("ID de l'Equip A (Local)")
    eq_b_id = Prompt.ask("ID de l'Equip B (Visitant)")

    if not (torneo_id.isdigit() and eq_a_id.isdigit() and eq_b_id.isdigit()):
        ctx.print_error("Els IDs han de ser numèrics.")
        Prompt.ask("Prem Enter per tornar")
        return

    round_number = IntPrompt.ask("Ronda del partit")
    duration_minutes = IntPrompt.ask("Durada en minuts")

    nuevo_partido = Match(
        match_date=datetime.now(),
        score_team_one=0,
        score_team_two=0,
        round_number=round_number,
        duration_minutes=duration_minutes,
        id_tournament=int(torneo_id),
        id_team_one=int(eq_a_id),
        id_team_two=int(eq_b_id),
        id_team_winner=None,
    )

    with ctx.uow_factory() as uow:
        repo = MatchRepository(uow, Match)
        try:
            repo.add(nuevo_partido)
            uow.commit()
            ctx.print_success("El partit s'ha registrat al calendari.")
        except Exception as e:
            ctx.print_error(f"Error en registrar el partit. Verifica que els IDs d'equips i tornejos existeixin.\nDetall: {e}")

    Prompt.ask("Prem Enter per continuar")

def actualizar_resultado(ctx: UIContext):
    ctx.print_header("Actualitzar Resultat del Partit")
    id_str = Prompt.ask("Introdueix l'ID del partit")
    
    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = MatchRepository(uow, Match)
        partido = repo.get(int(id_str))
        
        if not partido:
            ctx.print_error("Partit no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        ctx.console.print(
            f"\n[bold cyan]Partit Seleccionat:[/bold cyan] Equip A ({getattr(partido, 'id_team_one', '?')}) vs Equip B ({getattr(partido, 'id_team_two', '?')})"
        )

        puntuacion_a = Prompt.ask(
            "Puntuació de l'Equip A (Local)",
            default=str(partido.score_team_one) if partido.score_team_one is not None else "0"
        )
        puntuacion_b = Prompt.ask(
            "Puntuació de l'Equip B (Visitant)",
            default=str(partido.score_team_two) if partido.score_team_two is not None else "0"
        )

        if puntuacion_a.isdigit() and puntuacion_b.isdigit():
            partido.score_team_one = int(puntuacion_a)
            partido.score_team_two = int(puntuacion_b)

            if partido.score_team_one > partido.score_team_two:
                partido.id_team_winner = partido.id_team_one
            elif partido.score_team_two > partido.score_team_one:
                partido.id_team_winner = partido.id_team_two
            else:
                partido.id_team_winner = None

            uow.commit()
            ctx.print_success("Resultat actualitzat amb èxit.")
        else:
            ctx.print_error("Les puntuacions han de ser nombres vàlids.")
            
    Prompt.ask("Prem Enter per continuar")

def eliminar_partido(ctx: UIContext):
    ctx.print_header("Cancel·lar / Eliminar Partit")
    id_str = Prompt.ask("Introdueix l'ID del partit a eliminar")
    
    if not id_str.isdigit():
        ctx.print_error("L'ID ha de ser numèric.")
        Prompt.ask("Prem Enter per tornar")
        return

    with ctx.uow_factory() as uow:
        repo = MatchRepository(uow, Match)
        partido = repo.get(int(id_str))
        
        if not partido:
            ctx.print_error("Partit no trobat.")
            Prompt.ask("Prem Enter per tornar")
            return
            
        confirmacion = Confirm.ask(f"Segur que vols cancel·lar el partit ID {partido.id}?")
        if confirmacion:
            repo.delete(partido)
            uow.commit()
            ctx.print_success("Partit eliminat del calendari.")
            
    Prompt.ask("Prem Enter per continuar")

