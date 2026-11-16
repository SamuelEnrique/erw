#!/usr/bin/env python3
"""ERW, curtailment (/curtailment): an independent replication of the page's files (session 7014, chain 301; the done
line's tool 23). Part one, California by the hour (site/data/curtailment_profile.json); part two, Texas below the High
Sustained Limit (site/data/curtailment/ercot.json).

Part one, written from docs/methods/caiso_curtailment_intervals.md ("caiso_curtailment_profile") and the table
caiso_curtailment_intervals alone: a day is held when the table has its day rows; to 2025 an interval's MWh is its MW
over twelve (five minutes), with no reason (curtailed_<fuel>_mw, "unspecified") or with CAISO's (local, system); from
2026 each hour's MWh by category (econ, ss, oi) and reason; all dated in Pacific time. A month is written when at least
90 percent of its days are held, its figures sums over those days, never scaled up: by fuel, by reason, by category, by
local hour. The batteries (caiso_battery_storage, five-minute, positive is discharge): an hour is held with all twelve
values, a day with every hour; charging is the part below zero, as a positive number; for the days both tables hold, the
average day of curtailment and of charging by hour, their sums, and the share of the curtailed MWh in hours the
batteries charged on balance, written for a month with 90 percent of its days held by both. A year is the sum of its
months when every month of the year to date is held.

Part two, written from docs/methods/curtailment.md ("Texas: nine days, by the hour") and ercot_wind_solar_hsl_hourly:
output below the limit is max(0, HSL less output) each hour, wind and solar each on its own (a fuel's hour counts in its
day's sums when that fuel has both values); a day is the Central clock day and is whole when every one of its hours
holds all four.

    python replication/curtailment/replicate.py [--tables DIR] [--site DIR]

Figures are compared to half a unit of their printed last decimal. Exit 0 when every figure is equal, 1 when one is not,
2 when the inputs cannot be read. Standard library only.
"""
import argparse
import calendar
import csv
import datetime as dt
import json
import math
import os
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UTC = dt.timezone.utc
PT = ZoneInfo("America/Los_Angeles")
CT = ZoneInfo("America/Chicago")
FUELS = ("solar", "wind")


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def utc(s):
    return dt.datetime.fromisoformat(s[:19]).replace(tzinfo=UTC)


def decimals(x):
    s = repr(float(x))
    return 0 if "e" in s else len(s.split(".")[1])


def hours_in(day, tz):
    a = dt.datetime.combine(day, dt.time(), tzinfo=tz).astimezone(UTC)
    b = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(), tzinfo=tz).astimezone(UTC)
    return round((b - a).total_seconds() / 3600)


def profile(tables):
    days = set()
    day_mwh = defaultdict(lambda: defaultdict(float))   # day -> key -> MWh
    hour_mwh = defaultdict(float)                         # (day, local hour start UTC) -> curtailed MWh, both fuels
    for r in rows_of(os.path.join(tables, "caiso_curtailment_intervals.csv")):
        var, v = r["variable"], r["value"]
        if v in ("", None):
            continue
        v = float(v)
        if var.endswith("_day_mwh"):
            days.add(dt.date.fromisoformat(r["ts_utc"][:10]))
            continue
        t = utc(r["ts_utc"])
        lt = t.astimezone(PT)
        d, h = lt.date(), lt.hour
        parts = var.split("_")      # curtailed_<fuel>[_<cat>]_[<reason>_]mw|mwh
        fuel = parts[1]
        if var.endswith("_mwh"):    # 2026 on: hourly, by category and reason
            cat, reason, mwh = parts[2], parts[3], v
            day_mwh[d][f"curtailed_{fuel}_{cat}_mwh"] += mwh
        else:
            reason = parts[2] if len(parts) == 4 else "unspecified"
            mwh = v / 12
        day_mwh[d][f"curtailed_{fuel}_{reason}_mwh"] += mwh
        day_mwh[d][f"curtailed_{fuel}_mwh"] += mwh
        day_mwh[d][f"curtailed_{fuel}_mwh_h{h:02d}"] += mwh
        hour_mwh[(d, t.replace(minute=0))] += mwh
    # the batteries
    bat = defaultdict(list)
    for r in rows_of(os.path.join(tables, "caiso_battery_storage.csv")):
        if r["variable"] != "batteries_mw" or r["value"] in ("", None):
            continue
        t = utc(r["ts_utc"])
        bat[t.replace(minute=0)].append(float(r["value"]))
    bat_hours = {t: xs for t, xs in bat.items() if len(xs) == 12}
    bat_day_hours = defaultdict(int)
    for t in bat_hours:
        bat_day_hours[t.astimezone(PT).date()] += 1
    bat_days = {d for d, n in bat_day_hours.items() if n == hours_in(d, PT)}
    months = defaultdict(list)
    first = min(days)
    d = first.replace(day=1)
    last = max(days)
    out = {}
    while d <= last:
        y, m = d.year, d.month
        n_days = calendar.monthrange(y, m)[1]
        held = [d.replace(day=k) for k in range(1, n_days + 1) if d.replace(day=k) in days]
        if len(held) >= 0.9 * n_days:
            f = defaultdict(float)
            f["days_held"], f["days_in_month"] = len(held), n_days
            for x in held:
                for k, v in day_mwh[x].items():
                    f[k] += v
            both = [x for x in held if x in bat_days]
            if len(both) >= 0.9 * n_days:
                f["battery_days_held"] = len(both)
                cur_h, chg_h = defaultdict(float), defaultdict(float)
                cur_all = chg_all = cur_charging = 0.0
                for x in both:
                    a = dt.datetime.combine(x, dt.time(), tzinfo=PT).astimezone(UTC)
                    for i in range(hours_in(x, PT)):
                        t = a + dt.timedelta(hours=i)
                        hh = t.astimezone(PT).hour
                        c = hour_mwh.get((x, t), 0.0)
                        xs = bat_hours[t]
                        ch = sum(max(0.0, -v) for v in xs) / 12
                        cur_h[hh] += c
                        chg_h[hh] += ch
                        cur_all += c
                        chg_all += ch
                        if sum(xs) < 0:
                            cur_charging += c
                for hh in range(24):
                    f[f"avg_curtailed_mw_h{hh:02d}"] = cur_h[hh] / len(both)
                    f[f"avg_battery_charging_mw_h{hh:02d}"] = chg_h[hh] / len(both)
                f["curtailed_mwh_battery_days"] = cur_all
                f["battery_charging_mwh"] = chg_all
                f["curtailed_while_charging_share_pct"] = 100 * cur_charging / cur_all if cur_all else None
            out[f"{y:04d}-{m:02d}"] = f
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out, days


def main(argv=None):
    ap = argparse.ArgumentParser(description="The curtailment page's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "curtailment_profile.json"), encoding="utf-8") as f:
            prof = json.load(f)
        with open(os.path.join(a.site, "data", "curtailment", "ercot.json"), encoding="utf-8") as f:
            erc = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    n, misses = 0, []

    def check(what, mine, theirs):
        nonlocal n
        n += 1
        if isinstance(theirs, (int, float)) and isinstance(mine, (int, float)) and not isinstance(theirs, bool):
            ok = abs(mine - theirs) <= 0.5 * 10 ** -decimals(theirs) + 1e-6
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    # part one
    mine, days = profile(a.tables)
    built_last = prof["last_day"]
    check("profile last_day", max(d for d in days if d.isoformat() <= built_last).isoformat(), built_last)
    for mk, theirs in prof["months"].items():
        f = mine.get(mk, {})
        for k, v in theirs.items():
            check(f"profile {mk} {k}", f.get(k, 0.0 if k.startswith("curtailed_") else None), v)
    newer = sorted(k for k in mine if k > prof["last"])
    # part two: the system's hours, and the Central days
    sysh = defaultdict(dict)
    for r in rows_of(os.path.join(a.tables, "ercot_wind_solar_hsl_hourly.csv")):
        if r["entity"] == "ercot:system" and r["value"] not in ("", None):
            sysh[utc(r["ts_utc"])][r["variable"]] = float(r["value"])
    first_h, last_h = utc(erc["first_hour"]), utc(erc["last_hour"])
    held = {t: x for t, x in sysh.items() if first_h <= t <= last_h and len(x) == 4}
    check("ercot hours_held", len(held), erc["hours_held"])
    theirs_h = {h["ts"]: h for h in erc["hours"]}
    for t, x in sorted(held.items()):
        h = theirs_h.get(t.strftime("%Y-%m-%dT%H:%M:%SZ"), {})
        for fuel in ("wind", "solar"):
            check(f"ercot {t:%Y-%m-%d %H} {fuel}_gen", x[f"{fuel}_generation_mw"], h.get(f"{fuel}_gen"))
            check(f"ercot {t:%Y-%m-%d %H} {fuel}_hsl", x[f"{fuel}_hsl_mw"], h.get(f"{fuel}_hsl"))
    dd = defaultdict(lambda: defaultdict(float))
    for t, x in sysh.items():   # a fuel's hour counts when that fuel has both its values; the day's hours, all four
        if not first_h <= t <= last_h:
            continue
        d = t.astimezone(CT).date()
        dd[d]["n"] += len(x) == 4
        for fuel in ("wind", "solar"):
            if f"{fuel}_generation_mw" not in x or f"{fuel}_hsl_mw" not in x:
                continue
            g, l = x[f"{fuel}_generation_mw"], x[f"{fuel}_hsl_mw"]
            dd[d][f"{fuel}_g"] += g
            dd[d][f"{fuel}_l"] += l
            dd[d][f"{fuel}_b"] += max(0.0, l - g)
            dd[d][f"{fuel}_a"] += max(0.0, g - l)
    for day, theirs in erc["days"].items():
        d = dt.date.fromisoformat(day)
        m = dd.get(d, {})
        check(f"ercot day {day} hours_held", int(m.get("n", 0)), theirs["hours_held"])
        check(f"ercot day {day} hours_in_day", hours_in(d, CT), theirs["hours_in_day"])
        check(f"ercot day {day} whole", m.get("n", 0) == hours_in(d, CT), theirs["whole"])
        for fuel in ("wind", "solar"):
            tf = theirs.get(fuel) or {}
            for k, mk in (("generation_mwh", "g"), ("hsl_mwh", "l"), ("below_hsl_mwh", "b"), ("above_hsl_mwh", "a")):
                if k in tf:
                    check(f"ercot day {day} {fuel} {k}", m.get(f"{fuel}_{mk}", 0.0), tf[k])
            if "share_pct" in tf and m.get(f"{fuel}_l"):
                check(f"ercot day {day} {fuel} share_pct", 100 * m[f"{fuel}_b"] / m[f"{fuel}_l"], tf["share_pct"])
    # part three (session 7019): CAISO's shares of the months whose output is CAISO's own supply data (basis
    # caiso_fuel_supply): curtailed over curtailed plus solar and wind output, over the Pacific days both tables hold
    shares_n = 0
    sp = os.path.join(a.site, "data", "curtailment", "shares.json")
    if os.path.exists(sp):
        with open(sp, encoding="utf-8") as f:
            sh = json.load(f)["grids"]["caiso"]["months"]
        cur, cdays = defaultdict(float), set()
        for r in rows_of(os.path.join(a.tables, "caiso_curtailment_daily.csv")):
            if r["variable"] in ("curtailed_solar_mwh", "curtailed_wind_mwh") and r["value"] not in ("", None):
                cur[r["ts_utc"][:10]] += float(r["value"])
                cdays.add(r["ts_utc"][:10])
        out, hrs = defaultdict(float), defaultdict(set)
        for r in rows_of(os.path.join(a.tables, "caiso_fuel_supply.csv")):
            if r["variable"] in ("solar_mw", "wind_mw") and r["value"] not in ("", None):
                t = utc(r["ts_utc"]).astimezone(PT)
                out[t.date().isoformat()] += float(r["value"])
                hrs[t.date().isoformat()].add((t.hour, t.utcoffset()))
        for m, s_ in sorted(sh.items()):
            if s_.get("basis") != "caiso_fuel_supply" or "share_pct" not in s_:
                continue
            days = [d for d in cdays if d.startswith(m) and d in out]
            c, o = math.fsum(cur[d] for d in days), math.fsum(out[d] for d in days)
            shares_n += 1
            check(f"shares caiso {m} days_held", len(days), s_["days_held"])
            check(f"shares caiso {m} hours_held", sum(len(hrs[d]) for d in days), s_["hours_held"])
            check(f"shares caiso {m} curtailed_mwh", c, s_["curtailed_mwh"])
            check(f"shares caiso {m} output_mwh", o, s_["output_mwh"])
            check(f"shares caiso {m} share_pct", 100 * c / (c + o) if c + o else None, s_["share_pct"])
    print(f"Curtailment: California's profile (built {prof['built']}, months {prof['first']} to {prof['last']}) and "
          f"Texas's hours (built {erc['built']}) and CAISO's shares of {shares_n} months on CAISO's own supply data against the tables in {a.tables}. The table holds {len(newer)} whole "
          f"month(s) newer than the profile's last: {', '.join(newer) or 'none'}")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
