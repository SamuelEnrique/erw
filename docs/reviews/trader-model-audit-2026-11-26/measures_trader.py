"""Session 10209: one rule of the trader view changed at a time, each measured. Standard library only.

    measures_trader.py <dir of warehouse/output> <site dir>

Reads, never writes: the main checkout's iso_dam_hub_prices, iso_rtm_hub_prices, eia_fuel_spot_prices (26 August to
12 November 2026: under one year), and the page's own files site/public/board/h/<hub>.json and
site/public/board/s/eia-henry-hub-spot.json and site/data/board.json. Public grids only (ERCOT, CAISO, SPP).
"""
import collections
import csv
import datetime as dt
import json
import math
import os
import statistics
import sys
from zoneinfo import ZoneInfo

OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\lossa\Documents\erw\warehouse\output"
SITE = sys.argv[2] if len(sys.argv) > 2 else "site"
UTC = dt.timezone.utc
TZ = {"ercot": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles"), "spp": ZoneInfo("America/Chicago")}
MAINS = {"ercot:HB_HUBAVG", "ercot:HB_NORTH", "ercot:HB_WEST", "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND", "spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"}


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def holidays(y):
    def mon(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31 = dt.date(y, 5, 31)
    sep1 = dt.date(y, 9, 1)
    nov1 = dt.date(y, 11, 1)
    return {mon(dt.date(y, 1, 1)), may31 - dt.timedelta(days=may31.weekday()), mon(dt.date(y, 7, 4)),
            sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7), nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21),
            mon(dt.date(y, 12, 25))}


def hours_in(day, tz):
    a = dt.datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(UTC)
    n = day + dt.timedelta(days=1)
    return round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(UTC) - a).total_seconds() / 3600)


def onpeak(t, tz):
    loc = t.astimezone(tz)
    return loc.weekday() < 5 and loc.date() not in holidays(loc.year) and 6 <= loc.hour <= 21


def complete_days(hours, tz):
    """{local day: [(utc, value)]} for the days holding every hour."""
    by = collections.defaultdict(list)
    for t, v in hours.items():
        if v is not None:
            by[t.astimezone(tz).date()].append((t, v))
    return {d: sorted(hv) for d, hv in by.items() if len(hv) == hours_in(d, tz)}


def load_tables():
    da, rtq = collections.defaultdict(dict), collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows("iso_dam_hub_prices"):
        iso = r["market"].split("_")[0]
        if iso in TZ:
            da[r["entity"]][ts(r["ts_utc"])] = float(r["value"])
    for r in rows("iso_rtm_hub_prices"):
        iso = r["market"].split("_")[0]
        if iso in TZ:
            t = ts(r["ts_utc"])
            rtq[r["entity"]][t.replace(minute=0)].append((t, float(r["value"])))
    rt = {e: {h: sum(v for _, v in q) / 4 for h, q in hs.items() if len(q) == 4} for e, hs in rtq.items()}
    hh = {ts(r["ts_utc"]).date(): float(r["value"]) for r in rows("eia_fuel_spot_prices") if r["entity"] == "eia:henry_hub"}
    return da, rt, rtq, hh


def hourly_file(hid):
    f = json.load(open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8"))
    out = {}
    for m in ("da", "rt"):
        vals = f.get(m) or []
        out[m] = {dt.datetime.fromtimestamp((f["t0"] + i) * 3600, tz=UTC): v for i, v in enumerate(vals)}
    return out, ZoneInfo(f["tz"])


def gas_for(day, hh, back):
    """Henry Hub of the newest trading date from day-back to day-back-4 (the code: back 0)."""
    for k in range(back, back + 5):
        d = day - dt.timedelta(days=k)
        if d in hh:
            return hh[d], d
    return None, None


def main():
    da, rt, rtq, hh = load_tables()
    ents = sorted(e for e in da if e.split(":")[0] in TZ)
    print("hubs read:", len(ents), "Henry Hub to", max(hh))

    # 1. the off-peak week: the mean of 7 daily off-peak means (the code) against the mean of the week's off-peak hours
    print("\n--- 1. Off-peak week: mean of daily means (the page) against hour-weighted (every off-peak hour of the 7 days counts once)")
    for e in ents:
        iso = e.split(":")[0]
        tz = TZ[iso]
        days = complete_days(da[e], tz)
        ds = sorted(days)
        gaps = []
        for i in range(6, len(ds)):
            wk = ds[i - 6:i + 1]
            if (wk[-1] - wk[0]).days > 10:
                continue
            daily, allh = [], []
            for d in wk:
                off = [v for t, v in days[d] if not onpeak(t, tz)]
                daily.append(sum(off) / len(off))
                allh += off
            gaps.append((sum(allh) / len(allh)) - (sum(daily) / 7))
        if gaps and e in MAINS:
            print(f"  {e:26s} {len(gaps)} weeks to {ds[-1]}: hour-weighted less the page's, mean {statistics.mean(gaps):+.2f}, mean absolute {statistics.mean(abs(g) for g in gaps):.2f}, largest {max(gaps, key=abs):+.2f} USD/MWh")

    # 1b. the same on the page's hourly files for the week the board of 25 November shows
    print("\n  the week on the board of 25 November, from the page's hourly files:")
    for hid in ("caiso-th-sp15-gen-apnd", "caiso-th-np15-gen-apnd", "spp-sppnorth-hub", "spp-sppsouth-hub", "ercot-hb-hubavg"):
        f, tz = hourly_file(hid)
        days = complete_days(f["da"], tz)
        wk = sorted(days)[-7:]
        daily, allh = [], []
        for d in wk:
            off = [v for t, v in days[d] if not onpeak(t, tz)]
            daily.append(sum(off) / len(off))
            allh += off
        print(f"  {hid:24s} {wk[0]} to {wk[-1]}: the page's way {sum(daily) / 7:.2f}, hour-weighted {sum(allh) / len(allh):.2f} ({len(allh)} hours), gap {sum(allh) / len(allh) - sum(daily) / 7:+.2f}")

    # 2. the implied heat rate's gas day
    print("\n--- 2. Implied heat rate: Henry Hub of the operating day's own trading date (the code) against the trading date before it")
    print("     (EIA's daily Henry Hub is dated by the trading date, gas for next-day flow; the day-ahead power market for day D trades on D-1)")
    for e in ents:
        if e not in MAINS:
            continue
        tz = TZ[e.split(":")[0]]
        days = complete_days(da[e], tz)
        diffs, n_diff_gas = [], 0
        for d in sorted(days):
            m = sum(v for _, v in days[d]) / len(days[d])
            g0, d0 = gas_for(d, hh, 0)
            g1, d1 = gas_for(d, hh, 1)
            if g0 and g1:
                diffs.append(m / g0 - m / g1)
                n_diff_gas += d0 != d1 and g0 != g1
        print(f"  {e:26s} {len(diffs)} days: heat rate (code) less heat rate (the day before), mean {statistics.mean(diffs):+.3f}, mean absolute {statistics.mean(abs(x) for x in diffs):.3f}, largest {max(diffs, key=abs):+.3f} MMBtu/MWh; days on another gas price {n_diff_gas}")
    # the gas behind the heat-rate week on the board of 25 November
    s = json.load(open(os.path.join(SITE, "public", "board", "s", "eia-henry-hub-spot.json"), encoding="utf-8"))
    t0 = dt.date.fromisoformat(s["t0"]) if isinstance(s["t0"], str) else dt.date(1970, 1, 1) + dt.timedelta(days=s["t0"])
    hhs = {t0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}
    last = max(hhs)
    print(f"\n  the board's Henry Hub series ends {last}; the heat-rate week of the board of 25 November ends 2026-11-21:")
    for k in range(6, -1, -1):
        d = dt.date(2026, 11, 21) - dt.timedelta(days=k)
        g, gd = gas_for(d, hhs, 0)
        print(f"    {d} ({d.strftime('%a')}): gas of {gd} ({(d - gd).days} days before)" if gd else f"    {d}: none")

    # 3. the heat-rate week: the mean of daily ratios against the week's mean price over the week's mean gas
    print("\n--- 3. Heat-rate week: mean of 7 daily ratios (the page) against the week's mean day-ahead over the mean gas of those days")
    for e in ents:
        if e not in MAINS:
            continue
        tz = TZ[e.split(":")[0]]
        days = complete_days(da[e], tz)
        ds = sorted(days)
        gaps = []
        for i in range(6, len(ds)):
            wk = ds[i - 6:i + 1]
            ms = [sum(v for _, v in days[d]) / len(days[d]) for d in wk]
            gs = [gas_for(d, hh, 0)[0] for d in wk]
            if None in gs:
                continue
            gaps.append(statistics.mean(m / g for m, g in zip(ms, gs)) - statistics.mean(ms) / statistics.mean(gs))
        print(f"  {e:26s} {len(gaps)} weeks: page less ratio of means, mean {statistics.mean(gaps):+.3f}, largest {max(gaps, key=abs):+.3f}")

    # 4. volatility
    print("\n--- 4. 30-day volatility: the page's USD standard deviation of daily changes against a trader's measures")
    for hid in ("caiso-th-sp15-gen-apnd", "caiso-th-np15-gen-apnd", "caiso-th-zp26-gen-apnd", "spp-sppnorth-hub", "spp-sppsouth-hub", "ercot-hb-hubavg", "ercot-hb-north", "ercot-hb-west"):
        f, tz = hourly_file(hid)
        days = complete_days(f["da"], tz)
        means = {d: sum(v for _, v in hv) / len(hv) for d, hv in days.items()}
        ds = sorted(means)
        end = ds[-1]
        win = [end - dt.timedelta(days=k) for k in range(30, -1, -1)]
        line = f"  {hid:24s}"
        if all(d in means for d in win):
            ch = [means[win[i]] - means[win[i - 1]] for i in range(1, 31)]
            sdv = statistics.stdev(ch)
            avg = statistics.mean(means[d] for d in win)
            line += f" to {end}: page {sdv:.4f} USD/MWh ({100 * sdv / avg:.1f} percent of the 31 days' mean {avg:.2f})"
            if all(means[d] > 0 for d in win):
                lr = [math.log(means[win[i]] / means[win[i - 1]]) for i in range(1, 31)]
                line += f"; log returns {statistics.stdev(lr):.4f} a day, annualized x sqrt(365) {100 * statistics.stdev(lr) * math.sqrt(365):.0f} percent"
            else:
                line += "; a day at or below zero: no log return"
            wkday = [means[win[i]] - means[win[i - 7]] for i in range(7, 31)]
            line += f"; 7-day changes {statistics.stdev(wkday):.2f}"
        else:
            held = [d for d in win if d in means]
            last31 = ds[-31:]
            ch = [means[last31[i]] - means[last31[i - 1]] for i in range(1, 31)]
            line += f" to {end}: 31 calendar days not whole ({31 - len(held)} missing: {[str(d) for d in win if d not in means]}); the newest 31 held days ({last31[0]} to {last31[-1]}) give {statistics.stdev(ch):.4f}"
        print(line)

    # 5. hours real time ran 50 over day-ahead: the hour's mean against any of its intervals
    print("\n--- 5. Hours real time over day-ahead + 50: the hour's mean of 4 intervals (the code) against any interval of the hour")
    for e in ents:
        if e not in MAINS or e.split(":")[0] == "spp":
            continue
        hm = ha = 0
        for h, q in rtq[e].items():
            if len(q) == 4 and h in da[e]:
                d = da[e][h]
                hm += (sum(v for _, v in q) / 4 - d) > 50
                ha += any(v - d > 50 for _, v in q)
        print(f"  {e:26s} hours by the mean {hm}, hours with an interval over {ha} ({'x%.1f' % (ha / hm) if hm else 'n/a'})")

    # 6. SPP's real-time metrics: what the week would show from the page's own hourly file
    print("\n--- 6. SPP: the real-time week the method's rule makes from the page's hourly file (the page shows 'not held yet')")
    for hid in ("spp-sppnorth-hub", "spp-sppsouth-hub"):
        f, tz = hourly_file(hid)
        dd = complete_days(f["da"], tz)
        rr = complete_days(f["rt"], tz)
        both = sorted(d for d in dd if d in rr and len(rr[d]) == len(dd[d]))
        wk = both[-7:]
        spreads = {d: [r - a for (t, a), (_, r) in zip(dd[d], rr[d])] for d in wk}
        means = [statistics.mean(spreads[d]) for d in wk]
        print(f"  {hid}: days with both markets whole, newest {both[-1] if both else None}; the latest 7 {wk[0]} to {wk[-1]}: RT minus DA week {statistics.mean(means):+.2f}, largest hourly {max(max(s) for s in spreads.values()):.2f}, hours over DA + 50: {sum(sum(1 for x in s if x > 50) for s in spreads.values())}")
        prev = both[-14:-7]
        if len(prev) == 7:
            pm = [statistics.mean([r - a for (t, a), (_, r) in zip(dd[d], rr[d])]) for d in prev]
            print(f"      change on the 7 before ({prev[0]} to {prev[-1]}): {statistics.mean(means) - statistics.mean(pm):+.2f}")

    # 7. the windows the week's columns cover on the board of 25 November
    b = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
    print("\n--- 7. The windows of one row's columns on the board of", b["built"])
    for w in b["week"]:
        if w["hub"] in ("caiso-th-sp15-gen-apnd", "ercot-hb-hubavg", "spp-sppnorth-hub"):
            print(f"  {w['hub']}: " + "; ".join(f"{k} ends {m['end']}" for k, m in w["means"].items()) + f"; volatility as of {w.get('vol', {}).get('t')}")


if __name__ == "__main__":
    main()
