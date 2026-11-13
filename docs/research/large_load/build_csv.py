"""Write the large-load research CSV from the checked rows.

Energy Research Warehouse (ERW), session 5300. Reads docs/research/large_load/rows/*.json (the rows after
verify_quotes.py and the spot-check) and writes docs/research/large_load/utilities_<date>.csv, one row a rule.
Makes no request. A cite is written as `p. 4, Section C: "the words"`; a cite from another document than the row's
source_url starts with that document's address and the day it was read.

    python -I build_csv.py --date 2026-11-13
"""

from __future__ import annotations

import argparse
import csv
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ("threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
          "connection_timeline", "queue_size")
GROUP_ORDER = ("dominion", "southern_florida", "aep", "entergy", "texas", "duke", "southwest_california", "pjm_east",
               "northwest_mountain", "xcel_plains", "ameren_evergy_spp", "tva_southeast", "great_lakes", "northeast")
COLUMNS = (["row_id", "group", "utility", "state", "iso_region", "rule_name", "docket", "docket_cite", "status",
            "status_date", "status_cite"]
           + [c for f in FIELDS for c in (f, f + "_cite")]
           + ["source_url", "source_title", "date_read", "quoted_clause", "license", "license_basis", "erw_overlap",
              "notes_file", "notes"])


def slug(s: str) -> str:
    s = re.sub(r"\(.*?\)", " ", s or "")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:60] or "unknown"


def slug_for(name: str, given: str = "") -> str:
    """The notes file's slug: the row's own notes_slug, else notes_slugs.json's entry for the name, else the name's."""
    if given:
        return given
    try:
        table = json.load(open(os.path.join(HERE, "notes_slugs.json"), encoding="utf-8"))
    except FileNotFoundError:
        table = {}
    return table.get(name) or slug(name)


def cite_text(c: dict, src: str) -> str:
    where = []
    if c.get("page") not in (None, ""):
        where.append(f"p. {c['page']}")
    if c.get("section"):
        where.append(str(c["section"]))
    loc = ", ".join(where) or "the document"
    url = c.get("url")
    head = f"{url} (read {c.get('date_read', 'date not stamped')}) " if url and url != src else ""
    return f'{head}{loc}: "{c.get("quote", "")}"'


def cites_text(v, src: str) -> str:
    if not isinstance(v, dict):
        return ""
    if (v.get("value") or "").strip().lower() == "not published":
        return f"searched: {v.get('searched', 'not stated')}" if v.get("searched") else ""
    return " | ".join(cite_text(c, src) for c in v.get("cites") or [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--rows", default=os.path.join(HERE, "rows"))
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.rows, "*.json")),
                   key=lambda p: (GROUP_ORDER.index(os.path.basename(p)[:-5])
                                  if os.path.basename(p)[:-5] in GROUP_ORDER else 99, p))
    out_rows = []
    for fp in files:
        data = json.load(open(fp, encoding="utf-8"))
        group = data.get("group") or os.path.basename(fp)[:-5]
        for i, r in enumerate(data.get("rows") or [], 1):
            src = r.get("source_url", "")
            st = r.get("status") or {}
            dk = r.get("docket") or {}
            qc = r.get("quoted_clause") or {}
            rec = {
                "row_id": f"{group}-{i:02d}",
                "group": group,
                "utility": r.get("utility", ""),
                "state": r.get("state", ""),
                "iso_region": r.get("iso_region", ""),
                "rule_name": r.get("rule_name", ""),
                "docket": dk.get("value", "") if isinstance(dk, dict) else str(dk),
                "docket_cite": cites_text(dk, src),
                "status": st.get("value", ""),
                "status_date": st.get("date", "") or "not published",
                "status_cite": cites_text(st, src),
                "source_url": src,
                "source_title": r.get("source_title", ""),
                "date_read": r.get("date_read", ""),
                "quoted_clause": cite_text(qc, src) if qc.get("quote") else "",
                "license": r.get("license", ""),
                "license_basis": r.get("license_basis", ""),
                "erw_overlap": r.get("erw_overlap", "") or "none",
                "notes_file": f"notes/{slug_for(r.get('utility', ''), r.get('notes_slug') or '')}.md",
                "notes": r.get("notes", ""),
            }
            for f in FIELDS:
                v = (r.get("fields") or {}).get(f) or {}
                rec[f] = v.get("value", "")
                rec[f + "_cite"] = cites_text(v, src)
            out_rows.append(rec)
    buf = io.StringIO()
    buf.write(f"# US utilities' large-load connection rules, research pass of {a.date} (ERW, session 5300, "
              f"portable laptop window P4).\n")
    buf.write("# One row a rule. Every value is printed in the document its cite names (URL, page or section, the "
              "words); 'not published' means the documents read do not state it; 'held: <registry>/<file>' means "
              "window A's registry already holds the same value. Method: docs/research/large_load/README.md.\n")
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    for rec in out_rows:
        w.writerow(rec)
    path = os.path.join(HERE, f"utilities_{a.date}.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    print(f"wrote {path}: {len(out_rows)} rows from {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
