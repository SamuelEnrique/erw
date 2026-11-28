"""Audit of /equities, session 11403: the six companies whose newest capital spending is filed as 0: the concept, the
company's code, and its capital spending over the year-to-date periods before. No request, no write."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = {c["ticker"]: c for c in json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))["companies"]}
for tk in ("BSIN", "EGY", "EONR", "PROP", "HDRN", "SPRU"):
    c = idx[tk]
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    rows = [dict(zip(s["quarterly_columns"], r)) for r in s["quarterly"]]
    cap = [(r["period_end"], r["months"], r["capex"], r["revenue"]) for r in rows if r["capex"] is not None]
    print(f"{tk} {c['name']} SIC {c['sic']} {c['sic_label']}; concept {s['concepts'].get('capex')}; "
          f"newest {c['newest_filed']['capex']} revenue {c['newest_filed']['revenue']}")
    print("   " + "; ".join(f"{e} {m}m capex {v:,} rev {rv if rv is None else f'{rv:,}'}" for e, m, v, rv in cap[:8]))
