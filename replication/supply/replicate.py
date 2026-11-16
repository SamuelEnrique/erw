#!/usr/bin/env python3
"""ERW, supply and trade (/supply): an independent replication of the figures of the page's file (session 7013, chain
301; the done line's tool 20).

Written from docs/methods/supply_and_trade.md ("The three comparisons", "The surprise", "Notes on the series",
"Positioning", "Day-ahead energy cleared") and the tables alone, not from warehouse/derived/supply_page.py. For each row
of site/data/supply.json it rebuilds the row's series from its table:

  stocks, refining, trade, weekly production, gas storage   eia_petroleum_supply_weekly, eia_gas_storage_weekly (the
                     row's id is the EIA series id); stocks in million barrels (EIA's thousands over 1,000)
  gas trade          eia_gas_trade_monthly: the month's MMcf over 1,000 and over the month's days (Bcf a day); the row
                     of every other point of exit is the total less the terminals named
  monthly production eia_basin_production_monthly, months to three before the month of the build
  positioning        cftc_cot_positions, managed money's net
  day-ahead cleared  each operator's table: the mean of the seven whole local days of a week ending Friday, a day
                     counting only when every hour of it is held

and recomputes: the latest; the period before (7 days, or the month before); last year (364 days before or the nearest
within 3; the same month a year before); the five-year average of the values 52 to 260 weeks before (the same month of
the five years before), only when all five are held, with its lowest, highest and whether the latest is outside them;
the change (latest less the period before) against the mean of the same change in the five years before, its lowest,
highest, the surprise and whether it is outside; the spark (the last 52 values). The fuel burned for power is derived
from EIA-930's hourly generation workbooks held only in the data machine's raw store, not a table: its rows are counted
apart. Values are compared to 0.0001 of their printed precision. Prints N of N.

    python replication/supply/replicate.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import calendar
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLEARED = {"cleared-ercot": ("ercot_dam_cleared_energy", "America/Chicago", None),
           "cleared-caiso": ("caiso_dam_cleared_energy", "America/Los_Angeles", None),
           "cleared-nyiso": ("nyiso_dam_cleared_energy", "America/New_York", None),
           "cleared-iso-ne": ("isone_dam_cleared_energy", "America/New_York", None),
           "cleared-spp": ("spp_dam_cleared_energy", "America/Chicago", "SPP"),
           "cleared-spp-west": ("spp_dam_cleared_energy", "America/Chicago", "SWPW")}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def day(s):
    return dt.date.fromisoformat(s[:10])


def table_series(tables, name, want_var=None):
    """{normalized entity: {date: value}} of a table (one variable an entity, or want_var)."""
    out = defaultdict(dict)
    p = os.path.join(tables, name + ".csv")
    if not os.path.exists(p):
        return out
    for r in rows_of(p):
        if want_var and r["variable"] != want_var:
            continue
        if r["value"] in ("", None):
            continue
        out[norm(r["entity"])][day(r["ts_utc"])] = float(r["value"])
    return out


def cleared_series(tables, name, tz_name, area):
    """{week ending Friday: mean MWh a day} from an operator's hourly cleared table."""
    tz = ZoneInfo(tz_name)
    hours = defaultdict(float)
    count = defaultdict(int)
    for r in rows_of(os.path.join(tables, name + ".csv")):
        if area and area not in (r.get("node", "") + r.get("entity", "")):
            continue
        if r["value"] in ("", None):
            continue
        t = dt.datetime.fromisoformat(r["ts_utc"][:19]).replace(tzinfo=dt.timezone.utc).astimezone(tz)
        hours[t.date()] += float(r["value"])
        count[t.date()] += 1
    days = {}
    for d, n in count.items():
        start = dt.datetime.combine(d, dt.time(), tzinfo=tz)
        nxt = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(), tzinfo=tz)
        if n == round((nxt - start).total_seconds() / 3600):
            days[d] = hours[d]
    weeks = {}
    for d in days:
        if d.weekday() == 4:   # a Friday ends the week
            ds = [d - dt.timedelta(days=k) for k in range(7)]
            if all(x in days for x in ds):
                weeks[d] = sum(days[x] for x in ds) / 7
    return weeks


def at(series, d, near=0):
    if d in series:
        return d, series[d]
    for k in range(1, near + 1):
        for x in (d - dt.timedelta(days=k), d + dt.timedelta(days=k)):
            if x in series:
                return x, series[x]
    return None


def month_back(d, n):
    y, m = d.year, d.month - n
    while m <= 0:
        y, m = y - 1, m + 12
    return dt.date(y, m, 1)


def figures(series, freq):
    pts = sorted(series.items())
    if not pts:
        return {}
    t, v = pts[-1]
    out = {"last": (t, v)}
    if freq == "W":
        prev = at(series, t - dt.timedelta(days=7))
        year = at(series, t - dt.timedelta(days=364), 3)
        fives = [at(series, t - dt.timedelta(weeks=52 * k)) for k in range(1, 6)]
        changes = []
        for k in range(1, 6):
            a = at(series, t - dt.timedelta(weeks=52 * k))
            b = at(series, t - dt.timedelta(weeks=52 * k, days=7))
            changes.append(a[1] - b[1] if a and b else None)
    else:
        prev = at(series, month_back(t, 1))
        year = at(series, month_back(t, 12))
        fives = [at(series, month_back(t, 12 * k)) for k in range(1, 6)]
        changes = []
        for k in range(1, 6):
            a, b = at(series, month_back(t, 12 * k)), at(series, month_back(t, 12 * k + 1))
            changes.append(a[1] - b[1] if a and b else None)
    if prev:
        out["prev"] = (prev[0], prev[1], v - prev[1])
    if year:
        out["year"] = (year[0], year[1], v - year[1])
    if all(fives):
        xs = [x[1] for x in fives]
        avg = sum(xs) / 5
        out["avg5"] = (avg, min(xs), max(xs), v - avg, v < min(xs) or v > max(xs))
    if prev and all(c is not None for c in changes):
        ch = v - prev[1]
        a5 = sum(changes) / 5
        out["change"] = (ch, a5, min(changes), max(changes), ch - a5, ch < min(changes) or ch > max(changes))
    out["spark"] = pts[-52:]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Supply and trade's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "supply.json"), encoding="utf-8") as f:
            sup = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    weekly = {}
    for t in ("eia_petroleum_supply_weekly", "eia_gas_storage_weekly"):
        weekly.update(table_series(a.tables, t))
    trade = table_series(a.tables, "eia_gas_trade_monthly")
    basin = table_series(a.tables, "eia_basin_production_monthly")
    cftc = table_series(a.tables, "cftc_cot_positions", "managed_money_net")
    built = day(sup["built"])
    n, misses, apart = 0, [], []

    def check(what, mine, theirs, tol=0.0001):
        nonlocal n
        n += 1
        if isinstance(mine, bool) or isinstance(theirs, bool) or mine is None or theirs is None:
            ok = mine == theirs
        elif isinstance(mine, (int, float)):
            ok = abs(float(mine) - float(theirs)) <= tol * max(1.0, abs(float(theirs))) * 0 + tol + 1e-9
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    named = [r for r in sup["rows"] if r["group"] == "gastrade" and "-eng-y" in r["id"]]
    for r in sup["rows"]:
        if r.get("status") != "ok":
            continue
        rid, g, freq = r["id"], r["group"], r["freq"]
        if g == "burn":
            apart.append(rid)
            continue
        if g == "cleared":
            spec = CLEARED.get(rid)
            ser = cleared_series(a.tables, *spec) if spec else {}
        elif g == "position":
            ser = cftc.get(norm(rid[5:]), {})
        elif g == "gastrade":
            def bcfd(s):
                return {d: x / 1000 / calendar.monthrange(d.year, d.month)[1] for d, x in s.items()}
            key = norm(rid[4:])
            if key in trade:
                ser = bcfd(trade[key])
            else:   # every other point of exit: the total less the terminals named
                tot = trade.get(norm("N9133US2"), {})
                parts = [trade.get(norm(x["id"][4:]), {}) for x in named]
                ser = bcfd({d: x - sum(p.get(d, 0.0) for p in parts) for d, x in tot.items()})
        elif g == "prod" and freq == "M":
            lim = month_back(dt.date(built.year, built.month, 1), 3)
            ser = {d: x for d, x in basin.get(norm(rid[4:]), {}).items() if d <= lim}
        else:
            ser = dict(weekly.get(norm(rid[4:]), {}))
            if r.get("unit") == "million bbl":
                ser = {d: x / 1000 for d, x in ser.items()}
        got = figures(ser, freq)
        if not got:
            check(f"{rid} series", None, r["last"])
            continue
        check(f"{rid} last.t", got["last"][0].isoformat(), r["last"]["t"])
        check(f"{rid} last.v", got["last"][1], r["last"]["v"])
        for k in ("prev", "year"):
            if r.get(k):
                gk = got.get(k)
                check(f"{rid} {k}.t", gk and gk[0].isoformat(), r[k]["t"])
                check(f"{rid} {k}.v", gk and gk[1], r[k]["v"])
                check(f"{rid} {k}.ch", gk and gk[2], r[k]["ch"])
        if r.get("avg5"):
            g5 = got.get("avg5")
            for i, k in enumerate(("v", "lo", "hi", "ch", "outside")):
                if k in r["avg5"]:
                    check(f"{rid} avg5.{k}", g5 and g5[i], r["avg5"][k])
        if r.get("change"):
            gc = got.get("change")
            for i, k in enumerate(("v", "avg5", "lo", "hi", "surprise", "outside")):
                if k in r["change"]:
                    check(f"{rid} change.{k}", gc and gc[i], r["change"][k])
        if r.get("spark"):
            sp = got.get("spark", [])
            check(f"{rid} spark.t", [d.isoformat() for d, _ in sp], r["spark"]["t"])
            for i, (d, x) in enumerate(sp):
                if i < len(r["spark"]["v"]):
                    check(f"{rid} spark.v {d}", x, r["spark"]["v"][i])
    print(f"Supply and trade, from {a.tables} against supply.json (built {sup['built']}): "
          f"{sum(1 for r in sup['rows'] if r.get('status') == 'ok') - len(apart)} rows recomputed; the fuel burn's "
          f"{len(apart)} rows counted apart (built from EIA-930 workbooks, not a table)")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
