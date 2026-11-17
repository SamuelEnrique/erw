#!/usr/bin/env python3
"""ERW, ruling impact for /datacenters (session 7594, 17 November 2026).

The seven lines marked "Changes a figure" under the datacenter tracker in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). datacenter_facilities is held ("license needed"): this file prints counts and sums only,
never a facility's name, operator or own figure. A facility is counted as the page counts it (the method note, by
replication/datacenter_tracker/replicate.py: in the United States and not withdrawn or cancelled; its MW the table's
capacity_mw). The source registry warehouse/metadata/sources.csv gives each source's license; the grids' public figures
are the site's own copy, site/data/siting/headroom.json (EIA-930's peak hour and EIA-860M's capacity); site/data/map.json
the map's layer.

    .venv/Scripts/python.exe runs/ruling_impact/datacenters_impact.py
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "warehouse", "output")
US = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN "
         "TX UT VT VA WA WV WI WY".split())


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


with open(os.path.join(OUT, "datacenter_facilities.csv"), encoding="utf-8", newline="") as f:
    R = list(csv.DictReader(l for l in f if not l.startswith("#")))
counted = [r for r in R if (r["country"] or ("US" if r["state"] in US else "")) == "US" and (r["status"] or "").lower() not in ("withdrawn", "cancelled")]
mw = lambda r: num(r["capacity_mw"])
stating = [r for r in counted if mw(r) is not None]
total = sum(mw(r) for r in stating)
LIC = {r["source"]: r["license"] for r in csv.DictReader(open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8"))}
print(f"datacenter_facilities: {len(R)} rows, {len(counted)} counted; MW stated by {len(stating)}: {total:,.0f} MW (the page's 28,254 MW by 21)")

print("\n== line 1: the facilities held whole (default) or the rows whose every source is public shown, each with its license")
PUBLIC_DOMAINS = {"digitalrealty.com", "equinix.com", "datacenters.google", "cloud.google.com", "datacenters.atmeta.com", "azure.microsoft.com", "b0.p.awsstatic.com",
                  "switch.com", "oracle.com", "ercot.com"}
pub = []
for r in counted:
    doms = {re.sub(r"^www\.", "", m.group(1)) for u in (r["source_urls"] or r["source_url"] or "").split(";") for m in [re.match(r"https?://([^/]+)", u.strip())] if m}
    if LIC.get(r["source"]) == "public" and doms and doms <= PUBLIC_DOMAINS:
        pub.append(r)
pm = [r for r in pub if mw(r) is not None]
print(f"counted rows whose source is public in the registry and every cited page a public source's (the operators' own location pages, ERCOT): {len(pub)} of {len(counted)}; "
      f"MW stated by {len(pm)} of them, {sum(mw(r) for r in pm):,.0f} MW; the other {len(counted) - len(pub)} rest on at least one news source (internal) and stay held")

print("\n== line 2: the by-grid view's peak hour and generating capacity (EIA's public figures) shown while the facilities are held")
H = json.load(open(os.path.join(ROOT, "site", "data", "siting", "headroom.json"), encoding="utf-8"))["peak_capacity"]
for g, v in H.items():
    print(f"   {g}: peak hour {v['year']} {v['peak_mw']:,.0f} MW; generating capacity {v['capacity_mw']:,.1f} MW (list {v['list']})")
print(f"{2 * len(H)} cells would go from the hold's footnote to a figure; the share of peak (a facility figure) stays held")

print("\n== line 3: the project map's datacenter layer while the tracker shows none")
M = json.load(open(os.path.join(ROOT, "site", "data", "map.json"), encoding="utf-8"))
print(f"the map's file of {M['built']}: {M['counts']['datacenter']} datacenters, {M['counts']['datacenter_mw']:,.1f} MW stated (the rulings file's 263 and 15,384 MW are an earlier build); "
      "held there too, these leave the map (ruling-impact-map-2026-11-17.md, line 1); the tracker's own figures do not move")

print("\n== line 4: the views by operator count a facility under its developer where no operator is named")
no_op = [r for r in stating if not (r["operator"] or "").strip()]
dev = [r for r in no_op if (r["developer"] or "").strip()]
a = sum(mw(r) for r in no_op)
b = a - sum(mw(r) for r in dev)
print(f"'operator not stated' (rows stating MW): {len(no_op)} facilities, {a:,.0f} MW of {total:,.0f}; counted under the developer where one is named: {len(no_op) - len(dev)} facilities, "
      f"{b:,.0f} MW ({b - a:+,.0f} MW, {(b / a - 1) * 100 if a else 0:+.1f} percent); {len(dev)} facilities move to their developers' lines (names not printed: held)")

print("\n== line 5: the headline 'Megawatts stated' with a line naming the share held by its two largest rows")
top2 = sorted((mw(r) for r in stating), reverse=True)[:2]
print(f"the two largest rows hold {sum(top2):,.0f} of {total:,.0f} MW ({sum(top2) / total * 100:.1f} percent); one figure added, none moves")

print("\n== lines 6 and 7: the cross-check's published figures on the page; PJM's two figures in the cross-check")
va = [r for r in counted if r["state"] == "VA"]
print(f"Virginia: {len(va)} facilities counted, {sum(mw(r) or 0 for r in va):,.0f} MW stated; the cross-check's Dominion figure beside it: a 4,800 MW datacenter billing peak")
print("line 7: dropping PJM's two figures removes two rows of the cross-check note (PJM's 2026 load report; Dominion's presentation on PJM's committee page); no figure of the page moves")
