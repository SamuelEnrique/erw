"""Session 10221: the scale an expert sets a fleet's figure against: United States retail sales of electricity, all
sectors and commercial, in 2020, 2024 and the twelve months July 2024 to June 2025 (Microsoft's fiscal year 2025), from
the main copy's eia_retail_sales_monthly.csv (read only, streamed line by line). The audit's own arithmetic, never the
page's.

    python us_sales.py <eia_retail_sales_monthly.csv> <out json>
"""
import csv
import json
import sys

path, out = sys.argv[1], sys.argv[2]
want = {}
head = None
sample = []
with open(path, encoding="utf-8", newline="") as f:
    for line in f:
        if line.startswith("#"):
            continue
        if head is None:
            head = next(csv.reader([line]))
            continue
        if ":US:" not in line and "US:" not in line:
            continue
        r = dict(zip(head, next(csv.reader([line]))))
        key = f"{r.get('entity')}|{r.get('variable')}"
        if len(sample) < 12 and key not in [s[0] for s in sample]:
            sample.append((key, r.get("unit", "")))
        ts = r["ts_utc"][:7]
        want.setdefault(key, {})[ts] = float(r["value"]) if r["value"] not in ("", None) else None

res = {"columns": head, "keys_seen": sample}
for key, series in want.items():
    if "sales" not in key.lower():
        continue
    y = lambda yr: sum(v for t, v in series.items() if t.startswith(yr) and v is not None)
    n = lambda yr: sum(1 for t, v in series.items() if t.startswith(yr) and v is not None)
    fy = [f"2024-{m:02d}" for m in range(7, 13)] + [f"2025-{m:02d}" for m in range(1, 7)]
    res[key] = {"2020": y("2020"), "2020 months": n("2020"), "2024": y("2024"), "2024 months": n("2024"),
                "Jul 2024 to Jun 2025": sum(series.get(t) or 0 for t in fy), "fy months": sum(1 for t in fy if series.get(t) is not None)}
json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
print(json.dumps(res, indent=1))
