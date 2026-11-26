"""Data request 15 of docs/state/data_requests_five_tools.md (the board audit): the board's week lines for ERCOT's six
hubs, CAISO ZP26 and SPP South recomputed from iso_trader_daily for 19 to 25 November 2026 (each measure's mean of the
seven days), beside board.json's own week lines. Usage: week_check.py BOARD_JSON [BOARD_JSON ...]"""
import json
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

p = "warehouse/output/iso_trader_daily.csv"
t = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str)
days = [f"2026-11-{d}T00:00:00Z" for d in range(19, 26)]
want = [e for e in sorted(set(t["entity"])) if e.startswith("ercot:HB_")] + ["caiso:TH_ZP26_GEN-APND", "spp:SPPSOUTH_HUB"]
means = ["da_mean_usd", "da_onpeak_mean_usd", "da_offpeak_mean_usd", "da_rt_spread_mean_usd", "implied_heat_rate"]
mine = {}
for e in want:
    for v in means:
        held = t[(t["entity"] == e) & (t["variable"] == v)].sort_values("ts_utc")
        s = held.tail(7)   # the board's week_of: the last 7 days the measure is held
        if len(s) == 7 or (v == "da_onpeak_mean_usd" and len(s) >= 1):  # the board's rule (board_page.wmean)
            mine[(e.split(":", 1)[1], v)] = (round(s["value"].astype(float).mean(), 4), s["ts_utc"].max()[:10])
for path in sys.argv[1:]:
    b = json.load(open(path, encoding="utf-8"))
    week = {w["code"]: w for w in b.get("week", [])}
    same = diff = absent = 0
    print(f"== {path}: built {b.get('built')}")
    for (code, v), (m, end) in sorted(mine.items()):
        w = week.get(code, {}).get("means", {}).get(v)
        if w is None:
            absent += 1
            print(f"  {code} {v}: recomputed {m}; the file has no line")
        elif abs(w["v"] - m) <= 0.0001 and w.get("end") == end:
            same += 1
        else:
            diff += 1
            print(f"  {code} {v}: recomputed {m} (the 7 days to {end}); the file {w['v']} (to {w.get('end')})")
    print(f"  {same} equal, {diff} differ, {absent} absent, of {len(mine)} recomputed")
