"""Session 51: the cost of power, the seller's side.

Energy Research Warehouse (ERW). No network, no model, no database. Checks that need the warehouse's files run where
they are on this machine and are skipped otherwise (warehouse/output and warehouse/raw are not in git).
1. Hand-computed, from the source files and not through the builder: one ERCOT solar month (2025-07: the hub's
   15-minute real-time prices averaged to hours, EIA-930's Adjusted SUN Gen over EIA-860M's solar nameplate in ERCO
   that month), one peaker month (2025-07: Henry Hub, the last trading day's on a day without one, x 10.725 + 4.25),
   and one battery day against the DP (2023-08-10, a 2-hour battery: the DP equals brute force over every action
   sequence of the day's 12 evening hours, and the full day's plan replays to its value).
2. The snapshot the page reads equals the warehouse table, every asset, month and metric.
3. The table is never in Supabase; the units are in the vocabulary; the defaults trace to Lazard.
4. The questions file: ten questions, each tied to a part of the tab.

    python -m unittest tests.test_session51 -v
"""

import glob
import itertools
import json
import math
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
SNAP = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    p = os.path.join(OUT, name + ".csv")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(p, skiprows=n, low_memory=False)


def ercot_rt_hours(start, end):
    """ERCOT HB_HUBAVG real-time, the hours of [start, end) (UTC), each the mean of its four 15-minute prices."""
    parts = []
    for name in ("ercot_all_hub_prices_history", "iso_rtm_hub_prices"):
        p = os.path.join(OUT, name + ".csv")
        with open(p, encoding="utf-8") as f:
            n = sum(1 for line in f if line.startswith("#"))
        for ch in pd.read_csv(p, skiprows=n, chunksize=500_000, usecols=["entity", "variable", "ts_utc", "value", "market"]):
            x = ch[(ch["entity"] == "ercot:HB_HUBAVG") & (ch["market"] == "ercot_rtm") & (ch["ts_utc"] >= start) & (ch["ts_utc"] < end)]
            if len(x):
                parts.append(x)
    x = pd.concat(parts).drop_duplicates("ts_utc")
    x["h"] = pd.to_datetime(x["ts_utc"], utc=True).dt.floor("h")
    g = x.groupby("h")["value"].agg(["mean", "size"])
    return g.loc[g["size"] == 4, "mean"]


HAVE = all(os.path.exists(os.path.join(OUT, n + ".csv")) for n in (
    "merchant_revenue_monthly", "ercot_all_hub_prices_history", "iso_rtm_hub_prices", "eia860m_operating_generators", "eia_fuel_spot_prices"))


@unittest.skipUnless(HAVE and os.path.exists(SNAP), "the warehouse tables are not on this machine")
class ByHand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = table("merchant_revenue_monthly")
        cls.t = t[t["entity"] == "ercot:HB_HUBAVG"].assign(m=lambda d: d["ts_utc"].str[:7])
        # July 2025, Central time: 2025-07-01 05:00 UTC to 2025-08-01 05:00 UTC
        cls.p = ercot_rt_hours("2025-07-01T05:00:00Z", "2025-08-01T05:00:00Z")

    def row(self, v):
        x = self.t[(self.t["m"] == "2025-07") & (self.t["variable"] == v)]
        self.assertEqual(len(x), 1, v)
        return float(x["value"].iloc[0])

    def test_ercot_solar_month(self):
        import openpyxl
        wb = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "eia930_emissions", "*", "*_ERCO.xlsx")))
        wb = [w for w in wb if os.path.getsize(w) > 0]
        if not wb:  # session 77: raw files stay on the machine that downloaded them (docs/machines.md)
            self.skipTest("EIA-930's ERCO workbook (warehouse/raw/eia930_emissions) is not on this machine")
        wb = wb[-1]
        ws = openpyxl.load_workbook(wb, read_only=True)["Published Hourly Data"]
        rows = ws.iter_rows(values_only=True)
        hdr = list(next(rows))
        it, isun = hdr.index("UTC time"), hdr.index("Adjusted SUN Gen")
        sun = {}
        for r in rows:
            if r[it] is None:
                continue
            h = pd.Timestamp(r[it], tz="UTC") - pd.Timedelta(hours=1)
            if pd.Timestamp("2025-07-01T05:00:00Z") <= h < pd.Timestamp("2025-08-01T05:00:00Z") and r[isun] is not None:
                sun[h] = float(r[isun])
        g = table("eia860m_operating_generators")
        r_ = table("eia860m_retired_generators")
        g = pd.concat([g.assign(ret=pd.NaT), r_.assign(ret=pd.to_datetime(r_["retirement_date"], errors="coerce"))])
        start = pd.to_datetime(g["operating_year"].astype("Int64").astype(str) + "-" + g["operating_month"].astype("Int64").astype(str).str.zfill(2) + "-01", errors="coerce")
        ms = pd.Timestamp("2025-07-01")
        cap = g.loc[(g["balancing_authority"] == "ERCO") & (g["energy_source"] == "SUN") & (start <= ms) & (g["ret"].isna() | (g["ret"] > ms)), "nameplate_mw"].sum()
        hours = [h for h in self.p.index if h in sun]
        energy = sum(sun[h] / cap for h in hours)
        sales = sum(sun[h] / cap * self.p[h] for h in hours)
        self.assertGreater(len(hours), 700)
        self.assertAlmostEqual(energy, self.row("solar_energy_per_mw"), places=3)
        self.assertAlmostEqual(sales, self.row("solar_revenue_per_mw"), places=2)
        self.assertAlmostEqual(sales / energy, self.row("solar_capture_price"), places=3)
        print(f"\n  ERCOT solar, 2025-07, by hand: {len(hours)} hours, {cap:,.1f} MW installed, {energy:.4f} MWh/MW, {sales:.4f} USD/MW, capture {sales / energy:.4f} USD/MWh")

    def test_ercot_peaker_month(self):
        f = table("eia_fuel_spot_prices")
        hh = f[(f["entity"] == "eia:henry_hub") & (f["variable"] == "spot_price")]
        hh = pd.Series(hh["value"].values, index=pd.to_datetime(hh["ts_utc"].str[:10])).sort_index()
        sales = cost = run = 0.0
        for h, p in self.p.items():
            day = pd.Timestamp(h.tz_convert("America/Chicago").strftime("%Y-%m-%d"))
            g = hh[hh.index <= day].iloc[-1]
            c = g * 10.725 + 4.25
            if p > c:
                sales, cost, run = sales + p, cost + c, run + 1
        self.assertAlmostEqual(run, self.row("peaker_energy_per_mw"), places=6)
        self.assertAlmostEqual(sales, self.row("peaker_sales_per_mw"), places=2)
        self.assertAlmostEqual(sales - cost, self.row("peaker_revenue_per_mw"), places=2)
        print(f"\n  ERCOT peaker, 2025-07, by hand: {int(run)} run hours, sales {sales:.4f}, fuel and VOM {cost:.4f}, margin {sales - cost:.4f} USD/MW")

    def test_battery_day_against_the_dp(self):
        import merchant_revenue as mr
        day = ercot_rt_hours("2023-08-10T05:00:00Z", "2023-08-11T05:00:00Z")
        self.assertEqual(len(day), 24)
        prices = list(day.values)
        # brute force over every action sequence of the evening's 12 hours (3^12), a 2-hour battery from empty, one cycle
        eve = prices[12:]
        eta = math.sqrt(mr.RTE)
        best = -1e18
        for seq in itertools.product((1, 0, -1), repeat=12):
            soc = cyc = cash = 0.0
            for a, p in zip(seq, eve):
                if a == 1:
                    stored = min(eta, 2 - soc)
                    if stored > 0:
                        soc += stored
                        cash -= stored / eta * p
                elif a == -1:
                    taken = min(1 / eta, soc, 2 - cyc)
                    if taken > 0:
                        soc -= taken
                        cyc += taken
                        cash += taken * eta * p
            best = max(best, cash)
        dp = mr.battery_day(eve, 2)
        # equal to a tenth of a thousandth of a dollar: the DP keys each state of charge to 1e-9 MWh, and at Uri-scale
        # prices that rounding moves the sum by about 1e-6 USD
        self.assertAlmostEqual(dp[0], best, places=4)
        # the full day: the DP's plan, replayed by hand, earns its value and takes at most one cycle
        net, sales, buys, deliv, acts = mr.battery_day(prices, 2)
        soc = cyc = cash = 0.0
        for a, p in zip(acts, prices):
            if a == 1:
                stored = min(eta, 2 - soc)
                soc, cash = soc + stored, cash - stored / eta * p
            elif a == -1:
                taken = min(1 / eta, soc, 2 - cyc)
                soc, cyc, cash = soc - taken, cyc + taken, cash + taken * eta * p
        self.assertAlmostEqual(cash, net, places=4)
        self.assertLessEqual(cyc, 2 + 1e-9)
        hrs = lambda a: [i for i, x in enumerate(acts) if x == a]
        print(f"\n  battery 2h, 2023-08-10: evening DP {dp[0]:.4f} = brute force {best:.4f}; the day: charge hours {hrs(1)}, discharge hours {hrs(-1)}, net {net:.4f} USD/MW")


@unittest.skipUnless(HAVE and os.path.exists(SNAP), "the warehouse tables are not on this machine")
class Snapshot(unittest.TestCase):
    def test_snapshot_equals_the_table(self):
        t = table("merchant_revenue_monthly")
        with open(SNAP, encoding="utf-8") as f:
            snap = json.load(f)
        n = 0
        for iso, s in snap["isos"].items():
            x = t[t["entity"] == f"{iso}:{s['hub']}"]
            by = {(r.ts_utc[:7], r.variable): r.value for r in x.itertuples()}
            for m, row in s["months"].items():
                self.assertAlmostEqual(row["flat"], by[(m, "flat_price")], places=4)
                for asset, v in row.items():
                    if not isinstance(v, dict):
                        continue
                    for k, val in v.items():
                        if val is None:
                            continue
                        self.assertAlmostEqual(val, by[(m, f"{asset}_{k}")], places=4, msg=f"{iso} {m} {asset}_{k}")
                        n += 1
        self.assertGreater(n, 3000)


class Rules(unittest.TestCase):
    def test_never_in_supabase(self):
        # Session 51 loaded nothing. Session 102 loads the table whole for Ask ERCOT (in review), on Samuel's instruction
        # of 4 October 2026: one rule, and no other mention of the table in the live set
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertEqual(live.count("merchant"), 1)
        self.assertIn("  - '^merchant_revenue_monthly$'", live)

    def test_units(self):
        v = src("warehouse", "validate", "erw_validate.py")
        self.assertIn('"USD/MW", "MWh/MW"', v)
        self.assertIn("34. **Session 51: USD/MW and MWh/MW.**", src("docs", "datastandard.md"))

    def test_defaults_trace_to_lazard(self):
        m = src("site", "lib", "merchant.ts")
        for k, capex, life in (("solar", 1375, 35), ("wind", 2100, 30), ("peaker", 1300, 30), ("battery_4h", 1110, 20)):
            self.assertRegex(m, rf"{k}: \{{ capex: {capex}, life: {life},")
        self.assertIn("share: 0.6, rate: 0.08", m)
        # Lazard's own illustration: 300 MW of wind at 1,900 USD/kW, 60 percent debt at 8 percent over 30 years: 30.4 million a year
        crf = 0.08 / (1 - 1.08 ** -30)
        self.assertAlmostEqual(300 * 1900e3 * 0.6 * crf / 1e6, 30.4, places=1)

    def test_questions_file(self):
        q = src("docs", "reviews", "nabihan-questions.md")
        self.assertEqual(len(re.findall(r"^\d+\. \*\*", q, flags=re.M)), 10)
        self.assertEqual(q.count("*Decides:*"), 10)
        self.assertNotIn("—", q)


if __name__ == "__main__":
    unittest.main()
