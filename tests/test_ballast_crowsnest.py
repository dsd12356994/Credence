"""Tests for credence.ballast (ladder engine) and credence.crowsnest (watchtower)."""
import unittest
from datetime import date, timedelta

from credence.ballast import Ladder, Rung
from credence.crowsnest import Event, EventCalendar, EventKind


def make_ladder() -> Ladder:
    """The reference ladder used in live trading: 1400 -> 800 -> 400, plus an
    exit-into-strength rung at 56 -> 600."""
    return Ladder(
        rungs=[
            Rung("close_below", 47.0, 800, label="R2a: reduce to 800"),
            Rung("close_below", 44.0, 400, label="R2b: reduce to 400"),
            Rung("close_above", 56.0, 600, label="R1: exit into strength"),
        ],
        position=1400,
    )


class TestBallast(unittest.TestCase):
    def test_close_based_not_intraday(self):
        ladder = make_ladder()
        # Intraday wick below 47 never reaches on_close — only closes matter.
        self.assertIsNone(ladder.on_close(date(2026, 10, 12), 47.30))

    def test_first_rung_fires_on_close(self):
        ladder = make_ladder()
        order = ladder.on_close(date(2026, 10, 13), 45.56)   # close < 47, > 44
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, 600)
        self.assertEqual(order.target_position, 800)
        self.assertEqual(order.side, "SELL")

    def test_gap_through_two_rungs_applies_deepest(self):
        ladder = make_ladder()
        order = ladder.on_close(date(2026, 10, 14), 43.60)   # closes below both 47 and 44
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, 1000)               # 1400 -> 400 directly
        self.assertEqual(order.target_position, 400)

    def test_each_level_fires_at_most_once(self):
        ladder = make_ladder()
        first = ladder.on_close(date(2026, 10, 13), 45.56)
        self.assertIsNotNone(first)
        # Still below 47 but already at 800: nothing further.
        self.assertIsNone(ladder.on_close(date(2026, 10, 14), 45.00))

    def test_exit_into_strength(self):
        ladder = make_ladder()
        ladder.on_close(date(2026, 10, 13), 45.56)           # reduce to 800
        order = ladder.on_close(date(2026, 11, 5), 57.20)    # close > 56
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, 200)                # 800 -> 600
        self.assertEqual(order.target_position, 600)

    def test_ladders_never_buy_back(self):
        ladder = Ladder(rungs=[Rung("close_below", 10.0, 100)], position=100)
        self.assertIsNone(ladder.on_close(date(2026, 1, 1), 12.0))


class TestCrowsnest(unittest.TestCase):
    def test_storm_watch_leads_the_calendar(self):
        cal = EventCalendar()
        today = date(2026, 10, 14)
        cal.add(date(2026, 12, 30), EventKind.LOCKUP, "controlling-shareholder unlock")
        cal.add(date(2027, 3, 1), EventKind.EARNINGS, "FY26 results")
        storms = cal.storm_watch(today=today, horizon_days=45)
        self.assertEqual(len(storms), 0)   # 12-30 is 77 days out: not yet in horizon
        soon = cal.storm_watch(today=today, horizon_days=80)
        self.assertEqual([e.kind for e in soon], [EventKind.LOCKUP])

    def test_next_skips_past_events(self):
        cal = EventCalendar()
        cal.add(date(2026, 10, 1), EventKind.RATE_DECISION, "FOMC")
        cal.add(date(2026, 10, 28), EventKind.EARNINGS, "Q3")
        nxt = cal.next(date(2026, 10, 14), n=5)
        self.assertEqual([e.name for e in nxt], ["Q3"])


if __name__ == "__main__":
    unittest.main()
