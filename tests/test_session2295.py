"""Session 2295: the Central Electricity Authority's power supply position, India, a fiscal year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cea_india_psp.py on report lines built here in CEA's form
(figures made up for the test, not CEA's): the fiscal year's block read in MWh, a name printed over two lines joined, a
place marked # kept outside its region's sum, "Others" named by their region, a region's gap named; the regions not
summing to All India stopping the run; the sector rule and the hold. No network.

    python -m unittest tests.test_session2295 -v
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import cea_india_psp as C  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = ["Energy Power Supply Position Report", "March,2025 / April,2024 to March,2025"]


def run(lines):
    class Page:
        def extract_text(self):
            return "\n".join(lines)

    class Pdf:
        pages = [Page()]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    gaps = {}
    with mock.patch.object(C.pdfplumber, "open", lambda f: Pdf()):
        return C.parse(b"", "2024-25", {}, gaps), gaps


class Parse(unittest.TestCase):
    def test_rows(self):
        rows, gaps = run(HEAD + ["x / Delhi 1 1 0 0.0 1,000 990 10 1.0",
                                 "x / y /", "2 2 0 0.0 2,000 2,000 0 0.0", "UT of J&K and Ladakh",
                                 "Others 1 1 0 0.0 100 100 0 0.0",
                                 "x / Lakshadweep # 1 1 0 0.0 56 56 0 0.0",
                                 "x / Northern Region (##) 4 4 0 0.0 3,100 3,090 10 0.3",
                                 "x / Western Region 4 4 0 0.0 5,000 5,000 0 0.0",
                                 "x / All India 8 8 0 0.0 8,100 8,090 10 0.1"])
        got = {(r["entity"], r["variable"]): r for r in rows}
        d = got[("cea_psp:delhi", "energy_supplied")]
        self.assertEqual((d["value"], d["unit"], d["ts_utc"], d["x_region"], d["x_kind"]), (990000.0, "MWh", "2024-04-01T00:00:00Z", "Northern Region", "state"))
        self.assertIn(("cea_psp:ut_of_j_k_and_ladakh", "energy_requirement"), got)
        self.assertIn(("cea_psp:others_northern_region", "energy_supplied"), got)
        self.assertEqual(got[("cea_psp:lakshadweep", "energy_supplied")]["x_kind"], "state_outside_region_total")
        self.assertEqual(got[("cea_psp:all_india", "energy_not_supplied")]["value"], 10000.0)
        self.assertEqual(gaps, {"2024-25 Western Region": 5000})  # no states listed above it in this fixture

    def test_gap_and_stop(self):
        _, gaps = run(HEAD + ["x / Delhi 1 1 0 0.0 1,000 1,000 0 0.0", "x / Northern Region (##) 1 1 0 0.0 1,500 1,500 0 0.0",
                              "x / All India 1 1 0 0.0 1,500 1,500 0 0.0"])
        self.assertEqual(gaps, {"2024-25 Northern Region": 500})
        with self.assertRaises(RuntimeError) as c:
            run(HEAD + ["x / Delhi 1 1 0 0.0 1,000 1,000 0 0.0", "x / Northern Region 1 1 0 0.0 1,000 1,000 0 0.0",
                        "x / All India 1 1 0 0.0 2,000 2,000 0 0.0"])
        self.assertIn("the regions sum", str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(C.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
