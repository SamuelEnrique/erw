"""Session 10222: measures for the supply audit from the restated burn weeks (burn_<grid>.csv), CAISO's own weeks
(caiso_gas_own.csv) and the page file.

    python measures.py <run dir> <supply.json>
"""
import csv
import datetime as dt
import json
import sys
from collections import defaultdict

d = sys.argv[1]
F = {r["id"]: r for r in json.load(open(sys.argv[2], encoding="utf-8"))["rows"]}


def load(grid):
    s = defaultdict(dict)
    for r in csv.DictReader(open(f"{d}/burn_{grid}.csv", encoding="utf-8")):
        s[r["fuel"]][dt.date.fromisoformat(r["week_end"])] = float(r["value"])
    return s


own = {dt.date.fromisoformat(r["week_end"]): float(r["value"]) for r in csv.DictReader(open(f"{d}/caiso_gas_own.csv", encoding="utf-8"))}
g = {k: load(k) for k in ("caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp")}

print("== 1. California's gas, EIA's (before the join) against CAISO's own, the same weeks")
eia = g["caiso"]["natural_gas"]
both = sorted(w for w in eia if w in own)
by_year = defaultdict(list)
for w in both:
    by_year[w.year].append((eia[w], own[w]))
for y, v in sorted(by_year.items()):
    a = sum(x for x, _ in v) / len(v)
    b = sum(x for _, x in v) / len(v)
    print(f"  {y}: {len(v)} weeks, EIA {a:.4f} Bcf/d, CAISO's own {b:.4f}, EIA over own {100 * (a / b - 1):+.1f} percent")
for w in [dt.date(2025, 11, 14), dt.date(2024, 11, 15), dt.date(2023, 11, 17), dt.date(2022, 11, 18), dt.date(2021, 11, 19), dt.date(2025, 10, 31)]:
    print(f"  week ending {w}: EIA {eia.get(w)}, own {own.get(w)}")
tot = F["burn-all-natural-gas"]
yv = tot["year"]["v"]
yt = tot["year"]["t"]
w = dt.date.fromisoformat(yt)
alt = yv - eia[w] + own[w]
v0 = tot["last"]["v"]
print(f"  the seven grids together, week ending {tot['last']['t']}: {v0}; on the year (base {yt}) page {v0 - yv:+.4f} ({100 * (v0 - yv) / yv:+.2f} percent); with CAISO's own in the base {v0 - alt:+.4f} ({100 * (v0 - alt) / alt:+.2f} percent)")

print("== 2. Oil burned for power: yearly means of the restated weeks, and the share of weeks at zero")
for grid in ("nyiso", "spp", "pjm"):
    s = g[grid].get("oil", {})
    yrs = defaultdict(list)
    for w, v in s.items():
        yrs[w.year].append(v)
    print(" ", grid, " ".join(f"{y}: {sum(v) / len(v):.3f} ({sum(1 for x in v if x == 0)}/{len(v)} zero)" for y, v in sorted(yrs.items())))
    nz = sorted(w for w, v in s.items() if v > 0)
    if nz:
        print(f"    last week above zero: {nz[-1]}; first: {nz[0]}")
for rid in ("burn-nyiso-oil", "burn-spp-oil"):
    r = F[rid]
    print(f"  {rid}: latest {r['last']}, year {r['year']}, five-year {r['avg5']}")

print("== 3. ERCOT: gas burn, the year before and the five years, and coal")
for fuel in ("natural_gas", "coal"):
    s = g["ercot"][fuel]
    for w in [dt.date(2025, 11, 14), dt.date(2024, 11, 15), dt.date(2023, 11, 17), dt.date(2022, 11, 18), dt.date(2021, 11, 19)]:
        print(f"  {fuel} week ending {w}: {s.get(w)}")

print("== 4. The weeks of the join: a week built on both sources")
for wk in (dt.date(2025, 12, 19),):
    print(f"  week ending {wk}: file spark {dict(zip(F['burn-caiso-natural-gas']['spark']['t'], F['burn-caiso-natural-gas']['spark']['v'])).get(wk.isoformat())}, CAISO's own alone {own.get(wk)}")

print("== 5. Heat rate: the gas burn at another stated rate (the page's 7.6 MMBtu/MWh)")
for hr in (7.0, 7.2, 7.8, 8.0):
    r = F["burn-all-natural-gas"]
    print(f"  {hr}: the seven grids together {r['last']['v'] * hr / 7.6:.2f} Bcf/d (page {r['last']['v']:.2f}); the change on the year {(r['year']['ch']) * hr / 7.6:+.2f}; percents unchanged")
