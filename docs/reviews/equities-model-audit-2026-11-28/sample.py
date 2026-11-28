"""Audit of /equities, session 11403: a company's filed figures against its filing, for a sample drawn at random.

The sample: random.Random(11403).sample of the companies whose filed figures are shown, sorted by ticker, 12 of them.
For each, the newest period's figures as the page prints them (the shortest period to the newest end; debt and shares
at that end), each with its accession and concept. The filings themselves are not on this machine and EDGAR may not be
requested from it, so each figure is checked here only:
  - against the figures of the filings read by chain 701 (docs/reviews/answers-c701-2026-11-26/equities_crosscheck.txt),
    where a company of the sample is among them;
  - by the filing's own arithmetic: a 9-month figure less the 6-month figure of the filing before is the 3-month figure
    filed (the note's rule of 27 November, which the page carries as a note);
  - for sign and size: capital spending a payment (not negative), shares a count, debt not negative.
and is written out as a data request for the main session (the filing's own page, the figure to find).
Also: the five companies chain 701 read in their filings, against the series files now. No request, no write."""
import json
import os
import random
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
shown = sorted(c["ticker"] for c in idx["companies"] if c["fundamentals_status"] == "shown")
sample = random.Random(11403).sample(shown, 12)
print(f"{len(shown)} companies with filed figures; seed 11403; sample of 12: {', '.join(sample)}")


def rows_of(tk):
    c = next(c for c in idx["companies"] if c["ticker"] == tk)
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    return c, s, [dict(zip(s["quarterly_columns"], r)) for r in s["quarterly"]]


def pick(rows, end, months, col):
    best = None
    for r in rows:
        if r["period_end"] == end and (months is None or r["months"] == months) and r[col] is not None:
            if best is None or (r["filed"], r["accession"]) > (best["filed"], best["accession"]):
                best = r
    return best


for tk in sorted(sample):
    c, s, rows = rows_of(tk)
    nf = c["newest_filed"]
    end = nf["period_end"]
    print(f"\n{tk} {c['name']} (SIC {c['sic']}, {';'.join(c['segments'])}); newest {end}, {nf['form']} filed {nf['filed']}")
    print(f"  filing: {nf['url']}")
    print(f"  concepts: {s['concepts']}")
    for col in ("revenue", "net_income", "capex"):
        x = nf[col]
        if not x:
            print(f"  {col}: not filed for the period to {end}")
            continue
        r = pick(rows, end, x["months"], col)
        print(f"  {col}: {x['v']:,} USD over {x['months']} months to {end} (accession {r['accession']})")
        if col == "capex" and x["v"] < 0:
            print("    SIGN: capital spending is negative")
    for col in ("debt", "shares_outstanding"):
        v = nf[col]
        print(f"  {col}: {v:,} at {end}" if v is not None else f"  {col}: not filed at {end}")
        if v is not None and v < 0:
            print("    SIGN: negative")
    # the filing's own arithmetic, for each sum: the longest period less the same-length-minus-3 period of the filing before
    for col in ("revenue", "net_income", "capex"):
        q3 = pick(rows, end, 3, col)
        for m in (6, 9, 12):
            ytd = pick(rows, end, m, col)
            y, mo = int(end[:4]), int(end[5:7]) - 3
            if mo < 1:
                y, mo = y - 1, mo + 12
            prev_end = max((r["period_end"] for r in rows if r["period_end"].startswith(f"{y:04d}-{mo:02d}")), default=None)
            prev = pick(rows, prev_end, m - 3, col) if prev_end else None
            if ytd and prev and q3:
                diff = ytd[col] - prev[col]
                ok = abs(diff - q3[col]) <= 0.01 * max(abs(q3[col]), 1)
                print(f"  {col}: {m} months less the {m - 3} months to {prev_end} = {diff:,}; 3 months filed {q3[col]:,}: "
                      f"{'agree' if ok else 'DIFFER'}")

print("\nThe filings chain 701 read (equities_crosscheck.txt), against the series files now:")
txt = open(os.path.join(ROOT, "docs", "reviews", "answers-c701-2026-11-26", "equities_crosscheck.txt"), encoding="cp1252", errors="replace").read()
after = txt.split("# After the fix")[1]
first = txt.split("# After the fix")[0]
seen = {}
for block in (first, after):
    for m in re.finditer(r"^(\w+) (\d{4}-\d{2}-\d{2}) (\w+) = ([\d,]+) \(us-gaap:(\w+)\); FOUND as '([\d,]+)'", block, re.M):
        seen[(m.group(1), m.group(2), m.group(3))] = (int(m.group(4).replace(",", "")), m.group(5), m.group(6))
for (tk, end, var), (v, concept, as_found) in sorted(seen.items()):
    c, s, rows = rows_of(tk)
    col = "revenue" if var.startswith("revenue") else "shares_outstanding"
    r = pick(rows, end, 3 if col == "revenue" else None, col)
    now = r[col] if r else None
    print(f"  {tk} {end} {col}: the filing printed {as_found} (table {v:,}, {concept}); series file now {now if now is None else f'{now:,}'}"
          f"{'' if now == v else '  <-- DIFFERS'}")
