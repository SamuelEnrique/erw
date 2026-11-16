#!/usr/bin/env python3
"""ERW, the contracts page (/contracts): what the page is served, made from the tables on this machine (session 7501,
chain 304).

ferc_eqr_contracts and its seven sister tables are internal: row-level security hides them, the page reads them only
through two database functions that answer with the server's internal token, and no row of them is in git. This script
reads the tables as CSV in warehouse/output (read only) and writes, into this folder's rows/ (never in git):

    rows/summary.json            the stored summary the page reads (internal_eqr_summary): the loader's own function,
                                 warehouse/supabase/load.py eqr_summary, run on the rows the live set holds on the day
                                 of a load (the rows executed in the 1,000 days before it, live_set.yaml event_days)
    rows/quarters/<quarter>.json the rows internal_eqr_contracts answers for each quarter of execution: the columns of
                                 migration 020, the newest 5,000 of the quarter
    rows/contracts_slim.csv      for the do-file: one line a row of the newest quarter's file, the columns the five
                                 headline figures read, no free text but the two parties' names
    rows/retrieved.json          which files, their Retrieved lines, the day of the load, the counts

    python replication/contracts/copy_rows.py                      # the load of 5 October 2026 (the last the note records)
    python replication/contracts/copy_rows.py --load-day 2026-11-16
    python replication/contracts/copy_rows.py --tables DIR         # another folder of tables

No request is made and nothing is written outside rows/. Exit 0 when written, 2 when a table is not on the machine
(nothing is written then). Needs pandas and yaml (the loader's own imports).
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROWS = os.path.join(HERE, "rows")
TABLES = ["ferc_eqr_contracts", "ferc_eqr_contract_terms", "ferc_eqr_party_totals", "ferc_eqr_party_mw", "ferc_eqr_buyer_names",
          "ferc_eqr_buyer_doubtful", "ferc_eqr_quarter_changes", "ferc_eqr_contracts_history"]
EVENT_DAYS = 1000        # warehouse/supabase/live_set.yaml, select, ferc_eqr_contracts: event_days
LIMIT = 5000             # site/app/contracts/read.ts asks for 5,000; migration 020 allows no more
# migration 020, internal_eqr_contracts: the page's name of a column, and the table's
COLUMNS = {"seller": "x_seller_company_name", "buyer": "x_customer_company_name", "affiliate": "x_contract_affiliate",
           "agreement": "x_contract_service_agreement_id", "product_type": "x_product_type_name", "product": "x_product_name",
           "class": "x_class_name", "term": "x_term_name", "commencement": "x_commencement_date_of_contract_term",
           "termination": "x_contract_termination_date", "quantity": "x_quantity", "units": "x_units", "rate": "x_rate",
           "rate_units": "x_rate_units", "rate_description": "x_rate_description", "pod_ba": "x_point_of_delivery_balancing_authority",
           "pod_location": "x_point_of_delivery_specific_location", "quarter": "x_quarter"}
SLIM = ["event_id", "event_date", "status", "product", "company_id", "contract_id", "seller", "buyer", "quantity", "units", "rate", "rate_description"]


def tables_dir(given):
    """The folder of tables: the one named, else this checkout's, else the main checkout's beside it."""
    for d in ([given] if given else []) + [os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")]:
        if d and os.path.exists(os.path.join(d, "ferc_eqr_contracts.csv")):
            return d
    return None


def header(path):
    """The comment lines of a table, and how many they are."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            out.append(line.rstrip("\n"))
    return out


def rows_of(path):
    """Each row of a table as a dict, one at a time (the file is never held whole)."""
    csv.field_size_limit(1 << 30)
    with open(path, encoding="utf-8", newline="") as f:
        n = len(header(path))
        for _ in range(n):
            next(f)
        yield from csv.DictReader(f)


def number(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def quarter_of(day):
    return f"{day[:4]}-Q{(int(day[5:7]) - 1) // 3 + 1}"


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--tables")
    p.add_argument("--load-day", default="2026-10-05")
    a = p.parse_args(argv[1:])
    d = tables_dir(a.tables)
    missing = [t for t in TABLES if not d or not os.path.exists(os.path.join(d, t + ".csv"))]
    if missing:
        print(f"not on this machine: {', '.join(missing)} (looked in {d or 'no folder'})")
        return 2
    cutoff = (dt.date.fromisoformat(a.load_day) - dt.timedelta(days=EVENT_DAYS)).isoformat()
    live, slim, total = [], [], 0
    for r in rows_of(os.path.join(d, "ferc_eqr_contracts.csv")):
        total += 1
        slim.append([r["event_id"], r["event_date"][:10], r["status"], r["x_product_name"].strip().upper(), r["x_company_id"], r["x_contract_unique_id"],
                     r["x_seller_company_name"], r["x_customer_company_name"], r["x_quantity"], r["x_units"], r["x_rate"], "1" if r["x_rate_description"].strip() else "0"])
        if r["event_date"][:10] >= cutoff:
            live.append(r)

    # the stored summary, by the loader's own function on the live rows (and on the derived tables in the same folder)
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
    import pandas as pd
    import load
    load.OUT = d
    summary = load.eqr_summary(pd.DataFrame(live, dtype=str))

    # the rows the database function answers for a quarter: event_date desc, then event_id; the newest 5,000
    by_q = {}
    for r in live:
        by_q.setdefault(quarter_of(r["event_date"][:10]), []).append(r)
    os.makedirs(os.path.join(ROWS, "quarters"), exist_ok=True)
    over = {}
    for q, rs in by_q.items():
        rs.sort(key=lambda r: r["event_id"])
        rs.sort(key=lambda r: r["event_date"][:10], reverse=True)
        if len(rs) > LIMIT:
            over[q] = len(rs)
        out = [{"event_id": r["event_id"], "event_date": r["event_date"][:10], "status": r["status"] or None, "mw": number(r["mw"]), "price": number(r["price"]),
                **{k: r[c] for k, c in COLUMNS.items()}} for r in rs[:LIMIT]]
        out.sort(key=lambda r: (r["seller"], r["event_id"]))
        out.sort(key=lambda r: r["event_date"], reverse=True)
        with open(os.path.join(ROWS, "quarters", q + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f)
    with open(os.path.join(ROWS, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f)
    with open(os.path.join(ROWS, "contracts_slim.csv"), "w", encoding="utf-8", newline="") as f:
        f.write("# ERW, /contracts: the newest quarter's contract rows, the columns the do-file reads (internal: never in git)\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SLIM)
        w.writerows(slim)
    stamp = {"tables": d.replace("\\", "/"), "load_day": a.load_day, "window_from": cutoff, "rows_in_file": total, "rows_in_live_window": len(live),
             "quarters_written": sorted(by_q), "quarters_over_5000": over,
             "retrieved": {t: next((h for h in header(os.path.join(d, t + ".csv")) if h.startswith("# Retrieved")), "") for t in TABLES},
             "written_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(ROWS, "retrieved.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(stamp, f, indent=1)
    print(f"{total:,} rows in the quarter's file; {len(live):,} executed on or after {cutoff} (the live set of a load on {a.load_day}); "
          f"{len(by_q)} quarters of execution written; over 5,000 rows: {over or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
