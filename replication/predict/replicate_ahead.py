#!/usr/bin/env python3
"""Replication of the demand forecast two to seven days ahead (site/data/predict/ahead.json), session 10603.
Written from docs/methods/predict.md sections 3, 12 and 14; it imports nothing of the builder, only the replication's own
readers (replicate.py) and the vectorised rows of section 3's regression (replicate_price.py). For each place and
horizon h of the file (3 to 7): the regression of section 3 and regression_recent of section 14 (three more
regressors: the last hour of day A, the same hour of day A-1, the same hour of day T-14), each refitted at that horizon
for every target day on the 730 days before it (at least 300); yesterday (the hour of day T-h) and the same hour a week
ago. Over the last two years of the hours all four hold: each method's MAE and MAPE, the horizon's method (the lower
MAE of the two regressions) and whether it is shown (its MAE below the week-ago hour's). Prints N of N and writes
replication/predict/figures_ahead.csv. Run it on a file built from the same tables (the daily run rewrites ahead.json).
    python replication/predict/replicate_ahead.py --tables DIR [--file site/data/predict/ahead.json]
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
CHOICE = 730
METHODS = ["regression", "regression_recent", "week_ago", "yesterday"]


def metric(x, m):
    e = (x[m] - x["actual"]).abs()
    keep = x["actual"] > 0
    return round(float(e.mean()), 2), round(float((e[keep] / x["actual"][keep]).mean() * 100), 3)


def horizon(f, h):
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
    c = x.dropna(subset=["actual"] + METHODS)
    return c[c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "ahead.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    places = [p["place"] for p in doc["places"]]
    dem, tz = rep.demand_places(a.tables, places)
    figs = []
    for p in doc["places"]:
        f = rep.local(dem[p["place"]], tz[p["place"]])
        for row in p["horizons"]:
            h = row["horizon_days"]
            rec = horizon(f, h)
            got = {m: metric(rec, m) for m in METHODS}
            method = min(["regression", "regression_recent"], key=lambda m: got[m][0])
            shown = got[method][0] < got["week_ago"][0]
            key = f"{p['place']}.h{h}"
            fl = row["last_2_years"]
            figs.append((key + ".hours", fl["hours"], len(rec), fl["hours"] == len(rec)))
            for m in METHODS:
                fm = (fl["mae"][m], fl["mape"][m])
                ok = fm[0] is not None and abs(fm[0] - got[m][0]) <= 0.011 and abs(fm[1] - got[m][1]) <= 0.0011
                figs.append((f"{key}.{m}", fm, got[m], ok))
            figs.append((key + ".method", row["method"], method, row["method"] == method))
            figs.append((key + ".shown", row["shown"], shown, row["shown"] == shown))
        print(f"{p['place']}: {sum(1 for g in figs if g[0].startswith(p['place'] + '.') and g[3])} of {sum(1 for g in figs if g[0].startswith(p['place'] + '.'))} figures equal", flush=True)
    with open(os.path.join(HERE, "figures_ahead.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for g in figs if g[3])
    print(f"further ahead: {ok} of {len(figs)} figures equal")
    for g in [g for g in figs if not g[3]][:40]:
        print("  differs:", g)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
