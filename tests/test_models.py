from datetime import date

from moveops.models import ChecklistItem


def test_deadline_date():
    item = ChecklistItem(id="x", category="Test", title="Test item", deadline_days=30)
    move_date = date(2026, 8, 1)
    assert item.deadline_date(move_date) == date(2026, 8, 31)


def test_days_remaining():
    item = ChecklistItem(id="x", category="Test", title="Test item", deadline_days=30)
    move_date = date(2026, 8, 1)
    today = date(2026, 8, 10)
    assert item.days_remaining(move_date, today) == 21


def test_no_deadline_returns_none():
    item = ChecklistItem(id="x", category="Test", title="Test item")
    assert item.deadline_date(date(2026, 8, 1)) is None
    assert item.days_remaining(date(2026, 8, 1), date(2026, 8, 10)) is None
