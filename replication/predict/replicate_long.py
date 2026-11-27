#!/usr/bin/env python3
"""Replication of the demand forecast's longer backtest (site/data/predict/long_backtest.json), session 10603.
Written from docs/methods/predict.md sections 3, 14 and 25; it imports nothing of the builder, only the replication's
own readers (replicate.py) and the vectorised rows of section 3's regression (replicate_price.py). The demand: each
authority's demand_mw of eia930_all_history (EIA's six-month files, July 2015 to June 2018) and of
eia930_ba_demand_hourly, the hourly table winning an hour both hold; a region summed by the demand pages' rule
(warehouse/derived/region_files.py). The regression and regression_recent refitted for every target day (730 days
before it, at least 300, horizon two days), yesterday and the week-ago hour; from 1 July 2016. The method: the lowest
MAE over the last two years on the hours every candidate and the operator hold (a tie by name). Every figure of the
file (each year and the whole span: hours, MAE, MAPE of every method; the operator beside the ERW on its own hours) is
recomputed. Prints N of N and writes replication/predict/figures_long.csv.
    python replication/predict/replicate_long.py --tables DIR [--file site/data/predict/long_backtest.json]
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

FIRST = pd.Timestamp("2016-07-01")
H, CHOICE = 2, 730
METHODS = ["erw", "yesterday", "week_ago", "regression", "regression_recent"]
CANDS = ["yesterday", "week_ago", "regression", "regression_recent"]


def demand_long(tables, places):
    sys.path.append(os.path.join(ROOT, "warehouse", "connectors"))
    sys.path.append(os.path.join(ROOT, "warehouse", "derived"))
    import region_files as rf
    rf.ROOT = os.path.abspath(os.path.join(tables, "..", ".."))
    ref, _ = rf.reference()
    frames = []
    for order, t in enumerate(["eia930_all_history", "eia930_ba_demand_hourly"]):
        d = rep.read(os.path.join(tables, t + ".csv"), ["entity", "variable", "ts_utc", "value"])
        d = d[d["variable"] == "demand_mw"].copy()
        d["order"] = order
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    d = d.sort_values(["entity", "ts", "order"]).drop_duplicates(["entity", "ts"], keep="last")
    out, tz = {}, {}
    for p in places:
        kind, code = p.split("-", 1)
        code = code.upper()
        if kind == "region":
            s, _ = rf.region_demand(code, ref, d)
            tz[p] = rf.REGION_TZ[code]
        else:
            g = d[d["entity"] == f"eia930:{code}"]
            s = pd.Series(g["value"].to_numpy(float), index=pd.DatetimeIndex(g["ts"])).sort_index()
            tz[p] = rf.BA_TZ.get(code) or ref[code]["tz"]
        out[p] = s.dropna()
    return out, tz


def score(x, m):
    if not len(x):
        return 0, None, None
    e = (x[m] - x["actual"]).abs()
    keep = x["actual"] > 0
    return int(len(x)), round(float(e.mean()), 2), round(float((e[keep] / x["actual"][keep]).mean() * 100), 3)


def frame(s, tz):
    f = rep.local(s, tz)
    M = rep.mat(f)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=H), freq="D"))
    X, ly = rpp.demand_X(M, H)
    raw = M.to_numpy(float)
    fil = rpp.fill_lone(raw)
    with np.errstate(divide="ignore", invalid="ignore"):
        lf = np.log(np.where(fil > 0, fil, np.nan))
    extra = np.stack([np.repeat(rpp.lag(lf[:, 23], H)[:, None], 24, axis=1), rpp.lag(lf, H + 1), rpp.lag(lf, 14)], axis=2)
    P = {"regression": np.exp(rpp.walk(X, ly, H)), "regression_recent": np.exp(rpp.walk(np.concatenate([X, extra], axis=2), ly, H)),
         "yesterday": rpp.lag(raw, H), "week_ago": rpp.lag(raw, 7)}
    pos = pd.Series(np.arange(len(M)), index=M.index)
    x = f[f["day"] >= FIRST].copy()
    i = pos.reindex(x["day"]).to_numpy()
    k = x["hour"].to_numpy()
    for m, arr in P.items():
        x[m] = arr[i, k]
    return x


def check(key, shown, got, figs):
    ok = shown is not None and shown["hours"] == got[0]
    for m in got[1]:
        a, b = (shown or {}).get("mae", {}).get(m), got[1][m]
        c, d = (shown or {}).get("mape", {}).get(m), got[2][m]
        ok = ok and ((a is None and b is None) or (a is not None and b is not None and abs(a - b) <= 0.011)) and \
            ((c is None and d is None) or (c is not None and d is not None and abs(c - d) <= 0.0011))
    figs.append((key, None if shown is None else (shown["hours"], shown.get("mae"), shown.get("mape")), got, ok))


def summary(z, methods):
    c = z.dropna(subset=["actual"] + methods)
    res = {m: score(c, m) for m in methods}
    return len(c), {m: v[1] for m, v in res.items()}, {m: v[2] for m, v in res.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "long_backtest.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    places = [p["place"] for p in doc["places"]]
    dem, tz = demand_long(a.tables, places)
    ops = rep.operator(a.tables)
    figs = []
    for p in doc["places"]:
        name = p["place"]
        x = frame(dem[name], tz[name])
        x["operator"] = ops[name].reindex(pd.DatetimeIndex(x["ts"])).to_numpy() if name in ops else np.nan
        rec = x[x["day"] > x["day"].max() - pd.Timedelta(days=CHOICE)]
        need = CANDS + (["operator"] if name in ops else [])
        c2 = rec.dropna(subset=["actual"] + need)
        maes = {m: score(c2, m)[1] for m in CANDS}
        chosen = min((v, m) for m, v in maes.items() if v is not None)[1]
        x["erw"] = x[chosen]
        figs.append((f"{name}.method", p["method"], chosen, p["method"] == chosen))
        check(f"{name}.all", p["all"], summary(x, METHODS), figs)
        shown_years = {y["year"]: y for y in p["by_year"]}
        for yr in sorted(x["day"].dt.year.unique()):
            g = x[x["day"].dt.year == yr]
            got = summary(g, METHODS)
            if not got[0]:
                continue
            sy = shown_years.get(int(yr))
            check(f"{name}.{yr}", sy, got, figs)
            if name in ops:
                go = summary(g, ["erw", "operator"])
                so = (sy or {}).get("operator_same_hours")
                if go[0]:
                    check(f"{name}.{yr}.operator", so, go, figs)
                else:
                    figs.append((f"{name}.{yr}.operator", so, None, so is None))
        print(f"{name}: {sum(1 for g in figs if g[0].startswith(name + '.') and g[3])} of {sum(1 for g in figs if g[0].startswith(name + '.'))} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_long.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for g in figs if g[3])
    print(f"longer backtest: {ok} of {len(figs)} groups of figures equal")
    for g in [g for g in figs if not g[3]][:40]:
        print("  differs:", g)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
