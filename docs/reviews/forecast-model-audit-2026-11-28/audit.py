"""Session 11402 (chain 770, part B item 1): the /forecast audit, restated from the page's own files with none of the
builder's code. Read only. Writes JSON and text to the folder given (default: docs/reviews/forecast-model-audit-2026-11-28).

Vintages read with git show (no checkout):
  MAIN  the worktree's site/data/predict (origin/main f35d8245b): place files of the build made as at 18:00 UTC
        26 November (tables through 25 November), tomorrow taken from the ledger's making of 11:00 UTC 26 November.
  V1    0cdfd65ad: the first build, made 11:00 UTC 26 November (tables through 24 November).
  V3    15511cb2e: the data machine's daily run of 27 November (made 19:00 UTC, tables through 26 November), later
        put back by 993a5d99b.
"""
import json
import math
import os
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "predict")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "reviews", "forecast-model-audit-2026-11-28")
os.makedirs(OUT, exist_ok=True)
V1, V3 = "0cdfd65ad", "15511cb2e"


def load(name, commit=None):
    if commit is None:
        with open(os.path.join(D, name), encoding="utf-8") as f:
            return json.load(f)
    raw = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:site/data/predict/{name}"], capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))


def ledger(series="demand", commit=None):
    name = f"ledger_{series}.csv"
    if commit is None:
        with open(os.path.join(D, name), encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:site/data/predict/{name}"], capture_output=True, check=True).stdout.decode("utf-8").splitlines()
    lines = [x for x in lines if not x.startswith("#")]
    head = lines[0].split(",")
    return [dict(zip(head, x.split(","))) for x in lines[1:] if x]


def fl(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def r2(x, nd=2):
    return None if x is None else round(x, nd)


index = load("index.json")
places = [p["place"] for p in index["places"]]
scores = load("scores.json")
SC = scores["rows_columns"]
rows = [dict(zip(SC, r)) for r in scores["rows"]]
files = {p: load(f"{p}.json") for p in places}
res = {}

# ---- 1. data request 577: the tomorrow of each file against the ledger ----------------------------------------------
def against_ledger(fs, led, series):
    out = []
    by = defaultdict(list)
    for r in led:
        if r["series"] == series:
            by[(r["place"], r["target_day"])].append(r)
    for p, f in fs.items():
        s = f["series"][series]
        if s.get("status") != "shown" or not s.get("tomorrow"):
            continue
        L = by.get((p, s["target_day"]), [])
        cols = s["tomorrow_columns"]
        tm = {r[0]: r for r in s["tomorrow"]}
        diff_v = sum(1 for r in L if r["ts_utc"] in tm and fl(r["erw"]) != tm[r["ts_utc"]][cols.index("erw")])
        diff_b = sum(1 for r in L if r["ts_utc"] in tm and (fl(r["lo"]) != tm[r["ts_utc"]][cols.index("lo")] or fl(r["hi"]) != tm[r["ts_utc"]][cols.index("hi")]))
        out.append({"place": p, "target_day": s["target_day"], "ledger_rows": len(L), "file_hours": len(tm),
                    "values_differ": diff_v, "band_differs": diff_b,
                    "file_made": s.get("made_utc"), "ledger_made": L[0]["made_utc"] if L else None,
                    "file_method": s.get("method"), "ledger_method": L[0]["method"] if L else None,
                    "file_horizon": s.get("horizon_days"), "ledger_horizon": int(L[0]["horizon_days"]) if L else None,
                    "file_inputs_through": s.get("inputs_through_utc"), "ledger_inputs_through": L[0]["inputs_through_utc"] if L else None,
                    "ledger_empty_figures": sum(1 for r in L if fl(r["erw"]) is None)})
    return out


led_d, led_p = ledger("demand"), ledger("price")
a577 = {"main_demand": against_ledger(files, led_d, "demand"), "main_price": against_ledger(files, led_p, "price")}
files3 = {p: load(f"{p}.json", V3) for p in places}
a577["v3_demand"] = against_ledger(files3, led_d, "demand")
a577["v3_price"] = against_ledger(files3, led_p, "price")
summ577 = {}
for k, v in a577.items():
    summ577[k] = {"places": len(v), "values_differ_places": sum(1 for x in v if x["values_differ"]),
                  "band_differ_places": sum(1 for x in v if x["band_differs"]),
                  "no_ledger_rows": [x["place"] for x in v if not x["ledger_rows"]],
                  "made_differ": sum(1 for x in v if x["ledger_rows"] and x["file_made"] != x["ledger_made"]),
                  "method_differ": sum(1 for x in v if x["ledger_rows"] and x["file_method"] != x["ledger_method"]),
                  "horizon_differ": [(x["place"], x["file_horizon"], x["ledger_horizon"]) for x in v if x["ledger_rows"] and x["file_horizon"] != x["ledger_horizon"]],
                  "inputs_differ": sum(1 for x in v if x["ledger_rows"] and x["file_inputs_through"] != x["ledger_inputs_through"]),
                  "ledger_empty": [(x["place"], x["ledger_empty_figures"]) for x in v if x["ledger_empty_figures"]]}
res["request_577"] = summ577
res["request_577_rows"] = a577

# ---- 2. the default view (Texas, demand, newest past day, percent error), restated ----------------------------------
tex = files["region-tex"]["series"]["demand"]
tc = tex["tomorrow_columns"]
tm = tex["tomorrow"]
hi_row = max((r for r in tm if r[tc.index("erw")] is not None), key=lambda r: r[tc.index("erw")])
lo_row = min((r for r in tm if r[tc.index("erw")] is not None), key=lambda r: r[tc.index("erw")])
hc = tex["history_columns"]
H = [dict(zip(hc, r)) for r in tex["history"]]
full = sorted({h["local_day"] for h in H if h["erw"] is not None and h["actual"] is not None})
day = full[-1]
FOUR = ["erw", "operator", "yesterday", "week_ago"]
hd = [h for h in H if h["local_day"] == day]
ms = [m for m in FOUR if any(h[m] is not None for h in hd)]
used = [h for h in hd if h["actual"] is not None and all(h[m] is not None for m in ms)]
day_mae = {m: sum(abs(h[m] - h["actual"]) for h in used) / len(used) for m in ms}
res["default_view"] = {
    "target_day": tex["target_day"], "made_utc": tex["made_utc"], "horizon_days_in_file": tex["horizon_days"],
    "highest_hour": {"ts": hi_row[0], "local_hour": hi_row[1], "erw": hi_row[tc.index("erw")], "operator_same_hour": hi_row[tc.index("operator")]},
    "lowest_hour": {"ts": lo_row[0], "local_hour": lo_row[1], "erw": lo_row[tc.index("erw")]},
    "past_day": day, "past_day_hours": len(used), "past_day_mae_mw": {m: round(v, 1) for m, v in day_mae.items()},
    "past_day_mae_as_printed": {m: round(v) for m, v in day_mae.items()},
}

# last 30 days, restated from the history rows (the file's summary needs every scored method; history holds four)
def restate_30(s):
    Hs = [dict(zip(s["history_columns"], r)) for r in s["history"]]
    days = sorted({h["local_day"] for h in Hs if h["kind"] == "backtest"})
    last = s["summary"]["last_30_days"]["last_day"]
    import datetime as dt
    lastd = dt.date.fromisoformat(last)
    keep = [h for h in Hs if h["kind"] == "backtest" and (lastd - dt.date.fromisoformat(h["local_day"])).days < 30
            and h["actual"] is not None and all(h[m] is not None for m in FOUR)]
    out = {"hours": len(keep)}
    for m in FOUR:
        out[m] = round(mean(abs(h[m] - h["actual"]) for h in keep), 2) if keep else None
        out[m + "_mape"] = round(mean(abs(h[m] - h["actual"]) / h["actual"] for h in keep if h["actual"] > 0) * 100, 3) if keep else None
    return out


r30 = {}
for p, f in files.items():
    s = f["series"]["demand"]
    if s.get("status") != "shown":
        continue
    got = restate_30(s)
    want = s["summary"]["last_30_days"]
    r30[p] = {"restated": got, "file_hours": want["hours"], "file_mae": want["mae"], "file_mape": want["mape"],
              "max_abs_diff_mae": max(abs((got[m] or 0) - (want["mae"][m] or 0)) for m in FOUR),
              "max_abs_diff_mape": max(abs((got[m + "_mape"] or 0) - (want["mape"][m] or 0)) for m in FOUR)}
res["last_30_days_restated"] = {"places": len(r30), "hours_equal": sum(1 for v in r30.values() if v["restated"]["hours"] == v["file_hours"]),
                                "max_diff_mae": max(v["max_abs_diff_mae"] for v in r30.values()),
                                "max_diff_mape": max(v["max_abs_diff_mape"] for v in r30.values()),
                                "region-tex": r30["region-tex"]}

# the summary's backtest against scores.json's 'all' row; month and hour cuts adding up
def row(place, series, method, cut, key=""):
    for r in rows:
        if r["place"] == place and r["series"] == series and r["method"] == method and r["cut"] == cut and str(r["key"]) == key:
            return r
    return None


ident = {"backtest_eq_all": 0, "backtest_ne_all": [], "month_adds": 0, "month_off": [], "hour_adds": 0, "hour_off": []}
by_place = defaultdict(list)
for r in rows:
    by_place[(r["place"], r["series"])].append(r)
for p, f in files.items():
    s = f["series"]["demand"]
    if s.get("status") != "shown":
        continue
    g = by_place[(p, "demand")]
    allr = {r["method"]: r for r in g if r["cut"] == "all"}
    bt = s["summary"]["backtest"]
    if all(allr[m]["mae"] == bt["mae"][m] and allr[m]["hours"] == bt["hours"] for m in FOUR):
        ident["backtest_eq_all"] += 1
    else:
        ident["backtest_ne_all"].append(p)
    for cut, ref in (("month", "all"), ("hour", "last_2_years")):
        for m in ["erw", "operator"]:
            parts = [r for r in g if r["cut"] == cut and r["method"] == m and r["hours"]]
            n = sum(r["hours"] for r in parts)
            w = sum(r["hours"] * r["mae"] for r in parts) / n
            R = allr[m] if ref == "all" else next(r for r in g if r["cut"] == ref and r["method"] == m)
            ok = n == R["hours"] and abs(w - R["mae"]) < 0.01
            if ok:
                ident[cut + "_adds"] += 1
            else:
                ident[cut + "_off"].append((p, m, n, R["hours"], round(w, 3), R["mae"]))
res["identities"] = ident

# ---- 3. the band: coverage restated from the history rows, against the file's by-month figure -----------------------
band = {"places": 0, "nov_equal": 0, "nov_off": [], "pooled": None}
tot = {"in": 0, "below": 0, "above": 0, "n": 0}
per = []
for p, f in files.items():
    s = f["series"]["demand"]
    if s.get("status") != "shown":
        continue
    Hs = [dict(zip(s["history_columns"], r)) for r in s["history"]]
    x = [h for h in Hs if h["kind"] == "backtest" and h["actual"] is not None and h["lo"] is not None and h["hi"] is not None]
    nov = [h for h in x if h["local_day"].startswith("2026-11")]
    ins = sum(1 for h in nov if h["lo"] <= h["actual"] <= h["hi"])
    fm = {m[0]: m for m in s["band_coverage"]["by_month"]}.get("2026-11")
    band["places"] += 1
    mine = round(ins / len(nov) * 100, 1) if nov else None
    if fm and fm[1] == len(nov) and abs(fm[2] - mine) < 0.051:
        band["nov_equal"] += 1
    else:
        band["nov_off"].append((p, len(nov), mine, fm))
    b = sum(1 for h in x if h["actual"] < h["lo"])
    a = sum(1 for h in x if h["actual"] > h["hi"])
    tot["in"] += len(x) - a - b
    tot["below"] += b
    tot["above"] += a
    tot["n"] += len(x)
    bc = s["band_coverage"]
    per.append((p, bc["inside_pct"], bc["below_pct"], bc["above_pct"], bc["hours"]))
band["pooled_last_35_days"] = {k: (round(v / tot["n"] * 100, 1) if k != "n" else v) for k, v in tot.items()}
per.sort(key=lambda t: t[1])
band["two_years_by_place"] = per
band["two_years_places_below_80"] = sum(1 for t in per if t[1] < 80)
band["two_years_places_below_78"] = sum(1 for t in per if t[1] < 78)
band["two_years_weighted_inside"] = round(sum(t[1] * t[4] for t in per) / sum(t[4] for t in per), 2)
band["two_years_weighted_below"] = round(sum(t[2] * t[4] for t in per) / sum(t[4] for t in per), 2)
band["two_years_weighted_above"] = round(sum(t[3] * t[4] for t in per) / sum(t[4] for t in per), 2)
# by local hour: the hour with the lowest share at each place
band["worst_local_hour"] = sorted(((p, min((v, k) for k, v in enumerate(files[p]["series"]["demand"]["band_coverage"]["by_local_hour_inside_pct"]) if v is not None)) for p in places if files[p]["series"]["demand"].get("status") == "shown"), key=lambda t: t[1][0])[:8]
# by month: the months furthest under 80
months = []
for p in places:
    s = files[p]["series"]["demand"]
    if s.get("status") != "shown":
        continue
    for m in s["band_coverage"]["by_month"]:
        if m[1] >= 600:
            months.append((m[2], p, m[0], m[1]))
months.sort()
band["worst_months"] = months[:12]
band["months_under_70"] = sum(1 for m in months if m[0] < 70)
band["months_total"] = len(months)
# the price band
pb = []
for p in places:
    s = files[p]["series"]["price"]
    if s.get("status") == "shown":
        bc = s["band_coverage"]
        pb.append((p, bc["inside_pct"], bc["below_pct"], bc["above_pct"], bc["hours"]))
band["price"] = pb
# the band on the top ten days and the spike hours cannot be read from the files (the backtest is not in them)
res["band"] = band

# ---- 4. does each forecast beat its naive line: in the choice window and before it ----------------------------------
def before(allr, l2r):
    """MAE over the hours of 'all' that are not in 'last_2_years' (both on the same common hours)."""
    n = allr["hours"] - l2r["hours"]
    if n <= 0 or allr["mae"] is None or l2r["mae"] is None:
        return None, 0
    return (allr["mae"] * allr["hours"] - l2r["mae"] * l2r["hours"]) / n, n


naive = {"demand": [], "price": [], "peak": []}
for p in places:
    g = by_place[(p, "demand")]
    if not g:
        continue
    a = {r["method"]: r for r in g if r["cut"] == "all"}
    l = {r["method"]: r for r in g if r["cut"] == "last_2_years"}
    if "erw" not in a or a["erw"]["mae"] is None:
        continue
    pre = {m: before(a[m], l[m])[0] for m in ("erw", "operator", "yesterday", "week_ago")}
    npre = before(a["erw"], l["erw"])[1]
    naive["demand"].append({"place": p, "choice": files[p]["series"]["demand"]["method"],
                            "l2_erw": l["erw"]["mae"], "l2_yesterday": l["yesterday"]["mae"], "l2_week": l["week_ago"]["mae"], "l2_operator": l["operator"]["mae"],
                            "pre_hours": npre, "pre_erw": r2(pre["erw"]), "pre_yesterday": r2(pre["yesterday"]), "pre_week": r2(pre["week_ago"]), "pre_operator": r2(pre["operator"])})
    pk = files[p]["series"]["demand"].get("peak") or {}
    if pk.get("backtest") and pk.get("last_2_years"):
        B, L2 = pk["backtest"], pk["last_2_years"]
        n = B["days"] - L2["days"]
        def pre_pk(m, f="mae"):
            if n <= 0:
                return None
            return (B["methods"][m][f] * B["days"] - L2["methods"][m][f] * L2["days"]) / n
        naive["peak"].append({"place": p, "peak_method": pk.get("method"), "l2_days": L2["days"], "pre_days": n,
                              "l2_erw": L2["methods"]["erw"]["mae"], "l2_yesterday": L2["methods"]["yesterday"]["mae"], "l2_week": L2["methods"]["week_ago"]["mae"], "l2_operator": L2["methods"]["operator"]["mae"],
                              "pre_erw": r2(pre_pk("erw"), 1), "pre_yesterday": r2(pre_pk("yesterday"), 1), "pre_week": r2(pre_pk("week_ago"), 1), "pre_operator": r2(pre_pk("operator"), 1),
                              "l2_erw_mape": L2["methods"]["erw"]["mape"], "l2_yesterday_mape": L2["methods"]["yesterday"]["mape"],
                              "pre_erw_mape": r2(pre_pk("erw", "mape"), 3), "pre_yesterday_mape": r2(pre_pk("yesterday", "mape"), 3)})
for p in places:
    g = by_place[(p, "price")]
    a = {r["method"]: r for r in g if r["cut"] == "all"}
    l = {r["method"]: r for r in g if r["cut"] == "last_2_years"}
    if "erw" not in a or a["erw"]["mae"] is None:
        continue
    pre = {m: before(a[m], l[m]) for m in ("erw", "yesterday", "week_ago", "regression")}
    naive["price"].append({"place": p, "choice": files[p]["series"]["price"]["method"], "all_hours": a["erw"]["hours"],
                           "l2_erw": l["erw"]["mae"], "l2_yesterday": l["yesterday"]["mae"], "l2_week": l["week_ago"]["mae"], "l2_regression": l["regression"]["mae"],
                           "all_erw": a["erw"]["mae"], "all_yesterday": a["yesterday"]["mae"], "all_regression": a["regression"]["mae"],
                           "pre_hours": pre["erw"][1], "pre_erw": r2(pre["erw"][0]), "pre_yesterday": r2(pre["yesterday"][0]), "pre_regression": r2(pre["regression"][0])})
d = naive["demand"]
naive["demand_summary"] = {"places": len(d),
                           "l2_beats_yesterday": sum(1 for x in d if x["l2_erw"] < x["l2_yesterday"]),
                           "l2_beats_week": sum(1 for x in d if x["l2_erw"] < x["l2_week"]),
                           "pre_beats_yesterday": sum(1 for x in d if x["pre_erw"] is not None and x["pre_erw"] < x["pre_yesterday"]),
                           "pre_beats_week": sum(1 for x in d if x["pre_erw"] is not None and x["pre_erw"] < x["pre_week"]),
                           "l2_beats_operator": [x["place"] for x in d if x["l2_operator"] is not None and x["l2_erw"] < x["l2_operator"]],
                           "pre_beats_operator": [x["place"] for x in d if x["pre_operator"] is not None and x["pre_erw"] < x["pre_operator"]],
                           "pre_worst_ratio_to_yesterday": sorted(((round(x["pre_erw"] / x["pre_yesterday"], 3), x["place"]) for x in d if x["pre_erw"]), reverse=True)[:5]}
k = naive["peak"]
naive["peak_summary"] = {"places": len(k),
                         "l2_beats_yesterday": sum(1 for x in k if x["l2_erw"] < x["l2_yesterday"]),
                         "pre_beats_yesterday": sum(1 for x in k if x["pre_erw"] is not None and x["pre_erw"] < x["pre_yesterday"]),
                         "pre_loses_to_yesterday": [(x["place"], x["pre_erw"], x["pre_yesterday"], x["pre_days"]) for x in k if x["pre_erw"] is not None and x["pre_erw"] >= x["pre_yesterday"]],
                         "l2_beats_operator": [x["place"] for x in k if x["l2_erw"] < x["l2_operator"]],
                         "l2_peak_loses_to_yesterday_mape": [(x["place"], x["l2_erw_mape"], x["l2_yesterday_mape"]) for x in k if x["l2_erw_mape"] >= x["l2_yesterday_mape"]]}
res["naive"] = naive

# ---- 5. the days ahead --------------------------------------------------------------------------------------------
ah = load("ahead.json")
res["ahead_keys"] = list(ah.keys())
ahr = []
for pi, e in enumerate(ah.get("places", [])):
    for h in e.get("horizons", []):
        l2 = h.get("last_2_years") or {}
        ahr.append({"place": e.get("place"), "h": h.get("horizon_days"), "shown": h.get("shown"), "method": h.get("method"),
                    "keys": sorted(l2.keys()), "mae": l2.get("mae"), "hours": l2.get("hours"),
                    "op": l2.get("operator_day_ahead_mae_same_hours"), "cov": h.get("band_coverage_pct")})
res["ahead_sample"] = ahr[:6]
res["ahead_count"] = len(ahr)
res["ahead_shown"] = sum(1 for x in ahr if x["shown"])
bad = []
for x in ahr:
    m = x["mae"] or {}
    erw = m.get(x["method"]) if x["method"] else None
    wk = m.get("week_ago")
    if x["shown"] and (erw is None or wk is None or not erw < wk):
        bad.append(x)
res["ahead_shown_not_beating"] = bad
res["ahead_methods_in_scores"] = sorted({kk for x in ahr for kk in (x["mae"] or {}).keys()})
margins = sorted(((round(1 - x["mae"][x["method"]] / x["mae"]["week_ago"], 4), x["place"], x["h"]) for x in ahr if x["mae"] and x["method"] in x["mae"] and x["mae"].get("week_ago")))
res["ahead_smallest_margins"] = margins[:6]

with open(os.path.join(OUT, "audit_files.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps({k: res[k] for k in ("request_577", "default_view", "last_30_days_restated", "identities")}, indent=1, default=str)[:12000])
print(json.dumps({k: v for k, v in res["band"].items() if k != "two_years_by_place"}, default=str)[:4000])
print(json.dumps(res["naive"]["demand_summary"], default=str))
print(json.dumps(res["naive"]["peak_summary"], default=str))
print(json.dumps(res["naive"]["price"], default=str))
print(json.dumps({k: res[k] for k in ("ahead_keys", "ahead_sample", "ahead_count", "ahead_shown", "ahead_shown_not_beating", "ahead_methods_in_scores", "ahead_smallest_margins")}, default=str)[:4000])
