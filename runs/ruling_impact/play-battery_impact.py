#!/usr/bin/env python3
"""ERW, ruling impact for /play/battery (session 7583, 17 November 2026).

The four lines marked "Changes a figure" under the home battery game in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads). The game's rules are replication/battery_game/replicate.py of branch wip/7535-play-battery
(copied unchanged to runs/ruling_impact/battery_game/ and imported: rules, play, best_score, emergency); the days are
site/data/battery_levels.json (the frozen famous days); ERCOT's demand on 10 August 2023 from
replication/events/window_rows.csv (event_window_daily, EIA-930).

    .venv/Scripts/python.exe runs/ruling_impact/play-battery_impact.py
"""
import csv
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("game", os.path.join(ROOT, "runs", "ruling_impact", "battery_game", "replicate.py"))
game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)
LV = json.load(open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8"))["levels"]
LV = LV if isinstance(LV, list) else list(LV.values())
SET = {"kwh": 13.5, "kw": 5, "rte": 0.9, "reserve": 0.25, "deg": 0.11}     # the game's settings (cases.json)


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


print("days: " + ", ".join(f"{l['slug']} ({l['date']})" for l in LV))

# ---- line 1: the score net of the starting charge
print("\n== line 1: the perfect battery's score as the game counts it (default) or net of the half-full start valued at the day's first price (Normal)")
for l in LV:
    R = game.rules(SET, "normal", [])
    best = game.best_score(l, R)
    start_val = R["start"] * l["price"][0] / 1000
    print(f"{l['slug']}: perfect {best:,.2f} USD; the starting {R['start']} kWh at the first price {l['price'][0]:,.2f} USD/MWh is worth {start_val:,.2f}; net {best - start_val:,.2f} ({pct(best, best - start_val)})")

# ---- line 2: the battery's duration
print("\n== line 2: the game's battery (13.5 kWh and 5 kW, 2.7 hours; default) or one of the battery page's durations at the same 5 kW")
for l in LV:
    R0 = game.rules(SET, "normal", [])
    b0 = game.best_score(l, R0)
    parts = []
    for h in (2, 4, 8):
        R = game.rules(dict(SET, kwh=5 * h), "normal", [])
        b = game.best_score(l, R)
        parts.append(f"{h} h ({5 * h} kWh) {b:,.2f} ({pct(b0, b)})")
    print(f"{l['slug']}: 2.7 h {b0:,.2f}; " + "; ".join(parts))

# ---- line 3: 10 August 2023, ERCOT's demand record of 2023
print("\n== line 3: the August 2023 day's line: ERCOT's demand that day")
best = None
with open(os.path.join(ROOT, "replication", "events", "window_rows.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["entity"] == "eia930:ERCO" and r["variable"] == "demand_max_mw" and r["event"] == "ercot_heat_2023" and r["ts_utc"].startswith("2023-08"):
            v = float(r["value"])
            if best is None or v > best[1]:
                best = (r["ts_utc"][:10], v)
print(f"EIA-930's highest ERCOT hour in August 2023: {best[1]:,.0f} MW on {best[0]}; Potomac Economics' 2023 State of the Market Report: 85.7 GW, ERCOT's record of 2023 "
      f"(difference {85700 - best[1]:+,.0f} MW, {(85700 / best[1] - 1) * 100:+.2f} percent)")

# ---- line 4: the value of lost load beside ERCOT's
print("\n== line 4: the game's lights-out charge at USD 35,000 per MWh (default, the PUCT's value of lost load) beside ERCOT's shortage-pricing value, USD 5,000 since 1 January 2022")
need = game.HOUSE_KW * game.OUTAGE_INTERVALS * game.MIN / 60
print(f"a lights out on Hard charges the outage's unserved energy, at most {need:.1f} kWh (1.5 kW for two hours, less the roof): USD {need * 35:,.2f} at 35,000 against {need * 5:,.2f} at 5,000 (-85.7 percent). "
      "The ruling is one sentence: no figure that stands moves")
