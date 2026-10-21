#!/usr/bin/env python3
"""BOEM: every renewable energy lease and grant on the Outer Continental Shelf (session 493).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/boem_renewable_leases.csv, from the
Bureau of Ocean Energy Management's table of the leases and grants it has executed since its renewable energy program
began, on its Lease and Grant Information page:

    https://www.boem.gov/renewable-energy/lease-and-grant-information

    entity_id    boem:<lease or grant number>, lower case with spaces as underscores (boem:ocs-a_0472)
    entity_type  project; name the lease or grant page's title; geo US (the page names no state)
    status       active for BOEM's "Active"; empty for its other words (Cancelled, Relinquished, Expired,
                 Consolidated), which the standard's vocabulary has no word for; boem_status keeps BOEM's own word
    the rest     lease_number, lessee, authorization (BOEM's, with its "*" note mark), resource_type, effective_year

The table as BOEM publishes it; nothing is filled. A lease number given twice stops the run, and so does a table whose
columns are not the seven read on 21 October 2026.

    python warehouse/connectors/boem_leases.py

Ceiling: one request (the page). License: public (BOEM: "Generally, materials produced by federal agencies are in the
public domain", record 86 of license_reads.csv; credit BOEM as the source).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "boem_renewable_leases"
CONNECTOR = "boem_leases"
SOURCE = "boem:lease_and_grant_information"
PAGE = "https://www.boem.gov/renewable-energy/lease-and-grant-information"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLUMNS = ["Lease or Grant Number", "Lease or Grant Page", "Authorization Resource Type", "Resource Type", "Lease Effective Year",
           "Lessee or Grantee", "Status"]
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
EXTRA_COLS = ["lease_number", "lessee", "authorization", "resource_type", "effective_year", "boem_status"]
STATUS = {"Active": "active", "Cancelled": "", "Relinquished": "", "Expired": "", "Consolidated": ""}


def leases(page_html, url, retrieved):
    tables = [t for t in pd.read_html(io.StringIO(page_html)) if list(t.columns) == COLUMNS]
    if len(tables) != 1:
        raise RuntimeError(f"the page holds {len(tables)} tables with the columns {COLUMNS}")
    t = tables[0]
    unknown = sorted(set(t["Status"].astype(str)) - set(STATUS))
    if unknown:
        raise RuntimeError(f"a status not in the map: {unknown}")
    num = t["Lease or Grant Number"].astype(str).str.strip()
    if num.duplicated().any():
        raise RuntimeError(f"a lease number given twice: {sorted(num[num.duplicated()])[:5]}")
    year = pd.to_numeric(t["Lease Effective Year"], errors="coerce")
    return pd.DataFrame({
        "entity_id": "boem:" + num.str.lower().map(lambda s: re.sub(r"\s+", "_", s)), "entity_type": "project",
        "name": t["Lease or Grant Page"].astype(str).str.strip(), "geo": "US", "lat": None, "lon": None, "capacity_mw": None,
        "status": t["Status"].map(STATUS), "status_date": "", "operator": t["Lessee or Grantee"].astype(str).str.strip(),
        "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": "",
        "lease_number": num, "lessee": t["Lessee or Grantee"].astype(str).str.strip(), "authorization": t["Authorization Resource Type"].astype(str).str.strip(),
        "resource_type": t["Resource Type"].astype(str).str.strip(), "effective_year": year.map(lambda v: "" if pd.isna(v) else str(int(v))),
        "boem_status": t["Status"].astype(str).str.strip(),
    }).sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="BOEM: every renewable energy lease and grant on the OCS")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, rec = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=UA)
        t = leases(page.decode("utf-8", errors="replace"), PAGE, rec["retrieved_at"])
        header = [
            "Energy Research Warehouse (ERW): BOEM, every renewable energy lease and grant on the Outer Continental Shelf (session 493)",
            "Shape: entities (docs/datastandard.md v0). entity_id boem:<lease or grant number>; entity_type project; status active for BOEM's Active, empty for its other words; boem_status BOEM's own word; operator the lessee or grantee.",
            f"Leases and grants: {len(t)}; by BOEM's status: " + ", ".join(f"{k} {v}" for k, v in t["boem_status"].value_counts().items()) + ". The page names no state, area or acreage. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/boem_leases.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Bureau of Ocean Energy Management (BOEM), Lease and Grant Information (renewable energy), {PAGE}",
            "License: public (a work of the U.S. government; credit BOEM as the source).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Bureau of Ocean Energy Management (BOEM)",
                                    report="Renewable energy Lease and Grant Information", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} leases and grants"))
        print(f"{NAME}: {len(t)} leases and grants")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
