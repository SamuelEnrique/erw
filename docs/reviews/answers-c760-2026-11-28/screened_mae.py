"""Chain 760, five-tools data request 61: per forecast place, the hours of the last two years the forecast-error screen
takes out (x_screened 1), and the operator's mean absolute error with and without them.

Reads eia930_forecast_error_hourly (warehouse/output) and the places of site/data/predict/index.json. The window is the
forecast's last_2_years cut: the 730 days ending on scores.json's span last_day. Writes a CSV beside this script's
output and prints a summary.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date, timedelta

ROOT = r"C:\Users\Shared\Documents\erw"
sc = json.load(open(os.path.join(ROOT, "site", "data", "predict", "scores.json"), encoding="utf-8"))
last = date.fromisoformat(sc["span"]["demand"]["last_day"])
first = last - timedelta(days=729)
lo, hi = first.isoformat(), (last + timedelta(days=1)).isoformat()
idx = json.load(open(os.path.join(ROOT, "site", "data", "predict", "index.json"), encoding="utf-8"))
places = {}
for p in idx.get("places", []):
    pid = p.get("id") or p.get("place")
    code = p.get("eia930") or pid.split("-", 1)[1].upper()
    places["eia930:" + code] = pid
acc = defaultdict(lambda: {"n": 0, "n_scr": 0, "abs": 0.0, "abs_scr": 0.0, "dem": 0.0, "dem_scr": 0.0})
path = os.path.join(ROOT, "warehouse", "output", "eia930_forecast_error_hourly.csv")
with open(path, encoding="utf-8", newline="") as fh:
    rd = csv.reader(ln for ln in fh if not ln.startswith("#"))
    head = next(rd)
    ie, it, iv, idm, isc = (head.index(c) for c in ("entity", "ts_utc", "value", "x_demand_mw", "x_screened"))
    for r in rd:
        e = r[ie]
        if e not in places or not (lo <= r[it] < hi):
            continue
        a = acc[e]
        v = abs(float(r[iv]))
        d = float(r[idm]) if r[idm] else 0.0
        if r[isc] == "1":
            a["n_scr"] += 1
            a["abs_scr"] += v
            a["dem_scr"] += d
        else:
            a["n"] += 1
            a["abs"] += v
            a["dem"] += d
out = os.path.join(ROOT, "runs", "c760", "screened_mae.csv")
with open(out, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["place", "window", "hours_kept", "hours_screened", "operator_mae_mw_screened_out",
                "operator_mae_mw_put_back", "operator_mape_pct_screened_out", "operator_mape_pct_put_back"])
    rows = []
    for e, pid in sorted(places.items(), key=lambda kv: kv[1]):
        a = acc.get(e)
        if not a or not a["n"]:
            continue
        m0 = a["abs"] / a["n"]
        m1 = (a["abs"] + a["abs_scr"]) / (a["n"] + a["n_scr"])
        p0 = a["abs"] / a["dem"] * 100 if a["dem"] else None
        p1 = (a["abs"] + a["abs_scr"]) / (a["dem"] + a["dem_scr"]) * 100 if a["dem"] + a["dem_scr"] else None
        row = [pid, f"{lo}..{last.isoformat()}", a["n"], a["n_scr"], round(m0, 1), round(m1, 1),
               round(p0, 2) if p0 else None, round(p1, 2) if p1 else None]
        w.writerow(row)
        rows.append(row)
print(f"window {lo}..{last.isoformat()}; {len(rows)} places; places with any hour screened: "
      f"{sum(1 for r in rows if r[3])}")
for r in sorted(rows, key=lambda r: -r[3])[:12]:
    print(r)
