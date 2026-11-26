#!/usr/bin/env python3
"""Announced datacenters as a warehouse table (session 10000, chain 701: data request 6 of
docs/state/data_requests_forecast.md, for chain 740's /impact).

Energy Research Warehouse (ERW). Reads warehouse/forecast/datacenter_announced_rows.json, the evidence rows chain 740
transcribed by hand from public documents (state agencies' and the companies' own releases), each figure with the
document's own words, and writes one events table:

    datacenter_announced   one row a named datacenter project and one public document. event_id
               erw_dc_announced:<row id>; event_date the document's date; event_type announcement; parties the company;
               mw the megawatts as stated (null where the document states none) and x_mw_measure what they measure; status
               announced; source erw:datacenter_announced; source_url the document's address; x_name, x_state, x_county,
               x_place, x_doc_title, x_doc_publisher; for each figure its value, what it counts, the document's phrase
               (says), its qualifier ("at least", "nearly", "up to") and the sentence it sits in (quote): investment (USD,
               with its year), construction jobs, permanent jobs, megawatts; x_incentive, x_years and x_note as written

Nothing is computed or filled: a figure a document does not state is empty. Before writing, each figure's `says` must
sit inside its `quote` (chain 740's own check, warehouse/forecast/datacenter_announced.py, also checks every quote
against the kept text of its document on the machine that read it); a row id given twice stops the run.

Tier: model_extracted (build_coverage.TIER_RULES): the rows were read from the documents by a chain session, as the
large-load tables were. License: internal. The rows quote the documents' sentences, and session 255's rule (the one
large_load_public follows) makes public only facts with a link and no quoted text; the documents' own reuse terms were
not read. Whether the facts alone may be a public selection is a line for Samuel's ruling.

    python warehouse/derived/datacenter_announced_table.py [--out-dir DIR]

Method: docs/methods/datacenter_announced.md. Makes no request.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "datacenter_announced"
SOURCE = "erw:datacenter_announced"
ROWS = os.path.join(ROOT, "warehouse", "forecast", "datacenter_announced_rows.json")
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_announced.md"
FIGURES = ("investment", "construction_jobs", "permanent_jobs", "mw")
COLS = (["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
         "source_url", "retrieved_at", "x_doc_date", "x_date_precision", "x_name", "x_state", "x_county", "x_place", "x_doc_title", "x_doc_publisher",
         "x_doc_request", "x_mw_measure", "x_mw_says", "x_mw_qualifier", "x_mw_quote",
         "x_investment_usd", "x_investment_year", "x_investment_says", "x_investment_qualifier", "x_investment_quote",
         "x_investment_includes_generation",
         "x_construction_jobs", "x_construction_jobs_measure", "x_construction_jobs_says", "x_construction_jobs_qualifier",
         "x_construction_jobs_quote",
         "x_permanent_jobs", "x_permanent_jobs_measure", "x_permanent_jobs_says", "x_permanent_jobs_qualifier",
         "x_permanent_jobs_quote", "x_wage", "x_incentive", "x_years", "x_note"])


def plain(s):
    return " ".join(str(s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').split())


def check(rows):
    """The rows' own consistency: ids once each, each figure's phrase inside its sentence, a value for each phrase."""
    ids = [r["id"] for r in rows]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        raise RuntimeError(f"row ids given twice: {twice}")
    for r in rows:
        for f in FIGURES:
            fig = r.get(f)
            if fig is None:
                continue
            if fig.get("value") is None or not fig.get("says") or not fig.get("quote"):
                raise RuntimeError(f"{r['id']} {f}: a figure without its value, phrase or sentence")
            if plain(fig["says"]) not in plain(fig["quote"]):
                raise RuntimeError(f"{r['id']} {f}: {fig['says']!r} is not inside its quote")


def event_day(date):
    """The document's date as the standard writes it. A document dated by its month only (three of chain 740's rows) is
    written on the month's first day, and x_date_precision says "month"; no day is guessed."""
    s = str(date)
    if len(s) == 10:
        return s
    if len(s) == 7 and s[4] == "-":
        return s + "-01"
    raise RuntimeError(f"a document date neither YYYY-MM-DD nor YYYY-MM: {date!r}")


def row_of(r, retrieved):
    def fig(f, key):
        x = r.get(f)
        return "" if x is None else x.get(key, "")
    doc = r["doc"]
    wage = r.get("wage")
    return {
        "event_id": f"erw_dc_announced:{r['id']}", "event_date": event_day(doc["date"]), "event_type": "announcement",
        "x_doc_date": doc["date"], "x_date_precision": "day" if len(str(doc["date"])) == 10 else "month",
        "parties": r.get("company", ""), "entity_ids": "", "mw": fig("mw", "value"), "price": "", "currency": "USD",
        "status": "announced", "source": SOURCE, "source_url": doc["url"], "retrieved_at": retrieved,
        "x_name": r.get("name", ""), "x_state": str(r.get("state", "")).upper(), "x_county": r.get("county", ""),
        "x_place": r.get("place", ""), "x_doc_title": doc.get("title", ""), "x_doc_publisher": doc.get("publisher", ""),
        "x_doc_request": doc.get("request", ""),
        "x_mw_measure": fig("mw", "measure"), "x_mw_says": fig("mw", "says"), "x_mw_qualifier": fig("mw", "qualifier"),
        "x_mw_quote": fig("mw", "quote"),
        "x_investment_usd": fig("investment", "value"), "x_investment_year": fig("investment", "year"),
        "x_investment_says": fig("investment", "says"), "x_investment_qualifier": fig("investment", "qualifier"),
        "x_investment_quote": fig("investment", "quote"),
        "x_investment_includes_generation": "yes" if r.get("investment_includes_generation") else "",
        "x_construction_jobs": fig("construction_jobs", "value"), "x_construction_jobs_measure": fig("construction_jobs", "measure"),
        "x_construction_jobs_says": fig("construction_jobs", "says"), "x_construction_jobs_qualifier": fig("construction_jobs", "qualifier"),
        "x_construction_jobs_quote": fig("construction_jobs", "quote"),
        "x_permanent_jobs": fig("permanent_jobs", "value"), "x_permanent_jobs_measure": fig("permanent_jobs", "measure"),
        "x_permanent_jobs_says": fig("permanent_jobs", "says"), "x_permanent_jobs_qualifier": fig("permanent_jobs", "qualifier"),
        "x_permanent_jobs_quote": fig("permanent_jobs", "quote"),
        "x_wage": json.dumps(wage, ensure_ascii=False, sort_keys=True) if wage else "",
        "x_incentive": r.get("incentive", ""), "x_years": r.get("years", ""), "x_note": r.get("note", ""),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Announced datacenters (chain 740's evidence rows) as an events table")
    ap.add_argument("--out-dir", help="a trial: write the table here, record nothing")
    a = ap.parse_args(argv)
    out_dir = a.out_dir or ip.OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(out_dir if a.out_dir else ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        if not a.out_dir:
            ip._require_lock(os.path.join(out_dir, NAME + ".csv"), f"writing {NAME}")
        with open(ROWS, encoding="utf-8") as f:
            src = json.load(f)
        rows = src["rows"]
        check(rows)
        df = pd.DataFrame([row_of(r, retrieved) for r in rows], columns=COLS).sort_values(["event_date", "event_id"])
        head = [
            "Energy Research Warehouse (ERW): announced datacenters, what a named project's own government or company document said it "
            "would bring, one row a project and a document, every figure with the document's own words (session 10000, chain 701)",
            "Shape: events (docs/datastandard.md v0). event_id erw_dc_announced:<row id>; event_date the document's date (a document dated by month only: the month's first day, x_date_precision month, x_doc_date as printed); event_type "
            "announcement; parties the company; mw as stated (x_mw_measure says what it measures: IT capacity, grid capacity); for each "
            "figure its value, measure, says (the phrase), qualifier and quote (the sentence): investment (USD, x_investment_year), "
            "construction jobs, permanent jobs; x_incentive, x_years, x_note as written. A figure a document does not state is empty.",
            f"Rows: {len(df)}, documents dated {df['event_date'].min()} to {df['event_date'].max()}. Read by hand by chain 740 (lab-desktop "
            f"window 3) on {src.get('read', '')}; x_doc_request is the request's row in runs/c740/probe/probe.csv on that machine. Each "
            "phrase is checked to sit inside its sentence before writing; chain 740's script checks each sentence against the kept text.",
            "Tier: model_extracted (read from the documents by a chain session, as the large-load tables were). Cite the document of the row.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/datacenter_announced_table.py, from warehouse/forecast/datacenter_announced_rows.json",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {SOURCE} ERW, announced datacenters (docs/methods/datacenter_announced.md), {METHOD_URL}",
            "License: internal. The rows quote the documents' sentences; session 255's rule (as large_load_public follows it) makes public "
            "only facts with a link and no quoted text, and the documents' own reuse terms were not read.",
        ]
        path = os.path.join(out_dir, NAME + ".csv")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            for line in head:
                f.write("# " + line + "\n")
            df.to_csv(f, index=False, lineterminator="\n")
        os.replace(tmp, path)
        log(f"{NAME}: {len(df)} rows written")
        print(f"{NAME}.csv: rows={len(df)}")
        results.append(dict(table=NAME, market="derived", status="ok", detail=f"{len(df)} rows"))
        if not a.out_dir:
            ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), read from public documents",
                                "report": "Announced datacenters: each project's own government or company document (docs/methods/datacenter_announced.md)",
                                "report_url": METHOD_URL, "document_list": "", "license": "internal", "tables": [NAME]}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not a.out_dir:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
