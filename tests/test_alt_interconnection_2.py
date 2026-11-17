"""Ruling alternative 2 of /explore/interconnection (session 7710, 17 November 2026, branch wip/alt-interconnection-2; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-interconnection-2026-11-17.md, line 2): open the
page on a year with tens of positions, not CAISO's newest complete year (2023, 4 positions)? On this branch the last year
chosen as the page opens is the newest complete entry year with at least 20 positions entered
(site/lib/explore/interconnection.ts openingYear, OPENING_MIN_POSITIONS). The page opens on CAISO as before, now on 2021:
361 positions entered (105,537 MW), 2 reached operation, withdrawn share 0.71, 104 waiting, against 2023's 4 (664 MW), 0,
1.00 and 0: every headline of the opening view changes. ERCOT and SPP open on 2025 either way. Pinned with the page's own
library on the local table where it is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names).

    python -m unittest tests.test_alt_interconnection_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "iso_queue_statistics.csv")


@unittest.skipUnless(os.path.exists(CSV), "iso_queue_statistics is not on this machine")
class TheOpeningView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-interconnection-figures.mjs", CSV, "2026-10-19"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_caiso_opens_on_2021(self):
        o, m = self.f["caiso"]["opens"], self.f["caiso"]["main"]
        self.assertEqual((o["year"], o["entered"], round(o["mw"]), o["operating"], round(o["withdrawn_share"], 2), o["waiting"]), (2021, 361, 105537, 2, 0.71, 104))
        self.assertEqual((m["year"], m["entered"], round(m["mw"]), m["operating"], m["withdrawn_share"], m["waiting"]), (2023, 4, 664, 0, 1, 0))

    def test_ercot_and_spp_do_not_move(self):
        for iso, year, entered in (("ercot", 2025, 354), ("spp", 2025, 421)):
            self.assertEqual(self.f[iso]["opens"], self.f[iso]["main"])
            self.assertEqual((self.f[iso]["opens"]["year"], self.f[iso]["opens"]["entered"]), (year, entered))

    def test_the_page_uses_it(self):
        with open(os.path.join(SITE, "app", "explore", "interconnection", "page.tsx"), encoding="utf-8") as f:
            self.assertIn('choose(sp, "to", ys, String(openingYear(rows, iso, complete)', f.read())


if __name__ == "__main__":
    unittest.main()
