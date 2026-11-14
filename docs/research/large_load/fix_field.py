"""Correct one field of one row from the audit, with the document's own words, and check the words before saving.

Energy Research Warehouse (ERW), session 5304. A finding of the independent audit (audit_<date>.md) is applied here:
the field's value and cites are replaced, the old value is kept in the row's notes with the finding's number, and the
new quote must be found on its cited page of the cached copy (verify_quotes.find) or nothing is written. Makes no
request.

    python -I fix_field.py <row_id> <field> --value "..." --page N --quote "..." [--url URL] [--section S]
           [--add] [--finding A-03]
    python -I fix_field.py <row_id> <field> --not-published "what was read" [--finding A-03]
    python -I fix_field.py <row_id> status --status "in effect" --date YYYY-MM-DD --page N --quote "..." [--url URL]

<field> is one of the eight fields, docket, or status. --add keeps the field's cites and adds the new one (for a
value made more exact); without it the cites are replaced.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_quotes import FIELDS, find, load_doc  # noqa: E402

STATUSES = ("proposed", "approved", "in effect", "denied", "withdrawn")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("row_id")
    ap.add_argument("field")
    ap.add_argument("--value")
    ap.add_argument("--page")
    ap.add_argument("--section", default="")
    ap.add_argument("--quote")
    ap.add_argument("--url")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--not-published", dest="not_published")
    ap.add_argument("--status")
    ap.add_argument("--date", default="")
    ap.add_argument("--finding", default="")
    a = ap.parse_args()
    if a.field not in FIELDS + ("docket", "status"):
        print("unknown field")
        return 2
    for fp in glob.glob(os.path.join(HERE, "rows", "*.json")):
        data = json.load(open(fp, encoding="utf-8"))
        for r in data.get("rows") or []:
            if r.get("row_id") != a.row_id:
                continue
            src = r.get("source_url")
            if a.field == "status":
                old = r.get("status") or {}
            elif a.field == "docket":
                old = r.get("docket") or {}
            else:
                old = (r.get("fields") or {}).get(a.field) or {}
            if a.not_published is not None:
                new = {"value": "not published", "searched": a.not_published}
            else:
                if not (a.quote and a.page):
                    print("a value needs --page and --quote")
                    return 2
                url = a.url or src
                doc = load_doc(url)
                if not doc:
                    print(f"no cached copy of {url}: nothing written")
                    return 1
                kind, detail = find(a.quote, doc[0], doc[1], a.page)
                if kind not in ("exact", "nospace"):
                    print(f"the quote is not on p.{a.page} of the copy ({kind}: {detail}): nothing written")
                    return 1
                cite = {"page": str(a.page), "section": a.section, "quote": a.quote}
                if a.url and a.url != src:
                    cite["url"] = a.url
                    cite["date_read"] = doc[0].get("date_read")
                cites = (list(old.get("cites") or []) if a.add else []) + [cite]
                if a.field == "status":
                    if a.status not in STATUSES:
                        print("a status needs --status, one of " + ", ".join(STATUSES))
                        return 2
                    new = {"value": a.status, "date": a.date, "cites": cites}
                else:
                    new = {"value": a.value, "cites": cites}
            if a.field == "status":
                r["status"] = new
            elif a.field == "docket":
                r["docket"] = new
            else:
                r["fields"][a.field] = new
            was = old.get("value", "")
            if a.field == "status":
                was = f"{old.get('value')} {old.get('date', '')}".strip()
            r["notes"] = (r.get("notes", "").rstrip() + f" Corrected by the independent audit of session 5304"
                          f"{' (' + a.finding + ')' if a.finding else ''}: {a.field} was '{was}'.").strip()
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
                f.write("\n")
            print(f"{a.row_id} {a.field}: '{str(was)[:80]}' -> '{new.get('value')}'")
            return 0
    print(f"no row {a.row_id}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
