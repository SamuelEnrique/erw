"""Audit of /equities, session 11403: one choice of the segment rule changed at a time, measured on the list.

- 4911 in both regulated utilities and independent power; 2911 in both integrated and refining: the segments' overlap.
- Each segment's 3-month revenue for the quarter to 30 September 2026 summed over the companies that filed it, and the
  part of that sum that is counted twice (a company and the company that consolidates it, both listed in the segment).
- The companies a segment holds with no filed figures (foreign filers, mostly), and their share.
No request, no write."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
idx = json.load(open(os.path.join(ROOT, "site", "data", "equities", "index.json"), encoding="utf-8"))
cos = idx["companies"]
seg = {s["id"]: [c for c in cos if s["id"] in c["segments"]] for s in idx["segments"]}
both = lambda a, b: {c["ticker"] for c in seg[a]} & {c["ticker"] for c in seg[b]}
print(f"regulated utilities {len(seg['regulated_utilities'])}, independent power {len(seg['independent_power'])}, in both "
      f"{len(both('regulated_utilities', 'independent_power'))}; independent power by its own code alone (4991): "
      f"{[c['ticker'] for c in seg['independent_power'] if c['sic'] == '4991']}")
print(f"integrated {len(seg['integrated_oil_gas'])}, refining {len(seg['refining'])}, in both {len(both('integrated_oil_gas', 'refining'))}")
print(f"midstream {len(seg['midstream_pipelines'])}, regulated {len(seg['regulated_utilities'])}, in both "
      f"{len(both('midstream_pipelines', 'regulated_utilities'))}")
distinct = {frozenset(c['ticker'] for c in v) for v in seg.values() if v}
print(f"segments holding a company: {sum(1 for v in seg.values() if v)}; distinct sets of companies among them: {len(distinct)}")

# parent and consolidated company, both listed (from pairs.py and shared.py): the second's revenue is inside the first's
TWICE = [("PAGP", "PAA"), ("SUNC", "SUN"), ("CMS", "CMS-PB"), ("EIX", "SCE-PG"), ("PCG", "PCG-PE")]
print("\n3-month revenue to 2026-09-30, summed by segment, and the part counted twice:")
for sid, cs in seg.items():
    if not cs:
        continue
    q = {c["ticker"]: c["newest_filed"]["revenue"]["v"] for c in cs
         if c.get("newest_filed") and c["newest_filed"]["period_end"] == "2026-09-30" and c["newest_filed"]["revenue"]
         and c["newest_filed"]["revenue"]["months"] == 3}
    total = sum(q.values())
    twice = sum(q[b] for a, b in TWICE if a in q and b in q)
    nofig = sum(1 for c in cs if c["fundamentals_status"] != "shown")
    print(f"  {sid:24s} {len(cs):>3d} companies, {len(q):>3d} with a 3-month revenue to 30 September: USD {total / 1e9:,.1f} billion; "
          f"counted twice {twice / 1e9:,.1f} billion ({twice / total * 100 if total else 0:.1f} percent); no filed figures {nofig} "
          f"({nofig / len(cs) * 100:.0f} percent)")
big = sorted((c for c in seg["midstream_pipelines"] if c.get("newest_filed") and c["newest_filed"]["revenue"]),
             key=lambda c: -c["newest_filed"]["revenue"]["v"])[:6]
print("midstream's largest revenues: " + "; ".join(f"{c['ticker']} {c['newest_filed']['revenue']['v'] / 1e9:.1f} ({c['sic']} {c['sic_label']})" for c in big))
