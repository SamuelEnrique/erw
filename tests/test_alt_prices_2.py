"""Ruling alternative 2 of /prices (session 7723, 17 November 2026, branch wip/alt-prices-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-prices-2026-11-17.md, line 2): a calendar month's
line under the rolling 30 days, so October 2026 can be read whole? On this branch /prices/<hub> adds a row a market for
the newest whole month, from hub_price_comparison's monthly row (site/lib/pricehub.ts monthLine): the live set keeps about
35 days of the hourly tables, so a whole month cannot come from them on the site. The rolling figures stay. On the live
set the month is October 2026 (the impact file, from the hourly tables: real time SPP North 33.56 against the rolling
26.13, +28.5 percent; day-ahead CAISO SP15 46.78 against 41.95, the same 46.78 the monthly table holds). Pinned with the
page's own library on this machine's older copy of the monthly table, where its newest month is September 2026: SPP North
real time 36.68 and day-ahead 36.21 over 720 of 720 hours; ERCOT North 40.09 and 38.44; CAISO SP15 38.31 and 40.77; SPP
South day-ahead 38.58 and no real-time month (the table holds none: line 4's matter).

    python -m unittest tests.test_alt_prices_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "hub_price_comparison.csv")), "hub_price_comparison is not on this machine")
class TheMonthLine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-prices-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_newest_whole_month(self):
        self.assertEqual(self.f["spp:SPPNORTH_HUB"], {"month": "2026-09", "rt": 36.68, "da": 36.21, "rtHours": 720, "daHours": 720, "rtDue": 720, "daDue": 720})
        self.assertEqual((self.f["ercot:HB_NORTH"]["rt"], self.f["ercot:HB_NORTH"]["da"]), (40.09, 38.44))
        self.assertEqual((self.f["caiso:TH_SP15_GEN-APND"]["rt"], self.f["caiso:TH_SP15_GEN-APND"]["da"]), (38.31, 40.77))

    def test_a_market_the_table_does_not_hold(self):
        self.assertEqual((self.f["spp:SPPSOUTH_HUB"]["rt"], self.f["spp:SPPSOUTH_HUB"]["da"]), (None, 38.58))


class ThePage(unittest.TestCase):
    def test_the_page_reads_and_draws_it(self):
        with open(os.path.join(SITE, "app", "prices", "[entity]", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("series(MONTH_TABLE, { entity })", s)
        self.assertIn("data-month-mean=", s)


if __name__ == "__main__":
    unittest.main()
