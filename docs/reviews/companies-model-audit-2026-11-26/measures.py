"""One rule changed at a time, and the claims measured, on the company pages' files (site/data/companies/) and, read
only, the main copy's input tables. Session 10228, the companies audit. Prints counts and sums only; no row of a held
table is printed. Writes measures.json beside it."""
import csv
import io
import json
import math
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", ".."))
MAIN_OUT = r"C:\Users\lossa\Documents\erw\warehouse\output"
D = os.path.join(WT, "site", "data", "companies")
ix = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
T = ix["tables"]
cols = ix["columns"]
irows = [dict(zip(cols, r)) for r in ix["rows"]]
comp = {}
for f in sorted(os.listdir(os.path.join(D, "c"))):
    comp.update(json.load(open(os.path.join(D, "c", f), encoding="utf-8")))
M = {}


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def jsround(v):
    return math.floor(v + 0.5)


# 0. the sources lines (the as-of of each input, as the page files hold it)
M["sources"] = ix["sources"]
M["built"] = ix["built"]

# 1. the footprint's double count: a jointly owned generator the company also operates is in plants_mw whole and in
#    owned_mw for its share
overlap = {}
for cid, c in comp.items():
    op_gens = {}
    for l in c["links"]:
        if T[l[1]] == "eia860m_operating_generators":
            parts = l[2].split(":")          # eia860:<plant>:<generator>
            if len(parts) >= 3:
                op_gens[(parts[1], parts[2])] = fnum(l[6]) or 0.0
    ov = 0.0
    n = 0
    for l in c["links"]:
        if T[l[1]] == "eia860_generator_owners":
            parts = l[2].split(":")          # eia860_owner:<plant>:<generator>:<owner>
            if len(parts) >= 4 and (parts[1], parts[2]) in op_gens and fnum(l[6]):
                ov += fnum(l[6])
                n += 1
    if ov:
        overlap[cid] = (round(ov, 1), n)
M["double_count"] = dict(companies=len(overlap), mw=round(sum(v[0] for v in overlap.values()), 1),
                         generators=sum(v[1] for v in overlap.values()),
                         owned_mw_all=round(sum(float(r["owned_mw"]) for r in irows), 1))
by_fp = sorted(irows, key=lambda r: (-float(r["footprint_mw"]), -r["n_links"], r["id"]))
alt = sorted(irows, key=lambda r: (-(float(r["footprint_mw"]) - overlap.get(r["id"], (0, 0))[0]), -r["n_links"], r["id"]))
alt2 = sorted(irows, key=lambda r: (-(float(r["plants_mw"]) + float(r["planned_mw"]) + float(r["queue_mw"])), -r["n_links"], r["id"]))


def moved(a, b, k):
    pa = {r["id"]: i for i, r in enumerate(a)}
    pb = {r["id"]: i for i, r in enumerate(b)}
    top_a = [r["id"] for r in a[:k]]
    return dict(changed_places=sum(1 for i in top_a if pa[i] != pb[i]), left_top=sum(1 for i in top_a if pb[i] >= k))


M["double_count"]["rank_without_overlap"] = {f"top{k}": moved(by_fp, alt, k) for k in (10, 50)}
M["double_count"]["rank_operated_planned_queue_only"] = {f"top{k}": moved(by_fp, alt2, k) for k in (10, 50)}
M["double_count"]["top10"] = [(r["id"], r["name"], r["footprint_mw"], overlap.get(r["id"], (0, 0))[0]) for r in by_fp[:10]]
M["double_count"]["top10_without_overlap"] = [(r["id"], r["name"]) for r in alt[:10]]
M["double_count"]["top10_operated_planned_queue"] = [(r["id"], r["name"]) for r in alt2[:10]]
M["double_count"]["largest"] = sorted(((v[0], k, comp[k]["name"]) for k, v in overlap.items()), reverse=True)[:8]

# 2. owned links without MW (a share the builder could not compute: the generator is not in EIA-860M's operating list)
own_blank = Counter()
own_all = Counter()
for cid, c in comp.items():
    for l in c["links"]:
        if T[l[1]] == "eia860_generator_owners":
            own_all[cid] += 1
            if fnum(l[6]) is None:
                own_blank[cid] += 1
M["owned_without_mw"] = dict(links=sum(own_blank.values()), of=sum(own_all.values()), companies=len(own_blank),
                             companies_with_owned=len(own_all))

# 3. the printed figures rounded twice (the builder rounds to 0.1 MW, the page to a whole MW)
def raw_sum(c, table, live=False):
    s = 0.0
    for l in c["links"]:
        if T[l[1]] == table and (not live or l[12] not in ("withdrawn", "Completed")):
            s += fnum(l[6]) or 0.0
    return s


dbl = Counter()
dbl_rows = set()
for r in irows:
    c = comp[r["id"]]
    for col, table, live in (("plants_mw", "eia860m_operating_generators", False), ("planned_mw", "eia860m_planned_generators", False),
                             ("queue_mw", "ercot_interconnection_queue", True), ("owned_mw", "eia860_generator_owners", False)):
        v = raw_sum(c, table, live)
        if v and jsround(float(r[col])) != jsround(v):
            dbl[col] += 1
            dbl_rows.add(r["id"])
    v = raw_sum(c, "eia860m_operating_generators") + raw_sum(c, "eia860m_planned_generators") + raw_sum(c, "ercot_interconnection_queue", True) + raw_sum(c, "eia860_generator_owners")
    if v and jsround(float(r["footprint_mw"])) != jsround(v):
        dbl["footprint_mw"] += 1
        dbl_rows.add(r["id"])
M["double_rounding"] = dict(cells=dict(dbl), companies=len(dbl_rows), max_gap_mw=1)

# 4. policy actions: held, every cell 0, the regulator kind empty
M["policy"] = dict(held_links=ix["held_links"].get("policy_actions"), cells_above_zero=sum(1 for r in irows if r["n_policy_actions"]),
                   regulators_listed=ix["kinds"].get("regulator", 0), has_policy_option_returns=sum(1 for r in irows if r["n_policy_actions"] > 0))

# 5. "rows" of the held tables against the tables' rows (the main copy's files, and coverage's count)
def nrows(name):
    p = os.path.join(MAIN_OUT, name + ".csv")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return len(list(csv.reader(io.StringIO("".join(lines))))) - 1


cov = {}
with open(os.path.join(WT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        cov[r["table"]] = r["n_rows"]
M["held_rows_vs_links"] = {t: dict(page_says_rows=n, main_copy_file_rows=nrows(t), coverage_rows=cov.get(t))
                           for t, n in ix["held_links"].items()}

# 6. the kind filter: the kinds the index counts that the page's list (lib/companydb.ts KIND_ORDER) leaves out
src = open(os.path.join(WT, "site", "lib", "companydb.ts"), encoding="utf-8").read()
order = re.search(r"KIND_ORDER = \[(.*?)\]", src).group(1)
listed = re.findall(r'"([^"]+)"', order)
M["kind_filter"] = dict(page_list=listed, missing={k: v for k, v in ix["kinds"].items() if k not in listed})

# 7. corporate families: rows that share a parent field, and name families (a name's first word), as an illustration
fam = defaultdict(list)
for r in irows:
    first = re.sub(r"[^a-z]", "", r["name"].split()[0].lower()) if r["name"].split() else ""
    fam[first].append(r)
ill = {}
for w in ("constellation", "nextera", "duke", "dominion", "entergy", "invenergy", "talenenergy", "vistra", "calpine", "aes"):
    rs = fam.get(w, [])
    if not rs:
        continue
    top = max(rs, key=lambda r: float(r["plants_mw"]))
    ill[w] = dict(rows=len(rs), operating_mw=round(sum(float(r["plants_mw"]) for r in rs), 1),
                  largest_row=(top["id"], top["name"], top["plants_mw"]),
                  planned_mw=round(sum(float(r["planned_mw"]) for r in rs), 1), queue_mw=round(sum(float(r["queue_mw"]) for r in rs), 1),
                  rows_with_parent=sum(1 for r in rs if comp[r["id"]]["parent"]))
M["families"] = ill
M["parents"] = dict(companies_with_parent=sum(1 for c in comp.values() if c["parent"]),
                    parent_linked=sum(1 for c in comp.values() if c["parent_id"]),
                    bases=Counter((c["parent_basis"] or "").split(" ")[0] for c in comp.values() if c["parent"]))
# FPL's parent and NextEra's own row
M["nextera_rows"] = [(r["id"], r["name"], r["kind"], r["plants_mw"], r["footprint_mw"]) for r in irows if "nextera" in r["name"].lower()][:6]

# 8. near duplicates: listed rows whose names agree once spaces, punctuation and legal forms are dropped
LEG = {"inc", "llc", "lp", "corp", "co", "company", "corporation", "ltd", "the"}
def key(n):
    w = [x for x in re.sub(r"[^a-z0-9 ]+", " ", n.lower().replace("&", " and ")).split() if x not in LEG]
    return "".join(w)
bykey = defaultdict(list)
for r in irows:
    bykey[key(r["name"])].append(r["id"])
dups = {k: v for k, v in bykey.items() if len(v) > 1}
M["near_duplicates"] = dict(groups=len(dups), rows=sum(len(v) for v in dups.values()),
                            eia_id_pairs=sum(1 for v in dups.values() if all(i.startswith("eia-") for i in v)),
                            shared_exact_names=sum(1 for v in Counter(r["name"] for r in irows).values() if v > 1),
                            example_keys=sorted(dups)[:0])

# 9. the hold: does anything of a held table reach a public cell?
held = set(ix["held_tables"])
leak = Counter()
name_only_held = 0
for cid, c in comp.items():
    for l in c["links"]:
        if T[l[1]] in held:
            leak["links"] += 1
    for n in c["names"]:
        if n[1] in held:
            leak["names"] += 1
    for k in ("kind_basis", "segment_basis", "parent_basis"):
        if any(t in (c.get(k) or "") for t in held):
            leak[k] += 1
    if c["held"] and not any(l[4] == "" for l in c["links"]):
        name_only_held += 1
M["hold"] = dict(leaks=dict(leak), held_companies_listed=sum(1 for c in comp.values() if c["held"]),
                 held_companies_whose_name_no_public_row_writes=name_only_held, held_only_not_listed=ix["held_only"])

# 10. the HQ state against the states the rows name
hq = [r for r in irows if r["hq_state"]]
M["hq"] = dict(with_hq=len(hq), hq_not_among_states=sum(1 for r in hq if r["hq_state"] not in r["states"].split(";")),
               with_hq_and_no_operating=sum(1 for r in hq if not float(r["plants_mw"])))

# 11. the ERCOT queue in the files: positions by status, and the main copy's table date
q = Counter()
for c in comp.values():
    for l in c["links"]:
        if T[l[1]] == "ercot_interconnection_queue":
            q[l[12]] += 1
M["ercot_queue_links"] = dict(q)
M["kinds"] = ix["kinds"]
M["other_kind"] = ix["kinds"].get("other")

# 12. energy_companies (the deals page's companies tab): seeded from deals against researched, the stage and ticker
lines = [ln for ln in open(os.path.join(MAIN_OUT, "energy_companies.csv"), encoding="utf-8") if not ln.startswith("#")]
ec = list(csv.DictReader(io.StringIO("".join(lines))))
M["energy_companies"] = dict(rows=len(ec), from_deals=sum(1 for r in ec if r["confidence_note"].startswith("from deals")),
                             researched=sum(1 for r in ec if not r["confidence_note"].startswith("from deals")),
                             stage_names_exchange=sum(1 for r in ec if re.search(r"nasdaq|nyse", r["stage"], re.I)),
                             conf_below_50=sum(1 for r in ec if r["confidence"] and float(r["confidence"]) < 50),
                             conf_below_50_from_deals=sum(1 for r in ec if r["confidence"] and float(r["confidence"]) < 50 and r["confidence_note"].startswith("from deals")),
                             from_deals_with_location=sum(1 for r in ec if r["confidence_note"].startswith("from deals") and r["location"]))
json.dump(M, open(os.path.join(HERE, "measures.json"), "w", encoding="utf-8"), indent=1, default=list)
for k, v in M.items():
    if k != "sources":
        print(k, json.dumps(v, default=list)[:700])
for t, s in M["sources"].items():
    print("SOURCE", t, s[:300])
