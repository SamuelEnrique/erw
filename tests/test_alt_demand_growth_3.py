"""Ruling alternative 3 of /explore/demand-growth (session 7709, 17 November 2026, branch wip/alt-demand-growth-3; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-demand-growth-2026-11-17.md, line 3): an input
for a site's own MW, as a share of the grid's growth? On this branch the page adds a section with a GET form (?site=)
and, for each grid, the growth of the whole year's average demand from 2019 to its last whole year and the site's share
of it (site/lib/explore/demandgrowth.ts siteMw, siteShare; site/app/explore/demand-growth/SiteShare.tsx). No figure that
stands moves. Pinned with the page's own library and component on the rows the page reads
(replication/demand_growth/table_rows.csv; site/scripts/alt-demand-growth-figures.mjs): ERCOT +11,920 MW (a 300 MW site
2.52 percent of it, 1,000 MW 8.39); PJM +4,903 (6.12, 20.39); SPP +3,427 (8.75, 29.18); MISO +1,633 (18.37, 61.24);
CAISO +1,089 (27.54, 91.80); the Lower 48 +32,220 (0.93, 3.10); NYISO (-485 MW) and ISO-NE (-343 MW) fell: no share.

    python -m unittest tests.test_alt_demand_growth_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheSitesShare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/alt-demand-growth-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_each_grid(self):
        want = {"ercot": (11920, 2.52, 8.39), "pjm": (4903, 6.12, 20.39), "spp": (3427, 8.75, 29.18), "miso": (1633, 18.37, 61.24), "caiso": (1089, 27.54, 91.80), "us48": (32220, 0.93, 3.10)}
        for g, (mw, a, b) in want.items():
            x = self.f["grids"][g]
            self.assertEqual((round(x["growth"]), round(x["s300"], 2), round(x["s1000"], 2)), (mw, a, b), g)

    def test_a_grid_whose_demand_fell_has_no_share(self):
        for g, mw in (("nyiso", -485), ("isone", -343)):
            x = self.f["grids"][g]
            self.assertEqual((round(x["growth"]), x["s300"]), (mw, None), g)

    def test_what_a_reader_may_type(self):
        self.assertEqual(self.f["read"], [300, 1000, None, None, None, None])

    def test_the_section(self):
        self.assertEqual(self.f["drawn"], {"ercot": "2.52", "nyiso": "demand fell: no share", "tip": True, "bad": True})


if __name__ == "__main__":
    unittest.main()
