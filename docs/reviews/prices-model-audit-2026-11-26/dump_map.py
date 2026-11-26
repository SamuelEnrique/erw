"""Session 10218: what site/data/regions/prices_map.json holds (shown grids' figures; held grids by state only)."""
import json
import os
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "site")
m = json.load(open(os.path.join(SITE, "data", "regions", "prices_map.json"), encoding="utf-8"))
print("built", m["built"], "tables", m["tables"])
print("rules", m["rules"])
for g in m["grids"]:
    print("GRID", g["grid"], g.get("ba"), g["state"], g.get("region"), g.get("hubs"), (g.get("why") or "")[:90],
          "nodes listed:", len(g.get("nodes") or []))
for h in m["hubs"]:
    print("HUB", {k: v for k, v in h.items() if k not in ("region",)})
for k, b in m["bas"].items():
    print("BA", k, b)
# any number under a held grid?
for g in m["grids"]:
    if g["state"] != "shown":
        nums = [k for k, v in g.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        print("held grid numeric keys", g["grid"], nums)
