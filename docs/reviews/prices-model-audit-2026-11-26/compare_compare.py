"""Session 10218: the restatement (restate_compare.json) against site/data/price_compare.json, figure by figure.

    python compare_compare.py <site dir> <restate json>
"""
import json
import os
import sys

SITE, RJ = sys.argv[1], sys.argv[2]
f = json.load(open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8"))
r = json.load(open(RJ, encoding="utf-8"))
NUM2 = ["avg_price", "negative_hours_share_pct", "above_200_hours_share_pct", "day_spread_top4_bottom4", "daily_spread_mean_top4_bottom4"]
INTS = ["hours_held", "hours_in_window", "daily_spread_days"]
tot = same = 0
gaps = []
for w in ("year", "month"):
    mine = r["rows"][w]
    fe = {x["entity"] for x in f[w]}
    for e in sorted(set(mine) - fe):
        gaps.append(f"{w} {e}: restated, not in the file")
    for row in f[w]:
        e = row["entity"]
        m = mine.get(e)
        if m is None:
            gaps.append(f"{w} {e}: in the file, not restated")
            continue
        for side in ("dam", "rtm"):
            if (f"{side}_avg_price" in row) != (f"{side}_avg_price" in m):
                gaps.append(f"{w} {e} {side}: written in one only (file {f'{side}_avg_price' in row}, restated {f'{side}_avg_price' in m})")
                continue
            if f"{side}_avg_price" not in row:
                continue
            for k in NUM2:
                tot += 1
                a, b = row.get(f"{side}_{k}"), m.get(f"{side}_{k}")
                bb = None if b is None else round(b, 2)
                if a == bb:
                    same += 1
                else:
                    gaps.append(f"{w} {e} {side}_{k}: file {a}, restated {bb} (unrounded {b})")
            for k in INTS + ["basis"]:
                tot += 1
                a, b = row.get(f"{side}_{k}"), m.get(f"{side}_{k}")
                if a == b:
                    same += 1
                else:
                    gaps.append(f"{w} {e} {side}_{k}: file {a}, restated {b}")
        for k in ("grid_carbon_days_held", "grid_carbon_days_due"):
            tot += 1
            if row.get(k) == m.get(k):
                same += 1
            else:
                gaps.append(f"{w} {e} {k}: file {row.get(k)}, restated {m.get(k)}")
        tot += 1
        a, b = row.get("grid_carbon_intensity"), m.get("grid_carbon_intensity")
        if a == (None if b is None else round(b, 2)):
            same += 1
        else:
            gaps.append(f"{w} {e} grid_carbon_intensity: file {a}, restated {None if b is None else round(b, 2)}")
print(f"figures compared {tot}, equal {same}, differ {tot - same}")
for g in gaps:
    print("  ", g)
