"""B3, session 9900: the Monday of Thanksgiving week, US regular gasoline and No. 2 diesel retail, every year in
eia_retail_fuel_prices; 2026 uses 16 November (23 November not yet published). Prints the facts for the caption."""
import csv
import sys
from datetime import date, timedelta

SRC = sys.argv[1]
OUT = sys.argv[2]
ser = {"EMM_EPMR_PTE_NUS_DPG": "gasoline_regular", "EMD_EPD2D_PTE_NUS_DPG": "diesel"}
vals = {k: {} for k in ser.values()}
with open(SRC, newline="") as f:
    rows = (l for l in f if not l.startswith("#"))
    for r in csv.DictReader(rows):
        s = r["entity"].split(":")[1]
        if s in ser:
            vals[ser[s]][r["ts_utc"][:10]] = float(r["value"])


def monday(y):
    d = date(y, 11, 1)
    thu = d + timedelta(days=(3 - d.weekday()) % 7 + 21)
    return thu - timedelta(days=3)


out = []
for y in range(1990, 2027):
    m = monday(y).isoformat()
    if y == 2026:
        m = "2026-11-16"
    g, dz = vals["gasoline_regular"].get(m), vals["diesel"].get(m)
    if g is None and dz is None:
        continue
    out.append({"year": y, "week_of": m, "gasoline_regular": g, "diesel": dz})
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
for o in out:
    print(o)
for k in vals:
    mx = max(vals[k].items(), key=lambda kv: kv[1])
    tg = [o for o in out if o[k] is not None]
    best = max(tg, key=lambda o: o[k])
    print(f"{k}: series high {mx[1]} on {mx[0]} ({min(vals[k])} to {max(vals[k])}); highest Thanksgiving week {best[k]} in {best['year']}")
    top = sorted(vals[k].items(), key=lambda kv: -kv[1])[:5]
    print("  five highest weeks:", top)
