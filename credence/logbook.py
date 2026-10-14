"""logbook — evidence log and the intuition-vs-system scorecard.

Two CSV schemas:

1. Trade journal: every fill gets one row, including an emotion rating
   (1 = calm, 5 = about to smash something) and whether the trade followed
   a rule. The emotion column is the point: it correlates your P&L with
   your state of mind over months, which no broker statement will do.

2. Intuition log: every time your gut disagrees with the system, both
   opinions are recorded, plus which one you followed and the eventual
   outcome. Trust in a system is earned with a scorecard, not with slogans.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = [
    "JOURNAL_FIELDS",
    "INTUITION_FIELDS",
    "journal_row",
    "intuition_row",
    "write_csv",
    "tally_intuition",
]

JOURNAL_FIELDS = [
    "date", "ticker", "action", "quantity", "price",
    "reason", "emotion_1to5", "rule_followed", "note",
]

INTUITION_FIELDS = [
    "date", "event", "system_said", "gut_said", "followed", "outcome",
]


def journal_row(
    date: str,
    ticker: str,
    action: str,
    quantity: str,
    price: str,
    reason: str,
    emotion_1to5: int,
    rule_followed: bool,
    note: str = "",
) -> Dict[str, str]:
    if not 1 <= int(emotion_1to5) <= 5:
        raise ValueError("emotion_1to5 must be an integer in [1, 5]")
    return {
        "date": date, "ticker": ticker, "action": action,
        "quantity": quantity, "price": price, "reason": reason,
        "emotion_1to5": str(emotion_1to5),
        "rule_followed": "yes" if rule_followed else "NO",
        "note": note,
    }


def intuition_row(
    date: str, event: str, system_said: str, gut_said: str,
    followed: str, outcome: str,
) -> Dict[str, str]:
    if followed not in {"system", "gut"}:
        raise ValueError("followed must be 'system' or 'gut'")
    return {"date": date, "event": event, "system_said": system_said,
            "gut_said": gut_said, "followed": followed, "outcome": outcome}


def write_csv(path: str, rows: List[Dict[str, str]], fields: List[str]) -> None:
    """Append rows to a CSV, writing the header only if the file is new."""
    import os

    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            w.writeheader()
        w.writerows(rows)


@dataclass
class Scorecard:
    conflicts: int = 0
    followed_system: int = 0
    followed_gut: int = 0
    system_right: int = 0
    gut_right: int = 0
    ties: int = 0

    @property
    def system_win_rate(self) -> Optional[float]:
        decided = self.system_right + self.gut_right + self.ties
        return self.system_right / decided if decided else None

    def summary(self) -> str:
        wr = "n/a" if self.system_win_rate is None else f"{self.system_win_rate:.0%}"
        return (
            f"conflicts={self.conflicts}  followed system={self.followed_system} "
            f"/ gut={self.followed_gut}  | when they disagreed and it mattered: "
            f"system right {self.system_right}, gut right {self.gut_right}, "
            f"tie {self.ties}  -> system win rate {wr}"
        )


def tally_intuition(csv_text: str) -> Scorecard:
    """Tally an intuition log (CSV text) into a scorecard.

    `outcome` convention: "system", "gut", or "tie" — who turned out right.
    """
    card = Scorecard()
    for row in csv.DictReader(io.StringIO(csv_text)):
        card.conflicts += 1
        if row["followed"] == "system":
            card.followed_system += 1
        else:
            card.followed_gut += 1
        outcome = (row.get("outcome") or "").strip().lower()
        if outcome == "system":
            card.system_right += 1
        elif outcome == "gut":
            card.gut_right += 1
        else:
            card.ties += 1
    return card
