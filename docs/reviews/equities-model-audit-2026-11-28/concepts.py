"""Audit of /equities, session 11403: what each statement line holds across companies, as an equity analyst compares them.

For every company with filed figures, its newest period (the page's own rule) and the concept each line was read from
(the series file's `concepts`): counts by concept and segment; the companies a value weighting would lose for want of a
balance-sheet share count; capital spending against revenue over the same year to date, by concept; pairs of companies
that filed the same revenue for the same period (a parent and the partnership it consolidates). No request, no write."""
import collections
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
cos = [c for c in idx["companies"] if c["fundamentals_status"] == "shown"]
ser = {c["ticker"]: json.load(open(os.path.join(D, c["file"]), encoding="utf-8")) for c in cos}


def rows(tk):
    s = ser[tk]
    return [dict(zip(s["quarterly_columns"], r)) for r in s["quarterly"]]


for line in ("revenue", "net_income", "capex", "debt", "shares_outstanding"):
    cnt = collections.Counter((ser[c["ticker"]]["concepts"].get(line) or "none").replace("us-gaap:", "") for c in cos)
    print(f"{line}: " + "; ".join(f"{k} {v}" for k, v in cnt.most_common()))

print("\nThe newest period: a line not filed, by segment (of the companies with filed figures)")
segs = [s["id"] for s in idx["segments"] if s["n_companies"]]
print(f"  {'segment':24s} {'n':>4s} {'rev':>4s} {'ni':>4s} {'capex':>5s} {'debt':>4s} {'shares':>6s}")
for sg in segs:
    cs = [c for c in cos if sg in c["segments"]]
    nf = [c["newest_filed"] for c in cs]
    miss = {k: sum(1 for x in nf if not x[k]) for k in ("revenue", "net_income", "capex", "debt", "shares_outstanding")}
    print(f"  {sg:24s} {len(cs):>4d} {miss['revenue']:>4d} {miss['net_income']:>4d} {miss['capex']:>5d} {miss['debt']:>4d} {miss['shares_outstanding']:>6d}")
allseg = [c for c in idx["companies"]]
noshare = sum(1 for c in cos if not c["newest_filed"]["shares_outstanding"])
print(f"  every segment: {len(idx['companies'])} companies, {len(cos)} with filed figures; with no balance-sheet share count at "
      f"the newest period: {noshare} of {len(cos)}; with no filed figures at all: {len(idx['companies']) - len(cos)}")

print("\nCapital spending against revenue, the newest year to date (the same filing, the same months), by capex concept")
by = collections.defaultdict(list)
for c in cos:
    nf = c["newest_filed"]
    if not nf["capex"]:
        continue
    m = nf["capex"]["months"]
    rv = [r for r in rows(c["ticker"]) if r["period_end"] == nf["period_end"] and r["months"] == m and r["revenue"]]
    if not rv:
        continue
    rv = max(rv, key=lambda r: (r["filed"], r["accession"]))
    ratio = nf["capex"]["v"] / rv["revenue"] if rv["revenue"] else None
    concept = ser[c["ticker"]]["concepts"].get("capex", "").replace("us-gaap:", "")
    by[(c["segments"][0], concept)].append((ratio, c["ticker"], nf["capex"]["v"], rv["revenue"], m))
for (sg, concept), xs in sorted(by.items()):
    xs.sort()
    med = xs[len(xs) // 2][0]
    low = [f"{t} {r:.3f}" for r, t, *_ in xs if r is not None and r < 0.05]
    print(f"  {sg:24s} {concept:48s} n {len(xs):>3d} median {med:.3f}; under 5 percent of revenue: {', '.join(low) or 'none'}")
zero = [c["ticker"] for c in cos if c["newest_filed"]["capex"] and c["newest_filed"]["capex"]["v"] == 0]
print(f"  capital spending filed as exactly 0 at the newest period: {zero}")

print("\nThe same revenue for the same period and months, filed by two companies (one consolidates the other)")
seen = collections.defaultdict(list)
for c in cos:
    nf = c["newest_filed"]
    if nf["revenue"] and nf["revenue"]["v"]:
        seen[(nf["period_end"], nf["revenue"]["months"], nf["revenue"]["v"])].append(c)
for (end, m, v), cs in seen.items():
    if len(cs) > 1:
        print(f"  {end} {m} months {v:,}: " + "; ".join(f"{c['ticker']} ({c['name']}, {';'.join(c['segments'])})" for c in cs))
