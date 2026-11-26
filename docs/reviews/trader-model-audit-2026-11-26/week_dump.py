"""Session 10209: the week table and spikes of site/data/board.json, public grids only (ERCOT, CAISO, SPP).
Held grids (NYISO, ISO-NE) and MISO: counts and dates only, never a value."""
import json
import sys
from collections import Counter

PUBLIC = {"ERCOT", "CAISO", "SPP"}
path = sys.argv[1] if len(sys.argv) > 1 else "site/data/board.json"
b = json.load(open(path, encoding="utf-8"))
print("built", b["built"], "heat_rate", b.get("heat_rate"), "gas_back_days", b.get("gas_back_days"))
week = b["week"]
print("week rows by grid", Counter(w["grid"] for w in week))
for w in week:
    if w["grid"] not in PUBLIC:
        continue
    keys = {k: (m["v"], m["ch"], m["end"]) for k, m in w["means"].items()}
    print(w["hub"], "| last_da", w.get("last_da"), "| max", w.get("max_spread"), "| h50", w.get("hours50"), "| vol", w.get("vol"))
    for k, v in keys.items():
        print("    ", k, v)
held = [w for w in week if w["grid"] not in PUBLIC]
print("held or other week rows:", len(held), sorted({w["grid"] for w in held}))
sp = b["spikes"]
print("spikes by grid", Counter(s["grid"] for s in sp))
for s in sp:
    if s["grid"] in PUBLIC:
        print("  spike", s["grid"], s["code"], s["t"], s["v"], s["freq"])
