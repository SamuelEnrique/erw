"""Audit of /equities, session 11403: does each segment hold the companies its SIC rule says, every company checked.

Reads site/data/equities/index.json (as origin/main holds it) and the written rule in warehouse/connectors/sec_edgar.py
(SIC_SEGMENTS, TWO_NOTE, LISTED). Prints every disagreement and the counts. No request, no write."""
import collections
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import sec_edgar as se  # noqa: E402

idx = json.load(open(os.path.join(ROOT, "site", "data", "equities", "index.json"), encoding="utf-8"))
cos = idx["companies"]
print(f"built {idx['built']}; {len(cos)} companies; {len(idx['segments'])} segments")
bad = 0
for c in cos:
    want = se.SIC_SEGMENTS.get(c["sic"])
    if want is None:
        print(f"NOT AN ENERGY CODE: {c['ticker']} sic {c['sic']} {c['sic_label']}")
        bad += 1
        continue
    if c["segments"] != want:
        print(f"SEGMENTS DIFFER: {c['ticker']} sic {c['sic']}: file {c['segments']} rule {want}")
        bad += 1
    note = se.TWO_NOTE.get(c["sic"]) if len(want) > 1 else None
    if (c["segments_note"] or None) != note:
        print(f"NOTE DIFFERS: {c['ticker']} {c['segments_note']!r} rule {note!r}")
        bad += 1
    if c["exchange"] not in se.LISTED:
        print(f"NOT LISTED: {c['ticker']} {c['exchange']}")
        bad += 1
print(f"companies against the rule: {bad} disagree")

n = collections.Counter(s for c in cos for s in c["segments"])
for s in idx["segments"]:
    flag = "" if (s["n_companies"] or 0) == n.get(s["id"], 0) else "  <-- COUNT DIFFERS"
    print(f"  {s['id']:24s} file {s['n_companies']!s:>4s} recount {n.get(s['id'], 0):>4d}{flag}")

by_sic = collections.Counter((c["sic"], c["sic_label"]) for c in cos)
print("companies by SIC code and the SEC's label:")
for (sic, lab), k in sorted(by_sic.items()):
    print(f"  {sic} {lab}: {k}")

labels = collections.defaultdict(set)
for c in cos:
    labels[c["sic"]].add(c["sic_label"])
for sic, ls in labels.items():
    if len(ls) > 1:
        print(f"ONE CODE, TWO LABELS: {sic} {ls}")

cik = collections.Counter(c["cik"] for c in cos)
print("a SEC number twice:", [k for k, v in cik.items() if v > 1])
tk = collections.Counter(c["ticker"] for c in cos)
print("a ticker twice:", [k for k, v in tk.items() if v > 1])
pref = [c for c in cos if "-" in c["ticker"]]
print(f"tickers with a class suffix (a preferred or other class, not the common share): {len(pref)}")
for c in pref:
    print(f"  {c['ticker']:8s} {c['name']} (sic {c['sic']}, {c['exchange']}, {';'.join(c['segments'])})")
print(f"the ones in two segments: {sum(1 for c in cos if len(c['segments']) > 1)}")
print(f"companies with statements shown: {sum(1 for c in cos if c['fundamentals_status'] == 'shown')}")
print(f"companies with a directory_id: {sum(1 for c in cos if c['directory_id'])}")
