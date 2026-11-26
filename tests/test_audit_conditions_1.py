"""Session 10219 (chain 710, the conditions audit, finding 1): /conditions prints EIA-930's demand as published, with no
screen for impossible hours, so a report fault can be the "Highest peak demand" a window prints. PJM's COVID window
prints 215,682 MW (the hour starting 2020-04-10T03:00Z, 23:00 Eastern on 9 April), 2.7 times its forecast; the ERW's
own rule (warehouse/derived/impossible_hours.py) leaves that hour out, and the window's highest becomes 108,513 MW
(26 May). Not fixed: the figure moves, so the ruling is the owner's (docs/reviews/conditions-model-audit-2026-11-26.md).
These tests pass on main: they show the finding, not a fix.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def load(op):
    with open(os.path.join(DIR, op + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "pjm.json")), "the conditions files are not in this checkout")
class AnImpossibleHourIsThePeak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = load("pjm")
        cls.w = [w for w in cls.f["windows"] if w["id"] == "covid_2020"][0]

    def test_the_covid_window_prints_an_hour_far_from_its_neighbours(self):
        dc = self.f["daily_columns"]
        i, j = dc.index("demand_peak"), dc.index("forecast_peak")
        days = [r for r in self.f["daily"] if self.w["start"] <= r[0] <= self.w["end"] and r[i] is not None]
        top = max(days, key=lambda r: r[i])  # the page's glance: the largest day, the first on a tie
        self.assertEqual((top[0], top[i]), ("2020-04-09", 215682.0))
        self.assertGreater(top[i], 2.5 * top[j], "the forecast that day was a third of it")
        rows = self.f["hourly"]["covid_2020"]
        hc = self.f["hourly_columns"]
        k = hc.index("demand")
        at = [n for n, r in enumerate(rows) if r[0] == "2020-04-10T03:00:00Z"][0]
        around = sorted(rows[n][k] for n in (at - 2, at - 1, at + 1, at + 2))
        self.assertGreater(rows[at][k], 2.5 * (around[1] + around[2]) / 2)

    def test_the_erws_own_rule_leaves_it_out_and_the_figure_moves(self):
        import pandas as pd
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
        import impossible_hours as ih
        rows = self.f["hourly"]["covid_2020"]
        k = self.f["hourly_columns"].index("demand")
        s = pd.Series([r[k] if r[k] is not None else float("nan") for r in rows], index=pd.to_datetime([r[0] for r in rows], utc=True), dtype=float).asfreq("h")
        kept = ih.screen(s)
        self.assertTrue(pd.isna(kept[pd.Timestamp("2020-04-10T03:00:00Z")]))
        local = kept.tz_convert("America/New_York")
        inw = local[(local.index.strftime("%Y-%m-%d") >= self.w["start"]) & (local.index.strftime("%Y-%m-%d") <= self.w["end"])]
        self.assertEqual(float(inw.max()), 108513.0)
        self.assertEqual(inw.idxmax().strftime("%Y-%m-%d"), "2020-05-26")

    def test_a_day_outside_the_kept_windows_too(self):
        dc = self.f["daily_columns"]
        i, j = dc.index("demand_peak"), dc.index("forecast_peak")
        r = [x for x in self.f["daily"] if x[0] == "2020-07-13"][0]
        self.assertEqual(r[i], 224345.0)
        self.assertGreater(r[i], 1.5 * r[j])

    def test_the_builder_applies_no_screen(self):
        s = src("warehouse", "derived", "conditions_page.py")
        self.assertNotIn("impossible_hours", s)


if __name__ == "__main__":
    unittest.main()
