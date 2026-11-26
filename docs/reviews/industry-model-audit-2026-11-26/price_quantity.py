"""Session 10224: the quantity the State Energy Data System's industrial average price is per (expenditures over price),
against the total and the end use, every state and the nation, 2024 and 2019. Reads site/data/industry.json."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
S = json.load(open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8"))["states_annual"]
yrs = [int(y) for y in S["years"]]
for y in (2024, 2019):
    i = yrs.index(y)
    rows = []
    for st, d in S["states"].items():
        p, x = d["price_usd_per_mmbtu"][i], d["expenditures_usd"]["total"][i]
        if not p or x is None:
            continue
        q = x / p / 1e6
        rows.append((st, q / d["consumption_tbtu"]["total"][i], q / d["consumption_tbtu"]["end_use_total"][i]))
    below = [r for r in rows if r[2] < 0.99]
    print(f"{y}: rows {len(rows)}; quantity below the total in {sum(r[1] < 1 for r in rows)}; at or above 99 percent of end use: {[(r[0], round(100 * r[2], 1)) for r in rows if r[2] >= 0.99]}; below 99 percent of end use: {len(below)}")
