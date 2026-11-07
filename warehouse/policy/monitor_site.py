#!/usr/bin/env python3
"""The policy monitor's data file (session 3060, chain 166): site/data/policy/monitor.json, the one file the
monitor view of /policy (?view=monitor) reads.

Energy Research Warehouse (ERW), platform tool 12. No warehouse table is written, no request is made and no model is
called: this reads policy_actions and policy_reads as held, the impact reads kept in warehouse/policy/impact_reads.csv
(in git, as scores.csv is, so an action is read once), and writes one file whole, by rename.

    python warehouse/policy/monitor_site.py                         # from warehouse/output, into site/data/policy
    python warehouse/policy/monitor_site.py --in-dir DIR --out FILE # a trial
    python warehouse/policy/monitor_site.py --daily                 # the daily run's soft step: never a thinner file

One row a record (warehouse/policy/records.py: the documents that name one proceeding), with what the monitor's table
filters and sorts on: the date of its newest document, the body, the instrument, the sector (the scorer's, of its most
significant document), the grids (the grid operators the documents' reads name, and those a title names by the words
of rules_in_motion.OPERATOR_WORDS), the states, the status, the highest significance, the next step with its date and
words, the figure with its unit and words, the impact sentence (where one was read) and the plain read of
policy_reads, the sources (the newest document's page first), and the history. Every value is a table's or a written
rule's; none is the page's. The figures a chart sums are the records' own figures, each with its record id.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import policy_fields as pf  # noqa: E402  session 3233: its own name, beside the deals tracker's fields
import impact as pi  # noqa: E402
import records as pr  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "policy", "monitor.json")
IN_DIR = os.path.join(ROOT, "warehouse", "output")
IMPACT = os.path.join(HERE, "impact_reads.csv")
try:
    from rules_in_motion import OPERATOR_WORDS, GRID_NAMES
except Exception:   # the derived folder is the repository's own; a trial without it still runs
    OPERATOR_WORDS, GRID_NAMES = {}, {}
ISO_NAMES = {"ERCOT": "ercot", "PJM": "pjm", "MISO": "miso", "CAISO": "caiso", "NYISO": "nyiso", "ISO-NE": "isone",
             "ISONE": "isone", "SPP": "spp"}


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)


def grids_named(text):
    """The grid operators a text names by their own words."""
    out = []
    for key, words in OPERATOR_WORDS.items():
        if any(re.search(rf"(?<![A-Za-z]){re.escape(w)}(?![A-Za-z])", text or "") for w in words):
            out.append(key)
    return out


def impact_reads(path=IMPACT):
    """{event_id: (impact sentence, quotation, model)} of the kept reads."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    return {r["event_id"]: (r["impact"], r["quote"], r["model"]) for r in rows if r.get("kept") == "yes" and r.get("impact")}


def build(actions, reads=None, impacts=None, today=None):
    """The file's content (a dict) from the frames of policy_actions and policy_reads."""
    a = actions.copy().fillna("")
    for c in pf.FIELD_COLS:
        if c not in a.columns:
            a[c] = ""
    for i in a.index[a["fields_from"] == ""]:
        a.loc[i, pf.FIELD_COLS] = pd.Series(pf.derive(a.loc[i].to_dict(), "", None))
    rec = pr.records(a)
    by_id = a.set_index("event_id")
    rd = {} if reads is None or not len(reads) else {r["action_event_id"]: r for r in reads.fillna("").to_dict("records")}
    impacts = impacts or {}
    rows = []
    for r in rec.to_dict("records"):
        ids = r["event_ids"].split(";")
        docs = by_id.loc[ids]
        newest = docs.iloc[-1]
        grids, states, plain, impact = [], [], "", None
        for eid, d in docs.iterrows():
            x = rd.get(eid)
            if x:
                for g in (x.get("affected_isos") or "").split(";"):
                    k = ISO_NAMES.get(g.strip().upper())
                    if k and k not in grids:
                        grids.append(k)
                plain = x.get("plain_read") or plain
            for g in grids_named(d["title"]):
                if g not in grids:
                    grids.append(g)
            for s in (d.get("states") or "").split(";"):
                s = s.strip()
                if s and s not in states:
                    states.append(s)
            if eid in impacts:
                impact = {"text": impacts[eid][0], "quote": impacts[eid][1], "model": impacts[eid][2], "event_id": eid}
        # session 3061: every dated step of every document, with the document it stands in, for the calendar
        steps, seen = [], set()
        for eid, d in docs.iterrows():
            pairs = [p for p in (d.get("dates") or "").split("; ") if p]
            words = (d.get("dates_evidence") or "").split(" | ")
            for k, pair in enumerate(pairs):
                kind, date = pair.split("=")
                if (kind, date) in seen:
                    continue
                seen.add((kind, date))
                steps.append({"kind": kind, "date": date, "words": words[k] if k < len(words) else "", "event_id": eid})
        steps.sort(key=lambda s: (s["date"], s["kind"]))
        table, page = pi.bears_on(newest.to_dict() | {"body": r["body"]})
        row = {"id": r["event_id"], "date": r["event_date"], "first": r["first_date"], "body": r["body"],
               "instrument": newest["instrument"], "title": r["title"], "status": r["status"],
               "sector": r["sector"], "significance": int(r["significance"]) if r["significance"] else None,
               "grids": grids, "states": states, "n": int(r["n_documents"]),
               "next": {"step": r["next_step"], "date": r["next_step_date"], "words": r["next_step_evidence"]} if r["next_step_date"] else None,
               "steps": steps,
               "figure": {"value": float(r["figure_value"]), "unit": r["figure_unit"], "words": r["figure_evidence"],
                          "event_id": r["figure_event_id"]} if r["figure_value"] else None,
               "impact": impact, "plain": plain or None, "bears_on": {"table": table, "page": page},
               "sources": [u for u in r["source_urls"].split(";") if u][::-1],
               "news": [u for u in r["news_story_urls"].split(";") if u],
               "history": [h for h in r["history"].split(" | ") if h],
               "docket": r["proceeding_ids"],
               "scope": newest.get("scope", "")}
        rows.append({k: v for k, v in row.items() if v not in (None, "", [])})
    rows.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
    today = today or dt.date.today().isoformat()
    return {"built": today, "documents": int(len(a)), "records": len(rows),
            "fields_from": {k: int(v) for k, v in a["fields_from"].value_counts().items()},
            "about": ("One row a record: the documents of policy_actions that name one proceeding "
                      "(warehouse/policy/records.py), with the fields of warehouse/policy/fields.py and the impact "
                      "sentences of warehouse/policy/impact_reads.csv. Built by warehouse/policy/monitor_site.py."),
            "rows": rows}


def write(doc, out, daily=False, log=print):
    """Write the file whole, by rename; the daily step never writes one with fewer records than the file held."""
    if daily and os.path.exists(out):
        try:
            with open(out, encoding="utf-8") as f:
                held = json.load(f)
            if doc["records"] < held.get("records", 0):
                log(f"policy_monitor_records FAILED: {doc['records']} records, fewer than the {held['records']} held; not written")
                return 1
            same = {k: v for k, v in held.items() if k != "built"} == {k: v for k, v in doc.items() if k != "built"}
            if same:
                log("policy_monitor_records: nothing changed; the file is left as it is")
                return 0
        except (OSError, ValueError):
            pass
    s = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    s = s.replace(chr(0x2014), ": ").replace(chr(0x2013), "-")   # the repository's rule: no em or en dash in any file
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    os.replace(out + ".tmp", out)
    log(f"policy_monitor_records: {doc['documents']} documents, {doc['records']} records, written to {out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy monitor data file (session 3060)")
    ap.add_argument("--in-dir", default=IN_DIR)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--daily", action="store_true")
    args = ap.parse_args(argv)
    path = os.path.join(args.in_dir, "policy_actions.csv")
    if not os.path.exists(path):
        print(f"policy_monitor_records SKIPPED: no policy_actions.csv in {args.in_dir}")
        return 0
    reads_path = os.path.join(args.in_dir, "policy_reads.csv")
    reads = read(reads_path) if os.path.exists(reads_path) else None
    return write(build(read(path), reads, impact_reads()), args.out, args.daily)


if __name__ == "__main__":
    sys.exit(main())
