"""Session 10218: what site/data/price_compare.json holds (public grids' rows; held grids by name and count only)."""
import json
import os
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "site")
f = json.load(open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8"))
HELD = {"NYISO", "ISO-NE", "MISO"}
print("built", f["built"], "end_month", f["end_month"], "windows", f["windows"], "near", f["near_hours"], f["near_days"], "high", f["high"])
print("held_not_shown", len(f["held_not_shown"]), sorted({h["grid"] for h in f["held_not_shown"]}), "not_held", f["not_held"], "internal", f["internal_tables"])
for w in ("year", "month"):
    rows = f[w]
    print(f"== {w}: {len(rows)} rows; grids {sorted({r['grid'] for r in rows})}")
    for r in rows:
        if r["grid"] in HELD:
            print("  HELD ROW PRESENT", r["entity"], "keys", len(r))
            continue
        print("  ", json.dumps(r, separators=(",", ":")))
