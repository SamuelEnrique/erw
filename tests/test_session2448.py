"""Session 2448: Rwanda's electricity a quarter from RURA's Electricity Statistics Reports.

Energy Research Warehouse (ERW). Tests warehouse/connectors/rura_rwanda.py's readers on values built here in the
reports' form (made up for the test, not RURA's figures): a quarter's label, a number in kWh with or without decimals
written as MWh, a dash or blank read as no value; a label or value that does not read stopping the run; the sector rule
and the live-set hold (internal). No network, no PDF.

    python -m unittest tests.test_session2448 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import rura_rwanda as R  # noqa: E402
import build_coverage as B  # noqa: E402


class Readers(unittest.TestCase):
    def test_quarter(self):
        self.assertEqual(R.quarter("Q1 2023", "t"), "2023-01-01T00:00:00Z")
        self.assertEqual(R.quarter(" Q4 2021 ", "t"), "2021-10-01T00:00:00Z")
        for bad in ("Q5 2023", "2023 Q1", "Q1 23"):
            with self.assertRaises(RuntimeError):
                R.quarter(bad, "t")

    def test_num(self):
        self.assertEqual(R.num("36,537,200", "t"), 36537.2)
        self.assertEqual(R.num("0.0", "t"), 0.0)
        self.assertIsNone(R.num("-", "t"))
        self.assertIsNone(R.num("", "t"))
        for bad in ("36.537.200", "12a", "1,23"):
            with self.assertRaises(RuntimeError):
                R.num(bad, "t")

    def test_slug(self):
        self.assertEqual(R.slug("So Energy Mukungwa 1"), "so_energy_mukungwa_1")
        self.assertEqual(R.slug("Rukarara V-Mushishito"), "rukarara_v_mushishito")


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(R.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {R.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
