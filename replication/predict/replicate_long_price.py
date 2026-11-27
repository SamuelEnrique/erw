#!/usr/bin/env python3
"""Replication of the day-ahead price forecast's longer backtest (site/data/predict/long_price.json), session 10603.
Written from docs/methods/predict_price.md sections 1 to 4, 10 and 11; it imports nothing of the builder, only the
replication's own scripts: the longer demand of replicate_long.py (eia930_all_history before the hourly table) and the
price walk of replicate_price.py (the demand regression made with demand through T-3 and the price regression, refitted
for every target day), from 1 July 2016. The method: the lowest MAE over the last two years (a tie by name). Every
figure of the file (each year and the whole span: hours, MAE, MAPE over hours of at least 5 USD/MWh, every method) is
recomputed. Prints N of N and writes replication/predict/figures_long_price.csv.
    python replication/predict/replicate_long_price.py --tables DIR [--file site/data/predict/long_price.json]
"""
import argparse
import csv
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import replicate_long as rl  # noqa: E402
import replicate_price as rpp  # noqa: E402

FIRST = pd.Timestamp("2016-07-01")
CHOICE = 730
METHODS = ["erw", "yesterday", "week_ago", "regression"]


def summary(z):
    c = z.dropna(subset=["actual"] + METHODS)
    got = {m: rpp.metric(c, m, rpp.FLOOR) for m in METHODS}
    return len(c), {m: v[1] for m, v in got.items()}, {m: v[2] for m, v in got.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "predict", "long_price.json"))
    a = ap.parse_args()
    doc = json.load(open(a.file, encoding="utf-8"))
    dps = sorted({p["demand_place"] for p in doc["places"]})
    dem, tz = rl.demand_long(a.tables, dps)
    prices = rpp.dam(a.tables, sorted({p["hub"] for p in doc["places"]}))
    gas = rpp.henry(a.tables)
    figs = []
    for p in doc["places"]:
        dp = p["demand_place"]
        x = rpp.price_place(prices[p["hub"]], tz[dp], dem[dp], tz[dp], gas, first=FIRST)
        rec = x[x["day"] > x["day"].max() - pd.Timedelta(days=CHOICE)].dropna(subset=["actual", "yesterday", "week_ago", "regression"])
        maes = {m: rpp.metric(rec, m)[1] for m in ("yesterday", "week_ago", "regression")}
        chosen = min((v, m) for m, v in maes.items() if v is not None)[1]
        x["erw"] = x[chosen]
        figs.append((f"{p['place']}.method", p["method"], chosen, p["method"] == chosen))
        shown = {str(y["year"]): y for y in p["by_year"]}
        shown["all"] = p["all"]
        parts = {str(y): x[x["day"].dt.year == y] for y in sorted(x["day"].dt.year.unique())}
        parts["all"] = x
        for key, z in parts.items():
            got = summary(z)
            if not got[0] and key not in shown:
                continue
            r = shown.get(key)
            ok = r is not None and r["hours"] == got[0]
            for m in METHODS:
                a1, b1, c1, d1 = (r or {}).get("mae", {}).get(m), got[1][m], (r or {}).get("mape", {}).get(m), got[2][m]
                ok = ok and ((a1 is None and b1 is None) or (a1 is not None and b1 is not None and abs(a1 - b1) <= 0.011)) and \
                    ((c1 is None and d1 is None) or (c1 is not None and d1 is not None and abs(c1 - d1) <= 0.0011))
            figs.append((f"{p['place']}.{key}", None if r is None else (r["hours"], r["mae"], r["mape"]), got, ok))
        print(f"{p['place']}: {sum(1 for g in figs if g[0].startswith(p['place'] + '.') and g[3])} of {sum(1 for g in figs if g[0].startswith(p['place'] + '.'))} groups equal", flush=True)
    with open(os.path.join(HERE, "figures_long_price.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "file", "recomputed", "equal"])
        w.writerows(figs)
    ok = sum(1 for g in figs if g[3])
    print(f"longer price backtest: {ok} of {len(figs)} groups of figures equal")
    for g in [g for g in figs if not g[3]][:40]:
        print("  differs:", g)
    sys.exit(0 if ok == len(figs) else 1)


if __name__ == "__main__":
    main()
