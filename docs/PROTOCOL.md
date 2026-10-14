# The Credence Information-Grading Protocol

**Version 0.1** · Status: live in personal use · Lineage: [Admiralty system](https://en.wikipedia.org/wiki/Admiralty_code) (NATO intelligence source rating), adapted for market information.

## 1. Purpose

Every piece of market information that reaches a trading decision must carry an
explicit, reproducible credibility score. The protocol exists to answer one
question before any other: **how much does this deserve to influence what I do?**

## 2. The score

```
credence = source_tier × timeliness × corroboration        ∈ [0, 1]
```

### 2.1 Source tier

| Tier | Weight | Includes |
|---|---|---|
| `OFFICIAL` | 1.0 | Exchange filings, regulator publications, company IR / press releases, official lockup registrations |
| `TRUSTED_MEDIA` | 0.7 | Major financial media with editorial standards (newswires, established financial press) |
| `MEDIA` | 0.4 | General news media without a financial desk |
| `UGC` | 0.2 | Forums, social media, anonymous newsletters, aggregator blogs |

A `MEDIA` item that merely reprints an `OFFICIAL` source is not corroboration —
see §2.3; the tier should be inherited from the underlying source.

### 2.2 Timeliness (information half-life)

| Age | Weight |
|---|---|
| ≤ 1 day | 1.0 |
| ≤ 3 days | 0.8 |
| ≤ 7 days | 0.6 |
| older | 0.4 |

Markets re-price fast. Old information is not worthless, but it is usually
already in the price; its role is context, not action.

### 2.3 Corroboration (independence counting)

| Independent sources | Weight |
|---|---|
| 1 | 0.6 |
| 2 | 0.85 |
| 3 or more | 1.0 |

**Independence rules:**

- Outlets are independent if they have distinct original reporting. Two outlets
  running the same wire story = **one** source.
- An official confirmation subsumes media reports of the same fact; re-score the
  item as `OFFICIAL` with corroboration counted from distinct outlets that
  reported it *before* confirmation.
- An analyst price target citing public information is one source, and its tier
  is the analyst's, not the underlying company's.

### 2.4 Verdicts

| Verdict | Range | Meaning |
|---|---|---|
| `ACT` | ≥ 0.80 | Decision-grade. May enter the decision flow. |
| `WATCH` | 0.50 – 0.79 | Logged, monitored, re-scored as it ages or gains corroboration. |
| `NOISE` | < 0.50 | Excluded from decisions. Recorded only for audit. |

## 3. Worked examples

| # | Item | Tier × Time × Corrob. | Score | Verdict |
|---|---|---|---|---|
| 1 | Company officially announces a major cloud partnership; 2 independent outlets reported it same-day | 1.0 × 1.0 × 0.85 | **0.85** | `ACT` |
| 2 | Exchange filing registers insider shares for December lockup release; 3 outlets covered | 1.0 × 0.8 × 1.0 | **0.80** | `ACT` |
| 3 | Two newswires report a regulator inquiry has been opened (no official statement yet) | 0.7 × 1.0 × 0.85 | **0.60** | `WATCH` |
| 4 | Single sell-side note raises a price target 150% | 0.7 × 1.0 × 0.6 | **0.42** | `NOISE` |
| 5 | Forum thread claims an acquisition is imminent | 0.2 × 0.6 × 0.6 | **0.07** | `NOISE` |

Note the pattern the protocol encodes: **official action outranks narrative,
corroboration outranges volume, and freshness outranks repetition.**

## 4. Design boundaries

- The protocol grades *information*, not *theorems*. An `ACT`-grade item is
  decision-grade input — it is not a prediction, and acting on it still requires
  position sizing and risk rules (see the `ballast` module).
- Thresholds (0.80 / 0.50) are defaults from live personal use, not fitted
  parameters. Tune them if your verdict audit shows systematic misrouting.
- The protocol deliberately has **no sentiment dimension** in v0.1. Whether an
  `ACT`-grade item is bullish or bearish is a separate judgment; conflating
  credibility with direction is how narratives hijack process.

## 5. Audit

Every graded item should be stored with its components (tier, age, source count,
score, verdict). Re-grading history with different weights must always be
possible — a protocol whose past cannot be recomputed is not a protocol.
