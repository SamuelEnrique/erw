"""Session 10219: days whose peak demand in the /conditions page files stands far above the grid's days around it
(a report fault EIA-930 is known for), and whether one is the "Highest peak demand" a window prints.

argv: worktree. A day is flagged when its peak exceeds 1.3 times the median peak of the 31 days centred on it, or its
lowest hour is under 0.3 times the median lowest. For each flagged day: whether a window the page offers (the nine
events, the newest days, a chosen day's 31 days) would print it as its highest peak.
"""
import json
import os
import sys
from statistics import median

ROOT = sys.argv[1]
OPS = ["caiso", "ercot", "spp", "miso", "pjm", "nyiso", "isone"]
out = {}
for op in OPS:
    with open(os.path.join(ROOT, "site", "data", "conditions", op + ".json"), encoding="utf-8") as fh:
        f = json.load(fh)
    dc = f["daily_columns"]
    ip, imn, ifc = dc.index("demand_peak"), dc.index("demand_min"), dc.index("forecast_peak")
    days = [r for r in f["daily"] if r[ip] is not None]
    flagged = []
    for i, r in enumerate(days):
        near = [x[ip] for x in days[max(0, i - 15): i + 16] if x is not r]
        nearmin = [x[imn] for x in days[max(0, i - 15): i + 16] if x is not r and x[imn] is not None]
        m, mm = median(near), median(nearmin) if nearmin else None
        hi = r[ip] > 1.3 * m
        lo = mm is not None and r[imn] is not None and r[imn] < 0.3 * mm
        if hi or lo:
            # the windows that would print this day as their highest peak: any chosen day within 15 days whose window max is it
            n_days_max = 0
            for j in range(max(0, i - 15), min(len(days), i + 16)):
                win = days[max(0, j - 15): j + 16]
                if max(x[ip] for x in win) == r[ip]:
                    n_days_max += 1
            ev = [w["id"] for w in f["windows"] if w["start"] <= r[0] <= w["end"] and max(x[ip] for x in days if w["start"] <= x[0] <= w["end"]) == r[ip]]
            flagged.append({"day": r[0], "peak": r[ip], "median_peak_31": m, "ratio": round(r[ip] / m, 2), "min": r[imn],
                            "median_min_31": mm, "forecast_peak": r[ifc], "high": hi, "low": lo,
                            "chosen_days_printing_it_as_highest": n_days_max, "windows_printing_it": ev})
    out[op] = flagged
    print(op, len(days), "days;", len(flagged), "flagged")
    for x in flagged:
        print("  ", x)
with open(os.path.join(ROOT, "runs", "c10219", "spikes.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
