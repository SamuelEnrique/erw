"""Session 273: CAISO's price history before September 2024.

Energy Research Warehouse (ERW). The owner's ruling of 14 October 2026: pull CAISO's prices as far back as CAISO
publishes (OASIS keeps about 39 months: 14 July 2023 on the day), through the existing connectors, and rebuild the
battery and generator tables for CAISO on the longer history; examine the southern areas' gap with CAISO's node list.
Held here, with no request: the battery model starts CAISO at the first whole month held; the site's word for its depth;
the tables on the data machine reach back (skipped elsewhere); the two analyses make no request unless asked to pull,
and the southern one keeps under its own ceiling; the method note's new rows.
"""

import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (("warehouse", "derived"), ("warehouse", "connectors"), ("warehouse", "analysis")):
    sys.path.insert(0, os.path.join(ROOT, *p))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheModel(unittest.TestCase):
    def test_caiso_starts_at_the_first_whole_month_held(self):
        m = bs.MARKETS["caiso"]
        self.assertEqual(m["start"], "2023-08-01")
        for p in m["products"]:
            self.assertEqual(p["hours"][0][0], "2023-08-01", p["key"])
        self.assertIn('from: "August 2023" }', src("site", "lib", "batterystack.ts"))
        for g in ("nyiso", "spp"):   # the grids in review keep their own start
            self.assertEqual(bs.ALL_MARKETS[g]["start"], "2024-09-01")


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "caiso_as_prices.csv")) and not os.environ.get("GITHUB_ACTIONS"), "the tables are on the data machine")
class TheTablesOnTheDataMachine(unittest.TestCase):
    def test_the_prices_and_the_battery_reach_back(self):
        a = pd.read_csv(os.path.join(OUT, "caiso_as_prices.csv"), comment="#", usecols=["ts_utc"])
        self.assertLessEqual(a["ts_utc"].min(), "2023-07-14T07:00:00Z")
        b = pd.read_csv(os.path.join(OUT, "battery_stack_monthly.csv"), comment="#", usecols=["entity", "ts_utc"])
        self.assertEqual(b[b["entity"].str.startswith("caiso")]["ts_utc"].min(), "2023-08-01T00:00:00Z")
        s = pd.read_csv(os.path.join(OUT, "battery_stack_stress_daily.csv"), comment="#", usecols=["entity", "ts_utc"])
        self.assertEqual(s[s["entity"].str.startswith("caiso")]["ts_utc"].min(), "2023-08-15T00:00:00Z")


class TheAnalyses(unittest.TestCase):
    def test_no_request_unless_asked_and_a_ceiling(self):
        import caiso_southern_nodes as sn
        code = src("warehouse", "analysis", "caiso_southern_nodes.py")
        self.assertIn('if a.pull:', code)
        self.assertLessEqual(len(sn.NODES) * 8_784, sn.CEILING)
        self.assertEqual(set(sn.MONITOR), {"CAISO System", "LA Basin", "Big Creek/Ventura", "San Diego/Imperial Valley", "Greater Fresno"})
        years = src("warehouse", "analysis", "battery_caiso_years.py")
        self.assertNotIn("requests", years)
        self.assertIn('YEARS = ("2024", "2025")', years)

    def test_the_method_notes(self):
        note = src("docs", "methods", "battery_stack.md")
        for piece in ("14 July 2023 from session 273", "### Six more, on the history back to August 2023 (session 273)",
                      "`caiso_notices_20230815`", "| **2024** (session 273: a whole year held now)", "53, 78 and 103"):
            self.assertIn(piece, note)
        for rel in ("docs/methods/battery_stack.md", "docs/methods/generator_earns_algorithm.md", "warehouse/analysis/caiso_southern_nodes.py",
                    "warehouse/analysis/battery_caiso_years.py", "tests/test_session273.py"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
