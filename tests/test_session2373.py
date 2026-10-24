"""Session 2373: Ghana's Energy Commission, the National Energy Statistical Bulletin 2026: generation by source, imports and
exports, peak load, a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/energycom_ghana.py's row reader on rows built here in the form
pdfplumber gives the bulletin's tables (made up for the test, not the Commission's): cells shifted on alternate lines, the
year first, a dash read as no value, the shares not taken; a value that does not read, a year given twice and too few
values stopping the run; the sector rule and the live-set hold (internal). No network, no PDF.

    python -m unittest tests.test_session2373 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import energycom_ghana as G  # noqa: E402
import build_coverage as B  # noqa: E402

NAMES = ["generation_hydro", "generation_thermal", "generation_other_renewables", "generation_total"]


class Rows(unittest.TestCase):
    def test_rows(self):
        t = [["Year", None, "Generation (GWh)"], ["2000", None, None, "6,610", None, "614", None, "-", None, "7,224", "92"],
             ["", "2001", "", "", "6,609", "", "1,250", "", "-", "", "7,859", "84"], ["2025", None, "8,752", "18,996", "197", "27,945", "31"]]
        got = G.table_values(t, NAMES, "generation")
        self.assertEqual(got[2000], [6610.0, 614.0, None, 7224.0])
        self.assertEqual(got[2001], [6609.0, 1250.0, None, 7859.0])
        self.assertEqual(got[2025], [8752.0, 18996.0, 197.0, 27945.0])

    def test_stops(self):
        for t in ([["2000", "6,610", "6l4", "-", "7,224"]], [["2000", "1", "1", "-", "2"], ["2000", "1", "1", "-", "2"]], [["2000", "1", "1"]], [["Year"]]):
            with self.assertRaises(RuntimeError):
                G.table_values(t, NAMES, "generation")


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(G.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
