"""Audit of /equities, session 11403: one period filed twice on the same day under two accessions. The list's builder
breaks the tie by the accession number (equity_page_files.py later()); the page's figure line and newest columns
(site/lib/equities.ts later()) by the file's order alone. Where the two filings' figures differ, the page and the list
could print different figures for one period. No request, no write."""
import collections
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
COLS = ("revenue", "net_income", "capex", "debt", "shares_outstanding")
n = nd = 0
for c in idx["companies"]:
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    g = collections.defaultdict(list)
    for r in s["quarterly"]:
        r = dict(zip(s["quarterly_columns"], r))
        g[(r["period_end"], r["months"], r["filed"])].append(r)
    for k, rs in g.items():
        if len({r["accession"] for r in rs}) > 1:
            n += 1
            diff = [col for col in COLS if len({r[col] for r in rs if r[col] is not None}) > 1]
            if diff:
                nd += 1
                print(f"  {c['ticker']} {k}: {[r['accession'] for r in rs]} differ in {diff}")
print(f"periods filed twice on one day: {n}; with figures that differ: {nd}")
