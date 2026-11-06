"""Session 1604 (chain 165): carbon, the held rows' words, and the costs.

Held here: ERCOT's four coincident peaks are a monthly row of a cost group (four months a summer, each dated its month),
on the real rows of ercot_4cp_intervals (tests/fixtures/board_1604/), its month's move the month before in the same
summer and its year's move the same month a year before; the Texas delivery charges are a placeholder naming who would
supply them; RGGI's auctions, ISO-NE's reserves and the RIN prices are "licensed source needed" with the publisher named,
not "not held yet"; the RGGI and ISO-NE rows keep their ids. No network, no model. Nothing here sets the environment at
import.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1604")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheCosts(unittest.TestCase):
    def setUp(self):
        self.bp = builder()
        self.saved, self.absent = self.bp.ip.OUT_DIR, list(self.bp.ABSENT)
        self.bp.ip.OUT_DIR = FIX
        self.b = self.bp.Board()
        self.bp.build_costs(self.b, lambda s: None)
        self.rows = {r["id"]: r for r in self.b.rows}

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent

    def test_the_coincident_peaks_a_month_each(self):
        r = self.rows["ercot-system-cp4-load-mw"]
        t = pd.read_csv(os.path.join(FIX, "ercot_4cp_intervals.csv"), comment="#").sort_values("ts_utc")
        by = {ts[:7]: float(v) for ts, v in zip(t["ts_utc"], t["value"])}
        self.assertEqual((r["group"], r["freq"], r["unit"], r["status"]), ("costs", "M", "MW", "ok"))
        self.assertEqual((r["last"]["t"], r["last"]["v"]), ("2025-09-01", round(by["2025-09"], 4)))
        self.assertEqual((r["moves"]["m"]["t"], r["moves"]["m"]["v"]), ("2025-08-01", round(by["2025-08"], 4)))
        self.assertEqual((r["moves"]["y"]["t"], r["moves"]["y"]["v"]), ("2024-09-01", round(by["2024-09"], 4)))
        self.assertIsNone(r["range"])                    # four months a year: never nine of a year, so no one-year range
        self.assertIn("June to September", r["basis"])

    def test_the_delivery_charges_placeholder(self):
        r = self.rows["texas-delivery"]
        self.assertEqual((r["status"], r["group"]), ("licensed", "costs"))
        self.assertIn("Public Utility Commission of Texas", r["note"])

    def test_the_group(self):
        ids = [g["id"] for g in self.bp.GROUPS]
        self.assertEqual(ids[ids.index("costs") + 1], "other")


class TheHeldRowsWords(unittest.TestCase):
    def test_publisher_named_and_licensed(self):
        bp = builder()
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('b.grey("carbon", "rggi|auction", "RGGI carbon allowance, quarterly auction", "licensed", RGGI_NOTE', src)
        self.assertIn('b.grey("as", "isone|as", "ISO-NE reserves and regulation", "licensed", "ISO-NE\'s reserve and regulation prices', src)
        self.assertIn('b.grey("carbon", "rin|price", ', src)
        self.assertIn("RGGI, Inc.", bp.RGGI_NOTE)
        self.assertIn("OPIS or Argus Media", bp.RIN_NOTE)
        self.assertNotIn("The auction results are held internal while the publisher's terms are reviewed; not shown.", src)


if __name__ == "__main__":
    unittest.main()
