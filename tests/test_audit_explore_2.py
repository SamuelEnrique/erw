"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 1, the figure). Not for landing: a test only, for the owner's ruling.

/explore/ercot-peak-premium's default view sets 2015 beside 2025 in nominal dollars. Written in 2025 dollars by the GDP
price index the site already holds (site/data/forecast/deflator.json, the forecast tool's), 2015's thesis figures move
by a third: what the page would print for 2015 if the owner rules for constant dollars. The test passes on main where
the annual table is held (warehouse/output, or a folder named by ERW_AUDIT_OUTPUT).
"""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def table(name):
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name + ".csv")):
            return os.path.join(d, name + ".csv")
    return None


class TwentyFifteenInTwentyTwentyFiveDollars(unittest.TestCase):
    def test_the_thesis_figures_of_2015_in_2025_dollars(self):
        path = table("ercot_peak_premium_annual")
        if not path:
            self.skipTest("ercot_peak_premium_annual is not held on this machine")
        with open(os.path.join(ROOT, "site", "data", "forecast", "deflator.json"), encoding="utf-8") as f:
            idx = json.load(f)["index"]
        k = idx["2025"] / idx["2015"]
        a = {}
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["entity"] == "ercot:HB_HUBAVG" and r["ts_utc"].startswith("2015"):
                    a[r["variable"]] = float(r["value"])
        moved = {v: f"{a[v] * k:.2f}" for v in ("all_median", "all_p999", "peak_iqr", "peak_minus_midday_median", "midday_min", "peak_median", "midday_median")}
        self.assertEqual(moved, {
            "all_median": "27.15", "all_p999": "773.82", "peak_iqr": "10.12", "peak_minus_midday_median": "-0.21",
            "midday_min": "-5.27", "peak_median": "31.96", "midday_median": "32.17",
        })
        # a ratio and a count do not move
        self.assertEqual(f"{a['worst_interval_multiple']:.2f}", "28.50")


if __name__ == "__main__":
    unittest.main()
