"""Session 3754 (chain 211): the health summary's "Stale on main" line names the latest prices and the summary itself.

From 7 to 11 November 2026 every health summary was refused at the push guard (docs/state/main_red_2026-11-11.md) and no
line of any summary said the summary was not reaching main. The latest prices job (every 15 minutes, Supabase only) had
no line either. No network, no table: the commits and the ok rows are given.
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 11, 21, 0, tzinfo=UTC)
FRESH = [(NOW - dt.timedelta(hours=7), "Daily prices 2026-11-11: ok"), (NOW - dt.timedelta(days=3), "Energy Roundup 2026-W45")]


class TheNewLines(unittest.TestCase):
    def test_the_summary_refused_for_five_days_is_named(self):
        cs = FRESH + [(dt.datetime(2026, 11, 7, 15, 44, tzinfo=UTC), "Health summary 2026-11-06 (warehouse/health.py)")]
        st = health.stale_on_main(now=NOW, commits=cs, oks={"hourly network": NOW, "latest prices": NOW})
        self.assertEqual([s[0] for s in st], ["health summary"])
        self.assertEqual(health.stale_line(st), "**Stale on main:** health summary, 4.2 days (its last commit on main, 'Health summary ...', "
                                                 "2026-11-07 15:44 UTC; allowed 1 day).")

    def test_latest_prices_past_an_hour_is_named_in_hours(self):
        cs = FRESH + [(NOW - dt.timedelta(hours=6), "Health summary 2026-11-10 (warehouse/health.py)")]
        st = health.stale_on_main(now=NOW, commits=cs, oks={"hourly network": NOW, "latest prices": NOW - dt.timedelta(minutes=90)})
        self.assertEqual(health.stale_line(st), "**Stale on main:** latest prices, 1.5 hours (its last ok step in erw_health, "
                                                 "2026-11-11 19:30 UTC; allowed 1 hour).")

    def test_within_their_limits_nothing_is_named(self):
        cs = FRESH + [(NOW - dt.timedelta(hours=6), "Health summary 2026-11-10 (warehouse/health.py)")]
        st = health.stale_on_main(now=NOW, commits=cs, oks={"hourly network": NOW, "latest prices": NOW - dt.timedelta(minutes=40)})
        self.assertEqual(st, [])
        self.assertIn("the latest prices' within 1 hour, the health summary's commit within 1 day", health.stale_line(st))


if __name__ == "__main__":
    unittest.main()
