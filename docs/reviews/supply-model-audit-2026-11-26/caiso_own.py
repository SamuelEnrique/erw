"""Session 10222: California's gas burned for power on CAISO's own supply by fuel throughout (the like-for-like
alternative to the page's California row, which is EIA's before 16 December 2025 and CAISO's own from it).

    python caiso_own.py <history.csv> <recent.csv> <out.csv>

An hour is held when CAISO's file gives all thirteen of its columns (the twelve sources and imports) and the sum of the
sources is above zero; a local (Pacific) day counts when all its hours are held; gas MWh is the sum of its hours, an
hour below zero as zero; x 7.6 / 1.037e6, Bcf a day; a week ends Friday and is the mean of seven counted days.
Streamed; one hour's thirteen values at a time are kept until the hour is whole.
"""
import csv
import datetime as dt
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

tz = ZoneInfo("America/Los_Angeles")
UTC = dt.timezone.utc
ALL = {"batteries_mw", "biogas_mw", "biomass_mw", "coal_mw", "geothermal_mw", "large_hydro_mw", "natural_gas_mw", "nuclear_mw",
       "other_mw", "small_hydro_mw", "solar_mw", "wind_mw", "imports_mw"}
OWN = ALL - {"imports_mw"}
hours = defaultdict(dict)
for path in sys.argv[1:3]:
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["variable"] in ALL and r["value"] != "":
                hours[r["ts_utc"]][r["variable"]] = float(r["value"])
days = defaultdict(list)
for ts, v in hours.items():
    t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    held = set(v) >= ALL and sum(v[k] for k in OWN) > 0
    days[t.astimezone(tz).date()].append((held, v.get("natural_gas_mw")))
hours.clear()


def expected(d):
    a = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
    n = d + dt.timedelta(days=1)
    b = dt.datetime(n.year, n.month, n.day, tzinfo=tz)
    return round((b.astimezone(UTC) - a.astimezone(UTC)).total_seconds() / 3600)


daily = {d: sum(max(g, 0.0) for _, g in v) * 7.6 / 1.037e6 for d, v in days.items() if len(v) == expected(d) and all(h for h, _ in v)}
wk = defaultdict(list)
for d, v in daily.items():
    wk[d + dt.timedelta(days=(4 - d.weekday()) % 7)].append(v)
with open(sys.argv[3], "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["week_end", "value"])
    for e in sorted(wk):
        if len(wk[e]) == 7:
            w.writerow([e.isoformat(), repr(sum(wk[e]) / 7)])
print(f"{len(daily)} counted days of {len(days)}; {sum(1 for e in wk if len(wk[e]) == 7)} whole weeks")
