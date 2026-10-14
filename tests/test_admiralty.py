"""Tests for credence.admiralty (scoring protocol) — stdlib unittest only."""
import unittest
from datetime import date, timedelta

from credence.admiralty import (
    NewsItem, SourceTier, Verdict, corroboration, grade, score, timeliness, verdict,
)

TODAY = date(2026, 10, 14)


class TestComponents(unittest.TestCase):
    def test_timeliness_buckets(self):
        self.assertEqual(timeliness(TODAY, TODAY), 1.0)
        self.assertEqual(timeliness(TODAY - timedelta(days=1), TODAY), 1.0)
        self.assertEqual(timeliness(TODAY - timedelta(days=3), TODAY), 0.8)
        self.assertEqual(timeliness(TODAY - timedelta(days=7), TODAY), 0.6)
        self.assertEqual(timeliness(TODAY - timedelta(days=30), TODAY), 0.4)

    def test_corroboration(self):
        self.assertEqual(corroboration(1), 0.6)
        self.assertEqual(corroboration(2), 0.85)
        self.assertEqual(corroboration(5), 1.0)
        self.assertEqual(corroboration(0), 0.6)   # degenerate input treated as 1


class TestScoring(unittest.TestCase):
    def test_official_same_day_two_sources_is_act(self):
        item = NewsItem("official partnership", SourceTier.OFFICIAL, TODAY,
                        independent_sources=2)
        self.assertAlmostEqual(score(item, TODAY), 0.85)
        self.assertEqual(verdict(score(item, TODAY)), Verdict.ACT)

    def test_lockup_filing_three_days_three_sources_hits_act_boundary(self):
        item = NewsItem("lockup registration", SourceTier.OFFICIAL,
                        TODAY - timedelta(days=3), independent_sources=3)
        self.assertAlmostEqual(score(item, TODAY), 0.80)
        self.assertEqual(verdict(score(item, TODAY)), Verdict.ACT)

    def test_single_analyst_note_is_noise(self):
        item = NewsItem("analyst raises target 150%", SourceTier.TRUSTED_MEDIA,
                        TODAY, independent_sources=1)
        self.assertAlmostEqual(score(item, TODAY), 0.42)
        self.assertEqual(verdict(score(item, TODAY)), Verdict.NOISE)

    def test_two_wires_same_day_is_watch(self):
        item = NewsItem("regulator inquiry reported", SourceTier.TRUSTED_MEDIA,
                        TODAY, independent_sources=2)
        self.assertAlmostEqual(score(item, TODAY), 0.595)
        self.assertEqual(verdict(score(item, TODAY)), Verdict.WATCH)

    def test_stale_forum_rumor_is_deep_noise(self):
        item = NewsItem("acquisition rumor", SourceTier.UGC,
                        TODAY - timedelta(days=5), independent_sources=1)
        self.assertAlmostEqual(score(item, TODAY), 0.072)

    def test_grade_sorts_descending(self):
        items = [
            NewsItem("rumor", SourceTier.UGC, TODAY),
            NewsItem("official", SourceTier.OFFICIAL, TODAY, independent_sources=3),
            NewsItem("media", SourceTier.MEDIA, TODAY - timedelta(days=2),
                     independent_sources=2),
        ]
        scores = [g.score for g in grade(items, today=TODAY)]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
