"""Audit of /forecast, finding 4 (session 11402, docs/reviews/forecast-model-audit-2026-11-28.md): each place's method is
chosen by the lowest error over the last two years of the backtest, the same window its "last two years" figures are
scored on. Twice the method so chosen loses to the naive line over the rest of the page's own backtest:

- SPP's day-ahead price (region-cent, ba-swpp): the regression, chosen, beats yesterday's price over the last two years
  (14.52 against 16.53 USD/MWh) and loses over the whole backtest (34.63 against 18.73) and over the years before the
  window (45.81 against 19.95, 30,847 hours). CAISO: wins the window (5.90 against 6.20), loses the months before it
  (7.81 against 7.50, 4,776 hours), and stays the regression on the whole backtest (6.31 against 6.48).
- PSCO's day peak: regression_recent, chosen, loses to yesterday's peak before the window (727.5 against 527.7 MW over
  1,912 days); over the whole backtest yesterday's peak is ahead (MAPE 8.349 against 10.387).

The hourly demand forecast is not affected: it beats both naive lines before the window too, in all 64 places.

This moves figures, so no fix is made: choosing on the whole backtest is Samuel's ruling. The tests pass on main while
the files are those audited (built 2026-11-27T14:39:36Z) and are skipped once they are rebuilt."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site", "data", "predict")
AUDITED = "2026-11-27T14:39:36Z"


def load(name):
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        return json.load(f)


class ChoiceWindow(unittest.TestCase):
    def setUp(self):
        self.sc = load("scores.json")
        if self.sc.get("built") != AUDITED:
            self.skipTest("the score file is not the one audited (rebuilt since)")
        cols = self.sc["rows_columns"]
        self.R = {}
        for r in self.sc["rows"]:
            d = dict(zip(cols, r))
            self.R[(d["place"], d["series"], d["method"], d["cut"], str(d["key"]))] = d

    def before(self, place, series, m):
        a, l2 = self.R[(place, series, m, "all", "")], self.R[(place, series, m, "last_2_years", "")]
        return (a["mae"] * a["hours"] - l2["mae"] * l2["hours"]) / (a["hours"] - l2["hours"]), a["hours"] - l2["hours"]

    def test_spp_price_regression_wins_its_window_and_loses_the_backtest(self):
        for place in ("region-cent", "ba-swpp"):
            f = load(f"{place}.json")["series"]["price"]
            self.assertEqual(f["method"], "regression")
            l2 = {m: self.R[(place, "price", m, "last_2_years", "")]["mae"] for m in ("regression", "yesterday")}
            al = {m: self.R[(place, "price", m, "all", "")]["mae"] for m in ("regression", "yesterday")}
            self.assertLess(l2["regression"], l2["yesterday"])
            self.assertGreater(al["regression"], 1.8 * al["yesterday"])
            reg, n = self.before(place, "price", "regression")
            yes, _ = self.before(place, "price", "yesterday")
            self.assertGreater(n, 30000)
            self.assertGreater(reg, 2 * yes)

    def test_caiso_price_regression_loses_the_months_before_its_window(self):
        for place in ("region-cal", "ba-ciso"):
            reg, n = self.before(place, "price", "regression")
            yes, _ = self.before(place, "price", "yesterday")
            self.assertGreater(n, 4000)
            self.assertGreater(reg, yes)
            self.assertLess(self.R[(place, "price", "regression", "all", "")]["mae"], self.R[(place, "price", "yesterday", "all", "")]["mae"])

    def test_psco_peak_loses_to_yesterdays_before_its_window(self):
        pk = load("ba-psco.json")["series"]["demand"]["peak"]
        self.assertEqual(pk["method"], "regression_recent")
        B, L2 = pk["backtest"], pk["last_2_years"]
        n = B["days"] - L2["days"]
        pre = {m: (B["methods"][m]["mae"] * B["days"] - L2["methods"][m]["mae"] * L2["days"]) / n for m in ("erw", "yesterday")}
        self.assertGreater(n, 1800)
        self.assertGreater(pre["erw"], 1.3 * pre["yesterday"])
        self.assertLess(L2["methods"]["erw"]["mae"], L2["methods"]["yesterday"]["mae"])
        self.assertGreater(B["methods"]["erw"]["mape"], B["methods"]["yesterday"]["mape"])

    def test_hourly_demand_beats_both_naive_lines_before_the_window(self):
        idx = load("index.json")
        n = 0
        for p in idx["places"]:
            erw, _ = self.before(p["place"], "demand", "erw")
            for m in ("yesterday", "week_ago"):
                self.assertLess(erw, self.before(p["place"], "demand", m)[0], (p["place"], m))
            n += 1
        self.assertEqual(n, 64)


if __name__ == "__main__":
    unittest.main()
