"""Session 10236: stand-in rows for the home strip's read of latest_prices, which this machine does not hold. For each
grid's main hub or zone (site/data/markets.json), the newest row of the main copy's iso_rtm_hub_prices (an hourly mean,
not the 15-minute interval the live table holds). Used only to draw the page; the strip is not restated from them.
Run from the worktree root: <venv python> runs/c10236/make_latest.py <main copy warehouse/output>"""
import csv
import io
import json
import os
import sys

OUT = sys.argv[1]
mk = json.load(open(os.path.join("site", "data", "markets.json"), encoding="utf-8"))
mains = {m["main"] for m in mk["isos"]}
best = {}
with open(os.path.join(OUT, "iso_rtm_hub_prices.csv"), encoding="utf-8") as f:
    body = "\n".join(ln for ln in f.read().splitlines() if not ln.startswith("#"))
for r in csv.DictReader(io.StringIO(body)):
    if r["entity"] in mains and (r["entity"] not in best or r["ts_utc"] > best[r["entity"]]["ts_utc"]):
        best[r["entity"]] = {k: r[k] for k in ("entity", "variable", "ts_utc", "value", "unit")}
rows = json.load(open(os.path.join("runs", "c10236", "home_rows.json"), encoding="utf-8"))
rows["latest"] = sorted(best.values(), key=lambda r: r["entity"])
json.dump(rows, open(os.path.join("runs", "c10236", "home_rows.json"), "w", encoding="utf-8"))
for r in rows["latest"]:
    print(r)
print("mains without a row:", sorted(mains - set(best)))
