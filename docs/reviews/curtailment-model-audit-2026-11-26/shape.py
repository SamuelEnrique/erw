"""Session 10210: the hour-of-day shape of California's curtailment, same month in 2025 (five-minute record) and 2026
(daily report by the hour), from the page's own profile file. Prints each hour's share of the month's MWh and the
centroid hour (MWh-weighted mean of hour + 0.5)."""
import json, os, sys
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "site", "data")
p = json.load(open(os.path.join(ROOT, "curtailment_profile.json")))
for mo in ["03", "04", "05", "06", "09", "10"]:
    for y in ["2024", "2025", "2026"]:
        r = p["months"].get(f"{y}-{mo}")
        if not r:
            continue
        v = [r.get(f"curtailed_solar_mwh_h{h:02d}", 0) + r.get(f"curtailed_wind_mwh_h{h:02d}", 0) for h in range(24)]
        s = sum(v)
        cen = sum((h + 0.5) * x for h, x in enumerate(v)) / s
        first = next(h for h in range(24) if v[h] > 0.01 * max(v))
        last = max(h for h in range(24) if v[h] > 0.01 * max(v))
        print(f"{y}-{mo} centroid {cen:5.2f} peak {v.index(max(v)):2d} first>1%max {first:2d} last {last:2d} | " + " ".join(f"{100*x/s:4.1f}" for x in v[5:20]))
