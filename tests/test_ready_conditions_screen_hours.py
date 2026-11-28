"""Session 11407 (chain 770, part C), carried over from wip/audit-conditions-1 (session 10219, the conditions audit of
26 November, finding 1). /conditions printed EIA-930's demand as published, so PJM's COVID window printed 215,682 MW
(the hour starting 2020-04-10T03:00Z, 23:00 Eastern on 9 April), 2.7 times its forecast, as its "Highest peak demand".
On this branch the builder (warehouse/derived/conditions_page.py, screen_demand) applies the ERW's own rule for
impossible hours (warehouse/derived/impossible_hours.py) to each grid's demand before any figure is taken, and the
window's highest becomes 108,513 MW (26 May). The committed page files are rebuilt at landing by the desk: these tests
read the page file's hours and run the builder's own functions on them, so they pass before and after that rebuild.
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


def builder():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    import conditions_page
    return conditions_page


def frame(f, wid):
    """The window's hours as the builder holds them after its pivot: indexed by ts_utc, columns demand and forecast."""
    import pandas as pd
    hc = f["hourly_columns"]
    rows = f["hourly"][wid]
    w = pd.DataFrame({"demand": [r[hc.index("demand")] for r in rows], "forecast": [r[hc.index("forecast")] for r in rows]},
                     index=[r[0] for r in rows], dtype=float)
    w.index.name = "ts_utc"
    return w


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "pjm.json")), "the conditions files are not in this checkout")
class TheBuilderScreensImpossibleHours(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = load("pjm")
        cls.w = [w for w in cls.f["windows"] if w["id"] == "covid_2020"][0]
        cls.cp = builder()

    def test_the_builder_applies_the_rule_to_demand(self):
        s = src("warehouse", "derived", "conditions_page.py")
        self.assertIn("import impossible_hours", s)
        self.assertIn("impossible_hours.screen(s)", s)
        self.assertIn("w = screen_demand(w)", s)
        self.assertLess(s.index("w = screen_demand(w)"), s.index('if out is not None and "out" in o:'), "screened before any figure is taken")

    def test_the_impossible_hour_is_left_blank_and_nothing_else_moves_near_it(self):
        import pandas as pd
        w = frame(self.f, "covid_2020")
        kept = self.cp.screen_demand(w)
        self.assertTrue(pd.isna(kept.loc["2020-04-10T03:00:00Z", "demand"]))
        for t in ("2020-04-10T01:00:00Z", "2020-04-10T02:00:00Z", "2020-04-10T04:00:00Z", "2020-04-10T05:00:00Z"):
            self.assertEqual(kept.loc[t, "demand"], w.loc[t, "demand"], t)
        self.assertTrue(kept["forecast"].equals(w["forecast"]), "the forecast is not screened")

    def test_the_covid_window_peak_becomes_108513_on_26_may(self):
        w = self.cp.screen_demand(frame(self.f, "covid_2020")).reset_index()
        w["local"] = self.cp.local(w["ts_utc"], "America/New_York")
        w["day"] = w["local"].dt.strftime("%Y-%m-%d")
        cols, rows = self.cp.daily_rows(w, "pjm", None)
        i = cols.index("demand_peak")
        days = [r for r in rows if self.w["start"] <= r[0] <= self.w["end"] and r[i] is not None]
        top = max(days, key=lambda r: r[i])  # the page's glance: the largest day, the first on a tie
        self.assertEqual((top[0], top[i]), ("2020-05-26", 108513.0))

    def test_the_method_notes_say_so(self):
        self.assertIn("8. **Impossible hours.**", src("docs", "methods", "grid_conditions.md"))
        self.assertIn("the grid conditions page files", src("docs", "methods", "impossible_hours.md"))


if __name__ == "__main__":
    unittest.main()
