# Session 10206: which rows, week lines and spikes of site/data/board.json carry a figure for a held grid (NYISO, ISO-NE,
# MISO, PJM). Prints ids, counts and dates only: never a held value.
import collections
import json
import os

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site")
b = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
HELD = ("nyiso", "isone", "miso", "pjm")
rows = [r for r in b["rows"] if r["id"].startswith(HELD)]
print("held-grid rows:", len(rows), collections.Counter(r["status"] for r in rows))
with_fig = [r for r in rows if "last" in r]
print("held-grid rows carrying a latest value:", len(with_fig))
for r in with_fig:
    print("  ", r["id"], r["group"], r["status"], "last date", r["last"]["t"], "series points", len(r.get("spark", {}).get("v", [])))
wk = [w for w in b["week"] if w["hub"].startswith(HELD)]
print("week lines of held grids:", len(wk), [(w["hub"], sorted(w.get("means", {}).keys())[:2], w.get("last_da", {}).get("t")) for w in wk])
sp = [s for s in b["spikes"] if s["hub"].startswith(HELD)]
print("spikes of held grids:", len(sp), "dates", sorted({s["t"][:10] for s in sp}))
# the ids whose label names the grid but whose id does not start with it (a spread across grids)
other = [r["id"] for r in b["rows"] if not r["id"].startswith(HELD) and any(h in r["id"] for h in HELD) and "last" in r]
print("rows naming a held grid inside the id, with a value:", other)
