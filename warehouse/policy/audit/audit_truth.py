#!/usr/bin/env python3
"""Session 157: the place each sampled policy action concerns, as a file code can read, for both audit samples.

Energy Research Warehouse (ERW). The audits of sessions 154 and 157 read 100 policy actions against their source
documents. For the field `states` a person read each document and wrote a class with the source's words
(audit_findings.py STATES, audit_findings_s157.py STATES). This tool writes the same judgment as two-letter codes,
one line a row, so that a rule that reads the place from the printed document can be tested against it:

  sample, draw, event_id, fr_document_number, row_states (what the table holds), true_states (the states where the
  project, plant or plan the action concerns is, as the document says it, ";"-joined and sorted; empty when the
  document names none), cls, source_words, title_cut (yes or no), full_title

The standard is session 154's: a contact's address, a filing room, Washington, DC and a state that stands only in a
company's name do not count. One exception session 154 made and this file keeps, flagged in source_words: draw 7 of
sample 154, where the licensee's name is the only place the document names the state and the plants are in it.

title_cut: a Federal Register row whose title in the Register's API record is shorter than the printed document's
own title and is its beginning (the record cuts the title; the row holds the record's). full_title is then the
printed title. Settled by code from the two saved files of each document; no request is made here.

    python warehouse/policy/audit/audit_truth.py --audit 154=C:/.../runs/session154/audit \
        --audit 157=C:/.../runs/session157/audit --out warehouse/policy/eval/audit_states_truth.csv
"""

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "connectors")))

COLS = ["sample", "draw", "event_id", "fr_document_number", "row_states", "true_states", "cls", "source_words",
        "title_cut", "full_title"]


def title_cut(api_title, printed_title):
    """The record's title is the beginning of a longer printed title."""
    import audit_check as check
    a = check.loose(api_title).rstrip(";,: ")
    p = check.loose(printed_title)
    return bool(a) and len(p) > len(a) + 3 and p.startswith(a) and check.loose(api_title) != p


def printed_title(body, head):
    """The printed document's whole title. Where the heading block ends in a semicolon, a comma or a colon (the
    Register's record stops there: 'Gulf South Pipeline Company, LLC;' in 2026-17632), the title goes on in the
    print as the first indented paragraph of the next block, up to the next indented line, where the text begins."""
    import audit_check as check
    if not head or head.rstrip()[-1:] not in ";,:":
        return head
    blocks = [b for b in re.split(r"\n\s*\n", body) if b.strip()]
    k = next((i for i, b in enumerate(blocks) if check.ws(b) == head), None)
    if k is None or k + 1 >= len(blocks):
        return head
    lines = blocks[k + 1].split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    more = []
    for j, ln in enumerate(lines):
        if j and re.match(r"\s{2,}\S", ln):   # the next indented line: the text begins
            break
        more.append(ln)
    return check.ws(head + " " + " ".join(more))


def rows_of(label, folder, truth):
    import audit_check as check
    import policy_sources as ps
    with open(os.path.join(folder, "sample.csv"), encoding="utf-8") as f:
        sample = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    with open(os.path.join(folder, "findings.csv"), encoding="utf-8") as f:
        states = {r["event_id"]: r for r in csv.DictReader(f) if r["field"] == "states"}
    with open(os.path.join(folder, "manifest.csv"), encoding="utf-8") as f:
        doc = {(m["key"], m["kind"]): m for m in csv.DictReader(f) if m["status"] in ("200", "held")}
    out = []
    for s in sample:
        n, eid = int(s["draw"]), s["event_id"]
        st = states[eid]
        if n not in truth:
            raise RuntimeError(f"sample {label} draw {n}: no true_states written")
        true = ";".join(sorted(x for x in truth[n].split(";") if x))
        # the class and the codes must say the same thing
        held = ";".join(sorted(x for x in st["row_value"].split(";") if x))
        fits = {"correct": held == true and true != "", "source_silent": true == "" and held == "",
                "missing": held == "" and true != "", "wrong": held != "" and true != "" and held != true,
                "not_in_source": held != "" and true == "", "not_reachable": True}
        if not fits.get(st["cls"], False):
            raise RuntimeError(f"sample {label} draw {n}: class {st['cls']} does not fit held '{held}' and true '{true}'")
        cut, full, num = "no", "", ""
        if eid.startswith("federalregister:"):
            num = eid.split(":", 1)[1]
            a, t = doc.get((eid, "api")), doc.get((eid, "text"))
            if a and t:
                with open(os.path.join(folder, a["file"]), encoding="utf-8") as f:
                    api = json.load(f)
                with open(os.path.join(folder, t["file"]), encoding="utf-8", errors="replace") as f:
                    text = check.fr_text(f.read())
                p = check.fr_parse(text, [x.get("raw_name") or "" for x in api.get("agencies") or []]
                                   + [x.get("name") or "" for x in api.get("agencies") or []])
                whole = printed_title(p["body"], p["title"])
                if title_cut(ps.clean(api.get("title")), whole):
                    cut, full = "yes", whole
            else:
                cut = "not reachable"
        out.append(dict(sample=label, draw=n, event_id=eid, fr_document_number=num, row_states=st["row_value"],
                        true_states=true, cls=st["cls"], source_words=re.sub(r"\s+", " ", st["source_words"]),
                        title_cut=cut, full_title=full))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: the states truth file")
    ap.add_argument("--audit", action="append", required=True, help="LABEL=FOLDER, the audit folder of a sample")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    import audit_findings_s157 as F7
    truths = {"154": F7.TRUE_STATES_154, "157": getattr(F7, "TRUE_STATES", {})}
    rows = []
    for item in args.audit:
        label, folder = item.split("=", 1)
        rows += rows_of(label, folder, truths[label])
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for label in sorted({r["sample"] for r in rows}):
        d = [r for r in rows if r["sample"] == label]
        print(f"sample {label}: {len(d)} rows; a state in the document {sum(1 for r in d if r['true_states'])}; "
              f"the row differs {sum(1 for r in d if r['cls'] in ('missing', 'wrong', 'not_in_source'))}; "
              f"title cut {sum(1 for r in d if r['title_cut'] == 'yes')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
