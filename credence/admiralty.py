"""admiralty — information credibility scoring.

Numeric adaptation of the Admiralty system (NATO intelligence source
rating) for market information:

    credence = source_tier x timeliness x corroboration   in [0, 1]

Verdicts: ACT (>=0.80), WATCH (>=0.50), NOISE (<0.50).
See docs/PROTOCOL.md for the full specification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Iterable, List, Optional

__all__ = [
    "SourceTier",
    "NewsItem",
    "Verdict",
    "GradedItem",
    "timeliness",
    "corroboration",
    "score",
    "verdict",
    "grade",
]


class SourceTier(Enum):
    """Where the information comes from."""

    OFFICIAL = 1.0        # exchange filings, regulator, company IR
    TRUSTED_MEDIA = 0.7   # major financial media with editorial standards
    MEDIA = 0.4           # general news media
    UGC = 0.2             # forums, social media, anonymous newsletters


class Verdict(Enum):
    """What the score allows the item to do."""

    ACT = "ACT"          # decision-grade
    WATCH = "WATCH"      # logged and monitored
    NOISE = "NOISE"      # excluded from decisions


@dataclass
class NewsItem:
    """One discrete piece of market information."""

    headline: str
    source_tier: SourceTier
    published: date
    outlet: str = ""
    independent_sources: int = 1   # distinct outlets with original reporting
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GradedItem:
    """A news item with its score, components and verdict."""

    item: NewsItem
    score: float
    tier_weight: float
    timeliness_weight: float
    corroboration_weight: float
    verdict: Verdict


def timeliness(published: date, today: Optional[date] = None) -> float:
    """Information half-life: <=1d -> 1.0, <=3d -> 0.8, <=7d -> 0.6, else 0.4."""
    today = today or date.today()
    age = (today - published).days
    if age <= 1:
        return 1.0
    if age <= 3:
        return 0.8
    if age <= 7:
        return 0.6
    return 0.4


def corroboration(independent_sources: int) -> float:
    """1 source -> 0.6, 2 -> 0.85, 3+ -> 1.0. Zero or negative is treated as 1."""
    n = max(1, int(independent_sources))
    if n == 1:
        return 0.6
    if n == 2:
        return 0.85
    return 1.0


def score(item: NewsItem, today: Optional[date] = None) -> float:
    """Credence in [0, 1]: tier x timeliness x corroboration."""
    s = (
        item.source_tier.value
        * timeliness(item.published, today)
        * corroboration(item.independent_sources)
    )
    return round(min(1.0, max(0.0, s)), 4)


def verdict(score_value: float) -> Verdict:
    """Route a score into ACT / WATCH / NOISE."""
    if score_value >= 0.80:
        return Verdict.ACT
    if score_value >= 0.50:
        return Verdict.WATCH
    return Verdict.NOISE


def grade(items: Iterable[NewsItem], today: Optional[date] = None) -> List[GradedItem]:
    """Grade a batch of items, most credible first."""
    graded: List[GradedItem] = []
    for item in items:
        s = score(item, today)
        graded.append(
            GradedItem(
                item=item,
                score=s,
                tier_weight=item.source_tier.value,
                timeliness_weight=timeliness(item.published, today),
                corroboration_weight=corroboration(item.independent_sources),
                verdict=verdict(s),
            )
        )
    return sorted(graded, key=lambda g: g.score, reverse=True)
