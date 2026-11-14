"""Session 3935 (chain 267): request 1 of docs/state/data_requests_five_tools.md.

ERCOT's reserve prices end at 2026-10-31T04:00:00Z (30 October in Texas; ruling 2 of 6 November keeps them there), and
battery_stack.build_market stopped at the last ancillary day, so 31 October was counted neither solved nor left out:
the page's October held 30 + 0 of 31 days. Every local day of the last ancillary month is now gone through, and a day
the reserve prices do not reach is left out and counted. Held on made-up flat prices (no ERCOT figure): three local
days of energy, reserve prices to the end of the second. No network.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402


class TheLastAncillaryMonth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tz = bs.pb.TZ["ercot"]
        start = pd.Timestamp("2026-10-29").tz_localize(tz).tz_convert("UTC")
        hours = pd.date_range(start, periods=24 * 3, freq="h")
        price = pd.Series([20.0 + (i % 24) for i in range(len(hours))], index=hours)
        reserve_end = pd.Timestamp("2026-10-31").tz_localize(tz).tz_convert("UTC")
        rhours = hours[hours < reserve_end]
        reserve = {p["key"]: pd.Series(1.0, index=rhours) for p in bs.ALL_MARKETS["ercot"]["products"]}
        cls.days, cls.left = bs.build_market("ercot", {"rtm": price, "dam": price}, reserve, lambda s: None)

    def test_every_day_is_solved_or_left_out(self):
        for strat in bs.STRATEGIES:
            solved = set(self.days[(strat, bs.DURATIONS[0])])
            left = {d for d, _ in self.left[strat]}
            self.assertEqual(solved, {"2026-10-29", "2026-10-30"}, strat)
            self.assertEqual(left, {"2026-10-31"}, strat)

    def test_the_reason_is_the_reserve_prices(self):
        for strat in bs.STRATEGIES:
            self.assertTrue(all(why.startswith("ancillary") for _, why in self.left[strat]))

    def test_the_month_counts_add_up(self):
        rows = bs.monthly_rows("ercot", self.days, self.left, dict(source="x", source_url="x", retrieved_at="x"))
        frame = pd.DataFrame(rows)
        held = frame[frame["x_metric"] == "days_held"]["value"].astype(float)
        out = frame[frame["x_metric"] == "days_left_out"]["value"].astype(float)
        self.assertEqual(set(held), {2.0})
        self.assertEqual(set(out), {1.0})


if __name__ == "__main__":
    unittest.main()
