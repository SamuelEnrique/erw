#!/usr/bin/env python3
"""ERW, curtailment (/curtailment), where free energy is: an independent replication of site/data/curtailment/
free_energy.json (session 7020, chain 301; the done line's tool 23, its fourth part).

Written from docs/methods/curtailment.md ("Where free energy is") and the file's own statement of its rules, not from
warehouse/derived/free_energy.py. For each grid, place and window (the last whole month, and the twelve months ending
with it, each from the file's start and end in UTC, which are the grid's standard time):

  an hour of real time is the mean of its four 15-minute prices, held only when all four are (an hourly real-time
  table's hour as it is); the place's real time is used where it holds 95 percent of the window's hours, otherwise
  its day-ahead; a row held in two of the place's tables is read once, from the first listed;
  negative: the hours priced below zero; under5: the hours priced under USD 5 per MWh, those below zero included;
  mean: the mean of the hours held; the heat map: the twelve months by the 24 hours of the day in standard time, the
  hours under USD 5 (and below zero) in each cell, on the year's basis.

An hour's mean is rounded to nine places before it is compared with zero or five (an hour of four prices summing to
zero is not below zero: docs/reviews/price-compare-faults-2026-11-16.md, row 1). Prints N of N.

    python replication/curtailment/free_energy.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UTC = dt.timezone.utc


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def utc(s):
    return dt.datetime.fromisoformat(s[:19]).replace(tzinfo=UTC)


def decimals(x):
    s = repr(float(x))
    return 0 if "e" in s else len(s.split(".")[1])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Where free energy is: the replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "curtailment", "free_energy.json"), encoding="utf-8") as f:
            fe = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    near, thr = fe["near_hours"], fe["threshold_usd_per_mwh"]
    places = [(g, l) for g, v in fe["grids"].items() for l in v["locations"]]
    want = defaultdict(set)   # table -> entities
    for g, l in places:
        for side in ("rt", "da"):
            for t in l.get("tables", {}).get(side, []):
                want[t].add(l["entity"])
    raw = defaultdict(dict)   # (table, entity, side) -> {ts: value}
    for t, ents in want.items():
        p = os.path.join(a.tables, t + ".csv")
        if not os.path.exists(p):
            continue
        for r in rows_of(p):
            if r["entity"] in ents and r["value"] not in ("", None):
                side = "rt" if r["market"].endswith("rtm") else "da" if r["market"].endswith("dam") else None
                if side:
                    raw[(t, r["entity"], side)][r["ts_utc"][:19]] = float(r["value"])
    n, misses = 0, []

    def check(what, mine, theirs):
        nonlocal n
        n += 1
        if isinstance(theirs, float) and isinstance(mine, (int, float)):
            ok = abs(mine - theirs) <= 0.5 * 10 ** -decimals(theirs) + 1e-9
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    # each grid states its windows (its standard time) in grids[g].windows
    for g, l in places:
        std = fe["grids"][g]["std_hours_behind_utc"]
        hours = {}
        for side in ("rt", "da"):
            merged = {}
            for t in l.get("tables", {}).get(side, []):
                for ts, v in raw.get((t, l["entity"], side), {}).items():
                    merged.setdefault(ts, v)
            freq = l.get("freq", {}).get(side)
            h = {}
            if freq == "PT15M":
                acc = defaultdict(list)
                for ts, v in merged.items():
                    acc[utc(ts).replace(minute=0)].append(v)
                h = {k: round(sum(x) / 4, 9) for k, x in acc.items() if len(x) == 4}
            elif freq == "PT1H":
                h = {utc(ts): round(v, 9) for ts, v in merged.items()}
            hours[side] = h
        for wname in ("month", "year"):
            theirs = l.get(wname)
            if not theirs:
                continue
            W = fe["grids"][g]["windows"]
            s, e = utc(W[wname]["start_utc"]), utc(W[wname]["end_utc"])
            n_in = W[wname]["hours"]
            held = {side: {k: v for k, v in hours[side].items() if s <= k < e} for side in hours}
            basis = "rt" if len(held.get("rt", {})) >= near * n_in else "da"
            x = held[basis]
            what = f"{g} {l['id']} {wname}"
            if "missing" in theirs:   # neither market holds 95 percent of the window: the counts held, and no figure
                check(f"{what} rt_hours_held", len(held.get("rt", {})), theirs.get("rt_hours_held", 0))
                check(f"{what} da_hours_held", len(held.get("da", {})), theirs.get("da_hours_held", 0))
                check(f"{what} not written", max(len(held.get("rt", {})), len(held.get("da", {}))) < near * n_in, True)
                continue
            check(f"{what} basis", basis, theirs.get("basis"))
            check(f"{what} hours_in_window", n_in, theirs.get("hours_in_window"))
            check(f"{what} hours_held", len(x), theirs.get("hours_held"))
            if "negative" in theirs:
                check(f"{what} negative", sum(1 for v in x.values() if v < 0), theirs["negative"])
                check(f"{what} under5", sum(1 for v in x.values() if v < thr), theirs["under5"])
            if "mean" in theirs and x:
                check(f"{what} mean", sum(x.values()) / len(x), theirs["mean"])
        heat = l.get("heat")
        if heat and heat.get("under5"):
            W = fe["grids"][g]["windows"]
            s, e = utc(W["year"]["start_utc"]), utc(W["year"]["end_utc"])
            months = fe["year_months"]
            x = {k: v for k, v in hours[heat["basis"]].items() if s <= k < e}
            u = [[0] * 24 for _ in months]
            ng = [[0] * 24 for _ in months]
            for k, v in x.items():
                lt = k - dt.timedelta(hours=std)
                mi = months.index(f"{lt.year:04d}-{lt.month:02d}") if f"{lt.year:04d}-{lt.month:02d}" in months else None
                if mi is None:
                    continue
                if v < thr:
                    u[mi][lt.hour] += 1
                if v < 0:
                    ng[mi][lt.hour] += 1
            check(f"{g} {l['id']} heat under5", u, heat["under5"])
            if "negative" in heat:
                check(f"{g} {l['id']} heat negative", ng, heat["negative"])
            check(f"{g} {l['id']} heat hours_held", len(x), heat.get("hours_held"))
    print(f"Where free energy is: {len(places)} places of {len(fe['grids'])} grids, the file built {fe['built']}, against the tables in {a.tables}")
    for m in misses[:a.show]:
        print("  " + m[:300])
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
