"""crowsnest — the event watchtower.

Maintains a calendar of dated, decision-relevant events (lockup expiries,
earnings, rate decisions) and raises storm warnings on a fixed horizon.

Why it exists: the two most expensive retail mistakes around dated events are
(a) not knowing the date, and (b) knowing it and hoping it away. A lockup
expiry is OFFICIAL-tier information (credence 1.0); the watchtower makes sure
it is impossible to forget.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Iterable, List, Optional

__all__ = ["EventKind", "Event", "EventCalendar", "DEFAULT_STORM_HORIZON_DAYS"]

DEFAULT_STORM_HORIZON_DAYS = 45


class EventKind(Enum):
    LOCKUP = "lockup"            # share unlock / lockup expiry
    EARNINGS = "earnings"        # results, pre-announcements
    RATE_DECISION = "rate"       # central-bank meetings
    INDEX_EVENT = "index"        # index inclusion/exclusion
    OTHER = "other"


@dataclass(frozen=True)
class Event:
    """One dated event that a position's risk depends on."""

    day: date
    kind: EventKind
    name: str
    note: str = ""

    def days_until(self, today: date) -> int:
        return (self.day - today).days


class EventCalendar:
    """A simple sorted calendar of events with horizon queries."""

    def __init__(self, events: Optional[Iterable[Event]] = None) -> None:
        self._events: List[Event] = sorted(events or [], key=lambda e: e.day)

    def add(self, day: date, kind: EventKind, name: str, note: str = "") -> Event:
        ev = Event(day=day, kind=kind, name=name, note=note)
        self._events.append(ev)
        self._events.sort(key=lambda e: e.day)
        return ev

    def next(self, today: date, n: int = 5) -> List[Event]:
        """The next `n` events strictly on or after `today`."""
        return [e for e in self._events if e.day >= today][:n]

    def storm_watch(
        self,
        today: Optional[date] = None,
        horizon_days: int = DEFAULT_STORM_HORIZON_DAYS,
    ) -> List[Event]:
        """Events within the warning horizon, most imminent first.

        The default horizon (45 trading-ish days) reflects a live observation:
        post-IPO distributions in this playbook tended to top out roughly six
        to eight weeks *before* the lockup date, not on it. Front-running is
        the norm, so the warning must lead the calendar.
        """
        today = today or date.today()
        limit = today + timedelta(days=horizon_days)
        return [e for e in self._events if today <= e.day <= limit]
