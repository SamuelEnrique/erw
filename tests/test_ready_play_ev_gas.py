"""A ready branch for Samuel's ruling (session 11407, chain 770 part C), from the play audit's finding 7 (session 10227,
docs/reviews/play-model-audit-2026-11-26.md; its test tests/test_audit_play_7.py on wip/audit-play-7, carried over here
and turned to assert the new rule): "Should your family get an EV?" prices gasoline at the mean of its 52 newest weeks,
not the newest week alone (site/scripts/build-ev-prices.mjs, gasMean).

The builder is run here on a small table written to a temporary folder (no warehouse table is read or written), and
its gasoline cell must be the mean of the weeks in the 52 weeks to the newest, with the newest week kept beside it.
The size of the choice, from the audit's 52-week means (the main copy's table, to 2 November 2026): the United States'
net present value at the defaults falls from USD 3,887 to 2,946, and Massachusetts, New Hampshire, New York and Rhode
Island turn below zero. site/data/ev_prices.json itself is rebuilt by the desk at landing, on the data machine's tables.

No model call, no request; the environment is read, never set."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
# the 52 weeks of regular gasoline to 2026-11-02, mean USD a gallon (the audit's ev_restate.json)
GAS_52W = {"US": 3.732826923076923, "MA": 3.6705384615384613, "NH": 3.691230769230769, "NY": 3.749769230769231, "RI": 3.691230769230769}
D = dict(miles=15000, mpg=27, kwh_mile=0.31, gas_car=28600, ev_car=33600, years=8, rate=5.0)
HEAD = "entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage"


def npv(power_usd_mwh, gas_usd_gal):
    save = (100 / D["mpg"] * gas_usd_gal - 100 * D["kwh_mile"] * power_usd_mwh / 1000) * D["miles"] / 100
    return sum(save / (1 + D["rate"] / 100) ** t for t in range(1, D["years"] + 1)) - (D["ev_car"] - D["gas_car"])


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AYearOfGasoline(unittest.TestCase):
    def test_what_the_year_moves(self):
        with open(os.path.join(SITE, "data", "ev_prices.json"), encoding="utf-8") as f:
            d = json.load(f)
        places = {"US": d["us"], **{s["code"]: s for s in d["states"]}}
        us = places["US"]
        self.assertAlmostEqual(npv(us["power"]["value"], GAS_52W["US"]), 2945.57, places=2)   # the page's 3,887 becomes 2,946
        for code in ("MA", "NH", "NY", "RI"):
            with self.subTest(code=code):
                self.assertLess(npv(places[code]["power"]["value"], GAS_52W[code]), 0)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_builder_writes_the_52_week_mean(self):
        newest = date(2026, 11, 2)
        weeks = [newest - timedelta(days=7 * i) for i in range(60)]                     # 60 weeks, the newest first
        price = {w: round(3.0 + 0.01 * i, 3) for i, w in enumerate(weeks)}            # 3.00 the newest, rising into the past
        ma_weeks = [w for w in weeks if w != newest - timedelta(days=7 * 10)]          # Massachusetts misses one week
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "eia_regional_retail_fuel_prices.csv"), "w", encoding="utf-8") as f:
                f.write("# Source: test\n# Retrieved: test\n" + HEAD + "\n")
                for w in weeks:
                    f.write(f"eia:EMM_EPMR_PTE_NUS_DPG,retail_price,{w}T00:00:00Z,{price[w]},USD/gal,P1W,US,,,t,t,t,\n")
                for w in ma_weeks:
                    f.write(f"eia:EMM_EPMR_PTE_SMA_DPG,retail_price,{w}T00:00:00Z,{price[w]},USD/gal,P1W,US-MA,,,t,t,t,\n")
            with open(os.path.join(tmp, "eia_retail_electricity_prices.csv"), "w", encoding="utf-8") as f:
                f.write("# Source: test\n# Retrieved: test\n" + HEAD + "\n")
                f.write("eia:retail_price:US:RES,retail_price,2026-08-01T00:00:00Z,181.6,USD/MWh,P1M,US,,,t,t,t,\n")
            out = os.path.join(tmp, "ev_prices.json")
            r = subprocess.run([NODE, os.path.join("scripts", "build-ev-prices.mjs"), tmp, out], cwd=SITE, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            with open(out, encoding="utf-8") as f:
                d = json.load(f)
        g = d["us"]["gas"]
        want = sum(price[w] for w in weeks[:52]) / 52
        self.assertAlmostEqual(g["value"], want, places=12)
        self.assertEqual((g["weeks"], g["from"], g["ts"], g["newest"]), (52, str(weeks[51]), "2026-11-02", 3.0))
        ma = next(s for s in d["states"] if s["code"] == "MA")["gas"]
        held = [w for w in ma_weeks if w >= weeks[51]]
        self.assertEqual((ma["weeks"], ma["where"]), (51, "state"))                     # the missing week is not filled
        self.assertAlmostEqual(ma["value"], sum(price[w] for w in held) / 51, places=12)
        ct = next(s for s in d["states"] if s["code"] == "CT")
        self.assertIsNone(ct["gas"])                                                   # no region series held: nothing written
        self.assertIn("the mean of the 52 weeks to the newest week", d["note"])

    def test_the_page_says_it(self):
        game = read("site", "app", "play", "ev", "EvGame.tsx")
        self.assertIn("regular gasoline, the average of the {place.gas.weeks} weeks from the week of", game)
        self.assertIn("weeks?: number; from?: string; newest?: number", game)
        self.assertIn("the average of the 52 newest weekly prices EIA publishes", read("site", "app", "play", "ev", "Decisions.tsx"))
        self.assertIn("## A year of gasoline, not one week (session 11407", read("docs", "methods", "ev_game.md"))

    def test_no_em_dash(self):
        for p in (("tests", "test_ready_play_ev_gas.py"), ("site", "scripts", "build-ev-prices.mjs"), ("site", "app", "play", "ev", "EvGame.tsx"),
                  ("site", "app", "play", "ev", "Decisions.tsx"), ("docs", "methods", "ev_game.md")):
            self.assertNotIn(chr(0x2014), read(*p))


if __name__ == "__main__":
    unittest.main()
