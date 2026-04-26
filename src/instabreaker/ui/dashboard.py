from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.console import Console
from datetime import datetime

class Dashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.start_time = datetime.now()
        self.stats = {
            "cpm": 0,
            "success": 0,
            "failed": 0,
            "proxies_active": 0,
            "current_password": "",
            "elapsed": "00:00:00"
        }
        self.logs = []
        
        self.setup_layout()

    def setup_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="logs", ratio=2)
        )

    def update_stats(self, **kwargs):
        self.stats.update(kwargs)
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.stats["elapsed"] = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def add_log(self, message: str):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if len(self.logs) > 15:
            self.logs.pop(0)

    def generate_stats_panel(self) -> Panel:
        table = Table.grid(expand=True)
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white", justify="left")
        
        table.add_row("CPM: ", f"{self.stats['cpm']}")
        table.add_row("Success: ", f"[green]{self.stats['success']}[/green]")
        table.add_row("Failed: ", f"[red]{self.stats['failed']}[/red]")
        table.add_row("Proxies: ", f"{self.stats['proxies_active']}")
        table.add_row("Elapsed: ", f"{self.stats['elapsed']}")
        table.add_row("Testing: ", f"[yellow]{self.stats['current_password']}[/yellow]")
        
        return Panel(table, title="[bold]Statistics[/bold]", border_style="blue")

    def generate_logs_panel(self) -> Panel:
        return Panel("\n".join(self.logs), title="[bold]Real-time Logs[/bold]", border_style="green")

    def generate_header(self) -> Panel:
        return Panel("[bold magenta]InstaBreaker 2026 Ultra Edition[/bold magenta]", border_style="magenta")

    def render(self) -> Layout:
        self.layout["header"].update(self.generate_header())
        self.layout["stats"].update(self.generate_stats_panel())
        self.layout["logs"].update(self.generate_logs_panel())
        self.layout["footer"].update(Panel(f"Target: [bold]{self.stats.get('target', 'None')}[/bold]", border_style="cyan"))
        return self.layout
