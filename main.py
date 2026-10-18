import os
import sys


def main() -> None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

    from client.tcp_client import TcpClient
    from ui.cli import main_menu
    from ui.context import UIContext

    tcp_client = TcpClient(
        host=os.getenv("SERVER_HOST", "127.0.0.1"),
        port=int(os.getenv("SERVER_PORT", "5000")),
    )
    context = UIContext(tcp_client=tcp_client)

    try:
        main_menu(context)
    except KeyboardInterrupt:
        context.console.print(
            "\n\n[bold red]Programa interromput.[/bold red]"
        )


if __name__ == "__main__":
    main()
