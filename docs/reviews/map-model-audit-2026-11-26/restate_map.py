"""Session 10216: /map's Projects tab, default view, restated from the page's own file (site/data/map.json) with the
standard library alone, written from docs/methods/map.md (sections 3 to 11) and the page's words, not from
site/lib/projectmap.ts or warehouse/derived/project_map.py. Compares with the drawing (runs/c10216/out/default.html,
drawn by the site's own ProjectMap with draw.mjs).

  python runs/c10216/restate_map.py <map.json> <default.html> <main copy warehouse/output> <gazetteer folder>
"""
import collections
import csv
import io
import json
import math
import os
import re
import sys
import unicodedata
import zipfile

MAP, HTML, OUT, GAZ = sys.argv[1:5]
f = json.load(open(MAP, encoding="utf-8"))
html = open(HTML, encoding="utf-8").read()
N = len(f["k"])
ok = bad = 0


def check(what, mine, page):
    global ok, bad
    if str(mine) == str(page):
        ok += 1
    else:
        bad += 1
        print(f"  DIFFERS {what}: restated {mine} page {page}")


def whole(x):
    # half away from zero, as a reader rounds a sum to the megawatt (the page's sums are positive)
    return f"{int(math.floor(x + 0.5)):,}"


# ---- the projection the drawing uses (d3-geo geoAlbersUsa, scale 1300, translate 487.5, 305), written from d3's own
# published constants: three conic equal-area projections and their clip boxes
def conic(par0, par1):
    s0, s1 = math.sin(math.radians(par0)), math.sin(math.radians(par1))
    n = (s0 + s1) / 2
    c = 1 + s0 * (2 * n - s0)
    r0 = math.sqrt(c) / n

    def raw(lam, phi):
        r = math.sqrt(max(0.0, c - 2 * n * math.sin(phi))) / n
        return r * math.sin(lam * n), r0 - r * math.cos(lam * n)
    return raw


def proj(par, rot, center, k, tx, ty):
    raw = conic(*par)
    cx, cy = raw(math.radians(center[0]), math.radians(center[1]))

    def p(lon, lat):
        lam = math.radians(((lon + rot + 180) % 360) - 180)
        x, y = raw(lam, math.radians(lat))
        return tx + k * (x - cx), ty - k * (y - cy)
    return p


K, X, Y = 1300.0, 487.5, 305.0
LOWER48 = proj((29.5, 45.5), 96, (-0.6, 38.7), K, X, Y)
ALASKA = proj((55, 65), 154, (-2, 58.5), K * 0.35, X - 0.307 * K, Y + 0.201 * K)
HAWAII = proj((8, 18), 157, (-3, 19.9), K, X - 0.205 * K, Y + 0.212 * K)
BOXES = [(LOWER48, (X - 0.455 * K, Y - 0.238 * K, X + 0.455 * K, Y + 0.238 * K), "lower48"),
         (ALASKA, (X - 0.425 * K, Y + 0.120 * K, X - 0.214 * K, Y + 0.234 * K), "alaska"),
         (HAWAII, (X - 0.214 * K, Y + 0.166 * K, X - 0.115 * K, Y + 0.234 * K), "hawaii")]


def where(lon, lat):
    for p, (x0, y0, x1, y1), name in BOXES:
        x, y = p(lon, lat)
        if x0 <= x < x1 and y0 <= y < y1:
            return name
    return None


# ---- the default view: every row chosen
kinds = [k["slug"] for k in f["kinds"]]
by_kind = collections.defaultdict(lambda: [0, 0.0, 0])
by_status = collections.defaultdict(lambda: [0, 0.0, 0])
by_tech = collections.defaultdict(lambda: [0, 0.0])
drawn, box_of = 0, collections.Counter()
for i in range(N):
    k, mw = f["k"][i], f["mw"][i]
    for agg, key in ((by_kind, k), (by_status, f["st"][i])):
        agg[key][0] += 1
        if mw is not None:
            agg[key][1] += mw
            agg[key][2] += 1
    if k != 3:
        by_tech[(f["techs"][f["t"][i]]["slug"], kinds[k])][0] += 1
        by_tech[(f["techs"][f["t"][i]]["slug"], kinds[k])][1] += mw or 0
    if f["la"][i] is not None and f["lo"][i] is not None:
        w = where(f["lo"][i], f["la"][i])
        box_of[(w, f["states"][f["s"][i]] in ("AK", "HI", "PR") and f["states"][f["s"][i]] or "other")] += 1
        drawn += w is not None
print(f"rows {N}; drawn {drawn}; not drawn {N - drawn}")
print("projection box by state group:", sorted(box_of.items(), key=str))

text = re.sub(r"<[^>]+>", "", html).replace("&#x27;", "'").replace("&amp;", "&")
m = re.search(r"the map holds ([\d,]+) generating units of EIA's inventory of (\S+), ([\d,]+) MW; ([\d,]+) queue positions, ([\d,]+) MW requested; and ([\d,]+) datacenters, ([\d,]+) MW stated at ([\d,]+) of them", text)
units = by_kind[0][0] + by_kind[1][0]
check("sentence: units", f"{units:,}", m.group(1))
check("sentence: vintage", f["vintage"], m.group(2))
check("sentence: units MW", whole(by_kind[0][1] + by_kind[1][1]), m.group(3))
check("sentence: queue positions", f"{by_kind[2][0]:,}", m.group(4))
check("sentence: queue MW", whole(by_kind[2][1]), m.group(5))
check("sentence: datacenters", f"{by_kind[3][0]:,}", m.group(6))
check("sentence: datacenter MW", whole(by_kind[3][1]), m.group(7))
check("sentence: datacenters stating MW", f"{by_kind[3][2]:,}", m.group(8))
print(f"  queue MW: file's own count {f['counts']['queue_mw']:,}, sum of the rows as rounded in the file {by_kind[2][1]:,.1f}")

# tiles
tiles = re.findall(r'data-map-total="([^"]+)"[^>]*>([^<]*)</span>(?:<span[^>]*>MW</span>)?</div><div class="text-xs leading-snug text-muted">(.*?)</div>', html)
slug_i = {s["slug"]: j for j, s in enumerate(f["statuses"])}
shown = set()
for slug, val, note in tiles:
    j = slug_i[slug]
    shown.add(j)
    rows, mw, with_mw = by_status[j]
    kind = f["statuses"][j]["kind"]
    check(f"tile {slug} MW", whole(mw) if with_mw else "not stated", val)
    note = re.sub(r"<[^>]+>", "", note).replace("<!-- -->", "")
    if kind == 3:
        want = f"{rows:,} {'facility' if rows == 1 else 'facilities'}, " + (f"MW stated at {with_mw:,}" if with_mw else "no MW stated")
    else:
        word = "position" if kind == 2 else "unit"
        want = f"{rows:,} {word}{'' if rows == 1 else 's'}"
    check(f"tile {slug} count", want, note)
check("tiles drawn: every status with a row", sorted(j for j in by_status if by_status[j][0]), sorted(shown))

# by technology
for slug, kind, val in re.findall(r'data-tech-count="([^"|]+)\|([^"]+)"[^>]*>(.*?)</span>(?=<)', html):
    val = re.sub(r"<[^>]+>", "", val)
    check(f"tech count {slug}|{kind}", f"{by_tech[(slug, kind)][0]:,}", val)
for slug, kind, val in re.findall(r'data-tech-mw="([^"|]+)\|([^"]+)"[^>]*>(.*?)</span>', html):
    n, mw = by_tech[(slug, kind)]
    check(f"tech MW {slug}|{kind}", whole(mw) if n else "", val)
techs_drawn = set(re.findall(r'data-tech-count="([^"|]+)\|operating"', html))
want_techs = {t["slug"] for t in f["techs"] if t["slug"] != "datacenter" and any(by_tech[(t["slug"], kk)][0] for kk in kinds[:3])}
check("tech rows drawn", sorted(want_techs), sorted(techs_drawn))

# not drawn, drawn
m2 = re.search(r'data-map-not-drawn="1"[^>]*>([\d,]+)<', html)
check("rows with no place on the drawing", f"{N - drawn:,}", m2.group(1))
m3 = re.search(r'data-map-drawn="(\d+)"', html)
check("rows drawn (the map's accessible name)", str(drawn), m3.group(1))
held = re.findall(r"<li title=\"[^\"]*\"><span[^>]*>([^<]*)</span></li>", html)
check("held queues line", [f"{h['name']} queue positions: {h['words']}" for h in f["held"]], [h.replace("&#x27;", "'") for h in held])
check("lead: the unit count (counts.units)", f"{f['counts']['units']:,}", f"{units:,}")

# ---- the page's file against EIA's own tables (the main copy's warehouse/output, read only)
def read_csv(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lines))))


GRID = {"ERCO": "ercot", "CISO": "caiso", "PJM": "pjm", "MISO": "miso", "SWPP": "spp", "NYIS": "nyiso", "ISNE": "isone"}
eia = {}
for name in ("eia860m_operating_generators", "eia860m_planned_generators"):
    for r in read_csv(os.path.join(OUT, name + ".csv")):
        eia[r["entity_id"].replace("eia860:", "", 1)] = r
vint = collections.Counter(r["vintage"] for r in eia.values())
print(f"EIA tables of the main copy: {len(eia)} units, vintages {dict(vint)}")
same = collections.Counter()
diff = collections.Counter()
for i in range(f["kinds"][0]["start"], f["kinds"][2]["start"]):
    r = eia.get(f["id"][i])
    if r is None:
        diff["unit not in the tables"] += 1
        continue
    tg = r["technology_group"] if r["technology_group"] else "unknown"
    if tg == "storage" and r["prime_mover"] == "BA":
        tg = "battery"
    fields = {
        "mw": (round(float(r["capacity_mw"]), 1), f["mw"][i]),
        "lat": (round(float(r["lat"]), 4) if r["lat"] else None, f["la"][i]),
        "lon": (round(float(r["lon"]), 4) if r["lon"] else None, f["lo"][i]),
        "state": (r["state"], f["states"][f["s"][i]]),
        "grid": (GRID.get(r["balancing_authority"], "outside"), f["grids"][f["g"][i]]["slug"]),
        "tech": (tg, f["techs"][f["t"][i]]["slug"]),
        "status": ("operating" if r["status"] == "operating" else r["eia_status"].lower(), f["statuses"][f["st"][i]]["slug"]),
        "name": (r["name"], f["names"][f["n"][i]]),
    }
    for key, (a, b) in fields.items():
        (same if a == b else diff)[key] += 1
print(f"units in the file against EIA's tables: same {dict(same)}; differ {dict(diff)}")
op_mw = sum(float(r["capacity_mw"]) for r in eia.values() if r["status"] == "operating")
check("operating MW from EIA's table (to the MW)", whole(op_mw), whole(by_status[0][1]))
check("planned units from EIA's table", f"{sum(1 for r in eia.values() if r['status'] != 'operating'):,}", f"{by_kind[1][0]:,}")


# ---- queue positions placed at a county's internal point: restated from the Census Bureau's own gazetteer zips
def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" (county|parish|borough|census area|city and borough|municipality)$", "", s)
    return s.replace(" ", "")


gaz = {}
GAZ20, GAZ25 = {}, {}
for zname in sorted(os.listdir(GAZ), key=lambda z: "2020" in z):   # the 2025 file first, then 2020's for names it lacks
    if not zname.endswith(".zip"):
        continue
    with zipfile.ZipFile(os.path.join(GAZ, zname)) as z:
        for member in z.namelist():
            raw = z.read(member)
            text_ = raw.decode("utf-8-sig") if raw[:3] == b"\xef\xbb\xbf" or b"\xc3" in raw[:200000] else raw.decode("latin-1")
            rows = text_.splitlines()
            sep = "|" if "|" in rows[0] else "\t"
            head = [h.strip().lstrip("﻿") for h in rows[0].split(sep)]
            if "USPS" not in head:
                print("  gazetteer member without USPS:", member, head[:5])
                continue
            for ln in rows[1:]:
                v = dict(zip(head, [x.strip() for x in ln.split(sep)]))
                (GAZ20 if "2020" in zname else GAZ25)[(v["USPS"], key(v["NAME"]))] = (float(v["INTPTLAT"]), float(v["INTPTLONG"]))
                gaz.setdefault((v["USPS"], key(v["NAME"])), (float(v["INTPTLAT"]), float(v["INTPTLONG"]), v["NAME"], zname[-30:]))
print(f"gazetteer keys: {len(gaz)}")
qstart, qrows = f["kinds"][2]["start"], f["kinds"][2]["rows"]
res = collections.Counter()
far = []
for i in range(qstart, qstart + qrows):
    if f["pr"][i] != 1:
        continue
    st, county = f["states"][f["s"][i]], (f["counties"][f["c"][i]] if f["c"][i] >= 0 else "")
    hit = gaz.get((st, key(county)))
    if hit is None:
        for part in re.split(r"\s*[-/,;]\s*|\s+and\s+", re.sub(r",\s*[A-Z]{2}$", "", county)):
            hit = gaz.get((st, key(part)))
            if hit:
                break
    if hit is None:
        res["county words not found by the restatement"] += 1
        print("   not found:", repr(county), st, f["la"][i], f["lo"][i])
        continue
    same_pt = (round(hit[0], 4), round(hit[1], 4)) == (f["la"][i], f["lo"][i])
    res["same point" if same_pt else "another point"] += 1
    if not same_pt:
        far.append((county, st, hit[2], f["la"][i], f["lo"][i], hit[0], hit[1]))
print(f"queue positions at a county point ({sum(1 for i in range(qstart, qstart + qrows) if f['pr'][i] == 1)}): {dict(res)}")
def miles(la1, lo1, la2, lo2):
    a = math.sin(math.radians(la2 - la1) / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 3958.8 * math.asin(min(1, math.sqrt(a)))


gaps = sorted((miles(x[3], x[4], x[5], x[6]), x) for x in far)
print("  another point: gap in miles, largest ten:")
for d, x in gaps[-10:]:
    print(f"    {d:.3f}", x)
print(f"  another point within 0.01 mile: {sum(1 for d, _ in gaps if d < 0.01)}; over 0.1 mile: {sum(1 for d, _ in gaps if d >= 0.1)}")
trunc = sum(1 for _, x in gaps if (math.trunc(x[5] * 1e4) / 1e4, math.trunc(x[6] * 1e4) / 1e4) == (x[3], x[4]))
print(f"  another point equal to the gazetteer's point cut (not rounded) to four decimals: {trunc}")
src = collections.Counter()
for d, x in gaps:
    k20 = GAZ20.get((x[1], key(x[0])))
    near20 = k20 is not None and miles(x[3], x[4], k20[0], k20[1]) < 0.01
    src["within 0.01 mile of the 2020 file's point" if near20 else ("within 0.01 mile of the 2025 point" if d < 0.01 else "neither")] += 1
print("  another point, which file it is nearest:", dict(src))
CT = [k for k in GAZ25 if k[0] == "CT"]
print("  Connecticut in the 2025 file:", sorted(GAZ25_names for GAZ25_names in [k[1] for k in CT])[:12])

print(f"\nRESULT: {ok} of {ok + bad} drawn figures and checks agree")
