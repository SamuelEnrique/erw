"""Session 2450: Azerbaijan's electricity balance, production and plant capacity, a year (the State Statistical Committee).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statsaz_azerbaijan.py's readers on values built here in the
Committee's form (made up for the test, not its figures): a dash and "..." read as no value, a year written as a float
or a string, a line's slug; a value or year that does not read stopping the run; the sector rule, the live-set hold and
the release hold (public). No network, no workbook file.

    python -m unittest tests.test_session2450 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statsaz_azerbaijan as A  # noqa: E402
import build_coverage as B  # noqa: E402


class Readers(unittest.TestCase):
    def test_val(self):
        self.assertEqual(A.val(21847.2, "t"), 21847.2)
        self.assertEqual(A.val(-785.7, "t"), -785.7)
        for blank in ("-", "...", "", " - "):
            self.assertIsNone(A.val(blank, "t"))
        with self.assertRaises(RuntimeError):
            A.val("21,847", "t")

    def test_year(self):
        self.assertEqual(A.year(2007.0, "t"), 2007)
        self.assertEqual(A.year("2025.0", "t"), 2025)
        for bad in ("Years", 1850.0, "x"):
            with self.assertRaises(RuntimeError):
                A.year(bad, "t")

    def test_slug(self):
        self.assertEqual(A.slug("Electricity plants (EP)"), "electricity_plants_ep")
        self.assertEqual(A.slug("Commerce and pub. services"), "commerce_and_public_services")
        self.assertEqual(A.slug("Losses in transmission networks"), "losses_in_transmission_networks")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{A.NAME}"', f.read())


if __name__ == "__main__":
    unittest.main()
