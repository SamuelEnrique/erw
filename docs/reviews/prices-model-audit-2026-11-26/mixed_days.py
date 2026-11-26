"""Session 10218: a copy of prices_map.json with CAISO's area moved to another day, to read the legend's words when the
areas' days differ (written under runs/, never committed)."""
import json
import sys

m = json.load(open(sys.argv[1], encoding="utf-8"))
m["bas"]["CISO"]["day"] = "2026-11-15"
json.dump(m, open(sys.argv[2], "w", encoding="utf-8"))
print("written", sys.argv[2])
