"""Session 323: EIA's annual generation by balancing authority, and EIA-930's hourly sums against it.

Energy Research Warehouse (ERW). No network; the frames below are test fixtures, not data values.

  1. EIA-923's plant rows are summed by their balancing authority code; a blank code is "none", EIA's state-fuel
     increment has a name of its own.
  2. The header row of an EIA-923 sheet is found by its "Plant Id".
  3. The wiring: the live set, coverage's rules, the method note and the Grid pack's answer.

    python -m unittest tests.test_session323 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia923_annual_ba as e  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Sums(unittest.TestCase):
    def test_by_code(self):
        df = pd.DataFrame({"Plant Id": [1, 1, 2, 3, 99999],
                           "Balancing Authority Code": ["ERCO", "ERCO", "", "MISO", "State-Fuel Level Increment"],
                           "Net Generation (Megawatthours)": [10.0, 5.0, 7.0, "", 2.5]})
        got = {(b, v): (val, n) for b, y, v, val, n in e.sums(df, 2025, "net_generation_mwh")}
        self.assertEqual(got[("ERCO", "net_generation_mwh")], (15.0, 1))
        self.assertEqual(got[("none", "net_generation_mwh")], (7.0, 1))
        self.assertEqual(got[("MISO", "net_generation_mwh")], (0.0, 1))
        self.assertEqual(got[("state_fuel_increment", "net_generation_mwh")], (2.5, 1))

    def test_header_row(self):
        raw = pd.DataFrame([["U.S. Department of Energy"], [None], ["Plant Id"], [1]])
        self.assertEqual(e.header_row(raw), 2)


class Wiring(unittest.TestCase):
    def test_registered(self):
        ls = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("'^eia_annual_generation_ba$'", ls)
        self.assertIn("'^eia_annual_crosscheck_ba$'", ls)
        cov = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn('(r"^eia_annual_(generation|crosscheck)_ba$", "power")', cov)
        self.assertIn('("derived", r"^eia_annual_crosscheck_ba$")', cov)

    def test_the_answer(self):
        self.assertIn("Question 5, answered in session 323", src("docs", "reviews", "packs", "grid.md"))
        note = src("docs", "methods", "eia_annual_crosscheck.md")
        self.assertIn("https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip", note)
        self.assertIn("These reasons are hypotheses, not EIA's statements.", note)


if __name__ == "__main__":
    unittest.main()
