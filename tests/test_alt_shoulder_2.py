"""Ruling alternative 2 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 2): which measure is
the headline, the shoulder above the daily mean (cut at midnight) or the second measure to the midpoint of the evening
peak? On this branch the second measure is: the summary sentence, the first two headline numbers, the day chart's band
and the months' chart draw shoulder2_* rows (site/lib/shoulder.ts MEASURES), and the shoulder against the daily mean
stands where the second measure stood. The page does no arithmetic: it draws other rows of the same table.

Pinned with the page's own code drawn on the table (site/scripts/alt-shoulder-draw.mjs), where shoulder_hours_monthly is
on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): ERCOT, August 2026, shoulder 5 to 3 hours, MWh
66,630 to 22,526, hours needed 3.66 to 1.24; California by EIA-930, November 2025, 8 to 7 hours, hours needed 2.38 to
0.78; CAISO's own data, August 2026, hours needed 4.06 to 1.54. The fixture's months are held in
site/scripts/test-shoulder-read.mjs.

    python -m unittest tests.test_alt_shoulder_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "shoulder_hours_monthly.csv")
K = "series|shoulder_hours_monthly|{}|{}|{}-01T00:00:00Z"


def draw(path, queries):
    p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-shoulder-draw.mjs", path, json.dumps(queries)],
                       cwd=SITE, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


@unittest.skipUnless(os.path.exists(CSV), "shoulder_hours_monthly is not on this machine")
class OnTheTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = draw(CSV, [{"grid": "ercot", "month": "2026-08"}, {"grid": "caiso", "month": "2025-11"}, {"grid": "caiso-own", "month": "2026-08"}])

    def test_ercot_august_2026(self):
        s = self.d[0]["summary"]
        self.assertRegex(s, r"^In August 2026, ERCOT's evening shoulder lasted 3 hours, from 19:00 to 22:00 ;")
        self.assertIn("they would need 1.24 hours on the average day", s)
        c = self.d[0]["checks"]
        self.assertAlmostEqual(c[K.format("iso:ercot", "shoulder2_mwh_above_midpoint", "2026-08")], 22526.3387, places=3)
        self.assertAlmostEqual(c[K.format("iso:ercot", "shoulder_mwh_above_mean", "2026-08")], 66629.8817, places=3)   # main's headline, lower on the page
        self.assertIn("headline-measure=midpoint", self.d[0]["marks"])
        self.assertIn("The shoulder, against the daily mean 5 hours", self.d[0]["text"])

    def test_california_eia930_november_2025(self):
        s = self.d[1]["summary"]
        self.assertRegex(s, r"evening shoulder lasted 7 hours")
        self.assertIn("they would need 0.78 hours on the average day", s)

    def test_caiso_own_august_2026(self):
        self.assertIn("they would need 1.54 hours on the average day", self.d[2]["summary"])


if __name__ == "__main__":
    unittest.main()
