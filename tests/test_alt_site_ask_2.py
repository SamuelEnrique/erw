"""Ruling alternative 2 of Ask, the chat (session 7707, 17 November 2026, branch wip/alt-site-ask-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-ask-2026-11-17.md, line 2): should Ask ERCOT
read a spread across two grids (CAISO's SP15 less ERCOT's hub average)? On main it points to the price board. On this
branch hub_price_comparison is one of its tables, filtered to ercot:HB_HUBAVG and caiso:TH_SP15_GEN-APND, with a guide card
and one exception to rule 3 (warehouse/chat/ercot.py, and site/lib/chat/spec_ercot.json written to match it). A figure is
added where none was given: October 2026, day-ahead, SP15 46.78 less ERCOT's hub average 36.73 = +10.05 USD/MWh (the live
set as the impact file read it). Pinned with the site's compare tool in Ask ERCOT's scope on rows a stand-in answers
(site/scripts/alt-site-ask-figures.mjs), and with the local monthly table where it is on the machine (its newest month,
September 2026: SP15 40.77, ERCOT 38.80, +1.97).

    python -m unittest tests.test_alt_site_ask_2 -v
"""

import csv
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))


class AskErcotReadsTheSpread(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/alt-site-ask-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_compare_in_ask_ercots_scope(self):
        f = self.f
        self.assertEqual((f["inScope"], f["a"], f["b"], f["difference"], f["isError"], f["ruleThree"]), (True, 36.73, 46.78, 10.05, False, True))

    def test_no_other_hub_of_the_table_is_read(self):
        self.assertEqual(self.f["pjm"], {"isError": False, "value": None})

    def test_the_site_spec_is_the_profile_as_it_stands(self):
        import ercot
        with open(os.path.join(SITE, "lib", "chat", "spec_ercot.json"), encoding="utf-8") as fh:
            spec = json.load(fh)
        self.assertEqual(spec["tables"], ercot.SCOPE["tables"])
        self.assertEqual(spec["filters"], ercot.SCOPE["filters"])
        self.assertEqual(spec["holds"], ercot.HOLDS)
        self.assertTrue(spec["system"].startswith(ercot.RULES))
        self.assertIn(dict(ercot.CARDS)["hub_price_comparison"], spec["system"])


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "hub_price_comparison.csv")), "hub_price_comparison is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    def test_the_newest_month_held_here(self):
        got = {}
        with open(os.path.join(TABLES, "hub_price_comparison.csv"), encoding="utf-8") as fh:
            for r in csv.reader(line for line in fh if not line.startswith("#")):
                if r[1] == "dam_avg_price" and r[5] == "P1M" and r[2].startswith("2026-09") and r[0] in ("caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG"):
                    got[r[0]] = float(r[3])
        self.assertEqual((got["caiso:TH_SP15_GEN-APND"], got["ercot:HB_HUBAVG"], round(got["caiso:TH_SP15_GEN-APND"] - got["ercot:HB_HUBAVG"], 2)), (40.77, 38.8, 1.97))


if __name__ == "__main__":
    unittest.main()
