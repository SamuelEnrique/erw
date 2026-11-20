"""Ruling alternative 3 of /cost-of-power/battery/awards (session 7705, 17 November 2026, branch wip/alt-battery-awards-3;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-awards-2026-11-17.md, line 3): put both
durations of the fleet in the decisions tip "The model's figure beside the awards", the market monitor's and the EIA's?
On this branch the tip gives the monitor's 1.85 hours (31,500 MWh over 17,000 MW, Potomac Economics, June 2026) and the
EIA's 1.55 (December 2025) and 1.65 (July 2026), 0.20 hours (11 percent) under the monitor's; no figure that stands moves.
The EIA's figures are pinned to the table they come from (storage_buildout_monthly, where it is on the machine:
warehouse/output, or the folder ERW_TABLES_DIR names); the monitor's is pinned to its own arithmetic.

    python -m unittest tests.test_alt_battery_awards_3 -v
"""

import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
DECISIONS = os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "awards", "Decisions.tsx")


def decisions():
    with open(DECISIONS, encoding="utf-8") as f:
        return f.read()


class TheTip(unittest.TestCase):
    def test_both_durations_are_in_the_tip(self):
        s = decisions()
        self.assertIn("31,500 MWh at the end of 2025, 1.85 hours", s)
        self.assertIn("1.55 hours in December 2025 and 1.65 in July 2026", s)
        self.assertIn("0.20 hours under the monitor's", s)
        self.assertEqual(round(31500 / 17000, 2), 1.85)
        self.assertEqual(round(1.85 - 1.65, 2), 0.20)


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "storage_buildout_monthly.csv")), "storage_buildout_monthly is not on this machine")
class TheTable(unittest.TestCase):
    def test_the_eia_figures_are_the_tables(self):
        got = {}
        with open(os.path.join(TABLES, "storage_buildout_monthly.csv"), encoding="utf-8") as f:
            rows = csv.reader(line for line in f if not line.startswith("#"))
            next(rows)
            for r in rows:
                if r[0] == "iso:ercot" and r[1] == "battery_operating_mwh_per_mw":
                    got[r[2][:7]] = float(r[3])
        self.assertEqual((round(got["2025-12"], 2), round(got["2026-07"], 2)), (1.55, 1.65))


if __name__ == "__main__":
    unittest.main()
