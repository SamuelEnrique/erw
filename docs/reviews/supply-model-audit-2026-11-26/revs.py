"""Session 10222: EIA's revisions between the two copies (the main copy's tables of 9 October and 12 November against the
page file of 17 November) for the monthly rows: how many months of the file's last 52 moved, and by how much."""
import csv
import datetime as dt
import json
import re
import sys
from collections import defaultdict

F = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


tab = defaultdict(dict)
for name in ("eia_basin_production_monthly",):
    with open(f"{out}/{name}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            tab[slug(r["entity"])][r["ts_utc"][:10]] = float(r["value"])
for r in F["rows"]:
    if r["status"] != "ok" or r["id"] not in tab:
        continue
    s = tab[r["id"]]
    moved = [(t, s[t], v, 100 * (v / s[t] - 1)) for t, v in zip(r["spark"]["t"], r["spark"]["v"]) if t in s and abs(round(s[t], 4) - v) > 1.5e-4]
    recent = [m for m in moved if m[0] >= "2026-01-01"]
    big = max(moved, key=lambda m: abs(m[3])) if moved else None
    last_t = max(s)
    print(f"{r['id']:14} months moved {len(moved):2} of {sum(1 for t in r['spark']['t'] if t in s)}; in 2026 {len(recent)}; largest {big[0] if big else ''} {big[1] if big else ''} -> {big[2] if big else ''} ({big[3]:+.2f} percent)" if big else f"{r['id']:14} none moved", f"| the table's newest month {last_t}: {s[last_t]:.4f} -> file {dict(zip(r['spark']['t'], r['spark']['v'])).get(last_t)}")
