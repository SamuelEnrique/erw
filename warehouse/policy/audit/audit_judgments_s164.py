#!/usr/bin/env python3
"""Session 164: what the agent read, written down. The changed values of the 100 audited policy actions, each classed.

Energy Research Warehouse (ERW). audit_recheck_s164.py settles by code what code can settle. Every other value that
changed since sessions 154 and 157 read it was read again by session 164's agent (an AI research agent, as the two
audits' readers were) against the words of its source that the row and its evidence hold: the title, the Register's
summary, the first paragraph of the printed text (policy_actions) and, for an impact read, the spans the reader kept,
each proved word for word in the source text by the reader's own code (policy_reads_evidence). This file is that
reading: the rule is "supported unless named below", and every exception is named with the words it rests on. It
writes warehouse/policy/eval/audit_s164_judgments.csv (event_id, field, cls, words), which audit_recheck_s164.py reads.
No request, no model call, no table written. A value this file does not class stays "not read again".

The worksheets the agent read are runs/session164/audit/worksheet_model.txt and worksheet_reads.txt (the data
machine, not in git).

    python warehouse/policy/audit/audit_judgments_s164.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output
"""

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit_recheck_s164 as R  # noqa: E402

FR = "federalregister:"
HYDRO = ("the kind (hydropower) is read off FERC's project docket and the word license; the notice's held text names "
         "the project and not its kind. True of every FERC project licence, and not in the source's words: a judgment")
ANNUAL = ("'annual' and 'while relicensing proceeds' are what a notice of authorization for continued project operation "
          "does under the Federal Power Act; the one sentence of it the row holds says only when the license ended: a judgment")
# (event id, field): (class, the words it rests on). Everything else read is supported.
NAMED = {
    (FR + "2026-08214", "why"): ("unsupported", "'Small' and 'incremental' are not in the text, which gives a 48-inch header 'capable of wheeling up to "
                                 "5,000,000 dekatherms per day', 'a 2.5 billion cubic feet per day meter station' to the Golden Pass terminal and a cost of "
                                 "'approximately $39,000,000'"),
    (FR + "2026-05188", "why"): ("unsupported", "'Maine' is in neither the title nor the first paragraph (the row holds no place); the rest (two hydro "
                                 "projects, 37.5 and 67.9 megawatts, a revised schedule) is in the text"),
    (FR + "2026-07656", "why"): ("judgment", HYDRO),
    (FR + "2026-12333", "why"): ("judgment", HYDRO),
    (FR + "2026-09301", "why"): ("judgment", ANNUAL),
    (FR + "2026-05427", "why"): ("judgment", ANNUAL),
    (FR + "2026-12713", "why"): ("judgment", ANNUAL),
    (FR + "2026-07656", "sector"): ("judgment", HYDRO),
    (FR + "2026-18359", "sector"): ("judgment", HYDRO),
    (FR + "2026-12333", "sector"): ("judgment", HYDRO),
    (FR + "2026-07656", "sector_tags"): ("judgment", HYDRO),
    (FR + "2026-18359", "sector_tags"): ("judgment", HYDRO),
    (FR + "2026-12333", "sector_tags"): ("judgment", HYDRO),
    (FR + "2025-22120", "sector_tags"): ("supported", "Moomaws Dam Hydroelectric Project: renewables as before; power is added for a hydroelectric project, which generates power"),
    (FR + "2026-09919", "sector_tags"): ("supported", "R.J. Fortier Hydropower, Inc.: renewables as before; power is added for a hydropower project"),
    (FR + "2026-13550", "sector_tags"): ("supported", "hydrogen (read off hydrogen chloride) is gone; emissions, which the audit found right, stays"),
    (FR + "2026-13027", "abstract"): ("correct", "set against the Register's own record saved by the audit: the row's summary now differs from it only by the "
                                      "subscript markup around the X of NOX; the 'NO X' fault is gone"),
    (FR + "2026-03937", "abstract"): ("correct", "set against the Register's own record saved by the audit: the row's summary now differs from it only by the "
                                      "subscript markup around the X of NOX; the 'NO X' fault is gone"),
    (FR + "2026-08276", "affected_states"): ("missing", "the read held NY and now holds none; its own kept span says 'NMP1 is located in Oswego County, New York.'"),
    (FR + "2026-08276", "affected_isos"): ("judgment", "NYISO is inferred from New York; the notice names no grid operator (the audits classed such an inference a judgment)"),
    ("doe:52f19d96fc84", "affected_sectors"): ("unsupported", "'transmission' stands in the release only in a company's name (Tri-State Generation and Transmission "
                                               "Association); the order keeps a coal unit available to run. coal is supported"),
}
DEFAULT = {
    "why": "read against the title and the first paragraph or summary the row holds: every particular of the line is in them",
    "sector": "read against the title and the first paragraph or summary the row holds, which name the project's or the rule's kind",
    "what_changes": "read against the spans the reader kept for this field, each found word for word in the source text by the reader's code",
    "plain_read": "read against the spans the reader kept for this field, each found word for word in the source text by the reader's code",
    "timeline": "read against the spans the reader kept for this field: each date and step of the line is in them",
    "affected_sectors": "each sector named is in the summary or in a kept span",
}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: session 164's reading of the changed values")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out", default=os.path.join(R.EVAL, R.JUDGMENTS))
    a = ap.parse_args(argv)
    df, _, _, _ = R.run(a.in_dir, judged={})   # from scratch: what code alone settles, before any reading
    # a value named below is written whatever the code would say of it (the reading wins over a rule of thumb, as where
    # a read's list of states is now empty and the source names a state); the rest are the values code could not settle
    changed = df[df["changed"] == "yes"]
    rows, left = [], []
    for _, x in changed.iterrows():
        key = (x["event_id"], x["field"])
        if key in NAMED:
            rows.append({"event_id": key[0], "field": key[1], "cls": NAMED[key][0], "words": NAMED[key][1]})
        elif x["cls_now"] != R.NOT_READ:
            continue
        elif x["field"] in DEFAULT:
            rows.append({"event_id": key[0], "field": key[1], "cls": "supported", "words": DEFAULT[x["field"]]})
        else:
            left.append(key)
    unused = [k for k in NAMED if k not in {(r["event_id"], r["field"]) for r in rows}]
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event_id", "field", "cls", "words"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    by = {}
    for r in rows:
        by[(r["field"], r["cls"])] = by.get((r["field"], r["cls"]), 0) + 1
    print(f"{len(rows)} values classed by reading -> {a.out}")
    for k in sorted(by):
        print(f"  {k[0]}: {k[1]} {by[k]}")
    print(f"left not read again: {len(left)} {left[:5]}")
    print(f"named and not needed: {unused}")
    return 1 if unused else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
