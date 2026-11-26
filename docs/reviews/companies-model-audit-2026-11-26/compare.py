"""The restatement (restate.json) set against what the pages print: the index file's figures for every listed company,
the default view's first page as drawn by the site's own code (draw/main_index.html), and three company pages as drawn
(draw/main_fpl.html, main_google.html, main_ceg.html). Prints every key compared and every gap; writes compare.json.
Session 10228."""
import html
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", ".."))
D = os.path.join(WT, "site", "data", "companies")
R = json.load(open(os.path.join(HERE, "restate.json"), encoding="utf-8"))
ix = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
cols = ix["columns"]
irows = [dict(zip(cols, r)) for r in ix["rows"]]
n_keys, gaps, ties = 0, [], 0


def check(key, page, mine):
    global n_keys
    n_keys += 1
    if page != mine:
        gaps.append((key, page, mine))


# 1. the index's lists (the filters' counts) and its count
check("n_listed", ix["n_listed"], R["n_listed"])
for k in ("kinds", "segments", "states", "grids"):
    for name in sorted(set(ix[k]) | set(R[k])):
        check(f"{k}:{name}", ix[k].get(name), R[k].get(name))

# 2. every listed company's figures in the index
FIGS = ["n_plants", "plants_mw", "owned_mw", "planned_mw", "n_queue", "queue_mw", "n_reactors", "n_policy_actions"]
for r in irows:
    m = R["all_rows"][r["id"]]
    for c in FIGS:
        check(f"{r['id']}:{c}", round(float(r[c]), 1), round(m["fig"][c], 1))
    check(f"{r['id']}:footprint_mw", round(float(r["footprint_mw"]), 1), round(m["fig"]["footprint_mw"], 1))
    for c in ("kind", "segment", "grids", "n_links"):
        check(f"{r['id']}:{c}", r[c], m[c])
    check(f"{r['id']}:first_seen", r["first_seen"], m["first"])
    check(f"{r['id']}:last_seen", r["last_seen"], m["last"])
    # the states, most first: the order of states with equal counts is the input rows' order, not a rule
    a, b = r["states"].split(";") if r["states"] else [], m["states"].split(";") if m["states"] else []
    n_keys += 1
    if a != b:
        if sorted(a) == sorted(b):
            ties += 1
        else:
            gaps.append((f"{r['id']}:states", r["states"], m["states"]))
# 3. the default order
check("order (every listed company)", [r["id"] for r in irows], R["order"])

# 4. the first page as drawn
H = open(os.path.join(HERE, "draw", "main_index.html"), encoding="utf-8").read()
trs = re.findall(r'<tr class="border-b border-rule" data-company="([^"]+)">(.*?)</tr>', H, re.S)


def cells(s):
    out = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", s, re.S)
    return [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in out]


check("page 1 rows drawn", len(trs), 50)
for (cid, body), m in zip(trs, R["page1"]):
    cs = cells(body)
    check(f"drawn:{cid}:id", cid, m["id"])
    name_cell = cs[0]
    check(f"drawn:{cid}:name", name_cell.startswith(m["name"]), True)
    check(f"drawn:{cid}:kind", cs[1], m["kind"])
    check(f"drawn:{cid}:segment", cs[2], m["segment"])
    # the States cell: equal, or equal up to the order of tied states
    n_keys += 1
    if cs[3] != m["states_text"]:
        drawn = [s for s in cs[3].replace(" ...", "").split(", ") if s]
        cnt = m["states_counts"]
        mine = [s for s in m["states_text"].replace(" ...", "").split(", ") if s]
        if sorted(cnt[s] for s in drawn) == sorted(cnt[s] for s in mine) and all(s in cnt for s in drawn):
            ties += 1
        else:
            gaps.append((f"drawn:{cid}:states", cs[3], m["states_text"]))
    for i, k in ((4, "op"), (5, "planned"), (6, "queue"), (7, "policy"), (8, "footprint")):
        check(f"drawn:{cid}:{k}", cs[i], m[k])
T = html.unescape(re.sub(r"<[^>]+>", " ", H))
T = re.sub(r"\s+", " ", T)
check("drawn: the count line", f"{R['n_listed']:,} of {R['n_listed']:,} companies; page 1 of {R['pages']}." in T, True)
for k in ("kinds", "segments", "grids"):
    for name, n in R[k].items():
        if k == "kinds" and name == "power marketer":
            check(f"drawn option kind {name} ({n:,})", f"{name} ({n:,})" in T, True)
            continue
        check(f"drawn option {k} {name} ({n:,})", f"{name} ({n:,})" in T, True)

# 5. the company pages as drawn
for cid, f in (("eia-6452", "main_fpl"), ("eia-64846", "main_google"), ("eia-65506", "main_ceg")):
    P = open(os.path.join(HERE, "draw", f + ".html"), encoding="utf-8").read()
    PT = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", P)))
    m = R["company"][cid]
    check(f"{cid}: lead", (m["lead"] in PT), True)
    keyed = {a: b for a, b, _ in re.findall(r'data-n="company_directory\|company:[^|"]+\|([a-z_]+)" data-raw="([^"]*)"[^>]*>([^<]*)<', P)}
    for col, v in m["heads"].items():
        check(f"{cid}: headline {col}", keyed.get(col) is not None and v in PT, True)
    for col, tip in m["tips"].items():
        if col in m["heads"]:
            check(f"{cid}: tip {col}", tip in PT, True)
    for fu, (v, share) in m["fuel"].items():
        check(f"{cid}: fuel {fu}", f"{fu} {v} {share}" in PT, True)
    for t in m["year_titles"]:
        check(f"{cid}: year {t[:12]}", t in PT, True)
    drawn_rows = dict(re.findall(r'data-rows-table="([^"]+)" data-rows="(\d+)"', P))
    for t, n in m["rows_by_table"].items():
        check(f"{cid}: rows of {t}", int(drawn_rows.get(t, -1)), n)
    for t, n in m["held"].items():
        check(f"{cid}: held {t}", f"{n:,}, held" in PT, True)
    check(f"{cid}: kind", f"{m['kind']}" in PT, True)
    check(f"{cid}: seen", (m["seen"] in PT) if m["seen"] != " to " else True, True)
    check(f"{cid}: match", f"{m['match']}" in PT, True)
    if m["deals_held"]:
        check(f"{cid}: deals held line", m["deals_held"] in PT, True)
    # the names list: each (name, table, role) with its count of rows
    import itertools
    c = None
    for fn in os.listdir(os.path.join(D, "c")):
        s = json.load(open(os.path.join(D, "c", fn), encoding="utf-8"))
        if cid in s:
            c = s[cid]
            break
    for n, t, role, k, rule in c["names"]:
        check(f"{cid}: names {n}|{t}|{role}", k, m["names_counts"].get(f"{n}|{t}|{role}", 0))

out = dict(keys=n_keys, gaps=len(gaps), ties_in_state_order=ties, gap_list=gaps[:200])
json.dump(out, open(os.path.join(HERE, "compare.json"), "w", encoding="utf-8"), indent=1)
print(f"{n_keys:,} keys compared; {len(gaps)} gaps; {ties} states lists equal up to the order of tied states")
for g in gaps[:60]:
    print("GAP", str(g)[:300])
