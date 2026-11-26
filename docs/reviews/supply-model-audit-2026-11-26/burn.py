"""Session 10222 (supply audit): fuel burned for power, restated from EIA-930's workbook by the method note alone
(docs/methods/supply_and_trade.md, "Fuel burned for power"; the held hour of docs/methods/generation_mix_hourly.md).
No code of the warehouse or the site is imported. The workbook is streamed row by row; per hour only a compact record
(local day, net generation, the eight sources' sum, which sources are blank, gas, coal, oil) is kept.

    python burn.py <grid> <BA> <tz> <tolerance> <workbook.xlsx> <out.csv>

Rules, as the notes state them:
  hour      EIA's "UTC time" is the hour's end; the hour is dated by its start. Hours from 1 January 2019 local.
  sources   natural_gas NG; coal COL; nuclear NUC; wind WND+WNB; solar SUN+SNB; hydro WAT; storage BAT+PS+OES+UES;
            other OIL+GEO+OTH+UNK (EIA's Adjusted columns); a group is blank only when all its columns are. oil = OIL.
  held      net generation held and above zero; the eight groups' sum within the tolerance of it (5 percent, PJM 15);
            no main group blank (a main group: at least 5 percent of the grid's positive generation over its history).
  CISO      EIA's late hours from 2023-10-31T23:00Z to 2025-12-02T23:00Z moved one hour earlier (the row that lands on
            an hour already held is dropped); only hours before 2025-12-16T08:00Z (the join) are EIA's.
  day       a local day counts when every hour of it is held and it has its 23, 24 or 25 hours.
  fuel      a day counts for a fuel when every hour names it; MWh is the sum of its hours, an hour below zero as zero;
            skipped for a grid when the fuel is never above zero in a counted day.
  units     day MWh x heat rate (gas 7.6, coal 10.6, oil 11.0 MMBtu/MWh) / heat content (1.037e6 MMBtu per Bcf, 19.0e3
            per thousand short tons, 5.8e3 per thousand barrels).
  week      ends Friday; the mean of its seven days, only when all seven count.
"""
import csv
import datetime as dt
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

import openpyxl

grid, ba, tzname, tol, path, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5], sys.argv[6]
tz = ZoneInfo(tzname)
UTC = dt.timezone.utc
GROUPS = {"natural_gas": ["NG"], "coal": ["COL"], "nuclear": ["NUC"], "wind": ["WND", "WNB"], "solar": ["SUN", "SNB"], "hydro": ["WAT"],
          "storage": ["BAT", "PS", "OES", "UES"], "other": ["OIL", "GEO", "OTH", "UNK"]}
NAMES = list(GROUPS)
HR = {"natural_gas": 7.6, "coal": 10.6, "oil": 11.0}
HC = {"natural_gas": 1.037e6, "coal": 19.0e3, "oil": 5.8e3}
LATE_FROM = dt.datetime(2023, 10, 31, 23, tzinfo=UTC)
LATE_TO = dt.datetime(2025, 12, 2, 23, tzinfo=UTC)
JOIN = dt.datetime(2025, 12, 16, 8, tzinfo=UTC)
first_local = dt.datetime(2019, 1, 1, tzinfo=tz).astimezone(UTC)

ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
rows = ws.iter_rows(values_only=True)
head = list(next(rows))
it = head.index("UTC time")
ing = head.index("Adjusted net generation")
cols = {c: head.index(f"Adjusted {c} Gen") for codes in GROUPS.values() for c in codes if f"Adjusted {c} Gen" in head}
CK, CI = list(cols), list(cols.values())


def num(v):
    return float(v) if isinstance(v, (int, float)) else None


hours = {}          # start (aware UTC) -> record
order = []
for r in rows:
    t = r[it]
    if t is None or t.year < 2018:
        continue
    start = t.replace(tzinfo=UTC) - dt.timedelta(hours=1)
    rec = (num(r[ing]), tuple(num(r[i]) for i in CI))
    if ba == "CISO":
        if start >= JOIN:
            continue
    if start in hours:
        continue        # the first row of an hour is kept
    hours[start] = rec
    order.append(start)

if ba == "CISO":
    kept = {s: v for s, v in hours.items() if not (LATE_FROM <= s < LATE_TO)}
    for s, v in hours.items():
        if LATE_FROM <= s < LATE_TO:
            m = s - dt.timedelta(hours=1)
            if m not in kept:
                kept[m] = v
    hours = kept

pos = defaultdict(float)
recs = []
for s in sorted(hours):
    if s < first_local:
        continue
    ng, tv = hours[s]
    vals = dict(zip(CK, tv))
    g = {}
    for name, codes in GROUPS.items():
        have = [vals[c] for c in codes if c in vals and vals[c] is not None]
        g[name] = sum(have) if have else None
    oil = vals.get("OIL")
    for name in NAMES:
        if g[name] is not None and g[name] > 0:
            pos[name] += g[name]
    present = [g[n] for n in NAMES if g[n] is not None]
    total = sum(present) if present else None
    day = s.astimezone(tz).date()
    recs.append((day, ng, total, frozenset(n for n in NAMES if g[n] is None), g["natural_gas"], g["coal"], oil))

whole = sum(pos.values())
main = [n for n in NAMES if pos[n] / whole >= 0.05]
byday = defaultdict(list)
for rec in recs:
    day, ng, total, blank, gas, coal, oil = rec
    held = ng is not None and ng > 0 and total is not None and abs(total - ng) <= tol * ng and not (blank & set(main))
    byday[day].append((held, gas, coal, oil))


def expected(day):
    a = dt.datetime(day.year, day.month, day.day, tzinfo=tz)
    nd = day + dt.timedelta(days=1)
    b = dt.datetime(nd.year, nd.month, nd.day, tzinfo=tz)
    return round((b.astimezone(UTC) - a.astimezone(UTC)).total_seconds() / 3600)


complete = {d: v for d, v in byday.items() if len(v) == expected(d) and all(h for h, *_ in v)}
fidx = {"natural_gas": 1, "coal": 2, "oil": 3}
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["grid", "fuel", "week_end", "value", "days"])
    for fuel, k in fidx.items():
        if not any((x[k] or 0) > 0 for v in complete.values() for x in v):
            continue
        daily = {}
        for d, v in complete.items():
            if all(x[k] is not None for x in v):
                mwh = sum(max(x[k], 0.0) for x in v)
                daily[d] = mwh * HR[fuel] / HC[fuel]
        wk = defaultdict(list)
        for d, val in daily.items():
            wk[d + dt.timedelta(days=(4 - d.weekday()) % 7)].append(val)
        for end in sorted(wk):
            if len(wk[end]) == 7:
                w.writerow([grid, fuel, end.isoformat(), repr(sum(wk[end]) / 7), 7])
print(f"{grid}: {len(recs)} hours from 2019, main {main}, {len(complete)} complete days of {len(byday)}, newest hour {max(hours).isoformat()}")
