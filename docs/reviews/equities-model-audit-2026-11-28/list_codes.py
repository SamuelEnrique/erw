"""List the companies of the codes named on the command line (index.json), one line each. No request, no write."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
idx = json.load(open(os.path.join(ROOT, "site", "data", "equities", "index.json"), encoding="utf-8"))
for c in idx["companies"]:
    if c["sic"] in sys.argv[1:]:
        nf = c.get("newest_filed") or {}
        rev = (nf.get("revenue") or {})
        print(f"{c['sic']} {c['ticker']:7s} {c['name'][:44]:44s} {c['exchange']:6s} cik {c['cik']} fund {c['fundamentals_status']:13s} "
              f"newest {nf.get('period_end')} rev {rev.get('v')} ({rev.get('months')}m)")
