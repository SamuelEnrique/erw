# Session 10215: an independent restatement of every figure of the deal tracker (/deals and its views), written from
# the method notes (docs/methods/deal_tracker.md sections 2 to 7, docs/methods/energy_deals.md) and the pages' own
# words, not from site/lib/*.ts. Standard library only. It reads the warehouse's CSV as the extractor wrote it (not
# the live set) and the register (warehouse/deals/duplicates.csv) and the capital view's file.
#   python runs/c10215/restate.py <energy_deals.csv> <duplicates.csv> <capital.json> <month YYYY-MM> <out.json>
# Where the notes leave a rule open (a word list), the choice is written beside it, so a gap with the page's code
# is a finding about the note or about the code, never hidden.
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict

SRC, DUPS, CAP, MONTH, OUT = sys.argv[1:6]


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader([ln for ln in f if not ln.startswith("#")]))


def num(v):
    v = (v or "").strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def jsround(x):
    """JavaScript's Math.round: halves go up."""
    import math
    return math.floor(x + 0.5)


raw = rows_of(SRC)
pairs = rows_of(DUPS)
cap = json.load(open(CAP, encoding="utf-8"))

# the note's section 6 (and datacenter_tracker.md section 6): the states read to a grid
STATE_GRID = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO"}
for s in "CT ME MA NH RI VT".split():
    STATE_GRID[s] = "ISO-NE"
for s in "PA NJ MD DE VA WV OH DC".split():
    STATE_GRID[s] = "PJM"
for s in "MN IA WI MI LA".split():
    STATE_GRID[s] = "MISO"
for s in "OK KS NE".split():
    STATE_GRID[s] = "SPP"

# energy_deals.md, the kind of an older row from its type (the note: "else from its type")
FORM = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a", "debt": "capital",
        "equity_raise": "capital", "tax_equity": "capital", "joint_venture": "capital", "fuel_supply": "fuel_supply",
        "behind_the_meter": "behind_the_meter", "nuclear_restart": "nuclear_restart_uprate", "smr": "smr"}


def deal(r):
    state = (r.get("state") or "").strip().upper()
    usd = num(r.get("usd"))
    dollars = num(r.get("dollars"))
    return {
        "id": r["event_id"], "date": r["event_date"][:10], "month": r["event_date"][:7], "year": r["event_date"][:4],
        "type": r.get("deal_type", ""), "status": r.get("status", ""), "stage": r.get("stage", ""),
        "buyer": r.get("buyer", ""), "seller": r.get("seller", ""),
        "others": [x.strip() for x in (r.get("other_parties") or "").split(";") if x.strip()],
        "buyer_name": r.get("buyer_name", "") or r.get("buyer", ""), "seller_name": r.get("seller_name", "") or r.get("seller", ""),
        "asset": r.get("asset", ""), "technology": r.get("technology", ""), "state": state,
        "named_grid": r.get("grid", ""), "state_grid": STATE_GRID.get(state, ""),
        "mw": num(r.get("mw")), "mwh": num(r.get("mwh")),
        # the note: "US dollars (usd, the older dollars)"; usd = dollars
        "usd": usd if usd is not None else dollars,
        # the note: "A price (usd_per_mwh, the older price)"
        "price": num(r.get("usd_per_mwh")) if num(r.get("usd_per_mwh")) is not None else num(r.get("price")),
        "price_value": num(r.get("price_value")), "price_unit": r.get("price_unit", ""),
        "ai": (r.get("ai_power") or "").strip().lower() == "true",
        "confidence": num(r.get("confidence")), "flags": [x for x in (r.get("flags") or "").split("; ") if x],
        "kind": r.get("kind") or FORM.get(r.get("deal_type", ""), "other"),
        "links": [x for x in (r.get("story_urls") or "").split(";") if x],
    }


table = [deal(r) for r in raw]
F = {}

# 7.1 the table: every row
F["table|rows"] = len(table)
inm = [d for d in table if d["month"] == MONTH]
month = MONTH
if not inm:
    y, m = int(MONTH[:4]), int(MONTH[5:7]) - 1
    if m == 0:
        y, m = y - 1, 12
    month = f"{y}-{m:02d}"
    inm = [d for d in table if d["month"] == month]
F[f"deals|month_count|{month}"] = len(inm)
F[f"deals|month_mw|{month}"] = sum(d["mw"] for d in inm if d["mw"] is not None)
F[f"table|month_with_mw|{month}"] = sum(1 for d in inm if d["mw"] is not None)
if inm:
    F[f"deals|month_ai_pct|{month}"] = jsround(100 * sum(d["ai"] for d in inm) / len(inm))


def table_grid(d):
    return d["named_grid"] or d["state_grid"]


def disclosed(d):
    return d["price"] is not None or (d["price_value"] is not None and re.search(r"mwh|kwh|mw-?month|mmbtu", d["price_unit"], re.I) is not None)


F["table|filter|ai|yes"] = sum(d["ai"] for d in table)
F["table|filter|ai|no"] = sum(not d["ai"] for d in table)
F["table|filter|price|yes"] = sum(disclosed(d) for d in table)
F["table|filter|mw_from|500"] = sum(1 for d in table if d["mw"] is not None and d["mw"] >= 500)
for k in ["nuclear_restart_uprate", "smr", "behind_the_meter", "gas_buildout", "transmission", "storage", "compute_capacity", "ppa",
          "offtake", "project_finance", "m_and_a", "capital", "fuel_supply", "other"]:
    F[f"table|filter|kind|{k}"] = sum(1 for d in table if d["kind"] == k)
for s in ["rumored", "announced", "signed", "financed", "closed", "under_construction", "operating", "cancelled"]:
    F[f"table|filter|stage|{s}"] = sum(1 for d in table if (d["stage"] or d["status"]) == s)
F["table|filter|stage|none"] = sum(1 for d in table if not (d["stage"] or d["status"]))
F["table|with_mw"] = sum(1 for d in table if d["mw"] is not None)
F["table|with_usd"] = sum(1 for d in table if d["usd"] is not None)
F["table|with_flags"] = sum(1 for d in table if d["flags"])
conf = sorted(d["confidence"] for d in table if d["confidence"] is not None)
F["table|sure_min"], F["table|sure_max"] = conf[0], conf[-1]

# section 3: the register's folded pairs counted once, as the row kept (its own figures), with both rows' links
ids = {d["id"]: d for d in table}
gone = set()
nfold = 0
for p in pairs:
    if p["ruling"] == "fold" and p["duplicate_event_id"] in ids and p["kept_event_id"] in ids:
        gone.add(p["duplicate_event_id"])
        nfold += 1
alld = [d for d in table if d["id"] not in gone]
for d in alld:
    d["grid"] = d["state_grid"]   # section 6: the tracker, the comparables and the AI view read the state alone

# 7.2 the tracker tab
F["tracker|deals"] = len(alld)
F["tracker|with_mw"] = sum(1 for d in alld if d["mw"] is not None)
F["tracker|mw"] = sum(d["mw"] for d in alld if d["mw"] is not None)
F["tracker|with_price"] = sum(1 for d in alld if d["price"] is not None)
F["tracker|with_other_price"] = sum(1 for d in alld if d["price"] is None and d["price_value"] is not None)
F["tracker|with_dollars"] = sum(1 for d in alld if d["usd"] is not None)
F["tracker|folded"] = nfold
GROUP = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "acquisition", "tolling": "tolling"}
gc = Counter(GROUP.get(d["type"], "other") for d in alld)
for g in ["ppa", "offtake", "project_finance", "acquisition", "tolling", "other"]:
    F[f"tracker|type|{g}"] = gc.get(g, 0)


# energy_deals.md, "Read from fields already held": the four kinds, by type or by the note's words in asset or technology
def kinds(d):
    text = f"{d['asset']} | {d['technology']}"
    out = []
    if d["type"] == "nuclear_restart" or re.search(r"restart", text, re.I):
        out.append("nuclear_restart")
    if d["type"] == "smr" or re.search(r"small modular|\bSMRs?\b|microreactor|micro-reactor", text, re.I):
        out.append("smr")
    if (re.search(r"\bgas\b|natural gas|natgas", d["technology"], re.I) and re.search(r"plant|turbine|generat", d["asset"], re.I)
            and d["type"] not in ("m_and_a", "fuel_supply")):
        out.append("gas")
    if d["type"] == "behind_the_meter" or re.search(r"behind[- ]the[- ]meter|co-?located|on-?site", text, re.I):
        out.append("behind_the_meter")
    return out


for k in ["nuclear_restart", "smr", "gas", "behind_the_meter"]:
    F[f"tracker|kind|{k}"] = sum(1 for d in alld if k in kinds(d))
tc = Counter(d["technology"] for d in alld)
for t, n in tc.items():
    F[f"tracker|technology|{t if t else 'not stated'}"] = n
for g in ["ERCOT", "CAISO", "PJM", "MISO", "SPP", "NYISO", "ISO-NE"]:
    F[f"tracker|grid|{g}"] = sum(1 for d in alld if d["grid"] == g)
for y, n in Counter(d["year"] for d in alld).items():
    F[f"tracker|year|{y}"] = n
for s in ["rumored", "announced", "signed", "closed", "cancelled"]:
    F[f"tracker|status|{s}"] = sum(1 for d in alld if d["status"] == s)
F["tracker|view|storage"] = sum(1 for d in alld if re.search(r"batter|storage|\bbess\b", d["technology"], re.I)
                                or re.search(r"batter|energy storage|\bbess\b", d["asset"], re.I))
F["tracker|view|ai"] = sum(d["ai"] for d in alld)
pc = Counter()
for d in alld:
    for p in set(x for x in [d["buyer"], d["seller"], *d["others"]] if x):
        pc[p] += 1
for p, n in pc.items():
    if n >= 2:
        F[f"tracker|party|{p}"] = n
ms = sorted(d["month"] for d in alld)
y, m = int(ms[0][:4]), int(ms[0][5:7])
mc = Counter(d["month"] for d in alld)
while True:
    k = f"{y}-{m:02d}"
    F[f"tracker|month|{k}"] = mc.get(k, 0)
    if k >= ms[-1]:
        break
    m += 1
    if m > 12:
        y, m = y + 1, 1
F["tracker|with_state"] = sum(1 for d in alld if d["state"])
F["tracker|with_grid"] = sum(1 for d in alld if d["grid"])


def med3(xs):
    return statistics.median(xs) if len(xs) >= 3 else None


# 7.3 the comparables
for dim in ["type", "technology", "grid", "year"]:
    by = defaultdict(list)
    for d in alld:
        by[d[dim]].append(d)
    for v, ds in by.items():
        key = v if v != "" else "-"
        prices = [d["price"] for d in ds if d["price"] is not None]
        mws = [d["mw"] for d in ds if d["mw"] is not None]
        F[f"deals|comp_deals|{dim}|{key}"] = len(ds)
        F[f"deals|comp_with_price|{dim}|{key}"] = len(prices)
        F[f"deals|comp_with_mw|{dim}|{key}"] = len(mws)
        if med3(prices) is not None:
            F[f"deals|comp_median_price|{dim}|{key}"] = med3(prices)
        if med3(mws) is not None:
            F[f"deals|comp_median_mw|{dim}|{key}"] = med3(mws)
priced = [d for d in alld if d["type"] in ("ppa", "offtake") and d["price"] is not None]
F["deals|priced"] = len(priced)
for dim in ["technology", "grid", "year"]:
    by = defaultdict(list)
    for d in priced:
        by[d[dim]].append(d["price"])
    for v, ps in by.items():
        key = v if v != "" else "-"
        F[f"deals|price_count|{dim}|{key}"] = len(ps)
        if len(ps) >= 3:
            F[f"deals|price_median|{dim}|{key}"] = statistics.median(ps)
            F[f"deals|price_low|{dim}|{key}"] = min(ps)
            F[f"deals|price_high|{dim}|{key}"] = max(ps)


# 7.4 the AI view: the kind of supply, the first that the kind or the technology's words say
def supply(d):
    t = d["technology"].lower()
    k = d["kind"]
    if k in ("nuclear_restart_uprate", "smr") or re.search(r"nuclear|reactor|smr|fusion", t):
        return "nuclear"
    if k == "gas_buildout" or re.search(r"\bgas\b|lng|turbine", t):
        return "gas"
    if k == "storage" or re.search(r"solar|wind|batter|storage|hydro|geotherm|renewable", t):
        return "renewables_storage"
    if k == "compute_capacity":
        return "compute"
    if k in ("ppa", "offtake", "behind_the_meter"):
        return "grid"
    if k in ("capital", "m_and_a", "project_finance"):
        return "capital"
    return "other"


def quarter(d):
    return f"{d['year']}-Q{(int(d['date'][5:7]) - 1) // 3 + 1}"


def buyer(d):
    return d["buyer_name"] or d["seller_name"] or ""


ai = [d for d in alld if d["ai"]]
F["deals|ai_tagged"] = len(ai)
for dim, of in [("buyer", buyer), ("supply", supply), ("grid", lambda d: d["grid"]), ("quarter", quarter)]:
    by = defaultdict(list)
    for d in ai:
        by[of(d)].append(d)
    for v, ds in by.items():
        key = v if v != "" else "-"
        mws = [d["mw"] for d in ds if d["mw"] is not None]
        us = [d["usd"] for d in ds if d["usd"] is not None]
        F[f"deals|ai_deals|{dim}|{key}"] = len(ds)
        if mws:
            F[f"deals|ai_mw|{dim}|{key}"] = sum(mws)
        F[f"deals|ai_with_mw|{dim}|{key}"] = len(mws)
        if us:
            F[f"deals|ai_usd|{dim}|{key}"] = sum(us)
        F[f"deals|ai_with_usd|{dim}|{key}"] = len(us)
noncap = [d for d in ai if supply(d) != "capital"]
for by in ["mw", "usd"]:
    ds = sorted([d for d in noncap if d[by] is not None], key=lambda d: (-d[by], d["id"]))[:10]
    for i, d in enumerate(ds):
        F[f"deals|ai_top_{by}|{i + 1}"] = d[by]

# 7.5 the charts
G5 = ["nuclear", "gas", "renewables_storage", "grid", "other"]
for q in sorted(set(quarter(d) for d in alld)):
    inq = [d for d in alld if quarter(d) == q]
    for g in G5:
        F[f"deals|chart_mw|{q}|{g}"] = sum(d["mw"] for d in inq if d["mw"] is not None and (supply(d) if supply(d) in G5[:4] else "other") == g)
    F[f"deals|chart_mw|{q}|without"] = sum(1 for d in inq if d["mw"] is None)
    allmw = sum(d["mw"] for d in inq if d["mw"] is not None)
    aimw = sum(d["mw"] for d in inq if d["mw"] is not None and d["ai"])
    if allmw > 0:
        F[f"deals|chart_ai|{q}|share"] = jsround(1000 * aimw / allmw) / 10
    F[f"deals|chart_ai|{q}|ai_mw"] = aimw
    F[f"deals|chart_ai|{q}|all_mw"] = allmw
for d in priced:
    F[f"deals|chart_price|{d['id']}|price"] = d["price"]
pm = defaultdict(lambda: [0.0, 0])
for d in alld:
    names = set()
    for x in (d["buyer_name"], d["seller_name"]):
        for n in x.split("; "):
            if n.strip():
                names.add(n.strip())
    for n in names:
        if d["mw"] is not None:
            pm[n][0] += d["mw"]
            pm[n][1] += 1
top = sorted([(n, v[0]) for n, v in pm.items() if v[1] > 0], key=lambda t: (-t[1], t[0]))[:10]
for n, v in top:
    F[f"deals|chart_party|{n}|mw"] = v

# 7.6 capital
F["capital|n_rows"] = cap["n_rows"]

json.dump({"month": month, "figures": F}, open(OUT, "w", encoding="utf-8"), indent=1, sort_keys=True)
print(json.dumps({"keys": len(F), "month": month, "tracker_deals": F["tracker|deals"], "tracker_mw": F["tracker|mw"]}))
