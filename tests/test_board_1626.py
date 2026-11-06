"""Session 1626 (chain 167): the ERCOT 4CP exposure.

Held here, on ERCOT's 28 published coincident-peak intervals and the hub average's real 15-minute real-time prices in
them (tests/fixtures/board_1626/, cut from the old laptop's tables): a monthly row of the cost group, each summer month
the price in its interval, dated the month as the load row beside it is; every interval of the fixture priced; a table
not on the machine is skipped. No network, no model. Nothing here sets the environment at import.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1626")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheExposure(unittest.TestCase):
    def setUp(self):
        self.bp = builder()
        self.saved, self.absent = self.bp.ip.OUT_DIR, list(self.bp.ABSENT)
        self.bp.ip.OUT_DIR = FIX

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent

    def test_the_price_in_each_interval(self):
        b = self.bp.Board()
        self.bp.build_costs(b, lambda s: None)
        rows = {r["id"]: r for r in b.rows}
        r = rows["ercot-hb-hubavg-cp4-rt"]
        cp = pd.read_csv(os.path.join(FIX, "ercot_4cp_intervals.csv"), comment="#")
        px = pd.read_csv(os.path.join(FIX, "ercot_all_hub_prices_history.csv"), comment="#").set_index("ts_utc")["value"]
        newest = cp["ts_utc"].max()
        self.assertEqual((r["group"], r["freq"], r["unit"], r["status"]), ("costs", "M", "USD/MWh", "ok"))
        self.assertEqual((r["last"]["t"], r["last"]["v"]), (newest[:7] + "-01", round(float(px[newest]), 4)))
        self.assertEqual(r["moves"]["y"]["t"], "2024-09-01")
        self.assertEqual(rows["ercot-system-cp4-load-mw"]["last"]["t"], r["last"]["t"])
        self.assertIn("coincident peak", r["basis"])

    def test_every_interval_priced_and_a_table_not_here_skipped(self):
        said = []
        b = self.bp.Board()
        self.bp.cp4_price(b, said.append)
        self.assertEqual(said, ["  ERCOT's 4CP exposure: 28 of 28 intervals priced"])
        self.assertIn("iso_rtm_hub_prices", self.bp.ABSENT)                 # the rolling table is not in the fixture: skipped


if __name__ == "__main__":
    unittest.main()
