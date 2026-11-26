"""Session 10216: three more measures for the map audit. Standard library; files on disk only.

  python runs/c10216/measures2_map.py <site/data> <main copy warehouse/output> <gazetteer folder>

1. The point of interconnection: how many of the public queue tables' positions name one (CAISO, ERCOT, SPP; the
   held ISO-NE, MISO and NYISO tables are not read). The map carries none.
2. The proposed in-service dates the page's file carries and no card shows: how many, and how many had passed by the
   queue's own vintage.
3. EIA units whose point lies nearer another state's counties than their own state's, and far from their own county.
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

DATA, OUT, GAZ = sys.argv[1:4]
f = json.load(open(os.path.join(DATA, "map.json"), encoding="utf-8"))
K0, K1, K2, K3 = (f["kinds"][j]["start"] for j in range(4))


def miles(la1, lo1, la2, lo2):
    a = math.sin(math.radians(la2 - la1) / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 3958.8 * math.asin(min(1, math.sqrt(a)))


def read_csv(path):
    with open(path, encoding="utf-8") as fh:
        head = [ln for ln in fh if ln.startswith("#")]
    with open(path, encoding="utf-8") as fh:
        body = "".join(ln for ln in fh if not ln.startswith("#"))
    return head, list(csv.DictReader(io.StringIO(body)))


print("== 1. The point of interconnection in the public queue tables (main copy, read only)")
for g in ("caiso", "ercot", "spp"):
    head, rows = read_csv(os.path.join(OUT, f"{g}_interconnection_queue.csv"))
    ret = [h for h in head if h.startswith("# Retrieved")]
    live = [r for r in rows if r["status"] != "withdrawn"]
    poi = sum(1 for r in live if r["poi"].strip())
    print(f"  {g}: {poi:,} of {len(live):,} positions not withdrawn name a point of interconnection ({100 * poi / len(live):.1f} percent); {ret[0].strip() if ret else ''}")
    ex = [r["poi"] for r in live if r["poi"].strip()][:3]
    print(f"    for example: {ex}")

print("== 2. The proposed in-service date: in the page's file, on no card")
mq = f["more"]["queue"]
vint = int(f["vintages"]["queue"].replace("-", ""))
c = collections.Counter()
for j in range(f["kinds"][2]["rows"]):
    i = K2 + j
    p = mq["proposed"][j]
    st = f["statuses"][f["st"][i]]["slug"]
    g = f["grids"][f["g"][i]]["slug"]
    c[(g, st, "none" if not p else ("passed" if int(str(p).ljust(8, "0")[:8]) < vint else "to come"))] += 1
tot = sum(v for k, v in c.items() if k[2] != "none")
print(f"  {tot:,} of {f['kinds'][2]['rows']:,} positions carry one; queue vintage {f['vintages']['queue']}")
for k in sorted(c):
    print("   ", k, c[k])
act_passed = sum(v for k, v in c.items() if k[1] == "q-active" and k[2] == "passed")
act = sum(v for k, v in c.items() if k[1] == "q-active")
print(f"  active positions whose proposed date had passed by the vintage: {act_passed:,} of {act:,}")


def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" (county|parish|borough|census area|city and borough|municipality)$", "", s)
    return s.replace(" ", "")


pts = []
own = {}
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
                la, lo = float(v["INTPTLAT"]), float(v["INTPTLONG"])
                if "2020" not in zname:
                    pts.append((la, lo, v["USPS"]))
                own.setdefault((v["USPS"], key(v["NAME"])), (la, lo))

print("== 3. EIA units drawn in another state: the nearest county internal point is another state's, and the unit is over 50 miles from its own county's point")
cells = collections.defaultdict(list)
for la, lo, st in pts:
    cells[(int(la // 1), int(lo // 1))].append((la, lo, st))


def nearest_state(la, lo):
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for pla, plo, st in cells.get((int(la // 1) + dx, int(lo // 1) + dy), ()):
                d = miles(la, lo, pla, plo)
                if best is None or d < best[0]:
                    best = (d, st)
    return best


wrong = []
for i in range(K0, K2):
    if f["la"][i] is None or f["c"][i] < 0:
        continue
    st = f["states"][f["s"][i]]
    hit = own.get((st, key(f["counties"][f["c"][i]])))
    if not hit:
        continue
    d_own = miles(f["la"][i], f["lo"][i], *hit)
    if d_own <= 50:
        continue
    ns = nearest_state(f["la"][i], f["lo"][i])
    if ns and ns[1] != st:
        wrong.append((round(d_own), st, ns[1], f["counties"][f["c"][i]], f["names"][f["n"][i]], f["kinds"][f["k"][i]]["slug"], f["mw"][i], f["id"][i]))
print(f"  {len(wrong)} units, {sum(w[6] or 0 for w in wrong):,.1f} MW; plants: {len({w[7].split(':')[0] for w in wrong})}")
for w in sorted(wrong, reverse=True):
    print("   ", w)
