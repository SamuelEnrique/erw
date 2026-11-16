#!/usr/bin/env python3
"""ERW, where power is cheap (/prices/compare): an independent replication of every figure of the page's file (session
7012, chain 301; the done line's tool 19).

Written from docs/methods/hub_price_comparison.md and the tables alone, not from warehouse/derived/price_compare.py. For
the two windows of site/data/price_compare.json (twelve months and the last whole month, in each grid's local time) and
every hub and zone row of the file, it recomputes from the warehouse's tables, read in the method's order (a row held
in two tables is read once, from the first): iso_hub_prices_history, ercot_all_hub_prices_history, iso_dam_hub_prices,
iso_rtm_hub_prices, isone_dam_zone_prices, isone_rtm_zone_prices, isone_rtm_zone_prices_hourly, nyiso_dam_zone_prices,
nyiso_rtm_zone_prices:

  <m>_avg_price, <m>_negative_hours_share_pct, <m>_above_200_hours_share_pct, <m>_day_spread_top4_bottom4,
  <m>_hours_held, <m>_hours_in_window   for m = dam and rtm; an hour of real time is the mean of its four 15-minute
                                        prices, held only when all four are (ISO-NE's real time: the 15-minute means or
                                        its own hourly report, whichever holds more of the window, never mixed); a
                                        market under 95 percent of the window's hours writes no figure
  grid_carbon_intensity, grid_carbon_days_held   the mean of carbon_intensity_daily's days in the window, written
                                        where 90 percent of the window's days are held

and compares each with the file (rounded as printed: prices and shares to 0.01; counts exactly). Prints N of N.

    python replication/compare/replicate.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TABLES = ["iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices",
          "isone_dam_zone_prices", "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly", "nyiso_dam_zone_prices",
          "nyiso_rtm_zone_prices"]
BA = {"ercot": "ERCO", "spp": "SWPP", "miso": "MISO", "caiso": "CISO", "nyiso": "NYIS", "isone": "ISNE"}
TZ = {"ercot": "America/Chicago", "spp": "America/Chicago", "miso": "America/Chicago", "caiso": "America/Los_Angeles",
      "nyiso": "America/New_York", "isone": "America/New_York"}


def utc(s):
    return dt.datetime.fromisoformat(s[:19]).replace(tzinfo=dt.timezone.utc)


def read(tables_dir, entities, lo, hi):
    """{(entity, market): {form: {utc hour: [values]}}}; form 'hourly' or '15m' (ISO-NE's two real-time forms apart),
    each (entity, market, form, interval) read once, from the first table that holds it."""
    seen = set()
    out = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for t in TABLES:
        p = os.path.join(tables_dir, t + ".csv")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["entity"] not in entities or r["value"] in ("", None):
                    continue
                ts = r["ts_utc"][:19]
                if not (lo <= ts < hi):
                    continue
                market = r.get("market") or ("isone_rtm" if "rtm" in t else "")
                side = "rtm" if market.endswith("_rtm") else "dam"
                form = "15m" if r.get("freq") == "PT15M" else "hourly"
                key = (r["entity"], side, form, ts)
                if key in seen:
                    continue
                seen.add(key)
                h = utc(ts).replace(minute=0)
                out[(r["entity"], side)][form][h].append(float(r["value"]))
    return out


def hours_of(forms, side):
    """{utc hour: price} of one market: day-ahead's hourly values; real time's hours (four quarters held), from the
    form that holds more hours."""
    best = {}
    for form, hs in forms.items():
        got = {}
        for h, vals in hs.items():
            if form == "15m":
                if len(vals) == 4:
                    got[h] = round(sum(vals) / 4, 9)   # float noise away: four quarters summing to 0 are an hour of 0, not below it
            elif len(vals) == 1:
                got[h] = vals[0]
        if len(got) > len(best):
            best = got
    return best


def measures(hours, tz, start, end):
    lo = dt.datetime.combine(start, dt.time(), tzinfo=tz).astimezone(dt.timezone.utc)
    hi = dt.datetime.combine(end, dt.time(), tzinfo=tz).astimezone(dt.timezone.utc)
    in_window = round((hi - lo).total_seconds() / 3600)
    vals = {h: v for h, v in hours.items() if lo <= h < hi}
    n = len(vals)
    out = {"hours_held": n, "hours_in_window": in_window}
    if n < 0.95 * in_window:
        return out
    xs = list(vals.values())
    out["avg_price"] = sum(xs) / n
    out["negative_hours_share_pct"] = 100 * sum(1 for x in xs if x < 0) / n
    out["above_200_hours_share_pct"] = 100 * sum(1 for x in xs if x > 200) / n
    by_hour = defaultdict(list)
    for h, v in vals.items():
        by_hour[h.astimezone(tz).hour].append(v)
    avg_day = sorted(sum(v) / len(v) for v in by_hour.values())
    out["day_spread_top4_bottom4"] = sum(avg_day[-4:]) / 4 - sum(avg_day[:4]) / 4
    return out


def carbon(tables_dir, grid, start, end):
    p = os.path.join(tables_dir, "carbon_intensity_daily.csv")
    days = {}
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if r["entity"] == f"eia930:{BA[grid]}" and r["variable"] == "intensity_generation" and r["value"] not in ("", None):
                d = dt.date.fromisoformat(r["ts_utc"][:10])
                if start <= d < end:
                    days[d] = float(r["value"])
    due = (end - start).days
    out = {"days_held": len(days), "days_due": due}
    if len(days) >= 0.9 * due:
        out["intensity"] = sum(days.values()) / len(days)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The hub price comparison's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "price_compare.json"), encoding="utf-8") as f:
            pc = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    n, misses = 0, []

    def check(what, mine, theirs, tol):
        nonlocal n
        n += 1
        if mine is None and theirs is None:
            return
        if mine is None or theirs is None or abs(float(mine) - float(theirs)) > tol + 1e-9:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    for wname in ("year", "month"):
        w = pc["windows"][wname]
        start, end = dt.date.fromisoformat(w["start"]), dt.date.fromisoformat(w["end"])
        rows = pc[wname]
        ents = {r["entity"] for r in rows}
        lo = (dt.datetime.combine(start, dt.time()) - dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        hi = (dt.datetime.combine(end, dt.time()) + dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        data = read(a.tables, ents, lo, hi)
        carb = {}
        for r in rows:
            grid = r["entity"].split(":")[0]
            tz = ZoneInfo(TZ[grid])
            for side in ("dam", "rtm"):
                got = measures(hours_of(data.get((r["entity"], side), {}), side), tz, start, end)
                if f"{side}_hours_held" not in r:   # a market under the floor writes no figure and no count
                    check(f"{wname} {r['entity']} {side} under the floor", "avg_price" in got, False, 0)
                    continue
                for k in ("hours_held", "hours_in_window"):
                    check(f"{wname} {r['entity']} {side}_{k}", got.get(k), r.get(f"{side}_{k}"), 0)
                for k in ("avg_price", "negative_hours_share_pct", "above_200_hours_share_pct", "day_spread_top4_bottom4"):
                    check(f"{wname} {r['entity']} {side}_{k}", got.get(k), r.get(f"{side}_{k}"), 0.005 + 1e-6)
            if "grid_carbon_days_held" in r or "grid_carbon_intensity" in r:
                g = grid
                if g not in carb:
                    carb[g] = carbon(a.tables, g, start, end)
                c = carb[g]
                check(f"{wname} {r['entity']} grid_carbon_days_held", c["days_held"], r.get("grid_carbon_days_held"), 0)
                check(f"{wname} {r['entity']} grid_carbon_intensity", c.get("intensity"), r.get("grid_carbon_intensity"), 0.005 + 1e-6)
    print(f"Where power is cheap, from {a.tables} against price_compare.json (built {pc['built']}, through {pc['end_month']}): "
          f"{len(pc['year'])} twelve-month rows, {len(pc['month'])} month rows")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
