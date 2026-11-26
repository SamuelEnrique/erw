"""Session 10219: /conditions' alerts strip restated from the two held input tables, and counted three ways.

argv: worktree root, warehouse output folder (read only), out JSON.
  1. The page file's alerts list for CAISO and ERCOT against the input tables' rows, folded as grid_all_alerts does
     (event_date, x_label, start, end, source_url), sorted by date then event_id.
  2. In each window the page offers (the nine events, the newest days): rows (what the heading counts), distinct
     notices (one per kind, start and end, whatever the region and day), rows that are an update or a statement
     (ERCOT's: a release that ends a notice or announces none), rows ERCOT marks x_counts=no.
  3. Each input's last date and when it was retrieved.
"""
import csv
import json
import os
import sys
from collections import Counter

ROOT, OUTDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def rows(name):
    p = os.path.join(OUTDIR, name + ".csv")
    with open(p, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def page(op):
    with open(os.path.join(ROOT, "site", "data", "conditions", op + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


ca = rows("caiso_grid_emergencies")
er = rows("ercot_grid_notices")
fold = {
    "caiso": sorted(([r["event_date"], r["x_label"], r["x_start"] or None, r["x_end"] or None, r["source_url"], r["event_id"], r["event_type"], r["x_region"], "yes"] for r in ca), key=lambda x: (x[0], x[5])),
    "ercot": sorted(([r["event_date"], r["x_label"], r["x_issued_at"] or None, None, r["source_url"], r["event_id"], r["event_type"], r["x_region"], r.get("x_counts", "")] for r in er), key=lambda x: (x[0], x[5])),
}
res = {}
for op in ("caiso", "ercot"):
    f = page(op)
    pa = f["alerts"]
    mine = [x[:5] for x in fold[op]]
    # the page file may be built from a newer copy of the input: compare on the dates both hold
    last_mine = max(x[0] for x in mine)
    pa_upto = [a for a in pa if a[0] <= last_mine]
    same = pa_upto == mine
    diff = None
    if not same:
        sa = Counter(tuple(a) for a in pa_upto)
        sm = Counter(tuple(a) for a in mine)
        diff = {"in_page_not_input": sum((sa - sm).values()), "in_input_not_page": sum((sm - sa).values()),
                "examples_page": [list(k) for k in list((sa - sm).keys())[:3]], "examples_input": [list(k) for k in list((sm - sa).keys())[:3]],
                "same_as_multiset": sa == sm}
    wins = [w for w in f["windows"]]
    per = {}
    for w in wins:
        inw = [x for x in fold[op] if w["start"] <= x[0] <= w["end"]]
        pw = [a for a in pa if w["start"] <= a[0] <= w["end"]]
        distinct = {(x[6], x[2], x[3]) for x in inw}
        per[w["id"]] = {"page_rows": len(pw), "input_rows": len(inw), "distinct_notices": len(distinct),
                        "regions": dict(Counter(x[7] for x in inw)),
                        "kinds": dict(Counter(x[6] for x in inw)),
                        "update_or_statement": sum(1 for x in inw if x[6] in ("update", "statement")),
                        "counts_no": sum(1 for x in inw if x[8] == "no"),
                        "rows_same_date_kind_start_end_as_another": len(inw) - len({(x[0], x[1], x[2], x[3]) for x in inw})}
    allk = Counter(x[6] for x in fold[op])
    res[op] = {"page_alerts": len(pa), "page_last": max(a[0] for a in pa), "input_rows": len(mine), "input_last": last_mine,
               "page_equals_input_upto_input_last": same, "diff": diff, "windows": per, "kinds_all": dict(allk),
               "update_or_statement_all": sum(1 for x in fold[op] if x[6] in ("update", "statement")),
               "counts_no_all": sum(1 for x in fold[op] if x[8] == "no"),
               "retrieved": sorted({r.get("retrieved_at", "")[:10] for r in (ca if op == "caiso" else er)})[-3:]}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
for op, v in res.items():
    print(op, "page", v["page_alerts"], "last", v["page_last"], "| input", v["input_rows"], "last", v["input_last"], "| equal", v["page_equals_input_upto_input_last"], v["diff"])
    print("  kinds", v["kinds_all"], "update/statement", v["update_or_statement_all"], "counts=no", v["counts_no_all"], "retrieved", v["retrieved"])
    for k, w in v["windows"].items():
        if w["page_rows"] or w["input_rows"]:
            print("  ", k, w)
