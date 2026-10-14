"""Credence — an Admiralty-grade information layer and behavior engine
for the solo trader.

Layers:
    admiralty  information credibility scoring (source x timeliness x corroboration)
    crowsnest  event watchtower (lockups, earnings, rate decisions)
    ballast    close-based target-position ladder rules
    logbook    trade journal and the intuition-vs-system scorecard
"""

__version__ = "0.1.0"

from .admiralty import NewsItem, SourceTier, Verdict, grade, score, verdict
from .ballast import Ladder, Order, Rung
from .crowsnest import Event, EventCalendar, EventKind
from .logbook import journal_row, tally_intuition

__all__ = [
    "NewsItem", "SourceTier", "Verdict", "grade", "score", "verdict",
    "Ladder", "Order", "Rung",
    "Event", "EventCalendar", "EventKind",
    "journal_row", "tally_intuition",
    "__version__",
]
