"""Session 325: the known gaps and the gap days.

Energy Research Warehouse (ERW). The rows below are test fixtures, not data values.

  1. A known_gaps.csv row keyed "<table>:gap_days" closes that table's gap days by part and day; it is never read as a
     pass for the table's own failures (iso_prices.known_gap looks the table up by its name).
  2. The three rows of the owner's default: eia930_all_storage's first BAT days and US48's, SWPP's CO2 days.

    python -m unittest tests.test_session325 -v
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import build_status as bs  # noqa: E402
import iso_prices as ip  # noqa: E402


class Rules(unittest.TestCase):
    def test_parts_and_days(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "known_gaps.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("table,reason,since,decided,part,days\n"
                        "t1,whole table,2026-10-01,x,,\n"
                        "t1:gap_days,first days,2026-10-19,x,erco;isne,2024-11-06\n"
                        "t1:gap_days,a range,2026-10-19,x,us48,2024-07-01..2026-01-31\n"
                        "t2:gap_days,every day,2026-10-19,x,swpp,all\n")
            rules = bs.known_gap_days(p)
        self.assertEqual(len(rules), 3)
        self.assertTrue(bs.known_day(rules, "t1", "erco", "2024-11-06"))
        self.assertIsNone(bs.known_day(rules, "t1", "erco", "2025-12-05"))
        self.assertIsNone(bs.known_day(rules, "t1", "miso", "2024-11-06"))
        self.assertTrue(bs.known_day(rules, "t1", "us48", "2025-03-01"))
        self.assertIsNone(bs.known_day(rules, "t1", "us48", "2026-02-01"))
        self.assertTrue(bs.known_day(rules, "t2", "SWPP", "2019-03-12"))
        self.assertIsNone(bs.known_day(rules, "t2", "ciso", "2019-03-12"))

    def test_the_real_rows(self):
        rules = bs.known_gap_days()
        self.assertTrue(bs.known_day(rules, "eia930_all_storage", "us48", "2024-07-15"))
        self.assertTrue(bs.known_day(rules, "eia930_all_storage", "miso", "2025-01-15"))
        self.assertTrue(bs.known_day(rules, "eia930_all_emissions", "swpp", "2021-03-12"))
        self.assertIsNone(bs.known_day(rules, "eia930_all_storage", "erco", "2025-12-05"))

    def test_never_a_pass_for_the_table(self):
        self.assertIsNone(ip.known_gap("eia930_all_storage"))
        self.assertIsNone(ip.known_gap("eia930_all_emissions"))


if __name__ == "__main__":
    unittest.main()
