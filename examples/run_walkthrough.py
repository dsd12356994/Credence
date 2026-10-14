#!/usr/bin/env python3
"""End-to-end walkthrough of all four Credence layers.

Runs on the standard library only:
    python examples/run_walkthrough.py
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from credence.admiralty import NewsItem, SourceTier, grade
from credence.ballast import Ladder, Rung
from credence.crowsnest import EventCalendar, EventKind
from credence.logbook import INTUITION_FIELDS, tally_intuition, write_csv

TODAY = date(2026, 10, 14)
HERE = Path(__file__).parent


def demo_information_grading() -> None:
    print("=" * 72)
    print("1. ADMIRALTY — information credibility grading")
    print("=" * 72)
    raw = json.loads((HERE / "sample_news.json").read_text(encoding="utf-8"))
    items = [
        NewsItem(
            headline=r["headline"],
            source_tier=SourceTier[r["source_tier"]],
            published=date.fromisoformat(r["published"]),
            outlet=r.get("outlet", ""),
            independent_sources=r.get("independent_sources", 1),
        )
        for r in raw
    ]
    for g in grade(items, today=TODAY):
        components = (
            f"{g.tier_weight:.1f} x {g.timeliness_weight:.1f} x "
            f"{g.corroboration_weight:.2f}"
        )
        print(f"{g.score:>5.2f}  {g.verdict.name:<6} [{components}]  {g.item.headline[:58]}")
    print()


def demo_ballast() -> None:
    print("=" * 72)
    print("2. BALLAST — close-based ladder (decide on closes, execute on opens)")
    print("=" * 72)
    ladder = Ladder(
        rungs=[
            Rung("close_below", 47.0, 800, label="R2a: close<47 -> reduce to 800"),
            Rung("close_below", 44.0, 400, label="R2b: close<44 -> reduce to 400"),
            Rung("close_above", 56.0, 600, label="R1: close>56 -> exit into strength"),
        ],
        position=1400,
    )
    closes = [
        (date(2026, 10, 10), 47.30),   # intraday spiked below 47, close held: no action
        (date(2026, 10, 13), 45.56),   # first close below 47 -> SELL 600 (1400 -> 800)
        (date(2026, 10, 14), 46.10),   # still below 47 but already at target: no action
        (date(2026, 11, 5), 57.20),    # rally into strength -> SELL 200 (800 -> 600)
    ]
    for day, close in closes:
        order = ladder.on_close(day, close)
        if order:
            print(f"{day}  close={close:<6} -> {order.side} {order.quantity:.0f} "
                  f"(to {order.target_position:.0f})  [{order.reason}]")
        else:
            print(f"{day}  close={close:<6} -> no action")
    print()


def demo_crowsnest() -> None:
    print("=" * 72)
    print("3. CROWSNEST — event watchtower (45-day storm horizon)")
    print("=" * 72)
    cal = EventCalendar()
    cal.add(date(2026, 11, 20), EventKind.LOCKUP, "pre-IPO investor unlock (XYZ-like)")
    cal.add(date(2026, 12, 9), EventKind.LOCKUP, "IPO 6-month lockup (SPCX-like)")
    cal.add(date(2026, 12, 30), EventKind.LOCKUP, "controlling-shareholder unlock (NVX-like)")
    cal.add(date(2026, 11, 4), EventKind.EARNINGS, "Q3 results")
    for ev in cal.storm_watch(today=TODAY):
        print(f"in {ev.days_until(TODAY):>3} days  [{ev.kind.value:<6}] {ev.name}")
    print("        (the December unlock storm is outside the 45-day horizon —")
    print("         the watchtower will pick it up around mid-November,")
    print("         weeks before the date, because front-running is the norm)")
    print()


def demo_logbook() -> None:
    print("=" * 72)
    print("4. LOGBOOK — intuition vs. system scorecard")
    print("=" * 72)
    sample_csv = (
        "date,event,system_said,gut_said,followed,outcome\n"
        "2026-10-14,sell 600,SELL at open,wait for bounce,system,system\n"
        "2026-10-14,post-sale bounce,buy back 600,system,system,gut\n"
        "2026-10-13,intraday spike,sell now (early rule execution),no action,gut,system\n"
    )
    print(tally_intuition(sample_csv).summary())
    print()
    print("(write your own rows with logbook.intuition_row + logbook.write_csv)")


if __name__ == "__main__":
    print(f"Credence walkthrough — {TODAY}\n")
    demo_information_grading()
    demo_ballast()
    demo_crowsnest()
    demo_logbook()
