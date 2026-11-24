"""B2, session 9900: the local hour of highest demand on Thanksgiving and on the three Thursdays before it, seven grids,
2019 to 2025, from eia930_ba_demand_hourly (ts_utc is the hour's start; the hour reported is the hour ending, local
prevailing time, as EIA's 'Local Time at End of Hour'). Writes peaks.csv (every day) and summary.csv."""
import csv
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SRC = sys.argv[1]
OUT = sys.argv[2]
TZ = {"CISO": "America/Los_Angeles", "ERCO": "America/Chicago", "MISO": "America/Chicago", "SWPP": "America/Chicago",
      "ISNE": "America/New_York", "NYIS": "America/New_York", "PJM": "America/New_York"}


def thanksgiving(y):
    d = date(y, 11, 1)
    first_thu = d + timedelta(days=(3 - d.weekday()) % 7)
    return first_thu + timedelta(days=21)


days = {}
for y in range(2019, 2026):
    t = thanksgiving(y)
    days[t] = (y, "thanksgiving")
    for k in (1, 2, 3):
        days[t - timedelta(days=7 * k)] = (y, f"thursday_minus_{k}")

# (ba, local date) -> list of (hour_ending, value, ts_utc)
hours = defaultdict(list)
with open(SRC, newline="") as f:
    for row in csv.reader(f):
        ba = row[0].split(":")[1]
        ts = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        end_local = (ts + timedelta(hours=1)).astimezone(ZoneInfo(TZ[ba]))
        # the hour ending at local midnight belongs to the day before, as hour ending 24
        he = end_local.hour if end_local.hour != 0 else 24
        d = end_local.date() if end_local.hour != 0 else end_local.date() - timedelta(days=1)
        if d in days and row[3] != "":
            hours[(ba, d)].append((he, float(row[3]), row[2], row[9]))

peaks = []
for (ba, d), hs in sorted(hours.items()):
    he, v, ts, basis = max(hs, key=lambda h: h[1])
    y, kind = days[d]
    peaks.append({"ba": ba, "year": y, "kind": kind, "date": d.isoformat(), "hours": len(hs), "peak_hour_ending": he,
                  "peak_mw": v, "peak_ts_utc": ts, "basis": basis})
with open(OUT + "/peaks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(peaks[0]))
    w.writeheader()
    w.writerows(peaks)

summ = []
for ba in TZ:
    tg = [p["peak_hour_ending"] for p in peaks if p["ba"] == ba and p["kind"] == "thanksgiving"]
    nt = [p["peak_hour_ending"] for p in peaks if p["ba"] == ba and p["kind"] != "thanksgiving"]
    short = [p["date"] for p in peaks if p["ba"] == ba and p["hours"] != 24]
    summ.append({"ba": ba, "n_thanksgiving": len(tg), "n_thursdays": len(nt), "thanksgiving_hours": " ".join(map(str, tg)),
                 "thursday_hours": " ".join(map(str, nt)), "median_thanksgiving": statistics.median(tg) if tg else "",
                 "median_thursday": statistics.median(nt) if nt else "",
                 "shift_hours": (statistics.median(nt) - statistics.median(tg)) if tg and nt else "",
                 "days_not_24_hours": " ".join(short)})
with open(OUT + "/summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0]))
    w.writeheader()
    w.writerows(summ)
for s in summ:
    print(s)
