"""ballast — close-based, target-position ladder rules.

Design rules (learned in live use, not on a whiteboard):

1. Decide on closes, execute on next open. Intraday spikes never trigger.
2. Rules express *target positions* ("reduce to N"), not order sizes, so a
   wrong position count in your records cannot corrupt the plan. A close
   through several rungs applies the most severe rung crossed.
3. Completion over price. The engine returns pending orders to be executed
   in the next session; re-pricing is an execution detail, not a decision.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

__all__ = ["Rung", "Order", "Ladder"]


@dataclass(frozen=True)
class Rung:
    """One ladder step: when a *daily close* crosses `price`, reduce to `target_position`.

    `kind="close_below"` fires when close < price (risk rung).
    `kind="close_above"` fires when close > price (exit-into-strength rung).
    """

    kind: str            # "close_below" | "close_above"
    price: float
    target_position: float
    label: str = ""


@dataclass(frozen=True)
class Order:
    """A pending order produced by a triggered rung, for next-session execution."""

    decided_on: date
    side: str            # "SELL" (ladders only ever reduce; they never buy back)
    quantity: float
    reason: str
    target_position: float


@dataclass
class Ladder:
    """Stateful rule engine over one position.

    Feed it each daily close via :meth:`on_close`. When a rung triggers, the
    engine emits an order reducing the position to that rung's target and
    remembers the * deepest * target already reached, so each level fires at
    most once even after partial execution is reported back.
    """

    rungs: List[Rung] = field(default_factory=list)
    position: float = 0.0

    def __post_init__(self) -> None:
        if self.position < 0:
            raise ValueError("position must be >= 0")
        kinds = {r.kind for r in self.rungs}
        if not kinds <= {"close_below", "close_above"}:
            raise ValueError(f"unknown rung kinds: {kinds}")

    def on_close(self, day: date, close: float) -> Optional[Order]:
        """Evaluate one daily close; return an Order if a rung newly triggers."""
        fired = [
            r for r in self.rungs
            if (r.kind == "close_below" and close < r.price)
            or (r.kind == "close_above" and close > r.price)
        ]
        if not fired:
            return None
        # Most severe rung = lowest target among those crossed.
        rung = min(fired, key=lambda r: r.target_position)
        if self.position <= rung.target_position:
            return None  # already at or below this target; nothing to do
        quantity = self.position - rung.target_position
        self.position = rung.target_position
        return Order(
            decided_on=day,
            side="SELL",
            quantity=quantity,
            reason=rung.label or f"{rung.kind} {rung.price}",
            target_position=rung.target_position,
        )
