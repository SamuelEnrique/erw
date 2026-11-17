#!/usr/bin/env python3
"""ERW, ruling impact for /attention (session 7597, 17 November 2026).

The one line marked "Changes a figure" under the Attention and Friction indices in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads): does a cell with fewer than ten stories print
its counts and no Friction Index? The page's own file, site/data/attention.json (built 2026-11-16T09:24:19Z), its
columns as the file names them.

    .venv/Scripts/python.exe runs/ruling_impact/attention_impact.py
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = json.load(open(os.path.join(ROOT, "site", "data", "attention.json"), encoding="utf-8"))
col = {c: i for i, c in enumerate(J["columns"]["cells"])}
cells = [dict(zip(J["columns"]["cells"], c)) for c in J["cells"]]
withf = [c for c in cells if c["friction_index"] is not None]
small = [c for c in withf if c["stories"] < 10]
print(f"attention.json: {len(cells)} cells (sector, place, week); with a Friction Index {len(withf)}; of them fewer than ten stories {len(small)} ({len(small) / len(withf) * 100:.1f} percent)")
print(f"   by place: all places {sum(1 for c in small if J['geos'][c['geo']] == 'all')}, the US {sum(1 for c in small if J['geos'][c['geo']] == 'US')}, a state {sum(1 for c in small if J['geos'][c['geo']] not in ('all', 'US'))}")
print(f"   the indices that would go: {Counter(c['friction_index'] for c in small).most_common(6)} (value: cells); 100 and 0 are a single story's whole weight")
newest = max(c["week"] for c in cells)
nw = [c for c in small if c["week"] == newest]
print(f"in the newest week ({J['weeks'][newest][:10]}): {len(nw)} of {sum(1 for c in withf if c['week'] == newest)} indices go")
va = [c for c in cells if J["geos"][c["geo"]] == "VA" and J["sectors"][c["sector"]] == "datacenters"]
for c in sorted(va, key=lambda c: c["week"])[-4:]:
    print(f"   Virginia, datacenters, week of {J['weeks'][c['week']][:10]}: {c['stories']} stories, {c['opposition_stories']} opposition, Friction Index {c['friction_index']} -> "
          f"{'counts only' if c['stories'] < 10 else 'kept'}")
tw = [dict(zip(J["columns"]["together"], t)) for t in J["together"]]
print(f"the 'together' rows (each sector over the classified weeks): fewer than ten stories in {sum(1 for t in tw if t['stories'] < 10)} of {len(tw)}")
