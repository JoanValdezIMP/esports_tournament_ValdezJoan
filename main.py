# main.py
import sys
import os

# Assegurem que Python trobi la carpeta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# IMPORTANTE: Importa 'Base' i 'engine' des d'on vas definir la teva DB
from domain.db import get_uow, Base, engine 
from ui.context import UIContext
from ui.cli import main_menu

if __name__ == "__main__":
    Base.metadata.create_all(engine)

    # Inicialitzem el context
    contexto = UIContext(uow_factory=get_uow)
    
    # Llancem el menú principal

    try:
        main_menu(contexto)
    except KeyboardInterrupt:
        contexto.console.print("\n\n[bold red]Programa interromput.[/bold red]")