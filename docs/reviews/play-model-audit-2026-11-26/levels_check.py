"""Session 10227: the famous ERCOT days' frozen prices (site/data/battery_levels.json) against the history's own rows
(extract.json, from the main copy's ercot_all_hub_prices_history)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
lv = json.load(open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8"))["levels"]
ex = json.load(open(os.path.join(HERE, "extract.json")))
for L in lv:
    rows = ex["famous_ercot"].get(L["date"], {}).get("ercot:HB_HUBAVG|spp_rtm")
    if not rows:
        print(L["slug"], L["date"], "not in the history extract")
        continue
    rows = sorted(rows)
    same_ts = [r[0] for r in rows] == L["ts_utc"]
    diff = max(abs(a[1] - b) for a, b in zip(rows, L["price"])) if same_ts else None
    print(L["slug"], L["date"], "intervals", len(rows), len(L["price"]), "same times", same_ts, "largest price difference", diff)
