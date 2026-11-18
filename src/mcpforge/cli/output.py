"""Rich-based terminal output helpers."""

from collections.abc import Iterable

from rich.console import Console
from rich.table import Table

console = Console()


def print_success(message: str) -> None:
    """Print a successful operation message."""

    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""

    console.print(f"[red]Error:[/red] {message}")


def print_key_values(values: Iterable[tuple[str, str]]) -> None:
    """Render key-value data as a compact table."""

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for key, value in values:
        table.add_row(key, value)
    console.print(table)
