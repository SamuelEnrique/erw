"""Ruling alternative 26 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-26; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 26): a third column,
B less A? On this branch the A and B table has it (site/app/impact/Forecast.tsx). Pinned with the page's own view drawn to
HTML (site/scripts/alt-impact-diff.mjs), Lone Mountain with the local option on (A) and off (B): first-year property B less
A USD 1.07 million; over the life 16.55 million; taxes, present value 8.94 million; the jobs rows 0. 13 cells are added.

    python -m unittest tests.test_alt_impact_26 -v
"""

import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, SITE  # noqa: E402

QUERY = "tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&btech=geothermal&bstate=nv&bmw=36&bcost=4956.83&bstart=2026&biaval=0&bown=1.0917&bownyears=60"


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class BLessA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-impact-diff.mjs", JEDI_CSV, QUERY], cwd=SITE, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_column(self):
        self.assertTrue(self.f["head"])
        self.assertEqual(len(self.f["diffs"]), 13)

    def test_lone_mountain_option_off_less_on(self):
        d = self.f["diffs"]
        self.assertEqual((M(d["prop1"]["raw"]), M(d["propl"]["raw"]), M(d["pvtax"]["raw"])), (1.07, 16.55, 8.94))
        self.assertEqual((d["cjobs"]["raw"], d["ojobs"]["raw"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
