# Session 10211: one rule of the datacenter tracker changed at a time, each measured on the same rows as the
# restatement (the warehouse's datacenter_facilities.csv of 25 November 2026) and the site's own price files. Standard
# library only; prints JSON. No row of the held table is printed, only sums and counts.
#   python runs/c10211/measures.py <warehouse output dir> <site dir>
import csv
import json
import math
import os
import re
import sys
from collections import Counter

OUT, SITE = sys.argv[1], sys.argv[2]
US = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC "
         "ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split())
STATE_GRID = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM",
              "WV": "PJM", "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO",
              "OK": "SPP", "KS": "SPP", "NE": "SPP", "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE", "RI": "ISO-NE", "VT": "ISO-NE"}
WRONG = "datacenter:868a5b4c04ff1f44"   # the join datacenter_facilities.md names ("The news extractor's merge rule")


def table(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader([ln for ln in f if not ln.startswith("#")]))


def mw(r):
    return float(r["capacity_mw"]) if r["capacity_mw"] else None


def counted(r):
    return r["state"] in US and r["status"].lower() not in ("withdrawn", "cancelled")


def grid(r):
    return r["grid"] or STATE_GRID.get(r["state"], "")


rows = table("datacenter_facilities")
cnt = [r for r in rows if counted(r)]
wm = [r for r in cnt if mw(r) is not None]
total = sum(mw(r) for r in wm)
M = {"base": {"mw_total": total, "n_with_mw": len(wm), "counted": len(cnt)}}

# 1. the known wrong join left out of every sum
w = [r for r in wm if r["entity_id"] != WRONG]
M["1_wrong_join_out"] = {"mw_total": sum(mw(r) for r in w), "change_pct": 100 * (sum(mw(r) for r in w) - total) / total,
                         "planned_mw": sum(mw(r) for r in w if r["status"] == "planned"),
                         "planned_mw_base": sum(mw(r) for r in wm if r["status"] == "planned"),
                         "row_in_table": any(r["entity_id"] == WRONG for r in rows)}

# 2. the views by operator read the operator, else the developer
def by(key, rs):
    d = {}
    for r in rs:
        k = key(r)
        if k:
            d[k] = d.get(k, 0.0) + mw(r)
    return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))


op5 = by(lambda r: r["operator"], wm)[:5]
dev5 = by(lambda r: r["operator"] or r["developer"], wm)[:5]
M["2_operator_else_developer"] = {
    "top5_operator_mw": sum(v for _, v in op5), "top5_operator_share_pct": 100 * sum(v for _, v in op5) / total,
    "no_operator_mw": sum(mw(r) for r in wm if not r["operator"]), "no_operator_n": sum(1 for r in wm if not r["operator"]),
    "no_operator_with_developer_mw": sum(mw(r) for r in wm if not r["operator"] and r["developer"]),
    "no_operator_with_developer_n": sum(1 for r in wm if not r["operator"] and r["developer"]),
    "top5_else_developer_mw": sum(v for _, v in dev5), "top5_else_developer_share_pct": 100 * sum(v for _, v in dev5) / total,
    "top_operator_mw": op5[0][1] if op5 else None, "top_else_developer_mw": dev5[0][1] if dev5 else None}

# 3. the timeline of the counted facilities only (as every other section counts)
def tl(rs):
    out = []
    for r in rs:
        y = r["energized_year"] or r["planned_year"]
        if re.match(r"^\d{4}-\d{2}", r["first_story_at"]) and y and int(float(y)) >= 2000:
            out.append((grid(r), r["first_story_at"][:4], int(float(y)) - int(r["first_story_at"][:4]), r))
    return out


def med(xs):
    if len(xs) < 3:
        return None
    s = sorted(xs)
    h = len(s) // 2
    return s[h] if len(s) % 2 else (s[h - 1] + s[h]) / 2


t_all, t_c = tl(rows), tl(cnt)
M["3_timeline_counted_only"] = {
    "rows_all": len(t_all), "rows_no_us_state": sum(1 for x in t_all if x[3]["state"] not in US),
    "rows_cancelled": sum(1 for x in t_all if x[3]["state"] in US and not counted(x[3])),
    "median_all": med([x[2] for x in t_all]), "rows_counted": len(t_c), "median_counted": med([x[2] for x in t_c]),
    "median_2026_all": med([x[2] for x in t_all if x[1] == "2026"]), "median_2026_counted": med([x[2] for x in t_c if x[1] == "2026"]),
    "rows_counted_without_wrong_join": sum(1 for x in t_c if x[3]["entity_id"] != WRONG)}

# 4. firm against speculative: the megawatts stated by the stage a source states
stage = Counter()
for r in wm:
    ps = r["project_status"] if r["status"] == "planned" else r["status"] or "no status"
    stage["planned: " + ps if r["status"] == "planned" else ps] += mw(r)
M["4_stage"] = {"mw_by_stage": dict(stage), "firm_mw": stage["under_construction"] + stage["operating"],
                "firm_share_pct": 100 * (stage["under_construction"] + stage["operating"]) / total,
                "top3_mw": sum(sorted((mw(r) for r in wm), reverse=True)[:3]),
                "top3_share_pct": 100 * sum(sorted((mw(r) for r in wm), reverse=True)[:3]) / total}
pjm = [r for r in wm if grid(r) == "PJM" and r["status"] in ("planned", "under_construction")]
M["4_stage"]["pjm_planned_building_mw"] = sum(mw(r) for r in pjm)
M["4_stage"]["pjm_planned_building_largest_row_mw"] = max((mw(r) for r in pjm), default=0)

# 5. IT load against grid draw: at the cost-of-power calculator's own overhead ratio (1.56), if a figure of unstated basis is IT load
unstated = sum(mw(r) for r in wm if r["mw_basis"] in ("unstated", ""))
M["5_basis"] = {"basis_counted": dict(Counter(r["mw_basis"] or "-" for r in wm)), "unstated_mw": unstated,
                "grid_draw_if_it_at_1_56": unstated * 1.56 + sum(mw(r) for r in wm if r["mw_basis"] not in ("unstated", "")),
                "added_mw_if_it": unstated * 0.56, "added_pct_of_total": 100 * unstated * 0.56 / total}

# 6. the news window: the facilities' first stories by month, and the counted ones
months = Counter(r["first_story_at"][:7] for r in rows if r["first_story_at"])
M["6_news_window"] = {"by_month": dict(sorted(months.items())), "n": sum(months.values()),
                      "since_2026_09": sum(v for k, v in months.items() if k >= "2026-09"),
                      "before_2026_09": sum(v for k, v in months.items() if k < "2026-09"),
                      "mw_rows_first_since_2026_09": sum(1 for r in rows if r["capacity_mw"] and r["first_story_at"][:7] >= "2026-09"),
                      "mw_rows_with_story": sum(1 for r in rows if r["capacity_mw"] and r["first_story_at"])}

# 7. the by-grid price cell: cheapest and dearest ERCOT load zone, each in its own market, against one market for all
D = os.path.join(SITE, "data", "datacenter")
IDX = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def monthly(region, buy):
    gi = IDX["grids"]["ercot"]
    out = []
    for y in range(min(gi["years"]), max(gi["years"]) + 1):
        p = os.path.join(D, f"ercot_{y}.json")
        if not os.path.exists(p):
            continue
        f = json.load(open(p, encoding="utf-8"))
        s = f["regions"].get(region, {}).get(buy)
        if not s:
            continue
        pr = [None] * f["hours"]
        for i, v in enumerate(s["v"]):
            pr[s["s"] + i] = v
        st = 0
        for m in range(12):
            n = 24 * (DAYS[m] + (1 if m == 1 and leap(y) else 0))
            vals = [v for v in pr[st:st + n] if v is not None]
            st += n
            if vals:
                out.append(dict(m=f"{y}-{m + 1:02d}", held=len(vals), total=sum(vals), complete=len(vals) >= 0.95 * n))
    return out


def per_window(ms, frm, to):
    w = [x for x in ms if frm <= x["m"] <= to]
    return (sum(x["total"] for x in w) / sum(x["held"] for x in w), sum(1 for x in w if x["complete"]), len(w)) if w else None


zones = {}
for reg in IDX["grids"]["ercot"]["regions"]:
    if reg.get("kind", "") not in ("", "zone"):
        continue
    rt, da = monthly(reg["id"], "rt"), monthly(reg["id"], "da")
    zones[reg["id"]] = {"rt": per_window(rt, "2025-11", "2026-10"), "da": per_window(da, "2025-11", "2026-10"),
                        "rt_complete_months_held": sum(1 for x in rt if x["complete"]), "rt_last_month": rt[-1]["m"] if rt else None}
M["7_price_markets"] = zones

# 8. ERCOT: observed running at one moment against each load's own peak, the newest report with all three
ll = table("ercot_large_load_status")
rep = {}
for r in ll:
    rep.setdefault(r["ts_utc"][:10], {})[r["variable"]] = float(r["value"])
full = sorted(d for d, v in rep.items() if {"approved_to_energize_mw", "observed_nonsimultaneous_peak_mw", "observed_simultaneous_peak_mw"} <= set(v))
last = rep[full[-1]]
M["8_ercot"] = {"day": full[-1], "approved": last["approved_to_energize_mw"],
                "share_nonsimultaneous_pct": 100 * last["observed_nonsimultaneous_peak_mw"] / last["approved_to_energize_mw"],
                "share_simultaneous_pct": 100 * last["observed_simultaneous_peak_mw"] / last["approved_to_energize_mw"],
                "tracker_texas_mw": sum(mw(r) for r in rows if r["state"] == "TX" and mw(r) is not None),
                "tracker_texas_share_of_approved_pct": 100 * sum(mw(r) for r in rows if r["state"] == "TX" and mw(r) is not None) / last["approved_to_energize_mw"],
                "new_submissions_mw": next((v["new_submissions_mw"] for v in rep.values() if "new_submissions_mw" in v), None)}

# 9. the charts and the list: what the dated chart leaves out (operator and queue rows carry no first story)
ahead = [r for r in cnt if r["status"] in ("planned", "under_construction")]
M["9_chart_scope"] = {"counted_planned_or_building": len(ahead), "of_them_with_first_story": sum(1 for r in ahead if r["first_story_at"]),
                      "operator_rows_planned": sum(1 for r in ahead if r["kind"] == "operator")}
print(json.dumps(M, indent=1, sort_keys=True, default=str))
