"""Predict data request 7 (chain 730's questions to window A): read EIA-930's own six-month BALANCE files, independently of
the connectors, and say for each of the seven breaks whether EIA's published day-ahead forecast (the files' "Demand
Forecast (MW)") shows the same level against demand as the warehouse's eia930_forecast_error_hourly, or departs from it.

For each balancing authority named: by month, the sum of the forecast over the sum of demand on the hours that hold both,
(1) in EIA's file against its reported demand, (2) in EIA's file against its adjusted demand, (3) in the warehouse table
(x_forecast_mw over x_demand_mw, unscreened hours). And for PJM, the mean absolute percentage error of the forecast against
the demand of the same hour and of the hour after its stamp, from EIA's file. Files: the newest saved copy of each of
EIA930_BALANCE_2018_Jul_Dec to 2026_Jul_Dec in warehouse/raw (no request). Prints a table and writes the CSV beside it."""
import csv
import glob
import os
import sys
from collections import defaultdict

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

BAS = ["SWPP", "FPC", "PSCO", "FMPP", "SRP", "CISO", "PJM"]
files = {}
for p in glob.glob("warehouse/raw/**/*EIA930_BALANCE_20*.csv", recursive=True):
    name = "EIA930" + p.split("EIA930", 1)[1]
    if name not in files or os.path.getmtime(p) > os.path.getmtime(files[name]):
        files[name] = p
eia = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])   # (ba, month) -> [forecast on reported, reported, forecast on adjusted, adjusted]
pjm = []
for name in sorted(files):
    d = pd.read_csv(files[name], dtype=str, usecols=["Balancing Authority", "UTC Time at End of Hour", "Demand Forecast (MW)",
                                                        "Demand (MW)", "Demand (MW) (Adjusted)"], thousands=",")
    d = d[d["Balancing Authority"].isin(BAS)].copy()
    t = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p") - pd.Timedelta(hours=1)   # the hour's start
    d["month"] = t.dt.strftime("%Y-%m")
    d["t"] = t
    for c in ("Demand Forecast (MW)", "Demand (MW)", "Demand (MW) (Adjusted)"):
        d[c] = pd.to_numeric(d[c].str.replace(",", ""), errors="coerce")
    for (ba, m), g in d.groupby(["Balancing Authority", "month"]):
        a = g.dropna(subset=["Demand Forecast (MW)", "Demand (MW)"])
        a = a[a["Demand (MW)"] > 0]
        b = g.dropna(subset=["Demand Forecast (MW)", "Demand (MW) (Adjusted)"])
        b = b[b["Demand (MW) (Adjusted)"] > 0]
        r = eia[(ba, m)]
        r[0] += a["Demand Forecast (MW)"].sum(); r[1] += a["Demand (MW)"].sum()
        r[2] += b["Demand Forecast (MW)"].sum(); r[3] += b["Demand (MW) (Adjusted)"].sum()
    p = d[d["Balancing Authority"] == "PJM"].sort_values("t").drop_duplicates("t").set_index("t")
    pjm.append(p[["Demand Forecast (MW)", "Demand (MW) (Adjusted)", "month"]])
# the warehouse's table
wh = defaultdict(lambda: [0.0, 0.0])
p = "warehouse/output/eia930_forecast_error_hourly.csv"
for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=500_000,
                      usecols=["entity", "ts_utc", "x_forecast_mw", "x_demand_mw", "x_screened"]):
    ch = ch[ch["entity"].isin([f"eia930:{b}" for b in BAS]) & (ch["x_screened"] != "1")]
    ch = ch[(ch["x_forecast_mw"] != "") & (ch["x_demand_mw"] != "")]
    ch["m"] = ch["ts_utc"].str[:7]
    ch["f"] = ch["x_forecast_mw"].astype(float)
    ch["d"] = ch["x_demand_mw"].astype(float)
    for (e, m), g in ch.groupby(["entity", "m"]):
        w = wh[(e.split(":")[1], m)]
        w[0] += g["f"].sum(); w[1] += g["d"].sum()
rows = []
for (ba, m) in sorted(set(eia) | set(wh)):
    r, w = eia.get((ba, m)), wh.get((ba, m))
    rows.append({"ba": ba, "month": m,
                 "eia_forecast_over_reported_pct": round(100 * r[0] / r[1], 1) if r and r[1] else "",
                 "eia_forecast_over_adjusted_pct": round(100 * r[2] / r[3], 1) if r and r[3] else "",
                 "warehouse_forecast_over_demand_pct": round(100 * w[0] / w[1], 1) if w and w[1] else ""})
out = "docs/reviews/answers-c701-2026-11-26/predict_row7_eia930_forecast_levels.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
df = pd.DataFrame(rows)


def show(ba, since, until="9999"):
    x = df[(df.ba == ba) & (df.month >= since) & (df.month <= until)]
    print(f"{ba} {since} to {x.month.max()}: EIA's file (forecast over reported demand) {x.eia_forecast_over_reported_pct.tolist()}")
    print(f"   warehouse {x.warehouse_forecast_over_demand_pct.tolist()}")


show("SWPP", "2025-01", "2025-12")
show("FPC", "2019-01", "2019-06")
show("FPC", "2026-01")
show("PSCO", "2025-10")
show("FMPP", "2026-01", "2026-08")
show("SRP", "2026-01")
show("CISO", "2026-01")
# PJM: the forecast against the same hour's demand and the hour after
q = pd.concat(pjm).sort_index()
q = q[~q.index.duplicated()]
f, dem = q["Demand Forecast (MW)"], q["Demand (MW) (Adjusted)"]
nxt = dem.shift(-1, freq="h").reindex(q.index)
ok = f.notna() & dem.notna() & nxt.notna() & (dem > 0)
for label, since in (("all", "2018"), ("2026", "2026")):
    k = ok & (q.index.strftime("%Y") >= since)
    same = ((f[k] - dem[k]).abs() / dem[k]).mean() * 100
    after = ((f[k] - nxt[k]).abs() / nxt[k]).mean() * 100
    print(f"PJM ({label}): MAPE against the same hour {same:.2f} percent, against the hour after {after:.2f} percent, {int(k.sum())} hours")
print("written", out)
