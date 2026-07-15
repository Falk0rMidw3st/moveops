from datetime import date
from pathlib import Path

from moveops import storage


def test_build_state_generic_has_items():
    state = storage.build_state("generic", date(2026, 8, 1), "Old St", "New St")
    assert len(state.items) > 0
    assert all(item.category for item in state.items)


def test_wisconsin_overrides_generic_deadlines():
    state = storage.build_state("wisconsin", date(2026, 8, 1), "Old St", "New St")
    by_id = {item.id: item for item in state.items}

    assert by_id["id-license"].category == "Time-sensitive"
    assert by_id["id-license"].deadline_days == 30
    assert "security-clearance" in by_id

    # generic-only items are still present, untouched
    assert by_id["banks"].category == "Financial"


def test_no_duplicate_ids_across_extends():
    state = storage.build_state("wisconsin", date(2026, 8, 1), "Old St", "New St")
    ids = [item.id for item in state.items]
    assert len(ids) == len(set(ids))


def test_save_and_load_roundtrip(tmp_path: Path):
    state = storage.build_state("generic", date(2026, 8, 1), "Old St", "New St")
    path = tmp_path / "state.json"
    storage.save_state(path, state)
    loaded = storage.load_state(path)
    assert loaded.config.from_address == "Old St"
    assert len(loaded.items) == len(state.items)
