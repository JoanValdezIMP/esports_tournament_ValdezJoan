from __future__ import annotations

from rich.console import Console

from client.tcp_client import TcpClient


class UIContext:
    """UI state container shared across views and menus."""

    def __init__(
        self,
        tcp_client: TcpClient,
    ):
        """Initialize shared UI services."""
        self.console = Console()
        self.tcp_client = tcp_client

    def print_error(self, message: str) -> None:
        """Print a standardized error message."""
        self.console.print(
            f"\n[bold white on red] ERROR [/bold white on red] "
            f"[red]{message}[/red]\n"
        )

    def print_success(self, message: str) -> None:
        """Print a standardized success message."""
        self.console.print(
            f"\n[bold white on green] ÈXIT [/bold white on green] "
            f"[green]{message}[/green]\n"
        )

    def print_header(self, title: str) -> None:
        """Print a section header."""
        self.console.rule(f"[bold cyan]{title}[/bold cyan]")
