# Credence

> **An Admiralty-grade information layer and behavior engine for the solo trader.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![Dependencies](https://img.shields.io/badge/dependencies-none-success.svg)](#)

**Credence** (*n.*) — belief grounded in evidence, as distinct from blind faith.

Retail traders do not lack information. They lack a desk. Institutions grade every
piece of incoming information for source reliability and corroboration before it
touches a decision; solo traders ingest a timeline of ungraded headlines, analyst
notes, forum chatter and press releases — all weighted equally by whatever emotion
is currently in charge.

Credence is a small, dependency-free Python toolkit that gives the solo trader
three things institutions have and individuals don't:

| Layer | Module | What it does |
|---|---|---|
| **Information grading** | `credence.admiralty` | Scores every news item by source tier × timeliness × independent corroboration, and routes it into `ACT / WATCH / NOISE` |
| **Event watchtower** | `credence.crowsnest` | Maintains a calendar of lockup expiries, earnings and rate decisions, and raises storm warnings on a fixed horizon |
| **Rule engine** | `credence.ballast` | Close-based, target-position ladders that pre-commit your exits — decided when calm, executed mechanically |
| **Evidence log** | `credence.logbook` | Trade journal + a running *intuition vs. system* scorecard, so trust in the system is earned with data, not willpower |

---

## The scoring protocol (short version)

Adapted from the **Admiralty system** — the decades-old source-grading practice of
NATO intelligence desks — into a numeric form for market information:

```
credence = source_tier × timeliness × corroboration
```

| Dimension | Values |
|---|---|
| Source tier | Official filing / exchange / company IR = **1.0** · Major financial media = **0.7** · General media = **0.4** · UGC / forums / social = **0.2** |
| Timeliness | ≤1 day = **1.0** · ≤3 days = **0.8** · ≤7 days = **0.6** · older = **0.4** |
| Corroboration | 1 independent outlet = **0.6** · 2 = **0.85** · 3+ = **1.0** |

| Verdict | Threshold | Meaning |
|---|---|---|
| `ACT` | ≥ 0.80 | Decision-grade. May enter the decision flow. |
| `WATCH` | 0.50 – 0.79 | Logged and monitored; not decision-grade yet. |
| `NOISE` | < 0.50 | Excluded from decisions. |

Full spec, edge cases and worked examples: [docs/PROTOCOL.md](docs/PROTOCOL.md).

## Quickstart

No dependencies beyond the Python standard library (3.9+):

```bash
git clone https://github.com/dsd12356994/Credence.git
cd Credence

# grade a batch of news items
python examples/run_walkthrough.py

# run the test suite
python -m unittest discover -s tests -v
```

Programmatic use:

```python
from datetime import date
from credence.admiralty import NewsItem, SourceTier, grade

items = [
    NewsItem(
        headline="NVX announces multi-year cloud partnership (official PR)",
        source_tier=SourceTier.OFFICIAL,
        published=date(2026, 10, 14),
        independent_sources=2,
    ),
    NewsItem(
        headline="Sell-side analyst raises NVX price target by 150%",
        source_tier=SourceTier.TRUSTED_MEDIA,
        published=date(2026, 10, 14),
        independent_sources=1,
    ),
]

for g in grade(items, today=date(2026, 10, 14)):
    print(f"{g.score:.2f}  {g.verdict.name:<6}  {g.item.headline}")
# 0.85  ACT      official partnership ...
# 0.42  NOISE    analyst price target ...
```

## Why close-based ladders (`ballast`)?

Three design rules that came out of live use, not a whiteboard:

1. **Decide on closes, execute on opens.** Intraday spikes must not trigger
   actions; the decision is made after the close with complete information, and
   executed mechanically in the next session.
2. **Target positions, not order sizes.** Rules are expressed as *"reduce to N
   shares"*, so a data error about your position size cannot corrupt the plan.
   A gap through several rungs applies the most severe rung crossed.
3. **Completion over price.** A missed fill reprices the order on a schedule;
   the one unforgivable sin is not executing at all.

## What is original here — and what is not

Stated plainly, because credibility is the product:

- **Not original:** source-grading. The two-dimensional reliability/credibility
  rating is the Admiralty system used by intelligence services for decades.
  Multi-agent financial debate exists in academic and open-source form
  ([TradingAgents](https://github.com/TauricResearch/TradingAgents)); sentiment
  models exist ([FinBERT](https://github.com/ProsusAI/FinBERT) and Chinese
  variants); data aggregation exists ([AkShare](https://github.com/akfamily/akshare),
  [OpenBB](https://github.com/OpenBB-finance/OpenBB)).
- **Original:** the *assembly* — a numeric Admiralty adaptation tuned for market
  information, wired to a close-based rule engine and a behavioral scorecard,
  packaged as a dependency-free toolkit a solo trader can actually run. We found
  no turnkey open-source equivalent for that combination. If one exists, please
  open an issue and we will credit it here.

## Roadmap

- [x] v0.1 — scoring protocol, ladder engine, event calendar, logbook schemas
- [ ] v0.2 — adapters: pull graded inputs from AkShare research-report & announcement endpoints
- [ ] v0.3 — optional FinBERT (Chinese) sentiment as a fourth scoring dimension
- [ ] v0.4 — anonymized 12-week live logbook statistics (system vs. intuition scorecard)

## Disclaimer

Credence is a methodology research project and a personal toolkit. It is **not
investment advice**, not a recommendation service, and has no fiduciary
relationship with anyone. Markets can and will hurt you regardless of how well
you grade your information. See [DISCLAIMER.md](DISCLAIMER.md).

## License

[MIT](LICENSE) © 2026 dsd12356994
