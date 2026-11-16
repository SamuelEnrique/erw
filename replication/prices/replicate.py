#!/usr/bin/env python3
"""ERW, power prices (/prices and /prices/<hub>): an independent replication of every price the pages show (session 7011,
chain 301; the done line's tool 18).

The pages have no file of their own: at render time they read the live set (Supabase) with the public anon key, the
newest real-time interval of every hub and zone (latest_prices) and each market's day-ahead and real-time rows of the
last 30 days (site/data/markets.json names the table, variable and market of each). This script reads the same rows the
same way (SUPABASE_URL and SUPABASE_ANON_KEY from the environment or .env, the key the site's visitors' pages use) and
compares every one with the warehouse's own table (--tables, the tables of record), not with the site's code:

  - every day-ahead and real-time row of the live set's last 30 days whose (entity, hour or interval) the warehouse
    holds: the same value (to 0.0001 USD/MWh);
  - every latest_prices row whose interval the warehouse holds: the same value;
  - the page's rule for "day-ahead this hour" (the row whose hour holds the moment of the run), recomputed from the
    warehouse, against the live row it picks;
  - a held table (its publisher asks for permission: NYISO, ISO-NE) shows no row to the anon key, and none is compared.

Rows of the live set the warehouse does not hold yet (the newest intervals: latest_prices is refreshed every 15
minutes, the warehouse once a day) are counted apart, never compared. Prints N of N.

    python replication/prices/replicate.py [--tables DIR] [--days 30]

Exit 0 when every compared value is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    for p in (os.path.join(ROOT, ".env"), os.path.join(ROOT, "site", ".env.local")):
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                if ln.startswith(name + "="):
                    return ln.split("=", 1)[1].strip().strip('"')
    return ""


def rest(path, params):
    base = urllib.parse.urlsplit(env("SUPABASE_URL"))   # the origin alone, as site/lib/supabase.ts takes it
    url = f"{base.scheme}://{base.netloc}/rest/v1/{path}?" + urllib.parse.urlencode(params)
    key = env("SUPABASE_ANON_KEY")
    out, offset = [], 0
    while True:
        req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}",
                                                   "Range": f"{offset}-{offset + 999}", "Range-Unit": "items"})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.loads(r.read())
        out += page
        if len(page) < 1000:
            return out
        offset += 1000


def warehouse(path, market, variable):
    held = {}
    if not os.path.exists(path):
        return held
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if r.get("market", market) == market and r["variable"] == variable and r["value"] not in ("", None):
                held[(r["entity"], r["ts_utc"][:19])] = float(r["value"])
    return held


def main(argv=None):
    ap = argparse.ArgumentParser(description="The power prices pages' replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "markets.json"), encoding="utf-8") as f:
            markets = json.load(f)["isos"]
        now = dt.datetime.now(dt.timezone.utc)
        since = (now - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        latest = rest("latest_prices", {"select": "*", "order": "entity"})
    except Exception as exc:   # a network or a key fault: the inputs cannot be read
        print(f"the inputs could not be read: {exc}")
        return 2
    n, misses, unheld, held_tables = 0, [], 0, []

    def check(what, mine, theirs, tol=0.0001):
        nonlocal n
        n += 1
        if mine is None or theirs is None or abs(float(mine) - float(theirs)) > tol + 1e-9:
            misses.append(f"{what}: warehouse {mine!r}, live set {theirs!r}")

    wh_cache = {}
    for m in markets:
        for side in ("da", "rt"):
            spec = m.get(side)
            if not spec:
                continue
            live = rest("series", {"select": "entity,variable,ts_utc,value", "table_name": f"eq.{spec['table']}",
                                   "variable": f"eq.{spec['variable']}", "market": f"eq.{spec['market']}",
                                   "ts_utc": f"gte.{since}", "order": "entity,ts_utc"})
            if not live:
                held_tables.append(f"{m['iso']} {side} ({spec['table']})")
                continue
            key = (spec["table"], spec["market"], spec["variable"])
            if key not in wh_cache:
                wh_cache[key] = warehouse(os.path.join(a.tables, spec["table"] + ".csv"), spec["market"], spec["variable"])
            wh = wh_cache[key]
            for r in live:
                k = (r["entity"], r["ts_utc"][:19])
                if k in wh:
                    check(f"{m['iso']} {side} {k[0]} {k[1]}", wh[k], r["value"])
                else:
                    unheld += 1
            if side == "da":
                # the page's "day-ahead this hour": the row whose hour holds the moment of the run
                hour = now.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
                for ent in sorted({r["entity"] for r in live}):
                    lv = next((r["value"] for r in live if r["entity"] == ent and r["ts_utc"][:19] == hour), None)
                    if (ent, hour) in wh and lv is not None:
                        check(f"{m['iso']} day-ahead this hour {ent} {hour}", wh[(ent, hour)], lv)
            if side == "rt":
                for r in latest:
                    if r["entity"].split(":")[0] != m["main"].split(":")[0] or r.get("variable") != spec["variable"]:
                        continue
                    k = (r["entity"], r["ts_utc"][:19])
                    if k in wh:
                        check(f"{m['iso']} latest {k[0]} {k[1]}", wh[k], r["value"])
                    else:
                        unheld += 1
    print(f"Power prices, the live set at {now:%Y-%m-%d %H:%M} UTC against the tables in {a.tables}: "
          f"{unheld:,} live rows newer than the warehouse's copy (not compared); held for a license, no row shown: "
          f"{', '.join(held_tables) or 'none'}")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} prices equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
