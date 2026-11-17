"""Ruling alternative 1 of /cost-of-power/battery/awards (session 7705, 17 November 2026, branch wip/alt-battery-awards-1;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-awards-2026-11-17.md, line 1): add a
second column for a 4-hour battery beside the 2-hour, day-ahead model? On this branch "By month", "By year" and the gap in
three parts carry the 4-hour model's figures beside the 2-hour's (site/lib/storageawards.ts MODEL_PREFIX_4H, monthsOf and
gapOf with a prefix; the page reads the dayahead_4h rows of battery_stack_monthly). Pinned with the page's own library on
the public tables (site/scripts/alt-battery-awards-figures.mjs), where they are on the machine (warehouse/output, or the
folder ERW_TABLES_DIR names): July 2026 USD 2.87 to 4.45 per kW (+54.7 percent); January 2026 11.33 to 14.83; 2026's
whole months 30.14 to 42.60 (+41.3 percent) against awards of 6.53; the gap 23.61 to 36.07, never offered 9.70 to 13.72,
offered and not awarded 14.53 to 23.14.

    python -m unittest tests.test_alt_battery_awards_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NEED = ("ercot_storage_dam_awards_monthly", "battery_stack_monthly", "ercot_storage_dam_offers_monthly")


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the public tables are not on this machine")
class TheFourHourColumn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-awards-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def kw(self, v):
        return round(v / 1000, 2)

    def test_by_month(self):
        self.assertEqual([self.kw(v) for v in self.f["july"]], [2.87, 4.45])
        self.assertEqual([self.kw(v) for v in self.f["january"]], [11.33, 14.83])

    def test_by_year(self):
        y = self.f["year2026"]
        self.assertEqual(len(y["months"]), 7)
        self.assertEqual((self.kw(y["awards"]), self.kw(y["model2"]), self.kw(y["model4"])), (6.53, 30.14, 42.60))

    def test_the_gap_in_three_parts(self):
        g2, g4 = self.f["gap2"], self.f["gap4"]
        self.assertEqual(g2["months"], g4["months"])
        self.assertEqual([round(g2[k], 2) for k in ("gap", "never", "unawarded", "price")], [23.61, 9.70, 14.53, -0.62])
        self.assertEqual([round(g4[k], 2) for k in ("gap", "never", "unawarded", "price")], [36.07, 13.72, 23.14, -0.78])

    def test_the_offers_section_draws_the_columns(self):
        self.assertEqual(self.f["drawn"], {"cells4h": 4, "sentence": True})


if __name__ == "__main__":
    unittest.main()
