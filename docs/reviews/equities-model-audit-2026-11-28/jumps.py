"""Audit of /equities, session 11403: each company's balance-sheet share count, period end by period end (the later
filing where a period was filed twice): where it moves by more than half between two period ends a quarter or so apart,
the two counts and their filings. A subsidiary that took its parent's figures shows its parent's count. Also SCE-PG's
whole share count line. No request, no write."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
n = 0
for c in idx["companies"]:
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    best = {}
    for r in s["quarterly"]:
        r = dict(zip(s["quarterly_columns"], r))
        if r["shares_outstanding"] is None:
            continue
        k = r["period_end"]
        if k not in best or (r["filed"], r["accession"]) > (best[k]["filed"], best[k]["accession"]):
            best[k] = r
    ends = sorted(best)
    if c["ticker"] == "SCE-PG":
        print("SCE-PG share count: " + "; ".join(f"{e} {best[e]['shares_outstanding']:,} ({best[e]['accession']})" for e in ends[-6:]))
    for a, b in zip(ends, ends[1:]):
        x, y = best[a]["shares_outstanding"], best[b]["shares_outstanding"]
        if a >= "2025-01-01" and x and y and (y / x > 1.5 or y / x < 1 / 1.5):
            n += 1
            print(f"  {c['ticker']:7s} {a} {x:,} ({best[a]['form']} {best[a]['accession']}) to {b} {y:,} ({best[b]['form']} {best[b]['accession']})")
print(f"share counts moving by more than half between two period ends since 2025: {n}")
