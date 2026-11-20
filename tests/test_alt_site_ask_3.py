"""Ruling alternative 3 of Ask, the chat (session 7707, 17 November 2026, branch wip/alt-site-ask-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-ask-2026-11-17.md, line 3): two tables
give October's SP15 average differently (the hourly iso_dam_hub_prices keeps a moving window: 471 hours, USD 41.94 on 17
November; hub_price_comparison holds the whole month: 744 hours, USD 46.78); pick one? On this branch a mean of the
hourly table over one whole calendar month, at one hub, with no grouping, is answered from the whole-month table and says
so (site/lib/chat/tools.ts monthAsked and query): the answer moves from 41.94 to 46.78 (+11.55 percent). A mean over part
of a month is answered from the hourly table as on main. Pinned with the site's own query tool on rows read by a
stand-in for the database (site/scripts/alt-site-ask-figures.mjs; the monthly row's value is the live set's figure, the
hourly rows are made up), and on the local monthly table where it is on the machine (its newest month, September 2026:
USD 40.77).

    python -m unittest tests.test_alt_site_ask_3 -v
"""

import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


class TheMonthsAverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/alt-site-ask-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_a_whole_month_is_read_from_the_monthly_table(self):
        self.assertEqual(self.f["whole"], {"value": 46.78, "read_from": "hub_price_comparison", "isError": False, "asked": ["hub_price_comparison"]})

    def test_part_of_a_month_is_read_from_the_hourly_table(self):
        self.assertEqual(self.f["part"], {"value": 42, "read_from": None, "isError": False, "asked": ["iso_dam_hub_prices"]})

    def test_which_requests_are_a_whole_month(self):
        self.assertEqual(self.f["monthAsked"], [{"start": "2026-10-01", "end": "2026-11-01"}, {"start": "2026-12-01", "end": "2027-01-01"}, None, None])

    def test_the_change_on_the_live_set(self):
        self.assertEqual(round((46.78 - 41.94) / 41.94 * 100, 2), 11.54)   # the impact file prints +11.55 from the unrounded means


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "hub_price_comparison.csv")), "hub_price_comparison is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    def test_the_newest_month_the_local_table_holds(self):
        got = {}
        with open(os.path.join(TABLES, "hub_price_comparison.csv"), encoding="utf-8") as f:
            for r in csv.reader(line for line in f if not line.startswith("#")):
                if r[0] == "caiso:TH_SP15_GEN-APND" and r[1] == "dam_avg_price" and r[5] == "P1M":
                    got[r[2][:7]] = float(r[3])
        self.assertEqual((max(got), got[max(got)]), ("2026-09", 40.77))


if __name__ == "__main__":
    unittest.main()
