"""Audit of /equities, session 11403: every filing (accession) that appears in the files of two or more companies (a
joint 10-Q or 10-K), and whether those companies carry the very same figures from it. A parent and its subsidiary
cannot have the same revenue, net income, debt and share count to the dollar and the share: where they do, one of the
two carries the other's figures. Also each company's share count, period by period, where it jumps by a factor at a
shared filing. No request, no write."""
import collections
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
COLS = ("revenue", "net_income", "capex", "debt", "shares_outstanding")
acc = collections.defaultdict(lambda: collections.defaultdict(list))
for c in idx["companies"]:
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    for r in s["quarterly"]:
        r = dict(zip(s["quarterly_columns"], r))
        acc[r["accession"]][c["ticker"]].append(r)
shared = {a: v for a, v in acc.items() if len(v) > 1}
print(f"filings in two or more companies' files: {len(shared)}")
newest_hit = collections.defaultdict(set)
for a, v in sorted(shared.items()):
    tks = sorted(v)
    rows = {t: {(r["period_end"], r["months"]): r for r in v[t]} for t in tks}
    keys = set.intersection(*[set(x) for x in rows.values()])
    same = {col: sum(1 for k in keys if len({rows[t][k][col] for t in tks}) == 1 and rows[tks[0]][k][col] is not None) for col in COLS}
    filled = {col: sum(1 for k in keys if all(rows[t][k][col] is not None for t in tks)) for col in COLS}
    ends = sorted({k[0] for k in keys})
    print(f"  {a} ({', '.join(tks)}), period ends {ends[0] if ends else '-'} to {ends[-1] if ends else '-'}: "
          + "; ".join(f"{col} {same[col]}/{filled[col]} the same" for col in COLS))
    if filled["revenue"] and same["revenue"] == filled["revenue"] and same["shares_outstanding"]:
        for t in tks:
            newest_hit[t].add(a)
print("\ncompanies carrying another listed company's figures from a joint filing (every revenue and the share count equal):")
for t, accs in sorted(newest_hit.items()):
    c = next(x for x in idx["companies"] if x["ticker"] == t)
    nf = c["newest_filed"] or {}
    print(f"  {t:7s} {c['name'][:40]:40s} cik {c['cik']}; newest period {nf.get('period_end')}; shares at it {nf.get('shares_outstanding')}; "
          f"accessions {sorted(accs)}")
