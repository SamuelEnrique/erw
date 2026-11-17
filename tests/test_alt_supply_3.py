"""Ruling alternative 3 of /supply (session 7726, 17 November 2026, branch wip/alt-supply-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-supply-2026-11-17.md, line 3): a row of each
grid's net imports for the newest month, from the Grid page's table? On this branch the burn section draws one line: each
of the seven grids' net imports, EIA's total interchange over every day it reports in the newest month, in GWh, the average
MW on hover (site/lib/supply.ts netImports, read from ba_supply_monthly). Seven figures added; none that stands moves. The
impact file read October 2026 from the daily table (CAISO 2,831 GWh, NYISO 1,377, MISO 1,217, ERCOT 66, ISO-NE -23, SPP
-344, PJM -359). Pinned with the page's own library on this machine's copy of the table (built 2 October 2026), whose
newest month is September 2026: CAISO 4,142 GWh (5,753 MW over 30 days), MISO 2,331, NYISO 1,712 (29 days), ERCOT 88 (28
days), ISO-NE -330, SPP -717, PJM -778. EIA-930's figures are public; the page's other readers of the table draw them.

    python -m unittest tests.test_alt_supply_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "ba_supply_monthly.csv")), "ba_supply_monthly is not on this machine")
class NetImports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-supply-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = {n["ba"]: n for n in json.loads(p.stdout)}

    def test_seven_grids_one_month(self):
        self.assertEqual(sorted(self.f), ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"])
        self.assertEqual({n["month"] for n in self.f.values()}, {"2026-09"})

    def test_the_figures(self):
        got = {b: round(n["gwh"]) for b, n in self.f.items()}
        self.assertEqual(got, {"CISO": 4142, "MISO": 2331, "NYIS": 1712, "ERCO": 88, "ISNE": -330, "SWPP": -717, "PJM": -778})
        self.assertEqual((round(self.f["CISO"]["mw"]), self.f["CISO"]["days"], self.f["ERCO"]["days"]), (5753, 30, 28))


class ThePage(unittest.TestCase):
    def test_the_page_reads_and_draws_it(self):
        with open(os.path.join(SITE, "app", "supply", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("netImports(netRead.data, bas)", s)
        self.assertIn('data-net-imports="1"', s)


if __name__ == "__main__":
    unittest.main()
