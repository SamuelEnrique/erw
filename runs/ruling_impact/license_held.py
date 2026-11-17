"""Session 7615 (portable-laptop): the tables held on 17 November 2026 by site/data/license_status.json, with their
publishers and whether the hold is by grid (every publisher a grid operator), as site/lib/license.ts reads them."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
GRIDS = {"ISO-NE", "MISO", "NYISO", "PJM", "SPP", "CAISO", "ERCOT"}
d = json.loads((ROOT / "site" / "data" / "license_status.json").read_text(encoding="utf-8"))
print("from", d.get("from"), "written", d.get("written"))
held_grids = set()
for name, r in sorted(d["tables"].items()):
    status = r.get("status") or r.get("license") or ""
    pubs = r.get("publishers") or []
    if "need" not in str(status).lower():
        continue
    by = "row" if r.get("hold") == "row" else ("grid" if pubs and all(p in GRIDS for p in pubs) else "whole")
    held_grids |= {p for p in pubs if p in GRIDS}
    if len(sys.argv) > 1 and sys.argv[1] not in name:
        continue
    print(f"{name}: held by {by}; publishers {pubs}")
print("held grids:", sorted(held_grids))
