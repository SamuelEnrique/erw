"""Session 8013 (chain 505, part D2): the operators' wind and solar forecasts beside the output (renewables_forecast.json).

Contract: section 12 of docs/state/page_files_regions.md. The file is computed from caiso_wind_solar_forecast and
ercot_wind_solar_forecast; no figure of the ERW's own.
"""

import json
import os
import sys
import unittest

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "warehouse", "derived"))
import renewable_forecast_error as rfe  # noqa: E402

FILE = os.path.join(REPO, "site", "data", "regions", "renewables_forecast.json")


def load():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


class TheMeasures(unittest.TestCase):
    def test_a_miss_is_the_forecast_less_the_output(self):
        x = pd.DataFrame({"f": [110.0, 90.0], "a": [100.0, 100.0]})
        s = rfe.stats(x)
        self.assertEqual(s["bias_mw"], 0.0)
        self.assertEqual(s["mae_mw"], 10.0)
        self.assertEqual(s["wape_pct"], 10.0)

    def test_no_output_gives_no_percent(self):
        s = rfe.stats(pd.DataFrame({"f": [1.0], "a": [0.0]}))
        self.assertIsNone(s["wape_pct"])


class TheFile(unittest.TestCase):
    def test_two_grids_each_with_wind_and_solar_and_the_others_said(self):
        d = load()
        self.assertEqual([g["grid"] for g in d["grids"]], ["CAISO", "ERCOT"])
        for g in d["grids"]:
            self.assertEqual(set(g["series"]), {"wind", "solar"})
            for s in g["series"].values():
                self.assertEqual(len(s["by_hour"]["wape_pct"]), 24)
                self.assertEqual(len(s["events"]), 9)
                self.assertEqual(len(s["daily"]["days"]), len(s["daily"]["miss_mwh"]))
        self.assertEqual({n["grid"] for n in d["not_held"]}, {"SPP", "NYISO", "ISO-NE", "PJM", "MISO"})

    def test_a_daily_miss_is_its_forecast_less_its_output(self):
        s = load()["grids"][1]["series"]["solar"]["daily"]
        for f, a, m in zip(s["forecast_mwh"], s["actual_mwh"], s["miss_mwh"]):
            self.assertAlmostEqual(f - a, m, delta=0.2)

    def test_an_event_the_table_does_not_reach_is_blank(self):
        for g in load()["grids"]:
            for s in g["series"].values():
                for e in s["events"]:
                    if e["hours"] == 0:
                        self.assertIsNone(e["wape_pct"])


if __name__ == "__main__":
    unittest.main()
