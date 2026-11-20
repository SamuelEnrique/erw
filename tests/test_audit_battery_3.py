"""Audit of "What a battery earns", finding 3 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the battery
is paid the hourly mean of ERCOT's real-time price, which ERCOT settles every 15 minutes.

1. A day whose every hour has the same mean but whose quarters move: the model (battery_stack.solve_day, which sees the
   hourly means only, as warehouse/derived/cost_of_power.hourly makes them) earns nothing from energy, and the same
   program paid at the four quarter prices earns from the spread inside the hour.
2. On a machine with ERCOT's 15-minute tables (warehouse/output): the default case's last twelve months at the quarter
   prices, every other rule the model's. Session 9840 measured USD 83.64 per kW against the page's 81.40.
It passes on the code as it is: it shows the fault. Nothing is written."""
import csv
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import battery_stack as bs  # noqa: E402
from audit_battery_lp import solve_block  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


class QuarterHours(unittest.TestCase):
    def test_flat_hours_with_moving_quarters(self):
        quarters = [[20.0, 20.0, 60.0, 60.0]] * 24                  # every hour's mean is 40
        spec = ((True, 0.5),)                                       # one upward product, never paid here
        model = bs.solve_day([float(np.mean(q)) for q in quarters], [[0.0] * 24], spec, 4)
        self.assertAlmostEqual(model["energy"], 0.0, places=6)      # a flat hourly price: nothing to sell
        hrs = [dict(day="2026-01-01", p=q, a=[0.0], spec=spec, keys=["regup"]) for q in quarters]
        hourly = solve_block([dict(h, p=[float(np.mean(h["p"]))]) for h in hrs], 4, q=1)
        quarter = solve_block(hrs, 4, q=4)
        self.assertAlmostEqual(hourly["total"], model["total"], places=6)
        self.assertGreater(quarter["energy"], 20.0)                 # buy at 20 and sell at 60 inside the hours

    def test_last_twelve_months_at_quarter_prices(self):
        hist = os.path.join(ROOT, "warehouse", "output", "ercot_all_hub_prices_history.csv")
        roll = os.path.join(ROOT, "warehouse", "output", "iso_rtm_hub_prices.csv")
        if not (os.path.exists(hist) and os.path.exists(roll)):
            self.skipTest("ERCOT's 15-minute tables are not on this machine")
        import pandas as pd
        import iso_prices as ip

        def rt(path):
            parts = []
            for ch in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["ts_utc", "value", "market", "node"], dtype=str, chunksize=500_000):
                parts.append(ch[(ch["market"] == "ercot_rtm") & (ch["node"] == "HB_HUBAVG")])
            x = pd.concat(parts)
            return pd.Series(x["value"].astype(float).values, index=pd.to_datetime(x["ts_utc"], utc=True)).sort_index()
        h, r = rt(hist), rt(roll)
        q = pd.concat([h, r[r.index > h.index.max()]])
        with open(CSV, encoding="utf-8") as f:
            rows = [x for x in csv.reader(f) if x and not x[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        days = {}
        for x in rows[1:]:
            if x[ix["in_last_twelve"]] != "1":
                continue
            d = x[ix["local_day"]]
            ts = pd.Timestamp(x[ix["hour_utc"]])
            four = q.loc[ts:ts + pd.Timedelta(minutes=45)].to_numpy()
            self.assertEqual(len(four), 4)
            self.assertAlmostEqual(float(four.mean()), float(x[ix["price_energy_usd_mwh"]]), places=6)
            prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
            days.setdefault(d, []).append(dict(day=d, p=list(four), a=[float(x[ix[f"price_{p['key']}_usd_mw"]]) for p in prods],
                                               spec=tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods), keys=[p["key"] for p in prods]))
        quarter = sum(solve_block(hrs, 4, q=4)["total"] for hrs in days.values()) / 1000
        self.assertGreater(quarter, 81.4022 + 1.5, f"at quarter prices {quarter:.4f} per kW")


if __name__ == "__main__":
    unittest.main()
