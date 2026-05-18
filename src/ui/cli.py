# src/ui/cli.py
import time
from .context import UIContext  # <-- Aquí importamos el archivo de arriba

def dummy_menu(ctx: UIContext, modulo: str):
    ctx.print_header(f"Módulo de {modulo}")
    ctx.console.print(f"[yellow]Info:[/yellow] El CRUD para {modulo} se implementará pronto...\n")
    input("Presiona Enter para volver al menú principal...")

def main_menu(ctx: UIContext):
    while True:
        ctx.console.clear()
        ctx.print_header("🎯 E-SPORTS TOURNAMENT - BACK OFFICE 🎯")
        
        ctx.console.print("[bold cyan]1.[/bold cyan] Gestión de Equipos (Teams)")
        ctx.console.print("[bold cyan]2.[/bold cyan] Gestión de Jugadores (Players)")
        ctx.console.print("[bold cyan]0.[/bold cyan] Salir de la aplicación\n")
        
        opcion = ctx.console.input("[bold green]Elige una opción > [/bold green]")
        
        if opcion == "1":
            dummy_menu(ctx, "Equipos")
        elif opcion == "2":
            dummy_menu(ctx, "Jugadores")
        elif opcion == "0":
            ctx.console.print("\n[bold yellow]¡Hasta luego! Saliendo de forma segura...[/bold yellow] 👋")
            break
        else:
            ctx.print_error("Opción no válida. Intenta de nuevo.")
            time.sleep(1.5)