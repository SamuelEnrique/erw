#!/usr/bin/env python3
"""Replication of the ERW forecast of the real-time hub price (site/data/predict/rt_price.json), chain 730, part F.
Written from docs/methods/predict_price.md, sections 7 and 8 (the longer backtest, session 10603), not from warehouse/predict/: it imports nothing of the builder.
Every figure of the file's score rows (hours, mean absolute error, MAPE over hours of at least 5 USD/MWh, for every
hub, method and cut) is recomputed from the public price tables, the regression refitted for every target day.
    python replication/predict/replicate_rt.py --tables DIR [--file site/data/predict/rt_price.json]
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
LONG = pd.Timestamp("2016-01-01")   # section 8: the longer backtest
H, FIT, MIN_FIT, CHOICE, FLOOR, SPIKE = 2, 730, 300, 730, 5.0, 0.99
TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history_2018", "iso_hub_prices_history", "iso_dam_hub_prices"]
HUBS = {"ercot": ("ercot:HB_NORTH", "America/Chicago"), "spp": ("spp:SPPNORTH_HUB", "America/Chicago"),
        "caiso": ("caiso:TH_SP15_GEN-APND", "America/Los_Angeles")}


def read(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    with open(path, "rb") as fh:
        for _ in range(n):
            fh.readline()
        d = pd.read_csv(fh, usecols=["entity", "ts_utc", "value", "market"], engine="pyarrow")
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def prices(tables):
    """{grid: (real-time hourly Series, day-ahead hourly Series)}: later tables win for the same interval."""
    frames = []
    for order, t in enumerate(TABLES):
        d = read(os.path.join(tables, t + ".csv"))
        d = d[d["entity"].isin([v[0] for v in HUBS.values()])]
        d["order"] = order
        frames.append(d)
    d = pd.concat(frames).sort_values(["entity", "market", "ts", "order"]).drop_duplicates(["entity", "market", "ts"], keep="last")
    out = {}
    for grid, (ent, _) in HUBS.items():
        g = d[d["entity"] == ent]
        rt = g[g["market"].astype(str).str.endswith("_rtm")]
        a = rt.groupby(rt["ts"].dt.floor("h"))["value"].agg(["mean", "size"])
        da = g[g["market"].astype(str).str.endswith("_dam")].set_index("ts")["value"]
        out[grid] = (a["mean"].where(a["size"] == 4).dropna(), da)
    return out


def by_day(s, tz):
    loc = s.index.tz_convert(tz)
    f = pd.DataFrame({"ts": s.index, "v": s.to_numpy(float), "day": loc.tz_localize(None).normalize(), "hour": loc.hour})
    return f


def build(rt, da, tz, first=FIRST):
    f = by_day(rt, tz)
    for day in sorted(f["day"].unique())[::-1][:10]:
        day = pd.Timestamp(day)
        a = day.tz_localize(tz).tz_convert("UTC")
        b = (day + pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC")
        if int((f["day"] == day).sum()) >= int((b - a) / pd.Timedelta(hours=1)):
            last = day
            break
    f = f[f["day"] <= last]
    M = f.groupby(["day", "hour"])["v"].mean().unstack("hour").reindex(columns=range(24))
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=H), freq="D"))
    g = by_day(da, tz)
    D = g.groupby(["day", "hour"])["v"].mean().unstack("hour").reindex(columns=range(24)).reindex(M.index).to_numpy(float)
    R = M.to_numpy(float)
    n = len(R)

    def back(a, k):
        o = np.full_like(a, np.nan)
        o[k:] = a[:n - k]
        return o
    S = R - D
    s7 = np.stack([back(S, H + j) for j in range(7)])
    s7m = np.where(np.isfinite(s7).sum(axis=0) >= 5, np.nanmean(np.where(np.isfinite(s7), s7, np.nan), axis=0), np.nan)
    X = np.stack([np.ones_like(D), D, back(S, H), s7m], axis=2)
    ok = np.isfinite(X).all(axis=2) & np.isfinite(R)
    P = np.full((n, 24), np.nan)
    for i in range(H, n):
        j1 = i - H + 1
        j0 = max(0, j1 - FIT)
        for k in range(24):
            v = ok[j0:j1, k]
            if v.sum() < MIN_FIT or not np.isfinite(X[i, k]).all():
                continue
            P[i, k] = float(X[i, k] @ np.linalg.lstsq(X[j0:j1, k][v], R[j0:j1, k][v], rcond=None)[0])
    pos = pd.Series(np.arange(n), index=M.index)
    x = f[f["day"] >= first].rename(columns={"v": "actual"}).copy()
    i = pos.reindex(x["day"]).to_numpy()
    k = x["hour"].to_numpy()
    x["yesterday"], x["regression"], x["day_ahead"] = back(R, H)[i, k], P[i, k], D[i, k]
    return x.reset_index(drop=True)


def score(x, m):
    if not len(x):
        return 0, None, None
    e = (x[m] - x["actual"]).abs()
    a = x["actual"].abs()
    keep = a >= FLOOR
    return int(len(x)), round(float(e.mean()), 2), (round(float((e[keep] / a[keep]).mean() * 100), 3) if keep.any() else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "rt_price.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    cols = doc["rows_columns"]
    shown = {(r[0], r[2], r[3], r[4]): dict(zip(cols, r)) for r in doc["rows"]}
    pr = prices(a.tables)
    figs = []
    for grid, (ent, tz) in HUBS.items():
        xl = build(*pr[grid], tz, first=LONG)
        x = xl[xl["day"] >= FIRST].reset_index(drop=True)
        last = x["day"].max()
        rec = x[x["day"] > last - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "regression", "day_ahead"])
        maes = {m: score(rec, m)[1] for m in ("yesterday", "regression")}
        x["erw"] = x[min((v, m) for m, v in maes.items())[1]]
        ms = ["erw", "day_ahead", "yesterday", "regression"]
        c = x.dropna(subset=["actual"] + ms).reset_index(drop=True)
        r2 = (c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE)).to_numpy()
        cuts = {("all", ""): np.ones(len(c), bool), ("last_2_years", ""): r2}
        mo = c["day"].dt.strftime("%Y-%m").to_numpy()
        for m_ in sorted(set(mo)):
            cuts[("month", m_)] = mo == m_
        for h in range(24):
            cuts[("hour", str(h))] = r2 & (c["hour"].to_numpy() == h)
        top = set(c.groupby("day")["actual"].max().dropna().sort_values(ascending=False).index[:10])
        cuts[("top10", "")] = c["day"].isin(top).to_numpy()
        cuts[("spike", "")] = (c["actual"] > c["actual"].quantile(SPIKE)).to_numpy()
        place = f"hub-{grid}"
        for (cut, key), msk in cuts.items():
            for m in ms:
                n, mae, mape = score(c[msk], m)
                r = shown.get((place, m, cut, key))
                ok = r is not None and r["hours"] == n and (mae is None or abs(r["mae"] - mae) <= 0.011) and \
                    ((mape is None and r["mape"] is None) or (mape is not None and r["mape"] is not None and abs(r["mape"] - mape) <= 0.0011))
                figs.append((f"{place}.{m}.{cut}.{key}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
        # section 8: the longer backtest, the method chosen now in every year; each year and the whole span
        xl["erw"] = xl[min((v, m) for m, v in maes.items())[1]]
        cl = xl.dropna(subset=["actual"] + ms).reset_index(drop=True)
        lb = next(h for h in doc["hubs"] if h["grid"] == grid)["long_backtest"]
        shown_l = {str(y["year"]): y for y in lb["by_year"]}
        shown_l["all"] = lb["all"]
        parts = {str(y): (cl["day"].dt.year == y).to_numpy() for y in sorted(cl["day"].dt.year.unique())}
        parts["all"] = np.ones(len(cl), bool)
        for key, msk in parts.items():
            for m in ms:
                n, mae, mape = score(cl[msk], m)
                r = shown_l.get(key)
                got = None if r is None else (r["hours"], r["mae"][m], r["mape"][m])
                ok = got is not None and got[0] == n and (mae is None or abs(got[1] - mae) <= 0.011) and \
                    ((mape is None and got[2] is None) or (mape is not None and got[2] is not None and abs(got[2] - mape) <= 0.0011))
                figs.append((f"{place}.{m}.long.{key}", got, (n, mae, mape), ok))
        print(f"{place}: {sum(1 for f_ in figs if f_[0].startswith(place) and f_[3])} of {sum(1 for f_ in figs if f_[0].startswith(place))} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_rt.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for f_ in figs if f_[3])
    print(f"real-time price: {ok} of {len(figs)} figures equal")
    for f_ in [f_ for f_ in figs if not f_[3]][:40]:
        print("  differs:", f_)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
