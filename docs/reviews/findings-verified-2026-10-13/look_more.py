"""Session 252: three looks the verdicts need, from today's tables (no request to any publisher).
  1. DC industrial: the sales and the revenue behind the price of July 2026 (a price is revenue over sales).
  2. Cleveland regular gasoline: the weeks before the flagged fall.
  3. CFTC natural gas managed money long: why the history compared begins in 2022, and the weeks around the flag."""
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "warehouse", "output")


def table(name):
    return pd.read_csv(os.path.join(OUT, name + ".csv"), comment="#", dtype=str, keep_default_na=False)


pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 60)
for name in ("eia_retail_sales_monthly", "eia_retail_electricity_prices"):
    t = table(name)
    print(name, "columns:", list(t.columns))
    d = t[t["entity"].str.contains(":DC:IND")]
    print("variables for DC:IND:", sorted(d["variable"].unique()), "units:", sorted(d["unit"].unique()) if "unit" in d else "")
    for var, g in d.groupby("variable"):
        g = g.sort_values("ts_utc")
        print(f"  {var}: last 14 months")
        print("   ", [(r.ts_utc[:7], r.value) for r in g.tail(14).itertuples()])
        v = pd.to_numeric(g["value"])
        print(f"   all months: n {len(v)}, median {v.median()}, min {v.min()}, max {v.max()}")
    if name == "eia_retail_sales_monthly":
        for st in ("UT:RES", "IN:COM"):
            g = t[t["entity"].str.endswith(st) & (t["variable"] == "retail_sales")].sort_values("ts_utc")
            print(f"  {st} retail_sales unit {sorted(g['unit'].unique())}: last 4:", [(r.ts_utc[:7], r.value) for r in g.tail(4).itertuples()])
        # how DC:IND sales compare with the other DC sectors
        g = t[t["entity"].str.contains(":DC:") & (t["variable"] == "retail_sales") & t["ts_utc"].str.startswith("2026-07")]
        print("  DC, July 2026, sales by sector:", [(r.entity, r.value, r.unit) for r in g.itertuples()])
    else:
        g = t[t["entity"].str.endswith("IA:IND")].sort_values("ts_utc")
        print("  IA:IND price unit", sorted(g["unit"].unique()), "last 4:", [(r.ts_utc[:7], r.value) for r in g.tail(4).itertuples()])

t = table("eia_regional_retail_fuel_prices")
g = t[(t["entity"] == "eia:EMM_EPMR_PTE_YCLE_DPG")].sort_values("ts_utc")
print("Cleveland regular gasoline, columns", list(t.columns))
print("  unit", sorted(g["unit"].unique()), "node", sorted(g["node"].unique()) if "node" in g else "")
print("  last 12 weeks:", [(r.ts_utc[:10], r.value) for r in g.tail(12).itertuples()])
v = pd.to_numeric(g["value"]).reset_index(drop=True)
ch = v.diff()
top = ch.abs().sort_values(ascending=False).head(6).index
print("  six largest weekly changes held:", [(g["ts_utc"].iloc[i][:10], round(float(ch[i]), 3)) for i in top])
# the same week in the other cities and regions of the table
last2 = sorted(t["ts_utc"].unique())[-2:]
w = t[t["ts_utc"].isin(last2) & (t["variable"] == "retail_price") & t["entity"].str.contains("EPMR_")]
p = w.assign(value=pd.to_numeric(w["value"])).pivot_table(index=["entity", "node"] if "node" in w else ["entity"], columns="ts_utc", values="value")
p["change"] = p[last2[1]] - p[last2[0]]
print("  regular gasoline, every place of the table, the same week:")
print(p.sort_values("change").to_string())

t = table("cftc_cot_positions")
print("CFTC columns", list(t.columns))
g = t[(t["entity"] == "cftc:023651") & (t["variable"] == "managed_money_long")].sort_values("ts_utc")
print("  rows", len(g), "first", g["ts_utc"].iloc[0][:10], "last", g["ts_utc"].iloc[-1][:10], "sources:", [(s, x["ts_utc"].min()[:10], x["ts_utc"].max()[:10]) for s, x in g.groupby("source")] if "source" in g else "")
print("  nodes:", [(s, x["ts_utc"].min()[:10], x["ts_utc"].max()[:10], len(x)) for s, x in g.groupby("node")] if "node" in g else "")
print("  last 8 weeks:", [(r.ts_utc[:10], r.value) for r in g.tail(8).itertuples()])
for var in ("managed_money_short", "open_interest"):
    h = t[(t["entity"] == "cftc:023651") & (t["variable"] == var)].sort_values("ts_utc")
    if len(h):
        print(f"  {var}, last 4 weeks:", [(r.ts_utc[:10], r.value) for r in h.tail(4).itertuples()])
print("  variables:", sorted(t[t["entity"] == "cftc:023651"]["variable"].unique()))

t = table("caiso_as_prices")
g = t[(t["entity"] == "caiso:AS_CAISO_EXP") & (t["variable"] == "as_price_dam_nr")]
print("CAISO AS: unit", sorted(g["unit"].unique()), "columns", list(t.columns))
d = g.assign(day=g["ts_utc"].str[:10], value=pd.to_numeric(g["value"])).groupby("day")["value"].agg(["mean", "max", "count"])
print("  the six dearest days held (UTC day mean):")
print(d.sort_values("mean", ascending=False).head(6).to_string())
sys.exit(0)
