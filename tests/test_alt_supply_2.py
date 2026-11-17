"""Ruling alternative 2 of /supply (session 7726, 17 November 2026, branch wip/alt-supply-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-supply-2026-11-17.md, line 2): two grids side by
side (A and B, such as PJM against MISO), their burn rows over the weeks both hold? On this branch /supply takes ?a= and
?b= and draws, under the burn table, each fuel both grids hold over their common weeks (site/lib/supply.ts burnPair). The
table on main sets PJM's week of 13 November (gas 6.23 Bcf a day, coal 177.1 thousand short tons a day) against MISO's of
6 November (4.99; 202.2). Pinned with the page's own library on its committed file (site/data/supply.json, 17 November
2026 08:45 UTC): over the 50 weeks both hold, the newest common week 30 October, gas PJM 6.08 against MISO 4.92 (+1.16),
coal 154.8 against 217.4 (-62.6); means over the common weeks gas 7.41 and 5.09, coal 227.8 and 272.7. The burn rows are
EIA-930's, which the page draws on main; no hold is lifted.

    python -m unittest tests.test_alt_supply_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class PjmAgainstMiso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-supply-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)
        cls.p = {x["fuel"]: x for x in cls.f["pair"]}

    def test_main_sets_different_weeks(self):
        m = self.f["main"]
        self.assertEqual((m["pjm_gas"]["t"], m["miso_gas"]["t"]), ("2026-11-13", "2026-11-06"))

    def test_gas(self):
        g = self.p["natural-gas"]
        self.assertEqual((g["weeks"], g["week"], round(g["a"], 2), round(g["b"], 2), round(g["meanA"], 2), round(g["meanB"], 2)), (50, "2026-10-30", 6.08, 4.92, 7.41, 5.09))

    def test_coal(self):
        c = self.p["coal"]
        self.assertEqual((c["weeks"], c["week"], round(c["a"], 1), round(c["b"], 1), round(c["meanA"], 1), round(c["meanB"], 1)), (50, "2026-10-30", 154.8, 217.4, 227.8, 272.7))


if __name__ == "__main__":
    unittest.main()
