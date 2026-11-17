#!/usr/bin/env python3
"""ERW, ruling impact for /demand (session 7591, 17 November 2026).

The three lines marked "Changes a figure" under /demand in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads).

  line 3 (the weather view's fit years): warehouse/derived/demand_weather.py is imported (nothing written: analyse() only)
         and run with its own fit years, 2019 to 2021, and with 2019 to 2024, on the same EIA-930 workbooks and NOAA
         weather, for the four grids the site shows without a hold (ERCOT, CAISO, PJM, SPP);
  line 2 (a zone's own load growth): ERCOT's eight load zones from ercot_zone_load_hourly (ERCOT, public);
  line 1 (California's base months): CAISO's own load before September 2021 is not on this machine; the data
         machine's figures are quoted.

    .venv/Scripts/python.exe runs/ruling_impact/demand_impact.py
"""
import csv
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
os.chdir(ROOT)

print("== line 1: California's base months (26 February to 31 March 2019): EIA's file, or CAISO's own load")
print("CAISO's own hourly load on this machine (caiso_area_load_hourly) starts on 17 September 2021: not computed here. "
      "The data machine's figures (note_2026-11-17_data_c301.md, request 38): California's change to 2025 is 1,089.3 MW on EIA's file, 847.5 MW with CAISO's own load in the base months "
      "(-241.8 MW, -22.2 percent)")

print("\n== line 2: a zone's own load growth (ERCOT's load zones; Dominion's and the other held grids' zones are not read)")
acc = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
with open(os.path.join(ROOT, "warehouse", "output", "ercot_zone_load_hourly.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        y = r["ts_utc"][:4]
        if y in ("2019", "2025") and r["value"]:
            a = acc[r["entity"]][y]
            a[0] += float(r["value"])
            a[1] += 1
for e in sorted(acc):
    a, b = acc[e]["2019"], acc[e]["2025"]
    if a[1] and b[1]:
        m19, m25 = a[0] / a[1], b[0] / b[1]
        print(f"{e}: mean load 2019 {m19:,.0f} MW ({a[1]} hours), 2025 {m25:,.0f} MW ({b[1]} hours): {m25 - m19:+,.0f} MW, {(m25 / m19 - 1) * 100:+.1f} percent")

print("\n== line 3: the weather view's fit on 2019 to 2021 (default) or on 2019 to 2024")
import demand_weather as dw  # noqa: E402

weather = dw.read_weather(os.path.join(ROOT, "warehouse", "output", "noaa_grid_weather_hourly.csv"))
TZ = {"ERCO": "America/Chicago", "CISO": "America/Los_Angeles", "PJM": "America/New_York", "SWPP": "America/Chicago"}
for ba in ("ERCO", "CISO", "PJM", "SWPP"):
    try:
        demand, path = dw.read_demand(ba)
    except Exception as exc:  # a missing workbook is said, never filled
        print(f"{ba}: the workbook cannot be read ({exc})")
        continue
    out = {}
    for label, train in (("2019 to 2021", (2019, 2020, 2021)), ("2019 to 2024", (2019, 2020, 2021, 2022, 2023, 2024))):
        dw.TRAIN = train
        res = dw.analyse(demand, weather.get(ba), TZ[ba], ba)
        out[label] = res
        for y in (2025, 2026):
            g = (res["years"].get(y) or {}).get("summer_peak")
            if g:
                print(f"{ba} {label}: summer peak {y}: growth {g['growth_pct']:+.2f} percent, weather {g['weather_pct']:+.2f}, unexplained {g['unexplained_pct']:+.2f} "
                      f"(uncertainty {g['uncertainty_pct']:.2f} on {g['holdouts']} left-out years); outside the fit's weather {g.get('outside')}; a finding: {g['finding']}")
            e = (res["years"].get(y) or {}).get("energy")
            if e:
                print(f"{ba} {label}: energy {y}: unexplained {e['unexplained_pct']:+.2f} (uncertainty {e['uncertainty_pct']:.2f}); a finding: {e['finding']}")
        print(f"{ba} {label}: the fit's left-out hourly error {res['fit']['oos_mape_pct']:.2f} percent; hottest cooling degrees seen {res['fit']['cd_max']:.1f}")
    del demand
