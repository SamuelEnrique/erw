"""Audit of the games under /play, finding 7 (session 10227, docs/reviews/play-model-audit-2026-11-26.md), for the
owner's ruling, not for landing: "Should your family get an EV?" prices eight years of fuel at the newest week of
gasoline and the newest month of electricity, held flat (site/data/ev_prices.json; site/lib/ev.ts verdict). The page
says so. In the week the file holds (9 November 2026) gasoline stood above its year: the United States' 52-week mean to
2 November was USD 3.7328 against the week's 3.995 (eia_regional_retail_fuel_prices, the audit's copy).

This test shows the size of the choice and changes nothing; it passes on main. With the 52-week mean, the net present
value at the defaults falls from USD 3,887 to 2,946 for the United States and turns below zero in Massachusetts, New
Hampshire, New York and Rhode Island. The 52-week means are the audit's, measured from the warehouse table (the main
copy's, to 2 November 2026). Default: left as it is.

No table, no request, no model call; the environment is read, never set."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# the 52 weeks of regular gasoline to 2026-11-02, mean USD a gallon (the audit's ev_restate.json)
GAS_52W = {"US": 3.732826923076923, "MA": 3.6705384615384613, "NH": 3.691230769230769, "NY": 3.749769230769231, "RI": 3.691230769230769}
D = dict(miles=15000, mpg=27, kwh_mile=0.31, gas_car=28600, ev_car=33600, years=8, rate=5.0)


def npv(power_usd_mwh, gas_usd_gal):
    save = (100 / D["mpg"] * gas_usd_gal - 100 * D["kwh_mile"] * power_usd_mwh / 1000) * D["miles"] / 100
    return sum(save / (1 + D["rate"] / 100) ** t for t in range(1, D["years"] + 1)) - (D["ev_car"] - D["gas_car"])


class OneWeekOfGasoline(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "site", "data", "ev_prices.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.places = {"US": d["us"], **{s["code"]: s for s in d["states"]}}

    def test_the_page_uses_the_newest_week(self):
        self.assertEqual(self.places["US"]["gas"]["ts"], "2026-11-09")
        self.assertEqual(self.places["US"]["gas"]["value"], 3.995)

    def test_what_the_year_would_move(self):
        us = self.places["US"]
        self.assertAlmostEqual(npv(us["power"]["value"], us["gas"]["value"]), 3886.95, places=2)   # the page's 3,887
        self.assertAlmostEqual(npv(us["power"]["value"], GAS_52W["US"]), 2945.57, places=2)
        for code in ("MA", "NH", "NY", "RI"):
            with self.subTest(code=code):
                p = self.places[code]
                self.assertGreater(npv(p["power"]["value"], p["gas"]["value"]), 0)
                self.assertLess(npv(p["power"]["value"], GAS_52W[code]), 0)

    def test_no_em_dash(self):
        with open(os.path.join(ROOT, "tests", "test_audit_play_7.py"), encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
