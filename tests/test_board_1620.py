"""Session 1620 (chain 165): the second read's faults, fixed.

Held here: every row states its time base and step, a fuel's or a rate's from its step when the builder gives it no
interval of its own; ERCOT's adder row has its day's extremes, on its real hours (tests/fixtures/board_1601/); the
page's extremes cell on a row that is not daily says its step, not "not held yet". No network, no model. Nothing here
sets the environment at import.
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1601")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheSecondRead(unittest.TestCase):
    def test_a_row_with_no_interval_of_its_own_states_its_step(self):
        bp = builder()
        b = bp.Board()
        b.add("rates", "x|d", "A yield", "percent", "D", {dt.date(2026, 10, 1): 4.0})
        b.add("retailpower", "x|m", "A price", "USD/MWh", "M", {dt.date(2026, 8, 1): 120.0})
        b.add("power", "x|own", "A hub", "USD/MWh", "D", {dt.date(2026, 10, 1): 30.0}, extra=dict(basis="its own"))
        rows = {r["id"]: r for r in b.rows}
        self.assertEqual(rows["x-d"]["basis"], bp.STEP_BASIS["D"])
        self.assertEqual(rows["x-m"]["basis"], bp.STEP_BASIS["M"])
        self.assertEqual(rows["x-own"]["basis"], "its own")
        self.assertTrue(all(not any(ch in s for ch in "0123456789") for s in bp.STEP_BASIS.values()))

    def test_the_adder_has_its_day_extremes(self):
        bp = builder()
        saved, absent = bp.ip.OUT_DIR, list(bp.ABSENT)
        bp.ip.OUT_DIR = FIX
        try:
            b = bp.Board()
            bp.build_adders(b, bp.pb.nerc_holidays(range(2025, 2028)), lambda s: None)
        finally:
            bp.ip.OUT_DIR, bp.ABSENT[:] = saved, absent
        r = next(r for r in b.rows if r["id"] == "ercot-system-rtrdpa")
        self.assertEqual(r["ext"]["t"], r["last"]["t"])
        self.assertEqual((r["ext"]["tz"], r["ext"]["hours"]), ("America/Chicago", 24))
        self.assertGreaterEqual(r["ext"]["hi"]["v"], r["ext"]["lo"]["v"])

    def test_the_page_says_a_monthly_rows_step(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn("if (!e && row.freq !== \"D\") return", v)


if __name__ == "__main__":
    unittest.main()
