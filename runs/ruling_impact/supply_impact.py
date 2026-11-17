#!/usr/bin/env python3
"""ERW, ruling impact for /supply (session 7589, 17 November 2026).

The four lines marked "Changes a figure" under /supply in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The page's own file is site/data/supply.json (built 2026-11-17T04:51:44Z), read by the rules of
site/lib/supply.ts (the surprises list). A grid's net imports from eia930_daily_total_interchange (EIA-930, public,
warehouse/output): positive total interchange is an export, so net imports are its negative.

    .venv/Scripts/python.exe runs/ruling_impact/supply_impact.py
"""
import csv
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8"))
R = {r["id"]: r for r in S["rows"]}
print(f"supply.json built {S['built']}: {len(S['rows'])} rows")

# ---- line 1: A and B, PJM against MISO
print("\n== line 1: two grids side by side, their burn rows over the weeks both hold (PJM against MISO)")
for fuel, unit in (("natural-gas", "Bcf a day"), ("coal", "thousand short tons a week")):
    a, b = R.get(f"burn-pjm-{fuel}"), R.get(f"burn-miso-{fuel}")
    if not (a and b and a.get("spark") and b.get("spark")):
        print(f"{fuel}: no spark on one side")
        continue
    sa = dict(zip(a["spark"]["t"], a["spark"]["v"]))
    sb = dict(zip(b["spark"]["t"], b["spark"]["v"]))
    weeks = sorted(set(sa) & set(sb))
    print(f"{fuel} ({a.get('unit')}): PJM's newest week {a['last']['t']} ({a['last']['v']:.4f}), MISO's {b['last']['t']} ({b['last']['v']:.4f}): the table compares two different weeks; "
          f"over the {len(weeks)} weeks both hold, the newest common week {weeks[-1]}: PJM {sa[weeks[-1]]:.4f}, MISO {sb[weeks[-1]]:.4f} (PJM less MISO {sa[weeks[-1]] - sb[weeks[-1]]:+.4f}); "
          f"mean over the common weeks PJM {sum(sa[w] for w in weeks) / len(weeks):.4f}, MISO {sum(sb[w] for w in weeks) / len(weeks):.4f}")

# ---- line 2: a grid's net imports, the newest month
print("\n== line 2: a row of each grid's net imports for the newest whole month (EIA-930 total interchange)")
BA = {"ERCO": "ERCOT", "CISO": "CAISO", "PJM": "PJM", "MISO": "MISO", "SWPP": "SPP", "NYIS": "NYISO", "ISNE": "ISO-NE"}
acc = defaultdict(lambda: defaultdict(float))
days = defaultdict(lambda: defaultdict(int))
with open(os.path.join(ROOT, "warehouse", "output", "eia930_daily_total_interchange.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        code = r["entity"].split(":")[1]
        if code in BA and r["value"]:
            m = r["ts_utc"][:7]
            acc[code][m] += float(r["value"])
            days[code][m] += 1
for code, name in BA.items():
    months = sorted(m for m in acc[code] if days[code][m] >= 28)
    m = months[-1]
    print(f"{name}: {m} ({days[code][m]} days) net imports {-acc[code][m] / 1e3:,.0f} GWh ({-acc[code][m] / days[code][m] / 24:,.0f} MW on average)")

# ---- line 3: the surprises list with a floor
print("\n== line 3: 'Changes outside the five years' range': every series (default) or only series whose latest value is above a floor")


def far(r):
    c = r["change"]
    span = (c.get("hi") or 0) - (c.get("lo") or 0)
    return abs(c.get("surprise") or 0) / span if span > 0 else 0


lst = sorted([r for r in S["rows"] if r["status"] == "ok" and (r.get("change") or {}).get("outside") and r["change"].get("surprise") is not None], key=lambda r: -far(r))
print(f"default: {len(lst)} lines: " + "; ".join(f"{r['label']}, {r['at']} (latest {r['last']['v']} {r['unit']}, {far(r):.2f} ranges)" for r in lst))
for frac in (0.01, 0.05):
    keep = []
    for r in lst:
        avg = (r.get("avg5") or {}).get("v")
        if avg is None or abs(r["last"]["v"]) >= frac * abs(avg):
            keep.append(r)
    print(f"a floor of {frac * 100:.0f} percent of the series' own five-year average (an example of a stated floor): {len(keep)} lines; first {keep[0]['label']}, {keep[0]['at']}" if keep else f"floor {frac}: none")
small = [r for r in lst if abs(r["last"]["v"]) < 0.05 and r["unit"].lower().startswith("bcf")]
print(f"lines whose latest value is under 0.05 Bcf a day: {len(small)} ({', '.join(r['label'] + ', ' + r['at'] for r in small)})")

# ---- line 4: the ask panel's licence hold
print("\n== line 4: the grid pages' ask panel and NYISO's and ISO-NE's cleared rows")
for k in ("cleared-nyiso", "cleared-iso-ne", "cleared-pjm"):
    r = R[k]
    print(f"{k}: status {r['status']}, {'a value in the file' if r.get('last') else 'no value in the file'}")
print("on this build the file carries no value for the held grids' cleared rows (the builder's fix, request 154): a hold in the panel moves no figure today")
