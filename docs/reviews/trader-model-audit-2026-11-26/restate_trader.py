"""Session 10209 (chain 710, part D): the trader view restated independently, standard library only.

Written from docs/methods/trader_view.md and docs/methods/iso_trader_daily.md, not from warehouse/derived/trader_view.py.
Reads, never writes, the main checkout's tables (paths passed on the command line):

    restate_trader.py <dir of warehouse/output>

Part 1: every row of iso_trader_daily (ERCOT, CAISO, SPP: public; MISO: counts only, never a value) made again from
        iso_dam_hub_prices, iso_rtm_hub_prices and eia_fuel_spot_prices, each variable compared to the 4th decimal.
Part 2: the clock-change days held in the price tables: hours a local day holds, and whether a row is written.
Part 3: iso_rt_top_intervals (the snapshot on disk) made again for ERCOT and CAISO, and the rule "every interval of
        every hub" against "every interval time held by some hub".
NYISO and ISO-NE are not read (held, and their inputs are other tables).
"""
import collections
import csv
import datetime as dt
import math
import os
import sys
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\lossa\Documents\erw\warehouse\output"
PUBLIC = {"ercot", "caiso", "spp"}
HELD = {"miso"}
TZ = {"ercot": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles"),
      "spp": ZoneInfo("America/Chicago"), "miso": dt.timezone(dt.timedelta(hours=-5))}
Q = Decimal("0.0001")
UTC = dt.timezone.utc


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        body = (line for line in f if not line.startswith("#"))
        yield from csv.DictReader(body)


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def iso_of(market):
    return market.split("_")[0]


def holidays(y):
    """NERC's six, written a second way: fixed dates, then the Monday rules by arithmetic on the month's first or last day."""
    def monday_rule(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31 = dt.date(y, 5, 31)
    memorial = may31 - dt.timedelta(days=may31.weekday())
    sep1 = dt.date(y, 9, 1)
    labor = sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7)
    nov1 = dt.date(y, 11, 1)
    thanks = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21)
    return {monday_rule(dt.date(y, 1, 1)), memorial, monday_rule(dt.date(y, 7, 4)), labor, thanks, monday_rule(dt.date(y, 12, 25))}


def hours_in(day, tz):
    a = dt.datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(UTC)
    n = day + dt.timedelta(days=1)
    b = dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(UTC)
    return round((b - a).total_seconds() / 3600)


def r4(x):
    return x.quantize(Q, rounding=ROUND_HALF_UP)


def sd(xs):
    m = sum(xs, Decimal(0)) / len(xs)
    v = sum(((x - m) ** 2 for x in xs), Decimal(0)) / (len(xs) - 1)
    return v.sqrt()


def main():
    # day-ahead hours: (iso, entity) -> {utc hour: Decimal}
    da = collections.defaultdict(dict)
    for r in rows("iso_dam_hub_prices"):
        iso = iso_of(r["market"])
        if iso in PUBLIC | HELD:
            da[(iso, r["entity"])][ts(r["ts_utc"])] = Decimal(r["value"])
    # real time: 15-minute intervals or hours
    rt_raw = collections.defaultdict(dict)
    freq_of = {}
    for r in rows("iso_rtm_hub_prices"):
        iso = iso_of(r["market"])
        if iso in PUBLIC | HELD:
            rt_raw[(iso, r["entity"])][ts(r["ts_utc"])] = Decimal(r["value"])
            freq_of[iso] = r["freq"]
    print("day-ahead hubs:", collections.Counter(k[0] for k in da), "real-time hubs:", collections.Counter(k[0] for k in rt_raw), "freq:", freq_of)
    rt = {}
    for key, d in rt_raw.items():
        hours = collections.defaultdict(list)
        for t, v in d.items():
            hours[t.replace(minute=0)].append(v)
        if freq_of[key[0]] == "PT1H":
            rt[key] = {h: vs[0] for h, vs in hours.items()}
        else:
            rt[key] = {h: sum(vs, Decimal(0)) / 4 for h, vs in hours.items() if len(vs) == 4}
    hh = {}
    for r in rows("eia_fuel_spot_prices"):
        if r["entity"] == "eia:henry_hub":
            hh[ts(r["ts_utc"]).date()] = Decimal(r["value"])
    print("Henry Hub days:", len(hh), "from", min(hh), "to", max(hh))

    mine = {}  # (iso, entity, variable, day) -> Decimal unrounded
    dst_lines = []
    for (iso, ent), hrs in da.items():
        tz = TZ[iso]
        byday = collections.defaultdict(list)
        for t, v in hrs.items():
            byday[t.astimezone(tz).date()].append((t, v))
        means = {}
        for day, hv in byday.items():
            want = hours_in(day, tz)
            if want != 24 and iso in PUBLIC:
                dst_lines.append(f"  {iso} {ent} {day}: {len(hv)} hours held, {want} in the local day; written: {len(hv) == want}")
            if len(hv) != want:
                continue
            hv.sort()
            vals = [v for _, v in hv]
            m = sum(vals, Decimal(0)) / len(vals)
            means[day] = m
            mine[(iso, ent, "da_mean_usd", day)] = m
            work = day.weekday() < 5 and day not in holidays(day.year)
            on = [v for t, v in hv if work and 6 <= t.astimezone(tz).hour <= 21]
            off = [v for t, v in hv if not (work and 6 <= t.astimezone(tz).hour <= 21)]
            if on:
                mine[(iso, ent, "da_onpeak_mean_usd", day)] = sum(on, Decimal(0)) / len(on)
            if off:
                mine[(iso, ent, "da_offpeak_mean_usd", day)] = sum(off, Decimal(0)) / len(off)
            rth = rt.get((iso, ent))
            if rth and all(t in rth for t, _ in hv):
                sp = [rth[t] - v for t, v in hv]
                mine[(iso, ent, "rt_mean_usd", day)] = sum((rth[t] for t, _ in hv), Decimal(0)) / len(hv)
                mine[(iso, ent, "da_rt_spread_mean_usd", day)] = sum(sp, Decimal(0)) / len(sp)
                mine[(iso, ent, "da_rt_spread_max_usd", day)] = max(sp)
                mine[(iso, ent, "hours_rt_over_da_50", day)] = Decimal(sum(1 for s in sp if s > 50))
            for k in range(5):
                g = hh.get(day - dt.timedelta(days=k))
                if g is not None:
                    if g > 0:
                        mine[(iso, ent, "implied_heat_rate", day)] = m / g
                    break
        for day in means:
            win = [day - dt.timedelta(days=k) for k in range(31)]
            if all(d in means for d in win):
                win.reverse()
                ch = [means[win[i]] - means[win[i - 1]] for i in range(1, 31)]
                mine[(iso, ent, "da_volatility_30d_usd", day)] = sd(ch)

    # compare with iso_trader_daily
    theirs = {}
    for r in rows("iso_trader_daily"):
        iso = r["market"]
        if iso in PUBLIC | HELD:
            theirs[(iso, r["entity"], r["variable"], ts(r["ts_utc"]).date())] = Decimal(r["value"])
    span = {}
    for (iso, ent, var, day) in theirs:
        lo, hi = span.get(iso, (day, day))
        span[iso] = (min(lo, day), max(hi, day))
    print("iso_trader_daily spans:", {k: (str(a), str(b)) for k, (a, b) in span.items()})
    n = collections.Counter()
    exact = collections.Counter()
    near = collections.Counter()
    worst = collections.defaultdict(lambda: (Decimal(0), None))
    missing_mine = collections.Counter()
    for key, v in theirs.items():
        iso, ent, var, day = key
        tag = ("held " if iso in HELD else "") + var
        m = mine.get(key)
        if m is None:
            missing_mine[tag] += 1
            continue
        n[tag] += 1
        g = abs(r4(m) - v)
        if g == 0:
            exact[tag] += 1
        if g <= Q:
            near[tag] += 1
        if g > worst[tag][0]:
            worst[tag] = (g, key if iso in PUBLIC else (iso, "(held)", var, day))
    print("\n--- Part 1: iso_trader_daily restated (rounded half up to 4 decimals, compared)")
    for tag in sorted(n):
        w = worst[tag]
        print(f"  {tag:34s} {n[tag]:6d} compared, {exact[tag]:6d} exact, {near[tag]:6d} within 0.0001, largest gap {w[0]} {w[1] if w[0] > 0 else ''}")
    for key, v in sorted(theirs.items()):
        if key[0] in PUBLIC and key[2] == "implied_heat_rate" and key in mine and r4(mine[key]) != v:
            iso, ent, var, day = key
            used = next((day - dt.timedelta(days=k) for k in range(5) if day - dt.timedelta(days=k) in hh), None)
            dam = r4(mine[(iso, ent, "da_mean_usd", day)])
            back = (dam / v).quantize(Decimal("0.001")) if v else None
            print(f"    heat rate {ent} {day}: table {v}, restated {r4(mine[key])}; gas today's file takes {used} ({hh.get(used)}); the table's implies gas {back}")
    absent_days = collections.defaultdict(set)
    for (iso, ent, var, day) in mine:
        if iso in PUBLIC and iso in span and span[iso][0] <= day <= span[iso][1] and (iso, ent, var, day) not in theirs:
            absent_days[(iso, var)].add(day)
    for (iso, var), ds in sorted(absent_days.items()):
        print(f"    absent from the table, restated today: {iso} {var} on {sorted(str(d) for d in ds)}")
    for tag, c in sorted(missing_mine.items()):
        print(f"  in the table, not restated: {tag} {c} (the price tables on disk do not hold the day whole)")
    # rows I make inside the table's span that the table lacks
    extra = collections.Counter()
    for (iso, ent, var, day) in mine:
        if iso in span and span[iso][0] <= day <= span[iso][1] and (iso, ent, var, day) not in theirs:
            extra[("held " if iso in HELD else "") + var] += 1
    for tag, c in sorted(extra.items()):
        print(f"  restated inside the table's span, absent from the table: {tag} {c}")
    # SPP's real time
    spp_rt = [k for k in mine if k[0] == "spp" and k[2] == "rt_mean_usd"]
    print(f"  SPP real-time metrics the method's rule makes from iso_rtm_hub_prices (spp_rtm) on disk: {len(spp_rt)} rows; in the table: {sum(1 for k in theirs if k[0] == 'spp' and k[2] == 'rt_mean_usd')}")

    print("\n--- Part 2: clock-change days in the price tables (public grids)")
    for line in sorted(dst_lines):
        print(line)

    # Part 3: the top intervals
    print("\n--- Part 3: iso_rt_top_intervals restated (ERCOT, CAISO)")
    snap = collections.defaultdict(list)
    for r in rows("iso_rt_top_intervals"):
        snap[r["market"]].append((ts(r["ts_utc"]), Decimal(r["value"]), r["entity"]))
    for iso in ("ercot", "caiso"):
        tz = TZ[iso]
        last_snap = max(t for t, _, _ in snap[iso]).astimezone(tz).date()
        ents = [k for k in rt_raw if k[0] == iso]
        step = 15
        per_day_any = collections.defaultdict(set)
        per_day_hub = collections.defaultdict(lambda: collections.defaultdict(int))
        for k in ents:
            for t in rt_raw[k]:
                d = t.astimezone(tz).date()
                per_day_any[d].add(t)
                per_day_hub[d][k[1]] += 1
        full_any, full_every = [], []
        for d in sorted(per_day_any):
            want = hours_in(d, tz) * 60 // step
            if len(per_day_any[d]) == want:
                full_any.append(d)
                if len(per_day_hub[d]) == len(ents) and all(c == want for c in per_day_hub[d].values()):
                    full_every.append(d)
        thin = [d for d in full_any if d not in full_every]
        print(f"  {iso}: {len(full_any)} days complete in interval times held by some hub, {len(full_every)} complete for every hub; days that pass the code's rule but not the note's: {[str(d) for d in thin][:12]}")
        # the snapshot's own week from its header line "Weeks: ercot A to B (...)"
        with open(os.path.join(OUT, "iso_rt_top_intervals.csv"), encoding="utf-8") as f:
            wl = next(line for line in f if line.startswith("# Weeks:"))
        part = wl.split(f" {iso} ", 1)[1].split(" (", 1)[0]
        a, b = (dt.date.fromisoformat(x) for x in part.split(" to "))
        week = [d for d in full_any if a <= d <= b]
        print(f"  {iso}: the header's week {a} to {b}; days complete in today's table within it: {len(week)} (the code took 7, so on its run day {len(week) - 7} of them was not complete)")
        pool = []
        for k in ents:
            for t, v in rt_raw[k].items():
                if t.astimezone(tz).date() in week:
                    pool.append((v, t, k[1]))
        pool.sort(key=lambda x: (-x[0], x[1]))
        top = pool[:10]
        theirs_top = sorted(snap[iso], key=lambda x: (-x[1], x[0]))
        same = sum(1 for a, b in zip(top, theirs_top) if a[0] == b[1] and a[1] == b[0])
        print(f"  {iso}: week {week[0]} to {week[-1]} ({len(week)} days, {(week[-1] - week[0]).days + 1} calendar days); the 10 restated against the snapshot: {same} of {len(theirs_top)} the same value and interval")
        for a, b in zip(top, theirs_top):
            if not (a[0] == b[1] and a[1] == b[0]):
                print(f"    mine {a[1]} {a[2]} {a[0]}  snapshot {b[0]} {b[2]} {b[1]}")


if __name__ == "__main__":
    main()
