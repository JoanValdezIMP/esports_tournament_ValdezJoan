from rich.console import Console
from typing import Callable

from repositories import SqlAlchemyUnitOfWork


class UIContext:
    """
    Contenedor de estado de la interfaz.
    Se comparte con las vistas para que compartan la consola y el uow_factory
    """

    def __init__(self, uow_factory: Callable[[], SqlAlchemyUnitOfWork]):
        """
        uow_factory: función que crea y devuelve un nuevo UnitOfWork cuando se necesite.

        Callable[
            [tipos de parámetros],
            tipo de retorno
        ]
        La funcion no recibe parametros y devuelve un SqlAlchemyUOW  
        uow_factory es una función sin parámetros que devuelve un SqlAlchemyUnitOfWork
        """
        # Instanciamos la consola de Rich UNA SOLA VEZ para toda la app.
        # Esto permite mantener el mismo tema, colores y estado en todas las pantallas.
        self.console = Console()

        # Guardamos la "fábrica" de Unit of Work, NO una sesión abierta.
        # Es decir, guardamos la función get_uow, no su resultado.
        self.uow_factory = uow_factory


    # Funciones de utilidad visual 
    def print_error(self, message: str) -> None:
        """Imprime un error estandarizado."""
        self.console.print(f"\n[bold white on red] ERROR [/bold white on red] [red]{message}[/red]\n")

    def print_success(self, message: str) -> None:
        """Imprime un success  estandarizado."""
        self.console.print(f"\n[bold white on green] SUCCESS [/bold white on green] [green]{message}[/green]\n")
        
    def print_header(self, title: str) -> None:
        """Imprime una cabecera de sección."""
        self.console.rule(f"[bold cyan]{title}[/bold cyan]")
    
