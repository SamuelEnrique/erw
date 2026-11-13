"""Write the second and third passes' CSVs: changes_<date>.csv and legislation_<date>.csv.

Energy Research Warehouse (ERW), session 5300. Reads docs/research/large_load/changes/*.json and legislation/*.json
(after verify_quotes.py) and writes one CSV each, in the README's forms. Makes no request.

    python -I build_passes.py --date 2026-11-13
"""

from __future__ import annotations

import argparse
import csv
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_csv import cite_text  # noqa: E402

CHANGE_COLS = ["change_id", "group", "utility", "state", "rule_name", "affects", "change", "date", "docket", "what",
               "cite", "source_url", "source_title", "date_read", "license", "license_basis"]
LAW_COLS = ["law_id", "group", "state", "bill", "session", "title", "status", "status_date", "effective_date",
            "status_cite", "threshold_mw", "threshold_mw_cite", "requirements", "source_url", "source_title",
            "date_read", "license", "notes"]


def write(path, cols, rows, head):
    buf = io.StringIO()
    for line in head:
        buf.write("# " + line + "\n")
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    print(f"wrote {path}: {len(rows)} rows")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    changes = []
    for fp in sorted(glob.glob(os.path.join(HERE, "changes", "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        g = d.get("group") or os.path.basename(fp)[:-5]
        for i, c in enumerate(d.get("changes") or [], 1):
            src = c.get("source_url", "")
            changes.append({
                "change_id": f"{g}-{i:02d}", "group": g, "utility": c.get("utility", ""), "state": c.get("state", ""),
                "rule_name": c.get("rule_name", ""), "affects": c.get("affects", ""), "change": c.get("change", ""),
                "date": c.get("date", "") or "not published", "docket": c.get("docket", "") or "not published",
                "what": c.get("what", ""), "cite": " | ".join(cite_text(x, src) for x in c.get("cites") or []),
                "source_url": src, "source_title": c.get("source_title", ""), "date_read": c.get("date_read", ""),
                "license": c.get("license", ""), "license_basis": c.get("license_basis", ""),
            })
    if changes:
        write(os.path.join(HERE, f"changes_{a.date}.csv"), CHANGE_COLS, changes, [
            f"US utilities' large-load rules: what changed in the 90 days to {a.date} (ERW, session 5300 upward, "
            "portable laptop window P4).",
            "One row a change, each printed in the document its cite names. Method: docs/research/large_load/README.md."])
    laws = []
    for fp in sorted(glob.glob(os.path.join(HERE, "legislation", "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        g = d.get("group") or os.path.basename(fp)[:-5]
        for i, law in enumerate(d.get("laws") or [], 1):
            src = law.get("source_url", "")
            tm = law.get("threshold_mw") or {}
            reqs = []
            for q in law.get("requirements") or []:
                cites = " | ".join(cite_text(x, src) for x in q.get("cites") or [])
                reqs.append(f"{q.get('topic', '')}: {q.get('value', '')} [{cites}]")
            laws.append({
                "law_id": f"{g}-{i:02d}", "group": g, "state": law.get("state", ""), "bill": law.get("bill", ""),
                "session": law.get("session", ""), "title": law.get("title", ""), "status": law.get("status", ""),
                "status_date": law.get("status_date", "") or "not published",
                "effective_date": law.get("effective_date", "") or "not published",
                "status_cite": " | ".join(cite_text(x, src) for x in law.get("cites") or []),
                "threshold_mw": tm.get("value", "") or "not published",
                "threshold_mw_cite": " | ".join(cite_text(x, src) for x in tm.get("cites") or [])
                if tm.get("value") != "not published" else (f"searched: {tm['searched']}" if tm.get("searched") else ""),
                "requirements": " || ".join(reqs), "source_url": src, "source_title": law.get("source_title", ""),
                "date_read": law.get("date_read", ""), "license": law.get("license", ""), "notes": law.get("notes", ""),
            })
    if laws:
        write(os.path.join(HERE, f"legislation_{a.date}.csv"), LAW_COLS, laws, [
            f"US states' large-load laws and bills of the 2025 and 2026 sessions, read {a.date} (ERW, session 5300 upward, "
            "portable laptop window P4).",
            "One row a law or bill, each value read in the legislature's own text. Method: docs/research/large_load/README.md."])
    return 0


if __name__ == "__main__":
    sys.exit(main())
