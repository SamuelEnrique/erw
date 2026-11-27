#!/usr/bin/env python3
"""Replication of the separate line "with the weather known" (scores.json, series demand_weather_known), session 10603.
Written from docs/methods/predict.md section 13 and section 3; it imports nothing of the builder, only the replication's
own readers (replicate.py) and the vectorised rows of section 3's regression (replicate_price.py). The regression of
section 3, made with demand through two days before, with three regressors added: the region's observed
population-weighted temperature at the hour (region_weather_hourly, over 100), its square, and the day's mean over 100
(a lone missing hour is the mean of its neighbours, for the regressors only); an authority takes its EIA region's
temperature. Refitted for every target day on the 730 days before it (at least 300), as the regression itself, which is
refitted here too. Every figure of the series' rows (hours, MAE, MAPE; cuts all and last_2_years, the last two years
counted from the place's last day) is recomputed on the hours the actual, the line, the regression and the operator all
hold. Prints N of N and writes replication/predict/figures_wk.csv.
    python replication/predict/replicate_wk.py --tables DIR [--file site/data/predict/scores.json]
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
sys.path.insert(0, HERE)
import replicate as rep  # noqa: E402
import replicate_price as rpp  # noqa: E402

FIRST = pd.Timestamp("2019-07-01")
H, CHOICE = 2, 730
METHODS = ["with_weather_known", "regression", "operator"]


def temperatures(tables):
    d = rep.read(os.path.join(tables, "region_weather_hourly.csv"), ["entity", "variable", "ts_utc", "value"])
    d = d[d["variable"] == "temperature_f"].copy()
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    out = {}
    for e, g in d.groupby("entity"):
        s = pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index()
        out[e.split(":", 1)[1].lower()] = s[~s.index.duplicated(keep="last")].dropna()
    return out


def regions(tables, places):
    sys.path.append(os.path.join(ROOT, "warehouse", "connectors"))
    sys.path.append(os.path.join(ROOT, "warehouse", "derived"))
    import region_files as rf
    rf.ROOT = os.path.abspath(os.path.join(tables, "..", ".."))
    ref, _ = rf.reference()
    out = {}
    for p in places:
        kind, code = p.split("-", 1)
        if kind == "region":
            out[p] = code
        else:
            r = ref.get(code.upper())
            out[p] = r["region"].lower() if r and r.get("region") else None
    return out


def metric(x, m):
    e = (x[m] - x["actual"]).abs()
    keep = x["actual"] > 0
    return int(len(x)), round(float(e.mean()), 2), round(float((e[keep] / x["actual"][keep]).mean() * 100), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "scores.json"))
    a = ap.parse_args()
    sc = json.load(open(a.file, encoding="utf-8"))
    cols = sc["rows_columns"]
    shown = {(r[0], r[2], r[3]): dict(zip(cols, r)) for r in sc["rows"] if r[1] == "demand_weather_known"}
    places = sorted({k[0] for k in shown})
    dem, tz = rep.demand_places(a.tables, places)
    ops = rep.operator(a.tables)
    temp = temperatures(a.tables)
    reg = regions(a.tables, places)
    figs = []
    for p in places:
        f = rep.local(dem[p], tz[p])
        M = rep.mat(f)
        M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=H), freq="D"))
        X, ly = rpp.demand_X(M, H)
        T = rep.mat(rep.local(temp[reg[p]], tz[p])).reindex(M.index).to_numpy(float)
        T = rpp.fill_lone(T)
        tm = np.mean(T, axis=1)
        W = np.stack([T / 100.0, (T / 100.0) ** 2, np.repeat((tm / 100.0)[:, None], 24, axis=1)], axis=2)
        P = {"regression": np.exp(rpp.walk(X, ly, H)), "with_weather_known": np.exp(rpp.walk(np.concatenate([X, W], axis=2), ly, H))}
        pos = pd.Series(np.arange(len(M)), index=M.index)
        x = f[f["day"] >= FIRST].copy()
        i = pos.reindex(x["day"]).to_numpy()
        k = x["hour"].to_numpy()
        for m, arr in P.items():
            x[m] = arr[i, k]
        x["operator"] = ops[p].reindex(pd.DatetimeIndex(x["ts"])).to_numpy() if p in ops else np.nan
        last = x["day"].max()
        for cut, z in (("all", x), ("last_2_years", x[x["day"] > last - pd.Timedelta(days=CHOICE)])):
            c = z.dropna(subset=["actual"] + METHODS)
            for m in METHODS:
                n, mae, mape = metric(c, m) if len(c) else (0, None, None)
                r = shown.get((p, m, cut))
                ok = r is not None and r["hours"] == n and ((mae is None and r["mae"] is None) or
                                                            (mae is not None and r["mae"] is not None and abs(r["mae"] - mae) <= 0.011 and abs(r["mape"] - mape) <= 0.0011))
                figs.append((f"{p}.{m}.{cut}", None if r is None else (r["hours"], r["mae"], r["mape"]), (n, mae, mape), ok))
        print(f"{p} (region {reg[p]}): {sum(1 for g in figs if g[0].startswith(p + '.') and g[3])} of {sum(1 for g in figs if g[0].startswith(p + '.'))} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_wk.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for g in figs if g[3])
    print(f"with the weather known: {ok} of {len(figs)} figures equal")
    for g in [g for g in figs if not g[3]][:40]:
        print("  differs:", g)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
