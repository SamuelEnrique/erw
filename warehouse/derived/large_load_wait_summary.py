#!/usr/bin/env python3
"""How long large loads waited, by publisher and interval: the summary of large_load_waits that names no request
(session 7008, chain 301, goal 2).

Energy Research Warehouse (ERW). Reads warehouse/output/large_load_waits.csv (internal: one row a request and stage
interval, with its range of days between dated copies and its label) and writes large_load_wait_summary (series shape,
one row a publisher, interval and figure). No request, no model call. Method: docs/methods/large_load_waits.md,
"The public summary".

For each publisher and interval (request to energized, request to a stage, and the publisher's other intervals):

  requests            the requests with a row for the interval
  measured            those labeled measured (both ends between dated copies)
  lower_bounds        those still waiting, or seen in two copies only: counted apart, never in a median
  upper_bounds        those whose end had come by the first copy that holds them
  median_days_at_least, median_days_at_most
                      over the measured requests only: the median of the shorter end of each range, and the median of
                      the longer end (a range of medians, never a midpoint); written only where five or more are
                      measured (the method's rule: a figure on fewer than five requests is its values, and a value would
                      describe a request)

No request is named, no megawatt is given, nothing is filled in. Each row carries its publisher's license verdict in
x_license, and x_terms the words of the publisher's terms it rests on: public only where those terms allow derived
statistics; internal where they do not or are unclear (then the question is the owner's, the default internal). The
table's license is the strictest of its rows (internal while any row is).

    python warehouse/derived/large_load_wait_summary.py            # the table (data lock)
    python warehouse/derived/large_load_wait_summary.py --out-dir D
"""
import argparse
import csv
import datetime as dt
import os
import re
import statistics
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "large_load_wait_summary"
SOURCE = "erw:large_load_wait_summary"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/large_load_waits.md"
MIN_MEDIAN = 5
# Each publisher's verdict for derived statistics, from its terms as docs/methods/large_load_waits.md and
# docs/accelerator/large_load_waits.md quote them word for word (re-read and checked by session 7008's --terms run).
VERDICTS = {
    "New York ISO": ("internal", "US-NY",
                     "NYISO's legal notice confers no license (session 149): no word of it allows the reuse of its "
                     "workbook's contents or of statistics made from them"),
    "Grant County Public Utility District": ("internal", "US-WA",
                     "\"All information collected at this Web site or through this Service becomes a public record that may "
                     "be subject to inspection by the public unless an exemption in law exists.\" and \"Public Utility District "
                     "No. 2 of Grant County, WA, All Rights Reserved\": unclear for derived statistics; the owner's question"),
    "Bonneville Power Administration": ("internal", "US",
                     "an agency of the United States government whose site states no terms of use for its documents (its "
                     "privacy page only: \"When you visit our website to read pages or download information, we "
                     "automatically collect and store the following information only:\"); unclear; held internal until a "
                     "person rules, as the method says"),
    "Alberta Electric System Operator (Canada)": ("internal", "CA-AB",
                     "\"The material may be used and copied for non-commercial, personal or educational purposes, provided "
                     "that the material is not modified and that copyright notices are not deleted.\" and \"Any other use of "
                     "this material without the AESO's written permission is prohibited.\": not for the ERW's use without "
                     "permission"),
}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "source", "source_url", "retrieved_at",
        "x_publisher", "x_interval", "x_license", "x_terms", "x_note"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def summarize(rows, now):
    """The summary rows from the waits table's rows (dicts)."""
    by = {}
    for r in rows:
        by.setdefault((r["entity"], r["interval"]), []).append(r)
    last = {}
    for r in rows:
        last[r["entity"]] = max(last.get(r["entity"], ""), r.get("last_copy_date", ""))
    out = []
    for (pub, interval), g in sorted(by.items()):
        lic, geo, terms = VERDICTS.get(pub, ("internal", "", "no verdict written for this publisher: internal by default"))
        ids = {r["request_id"] for r in g}
        measured = [r for r in g if r["label"] == "measured"]
        lower = [r for r in g if r["label"] in ("lower bound", "two copies only")]
        upper = [r for r in g if r["label"] == "upper bound"]
        base = dict(ts_utc=f"{last[pub]}T00:00:00Z" if last.get(pub) else "", freq="", geo=geo, source=SOURCE,
                    source_url=METHOD_URL, retrieved_at=now, x_publisher=pub, x_interval=interval, x_license=lic,
                    x_terms=terms, x_note="")
        ent = f"llwaitsum:{slug(pub)}:{slug(interval)}"
        for var, val in (("requests", len(ids)), ("measured", len({r['request_id'] for r in measured})),
                         ("lower_bounds", len({r['request_id'] for r in lower})),
                         ("upper_bounds", len({r['request_id'] for r in upper}))):
            out.append(dict(base, entity=ent, variable=var, value=str(int(val)), unit="count"))
        lo = [num(r["days_at_least"]) for r in measured if num(r["days_at_least"]) is not None]
        hi = [num(r["days_at_most"]) for r in measured if num(r["days_at_most"]) is not None]
        if len(lo) >= MIN_MEDIAN and len(hi) >= MIN_MEDIAN:
            out.append(dict(base, entity=ent, variable="median_days_at_least", value=statistics.median(lo), unit="days",
                            x_note=f"median of the shorter end over {len(lo)} measured requests"))
            out.append(dict(base, entity=ent, variable="median_days_at_most", value=statistics.median(hi), unit="days",
                            x_note=f"median of the longer end over {len(hi)} measured requests"))
    return pd.DataFrame(out, columns=COLS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The summary of large_load_waits that names no request")
    ap.add_argument("--out-dir")
    ap.add_argument("--in-dir", default=None)
    a = ap.parse_args(argv)
    src = os.path.join(a.in_dir or ip.OUT_DIR, "large_load_waits.csv")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    now = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    with open(src, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    with open(src, encoding="utf-8") as f:
        retrieved = next((ln.strip("# \n") for ln in f if ln.startswith("# Retrieved")), "")
    s = summarize(rows, now)
    if not len(s):
        print(f"{NAME} FAILED: no rows in {src}; nothing written")
        return 1
    pubs = s.drop_duplicates("x_publisher")
    header = [
        f"Energy Research Warehouse (ERW): how long large loads waited, by publisher and interval, from dated copies of their queues; no request named, no megawatt given (session 7008, chain 301)",
        "Shape: series (docs/datastandard.md v0). entity llwaitsum:<publisher>:<interval>; variable requests, measured, lower_bounds, upper_bounds (count) and, where five or more are measured, median_days_at_least and median_days_at_most (days: the median of the shorter and of the longer end of the measured ranges, never a midpoint); ts_utc the publisher's latest dated copy; x_license and x_terms each publisher's verdict for derived statistics and the words it rests on.",
        f"Derived from: large_load_waits ({len(rows):,} rows; {retrieved})",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/large_load_wait_summary.py; no request, no model call",
        f"Method: {METHOD_URL} (\"The public summary\")",
        "Source: erw:large_load_wait_summary, the ERW's summary of large_load_waits (each publisher's dated copies in that table's header)",
        "License: internal. " + "; ".join(f"{r.x_publisher}: {r.x_license}" for r in pubs.itertuples())
        + ". A publisher's rows become public only when its terms allow derived statistics (a person's ruling for the unclear ones).",
    ]
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(path):
        os.remove(path)   # written whole from large_load_waits each run
    ip.write_snapshot(s, NAME, header, log, cols=COLS)
    if not a.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="How long large loads waited, by publisher and interval (docs/methods/large_load_waits.md)",
                                report_url=METHOD_URL, document_list="docs/methods/large_load_waits.md", license="internal",
                                tables=[NAME])])
    print(f"{NAME}: {len(s)} rows, {s['x_publisher'].nunique()} publishers, {s['entity'].nunique()} publisher and interval cells")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
