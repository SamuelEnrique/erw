"""Audit of Automated Analysis (session 10204): four weekly templates and one watch line re-done by hand for 2026-W44.

From the main checkout's tables (read only) and the template's method in words, not its code:
  watch_wti: WTI at Cushing (eia_fuel_spot_prices, eia:wti_cushing), weekly mean Monday to Sunday UTC with at least 4
    days, the change from the week before, ranked among the last 104 earlier changes (share smaller), and how many as large;
  peak_premium_block, ERCOT HB_NORTH: median 15-minute real-time price at peak (16:00 to 20:59 Central) minus the median
    at midday (12:00 to 15:59) over the 7 local days of the headline period (iso_rtm_hub_prices);
  curtailment_midday: CAISO's local plus system wind and solar curtailed, summed over the headline's 7 days
    (caiso_curtailment_daily);
  negative_price_hours, ERCOT HB_WEST: hours of September 2026 (Central) whose mean real-time price was below zero;
  storage_evening_peak: mean CAISO battery output 17:00 to 21:00 Pacific over the headline's 7 days (caiso_battery_storage).
Each set beside the figure in docs/analysis/2026-W44/results.json.

Run: python runs/a11_weekly_templates.py <repo root> <folder of the tables> > runs/a11.out
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT, D = sys.argv[1], sys.argv[2]
RES = json.load(open(os.path.join(ROOT, "docs", "analysis", "2026-W44", "results.json"), encoding="utf-8"))["results"]
HEAD = {r["template"]: r["headline"] for r in RES}


def read(table, keep):
    path = os.path.join(D, table + ".csv")
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    parts = []
    for ch in pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value", "market", "node"], dtype=str, chunksize=500_000):
        ch = ch[keep(ch)]
        if len(ch):
            parts.append(ch)
    d = pd.concat(parts, ignore_index=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d.dropna(subset=["value"])


def span(period):
    a, b = period.split(" to ")
    return pd.Timestamp(a), pd.Timestamp(b)


def wti():
    d = read("eia_fuel_spot_prices", lambda c: c["entity"] == "eia:wti_cushing")
    d = d[d["ts"] < pd.Timestamp("2026-10-26", tz="UTC")]
    d["monday"] = (d["ts"].dt.tz_localize(None).dt.normalize() - pd.to_timedelta(d["ts"].dt.dayofweek, unit="D"))
    w = d.groupby("monday")["value"].agg(["mean", "size"])
    w = w[w["size"] >= 4]["mean"]
    deltas = w.diff().dropna()
    dlt = float(deltas.iloc[-1])
    earlier = deltas.iloc[:-1].tail(104).to_numpy()
    score = 100 * float((np.abs(earlier) < abs(dlt)).mean())
    big = int((np.abs(earlier) >= abs(dlt)).sum())
    print(f"watch_wti: week of {w.index[-1].date()}: {round(w.iloc[-1], 2)} (file {HEAD['watch_wti']['value']}), before {round(w.iloc[-2], 2)}, "
          f"change {dlt:.4f}; ranked among {len(earlier)}: score {score:.1f}, as large {big} (caption: 87.5, 13 of 104)")


def peak():
    h = HEAD["peak_premium_block"]
    a, b = span(h["period"])
    d = read("iso_rtm_hub_prices", lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_NORTH"))
    loc = d["ts"].dt.tz_convert("America/Chicago")
    day = loc.dt.tz_localize(None).dt.normalize()
    d = d[(day >= a) & (day <= b)]
    hr = d["ts"].dt.tz_convert("America/Chicago").dt.hour
    pk = float(np.percentile(d.loc[(hr >= 16) & (hr < 21), "value"], 50))
    md = float(np.percentile(d.loc[(hr >= 12) & (hr < 16), "value"], 50))
    print(f"peak_premium_block ERCOT HB_NORTH {h['period']}: intervals {len(d)}; peak median {pk:.4f} minus midday median {md:.4f} = {pk - md:.2f} (file {h['value']})")


def curtail():
    h = HEAD["curtailment_midday"]
    a, b = span(h["period"])
    v = ["curtailed_solar_local_mwh", "curtailed_solar_system_mwh", "curtailed_wind_local_mwh", "curtailed_wind_system_mwh"]
    d = read("caiso_curtailment_daily", lambda c: c["variable"].isin(v))
    day = d["ts"].dt.tz_localize(None).dt.normalize()
    s = float(d.loc[(day >= a) & (day <= b), "value"].sum())
    print(f"curtailment_midday {h['period']}: {s:.2f} MWh (file {h['value']})")


def negative():
    h = HEAD["negative_price_hours"]
    d = read("iso_rtm_hub_prices", lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_WEST"))
    d["hour"] = d["ts"].dt.floor("h")
    hm = d.groupby("hour")["value"].mean()
    loc = hm.index.tz_convert("America/Chicago")
    m = hm[(loc.year == 2026) & (loc.month == 9)]
    print(f"negative_price_hours ERCOT HB_WEST {h['period']}: hours held {len(m)}, below zero {int((m < 0).sum())} (file {h['value']})")


def storage():
    h = HEAD["storage_evening_peak"]
    a, b = span(h["period"])
    d = read("caiso_battery_storage", lambda c: c["variable"] == "batteries_mw")
    loc = d["ts"].dt.tz_convert("America/Los_Angeles")
    day = loc.dt.tz_localize(None).dt.normalize()
    d = d[(day >= a) & (day <= b) & (loc.dt.hour >= 17) & (loc.dt.hour < 21)]
    print(f"storage_evening_peak {h['period']}: intervals {len(d)}, mean {d['value'].mean():.1f} MW (file {h['value']}); "
          f"with 21:00 to 21:59 as well: see the method's words '17:00 to 21:00'")


if __name__ == "__main__":
    for fn in (wti, peak, curtail, negative, storage):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            print(f"{fn.__name__}: not computed here: {type(exc).__name__}: {exc}")
