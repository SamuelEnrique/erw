"""Audit of /equities, session 11403: a listed parent and its subsidiary listed by a preferred share (or a partnership and
the company that holds it), period by period: how often the two files hold the very same figure, and from the same
filing. Pairs named on the command line as PARENT:CHILD. No request, no write."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
by = {c["ticker"]: c for c in idx["companies"]}
COLS = ("revenue", "net_income", "capex", "debt", "shares_outstanding")


def table(tk):
    s = json.load(open(os.path.join(D, by[tk]["file"]), encoding="utf-8"))
    out = {}
    for r in s["quarterly"]:
        r = dict(zip(s["quarterly_columns"], r))
        k = (r["period_end"], r["months"])
        if k not in out or (r["filed"], r["accession"]) > (out[k]["filed"], out[k]["accession"]):
            out[k] = r
    return out, s["concepts"]


for pair in sys.argv[1:]:
    p, c = pair.split(":")
    a, ca = table(p)
    b, cb = table(c)
    common = sorted(set(a) & set(b))
    same_acc = sum(1 for k in common if a[k]["accession"] == b[k]["accession"])
    print(f"\n{p} ({by[p]['name']}, cik {by[p]['cik']}) and {c} ({by[c]['name']}, cik {by[c]['cik']}): "
          f"{len(a)} and {len(b)} periods, {len(common)} in both, {same_acc} of them from the same filing (accession)")
    for col in COLS:
        both = [k for k in common if a[k][col] is not None and b[k][col] is not None]
        eq = [k for k in both if a[k][col] == b[k][col]]
        print(f"  {col:18s} both filed {len(both):>3d}, the very same figure {len(eq):>3d}"
              + (f" (newest {max(eq)[0]})" if eq else ""))
    recent = [k for k in common if k[0] >= "2025-01-01" and k[1] == 3]
    for k in recent[-4:]:
        print(f"  {k[0]} 3 months: revenue {a[k]['revenue']} against {b[k]['revenue']}; net income {a[k]['net_income']} "
              f"against {b[k]['net_income']}; accessions {a[k]['accession']} {b[k]['accession']}")
    print(f"  concepts: {p} {ca.get('revenue')}; {c} {cb.get('revenue')}")
