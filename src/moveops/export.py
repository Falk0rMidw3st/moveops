from __future__ import annotations

from datetime import date

from .storage import State


def render_markdown(state: State) -> str:
    lines = [
        f"# Move Checklist: {state.config.from_address} -> {state.config.to_address}",
        "",
        f"Move date: {state.config.move_date.isoformat()}",
        "",
    ]

    categories: dict[str, list] = {}
    for item in state.items:
        categories.setdefault(item.category, []).append(item)

    today = date.today()
    for category, items in categories.items():
        lines.append(f"## {category}")
        for item in items:
            box = "x" if item.status.value == "done" else " "
            days = item.days_remaining(state.config.move_date, today)
            suffix = f" (due in {days} days)" if days is not None and item.status.value != "done" else ""
            conf = f" — conf# {item.confirmation_number}" if item.confirmation_number else ""
            lines.append(f"- [{box}] {item.title}{suffix}{conf}")
        lines.append("")

    done = sum(1 for i in state.items if i.status.value == "done")
    lines.append(f"---\n{done}/{len(state.items)} complete")
    return "\n".join(lines)
