# Session 10215: more rules changed one at a time, on the page's own rows (runs/c10215/rows/energy_deals.json) with the
# page's own fold (site/data/deal_duplicates.json): the AI view's US-dollar sums by stage and with the register's
# doubtful pairs; the comparables' floor; a floor of "Sure"; the newest deal. Counts and sums only.
#   python runs/c10215/measures2.py <rows dir> <deal_duplicates.json> <out.json>
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

ROWS, DUPS, DEST = sys.argv[1:4]
rows = json.load(open(os.path.join(ROWS, "energy_deals.json"), encoding="utf-8"))
pairs = json.load(open(DUPS, encoding="utf-8"))["pairs"]
ids = {r["event_id"] for r in rows}
gone = {p["duplicate"] for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids}
deals = [r for r in rows if r["event_id"] not in gone]


def x(r, k):
    return (r["extra"] or {}).get(k, "")


def f(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def usd(r):
    return f(x(r, "dollars"))


ai = [r for r in deals if x(r, "ai_power").lower() == "true"]
M = {}
M["ai_usd_total"] = sum(usd(r) for r in ai if usd(r) is not None)
M["ai_usd_by_status"] = {k or "-": [sum(1 for r in ai if (r["status"] or "") == k and usd(r) is not None),
                                    sum(usd(r) for r in ai if (r["status"] or "") == k and usd(r) is not None)]
                         for k in sorted(set(r["status"] or "" for r in ai))}
M["ai_usd_largest5"] = sorted((usd(r) for r in ai if usd(r) is not None), reverse=True)[:5]
M["ai_usd_top5_share"] = round(100 * sum(M["ai_usd_largest5"]) / M["ai_usd_total"], 1)
by = {r["event_id"]: r for r in rows}
M["doubtful"] = []
for p in pairs:
    if p["ruling"] != "doubtful":
        continue
    a, b = by.get(p["duplicate"]), by.get(p["kept"])
    M["doubtful"].append({"ai": [x(a, "ai_power"), x(b, "ai_power")], "usd": [usd(a), usd(b)], "status": [a["status"], b["status"]]})
M["doubtful_ai_usd_smaller_sum"] = sum(min(v for v in d["usd"] if v is not None) for d in M["doubtful"]
                                       if all(s.lower() == "true" for s in d["ai"]) and all(v is not None for v in d["usd"]))
nonr = [r for r in ai if (r["status"] or "") not in ("rumored", "cancelled") and usd(r) is not None]
M["ai_usd_without_rumored_cancelled"] = [len(nonr), sum(usd(r) for r in nonr)]

# the comparables' floor: how many medians each floor leaves (by every dimension), and the default view's (type)
def dimv(r, dim):
    st = x(r, "state").upper()
    SG = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM",
          "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO", "OK": "SPP", "KS": "SPP", "NE": "SPP",
          "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE", "RI": "ISO-NE", "VT": "ISO-NE"}
    return {"type": x(r, "deal_type"), "technology": x(r, "technology"), "grid": SG.get(st, ""), "year": r["event_date"][:4]}[dim]


for floor in (3, 5, 10):
    out = {}
    for dim in ("type", "technology", "grid", "year"):
        g = defaultdict(list)
        for r in deals:
            if r["mw"] is not None:
                g[dimv(r, dim)].append(r["mw"])
        out[dim] = {k or "-": statistics.median(v) for k, v in g.items() if len(v) >= floor}
    M[f"medians_floor_{floor}"] = out
    M[f"medians_floor_{floor}_count"] = sum(len(v) for v in out.values())

# a floor of "Sure" at 0.7 (the Roundup's) and at 0.6 (the prompt's "doubtful" band)
for fl in (0.6, 0.7):
    keep = [r for r in deals if (f(x(r, "confidence")) or 0) >= fl]
    nov = [r for r in rows if r["event_date"][:7] == "2026-11" and (f(x(r, "confidence")) or 0) >= fl]
    M[f"sure_floor_{fl}"] = {"deals": len(keep), "with_mw": sum(1 for r in keep if r["mw"] is not None),
                             "mw": sum(r["mw"] for r in keep if r["mw"] is not None),
                             "ai": sum(1 for r in keep if x(r, "ai_power").lower() == "true"),
                             "nov_deals": len(nov), "nov_mw": sum(r["mw"] for r in nov if r["mw"] is not None),
                             "nov_ai_pct": round(100 * sum(1 for r in nov if x(r, "ai_power").lower() == "true") / len(nov)) if nov else None}

# one deal per row on the first tab: the register's folded pairs as two rows there, by month
M["first_tab_folded_dups_by_month"] = dict(Counter(by[d]["event_date"][:7] for d in gone))
M["newest"] = max(r["event_date"] for r in rows)[:10]
M["status_counts_all"] = dict(Counter(r["status"] or "-" for r in deals))
json.dump(M, open(DEST, "w", encoding="utf-8"), indent=1)
print(json.dumps(M, indent=1)[:6000])
