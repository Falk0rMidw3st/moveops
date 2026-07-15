from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from . import storage
from .models import Status

console = Console()

DEFAULT_STATE_FILE = Path("moveops_state.json")


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@click.group()
@click.option(
    "--state-file",
    type=click.Path(path_type=Path),
    default=DEFAULT_STATE_FILE,
    show_default=True,
    help="Path to the JSON state file.",
)
@click.pass_context
def main(ctx: click.Context, state_file: Path) -> None:
    """MoveOps: track the address-change cascade after a move."""
    ctx.ensure_object(dict)
    ctx.obj["state_file"] = state_file


@main.command()
@click.option("--template", default="generic", show_default=True, help="Template name (generic, wisconsin).")
@click.option("--move-date", "move_date_str", required=True, help="Move date, YYYY-MM-DD.")
@click.option("--from", "from_address", required=True, help="Old address.")
@click.option("--to", "to_address", required=True, help="New address.")
@click.pass_context
def init(ctx: click.Context, template: str, move_date_str: str, from_address: str, to_address: str) -> None:
    """Seed a new checklist from a template."""
    state_file: Path = ctx.obj["state_file"]
    if state_file.exists():
        raise click.ClickException(
            f"{state_file} already exists. Delete it or pass --state-file to start fresh."
        )
    move_date = _parse_date(move_date_str)
    state = storage.build_state(template, move_date, from_address, to_address)
    storage.save_state(state_file, state)
    console.print(f"[green]Initialized[/] {len(state.items)} items from '{template}' template -> {state_file}")


@main.command(name="list")
@click.option("--category", default=None, help="Filter by category.")
@click.option(
    "--status",
    "status_filter",
    type=click.Choice([s.value for s in Status]),
    default=None,
    help="Filter by status.",
)
@click.pass_context
def list_items(ctx: click.Context, category: Optional[str], status_filter: Optional[str]) -> None:
    """List checklist items."""
    state = storage.load_state(ctx.obj["state_file"])
    items = state.items
    if category:
        items = [i for i in items if i.category.lower() == category.lower()]
    if status_filter:
        items = [i for i in items if i.status.value == status_filter]

    table = Table(title="MoveOps Checklist")
    table.add_column("ID")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Days left")

    today = date.today()
    for item in items:
        days = item.days_remaining(state.config.move_date, today)
        table.add_row(item.id, item.category, item.title, item.status.value, "-" if days is None else str(days))
    console.print(table)


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show a deadline-sorted summary of what's still pending."""
    state = storage.load_state(ctx.obj["state_file"])
    today = date.today()

    pending = [i for i in state.items if i.status != Status.DONE]

    def sort_key(item):
        days = item.days_remaining(state.config.move_date, today)
        return (days is None, days if days is not None else 0)

    pending.sort(key=sort_key)

    table = Table(title=f"MoveOps Status — {state.config.from_address} -> {state.config.to_address}")
    table.add_column("Days left")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Notes")

    for item in pending:
        days = item.days_remaining(state.config.move_date, today)
        if days is None:
            days_str = "-"
        elif days < 0:
            days_str = f"[bold red]{days} (OVERDUE)[/]"
        elif days <= 7:
            days_str = f"[yellow]{days}[/]"
        else:
            days_str = str(days)
        table.add_row(days_str, item.category, item.title, item.notes)

    console.print(table)
    done_count = len(state.items) - len(pending)
    console.print(f"\n{done_count}/{len(state.items)} complete")


@main.command()
@click.argument("item_id")
@click.option("--confirmation", default=None, help="Confirmation number.")
@click.option("--date", "date_str", default=None, help="Completion date, YYYY-MM-DD (default: today).")
@click.pass_context
def complete(ctx: click.Context, item_id: str, confirmation: Optional[str], date_str: Optional[str]) -> None:
    """Mark an item complete."""
    state_file: Path = ctx.obj["state_file"]
    state = storage.load_state(state_file)
    item = next((i for i in state.items if i.id == item_id), None)
    if item is None:
        raise click.ClickException(f"No item with id '{item_id}'.")
    item.status = Status.DONE
    item.confirmation_number = confirmation
    item.completed_date = _parse_date(date_str) if date_str else date.today()
    storage.save_state(state_file, state)
    console.print(f"[green]Marked complete:[/] {item.title}")


@main.command()
@click.option("--output", type=click.Path(path_type=Path), default=None, help="Output file (default: stdout).")
@click.pass_context
def export(ctx: click.Context, output: Optional[Path]) -> None:
    """Export a printable one-pager (Markdown)."""
    from .export import render_markdown

    state = storage.load_state(ctx.obj["state_file"])
    doc = render_markdown(state)
    if output:
        output.write_text(doc, encoding="utf-8")
        console.print(f"[green]Exported[/] -> {output}")
    else:
        console.print(doc)


if __name__ == "__main__":
    main()
