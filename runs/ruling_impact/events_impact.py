#!/usr/bin/env python3
"""ERW, ruling impact for /events (session 7579, 17 November 2026).

The seven lines marked "Changes a figure" under /events in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The pages' rules and the event-study regression are replication/events/replicate.py (imported:
Rows, series_study, grid_weather, the windows). Rows: replication/events/window_rows.csv (event_window_daily's public
rows; the rows of ISO-NE, MISO and NYISO are held and not read), noaa_grid_weather_daily and
ercot_all_hub_prices_history (warehouse/output), and the figures the pages draw (replication/events/page_figures.json).

    .venv/Scripts/python.exe runs/ruling_impact/events_impact.py
"""
import collections
import csv
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE_REP = os.path.join(ROOT, "replication", "events")
spec = importlib.util.spec_from_file_location("rep", os.path.join(HERE_REP, "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
OUT = os.path.join(ROOT, "warehouse", "output")
raw, stamp = rep.read_csv(os.path.join(HERE_REP, "window_rows.csv"))
hold = rep.Hold()
raw = [r for r in raw if not hold.row(rep.T, r["entity"])]
rows = rep.Rows(raw)
fig = json.load(open(os.path.join(HERE_REP, "page_figures.json"), encoding="utf-8"))
HELD = ("ISNE", "MISO", "NYIS")

# ---- line 1: the EIA-930 figures drawn "license needed"
print("== line 1: the figures of the ten pages by what the hold does to them")
c = collections.Counter()
for page, v in fig["pages"].items():
    for f in v["figures"]:
        k = f["check"].split("|")
        ent = k[2] if k[0] == "series" else k[2]
        head, code = (ent.split(":") + [""])[:2]
        if head == "eia930":
            c["eia930, a held grid (ISO-NE, MISO, NYISO)" if code in HELD else "eia930, a grid that does not decide (CAISO, ERCOT, PJM, SPP, Lower 48)"] += 1
        else:
            c[f"{head}: (a market's own price)"] += 1
    c["held figures counted by the page file"] += v.get("heldFigures", 0)
n = sum(v for k, v in c.items() if not k.startswith("held figures"))
for k, v in c.most_common():
    print(f"   {k}: {v}")
print(f"of the {n} figures in the replication's file (the rulings file counts 1,127 event numbers, 1,117 drawn 'license needed'): "
      f"(a) EIA-930's entities named to their grids: {c['eia930, a held grid (ISO-NE, MISO, NYISO)']} stay held, "
      f"{c['eia930, a grid that does not decide (CAISO, ERCOT, PJM, SPP, Lower 48)']} are drawn; (b) rows of no grid: every EIA-930 figure is drawn, the three held grids' too; (c) as now")
caiso = next(f for f in fig["pages"]["index"]["figures"] if "CISO|demand_max_mw|2022-09-06" in f["check"])
print(f"   e.g. the index card's CAISO peak {caiso['shown']} MW (2022-09-06), drawn on /demand and /grid/caiso, blank here and on /learn/problems under (c)")

# ---- line 2: Elliott, SPP's peak beside FERC's
print("\n== line 2: the Elliott page: SPP's highest hour as EIA-930 holds it, beside FERC's published all-time winter peak")
spp = rows.pick("elliott_2022", "eia930:SWPP", "demand_max_mw", "max", lambda d: d.startswith("2022-12"))
print(f"EIA-930 SWPP highest hour in the window: {spp['value']:,.0f} MW on {spp['d']}; FERC and NERC's report on Winter Storm Elliott (October 2023): 47,157 MW; "
      f"difference {47157 - spp['value']:+,.0f} MW ({(47157 / spp['value'] - 1) * 100:+.2f} percent)")

# ---- line 3: a temperature version for the three newest events from noaa_grid_weather_daily
print("\n== line 3: the three newest events, PJM (each page's primary grid), ERCOT and SPP: the estimate without temperature (as now) and with it")
W = collections.defaultdict(dict)
with open(os.path.join(OUT, "noaa_grid_weather_daily.csv"), encoding="utf-8", newline="") as f:
    for r in csv.DictReader(l for l in f if not l.startswith("#")):
        if r["variable"] in ("heating_degree_days", "cooling_degree_days"):
            W[r["ba"]].setdefault(r["ts_utc"][:10], {})[r["variable"]] = float(r["value"])
for ev in ("cold_2025", "east_heat_2025", "cold_2026"):
    for ent in ("eia930:PJM", "eia930:ERCO", "eia930:SWPP"):
        ba = ent.split(":")[1].lower()
        wx = {d: (v["heating_degree_days"], v["cooling_degree_days"]) for d, v in W[ba].items() if len(v) == 2}
        if not rows.of(ev, ent, "demand_mwh"):
            continue
        s = rep.series_study(rows, ev, ent, "demand_mwh")
        t = rep.series_study(rows, ev, ent, "demand_mwh", wx)
        share = (1 - t["est"] / s["est"]) * 100 if s["est"] and (t["est"] / s["est"]) > 0 and abs(t["est"]) <= abs(s["est"]) else None
        print(f"{ev} {ent}: pooled effect {s['est']:,.0f} MWh a day ({s['est'] / s['cf'] * 100:+.2f} percent of the counterfactual) -> with temperature {t['est']:,.0f} "
              f"[{t['lo']:,.0f}, {t['hi']:,.0f}] on {t['n']} days; weather share {('%.1f percent' % share) if share is not None else 'not drawn (sign or size rule)'}")
print("the six older events' temperature version reads station rows of event_window_daily; these read the grid's mean of NOAA ISD-Lite stations (noaa_grid_weather_daily, base 65 F), "
      "the station set of that table, not the event table's: a like method, not the same rows")

# ---- line 4: Uri, ERCOT's offer cap
print("\n== line 4: Uri: the hub price near USD 9,000 per MWh (the reason, ERCOT's offer cap, is not in a table)")
n = 0
days = collections.Counter()
with open(os.path.join(OUT, "ercot_all_hub_prices_history.csv"), encoding="utf-8") as f:
    for line in f:
        if "HB_HUBAVG" not in line or ",2021-02-" not in line:
            continue
        p = line.split(",")
        if p[1] != "spp_rtm":
            continue
        v = float(p[3])
        if v >= 8900:
            n += 1
            days[p[2][:10]] += 1
print(f"HB_HUBAVG 15-minute intervals at or above USD 8,900 in February 2021: {n} ({n / 4:.0f} hours), by UTC day {dict(sorted(days.items()))}")
print("the sentence on the cap (USD 9,000, the PUCT's order of 15 February 2021) needs that document read: not held, so the words are not computed here")

# ---- line 5: September 2022 heat, each airport's hottest day
print("\n== line 5: the September 2022 California heat page: each airport's hottest day in the window, from rows held")
lo, hi = rep.WINDOWS["caiso_heat_2022"]
for st in ("noaa:SAC", "noaa:LAX"):
    b = rows.pick("caiso_heat_2022", st, "temp_max_f", "max", lambda d: lo <= d <= hi)
    print(f"{st}: {b['value']:.2f} F on {b['d']}")

# ---- line 6: ERCOT's Elliott peak
print("\n== line 6: Elliott: ERCOT's highest hour set against ERCOT's own release")
e = rows.pick("elliott_2022", "eia930:ERCO", "demand_max_mw", "max", lambda d: d.startswith("2022-12"))
print(f"EIA-930 ERCO highest hour: {e['value']:,.0f} MW on {e['d']}. ERCOT's release of that week is not held (its robots file and terms are to be read first): the cross-check row is not computed")

# ---- line 7: Elliott, PJM's daily estimates with temperature
print("\n== line 7: Elliott, PJM's estimate for each day, without temperature (as now) and with it (the event table's own station rows)")
w = rep.grid_weather(rows, "elliott_2022", "pjm")
s = rep.series_study(rows, "elliott_2022", "eia930:PJM", "demand_mwh")
t = rep.series_study(rows, "elliott_2022", "eia930:PJM", "demand_mwh", w)
tw = {d["day"]: d for d in t["days"]}
for d in s["days"]:
    x = tw.get(d["day"])
    print(f"{d['day']}: {d['est']:,.0f} MWh -> {x['est']:,.0f} MWh ({x['est'] - d['est']:+,.0f}; weather {(1 - x['est'] / d['est']) * 100:.1f} percent of the day's effect)" if x else f"{d['day']}: {d['est']:,.0f} -> no weather row")
print(f"pooled: {s['est']:,.0f} -> {t['est']:,.0f} MWh a day; weather share {(1 - t['est'] / s['est']) * 100:.2f} percent (the page's 65.33)")
