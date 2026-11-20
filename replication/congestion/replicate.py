#!/usr/bin/env python3
"""Replication of the congestion page (/congestion) from the rows alone (chain 601, part C4, session 9000).

Written from docs/methods/grid_congestion.md and the page file's contract (docs/state/page_files_conditions.md,
section 1), not from the builder's code: every figure of site/data/conditions/congestion.json is recomputed from
constraints_binding_hourly and price_congestion_hourly and compared. Prints N of N, names every difference, and writes
replication/congestion/figures.csv (one row a figure: key, page, recomputed, equal).

    python replication/congestion/replicate.py [--tables DIR] [--file PATH]
"""
import argparse
import csv
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TZ = {"spp": "America/Chicago", "caiso": "America/Los_Angeles"}


def read(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--file", default=os.path.join(ROOT, "site", "data", "conditions", "congestion.json"))
    a = ap.parse_args()
    page = json.load(open(a.file, encoding="utf-8"))
    figs = []

    def check(key, shown, mine, tol=0.011):
        if shown is None or mine is None:
            ok = shown is None and mine is None
        elif isinstance(shown, str) or isinstance(mine, str):
            ok = shown == mine
        else:
            ok = abs(float(shown) - float(mine)) <= tol  # an absolute tolerance: the page rounds to 2 places (1 for costs and shares)
        figs.append((key, shown, mine, ok))

    c = read(os.path.join(a.tables, "constraints_binding_hourly.csv"))
    c["v"] = c["value"].astype(float)
    c["a"] = c["v"].abs()
    c["op"] = c["market"].str.split("_").str[0]
    for op, d in c.groupby("op"):
        loc = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ[op]).dt.tz_localize(None)
        d = d.assign(year=loc.dt.year.astype(str), month=loc.dt.strftime("%Y-%m"))
        P = page["constraints"][op]
        for y, g in d.groupby("year"):
            check(f"{op}.hours_by_year.{y}", P["hours_by_year"].get(y), len(g), 0)
            check(f"{op}.constraints_by_year.{y}", P["constraints_by_year"].get(y), g["entity"].nunique(), 0)
            agg = g.groupby("entity")["a"].agg(["count", "sum"])
            # the top lists: the page's 25th entry must not be beaten by any entry left out
            for kind, colname in (("by_hours", "count"), ("by_cost", "sum")):
                shown = P["top"][y][kind]
                floor = agg.loc[shown, colname].min()
                beaten = agg[(~agg.index.isin(shown)) & (agg[colname] > floor + 1e-9)]
                check(f"{op}.top.{y}.{kind}.complete", 0, len(beaten), 0)
        for k, s in P["constraints"].items():
            x = d[d["entity"] == k]
            check(f"{op}.{k}.hours", s["hours"], len(x), 0)
            check(f"{op}.{k}.abs_mean", s["abs_mean"], round(x["a"].mean(), 2))
            check(f"{op}.{k}.abs_max", s["abs_max"], round(x["a"].max(), 2))
            check(f"{op}.{k}.cost", s["cost"], round(x["a"].sum(), 1), 0.051)
            for m in s["monthly"]:
                xm = x[x["month"] == m[0]]
                check(f"{op}.{k}.monthly.{m[0]}.hours", m[1], len(xm), 0)
    p = read(os.path.join(a.tables, "price_congestion_hourly.csv"))
    p["v"] = p["value"].astype(float)
    p["op"] = p["market"].str.split("_").str[0]
    for op, d in p.groupby("op"):
        loc = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ[op]).dt.tz_localize(None)
        d = d.assign(year=loc.dt.year.astype(str))
        w = d.pivot_table(index=["node", "ts_utc", "year"], columns="variable", values="v").reset_index()
        for pl in page["places"][op]:
            x = w[w["node"] == pl["node"]]
            for y, g in x.groupby("year"):
                s = pl["by_year"][y]
                lmp, cong = g["lmp_dam"].mean(), g["congestion_dam"].mean()
                check(f"{pl['id']}.{y}.hours", s["hours"], len(g), 0)
                check(f"{pl['id']}.{y}.lmp_mean", s["lmp_mean"], round(lmp, 2))
                check(f"{pl['id']}.{y}.congestion_mean", s["congestion_mean"], round(cong, 2))
                check(f"{pl['id']}.{y}.share", s["congestion_share_pct"], round(100 * cong / lmp, 1) if lmp > 0 else None, 0.051)
                check(f"{pl['id']}.{y}.up", s["hours_congestion_up"], int((g["congestion_dam"] > 0).sum()), 0)
                check(f"{pl['id']}.{y}.down", s["hours_congestion_down"], int((g["congestion_dam"] < 0).sum()), 0)
    out = os.path.join(HERE, "figures.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(["key", "page", "recomputed", "equal"])
        for row in figs:
            wr.writerow(row)
    bad = [x for x in figs if not x[3]]
    print(f"{len(figs) - len(bad)} of {len(figs)} figures equal")
    for x in bad[:30]:
        print("  differs:", x)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
