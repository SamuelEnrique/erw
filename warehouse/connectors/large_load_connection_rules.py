#!/usr/bin/env python3
"""Large loads' connection rules: each step a grid operator's or a utility's document states for connecting a large
load, with its stated duration or date, in the document's own words (session 2924, chain 153).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/large_load_connection_rules.csv, from the
registry files sessions fill by reading each document:

    warehouse/sources/large_load_connection_rules/<body>_<document>.yaml    one file a document (README.md there)

No request is made here: a session reads the document (robots and terms first), writes each step into its file with the
section and page it is printed in and the words it is printed in, and this connector turns the files into rows. A
duration is the number the step prints, in the step's own unit (business days, calendar days, days, months, years); a
date is the date the step prints. A step that states neither is written with its words and no duration. Nothing is
estimated, summed, converted between business and calendar days, or inferred.

    event_id    rule:<body slug>:<document slug>:<section slug>
    event_date  the date the step prints (x_date_kind "stated date"), else the document's own date ("document date")
    event_type  connection_rule
    parties     who acts in the step, as the document names it (ILLE, TSP, ERCOT, PG&E, the Applicant)
    mw          a load size the step prints, MW; else blank
    status      stated
    source_url  the document's address
    x_*         x_body, x_grid, x_utility, x_eia_id, x_state, x_document, x_document_date, x_section, x_page, x_step,
                x_duration, x_duration_unit, x_date_kind, x_printed, x_retrieved_at

License: public, row by row: each row quotes a grid operator's public guide or a utility's filed rule.

    python warehouse/connectors/large_load_connection_rules.py              # the table (data lock)
    python warehouse/connectors/large_load_connection_rules.py --check      # read and check the registry, write nothing
    python warehouse/connectors/large_load_connection_rules.py --out-dir D  # a trial: the table under D (no data lock)

Method: docs/methods/large_load_connection_rules.md.
"""

import argparse
import datetime as dt
import glob
import os
import re
import sys
import traceback

import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REGISTRY = os.path.join(ROOT, "warehouse", "sources", "large_load_connection_rules")
NAME = "large_load_connection_rules"
SOURCE = "filed:large_load_connection_rules"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_connection_rules.md"
UNITS = ("business days", "calendar days", "days", "months", "years")
FIELDS = ("body", "grid", "state", "document", "document_date", "document_url", "retrieved_at", "license", "steps")
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_body", "x_grid", "x_utility", "x_eia_id", "x_state", "x_document", "x_document_date", "x_section", "x_page", "x_step",
          "x_duration", "x_duration_unit", "x_date_kind", "x_printed", "x_retrieved_at"]
COLS = EVENT_COLS + X_COLS
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")[:60]


def text(v):
    """A YAML value as the registry's text: a date as YYYY-MM-DD, a time as YYYY-MM-DDTHH:MM:SSZ, None as ''."""
    if v is None:
        return ""
    if isinstance(v, dt.datetime):
        v = v.astimezone(dt.timezone.utc) if v.tzinfo else v
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(v, dt.date):
        return v.isoformat()
    return " ".join(str(v).split())


def check(reg, path):
    """The problems of one document's file, as sentences; [] when it can be written."""
    bad = [f"no {k}" for k in FIELDS if reg.get(k) in (None, "", [])]
    if not DATE_RE.match(text(reg.get("document_date"))):
        bad.append(f"document_date {reg.get('document_date')!r} is not YYYY-MM-DD")
    if not TS_RE.match(text(reg.get("retrieved_at"))):
        bad.append(f"retrieved_at {reg.get('retrieved_at')!r} is not YYYY-MM-DDTHH:MM:SSZ")
    if not re.match(r"^[A-Z]{2}$", text(reg.get("state"))):
        bad.append(f"state {reg.get('state')!r} is not a two-letter code")
    if not text(reg.get("document_url")).startswith(("http://", "https://")):
        bad.append("document_url is not an address")
    if text(reg.get("license")) != "public":
        bad.append(f"license {reg.get('license')!r}: only a public document is written here")
    seen = set()
    for i, s in enumerate(reg.get("steps") or []):
        sec = text(s.get("section"))
        if not sec:
            bad.append(f"step {i}: no section")
        if sec in seen:
            bad.append(f"step {i}: section {sec!r} twice")
        seen.add(sec)
        if not text(s.get("step")):
            bad.append(f"step {i} ({sec}): no step")
        if not text(s.get("printed")):
            bad.append(f"step {i} ({sec}): no printed words")
        d, u = s.get("duration"), text(s.get("unit"))
        if d not in (None, ""):
            if not isinstance(d, (int, float)) or isinstance(d, bool) or d <= 0:
                bad.append(f"step {i} ({sec}): duration {d!r} is not a positive number")
            if u not in UNITS:
                bad.append(f"step {i} ({sec}): unit {u!r} is not one of {list(UNITS)}")
            elif str(int(d)) not in text(s.get("printed")) and not any(w in text(s.get("printed")).lower() for w in NUMBER_WORDS.get(int(d), ())):
                bad.append(f"step {i} ({sec}): the duration {d} is not in its printed words")
        elif u:
            bad.append(f"step {i} ({sec}): a unit with no duration")
        if text(s.get("date")) and not DATE_RE.match(text(s.get("date"))):
            bad.append(f"step {i} ({sec}): date {s.get('date')!r} is not YYYY-MM-DD")
        m = s.get("mw")
        if m not in (None, "") and (not isinstance(m, (int, float)) or isinstance(m, bool) or str(m).rstrip("0").rstrip(".") not in text(s.get("printed"))):
            bad.append(f"step {i} ({sec}): mw {m!r} is not a number its printed words hold")
    return [f"{os.path.basename(path)}: {b}" for b in bad]


# a duration printed as a word ("seven Business Days") is checked against these
NUMBER_WORDS = {2: ("two",), 3: ("three",), 5: ("five",), 7: ("seven",), 10: ("ten",), 18: ("eighteen",), 20: ("twenty",),
                30: ("thirty",), 45: ("forty-five", "forty five"), 60: ("sixty",), 90: ("ninety",)}


def read_registry(folder=REGISTRY):
    """(the documents' files as dicts with their paths, the problems)."""
    regs, problems = [], []
    for p in sorted(glob.glob(os.path.join(folder, "*.yaml"))):
        with open(p, encoding="utf-8") as fh:
            reg = yaml.safe_load(fh) or {}
        problems += check(reg, p)
        regs.append((p, reg))
    return regs, problems


def rows(regs):
    """The table's rows from the documents' files."""
    out = []
    for p, reg in regs:
        doc = slug(os.path.splitext(os.path.basename(p))[0])
        for s in reg["steps"]:
            date = text(s.get("date"))
            d = s.get("duration")
            out.append({
                "event_id": f"rule:{doc}:{slug(s['section'])}", "event_date": date or text(reg["document_date"]), "event_type": "connection_rule",
                "parties": text(s.get("party")), "entity_ids": "", "mw": "" if s.get("mw") in (None, "") else f"{float(s['mw']):g}", "price": "",
                "currency": "", "status": "stated", "source": SOURCE, "source_url": text(reg["document_url"]),
                "x_body": text(reg["body"]), "x_grid": text(reg["grid"]), "x_utility": text(reg.get("utility")), "x_eia_id": text(reg.get("eia_id")),
                "x_state": text(reg["state"]), "x_document": text(reg["document"]), "x_document_date": text(reg["document_date"]),
                "x_section": text(s["section"]), "x_page": text(s.get("page")), "x_step": text(s["step"]),
                "x_duration": "" if d in (None, "") else f"{float(d):g}", "x_duration_unit": text(s.get("unit")),
                "x_date_kind": "stated date" if date else "document date", "x_printed": text(s["printed"]), "x_retrieved_at": text(reg["retrieved_at"])})
    d = pd.DataFrame(out, columns=COLS).fillna("")
    return d.sort_values(["x_grid", "x_body", "event_id"]).reset_index(drop=True)


def header(d, run_id):
    docs = d.drop_duplicates("source_url")[["x_body", "x_document_date"]].itertuples(index=False) if len(d) else []
    return [
        "Energy Research Warehouse (ERW): large loads' connection rules, one row a step a document states (session 2924, chain 153)",
        "Shape: events (docs/datastandard.md v0). event_id rule:<document>:<section>; event_date the date the step prints, else the "
        "document's own (x_date_kind); event_type connection_rule; parties who acts; mw a load size the step prints; x_duration and "
        "x_duration_unit the number and unit the step prints (business days, calendar days, days, months, years), blank where it states none; "
        "x_printed its words, x_section and x_page where.",
        f"Documents: {d['source_url'].nunique() if len(d) else 0}; steps: {len(d)}: " + "; ".join(f"{b} ({t})" for b, t in docs),
        "Source: the registry warehouse/sources/large_load_connection_rules/ (one file a document, each step with its section and words), "
        "filled by reading each document. No request is made by this connector.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_connection_rules.py; x_retrieved_at is when each document was read",
        f"Method: {METHOD_URL}",
        "License: public, row by row: each row quotes a grid operator's public guide or a utility's filed rule.",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: large loads' connection rules from the registry (session 2924)")
    ap.add_argument("--check", action="store_true", help="read and check the registry; write nothing")
    ap.add_argument("--out-dir", help="a trial: write under this directory (no data lock)")
    ap.add_argument("--registry", default=REGISTRY, help="the registry folder (a test's)")
    a = ap.parse_args(argv)
    regs, problems = read_registry(a.registry)
    for p in problems:
        print(f"REFUSED: {p}")
    if problems:
        print(f"{NAME} FAILED: {len(problems)} problems in the registry; nothing written")
        return 1
    d = rows(regs)
    print(f"{NAME}: {len(regs)} documents, {len(d)} steps, {int((d['x_duration'] != '').sum()) if len(d) else 0} with a duration, "
          f"{int((d['x_date_kind'] == 'stated date').sum()) if len(d) else 0} with a stated date")
    if a.check:
        return 0
    if d.empty:
        print(f"{NAME} SKIPPED: the registry holds no document; nothing written")
        return int(os.environ.get("ERW_SKIP_EXIT", "75"))
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        ip.write_csv(d, NAME, header(d, run_id), log, cols=COLS, key=["event_id"], time_col="event_date")
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="grid operators' guides and utilities' filed rules, read into the ERW's registry",
                                    report="Large loads' connection rules (warehouse/sources/large_load_connection_rules)", report_url=METHOD_URL,
                                    document_list="", license="public", tables=[NAME])])
    except Exception as exc:
        print(f"{NAME} FAILED: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
