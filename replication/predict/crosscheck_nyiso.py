"""Chain 730 part F, the cross-check's second place (session 10602): NYISO's market monitor (Potomac Economics,
Quarterly Report on the New York ISO Electricity Markets, Third Quarter of 2025, slide 26, "Load Forecast and Actual
Load", fetched 27 November 2026) prints the day-ahead peak load forecast's error by quarter: the mean of the day's
forecast peak less the real-time peak, and its mean absolute value, in MW. Beside it, the same from the backtest: the
operator's day-ahead forecast as filed on Form EIA-930 for NYIS (eia930_forecast_error_hourly) and NYIS's demand
(eia930_ba_demand_hourly), each local day's highest hour, over the days every hour of both is held.
Usage: python crosscheck_nyiso.py   (reads the warehouse through warehouse/predict's readers; writes crosscheck_nyiso.csv)"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "..", "warehouse", "predict"))
import numpy as np
import pandas as pd
import predict_data as data
import predict_demand as demand

PRINTED = {"2024Q3": (-180, 479), "2025Q2": (-124, 375), "2025Q3": (-124, 448)}   # (mean DA - RT, mean absolute), MW

dem = data.demand_panel()["ba-nyis"].dropna()
op = data.operator_panel()["ba-nyis"]
tz = "America/New_York"
f = demand.local_frame(dem, tz)
f["operator"] = op.reindex(pd.DatetimeIndex(f["ts"])).to_numpy()
whole = f.groupby("day")[["operator", "value"]].apply(lambda g: len(g) >= 23 and g["operator"].notna().all() and g["value"].notna().all())
f = f[f["day"].isin(whole[whole].index)]
pk = f.groupby("day").agg(actual=("value", "max"), forecast=("operator", "max"))
pk["err"] = pk["forecast"] - pk["actual"]
pk["q"] = pd.PeriodIndex(pk.index, freq="Q").astype(str).str.replace("Q", "Q")
out = []
print("| Quarter | Potomac: mean DA - RT, mean absolute (MW) | Backtest of the EIA-930 filing: mean, mean absolute (MW) | Days |")
print("|---|---|---|---:|")
for q, (m, a) in PRINTED.items():
    g = pk[pk["q"] == q]
    bm, ba = (round(float(g["err"].mean())), round(float(g["err"].abs().mean()))) if len(g) else (None, None)
    out.append([q, m, a, bm, ba, len(g)])
    print(f"| {q} | {m}, {a} | {bm}, {ba} | {len(g)} |")
with open(os.path.join(HERE, "crosscheck_nyiso.csv"), "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["quarter", "potomac_mean_mw", "potomac_mean_abs_mw", "eia930_mean_mw", "eia930_mean_abs_mw", "days"])
    w.writerows(out)
