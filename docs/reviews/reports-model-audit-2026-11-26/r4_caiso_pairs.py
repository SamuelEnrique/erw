"""Session 10232 (reports audit), r4: California's net import share by EIA's balance and by the pair sums, either side
of 16 December 2025 (the break the AI gigawatts draft's banner names), over the draft's year, restated from the extract
and eia930_daily_interchange (streamed: only CISO's rows are kept). Complete days as the builder counts them: a day
counts when every regular neighbour (present on at least half of the year's days) reported it.

    python runs/c10232/r4_caiso_pairs.py <csv dir> <raw extract dir>
"""
import csv
import os
import sys
from collections import defaultdict

CSV_DIR, EXTRACT_DIR = sys.argv[1], sys.argv[2]
W0, W1, BREAK = "2025-09-01", "2026-09-01", "2025-12-16"
days = defaultdict(dict)
with open(os.path.join(CSV_DIR, "eia930_daily_interchange.csv"), encoding="utf-8") as f:
    head = None
    for ln in f:
        if ln.startswith("#"):
            continue
        if head is None:
            head = next(csv.reader([ln]))
            ib, it, ie, iv = head.index("ba"), head.index("ts_utc"), head.index("entity"), head.index("value")
            continue
        if ",ciso," not in ln:
            continue
        r = next(csv.reader([ln]))
        if r[ib] != "ciso" or not (W0 <= r[it][:10] < W1):
            continue
        days[r[it][:10]][r[ie]] = float(r[iv])
cnt = defaultdict(int)
for d in days.values():
    for e in d:
        cnt[e] += 1
regular = {e for e, c in cnt.items() if c >= 0.5 * len(days)}
ok = sorted(d for d, v in days.items() if regular <= set(v))
dem = defaultdict(float)
ng = defaultdict(float)
with open(os.path.join(EXTRACT_DIR, "ciso_hours.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
        if not (W0 <= r["ts_utc"][:10] < W1):
            continue
        try:
            dd, gg = float(r["demand_mwh"]), float(r["net_generation_mwh"])
        except ValueError:
            continue
        dem[r["ts_utc"][:10]] += dd
        ng[r["ts_utc"][:10]] += gg
for label, sel in (("before 16 December 2025", lambda d: d < BREAK), ("from 16 December 2025", lambda d: d >= BREAK), ("the year", lambda d: True)):
    ds = [d for d in ok if sel(d) and dem.get(d)]
    pair = -sum(sum(days[d].values()) for d in ds) / sum(dem[d] for d in ds) * 100
    bal = (sum(dem[d] for d in ds) - sum(ng[d] for d in ds)) / sum(dem[d] for d in ds) * 100
    print(f"{label}: {len(ds)} complete days; pair sums {pair:.2f} percent; EIA's balance on the same days {bal:.2f} percent; gap {bal - pair:.2f} points")
