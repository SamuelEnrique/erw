# Session 10215: one rule at a time, and each claim of the deal pages measured, on the warehouse's CSVs on disk. Counts
# and sums only: no outlet text is printed (the evidence table is internal; only counts of its words are taken).
#   python runs/c10215/measures.py <warehouse output dir> <duplicates.csv> <deals checked.csv> <out.json>
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date

OUT, DUPS, CHECKED, DEST = sys.argv[1:5]
csv.field_size_limit(10 ** 9)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


def num(v):
    v = (v or "").strip()
    try:
        return float(v) if v else None
    except ValueError:
        return None


deals = rows(os.path.join(OUT, "energy_deals.csv"))
ev = rows(os.path.join(OUT, "energy_deals_evidence.csv"))
pairs = rows(DUPS)
M = {}

# --- the table and the folded set (the register's fold pairs both held)
ids = {r["event_id"] for r in deals}
gone = {p["duplicate_event_id"] for p in pairs if p["ruling"] == "fold" and p["duplicate_event_id"] in ids and p["kept_event_id"] in ids}
folded = [r for r in deals if r["event_id"] not in gone]
M["rows"], M["folded_deals"] = len(deals), len(folded)

# 1. the first tab's lead: "Energy deals reported in the news since 2025-10-01"
M["rows_dated_before_2025_10_01"] = sum(1 for r in deals if r["event_date"][:10] < "2025-10-01")
M["first_date"], M["last_date"] = min(r["event_date"] for r in deals)[:10], max(r["event_date"] for r in deals)[:10]
M["date_basis"] = dict(Counter(r.get("date_basis", "") for r in deals))

# 2. the month cell: November 2026 so far, and how current
nov = [r for r in deals if r["event_date"][:7] == "2026-11"]
M["nov_days"] = dict(sorted(Counter(r["event_date"][:10] for r in nov).items()))
M["nov_folded_pairs_in_month"] = sum(1 for r in nov if r["event_id"] in gone)
last = date.fromisoformat(M["last_date"])
M["days_from_newest_to_2026_11_26"] = (date(2026, 11, 26) - last).days
chk = rows(CHECKED)
M["checked_last"] = max(r["checked_at"] for r in chk)
M["checked_by_month_of_check"] = dict(sorted(Counter(r["checked_at"][:7] for r in chk).items()))

# 3. the news window: by month of publication, stories, scored, eligible for the extractor, sent
news = rows(os.path.join(OUT, "news_stories.csv"))
SECT = {"deal", "ppa", "capital", "nuclear", "generation", "datacenter_power", "lng", "oil", "gas"}
sent = {r["story_id"] for r in chk}
win = defaultdict(lambda: Counter())
for r in news:
    m = r["event_date"][:7]
    if m < "2025-01":
        continue
    w = win[m]
    w["stories"] += 1
    if r["scored_at"]:
        w["scored"] += 1
        sig = num(r["significance"])
        if r["sector"] in SECT and sig is not None and sig >= 5:
            w["eligible"] += 1
            if r["event_id"] not in sent:
                w["eligible_not_sent"] += 1
    if r["event_id"] in sent:
        w["sent"] += 1
dm = Counter(r["event_date"][:7] for r in folded)
M["window"] = {m: {**dict(win[m]), "deals": dm.get(m, 0)} for m in sorted(win)}
M["scored_last_story"] = max((r["event_date"][:10] for r in news if r["scored_at"]), default="")
M["scored_last_at"] = max((r["scored_at"] for r in news if r["scored_at"]), default="")
M["stories_after_newest_deal_scored_eligible"] = sum(1 for r in news if r["event_date"][:10] > M["last_date"] and r["scored_at"]
                                                    and r["sector"] in SECT and (num(r["significance"]) or 0) >= 5)
M["stories_after_newest_deal"] = sum(1 for r in news if r["event_date"][:10] > M["last_date"])

# 4. MW by stage: the tracker's "Disclosed megawatts" and the month's "MW announced" add every status
mwd = [r for r in folded if num(r["mw"]) is not None]
M["tracker_mw"] = sum(num(r["mw"]) for r in mwd)
M["mw_by_status"] = {k: [sum(1 for r in mwd if (r["status"] or "") == k), sum(num(r["mw"]) for r in mwd if (r["status"] or "") == k)]
                     for k in sorted(set(r["status"] or "" for r in mwd))}
M["mw_by_stage"] = {k: [sum(1 for r in mwd if (r["stage"] or r["status"] or "") == k), sum(num(r["mw"]) for r in mwd if (r["stage"] or r["status"] or "") == k)]
                    for k in sorted(set(r["stage"] or r["status"] or "" for r in mwd))}
M["nov_mw_by_status"] = {k: sum(num(r["mw"]) for r in nov if num(r["mw"]) is not None and (r["stage"] or r["status"]) == k)
                         for k in sorted(set((r["stage"] or r["status"]) for r in nov if num(r["mw"]) is not None))}
noncanc = [r for r in mwd if (r["status"] or "") not in ("cancelled", "rumored")]
M["tracker_mw_without_cancelled_and_rumored"] = [len(noncanc), sum(num(r["mw"]) for r in noncanc)]
nc2 = [r for r in mwd if (r["status"] or "") != "cancelled"]
M["tracker_mw_without_cancelled"] = [len(nc2), sum(num(r["mw"]) for r in nc2)]

# 5. MW concentration and what the MW are (the largest ten: type, kind, technology, status, flags; no names)
top = sorted(mwd, key=lambda r: -num(r["mw"]))
M["mw_top3_share"] = round(100 * sum(num(r["mw"]) for r in top[:3]) / M["tracker_mw"], 1)
M["mw_top10"] = [{"mw": num(r["mw"]), "type": r["deal_type"], "kind": r["kind"], "tech": r["technology"], "status": r["status"],
                  "mwh": num(r["mwh"]), "ai": r["ai_power"], "flags": bool(r["flags"]), "date": r["event_date"][:10],
                  "country": r["country"], "id": r["event_id"]} for r in top[:10]]
M["mw_us_named_country"] = [sum(1 for r in mwd if r["country"] in ("United States", "US", "USA")),
                            sum(num(r["mw"]) for r in mwd if r["country"] in ("United States", "US", "USA"))]
M["mw_by_country"] = {k: round(sum(num(r["mw"]) for r in mwd if r["country"] == k), 1) for k in sorted(set(r["country"] for r in mwd))}
M["rows_by_country_top"] = Counter(r["country"] or "" for r in folded).most_common(8)

# 6. MWh, MW and dollars: rows with mwh, both, flags of the MW/MWh kind
M["with_mwh"] = sum(1 for r in folded if num(r["mwh"]) is not None)
M["with_mw_and_mwh"] = sum(1 for r in folded if num(r["mwh"]) is not None and num(r["mw"]) is not None)
M["flags_rows"] = len([r for r in deals if r["flags"]])
M["flag_kinds"] = dict(Counter(re.sub(r"[0-9.,]+", "N", f.split(":")[0])[:60] for r in deals for f in r["flags"].split("; ") if f))

# 7. USD per MW: the deals that state both, by type (an analyst's price-per-MW comparable, which the page does not draw)
both = [r for r in folded if num(r["mw"]) is not None and num(r["usd"] or r["dollars"]) is not None]
M["usd_and_mw_rows"] = len(both)
M["usd_per_mw"] = [{"type": r["deal_type"], "kind": r["kind"], "tech": r["technology"], "usd_per_mw_million": round(num(r["usd"] or r["dollars"]) / num(r["mw"]) / 1e6, 3),
                    "status": r["status"]} for r in sorted(both, key=lambda r: r["deal_type"])]

# 8. the comparables' median size by type: what each median mixes
for t in ("ppa", "m_and_a", "other", "offtake", "behind_the_meter"):
    xs = [r for r in folded if r["deal_type"] == t and num(r["mw"]) is not None]
    M[f"median_mw_{t}_mix"] = sorted(((num(r["mw"]), r["technology"] or "-", r["kind"], r["country"] or "-") for r in xs))

# 9. the AI tag: of the tagged (folded), what they are
ai = [r for r in folded if (r["ai_power"] or "").lower() == "true"]
M["ai_tagged"] = len(ai)
M["ai_by_kind"] = dict(Counter(r["kind"] or "-" for r in ai))
M["ai_by_type"] = dict(Counter(r["deal_type"] for r in ai))
M["ai_tech_top"] = Counter(r["technology"] or "-" for r in ai).most_common(10)
M["ai_basis_set"] = sum(1 for r in ai if r["ai_power_basis"])
M["ai_with_mw"] = [sum(1 for r in ai if num(r["mw"]) is not None), sum(num(r["mw"]) for r in ai if num(r["mw"]) is not None)]
M["ai_with_usd"] = [sum(1 for r in ai if num(r["usd"] or r["dollars"]) is not None), sum(num(r["usd"] or r["dollars"]) for r in ai if num(r["usd"] or r["dollars"]) is not None)]
ENERGY = re.compile(r"nuclear|reactor|smr|fusion|gas|lng|oil|solar|wind|batter|storage|hydro|geotherm|renewab|power|coal|uranium|fuel|grid|transmission|electric|energy|turbine|microgrid|pipeline", re.I)
M["ai_no_energy_word"] = sum(1 for r in ai if not ENERGY.search(f"{r['technology']} {r['asset']}"))
M["ai_no_energy_word_by_kind"] = dict(Counter(r["kind"] for r in ai if not ENERGY.search(f"{r['technology']} {r['asset']}")))

# 10. the grid: rows with a named grid; where it differs from the state's (the AI view's note says named first)
SG = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM", "OH": "PJM",
      "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO", "OK": "SPP", "KS": "SPP", "NE": "SPP"}
for s in "CT ME MA NH RI VT".split():
    SG[s] = "ISO-NE"
named = [r for r in folded if r["grid"]]
M["named_grid_rows"] = [{"grid": r["grid"], "state": r["state"], "state_grid": SG.get((r["state"] or "").upper(), ""), "ai": r["ai_power"]} for r in named]

# 11. one deal, several rows: candidates the register has not folded (same type; same two canonical parties in either
# order; within 30 days); and the doubtful pairs left as two, with their MW and USD
def key(r):
    b, s = (r["buyer_name"] or r["buyer"]).strip().lower(), (r["seller_name"] or r["seller"]).strip().lower()
    return r["deal_type"], frozenset(x for x in (b, s) if x)


cand = []
fl = sorted(folded, key=lambda r: r["event_date"])
for i, a in enumerate(fl):
    for b in fl[i + 1:]:
        da, db = date.fromisoformat(a["event_date"][:10]), date.fromisoformat(b["event_date"][:10])
        if (db - da).days > 30:
            break
        ka, kb = key(a), key(b)
        if ka[0] == kb[0] and len(ka[1]) == 2 and ka[1] == kb[1]:
            cand.append((a, b))
M["candidate_pairs_same_type_parties_30d"] = len(cand)
M["candidate_pairs_detail"] = [{"type": a["deal_type"], "days": (date.fromisoformat(b["event_date"][:10]) - date.fromisoformat(a["event_date"][:10])).days,
                                "mw": [num(a["mw"]), num(b["mw"])], "usd": [num(a["usd"] or a["dollars"]), num(b["usd"] or b["dollars"])],
                                "status": [a["status"], b["status"]], "ids": [a["event_id"], b["event_id"]],
                                "doubtful_in_register": any({p["duplicate_event_id"], p["kept_event_id"]} == {a["event_id"], b["event_id"]} for p in pairs)}
                               for a, b in cand]
M["candidate_mw_counted_twice"] = sum(min(x["mw"]) for x in M["candidate_pairs_detail"] if None not in x["mw"])
M["candidate_usd_counted_twice"] = sum(min(x["usd"]) for x in M["candidate_pairs_detail"] if None not in x["usd"])
# same MW and same buyer, any type, within 60 days (a looser look)
loose = []
for i, a in enumerate(fl):
    for b in fl[i + 1:]:
        if (date.fromisoformat(b["event_date"][:10]) - date.fromisoformat(a["event_date"][:10])).days > 60:
            break
        if num(a["mw"]) is not None and num(a["mw"]) == num(b["mw"]) and ((a["buyer_name"] or a["buyer"]).lower() == (b["buyer_name"] or b["buyer"]).lower() or (a["seller_name"] or a["seller"]).lower() == (b["seller_name"] or b["seller"]).lower()):
            loose.append({"mw": num(a["mw"]), "types": [a["deal_type"], b["deal_type"]], "ids": [a["event_id"], b["event_id"]]})
M["same_mw_same_party_60d"] = loose
M["doubtful_pairs"] = [{"ids": [p["duplicate_event_id"], p["kept_event_id"]], "both_held": p["duplicate_event_id"] in ids and p["kept_event_id"] in ids}
                       for p in pairs if p["ruling"] == "doubtful"]
byid = {r["event_id"]: r for r in deals}
M["doubtful_usd_both"] = [[num(byid[i]["usd"] or byid[i]["dollars"]) if i in byid else None for i in x["ids"]] for x in M["doubtful_pairs"]]
M["folded_lost_figures"] = []
for p in pairs:
    if p["ruling"] == "fold" and p["duplicate_event_id"] in byid and p["kept_event_id"] in byid:
        d, k = byid[p["duplicate_event_id"]], byid[p["kept_event_id"]]
        M["folded_lost_figures"].append({"kept": k["event_id"], "dup_mw": num(d["mw"]), "kept_mw": num(k["mw"]),
                                         "dup_usd": num(d["usd"] or d["dollars"]), "kept_usd": num(k["usd"] or k["dollars"])})

# 12. the evidence: valuations in a USD span; another currency named where no USD is kept (counts only)
spans_by = defaultdict(str)
evtext = defaultdict(str)
for r in ev:
    spans_by[r["deal_id"]] += " ; " + r["spans"]
    evtext[r["deal_id"]] += " " + r["evidence"]


def usd_span(d):
    s = spans_by.get(d, "")
    m = re.findall(r"(?:dollars|usd):([^;]*)", s)
    return " ".join(m)


M["usd_span_valuation_word"] = sum(1 for r in folded if num(r["usd"] or r["dollars"]) is not None and re.search(r"valu", usd_span(r["event_id"]), re.I))
M["usd_rows_with_valuation_word_in_evidence"] = sum(1 for r in folded if num(r["usd"] or r["dollars"]) is not None and re.search(r"valuation|valued at|valuing", evtext.get(r["event_id"], ""), re.I))
CUR = re.compile(r"€|£|¥|\beuros?\b|\bpounds?\b|\byen\b|\brupees?\b|\bEUR\b|\bGBP\b|\bINR\b|\bJPY\b|\bA\$|\bC\$|\bAUD\b|\bCAD\b|\bkroner\b|\bNOK\b|\bSEK\b|\byuan\b|\bRMB\b|\bwon\b|\breais\b|\bBRL\b", re.I)
M["no_usd_other_currency_in_evidence"] = sum(1 for r in folded if num(r["usd"] or r["dollars"]) is None and CUR.search(evtext.get(r["event_id"], "")))
M["usd_kept_other_currency_in_evidence"] = sum(1 for r in folded if num(r["usd"] or r["dollars"]) is not None and CUR.search(evtext.get(r["event_id"], "")))
M["evidence_rows_found"] = sum(1 for r in folded if r["event_id"] in evtext)

# 13. confidence
M["sure_below_0_6"] = [sum(1 for r in folded if (num(r["confidence"]) or 1) < 0.6),
                       sum(num(r["mw"]) for r in folded if (num(r["confidence"]) or 1) < 0.6 and num(r["mw"]) is not None)]
M["sure_below_0_7"] = [sum(1 for r in folded if (num(r["confidence"]) or 1) < 0.7),
                       sum(num(r["mw"]) for r in folded if (num(r["confidence"]) or 1) < 0.7 and num(r["mw"]) is not None)]
M["fields_version"] = dict(Counter(r["fields_version"] for r in deals))

# 14. the companies tab: energy_companies rows seeded from the held deals
co = rows(os.path.join(OUT, "energy_companies.csv"))
M["companies_rows"] = len(co)
M["companies_from_deals"] = sum(1 for r in co if (r["confidence_note"] or "").startswith("from deals"))
M["companies_from_deals_with_story_link"] = sum(1 for r in co if (r["confidence_note"] or "").startswith("from deals") and r["sources"])
M["companies_from_deals_with_deal_tag"] = sum(1 for r in co if (r["confidence_note"] or "").startswith("from deals") and "deal:" in (r["niche_tags"] or ""))
M["companies_from_deals_with_location"] = sum(1 for r in co if (r["confidence_note"] or "").startswith("from deals") and r["location"])

json.dump(M, open(DEST, "w", encoding="utf-8"), indent=1, default=list)
print("written", DEST)
