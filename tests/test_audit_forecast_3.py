"""Audit of /forecast, finding 3 (session 11402, docs/reviews/forecast-model-audit-2026-11-28.md): the day-ahead price
forecast is scored as made at 14:00 UTC the day before, "before any grid publishes its day-ahead prices for the day", from
the demand through three days before (index.json's made_rule, docs/methods/predict_price.md section 2). The daily run
makes the live forecast at the hour it runs (about 19:00 UTC: the ledger's forecasts for 28 November were made at 19:00
UTC on 27 November), after ERCOT's day-ahead prices are usually public (median about 11.4 hours before the day begins,
18:36 UTC in winter; docs/reviews/predict-ground-2026-11-26.md), and run.py's price_place refits it on the demand held
then, through two days before (demand_horizon_days 2), not the three of the backtest.

1. The code (passes on main): price_place takes both horizons from what is held at the hour of the run.
2. The data machine's build of 27 November (passes on main; skipped where git history is shallow): every price place
   made at 19:00 UTC with demand_horizon_days 2, and the ledger's rows for 28 November made at 19:00 UTC.
3. The fix on this branch (fails on main): the rule and the note say what the live forecast is; the page's made-hour
   check (site/lib/predict.ts madeOffRule) still reads 14:00 as the price rule's hour."""
import json
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUN = os.path.join(ROOT, "warehouse", "predict", "run.py")
NOTE = os.path.join(ROOT, "docs", "methods", "predict_price.md")
V3 = "15511cb2e"


def text(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class LivePriceForecast(unittest.TestCase):
    def test_the_live_horizons_are_those_held_at_the_run(self):
        src = text(RUN)
        self.assertIn("hp, hd = int((target - last_p).days), int((target - last_d).days)", src)
        self.assertIn("res_h = price.place_forecasts(s, tz, dem[place], tz, gas, hp=hp, hd=hd)", src)

    def test_the_run_of_27_november_made_it_at_19_with_two_days_of_demand(self):
        got = subprocess.run(["git", "-C", ROOT, "show", f"{V3}:site/data/predict/region-cal.json"], capture_output=True)
        if got.returncode != 0:
            self.skipTest("the commit of the data machine's build is not in this clone")
        for place in ("region-tex", "ba-erco", "region-cent", "ba-swpp", "region-cal", "ba-ciso"):
            raw = subprocess.run(["git", "-C", ROOT, "show", f"{V3}:site/data/predict/{place}.json"], capture_output=True, check=True).stdout
            s = json.loads(raw.decode("utf-8"))["series"]["price"]
            self.assertEqual(s["made_utc"], "2026-11-27T19:00:00Z")
            self.assertEqual(s["target_day"], "2026-11-28")
            self.assertEqual(s["demand_horizon_days"], 2)

    def test_the_rule_and_the_note_say_what_the_live_forecast_is(self):
        src = text(RUN)
        self.assertIn("The daily run makes the live price forecast later, at about 19:00 UTC", src)
        self.assertIn("The live forecast is made later than the hour it is scored at", text(NOTE))
        line = next(x for x in src.splitlines() if "made_rule=" in x).replace("{price.PRICE_MADE_HOUR}", "14").replace("{DEMAND_MADE_HOUR}", "20")
        said = re.search(r"price forecast[^;.]*?\b(\d{1,2}:\d{2}) UTC", line, re.I)
        self.assertEqual(said.group(1), "14:00")
        said = re.search(r"demand forecast[^;.]*?\b(\d{1,2}:\d{2}) UTC", line, re.I)
        self.assertEqual(said.group(1), "20:00")


if __name__ == "__main__":
    unittest.main()
