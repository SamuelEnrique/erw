#!/usr/bin/env python3
"""ERW, ruling impact for /prices/compare (session 7588, 17 November 2026).

The three lines marked "Changes a figure" under "where power is cheap" in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). The rules are replication/compare/replicate.py (imported: read, hours_of, measures, carbon:
the method note docs/methods/hub_price_comparison.md in code), on the warehouse's tables (warehouse/output). Public hubs
only for prices; grid carbon intensity is EIA-930's (carbon_intensity_daily), public.

    .venv/Scripts/python.exe runs/ruling_impact/compare_impact.py
"""
import datetime as dt
import importlib.util
import os
import zoneinfo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "compare", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
OUT = os.path.join(ROOT, "warehouse", "output")
HUBS = ["ercot:HB_HUBAVG", "ercot:HB_WEST", "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND", "spp:SPPNORTH_HUB"]
D = dt.date

data = rep.read(OUT, set(HUBS), "2024-12-31T00:00:00", "2026-11-02T00:00:00")


def m(entity, side, start, end, tz=None):
    grid = entity.split(":")[0]
    tz = tz or zoneinfo.ZoneInfo(rep.TZ[grid])
    return rep.measures(rep.hours_of(data[(entity, side)], side), tz, start, end)


def fmt(x):
    return f"{x['avg_price']:.2f}" if "avg_price" in x else f"not written ({x['hours_held']} of {x['hours_in_window']} hours)"


print("== line 1: two windows (the twelve months to October 2026, and October 2026) or any months: calendar 2025 and summer 2026 as examples")
for e in HUBS:
    for side in ("dam", "rtm"):
        y = m(e, side, D(2025, 11, 1), D(2026, 11, 1))
        c = m(e, side, D(2025, 1, 1), D(2026, 1, 1))
        s = m(e, side, D(2026, 6, 1), D(2026, 9, 1))
        print(f"{e} {side}: twelve months {fmt(y)}; calendar 2025 {fmt(c)}; summer 2026 (June to August) {fmt(s)}")

print("\n== line 2: one time convention for a month: clock time here (default) against standard time (the cost of power page), September 2026")
STD = {"ercot": dt.timezone(dt.timedelta(hours=-6)), "spp": dt.timezone(dt.timedelta(hours=-6)), "caiso": dt.timezone(dt.timedelta(hours=-8))}
for e in HUBS:
    for side in ("dam", "rtm"):
        a = m(e, side, D(2026, 9, 1), D(2026, 10, 1))
        b = m(e, side, D(2026, 9, 1), D(2026, 10, 1), STD[e.split(":")[0]])
        if "avg_price" in a and "avg_price" in b:
            print(f"{e} {side}: clock {a['avg_price']:.4f} -> standard {b['avg_price']:.4f} ({b['avg_price'] - a['avg_price']:+.4f}); day spread {a['day_spread_top4_bottom4']:.2f} -> {b['day_spread_top4_bottom4']:.2f}")
        else:
            print(f"{e} {side}: clock {fmt(a)}; standard {fmt(b)}")

print("\n== line 3: ISO-NE's and NYISO's grid carbon intensity (EIA-930, public) shown while their prices stay held")
for grid in ("isone", "nyiso"):
    for label, s, e in (("twelve months", D(2025, 11, 1), D(2026, 11, 1)), ("October 2026", D(2026, 10, 1), D(2026, 11, 1))):
        c = rep.carbon(OUT, grid, s, e)
        print(f"{grid} {label}: {c.get('intensity', 'not written'):.1f} (kg CO2 per MWh generated, {c['days_held']} of {c['days_due']} days)" if "intensity" in c
              else f"{grid} {label}: not written ({c['days_held']} of {c['days_due']} days)")
for grid in ("ercot", "caiso", "spp"):
    c = rep.carbon(OUT, grid, D(2025, 11, 1), D(2026, 11, 1))
    print(f"   for scale, {grid} twelve months: {c.get('intensity', float('nan')):.1f}")
