#!/usr/bin/env python3
"""US utilities' large-load rules, their changes since August 2026 and the states' laws, from the research pass of 13 and
14 November 2026 (session 3937, chain 267; the data requests of docs/state/data_requests_large_load.md, rows 1, 15, 16).

Energy Research Warehouse (ERW). Writes three events tables:

    warehouse/output/utility_large_load_rules.csv         one row a utility's (or a state commission's) large-load rule
    warehouse/output/utility_large_load_rule_changes.csv  one row a filing, order, effective date, amendment, denial,
                                                          suspension or hearing on such a rule, 15 August to 13 November 2026
    warehouse/output/state_large_load_laws.csv            one row a state law or bill of the 2025 and 2026 sessions

What it is made from. Window P4 of the portable laptop (sessions 5300 to 5304) read each document a row names through
docs/research/large_load/fetch_doc.py (robots first, Anthropic's agents by name included; the paused publishers and the
barred hosts refused) and wrote docs/research/large_load/utilities_2026-11-13.csv (122 rows, 1,699 cites matched, every
row read by five auditors: audit_2026-11-14.md), changes_2026-11-13.csv (98 rows, 364 cites) and
legislation_2026-11-13.csv (28 rows, 295 cites). Every value is printed in the document its cite names. This script makes
no request and no model call: it reads the three files as committed and reshapes them.

The license, row by row (the files' license column; the owner's ruling 4 of 6 November 2026). A table has one license,
so only the rows marked public are written, as utility_large_load_tariffs writes only its public schedules; a row whose
only source asks written permission or allows personal use only is held, not written, and named in the header. In a
public row of the rules, the fields its internal_fields names (those resting only on such a host) are left empty with
their cites, and x_withheld names them.

Cells as the files mean them. "held: <registry>/<file>" is a pointer to the ERW's own registry, not a value: the cell is
left empty and the pointer kept in x_held. "not published" means the documents read do not state the value, and is
written as printed. The ISO or region column is the ERW's classification (x_iso_region), not a cited value. mw is left
empty: every size the files hold is a phrase, not a single number.

    python warehouse/connectors/large_load_research.py              # the three tables (data lock)
    python warehouse/connectors/large_load_research.py --out-dir D  # a trial
    python warehouse/connectors/large_load_research.py --check      # read and check; write nothing

Method: docs/methods/large_load_research.md; the research's own method docs/research/large_load/README.md.
"""
import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESEARCH = os.path.join(ROOT, "docs", "research", "large_load")
FILES = {"rules": "utilities_2026-11-13.csv", "changes": "changes_2026-11-13.csv", "laws": "legislation_2026-11-13.csv"}
NAMES = {"rules": "utility_large_load_rules", "changes": "utility_large_load_rule_changes", "laws": "state_large_load_laws"}
SOURCE = "research:large_load_2026-11-13"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_research.md"
README_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/research/large_load/README.md"
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")   # seven changes print a month only: kept as printed in x_date, dated by the day read
RULE_FIELDS = ["docket", "threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
               "connection_timeline", "queue_size"]
RULE_STATUSES = {"ordered", "proposed", "approved", "in effect", "denied", "withdrawn"}


def read(kind, folder=RESEARCH):
    """A research file as text cells: its '#' lines are its own header, not rows."""
    with open(os.path.join(folder, FILES[kind]), encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return pd.read_csv(io.StringIO("".join(lines)), dtype=str, keep_default_na=False)


def split_fields(cell):
    return [x.strip() for x in re.split(r"[;,]", cell or "") if x.strip()]


def check(kind, d):
    """The problems that stop a table: what a row must hold, said row by row."""
    bad = []
    idc = {"rules": "row_id", "changes": "change_id", "laws": "law_id"}[kind]
    if not d[idc].is_unique:
        bad.append(f"{FILES[kind]}: {idc} not unique")
    for _, r in d.iterrows():
        rid = r[idc]
        if r["license"] not in ("public", "internal"):
            bad.append(f"{rid}: license {r['license']!r}")
        if not r["source_url"].startswith("http"):
            bad.append(f"{rid}: source_url {r['source_url']!r}")
        if not DATE_RE.match(r["date_read"]):
            bad.append(f"{rid}: date_read {r['date_read']!r}")
        if kind == "rules":
            if r["status"] not in RULE_STATUSES:
                bad.append(f"{rid}: status {r['status']!r}")
            for f in split_fields(r["internal_fields"]):
                if f not in RULE_FIELDS:
                    bad.append(f"{rid}: internal_fields names {f!r}, not a field of the file")
        if kind == "changes" and not (DATE_RE.match(r["date"]) or MONTH_RE.match(r["date"])):
            bad.append(f"{rid}: date {r['date']!r}")
    return bad


def dated(cell, date_read):
    """(event_date, x_date_kind): the row's own date where it prints one, else the day it was read."""
    return (cell, "stated date") if DATE_RE.match(cell or "") else (date_read, "date read")


def rules_rows(d):
    out, held = [], []
    for _, r in d.iterrows():
        if r["license"] != "public":
            held.append(f"{r['row_id']} ({r['utility']})")
            continue
        withheld = split_fields(r["internal_fields"])
        x, pointers = {}, []
        for f in RULE_FIELDS:
            v, c = r[f], r.get(f + "_cite", "")
            if f in withheld:
                v, c = "", ""
            elif v.startswith("held:"):
                pointers.append(f"{f}: {v[5:].strip()}")
                v = ""
            x["x_" + f], x["x_" + f + "_cite"] = v, c
        date, kind = dated(r["status_date"], r["date_read"])
        out.append(dict({
            "event_id": f"llrule:{r['row_id']}", "event_date": date, "event_type": "large_load_rule", "parties": r["utility"],
            "entity_ids": "", "mw": "", "price": "", "currency": "", "status": r["status"], "source": SOURCE, "source_url": r["source_url"],
            "x_row_id": r["row_id"], "x_group": r["group"], "x_utility": r["utility"], "x_state": r["state"], "x_iso_region": r["iso_region"],
            "x_rule_name": r["rule_name"], "x_status_date": r["status_date"], "x_status_cite": r["status_cite"], "x_date_kind": kind},
            **x, **{"x_source_title": r["source_title"], "x_date_read": r["date_read"], "x_quoted_clause": r["quoted_clause"],
                    "x_license_basis": r["license_basis"], "x_withheld": ";".join(withheld), "x_held": "; ".join(pointers),
                    "x_erw_overlap": r["erw_overlap"], "x_notes": " ".join(r["notes"].split())}))
    return pd.DataFrame(out), held


def changes_rows(d):
    out, held = [], []
    for _, r in d.iterrows():
        if r["license"] != "public":
            held.append(f"{r['change_id']} ({r['utility']})")
            continue
        date, kind = dated(r["date"], r["date_read"])
        out.append({
            "event_id": f"llchange:{r['change_id']}", "event_date": date, "event_type": "large_load_rule_change", "parties": r["utility"],
            "entity_ids": "", "mw": "", "price": "", "currency": "", "status": r["change"], "source": SOURCE, "source_url": r["source_url"],
            "x_change_id": r["change_id"], "x_group": r["group"], "x_utility": r["utility"], "x_state": r["state"], "x_rule_name": r["rule_name"],
            "x_date": r["date"], "x_date_kind": kind, "x_affects": r["affects"], "x_docket": r["docket"], "x_what": r["what"], "x_cite": r["cite"], "x_source_title": r["source_title"],
            "x_date_read": r["date_read"], "x_license_basis": r["license_basis"]})
    return pd.DataFrame(out), held


def laws_rows(d):
    out, held = [], []
    for _, r in d.iterrows():
        if r["license"] != "public":
            held.append(f"{r['law_id']} ({r['state']} {r['bill']})")
            continue
        date, kind = dated(r["status_date"], r["date_read"])
        out.append({
            "event_id": f"lllaw:{r['law_id']}", "event_date": date, "event_type": "large_load_law", "parties": f"{r['state']} legislature",
            "entity_ids": "", "mw": "", "price": "", "currency": "", "status": r["status"], "source": SOURCE, "source_url": r["source_url"],
            "x_law_id": r["law_id"], "x_group": r["group"], "x_state": r["state"], "x_bill": r["bill"], "x_session": r["session"],
            "x_title": r["title"], "x_status_date": r["status_date"], "x_date_kind": kind, "x_effective_date": r["effective_date"],
            "x_status_cite": r["status_cite"], "x_threshold_mw": r["threshold_mw"], "x_threshold_mw_cite": r["threshold_mw_cite"],
            "x_requirements": r["requirements"], "x_source_title": r["source_title"], "x_date_read": r["date_read"],
            "x_notes": " ".join(r["notes"].split())})
    return pd.DataFrame(out), held


BUILD = {"rules": rules_rows, "changes": changes_rows, "laws": laws_rows}
WHAT = {
    "rules": "US utilities' (and two state commissions') large-load connection rules, one row a rule (session 3937, chain 267)",
    "changes": "changes to US utilities' large-load rules, 15 August to 13 November 2026, one row a filing, order or event (session 3937, chain 267)",
    "laws": "US states' large-load laws and bills of the 2025 and 2026 sessions, one row a law or bill (session 3937, chain 267)",
}
SHAPE = {
    "rules": "event_id llrule:<row_id>; event_date the status date the documents print, else the day read (x_date_kind); event_type "
             "large_load_rule; parties the utility or commission; status ordered, proposed, approved, in effect, denied or withdrawn. "
             "Each x_<field> as printed with its x_<field>_cite (page or section and the words); 'not published': the documents read do not state it",
    "changes": "event_id llchange:<change_id>; event_date the date the document prints, else (a month only, x_date) the day read (x_date_kind); event_type large_load_rule_change; status the kind "
               "of change (filed, order issued, approved, in effect, amended, suspended, hearing set, other); x_affects the rule's row_id, a "
               "registry file of the ERW, or 'new'; x_cite the page and words",
    "laws": "event_id lllaw:<law_id>; event_date the status date printed, else the day read (x_date_kind); event_type large_load_law; status "
            "introduced, passed one chamber, passed, enacted, in effect, vetoed or died; x_requirements the duties by topic, as printed",
}


def header(kind, d, held, run_id):
    return [
        f"Energy Research Warehouse (ERW): {WHAT[kind]}",
        f"Shape: events (docs/datastandard.md v0). {SHAPE[kind]}. mw empty: the files print sizes as phrases (x_threshold_mw).",
        f"Rows: {len(d)} written; held for a license and not written ({len(held)}): " + ("; ".join(held) if held else "none") + ".",
        f"Source: {SOURCE}, docs/research/large_load/{FILES[kind]} (window P4 of the portable laptop, sessions 5300 to 5304; method {README_URL}); "
        "each row's source_url is the document it was read in. No request is made by this connector.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_research.py; x_date_read is the day each document was read",
        f"Method: {METHOD_URL}",
        "License: public (row-level holds): each written row cites a commission's copy, a filed tariff book, an SEC filing, a grid operator's "
        "posted document or a legislature's own text (the owner's ruling 4 of 6 November 2026); rows and cells whose only source asks written "
        "permission are not written" + ("; x_withheld names a public row's cells left empty for that reason" if kind == "rules" else "") + ".",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the large-load research pass as three events tables (session 3937)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out-dir")
    ap.add_argument("--folder", default=RESEARCH)
    a = ap.parse_args(argv)
    built, problems = {}, []
    for kind in FILES:
        d = read(kind, a.folder)
        problems += check(kind, d)
        rows, held = BUILD[kind](d)
        built[kind] = (rows, held, len(d))
    for p in problems:
        print(f"REFUSED: {p}")
    if problems:
        print(f"large_load_research FAILED: {len(problems)} problems; nothing written")
        return 1
    for kind, (rows, held, n) in built.items():
        print(f"{NAMES[kind]}: {len(rows)} of {n} rows written, {len(held)} held for a license")
    if a.check:
        return 0
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"large_load_research_{run_id}.log"))
    try:
        for kind, (rows, held, n) in built.items():
            cols = EVENT_COLS + [c for c in rows.columns if c not in EVENT_COLS]
            path = os.path.join(ip.OUT_DIR, NAMES[kind] + ".csv")
            if os.path.exists(path):
                os.remove(path)   # written whole from the research file each run
            ip.write_csv(rows[cols], NAMES[kind], header(kind, rows, held, run_id), log, cols=cols, key=["event_id"], time_col="event_date")
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="US utilities, state commissions and legislatures, read by the ERW's research pass",
                                    report="Large-load rules, their changes and the states' laws (docs/research/large_load, 13 and 14 November 2026)",
                                    report_url=README_URL, document_list="", license="public", tables=list(NAMES.values()))])
    except Exception as exc:
        print(f"large_load_research FAILED: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
