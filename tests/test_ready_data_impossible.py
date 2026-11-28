"""wip/ready-data-impossible (session 11406, chain 770, part C): the other choice of the data pages audit of
26 November, finding 7 (docs/reviews/data-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main nine tables (impossible_hours.HELD: the three carbon intensity tables, cost_of_power_monthly and _carbon,
ba_supply_monthly, ai_power_regions, caiso_reliability_daily, event_window_daily) are built without the rule for
impossible values, held because a page open to visitors read them; no page is open now (site/lib/release.ts lists
none). On this branch HELD is empty, so each is built with the rule from its next build on the data machine. What it
moves, as session 118 measured it on the tables of 4 October (docs/methods/impossible_hours.md): 15,677 hours of
carbon_intensity_hourly; 701 days and 33 months of the daily and monthly tables; 210 rows and 391 values of
ba_supply_monthly (a balancing authority's October 2021 demand of 4,165,722,983 MWh becomes 55,904,508); 39 values of
cost_of_power_monthly; 8 of ai_power_regions; 78 rows of caiso_reliability_daily; 159 of event_window_daily. Measuring
it on today's tables is the audit's data request 2 (the hourly extract is not on this machine). The audit's test
(tests/test_audit_data_10.py on wip/audit-data-10) is carried, turned round."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
NINE = {"carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly", "cost_of_power_monthly", "cost_of_power_carbon",
        "ba_supply_monthly", "ai_power_regions", "caiso_reliability_daily", "event_window_daily"}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRuleIsAppliedToAllNine(unittest.TestCase):
    def test_none_is_held(self):
        import impossible_hours as ih
        self.assertEqual(ih.HELD, {})
        self.assertEqual(set(ih.HELD_UNTIL_RULED), NINE)
        for t in NINE:
            self.assertTrue(ih.applies(t), t)

    def test_no_page_is_open_to_visitors(self):
        rel = src("site", "lib", "release.ts")
        self.assertIsNone(re.search(r'":\s*"live"', rel))   # every page in review

    def test_the_page_and_the_note_say_it(self):
        self.assertIn("none is held for approval any longer", src("site", "app", "data", "faults", "page.tsx"))
        note = src("docs", "methods", "impossible_hours.md")
        self.assertIn("`HELD` is empty", note)
        self.assertNotIn("| **Held** |", note)


if __name__ == "__main__":
    unittest.main()
