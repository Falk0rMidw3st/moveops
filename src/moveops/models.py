from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class ChecklistItem:
    id: str
    category: str
    title: str
    deadline_days: Optional[int] = None
    notes: str = ""
    status: Status = Status.PENDING
    confirmation_number: Optional[str] = None
    completed_date: Optional[date] = None

    def deadline_date(self, move_date: date) -> Optional[date]:
        if self.deadline_days is None:
            return None
        return move_date + timedelta(days=self.deadline_days)

    def days_remaining(self, move_date: date, today: date) -> Optional[int]:
        deadline = self.deadline_date(move_date)
        if deadline is None:
            return None
        return (deadline - today).days


@dataclass
class MoveConfig:
    move_date: date
    from_address: str
    to_address: str
    template: str
