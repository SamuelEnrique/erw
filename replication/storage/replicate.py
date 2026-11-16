#!/usr/bin/env python3
"""ERW, storage (/storage, its tabs buildout and owners): an independent replication of every figure the page draws
(session 7014, chain 301; the done line's tool 21).

The page has no file of its own: at render time it reads the live set with the public anon key: the fleet
(storage_capacity, one entity a battery with its MW, status, state, ISO, planned year and MWh), the daily cycle of the
last 45 days (storage_daily_cycle), EIA-930's battery net generation of the last 31 days (eia930_all_storage), CAISO's
own battery output (caiso_battery_storage), and, on its tabs, the monthly buildout (storage_buildout_monthly) and the
owners (storage_owners_monthly). This script reads the same rows the same way and compares every one with the
warehouse's own table (--tables), and recomputes from the warehouse the fleet's sums the page states (operating MW and
MWh, by ISO and in all; planned MW by year), against the same sums of the live rows. A live row the warehouse does not
hold yet is counted apart. Prints N of N.

    python replication/storage/replicate.py [--tables DIR]

Needs SUPABASE_URL and SUPABASE_ANON_KEY in the environment (the key the site's visitors' pages use). Exit 0 when every
figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SERIES = [("storage_daily_cycle", None, 45), ("eia930_all_storage", "net_generation_battery_mw", 31),
          ("caiso_battery_storage", "batteries_mw", 31), ("storage_buildout_monthly", None, None),
          ("storage_owners_monthly", None, None)]


def rest(path, params):
    base = urllib.parse.urlsplit(os.environ["SUPABASE_URL"])
    url = f"{base.scheme}://{base.netloc}/rest/v1/{path}?" + urllib.parse.urlencode(params)
    key = os.environ["SUPABASE_ANON_KEY"]
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


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def sums(units):
    """The fleet's sums: operating MW and MWh by ISO and in all, planned MW by year."""
    s = defaultdict(float)
    for u in units:
        mw, mwh = num(u["capacity_mw"]) or 0.0, num(u.get("mwh")) or 0.0
        if u["status"] == "operating":
            s[("operating_mw", u.get("iso") or "")] += mw
            s[("operating_mw", "all")] += mw
            s[("operating_mwh", u.get("iso") or "")] += mwh
            s[("operating_mwh", "all")] += mwh
            s[("operating_n", "all")] += 1
        elif u.get("planned_year"):
            s[("planned_mw", u["planned_year"])] += mw
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description="The storage page's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    now = dt.datetime.now(dt.timezone.utc)
    n, misses, unheld = 0, [], 0

    def check(what, mine, theirs, tol=0.0001):
        nonlocal n
        n += 1
        if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)):
            ok = abs(mine - theirs) <= tol + 1e-9
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: warehouse {mine!r}, live set {theirs!r}")

    try:
        live_units = rest("entities", {"select": "entity_id,capacity_mw,status,state:extra->>state,iso:extra->>iso,"
                                                 "planned_year:extra->>planned_year,mwh:extra->>energy_capacity_mwh",
                                       "table_name": "eq.storage_capacity", "order": "entity_id"})
    except Exception as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    wh_units = {}
    for r in rows_of(os.path.join(a.tables, "storage_capacity.csv")):
        wh_units[r["entity_id"]] = dict(entity_id=r["entity_id"], capacity_mw=r["capacity_mw"], status=r["status"],
                                        state=r.get("state", ""), iso=r.get("iso", ""), planned_year=r.get("planned_year", ""),
                                        mwh=r.get("energy_capacity_mwh", ""))
    for u in live_units:
        w = wh_units.get(u["entity_id"])
        if w is None:
            unheld += 1
            continue
        check(f"storage_capacity {u['entity_id']} capacity_mw", num(w["capacity_mw"]), num(u["capacity_mw"]))
        check(f"storage_capacity {u['entity_id']} status", w["status"], u["status"])
        for k in ("state", "iso", "planned_year"):
            check(f"storage_capacity {u['entity_id']} {k}", w[k] or None, u[k] or None)
        check(f"storage_capacity {u['entity_id']} mwh", num(w["mwh"]), num(u["mwh"]))
    check("storage_capacity units", len(wh_units), len(live_units), 0)
    ws, ls = sums(wh_units.values()), sums(live_units)
    for k in sorted(set(ws) | set(ls)):
        check(f"fleet sum {k[0]} {k[1]}", round(ws.get(k, 0.0), 4), round(ls.get(k, 0.0), 4), 0.001)
    for table, var, days in SERIES:
        params = {"select": "entity,variable,ts_utc,value", "table_name": f"eq.{table}", "order": "entity,variable,ts_utc"}
        if var:
            params["variable"] = f"eq.{var}"
        if days:
            params["ts_utc"] = "gte." + (now - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            live = rest("series", params)
        except Exception as exc:
            print(f"the inputs could not be read: {table}: {exc}")
            return 2
        wh = {}
        p = os.path.join(a.tables, table + ".csv")
        if os.path.exists(p):
            for r in rows_of(p):
                if (not var or r["variable"] == var) and r["value"] not in ("", None):
                    wh[(r["entity"], r["variable"], r["ts_utc"][:19])] = float(r["value"])
        for r in live:
            k = (r["entity"], r["variable"], r["ts_utc"][:19])
            if k in wh:
                check(f"{table} {k}", wh[k], r["value"])
            else:
                unheld += 1
    print(f"Storage, the live set at {now:%Y-%m-%d %H:%M} UTC against the tables in {a.tables}: {len(live_units):,} units; "
          f"{unheld:,} live rows the warehouse's copy does not hold (not compared)")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
