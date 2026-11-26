"""Audit of the data pages, finding 7, for Samuel's ruling (session 10233, docs/reviews/data-model-audit-2026-11-26.md).
A test only, not for landing: it shows the tables the rule for impossible values is held for, and changes nothing.

warehouse/derived/impossible_hours.py holds the rule for the tables in HELD, each with the reason that a page open to
visitors reads it or the home page counts its rows. Since 8 October 2026 (session 166) no page is open to visitors
(site/lib/release.ts: every line "review"), and all nine are public tables /data lists. Applying the rule moves figures
(docs/methods/impossible_hours.md, "What the held builds would change", measured in session 118: 15,677 hours of
carbon_intensity_hourly, 701 days and 33 months of the daily and monthly tables, 210 rows and 391 values of
ba_supply_monthly, among them a balancing authority's October 2021 demand of 4,165,722,983 MWh that the rule gives as
55,904,508; 8 values of ai_power_regions; 78 rows of caiso_reliability_daily; 159 rows of event_window_daily).

The other choice, not made: HELD emptied, so the next builds apply the rule. Default: left as it is."""
import csv
import os
import re
import sys
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRuleIsHeldThoughNoPageIsLive(unittest.TestCase):
    def test_held_tables_are_listed_and_no_page_is_live(self):
        import impossible_hours
        held = sorted(impossible_hours.HELD)
        self.assertEqual(len(held), 9)
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cov = {r["table"]: r for r in csv.DictReader(f)}
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        rules = live["full"] + live["recent"]["tables"]
        loaded = lambda t: any(re.match(p, t) for p in rules)
        for t in held:
            self.assertEqual(cov[t]["license"], "public", t)
            self.assertNotIn(t, live["catalogue_hold"], t)
            self.assertFalse(loaded(t) and t in live["review_hold"], t)
        rel = src("site", "lib", "release.ts")
        block = rel[rel.index("export const RELEASE"):rel.index("};", rel.index("export const RELEASE"))]
        self.assertNotIn(': "live"', block)
        note = src("docs", "methods", "impossible_hours.md")
        self.assertIn("4,165,722,983 MWh and is 55,904,508", note)
        print(f"\nthe rule is held for {len(held)} listed public tables while no page is live: {held}")


if __name__ == "__main__":
    unittest.main()
