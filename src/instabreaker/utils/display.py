from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class Display:
    def __init__(self):
        self.console = Console()

    def banner(self):
        self.console.print(Panel.fit(
            "[bold cyan]InstaBreaker 2026[/bold cyan]\n[italic]Modern Instagram Tool[/italic]",
            border_style="blue"
        ))

    def log(self, message: str):
        self.console.print(f"[blue][*][/blue] {message}")

    def success(self, message: str):
        self.console.print(f"[green][+][/green] {message}")

    def error(self, message: str):
        self.console.print(f"[red][!][/red] {message}")

    def warning(self, message: str):
        self.console.print(f"[yellow][?][/yellow] {message}")

    def show_table(self, title: str, columns: list[str], rows: list[list[str]]):
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

display = Display()
