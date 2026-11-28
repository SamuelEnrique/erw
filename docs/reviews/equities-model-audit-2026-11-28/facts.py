"""Audit of /equities, session 11403: a few facts the audit's words rest on (no request, no write): the SIC of named
companies; EIX's share count at 30 June 2014; the newest accession of the six companies with a capital spending of 0."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = {c["ticker"]: c for c in json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))["companies"]}
for tk in ("VST", "NRG", "CEG", "TLN", "DUK", "SO", "NEE", "AES"):
    c = idx.get(tk)
    print(tk, (c["sic"], c["sic_label"], c["segments"]) if c else "not in the list")
s = json.load(open(os.path.join(D, idx["EIX"]["file"]), encoding="utf-8"))
for r in s["quarterly"]:
    r = dict(zip(s["quarterly_columns"], r))
    if r["period_end"].startswith("2014-06") and r["shares_outstanding"]:
        print("EIX 2014-06", r["shares_outstanding"], r["accession"])
for tk in ("BSIN", "EGY", "EONR", "PROP", "HDRN", "SPRU"):
    nf = idx[tk]["newest_filed"]
    s = json.load(open(os.path.join(D, idx[tk]["file"]), encoding="utf-8"))
    accs = sorted({r[12] for r in s["quarterly"] if r[1] == nf["period_end"]})
    print(tk, nf["period_end"], nf["form"], accs)
s = json.load(open(os.path.join(D, idx["EGY"]["file"]), encoding="utf-8"))
print("EGY 2025:", sorted({(r[1], r[12]) for r in s["quarterly"] if r[1] in ("2025-06-30", "2025-09-30")}))
