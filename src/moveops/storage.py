from __future__ import annotations

import importlib.resources
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .models import ChecklistItem, MoveConfig, Status

TEMPLATES_PACKAGE = "moveops.templates"


@dataclass
class State:
    config: MoveConfig
    items: list[ChecklistItem] = field(default_factory=list)


def _load_template_dict(name: str) -> dict[str, Any]:
    resource = importlib.resources.files(TEMPLATES_PACKAGE) / f"{name}.yaml"
    if not resource.is_file():
        raise FileNotFoundError(f"Unknown template '{name}'.")
    data = yaml.safe_load(resource.read_text(encoding="utf-8"))

    items_by_id = {item["id"]: item for item in data.get("items", [])}
    parent = data.get("extends")
    if parent:
        parent_items = _load_template_dict(parent)["items"]
        merged = {item["id"]: item for item in parent_items}
        merged.update(items_by_id)
        items_by_id = merged

    return {"name": data.get("name", name), "items": list(items_by_id.values())}


def build_state(template: str, move_date: date, from_address: str, to_address: str) -> State:
    data = _load_template_dict(template)
    items = [
        ChecklistItem(
            id=raw["id"],
            category=raw["category"],
            title=raw["title"],
            deadline_days=raw.get("deadline_days"),
            notes=raw.get("notes", ""),
        )
        for raw in data["items"]
    ]
    config = MoveConfig(move_date=move_date, from_address=from_address, to_address=to_address, template=template)
    return State(config=config, items=items)


def save_state(path: Path, state: State) -> None:
    payload = {
        "config": {
            "move_date": state.config.move_date.isoformat(),
            "from_address": state.config.from_address,
            "to_address": state.config.to_address,
            "template": state.config.template,
        },
        "items": [
            {
                **asdict(item),
                "status": item.status.value,
                "completed_date": item.completed_date.isoformat() if item.completed_date else None,
            }
            for item in state.items
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_state(path: Path) -> State:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run 'moveops init' first.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    config = MoveConfig(
        move_date=date.fromisoformat(payload["config"]["move_date"]),
        from_address=payload["config"]["from_address"],
        to_address=payload["config"]["to_address"],
        template=payload["config"]["template"],
    )
    items = [
        ChecklistItem(
            id=raw["id"],
            category=raw["category"],
            title=raw["title"],
            deadline_days=raw.get("deadline_days"),
            notes=raw.get("notes", ""),
            status=Status(raw.get("status", "pending")),
            confirmation_number=raw.get("confirmation_number"),
            completed_date=date.fromisoformat(raw["completed_date"]) if raw.get("completed_date") else None,
        )
        for raw in payload["items"]
    ]
    return State(config=config, items=items)
