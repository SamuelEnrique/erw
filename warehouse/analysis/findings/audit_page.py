#!/usr/bin/env python3
"""The findings audit of 19 November 2026, made into the one file /internal/findings reads (chain 507, session 8900).

Energy Research Warehouse (ERW). Chain 506 audited every draft of docs/findings/ (four checks a draft, "is it already
known?", a second route for the forty on the sheet) and wrote the audit as a document and a folder of CSVs. This script
reads them and writes site/data/findings_audit.json: one row a draft of docs/findings/, keyed by the draft's id in the
review list, with its four checks (passed, fixed, not checked, withdrawn or failed in part, each with its reason), its
verdict, whether it is already known and who printed it, its second route, its tables and their license, and, for the
forty on the sheet, the sheet's rank, reader, risk and the do-file's text. A draft of docs/findings/ the audit has no
row for is written as "not audited", so the file always has a row for every draft (tests/test_session8900_findings_audit.py).

    python warehouse/analysis/findings/audit_page.py [--check]

--check writes nothing and exits 1 when the committed file differs from what the script would write. Reads only files
of this repository; no network, no model, no table.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AUDIT_MD = os.path.join(ROOT, "docs", "reviews", "findings-audit-2026-11-19.md")
AUDIT_DIR = os.path.join(ROOT, "docs", "reviews", "findings-audit-2026-11-19")
SHEET_MD = os.path.join(ROOT, "docs", "reviews", "findings-shortlist-2026-11-19.md")
FINDINGS = os.path.join(ROOT, "docs", "findings")
OUT = os.path.join(ROOT, "site", "data", "findings_audit.json")
GH = "https://github.com/SamuelEnrique/erw/blob/main/"
RAW = "https://raw.githubusercontent.com/SamuelEnrique/erw/main/"

# The verdict words of the audit document, and what the page calls them. A draft whose verdict is in BLOCKED cannot be
# approved at /internal/findings: its figure was not reproduced here, or did not reproduce, or rests on a table that is
# not public.
VERDICT = {
    "passed": "passed",
    "passed after a fix": "passed after a fix",
    "not checked": "not checked",
    "held: internal table, not for the sheet": "held",
    "withdrawn: the figure does not reproduce": "withdrawn",
}
BLOCKED = {
    "not checked": "the figure was not reproduced by the audit of 19 November 2026",
    "held": "the draft rests on a table that is internal or held, so the audit could not reproduce it and it is not for /research",
    "withdrawn": "the figure does not reproduce (the audit of 19 November 2026 withdrew it)",
    "not audited": "the audit of 19 November 2026 has no row for this draft yet",
}
CHECK_NAMES = ["the sentence", "the figure reproduced", "the Stata file read", "the chart"]


def check_state(cell):
    """One check's cell of the audit document: its state and its reason."""
    head, _, why = cell.partition(":")
    head = head.strip()
    state = {"pass": "passed", "fixed": "fixed", "not checked": "not checked", "fail": "withdrawn", "fail in part": "failed in part"}.get(head)
    if state is None:
        raise ValueError(f"a check cell the page does not know: {cell[:60]!r}")
    return {"state": state, "why": why.strip()}


def audit_rows():
    rows = {}
    with open(AUDIT_MD, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\| ([a-z_]+) \| \[([a-z0-9-]+)\]\(", line)
            if not m:
                continue
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) != 11:
                raise ValueError(f"{m.group(2)}: {len(c)} cells, not 11")
            if c[9] not in VERDICT:
                raise ValueError(f"{m.group(2)}: a verdict the page does not know: {c[9]!r}")
            rows[m.group(2)] = {"family": m.group(1), "day": c[2], "checks": [check_state(x) for x in c[4:8]], "changed": c[8], "verdict": VERDICT[c[9]], "known_word": c[10]}
    return rows


def read_csv(name):
    p = os.path.join(AUDIT_DIR, name)
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return {r["slug"]: r for r in csv.DictReader(f)}


def sheet_entries():
    """The sheet of forty: rank, reader, compared with, risk, why it matters, in the sheet's order."""
    text = open(SHEET_MD, encoding="utf-8").read()
    out = []
    for block in re.split(r"\n### ", text)[1:]:
        m = re.match(r"(\d+)\. (.*)", block)
        if not m:
            continue
        rank, title = int(m.group(1)), m.group(2).strip()
        block = block.split("\n## ")[0]

        def field(label):
            fm = re.search(r"^- \*\*" + re.escape(label) + r":\*\* (.*)$", block, re.M)
            return fm.group(1).strip() if fm else ""
        do = re.search(r"docs/findings/([a-z_]+)/([a-z0-9-]+)\.reproduce\.do", block)
        if not do:
            raise ValueError(f"sheet entry {rank}: no do-file")
        out.append({"rank": rank, "title": title, "slug": do.group(2), "family": do.group(1), "reader": field("Reader"),
                    "figure": field("The figure"), "compared": field("Compared with"), "risk": field("The one thing that would make it wrong"),
                    "why": field("Why it matters, as a fact"), "headline": field("A publisher's own headline")})
    if [e["rank"] for e in out] != list(range(1, len(out) + 1)):
        raise ValueError("the sheet's ranks are not 1 to N in order")
    return out


def draft_files():
    """Every draft of docs/findings/: its family, slug, id, title and sentence as the draft's document now says them."""
    out = {}
    for md in sorted(glob.glob(os.path.join(FINDINGS, "*", "*.md"))):
        fam = os.path.basename(os.path.dirname(md))
        slug = os.path.basename(md)[:-3]
        text = open(md, encoding="utf-8").read()
        did = re.search(r"Draft `(scan-[a-z]+-[0-9a-f]{12})`", text)
        if not did:
            continue
        # a withdrawn draft's first line is the audit's one line; its title is the first heading
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), slug)
        sm = re.search(r"\*\*The finding\.\*\* (.*)", text)
        out[slug] = {"family": fam, "slug": slug, "id": did.group(1), "title": title, "sentence": sm.group(1).strip() if sm else ""}
    return out


def tables_of(cell):
    out = []
    for part in cell.split(";"):
        name, _, lic = part.partition("=")
        if name.strip():
            out.append({"name": name.strip(), "license": lic.strip() or "unknown"})
    return out


def known_of(word, row):
    word = word.strip()
    state = {"new as far as found": "new", "known": "known", "known in part": "known in part"}.get(word, "not read yet")
    return {"state": state, "detail": (row or {}).get("detail", "")}


def build():
    audit = audit_rows()
    files = draft_files()
    partc = read_csv("partc.csv")
    route2 = read_csv("route2.csv")
    inv = read_csv("inventory.csv")
    sheet = sheet_entries()
    on_sheet = {e["slug"]: e for e in sheet}
    drafts = {}
    for slug, f in files.items():
        a = audit.get(slug)
        base = f"docs/findings/{f['family']}/{slug}"
        row = {"slug": slug, "family": f["family"], "title": f["title"], "sentence": f["sentence"],
               "files": {"do": f"{base}.reproduce.do", "py": f"{base}.reproduce.py", "md": f"{base}.md", "png": f"{base}.png"}}
        if a is None:
            row.update({"verdict": "not audited", "day": "", "checks": [], "changed": "", "known": {"state": "not read yet", "detail": ""},
                        "route2": None, "tables": tables_of(inv.get(slug, {}).get("licenses", "")), "blocked": BLOCKED["not audited"]})
        else:
            r2 = route2.get(slug)
            row.update({"verdict": a["verdict"], "day": a["day"], "checks": [{"name": CHECK_NAMES[i], **c} for i, c in enumerate(a["checks"])],
                        "changed": a["changed"], "known": known_of(a["known_word"], partc.get(slug)),
                        "route2": {"state": r2["result"], "detail": r2["detail"]} if r2 else None,
                        "tables": tables_of(inv.get(slug, {}).get("licenses", "")), "blocked": BLOCKED.get(a["verdict"], "")})
        e = on_sheet.get(slug)
        if e:
            do_path = os.path.join(ROOT, *row["files"]["do"].split("/"))
            row["sheet"] = {k: e[k] for k in ("rank", "reader", "figure", "compared", "risk", "why", "headline")}
            row["sheet"]["do_text"] = open(do_path, encoding="utf-8").read().replace("\r\n", "\n")
        drafts[f["id"]] = row
    missing = [e["slug"] for e in sheet if e["slug"] not in files]
    if missing:
        raise ValueError(f"on the sheet but not in docs/findings: {missing}")
    counts = {}
    for r in drafts.values():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    known = {}
    for r in drafts.values():
        known[r["known"]["state"]] = known.get(r["known"]["state"], 0) + 1
    return {
        "made_by": "warehouse/analysis/findings/audit_page.py (chain 507, session 8900)",
        "audit": GH + "docs/reviews/findings-audit-2026-11-19.md",
        "sheet_doc": GH + "docs/reviews/findings-shortlist-2026-11-19.md",
        "gh": GH, "raw": RAW,
        "readers": sorted({e["reader"] for e in sheet if e["reader"]}),
        "sheet": [files[e["slug"]]["id"] for e in sheet],
        "counts": dict(sorted(counts.items())),
        "known_counts": dict(sorted(known.items())),
        "drafts": dict(sorted(drafts.items())),
    }


def dump(data):
    """Compact JSON with one draft a line, so a change to one draft is one line of the diff."""
    head = {k: v for k, v in data.items() if k != "drafts"}
    lines = [json.dumps(k, ensure_ascii=False) + ":" + json.dumps(v, ensure_ascii=False, separators=(",", ":")) for k, v in head.items()]
    rows = [json.dumps(k) + ":" + json.dumps(v, ensure_ascii=False, separators=(",", ":")) for k, v in data["drafts"].items()]
    return "{\n" + ",\n".join(lines) + ',\n"drafts":{\n' + ",\n".join(rows) + "\n}}\n"


def main():
    ap = argparse.ArgumentParser(description="The findings audit made into site/data/findings_audit.json (chain 507)")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the committed file differs")
    a = ap.parse_args()
    try:
        data = build()
    except (OSError, ValueError) as e:
        print(f"audit_page: {e}", file=sys.stderr)
        return 2
    text = dump(data)
    if a.check:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if old.replace("\r\n", "\n") != text:
            print("audit_page: site/data/findings_audit.json is not what the audit now says; run the script")
            return 1
        print(f"audit_page: the file agrees ({len(data['drafts'])} drafts)")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"audit_page: {len(data['drafts'])} drafts, {len(data['sheet'])} on the sheet, verdicts {data['counts']}, known {data['known_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
