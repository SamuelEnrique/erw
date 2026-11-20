"""Audit of "What a generator earns", finding 5 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): the
generator page's battery (warehouse/derived/merchant_revenue.py, battery_day: hourly, full power or nothing, with a last
partial step) is called "an upper bound" (its decision 3). On the same prices the battery page's program with no reserve
paid (battery_stack.solve_day, any power from 0 to 1, the same round trip, empty start and one cycle) earns more, so the
figure is below a bound its own page's sister computes.

1. One day where half power pays: four hours priced 10, 30, 30, 50 and the rest 20: solve_day beats battery_day.
2. Every day of the battery page's public file, last twelve months (ERCOT HB_HUBAVG real time, the generator page's own
   price), 4 hours: battery_day 58.72 per kW, solve_day 59.95 (session 9841), the full-power program below on most days.
It passes on main: it shows the fault. Nothing is written."""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402
import merchant_revenue as mr  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
SPEC = ((True, 0.5),)


def any_power(prices, hours):
    return bs.solve_day(prices, [[0.0] * len(prices)], SPEC, hours)["total"]


class GeneratorBatteryIsNotABound(unittest.TestCase):
    def test_a_day_where_part_power_pays(self):
        prices = [20.0] * 24
        prices[1:5] = [10.0, 30.0, 30.0, 50.0]
        self.assertGreater(any_power(prices, 2), mr.battery_day(prices, 2)[0] + 1.0)

    def test_last_twelve_months(self):
        days = {}
        with open(CSV, encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        for r in rows[1:]:
            if r[ix["in_last_twelve"]] == "1":
                days.setdefault(r[ix["local_day"]], []).append(float(r[ix["price_energy_usd_mwh"]]))
        self.assertEqual(len(days), 365)
        dp = sum(mr.battery_day(p, 4)[0] for p in days.values()) / 1000
        lp = sum(any_power(p, 4) for p in days.values()) / 1000
        below = sum(1 for p in days.values() if mr.battery_day(p, 4)[0] < any_power(p, 4) - 1e-6)
        self.assertAlmostEqual(dp, 58.72, places=1)
        self.assertAlmostEqual(lp, 59.95, places=1)
        self.assertGreater(below, 300)


    def test_no_text_calls_it_an_upper_bound(self):
        """The fix on this branch, in words: decision 3 and the note's section 3.3 (fails on main)."""
        for p in (("site", "lib", "decisions.ts"), ("docs", "methods", "generator_earns_algorithm.md")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn("so its figure is an upper bound", t, os.path.join(*p))
        with open(os.path.join(ROOT, "docs", "methods", "generator_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertNotIn("known in advance: **an upper bound**", f.read())


if __name__ == "__main__":
    unittest.main()
