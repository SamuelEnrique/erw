"""Ruling alternative 1 of /explore/demand-growth (session 7709, 17 November 2026, branch wip/alt-demand-growth-1; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-demand-growth-2026-11-17.md, line 1):
California's growth counts the batteries' charging; add a second row, demand less the charging? On this branch the CAISO
view adds a section with both rows for the windows CAISO's own data holds (site/lib/explore/demandgrowth.ts
chargingWindow and chargingWindows, the method note's rule; site/app/explore/demand-growth/Charging.tsx). Pinned with
the page's own library and component on replication/demand_growth/california_rows.csv (public rows copied unchanged
from eia930_demand_growth and shoulder_hours_monthly; site/scripts/alt-demand-growth-figures.mjs): June to December 2025
+2.81 percent with the charging (26,383 to 27,124 MW), -3.60 without (charging 1,690 MW); January to August 2026 +10.75
to +2.05 (charging 2,114 MW), as the impact file has them; the page's own second window is January to September 2026
(the months both tables hold), +10.23 to +1.69. No whole year is given: CAISO's own data starts in June 2025.

    python -m unittest tests.test_alt_demand_growth_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheSecondRow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/alt-demand-growth-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def rounded(self, w):
        return (round(w["base"]), round(w["eia"]), round(w["charging"]), round(w["growth"], 2), round(w["less"], 2))

    def test_the_impact_files_two_windows(self):
        self.assertEqual(self.rounded(self.f["june_december_2025"]), (26383, 27124, 1690, 2.81, -3.60))
        self.assertEqual(self.rounded(self.f["january_august_2026"]), (24282, 26893, 2114, 10.75, 2.05))

    def test_a_month_without_caisos_own_data_gives_no_figure(self):
        self.assertIsNone(self.f["may_2025"])

    def test_the_windows_the_page_draws(self):
        self.assertEqual([(w["year"], w["months"][0], w["months"][-1]) for w in self.f["page"]], [(2025, 6, 12), (2026, 1, 9)])
        self.assertEqual(self.f["drawn"], {"windows": ["June to December 2025", "January to September 2026"], "less": ["-3.60", "+1.69"], "tip": True})


if __name__ == "__main__":
    unittest.main()
