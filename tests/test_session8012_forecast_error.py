"""Session 8012, chain 505 (part D1): the day-ahead demand forecast beside the demand that came."""
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "regions", "forecast")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def load(rel):
    with open(os.path.join(DIR, rel), encoding="utf-8") as f:
        return json.load(f)


class TheArithmetic(unittest.TestCase):
    def setUp(self):
        # session 8013: loaded under its own name; warehouse/analysis/templates/forecast_error.py is another module of
        # the same name, and the template loader of the same test run would be handed this one from sys.modules
        import importlib.util
        spec = importlib.util.spec_from_file_location("derived_forecast_error", os.path.join(ROOT, "warehouse", "derived", "forecast_error.py"))
        fe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fe)
        self.fe = fe

    def test_miss_is_forecast_less_demand_and_the_screen(self):
        idx = pd.date_range("2025-07-01T00:00Z", periods=4, freq="h")
        x = self.fe.frame_of(pd.Series([110.0, 90.0, 400.0, 20.0], index=idx), pd.Series([100.0, 100.0, 100.0, 100.0], index=idx))
        self.assertEqual(list(x["miss"]), [10.0, -10.0, 300.0, -80.0])
        self.assertEqual(list(x["screened"]), [False, False, True, True])

    def test_wape_is_not_swamped_by_small_hours(self):
        idx = pd.date_range("2025-07-01T00:00Z", periods=2, freq="h")
        x = self.fe.frame_of(pd.Series([1000.0, 2.0], index=idx), pd.Series([1000.0, 1.0], index=idx))
        s = self.fe.stats(x)
        self.assertEqual(s["mape_pct"], 50.0)
        self.assertLess(s["wape_pct"], 0.2)

    def test_a_day_needs_every_hour(self):
        idx = pd.date_range("2025-07-01T05:00Z", periods=23, freq="h")   # one hour short of the Central day
        x = self.fe.frame_of(pd.Series(100.0, index=idx), pd.Series(100.0, index=idx))
        self.assertEqual(len(self.fe.daily_rows(x, "America/Chicago")), 0)


@unittest.skipUnless(os.path.isdir(DIR), "the forecast files are not on this checkout")
class TheFiles(unittest.TestCase):
    def test_the_regions_and_their_parts(self):
        index = json.load(open(os.path.join(ROOT, "site", "data", "regions", "index.json"), encoding="utf-8"))
        regions = {r["code"].lower() + ".json" for r in index["regions"]}
        have = {n for n in os.listdir(DIR) if n.endswith(".json")}
        self.assertEqual(have - regions, set())
        for n in have:
            d = load(n)
            for k in ("overall", "by_hour", "by_season", "by_year", "daily", "events"):
                self.assertIn(k, d, (n, k))
            self.assertEqual(len(d["by_hour"]["mape_pct"]), 24)
            self.assertEqual(len(d["events"]), 9)
            self.assertEqual(len(d["daily"]["days"]), len(d["daily"]["mape_pct"]))

    def test_texas_is_ercot(self):
        self.assertEqual(load("tex.json")["overall"]["mape_pct"], load(os.path.join("ba", "erco.json"))["overall"]["mape_pct"])

    def test_no_em_dash(self):
        for root, _, files in os.walk(DIR):
            for n in files:
                with open(os.path.join(root, n), encoding="utf-8") as f:
                    self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
