# main.py
import sys
import os

# Aseguramos que Python encuentre la carpeta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# from repositories import 
from repositories import UnitOfWorkFactory
from domain.db import get_uow

# La función de ayuda ahora llama a .create()


# from domain.db import get_uow # Tu fábrica de Unit of Work (ajusta la importación exacta)
from ui.context import UIContext
from ui.cli import main_menu

if __name__ == "__main__":
    # 1. Inicializamos el contexto compartiendo la fábrica (sin ejecutarla)
    contexto = UIContext(uow_factory=get_uow)
    
    # 2. Lanzamos el menú principal
    try:
        main_menu(contexto)
    except KeyboardInterrupt:
        # Por si el usuario pulsa Ctrl+C, que no reviente la consola
        contexto.console.print("\n\n[bold red]Programa interrumpido forzosamente.[/bold red]")