"""Session 10238, the small pages' audit, finding 11 (docs/reviews/small-pages-audit-2026-11-26.md): two sentences of
/shoulder. The panel's note for ERCOT said "EIA-930 hourly demand, solar, wind and battery output, from January 2019";
EIA's battery series for ERCO begins on 23 October 2024 (the page's own decision "texas-batteries"), and the table holds
an average day of battery output from November 2024. The fold's "Demand" line named two of the impossible-hour tests and
not the third (rule A, test 4 of docs/methods/impossible_hours.md: one third to three times the grid's median)."""
import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheFacts(unittest.TestCase):
    def test_the_battery_series_begins_in_october_2024(self):
        self.assertIn("discharge only from 23 October 2024 to 15 December 2025", src("site", "app", "shoulder", "Decisions.tsx"))

    def test_the_impossible_hour_rule_has_a_range_test(self):
        self.assertIn("between one third of and three times the median of the grid's hours", re.sub(r"\s+", " ", src("docs", "methods", "impossible_hours.md")))

    def test_the_table_holds_ercot_battery_output_from_november_2024(self):
        p = os.path.join(ROOT, "warehouse", "output", "shoulder_hours_monthly.csv")
        if not os.path.exists(p):
            self.skipTest("shoulder_hours_monthly is not on this machine")
        with open(p, encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(ln for ln in fh if not ln.startswith("#"))
                    if r["entity"] == "iso:ercot" and r["variable"] == "avg_battery_mw_h00"]
        self.assertEqual(min(r["ts_utc"][:7] for r in rows), "2024-11")


class TheWords(unittest.TestCase):
    def test_the_panel_note_dates_the_battery_output(self):
        lib = src("site", "lib", "shoulder.ts")
        self.assertNotIn("EIA-930 hourly demand, solar, wind and battery output, from January 2019.", lib)
        self.assertIn("EIA-930 hourly demand, solar and wind from January 2019, and battery output from November 2024", lib)

    def test_the_fold_names_the_range_test(self):
        self.assertIn("or outside one third to three times the grid&apos;s median hour) is a blank", src("site", "app", "shoulder", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
