#!/usr/bin/env python3
"""Replication of the longer backtest of the forecast two to seven days ahead (site/data/predict/long_ahead.json),
session 10603. Written from docs/methods/predict.md sections 3, 12, 14 and 30; it imports nothing of the builder, only
the replication's own readers (replicate.py, replicate_long.py's demand of the six-month files and the hourly table)
and the vectorised rows of section 3's regression (replicate_price.py). For each place and horizon h of the file (3 to
7): the regression of section 3 and regression_recent of section 14 refitted at that horizon for every target day on
the 730 days before it (at least 300), yesterday (the hour of day T-h) and the same hour a week ago, from 1 July 2016.
The horizon's method: the lower MAE of the two regressions over the last two years of the hours all four hold. Every
figure of the file is recomputed: the method, each year's and the whole span's hours, MAE and MAPE of every method on
the hours all five hold, whether the method beats the week-ago hour that year, and the count of such years. Prints N of
N and writes replication/predict/figures_long_ahead.csv.
    python replication/predict/replicate_long_ahead.py --tables DIR [--file site/data/predict/long_ahead.json]
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
import replicate_long as rl  # noqa: E402
import replicate_price as rpp  # noqa: E402

FIRST = pd.Timestamp("2016-07-01")
CHOICE = 730
CANDS = ["regression", "regression_recent", "week_ago", "yesterday"]
SCORED = ["erw", "regression", "regression_recent", "week_ago", "yesterday"]


def horizon_frame(f, h):
    M = rep.mat(f)
    M = M.reindex(pd.date_range(M.index.min(), M.index.max() + pd.Timedelta(days=h), freq="D"))
    X, ly = rpp.demand_X(M, h)
    raw = M.to_numpy(float)
    fil = rpp.fill_lone(raw)
    with np.errstate(divide="ignore", invalid="ignore"):
        lf = np.log(np.where(fil > 0, fil, np.nan))
    extra = np.stack([np.repeat(rpp.lag(lf[:, 23], h)[:, None], 24, axis=1), rpp.lag(lf, h + 1), rpp.lag(lf, 14)], axis=2)
    P = {"regression": np.exp(rpp.walk(X, ly, h)), "regression_recent": np.exp(rpp.walk(np.concatenate([X, extra], axis=2), ly, h)),
         "yesterday": rpp.lag(raw, h), "week_ago": rpp.lag(raw, 7)}
    pos = pd.Series(np.arange(len(M)), index=M.index)
    x = f[f["day"] >= FIRST].copy()
    i = pos.reindex(x["day"]).to_numpy()
    k = x["hour"].to_numpy()
    for m, arr in P.items():
        x[m] = arr[i, k]
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "long_ahead.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    places = [p["place"] for p in doc["places"]]
    dem, tz = rl.demand_long(a.tables, places)
    figs = []
    for p in doc["places"]:
        name = p["place"]
        f = rep.local(dem[name], tz[name])
        for row in p["horizons"]:
            h = row["horizon_days"]
            key = f"{name}.h{h}"
            x = horizon_frame(f, h)
            c = x.dropna(subset=["actual"] + CANDS)
            rec = c[c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE)]
            maes = {m: rl.score(rec, m)[1] for m in ["regression", "regression_recent"]}
            method = min(["regression", "regression_recent"], key=lambda m: maes[m])
            figs.append((key + ".method", row["method"], method, row["method"] == method))
            x["erw"] = x[method]
            rl.check(key + ".all", row["all"], rl.summary(x, SCORED), figs)
            shown = {y["year"]: y for y in row["by_year"]}
            beats = 0
            for yr in sorted(x["day"].dt.year.unique()):
                got = rl.summary(x[x["day"].dt.year == yr], SCORED)
                if not got[0]:
                    continue
                sy = shown.get(int(yr))
                rl.check(f"{key}.{yr}", sy, got, figs)
                b = bool(got[1]["erw"] < got[1]["week_ago"])
                beats += b
                figs.append((f"{key}.{yr}.beats", None if sy is None else sy.get("beats_week_ago"), b, sy is not None and sy.get("beats_week_ago") == b))
            figs.append((key + ".years_beating", row["years_beating_week_ago"], beats, row["years_beating_week_ago"] == beats))
        n_ok = sum(1 for g in figs if g[0].startswith(name + ".") and g[3])
        n = sum(1 for g in figs if g[0].startswith(name + "."))
        print(f"{name}: {n_ok} of {n} groups of figures equal", flush=True)
    with open(os.path.join(HERE, "figures_long_ahead.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for g in figs if g[3])
    print(f"longer backtest further ahead: {ok} of {len(figs)} groups of figures equal")
    for g in [g for g in figs if not g[3]][:40]:
        print("  differs:", g)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
