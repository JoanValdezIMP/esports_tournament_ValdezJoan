from rich.console import Console
from typing import Callable

from repositories.unit_of_work import SqlAlchemyUnitOfWork
# iniciar el UOF
# Standaritzar els missatges d'error, èxit i capçaleres per a totes les vistes

class UIContext:
    """UI state container shared across views and menus."""

    def __init__(self, uow_factory: Callable[[], SqlAlchemyUnitOfWork]):
        """Initialize the shared console and UnitOfWork factory."""
        self.console = Console()
        self.uow_factory = uow_factory

    def print_error(self, message: str) -> None:
        """Print a standardized error message."""
        self.console.print(f"\n[bold white on red] ERROR [/bold white on red] [red]{message}[/red]\n")

    def print_success(self, message: str) -> None:
        """Print a standardized success message."""
        self.console.print(f"\n[bold white on green] ÈXIT [/bold white on green] [green]{message}[/green]\n")

    def print_header(self, title: str) -> None:
        """Print a section header."""
        self.console.rule(f"[bold cyan]{title}[/bold cyan]")