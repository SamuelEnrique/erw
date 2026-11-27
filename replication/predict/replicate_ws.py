#!/usr/bin/env python3
"""Replication of the ERW forecast of wind and solar output (site/data/predict/wind_solar.json), chain 730, part F.
Written from docs/methods/predict_wind_solar.md, not from warehouse/predict/: it imports nothing of the builder. Every
figure of the file's score rows (hours, mean absolute error in MW, the error over the mean output in percent, for every
place, fuel, method and cut) is recomputed from the public tables: eia930_region_fuel_hourly, caiso_wind_solar_forecast,
ercot_wind_solar_forecast and caiso_curtailment_intervals. The three methods are rebuilt here, the regression refitted
for every target day by numpy.linalg.lstsq on its own window.
Prints N of N, names every difference, writes replication/predict/figures_ws.csv.
    python replication/predict/replicate_ws.py --tables DIR [--file site/data/predict/wind_solar.json]
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIRST = pd.Timestamp("2019-07-01")
H, FIT, MIN_FIT, CHOICE = 2, 365, 120, 730
TZ = {"region-cal": "America/Los_Angeles", "region-nw": "America/Los_Angeles", "region-sw": "America/Phoenix",
      "region-cent": "America/Chicago", "region-midw": "America/Chicago", "region-tex": "America/Chicago",
      "region-ten": "America/Chicago", "region-car": "America/New_York", "region-fla": "America/New_York",
      "region-mida": "America/New_York", "region-ne": "America/New_York", "region-ny": "America/New_York",
      "region-se": "America/Chicago", "grid-caiso": "America/Los_Angeles"}


def read(path, cols):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    with open(path, "rb") as fh:
        for _ in range(n):
            fh.readline()
        d = pd.read_csv(fh, usecols=cols, engine="pyarrow")
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def one_series(g):
    s = pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index()
    return s[~s.index.duplicated(keep="last")]


def hub_sum(c, var, need):
    w = c[c["variable"] == var].pivot_table(index="ts", columns="entity", values="value", aggfunc="last")
    return w.sum(axis=1, min_count=need)


def curtailed(tables):
    d = read(os.path.join(tables, "caiso_curtailment_intervals.csv"), ["variable", "ts_utc", "value", "freq"])
    out = {}
    for fuel in ("wind", "solar"):
        g = d[d["variable"].str.startswith(f"curtailed_{fuel}_")]
        a = g[g["freq"] == "PT5M"].groupby(g.loc[g["freq"] == "PT5M", "ts"].dt.floor("h"))["value"].sum() / 12.0
        b = g[g["freq"] == "PT1H"].groupby("ts")["value"].sum()
        s = pd.concat([a, b]).groupby(level=0).sum()
        days = set(g.loc[g["freq"] == "P1D", "ts"].dt.strftime("%Y-%m-%d"))
        out[fuel] = (s, days)
    return out


def local(s, tz):
    s = s.dropna()
    loc = s.index.tz_convert(tz)
    return pd.DataFrame({"ts": s.index, "value": s.to_numpy(float), "day": loc.tz_localize(None).normalize(), "hour": loc.hour})


def last_whole(f, tz):
    for day in sorted(f["day"].unique())[::-1][:10]:
        day = pd.Timestamp(day)
        a = day.tz_localize(tz).tz_convert("UTC")
        b = (day + pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC")
        if int((f["day"] == day).sum()) >= int((b - a) / pd.Timedelta(hours=1)):
            return day
    return None


def methods(f, tz):
    last = last_whole(f, tz)
    f = f[f["day"] <= last]
    M = f.groupby(["day", "hour"])["value"].mean().unstack("hour").reindex(columns=range(24))
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=H), freq="D"))
    raw = M.to_numpy(float)
    n = len(raw)
    fl = raw.copy()
    gap = np.isnan(raw[:, 1:23]) & np.isfinite(raw[:, :22]) & np.isfinite(raw[:, 2:])
    fl[:, 1:23] = np.where(gap, (raw[:, :22] + raw[:, 2:]) / 2.0, raw[:, 1:23])

    def back(d):
        o = np.full_like(fl, np.nan)
        o[d:] = fl[:n - d]
        return o
    A = back(H)
    am = np.repeat(np.mean(A, axis=1)[:, None], 24, axis=1)
    s7 = np.stack([back(H + j) for j in range(7)])
    p7 = np.where(np.isfinite(s7).all(axis=0), s7.mean(axis=0), np.nan)
    s14 = np.stack([back(H + j) for j in range(14)])
    env = np.where(np.isfinite(s14).sum(axis=0) >= 10, np.nanmax(np.where(np.isfinite(s14), s14, -np.inf), axis=0), np.nan)
    X = np.stack([np.ones_like(A), A, am, p7, env], axis=2)
    ok = np.isfinite(X).all(axis=2) & np.isfinite(raw)
    R = np.full((n, 24), np.nan)
    for i in range(H, n):
        j1 = i - H + 1
        j0 = max(0, j1 - FIT)
        for k in range(24):
            v = ok[j0:j1, k]
            if v.sum() < MIN_FIT or not np.isfinite(X[i, k]).all():
                continue
            beta = np.linalg.lstsq(X[j0:j1, k][v], raw[j0:j1, k][v], rcond=None)[0]
            R[i, k] = max(0.0, float(X[i, k] @ beta))
    pos = pd.Series(np.arange(n), index=M.index)
    g = f[f["day"] >= FIRST].copy()
    i = pos.reindex(g["day"]).to_numpy()
    k = g["hour"].to_numpy()
    g = g.rename(columns={"value": "actual"})
    g["yesterday"], g["profile7"], g["regression"] = A[i, k], p7[i, k], R[i, k]
    return g.reset_index(drop=True)


def score(x, m):
    if not len(x):
        return 0, None, None
    e = (x[m] - x["actual"]).abs()
    mean = x["actual"].mean()
    return int(len(x)), round(float(e.mean()), 1), (round(float(e.mean() / mean * 100), 2) if mean > 0 else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "wind_solar.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    cols = doc["rows_columns"]
    shown = {(r[0], r[1], r[2], r[3], r[4]): dict(zip(cols, r)) for r in doc["rows"]}
    rf = read(os.path.join(a.tables, "eia930_region_fuel_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
    c = read(os.path.join(a.tables, "caiso_wind_solar_forecast.csv"), ["entity", "variable", "ts_utc", "value"])
    e = read(os.path.join(a.tables, "ercot_wind_solar_forecast.csv"), ["entity", "variable", "ts_utc", "value"])
    cu = curtailed(a.tables)
    # session 10603 (method note section 8): the authorities' output, eia930_ba_wind_solar_hourly, on each authority's clock
    bt, tzs = None, dict(TZ)
    if any(p["place"].startswith("ba-") for p in doc["places"]):
        bt = read(os.path.join(a.tables, "eia930_ba_wind_solar_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
        sys.path.append(os.path.join(ROOT, "warehouse", "connectors"))
        sys.path.append(os.path.join(ROOT, "warehouse", "derived"))
        import region_files as rfiles
        rfiles.ROOT = os.path.abspath(os.path.join(a.tables, "..", ".."))
        ref, _ = rfiles.reference()
        for p in doc["places"]:
            if p["place"].startswith("ba-"):
                code = p["place"].split("-")[1].upper()
                tzs[p["place"]] = rfiles.BA_TZ.get(code) or (ref[code]["tz"] if code in ref and ref[code]["tz"] else "America/New_York")
    figs = []
    for p in doc["places"]:
        place = p["place"]
        for fuel in ("wind", "solar"):
            if p["fuels"][fuel]["status"] != "shown":
                continue
            if place == "grid-caiso":
                act = hub_sum(c, f"{fuel}_actual_mw", 3 if fuel == "solar" else 2)
                op = hub_sum(c, f"{fuel}_forecast_dam_mw", 3 if fuel == "solar" else 2)
            elif place.startswith("ba-"):
                code = place.split("-")[1].upper()
                act = one_series(bt[(bt["entity"] == f"eia930:{code}") & (bt["variable"] == f"net_generation_{fuel}_mw")])
                op = None
            else:
                code = place.split("-")[1].upper()
                act = one_series(rf[(rf["entity"] == f"eia930:{code}") & (rf["variable"] == f"net_generation_{fuel}_mw")])
                op = one_series(e[(e["entity"] == "ercot:SYSTEM") & (e["variable"] == f"{fuel}_forecast_24h_mw")]) if place == "region-tex" else None
            g = methods(local(act, tzs[place]), tzs[place])
            g["operator"] = op.reindex(pd.DatetimeIndex(g["ts"])).to_numpy() if op is not None else np.nan
            last = g["day"].max()
            rec = g[g["day"] > last - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "profile7", "regression"])
            maes = {m: score(rec, m)[1] for m in ("yesterday", "profile7", "regression")}
            raw = {m: float((rec[m] - rec["actual"]).abs().mean()) for m in ("yesterday", "profile7", "regression")}
            g["erw"] = g[min((v, m) for m, v in raw.items())[1]]   # the unrounded error (session 10603)
            ms = ["erw", "yesterday", "profile7", "regression"]
            cc = g.dropna(subset=["actual"] + ms).reset_index(drop=True)
            r2 = cc["day"] > cc["day"].max() - pd.Timedelta(days=CHOICE)
            cuts = {("all", ""): np.ones(len(cc), bool), ("last_2_years", ""): r2.to_numpy()}
            mo = cc["day"].dt.strftime("%Y-%m")
            for m_ in sorted(mo.unique()):
                cuts[("month", m_)] = (mo == m_).to_numpy()
            for h in range(24):
                cuts[("hour", str(h))] = (r2 & (cc["hour"] == h)).to_numpy()
            sets = [(cc, cuts, ms)]
            if op is not None:
                co = g.dropna(subset=["actual", "operator"] + ms).reset_index(drop=True)
                mo2 = co["day"].dt.strftime("%Y-%m")
                cuts2 = {("with_operator", ""): np.ones(len(co), bool)}
                for m_ in sorted(mo2.unique()):
                    cuts2[("with_operator_month", m_)] = (mo2 == m_).to_numpy()
                sets.append((co, cuts2, ms + ["operator"]))
                if place == "grid-caiso":
                    s, days = cu[fuel]
                    lday = co["ts"].dt.tz_convert("America/Los_Angeles").dt.strftime("%Y-%m-%d")
                    add = s.reindex(pd.DatetimeIndex(co["ts"])).fillna(0.0).to_numpy()
                    known = lday.isin(days).to_numpy() | np.isfinite(s.reindex(pd.DatetimeIndex(co["ts"])).to_numpy())
                    ca = co.assign(actual=co["actual"].to_numpy() + add)[known].reset_index(drop=True)
                    sets.append((ca, {("with_operator_available", ""): np.ones(len(ca), bool)}, ms + ["operator"]))
            for x, cl, mm in sets:
                for (cut, key), msk in cl.items():
                    for m in mm:
                        n, mae, nmae = score(x[msk], m)
                        r = shown.get((place, fuel, m, cut, key))
                        ok = r is not None and r["hours"] == n and (mae is None or abs(r["mae_mw"] - mae) <= 0.11) and \
                            (nmae is None or (r["nmae_pct"] is not None and abs(r["nmae_pct"] - nmae) <= 0.011))
                        figs.append((f"{place}.{fuel}.{m}.{cut}.{key}", None if r is None else (r["hours"], r["mae_mw"], r["nmae_pct"]), (n, mae, nmae), ok))
            mine = sum(1 for f_ in figs if f_[0].startswith(f"{place}.{fuel}.") and f_[3])
            alln = sum(1 for f_ in figs if f_[0].startswith(f"{place}.{fuel}."))
            print(f"{place} {fuel}: {mine} of {alln} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_ws.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for f_ in figs if f_[3])
    print(f"wind and solar: {ok} of {len(figs)} figures equal")
    for f_ in [f_ for f_ in figs if not f_[3]][:40]:
        print("  differs:", f_)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
