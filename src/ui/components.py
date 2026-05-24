# src/ui/components.py
from rich.table import Table
from rich.panel import Panel

def create_standard_table(title: str, columns: list[str], header_style: str = "bold magenta") -> Table:
    """Create a consistent table layout."""
    table = Table(title=f"\n[bold]{title}[/bold]", show_header=True, header_style=header_style)

    for col in columns:
        if col.upper() == "ID":
            table.add_column(col, justify="right", style="dim", width=6)
        elif "ID" in col.upper():
            table.add_column(col, justify="center", style="cyan")
        else:
            table.add_column(col)

    return table

def welcome_panel() -> Panel:
    cool_title = (r"""
                                                       __               __                                                           __    
          ____             ____________   ____________/  |_  ______   _/  |_  ____  __ _________  ____ _____    _____   ____   _____/  |_  
        _/ __ \   ______  /  ___/\____ \ /  _ \_  __ \   __\/  ___/   \   __\/  _ \|  |  \_  __ \/    \\__  \  /     \_/ __ \ /    \   __\ 
        \  ___/  /_____/  \___ \ |  |_> >  <_> )  | \/|  |  \___ \     |  | (  <_> )  |  /|  | \/   |  \/ __ \|  Y Y  \  ___/|   |  \  |   
         \___  >         /____  >|   __/ \____/|__|   |__| /____  >    |__|  \____/|____/ |__|  |___|  (____  /__|_|  /\___  >___|  /__|   
             \/               \/ |__|                           \/                                   \/     \/      \/     \/     \/       
        """)


    """Create the main menu welcome panel."""
    texto = (
        f"{cool_title}\n"
        "Benvingut al tauler d'administració.\n"
        "Usa els números per navegar i [bold red]0 per sortir[/bold red]."
    )
    return Panel(texto, title="[bold cyan]SISTEMA ACTIU[/bold cyan]", border_style="green", expand=False)


