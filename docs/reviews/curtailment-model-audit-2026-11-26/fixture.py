"""Session 10210 (curtailment audit): the rows the page's two live reads would get, from the main copy's tables (read only).

    python fixture.py <main copy warehouse/output> <out fixture.json>

The page reads iso_curtailment_monthly (one entity, every row) and the grid's daily table since 100 days before "now".
Here "now" is 2026-11-26 (the draw script sets Date.now to it). Rows are written as the live set returns them.
"""
import csv
import json
import os
import sys

src, out = sys.argv[1], sys.argv[2]
want = {
    "caiso_curtailment_daily": ("caiso:ISO", "2026-08-18"),
    "spp_curtailment_daily": ("spp:SPP", "2026-08-18"),
    "ercot_wind_solar_hsl_daily": ("ercot:system", "2026-08-18"),
    "iso_curtailment_monthly": (None, ""),
}
fx = {}
for t, (ent, since) in want.items():
    rows = []
    with open(os.path.join(src, f"{t}.csv"), encoding="utf-8", newline="") as f:
        r = csv.DictReader(line for line in f if not line.startswith("#"))
        for x in r:
            if ent and x["entity"] != ent:
                continue
            if x["ts_utc"] < since:
                continue
            rows.append({"entity": x["entity"], "variable": x["variable"], "ts_utc": x["ts_utc"], "value": float(x["value"]), "unit": x["unit"], "freq": x["freq"]})
    rows.sort(key=lambda r: (r["entity"], r["variable"], r["ts_utc"]))
    fx[t] = rows
    print(t, len(rows), rows[0]["ts_utc"] if rows else "-", rows[-1]["ts_utc"] if rows else "-")
with open(out, "w", encoding="utf-8") as f:
    json.dump(fx, f)
