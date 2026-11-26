"""Session 10216: the measures behind the map audit's claims, one rule at a time, from the page's own files
(site/data/map.json, site/data/map_layers/*.json) and the Census Bureau's county gazetteer (read only). Standard library.

  python runs/c10216/measures_map.py <site/data> <gazetteer folder>
"""
import bisect
import collections
import json
import math
import os
import re
import statistics
import sys
import unicodedata
import zipfile

DATA, GAZ = sys.argv[1:3]
f = json.load(open(os.path.join(DATA, "map.json"), encoding="utf-8"))
N = len(f["k"])
K0, K1, K2, K3 = (f["kinds"][j]["start"] for j in range(4))
R = 3958.8


def miles(la1, lo1, la2, lo2):
    a = math.sin(math.radians(la2 - la1) / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(min(1, math.sqrt(a)))


def pct(a, b):
    return f"{100 * a / b:.1f} percent" if b else "n/a"


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * (len(xs) - 1) + 0.5))]


print("== 1. Where each kind is placed (the file's precision code: 0 EIA's coordinates, 1 county point, 2 city or town point, 3 the operator's coordinates, 4 not placed)")
for kind in range(4):
    c = collections.Counter(f["pr"][i] for i in range(N) if f["k"][i] == kind)
    print(f"  {f['kinds'][kind]['name']}: {dict(sorted(c.items()))}")
dc_from = collections.Counter((f["more"]["datacenter"]["from"][i - K3], f["pr"][i]) for i in range(K3, N))
print("  datacenters by source kind and precision:", dict(sorted(dc_from.items())))
dc_mw = collections.Counter()
for i in range(K3, N):
    if f["mw"][i] is not None:
        dc_mw[f["pr"][i]] += f["mw"][i]
print("  datacenter MW stated, by precision:", {k: round(v, 1) for k, v in sorted(dc_mw.items())})

print("== 2. EIA's operating codes inside 'Operating'")
codes = f["more"]["operating"]["codes"]
c, m = collections.Counter(), collections.Counter()
for j, ci in enumerate(f["more"]["operating"]["code"]):
    c[codes[ci]["code"]] += 1
    m[codes[ci]["code"]] += f["mw"][K0 + j]
for code in c:
    print(f"  {code} ({codes[[x['code'] for x in codes].index(code)]['label']}): {c[code]:,} units, {m[code]:,.1f} MW")
print(f"  not OP: {sum(v for k, v in c.items() if k != 'OP'):,} units, {sum(v for k, v in m.items() if k != 'OP'):,.1f} MW of {sum(m.values()):,.1f}")

print("== 3. The marks' size: diameter 2 + 0.2 * sqrt(MW), held between 3 and 18 px")
for kind in range(3):
    rows = [f["mw"][i] or 0 for i in range(N) if f["k"][i] == kind]
    small = sum(1 for x in rows if x < 25)
    big = sum(1 for x in rows if x >= 6400)
    print(f"  {f['kinds'][kind]['name']}: {small:,} of {len(rows):,} under 25 MW ({pct(small, len(rows))}), drawn alike at the smallest size; {big} at or above 6,400 MW, drawn alike at the largest")

print("== 4. EIA's points are plants' points")
pts = collections.Counter((f["la"][i], f["lo"][i]) for i in range(K0, K2) if f["la"][i] is not None)
print(f"  {K2 - K0:,} units at {len(pts):,} distinct points; the most units at one point: {pts.most_common(1)[0][1]}")


# ---- the county gazetteer (2025, then 2020 for names it lacks), and the units' own counties
def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" (county|parish|borough|census area|city and borough|municipality)$", "", s)
    return s.replace(" ", "")


gaz = {}
for zname in sorted(os.listdir(GAZ), key=lambda z: "2020" in z):
    if not zname.endswith(".zip"):
        continue
    with zipfile.ZipFile(os.path.join(GAZ, zname)) as z:
        for member in z.namelist():
            raw = z.read(member)
            t = raw.decode("utf-8-sig") if raw[:3] == b"\xef\xbb\xbf" or b"\xc3" in raw[:200000] else raw.decode("latin-1")
            rows = t.splitlines()
            sep = "|" if "|" in rows[0] else "\t"
            head = [h.strip().lstrip("﻿") for h in rows[0].split(sep)]
            if "USPS" not in head:
                continue
            for ln in rows[1:]:
                v = dict(zip(head, [x.strip() for x in ln.split(sep)]))
                gaz.setdefault((v["USPS"], key(v["NAME"])), (float(v["INTPTLAT"]), float(v["INTPTLONG"])))

print("== 5. How far a county's internal point stands from the plants in it (EIA's units with a county the gazetteer holds)")
gap = {0: [], 1: []}
gap_mw = {0: [], 1: []}
countypt = {}
farlist = []
for i in range(K0, K2):
    if f["la"][i] is None or f["c"][i] < 0:
        continue
    st = f["states"][f["s"][i]]
    hit = gaz.get((st, key(f["counties"][f["c"][i]])))
    if not hit:
        continue
    d = miles(f["la"][i], f["lo"][i], hit[0], hit[1])
    gap[f["k"][i]].append(d)
    gap_mw[f["k"][i]].append((d, f["mw"][i] or 0))
    countypt[i] = hit
    if d > 100:
        farlist.append((round(d), st, f["counties"][f["c"][i]], f["names"][f["n"][i]], f["la"][i], f["lo"][i]))
for kind in (0, 1):
    xs = gap[kind]
    print(f"  {f['kinds'][kind]['name']}: {len(xs):,} units; median {statistics.median(xs):.1f} miles, 75th percentile {q(xs, .75):.1f}, 90th {q(xs, .9):.1f}, largest {max(xs):.0f}; "
          f"over 10 miles {pct(sum(1 for x in xs if x > 10), len(xs))}, over 20 {pct(sum(1 for x in xs if x > 20), len(xs))}; "
          f"MW-weighted median {statistics.median([d for d, w in gap_mw[kind] for _ in range(max(1, int(w // 10)))]):.1f}")
print(f"  units over 100 miles from their own county's point: {len(farlist)} (EIA's point or EIA's county is then wrong, or the county is very large); the first ten:")
for x in sorted(farlist, reverse=True)[:10]:
    print("   ", x)

print("== 6. One rule changed: a planned unit drawn at its county's point instead of EIA's coordinates, for 'Near a point' at 30 miles")
planned = [i for i in range(K1, K2) if i in countypt]
sites = [("Abilene", 32.4487, -99.7331), ("Amarillo", 35.2220, -101.8313), ("New Albany", 40.0812, -82.8088), ("Mason City", 43.1536, -93.2010), ("Bakersfield", 35.3733, -119.0187)]
for name, la, lo in sites:
    true = {i for i in planned if miles(la, lo, f["la"][i], f["lo"][i]) <= 30}
    cty = {i for i in planned if miles(la, lo, *countypt[i]) <= 30}
    print(f"  {name}: within 30 miles by EIA's point {len(true)}, by the county's point {len(cty)}; both {len(true & cty)}, lost {len(true - cty)}, gained {len(cty - true)}")
both = lost = gained = 0
for a in planned:
    la, lo = f["la"][a], f["lo"][a]
    for b in planned:
        if a == b:
            continue
        t = miles(la, lo, f["la"][b], f["lo"][b]) <= 30
        cc = miles(la, lo, *countypt[b]) <= 30
        both += t and cc
        lost += t and not cc
        gained += cc and not t
print(f"  every planned unit as a site, every other planned unit as a row: truly within 30 miles {both + lost:,} pairs; by the county point {both + gained:,}; "
      f"lost {lost:,} ({pct(lost, both + lost)} of the true), gained {gained:,} ({pct(gained, both + gained)} of those listed)")

print("== 7. Planned operation dates already past at the inventory's month (2026-09)")
past = [i for i in range(K1, K2) if f["d"][i] and int(str(f["d"][i])[:6].ljust(6, "0")) < 202609]
print(f"  {len(past):,} of {K2 - K1:,} planned units ({pct(len(past), K2 - K1)}), {sum(f['mw'][i] for i in past):,.1f} of {sum(f['mw'][i] for i in range(K1, K2)):,.1f} MW")
bys = collections.Counter(f["statuses"][f["st"][i]]["slug"] for i in past)
print("  by EIA status:", dict(bys))

print("== 8. Completed queue positions that bear the name of an operating unit in the same state (a plant drawn twice)")
DROP = re.compile(r"\b(solar|wind|energy|storage|bess|battery|project|power|farm|center|centre|llc|inc|lp|generating|generation|station|plant|facility|park|ranch|i|ii|iii|iv|v|phase|the|of|and|hybrid|repower|repowering|expansion|unit|units|\d+)\b")


def nm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", DROP.sub(" ", s)).strip()


opnames = collections.defaultdict(set)
for i in range(K0, K1):
    n = nm(f["names"][f["n"][i]])
    if len(n) >= 4:
        opnames[f["states"][f["s"][i]]].add(n)
match = collections.Counter()
match_mw = collections.Counter()
tot = collections.Counter()
for i in range(K2, K3):
    if f["statuses"][f["st"][i]]["slug"] != "q-completed":
        continue
    g = f["grids"][f["g"][i]]["slug"]
    tot[g] += 1
    n = nm(f["names"][f["n"][i]])
    if len(n) >= 4 and n in opnames[f["states"][f["s"][i]]]:
        match[g] += 1
        match_mw[g] += f["mw"][i] or 0
for g in tot:
    print(f"  {g}: {match[g]} of {tot[g]} completed positions ({pct(match[g], tot[g])}), {match_mw[g]:,.1f} MW requested")
print(f"  all: {sum(match.values())} of {sum(tot.values())}, {sum(match_mw.values()):,.1f} MW")

print("== 9. Held tables reaching the drawing: ISO-NE's queue positions and the datacenters")
isone = [i for i in range(K2, K3) if f["grids"][f["g"][i]]["slug"] == "isone"]
print(f"  ISO-NE: {len(isone)} positions, {sum(f['mw'][i] or 0 for i in isone):,.1f} MW requested; datacenters {K3 and N - K3}")

print("== 10. The line layers")
for name in ("transmission_230kv", "hgl_pipelines"):
    L = json.load(open(os.path.join(DATA, "map_layers", name + ".json"), encoding="utf-8"))
    print(f"  {name}: {L['lines']:,} lines, {L['km']:,} km; source: {L['source']}; retrieved {L['retrieved_at']}; built {L['built']}; license {L['license']}; "
          f"simplified at {L['simplify_tolerance_deg']} degrees; fields {L['fields']}; extra keys {[k for k in L if k not in ('rows', 'paths', 'names', 'fields', 'text_fields')]}")
    if name.startswith("trans"):
        fi = {k: j for j, k in enumerate(L["fields"])}
        kv = collections.Counter(r[fi["kv"]] for r in L["rows"])
        print(f"    voltage: {dict(sorted(kv.items(), key=lambda x: (x[0] is None, x[0] or 0)))}")
        val = lambda r, k: (L["names"][r[fi[k]]] if isinstance(r[fi[k]], int) and k in L["text_fields"] else r[fi[k]])
        no_owner = sum(1 for r in L["rows"] if val(r, "owner") is None)
        unnamed = sum(1 for r in L["rows"] if any(isinstance(val(r, e), str) and re.fullmatch(r"UNKNOWN\d+", val(r, e)) for e in ("from", "to")))
        print(f"    owner not stated {no_owner:,} ({pct(no_owner, L['lines'])}); an end HIFLD does not name {unnamed:,} ({pct(unnamed, L['lines'])})")
        TL = L

print("== 11. What a transmission planner would ask first: each planned unit's distance to the nearest line of 230 kV and above (the simplified web file)")
CELL = 0.5
segs = collections.defaultdict(list)
for path in TL["paths"]:
    for flat in path:
        for k in range(0, len(flat) - 3, 2):
            a, b, c2, d2 = flat[k], flat[k + 1], flat[k + 2], flat[k + 3]
            for cx in range(int(math.floor(min(a, c2) / CELL)), int(math.floor(max(a, c2) / CELL)) + 1):
                for cy in range(int(math.floor(min(b, d2) / CELL)), int(math.floor(max(b, d2) / CELL)) + 1):
                    segs[(cx, cy)].append((a, b, c2, d2))


def to_line(la, lo, reach=3):
    best = None
    cx, cy = int(math.floor(lo / CELL)), int(math.floor(la / CELL))
    kx = 69.172 * math.cos(math.radians(la))
    for dx in range(-reach, reach + 1):
        for dy in range(-reach, reach + 1):
            for (a, b, c2, d2) in segs.get((cx + dx, cy + dy), ()):
                ax, ay, bx, by = (a - lo) * kx, (b - la) * 69.0, (c2 - lo) * kx, (d2 - la) * 69.0
                vx, vy = bx - ax, by - ay
                L2 = vx * vx + vy * vy
                t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * vx + ay * vy) / L2))
                d = math.hypot(ax + t * vx, ay + t * vy)
                if best is None or d < best:
                    best = d
    return best   # None: no line within about 1.5 degrees


for kind, label in ((1, "planned units"), (0, "operating units")):
    ds = []
    for i in range(N):
        if f["k"][i] != kind or f["la"][i] is None or f["states"][f["s"][i]] in ("AK", "HI", "PR"):
            continue
        d = to_line(f["la"][i], f["lo"][i])
        ds.append((d if d is not None else 999.0, f["mw"][i] or 0))
    mw = sum(w for _, w in ds)
    for lim in (1, 5, 10, 20):
        n = sum(1 for d, _ in ds if d <= lim)
        w = sum(w for d, w in ds if d <= lim)
        print(f"  {label} (lower 48): within {lim} miles of a 230 kV line {n:,} of {len(ds):,} ({pct(n, len(ds))}), {pct(w, mw)} of their MW")
    big = [(d, w) for d, w in ds if w >= 100]
    print(f"  {label} of 100 MW or more: median distance {statistics.median([d for d, _ in big]):.1f} miles; over 10 miles {pct(sum(1 for d, _ in big if d > 10), len(big))}")
