"""Session 10235: for each issue's operating day, each grid's highest real-time interval in the main checkout's tables,
with the time the row was retrieved, so a figure the issue could not have seen (retrieved after the issue was written)
is told apart from one it missed. Also the US48 demand peak's row retrieval time for 12 November.

Run: python r1b_rt_when.py <output dir> > r1b_rt_when.out
"""
import csv
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

OUT = sys.argv[1]
WRITTEN = {"2026-10-09": "2026-10-09T15:34", "2026-10-12": "2026-10-12T15:35", "2026-10-13": "2026-10-13T15:36",
           "2026-10-14": "2026-10-14T16:18", "2026-10-20": "2026-10-20T06:55", "2026-10-21": "2026-10-21T15:45",
           "2026-10-22": "2026-10-22T15:39", "2026-10-23": "2026-10-23T15:45", "2026-11-06": "2026-11-06T00:48",
           "2026-11-12": "2026-11-12T22:56"}
TZ = {"ercot": ZoneInfo("America/Chicago"), "spp": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles"),
      "nyiso": ZoneInfo("America/New_York"), "isone": ZoneInfo("America/New_York"), "miso": timezone(timedelta(hours=-5))}
FILES = ["iso_rtm_hub_prices", "nyiso_rtm_zone_prices", "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly"]


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


data = []
span = {}
for name in FILES:
    for r in rows(name):
        g = r["entity"].split(":")[0]
        t = datetime.strptime(r["ts_utc"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        data.append((g, r["node"], r["variable"], t, float(r["value"]), r["retrieved_at"], name))
        lo, hi = span.get(name, (t, t))
        span[name] = (min(lo, t), max(hi, t))
for name, (lo, hi) in span.items():
    print(f"{name}: rows from {lo:%Y-%m-%d %H:%M} to {hi:%Y-%m-%d %H:%M} UTC")
for issue, written in WRITTEN.items():
    day = date.fromisoformat(issue) - timedelta(days=1)
    print(f"\n{issue} (written {written} UTC), operating day {day}:")
    for g, tz in TZ.items():
        st = datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(timezone.utc)
        en = st + timedelta(days=1)
        xs = [x for x in data if x[0] == g and st <= x[3] < en]
        if not xs:
            print(f"  {g}: no rows")
            continue
        top = max(xs, key=lambda x: x[4])
        before = [x for x in xs if x[5][:16] <= written]
        topb = max(before, key=lambda x: x[4]) if before else None
        print(f"  {g}: {len(xs)} rows; highest {top[4]:.2f} at {top[1]} {top[3]:%Y-%m-%d %H:%M}Z ({top[2]}, {top[6]}), retrieved {top[5]}"
              + (f"; highest among rows retrieved before the issue: {topb[4]:.2f} at {topb[1]} ({len(before)} rows)" if topb else "; no row retrieved before the issue"))

# the demand row of 12 November
with open(os.path.join(OUT, "eia930_all_demand.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
        if r["entity"] == "eia930:US48" and r["variable"] == "demand_mw" and r["ts_utc"].startswith("2026-11-11T23"):
            print(f"\nUS48 demand 2026-11-11 23:00 UTC: {r['value']} MW, retrieved {r['retrieved_at']}")
