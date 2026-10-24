#!/usr/bin/env python3
"""Statistics Canada's annual supply and disposition of electricity by province, 2005 to 2024 (table 25-10-0021-01):
generation, trade with the United States, interprovincial receipts and deliveries, electricity available, producers' own
use, sales to ultimate customers by sector, and unallocated electricity (session 2460, chain 118: a source of the
session's own choosing, beside statcan_generating_capacity_annual and StatCan's monthly generation and trade).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statcan_electricity_disposition_annual.csv,
from StatCan's full-table CSV (a zip), one request:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip

    entity    statcan_disp:<area>: ca or a province's or territory's two letters
    variable  the component as a slug: total_generation_of_electricity, total_imports_of_electricity_from_the_united_states
              and its purchased and exchanged parts, total_exports_of_electricity_to_the_united_states and its firm,
              secondary and exchanged parts, total_interprovincial_receipts_of_electricity and deliveries with their
              parts, total_electricity_available_for_use_within_specific_geographic_border, electricity_used_by_producers,
              total_sales_of_electricity_to_ultimate_customers and its residential, agriculture, mining and
              manufacturing, and other industries parts, unallocated_electricity
    unit      MWh (StatCan's megawatt hours); ts_utc the year's 1 January; freq P1Y; geo CA or CA-<province>
    x_*       StatCan's component name, the vector, its symbol (r revised) and terminated flag

The table's values in dollars (Estimates "Electricity value", Canadian dollars in thousands) are not taken: a currency
other than USD is a question for the owner. A figure marked .. (not available) has no row; nothing is filled. The
components overlap (totals hold their parts): a sum takes one level. Checks: the four sales sectors add to total sales
within 1 MWh, or the run stops; generation plus imports less exports plus receipts less deliveries is compared with the
electricity available, and producers' use plus sales plus unallocated with it too, and the header counts the area years
where each does not hold within 1 MWh, kept as StatCan publishes them. An area, component, unit or status not as read,
or a key given twice, stops the run.

    python warehouse/connectors/statcan_electricity_disposition.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/statcan_electricity_disposition/ with --offline. www150.statcan.gc.ca's
robots file asks a crawl delay of 2 seconds and disallows paths ending .csv, not the /n1/tbl/csv/ zip, and names no AI
agent (session 2460). License: public (the Statistics Canada Open Licence; the record's verdict).
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "statcan_electricity_disposition"
SOURCE = "statcan:25-10-0021-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002101"
TABLE = "statcan_electricity_disposition_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_component", "x_vector", "x_symbol", "x_terminated"]
AREAS = {"Canada": ("ca", "CA"), "Newfoundland and Labrador": ("nl", "CA-NL"), "Prince Edward Island": ("pe", "CA-PE"),
         "Nova Scotia": ("ns", "CA-NS"), "New Brunswick": ("nb", "CA-NB"), "Quebec": ("qc", "CA-QC"),
         "Ontario": ("on", "CA-ON"), "Manitoba": ("mb", "CA-MB"), "Saskatchewan": ("sk", "CA-SK"),
         "Alberta": ("ab", "CA-AB"), "British Columbia": ("bc", "CA-BC"), "Yukon": ("yt", "CA-YT"),
         "Northwest Territories": ("nt", "CA-NT"), "Nunavut": ("nu", "CA-NU")}
SALES = ["residential_sales_of_electricity", "agriculture_sales_of_electricity",
         "mining_and_manufacturing_sales_of_electricity", "other_industries_sales_of_electricity"]
TOL = 1.0   # MWh


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100021.csv"]:
        raise RuntimeError(f"the zip does not hold 25100021.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            est = r["Estimates"]
            if est == "Electricity value":
                counts["value_rows_not_taken"] = counts.get("value_rows_not_taken", 0) + 1
                continue
            if est != "Electricity quantity" or r["UOM"] != "Megawatt hours" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"an estimate or unit not as read: {est!r} {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, comp = r["GEO"], r["Electric power, components"]
            if area not in AREAS:
                raise RuntimeError(f"an area not in the map: {area!r}")
            if not re.fullmatch(r"\d{4}", r["REF_DATE"]):
                raise RuntimeError(f"a year that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in ("..", "x", "F"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code, geo = AREAS[area]
            ent, var = f"statcan_disp:{code}", slug(comp)
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01-01T00:00:00Z",
                            value=float(r["VALUE"]), unit="MWh", freq="P1Y", geo=geo, market="",
                            node=f"{area}: {comp}", x_component=comp, x_vector=r["VECTOR"],
                            x_symbol=(r["SYMBOL"] or "").strip(), x_terminated=(r["TERMINATED"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def checks(s):
    """Stops if the sales sectors do not add to total sales; returns the counts of the two identities that do not close."""
    w = s.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value", aggfunc="first")
    tot = w["total_sales_of_electricity_to_ultimate_customers"].dropna()
    parts = w.reindex(columns=SALES).fillna(0).sum(axis=1).reindex(tot.index)
    bad = (parts - tot).abs() > TOL
    if bad.any():
        k = bad[bad].index[0]
        raise RuntimeError(f"the sales sectors add to {parts[k]}, total sales are {tot[k]}: {k}")
    g = lambda c: w[c].fillna(0) if c in w.columns else 0  # noqa: E731
    avail = w["total_electricity_available_for_use_within_specific_geographic_border"].dropna()
    supply = (g("total_generation_of_electricity") + g("total_imports_of_electricity_from_the_united_states")
              - g("total_exports_of_electricity_to_the_united_states") + g("total_interprovincial_receipts_of_electricity")
              - g("total_interprovincial_deliveries_of_electricity")).reindex(avail.index)
    use = (g("electricity_used_by_producers") + g("total_sales_of_electricity_to_ultimate_customers")
           + g("unallocated_electricity")).reindex(avail.index)
    return len(tot), len(avail), int(((supply - avail).abs() > TOL).sum()), int(((use - avail).abs() > TOL).sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0021-01: electricity supply and disposition by province, a year")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=2)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        s = pd.DataFrame(parse(content, base, counts))
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        n_sales, n_avail, off_supply, off_use = checks(s)
        withheld = {k: v for k, v in counts.items() if k != "value_rows_not_taken"}
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0021-01, electric power, electric utilities and industry, annual supply and disposition, by province, "
            f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2460)",
            "Shape: series (docs/datastandard.md v0). entity statcan_disp:<area>; variable the component as a slug (generation, trade with the United States and its parts, interprovincial receipts and deliveries, electricity available, "
            "electricity used by producers, sales to ultimate customers and its four sectors, unallocated electricity); unit MWh; freq P1Y; ts_utc the year's 1 January; geo CA or CA-<province>; x_component StatCan's name; x_symbol r revised. "
            "The components overlap (totals hold their parts): a sum takes one level.",
            f"The four sales sectors add to total sales within 1 MWh in all {n_sales} area years. Generation plus imports less exports plus receipts less deliveries differs from the electricity available by more than 1 MWh in {off_supply} of {n_avail} area years, "
            f"and producers' use plus sales plus unallocated in {off_use}; both kept as StatCan publishes them. Figures StatCan marks .. have no row: {', '.join(f'{k} {v:,}' for k, v in sorted(withheld.items())) or 'none'}. "
            f"The values in Canadian dollars ({counts.get('value_rows_not_taken', 0):,} rows) are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_electricity_disposition.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0021-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} areas; withheld {withheld}; supply off {off_supply}, use off {off_use} of {n_avail}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0021-01, Electric power, electric "
                                    "utilities and industry, annual supply and disposition", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
