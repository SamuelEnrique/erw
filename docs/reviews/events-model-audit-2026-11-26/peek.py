"""Session 10225: the header fields of three event region files (no data values printed beyond the header)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for ev in ("uri_2021", "caiso_heat_2020", "elliott_2022"):
    f = json.load(open(os.path.join(ROOT, "site", "data", "regions", "events", ev + ".json"), encoding="utf-8"))
    hdr = {k: v for k, v in f.items() if k not in ("regions", "pairs")}
    print(ev, json.dumps(hdr, indent=1)[:1500])
    print("  regions:", sorted(f["regions"]), "pairs:", len(f.get("pairs", {})))
    r = f["regions"].get("TEX") or f["regions"].get("CAL")
    print("  region keys:", sorted(r), "baseline keys:", sorted(r.get("baseline", {})))
