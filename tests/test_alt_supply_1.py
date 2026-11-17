"""Ruling alternative 1 of /supply (session 7726, 17 November 2026, branch wip/alt-supply-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-supply-2026-11-17.md, line 1): leave out of
"Changes outside the five years' range" a series whose latest value is below a stated floor? On this branch a floor of 0.05
Bcf a day (site/lib/supply.ts SURPRISE_FLOOR, belowFloor, in surprises) leaves out "LNG exports, every other point of exit
together" (latest 0.004 Bcf a day, its five years' range near zero): the list holds 20 lines, not 21, led by US distillate
stocks (103.33 million bbl). Pinned with the page's own library on its committed file (site/data/supply.json, built 17
November 2026 08:45 UTC).

    python -m unittest tests.test_alt_supply_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheFloor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-supply-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_list(self):
        self.assertEqual(self.f["built"], "2026-11-17T08:45:54Z")
        self.assertEqual(self.f["length"], 20)
        self.assertEqual((self.f["first"][0]["label"], self.f["first"][0]["at"], self.f["first"][0]["last"]), ("Distillate stocks", "United States", 103.33))

    def test_the_line_left_out(self):
        self.assertEqual(self.f["left_out"], [{"label": "LNG exports", "at": "every other point of exit together, monthly", "unit": "bcf/d", "last": 0.004}])


if __name__ == "__main__":
    unittest.main()
