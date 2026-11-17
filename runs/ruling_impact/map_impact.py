#!/usr/bin/env python3
"""ERW, ruling impact for /map (session 7585, 17 November 2026).

The three lines marked "Changes a figure" under the project map in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The page's own file is site/data/map.json (built 2026-11-16T16:45:58Z: EIA-860M of September 2026,
the queue positions and datacenters as the live set held them). No name or operator of a held table's row is printed
here: only counts and megawatt sums, and the three projects the rulings line already names.

    .venv/Scripts/python.exe runs/ruling_impact/map_impact.py
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = json.load(open(os.path.join(ROOT, "site", "data", "map.json"), encoding="utf-8"))
K = {k["slug"]: i for i, k in enumerate(J["kinds"])}
C = J["counts"]
print(f"map.json built {J['built']}: {C['rows']:,} points; operating {C['operating']:,} ({C['operating_mw']:,.1f} MW), planned {C['planned']:,} ({C['planned_mw']:,.1f} MW), "
      f"queue {C['queue']:,} ({C['queue_mw']:,.1f} MW), datacenters {C['datacenter']:,} ({C['datacenter_mw']:,.1f} MW)")

# ---- line 1: the queue positions' MW as the table states them, or rounded to one decimal
print("\n== line 1: the queue positions' MW kept as the table states them (other choice) or rounded to one decimal in the map's file (default)")
q = [i for i in range(len(J["k"])) if J["k"][i] == K["queue"]]
s = sum(J["mw"][i] for i in q if J["mw"][i] is not None)
print(f"the file's {len(q):,} queue rows sum to {s:,.1f} MW (the page writes {round(s):,} MW requested); each row is rounded to 0.1 MW, so the sum can be off by at most "
      f"{0.05 * len(q):,.1f} MW. On the build the faults file read, the table summed to 761,478.2 MW and the page wrote 761,479: +0.8 MW (+0.0001 percent). "
      "The table's own sum for this build needs the live set's rows, which this machine does not hold: not computed")

# ---- line 2: the map's copy of the held tables
print("\n== line 2: the Projects tab's queue and datacenter layers drawn from the map's own copy (default) or held like their tables")
print(f"held as points without name, operator or MW: {C['queue']:,} queue positions lose {C['queue_mw']:,.1f} MW and {C['datacenter']:,} datacenters lose {C['datacenter_mw']:,.1f} MW from every sum and tip; "
      f"the tab's total of points stays {C['rows']:,}")
print(f"held as no layer: the tab draws {C['rows'] - C['queue'] - C['datacenter']:,} points ({C['units']:,} generating units, {C['units_mw']:,.1f} MW); the queue's and the datacenters' counts and MW leave the tab")
print("the hold lifted for those rows: nothing on the tab moves; the tables' own pages would show the same rows")

# ---- line 3: a project counted once when it is both a planned unit and a queue position
print("\n== line 3: planned units and queue positions matched by name and county, so a project counts once")


def norm(s):
    s = s.upper()
    s = re.sub(r"\b(BESS|ESS|SOLAR|WIND|STORAGE|ENERGY|PROJECT|PROJECTS|CENTER|FARM|LLC|LP|INC|II|I|III|IV|PV|PHASE|STATION)\b", " ", s)
    return " ".join(re.sub(r"[^A-Z0-9 ]", " ", s).split())


plan = defaultdict(list)
for i in range(len(J["k"])):
    if J["k"][i] == K["planned"]:
        plan[(norm(J["names"][J["n"][i]]), J["c"][i])].append(i)
both, mw_dup = [], 0.0
for i in q:
    key = (norm(J["names"][J["n"][i]]), J["c"][i])
    if key[0] and key in plan:
        both.append(i)
        mw_dup += J["mw"][i] or 0
named = ("CHIMNEY ROCK", "FUNSTON", "TIGER")
abilene = [(J["names"][J["n"][i]], J["mw"][i]) for i in both if norm(J["names"][J["n"][i]]) in named]
print(f"queue positions whose name and county match a planned unit's (names compared without words such as Solar, BESS, LLC): {len(both):,}; their MW {mw_dup:,.1f} "
      f"({mw_dup / C['queue_mw'] * 100:.2f} percent of the queue's MW)")
print(f"the three the rulings line names, as matched here: {abilene}")
print("matched, the queue layer's sum would fall by that MW (or the planned layer's, by the rule chosen); the match is by words only and a ruling would fix its rule")
