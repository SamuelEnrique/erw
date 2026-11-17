#!/usr/bin/env python3
"""ERW, ruling impact for /explore/ercot-peak-premium (session 7576, 17 November 2026).

The two lines marked "Changes a figure" under the explorer in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads):

  1. the page holds medians of a 16:00 to 21:00 block of every day: build a mean, or the traded 06:00 to 22:00 weekday
     block, so it can be set beside published figures;
  2. the two tables are computed by hand on the data machine: compute them on a schedule.

ERCOT's 15-minute real-time prices at the hubs (ercot_all_hub_prices_history and iso_rtm_hub_prices, market ercot_rtm,
warehouse/output), read by replication/ercot_peak_premium/from_hourly.py's rules (imported). ERCOT's hourly system load
(ercot_zone_load_hourly, entity ercot:system) weights a load-weighted mean.

    .venv/Scripts/python.exe runs/ruling_impact/ercot-peak-premium_impact.py
"""
import array
import csv
import datetime
import importlib.util
import os
import statistics
import sys
import zoneinfo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "replication", "ercot_peak_premium"))
spec = importlib.util.spec_from_file_location("fh", os.path.join(ROOT, "replication", "ercot_peak_premium", "from_hourly.py"))
fh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fh)
OUT = os.path.join(ROOT, "warehouse", "output")
CHI = zoneinfo.ZoneInfo("America/Chicago")
UTC = datetime.timezone.utc
HUB = "ercot:HB_HUBAVG"
TABLE_CUT = fh.header_value(os.path.join(OUT, "ercot_peak_premium_monthly.csv"), "Last input interval:").split(";")[0].strip()

# ---- the prices of the default hub, with their local hour and weekday, and the load of each UTC hour
load = {}
for r in csv.DictReader(fh.data_lines(os.path.join(OUT, "ercot_zone_load_hourly.csv"))):
    if r["entity"] == "ercot:system":
        load[r["ts_utc"][:13]] = float(r["value"])
by_year = {}
seen = set()
last_ts = ""
for name in fh.INPUTS:
    rd = csv.reader(fh.data_lines(os.path.join(OUT, name + ".csv")))
    ix = {k: i for i, k in enumerate(next(rd))}
    for r in rd:
        if r[ix["market"]] != "ercot_rtm" or r[ix["variable"]] != "spp_rtm" or r[ix["entity"]] != HUB:
            continue
        ts = r[ix["ts_utc"]]
        if (ts) in seen:
            continue
        seen.add(ts)
        last_ts = max(last_ts, ts)
        t = datetime.datetime(int(ts[0:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13]), int(ts[14:16]), tzinfo=UTC).astimezone(CHI)
        v = float(r[ix["value"]])
        by_year.setdefault(t.year, []).append((ts, t.month, t.hour, t.weekday(), v))
print(f"{HUB}: {sum(len(v) for v in by_year.values()):,} intervals from {min(by_year)} to {last_ts}; the local tables' last input {TABLE_CUT}")

# ---- line 1: what the page shows (median of the 16:00 to 21:00 block) beside the published kinds of figure
print("\n== line 1: the peak block's median (the page) beside a plain mean, a load-weighted mean and the traded 06:00 to 22:00 weekday block")
print("year | page: peak median | peak mean | all-interval median | all-interval mean | load-weighted mean (all) | 06-22 weekday median | 06-22 weekday mean")
for y in sorted(by_year):
    if y < 2016 or y > 2025:
        continue
    rows = [x for x in by_year[y] if x[0] <= TABLE_CUT]
    peak = sorted(v for _, _, h, _, v in rows if 16 <= h < 21)
    allv = sorted(v for *_, v in rows)
    onpk = sorted(v for _, _, h, wd, v in rows if 6 <= h < 22 and wd < 5)
    w = [(v, load.get(ts[:13])) for ts, *_, v in rows]
    w = [(v, l) for v, l in w if l]
    lw = sum(v * l for v, l in w) / sum(l for _, l in w) if w else float("nan")
    print(f"{y} | {fh.percentile(peak, 50):.2f} | {statistics.fmean(peak):.2f} | {fh.percentile(allv, 50):.2f} | {statistics.fmean(allv):.2f} | {lw:.2f} | "
          f"{fh.percentile(onpk, 50):.2f} | {statistics.fmean(onpk):.2f}")
print("published for 2024 (Potomac Economics, 2024 State of the Market Report for the ERCOT markets, May 2025): load-weighted average real-time price USD 31.91 per MWh (the faults file's row 11)")

# ---- line 2: the tables computed on a schedule, to the newest interval held
print(f"\n== line 2: the tables as held (to {TABLE_CUT}) against the tables computed to the newest interval held here ({last_ts})")


def blocks(rows):
    b = [array.array("d"), array.array("d"), array.array("d")]
    for _, _, h, _, v in rows:
        b[fh.block_of(h)].append(v)
    return b


for label, sel in (("year 2026", lambda x: True), ("September 2026", lambda x: x[1] == 9), ("October 2026", lambda x: x[1] == 10), ("November 2026", lambda x: x[1] == 11)):
    held = [x for x in by_year[2026] if sel(x) and x[0] <= TABLE_CUT]
    new = [x for x in by_year[2026] if sel(x)]
    a = fh.metrics(blocks(held)) if held else {}
    b = fh.metrics(blocks(new)) if new else {}
    keys = ("n_intervals", "peak_median", "midday_median", "peak_minus_midday_median", "all_p999", "n_scarcity", "n_negative")
    print(f"{label}: " + "; ".join(f"{k} {a.get(k, 'not held') if not isinstance(a.get(k), float) else round(a[k], 2)} -> {round(b[k], 2) if isinstance(b.get(k), float) else b.get(k, 'none')}" for k in keys))
print("the production tables were last computed on 21 October 2026 (the catalogue on 16 November); this machine's copy stops at 28 September, so the change on the site is the part after 21 October")
