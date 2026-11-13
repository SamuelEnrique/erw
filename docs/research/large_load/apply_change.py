"""Write a second-pass change into the row it affects: the row's status, date and cites, from the change's own document.

Energy Research Warehouse (ERW), session 5302. A change entry of changes/<group>.json that alters a rule's status (an
approval, a denial, a tariff taking effect) is written into its row in rows/*.json: the status value and date become
the change's, the status cites become the change's cites (each with the change's document address and read date), and
the row's notes record the change and the old status. Makes no request.

    python -I apply_change.py <change group> <change number> <new status>

<change number> counts the group's changes from 1, as changes_<date>.csv numbers them; <new status> is one of the
row statuses (proposed, approved, in effect, denied, withdrawn).
"""

from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATUSES = ("proposed", "approved", "in effect", "denied", "withdrawn")


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[3] not in STATUSES:
        print(__doc__)
        return 2
    cg, n, status = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    cfile = os.path.join(HERE, "changes", f"{cg}.json")
    ch = json.load(open(cfile, encoding="utf-8"))["changes"][n - 1]
    rid = ch["affects"].split()[0]
    for fp in glob.glob(os.path.join(HERE, "rows", "*.json")):
        data = json.load(open(fp, encoding="utf-8"))
        for r in data.get("rows") or []:
            if r.get("row_id") != rid:
                continue
            old = r.get("status") or {}
            cites = []
            for c in ch.get("cites") or []:
                c2 = dict(c)
                c2.setdefault("url", ch.get("source_url"))
                c2.setdefault("date_read", ch.get("date_read"))
                cites.append(c2)
            r["status"] = {"value": status, "date": ch.get("date", ""), "cites": cites}
            r["notes"] = (r.get("notes", "").rstrip() + f" Status updated by the 90-day pass ({cg}-{n:02d}): was "
                          f"'{old.get('value')}' ({old.get('date') or 'date not published'}); {ch.get('what', '')}").strip()
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
                f.write("\n")
            print(f"{rid}: {old.get('value')} {old.get('date')} -> {status} {ch.get('date')}")
            return 0
    print(f"no row {rid}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
