"""Session 1609 (chain 165): the trend line.

Held here: a row's trend line is the last 90 days of a daily series (at most 90 points), a year of a weekly one, three
years of a monthly or a quarterly one, each ending on the row's latest value, its points as the series holds them (no
day filled); the page draws it as before, with the hover of a point's date and value, under a column named for it. The
series are made in memory to set the spans: they test the rule, they are no one's prices. No network, no model.
Nothing here sets the environment at import.
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def points(sp):
    t0 = dt.date.fromisoformat(sp["t0"])
    return [t0 + dt.timedelta(days=d) for d in sp["d"]]


class TheSpans(unittest.TestCase):
    def test_daily_ninety_days(self):
        bp = builder()
        end = dt.date(2026, 10, 30)
        s = {end - dt.timedelta(days=i): float(i) for i in range(200)}
        sp = bp.stats(s, "D")["spark"]
        days = points(sp)
        self.assertEqual((len(days), days[0], days[-1]), (90, end - dt.timedelta(days=89), end))
        self.assertEqual(sp["v"][-1], 0.0)

    def test_a_fuel_with_no_weekend_has_its_trading_days_only(self):
        bp = builder()
        end = dt.date(2026, 10, 30)
        s = {end - dt.timedelta(days=i): 1.0 for i in range(200) if (end - dt.timedelta(days=i)).weekday() < 5}
        days = points(bp.stats(s, "D")["spark"])
        self.assertTrue(all(d.weekday() < 5 for d in days))
        self.assertGreater(days[0], end - dt.timedelta(days=90))
        self.assertLess(len(days), 90)

    def test_weekly_monthly_quarterly(self):
        bp = builder()
        end = dt.date(2026, 10, 26)
        w = {end - dt.timedelta(days=7 * i): 1.0 for i in range(120)}
        self.assertEqual(len(bp.stats(w, "W")["spark"]["v"]), 53)                   # the weeks of the last 365 days, the newest one included
        m = {dt.date(2026 - (i // 12), 12 - (i % 12), 1): 1.0 for i in range(80)}
        sp = bp.stats(m, "M")["spark"]
        self.assertEqual((len(sp["v"]), sp["t0"]), (36, "2024-01-01"))
        q = {dt.date(2020 + i // 4, 1 + 3 * (i % 4), 1): 1.0 for i in range(27)}
        self.assertEqual(len(bp.stats(q, "Q")["spark"]["v"]), 12)
        self.assertEqual((bp.SPARK_POINTS, bp.SPARK_DAYS), (90, {"D": 90, "W": 365, "M": 1095, "Q": 1095}))

    def test_the_column(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn(">Trend</th>", v)
        self.assertNotIn(">Last 30</th>", v)
        self.assertIn("<Spark row={row} />", v)


if __name__ == "__main__":
    unittest.main()
