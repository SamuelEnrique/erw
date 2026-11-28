"""Session 11402: one choice changed at a time, where the page's files allow (no table of the warehouse is read).
Prints and writes choices.json."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "predict")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out")


def load(n):
    with open(os.path.join(D, n), encoding="utf-8") as f:
        return json.load(f)


idx = load("index.json")
places = [p["place"] for p in idx["places"]]
sc = load("scores.json")
C = sc["rows_columns"]
rows = [dict(zip(C, r)) for r in sc["rows"]]
R = {}
for r in rows:
    R[(r["place"], r["series"], r["method"], r["cut"], str(r["key"]))] = r
files = {p: load(f"{p}.json") for p in places}
ahead = {e["place"]: e for e in load("ahead.json")["places"]}
out = {}


def pre(place, series, m):
    a, l = R.get((place, series, m, "all", "")), R.get((place, series, m, "last_2_years", ""))
    if not a or not l or a["mae"] is None or l["mae"] is None or a["hours"] <= l["hours"]:
        return None
    return (a["mae"] * a["hours"] - l["mae"] * l["hours"]) / (a["hours"] - l["hours"])


# 1. the same hours for every method: within each (place, series, cut, key) every method's count is one number
groups = {}
for r in rows:
    if r["held"]:
        continue
    groups.setdefault((r["place"], r["series"], r["cut"], str(r["key"])), set()).add(r["hours"])
out["same_hours_groups"] = len(groups)
out["same_hours_groups_unequal"] = [k for k, v in groups.items() if len(v) > 1][:10]

# 2. regression_recent (added after looking at the last two years) against the regression, before the window too
rr = []
for p in places:
    l2r, l2rr = R.get((p, "demand", "regression", "last_2_years", "")), R.get((p, "demand", "regression_recent", "last_2_years", ""))
    if not l2r:
        continue
    rr.append((p, l2r["mae"], l2rr["mae"], round(pre(p, "demand", "regression"), 2), round(pre(p, "demand", "regression_recent"), 2)))
out["recent_vs_regression"] = {"places": len(rr), "l2_recent_better": sum(1 for x in rr if x[2] < x[1]),
                               "pre_recent_better": sum(1 for x in rr if x[4] < x[3]),
                               "pre_recent_worse": [x for x in rr if x[4] >= x[3]]}

# 3. reading one day older: the day-ahead error (h = 2, the place file) against h = 3 (ahead.json), last two years, MAE
hz = []
for p in places:
    e = ahead.get(p)
    if not e:
        continue
    h3 = next((h for h in e["horizons"] if h["horizon_days"] == 3), None)
    h7 = next((h for h in e["horizons"] if h["horizon_days"] == 7), None)
    l2 = R.get((p, "demand", "erw", "last_2_years", ""))
    if h3 and l2:
        hz.append((p, l2["mae"], h3["last_2_years"]["mae"][h3["method"]], h7["last_2_years"]["mae"][h7["method"]], h3["last_2_years"]["mae"]["week_ago"],
                   h3["last_2_years"]["mae"]["yesterday"]))
out["horizon"] = {"places": len(hz), "median_pct_h2_to_h3": sorted(round((x[2] / x[1] - 1) * 100, 1) for x in hz)[len(hz) // 2],
                  "tex": [x for x in hz if x[0] == "region-tex"],
                  "h3_not_beating_latest_day": [x for x in hz if not x[2] < x[5]]}
# every horizon against the latest day held (the file's `yesterday` at that horizon) as well as the week-ago hour
lat = []
for p, e in ahead.items():
    for h in e["horizons"]:
        m = h["last_2_years"]["mae"]
        if h["shown"] and not m[h["method"]] < min(m["week_ago"], m["yesterday"]):
            lat.append((p, h["horizon_days"], m[h["method"]], m["week_ago"], m["yesterday"]))
out["ahead_shown_not_beating_either_naive"] = lat

# 4. the weather known (not a forecast): what a perfect temperature forecast would be worth, last two years, MAPE
wk = []
for p in places:
    w = files[p]["series"]["demand"].get("with_weather_known")
    if w and w.get("last_2_years"):
        m = w["last_2_years"]["mape"]
        wk.append((p, m["regression"], m["with_weather_known"], m["operator"]))
out["weather_known"] = {"places": len(wk), "median_cut_pct": sorted(round((1 - x[2] / x[1]) * 100, 1) for x in wk)[len(wk) // 2],
                        "tex": [x for x in wk if x[0] == "region-tex"], "beats_operator": sum(1 for x in wk if x[2] < x[3])}

# 5. the choice window: choose on the whole backtest instead of the last two years
cw = []
for p in places:
    for series, cands in (("demand", ["yesterday", "week_ago", "regression", "regression_recent"]), ("price", ["yesterday", "week_ago", "regression"])):
        l2 = {m: R.get((p, series, m, "last_2_years", "")) for m in cands}
        al = {m: R.get((p, series, m, "all", "")) for m in cands}
        if not all(l2.values()) or any(v["mae"] is None for v in l2.values()):
            continue
        now = min(cands, key=lambda m: (l2[m]["mae"], m))
        whole = min(cands, key=lambda m: (al[m]["mae"], m))
        if now != whole:
            cw.append({"place": p, "series": series, "chosen_now": now, "chosen_on_whole": whole,
                       "l2_now": l2[now]["mae"], "l2_whole": l2[whole]["mae"], "all_now": al[now]["mae"], "all_whole": al[whole]["mae"]})
# the peak
for p in places:
    pk = files[p]["series"]["demand"].get("peak") or {}
    B, L2 = pk.get("backtest"), pk.get("last_2_years")
    if not B or not L2:
        continue
    cands = ["yesterday", "week_ago", "regression", "regression_recent"]
    now = pk.get("method")
    whole = min(cands, key=lambda m: (B["methods"][m]["mae"], m))
    if now != whole:
        cw.append({"place": p, "series": "demand_peak", "chosen_now": now, "chosen_on_whole": whole,
                   "l2_now": L2["methods"][now]["mae"], "l2_whole": L2["methods"][whole]["mae"], "all_now": B["methods"][now]["mae"], "all_whole": B["methods"][whole]["mae"],
                   "l2_now_mape": L2["methods"][now]["mape"], "l2_whole_mape": L2["methods"][whole]["mape"], "all_now_mape": B["methods"][now]["mape"], "all_whole_mape": B["methods"][whole]["mape"]})
out["choice_window"] = cw

# 6. the filing check: the operator on every month against the sound months, last two years, MAPE (Texas and pooled)
fs = []
for p in places:
    of = files[p]["series"]["demand"].get("operator_filing")
    l2 = R.get((p, "demand", "operator", "last_2_years", ""))
    l2e = R.get((p, "demand", "erw", "last_2_years", ""))
    if of and l2 and of.get("sound_last_2_years") and of["sound_last_2_years"]["hours"]:
        s = of["sound_last_2_years"]
        fs.append((p, l2e["mape"], l2["mape"], s["mape"]["erw"], s["mape"]["operator"], s["hours"]))
out["filing"] = {"places_with_sound_hours": len(fs), "erw_ahead_all_months": sum(1 for x in fs if x[1] < x[2]), "erw_ahead_sound_months": sum(1 for x in fs if x[3] < x[4])}

# 7. the peak chosen by its own error against the peak of the hourly choice, last two years
pc = []
for p in places:
    s = files[p]["series"]["demand"]
    pk = s.get("peak") or {}
    L2 = pk.get("last_2_years")
    if not L2:
        continue
    hourly = max(s["method_mae_last_2_years"], key=lambda m: -s["method_mae_last_2_years"][m] if s["method_mae_last_2_years"][m] is not None else -1e18)
    hourly = min((v, m) for m, v in s["method_mae_last_2_years"].items() if v is not None)[1]
    if hourly != pk.get("method"):
        pc.append((p, hourly, pk.get("method"), L2["methods"][hourly]["mape"], L2["methods"][pk["method"]]["mape"]))
out["peak_own_choice"] = {"places_differ": len(pc), "rows": pc}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "choices.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1)[:9000])
