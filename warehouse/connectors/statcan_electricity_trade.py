#!/usr/bin/env python3
"""Statistics Canada's monthly electricity receipts, deliveries and availability by province, the trade with the United
States and between provinces among them (table 25-10-0016-01), in MWh (session 2328, chain 108: the session's own
choice, the electricity Canada sells to and buys from the U.S. grids, beside statcan_electricity_generation_monthly).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100016-eng.zip

    statcan_electricity_trade_monthly   entity statcan_trade:<area> (ca or a province or territory's postal code, lower
               case); variable the component (below, in MWh); ts_utc the month's first day; freq P1M; geo CA or
               CA-<province>; node the area and component as StatCan names them; x_total yes where the component is
               one of StatCan's totals (never summed with its parts); x_vector StatCan's vector id; x_revised r where
               StatCan marks the figure revised

    generation (Total generation); receipts_total, receipts_other_provinces, receipts_us_purchased, receipts_us_other;
    deliveries_total, deliveries_other_provinces, deliveries_us; deliveries_firm_total, deliveries_firm_other_provinces,
    deliveries_firm_us; deliveries_non_firm_total, deliveries_non_firm_other_provinces, deliveries_non_firm_us;
    deliveries_other_total, deliveries_other_us; available_for_use (Total electricity available for use within specific
    geographic border)

A figure StatCan marks ".." (not available), "x" (suppressed to meet the Statistics Act's confidentiality) or "F" (too
unreliable to be published) has no row, and the header counts each. A unit other than megawatt hours, a scalar factor
other than units, an area or component not in the maps, a month that does not read or a key given twice stops the run.
Nothing is filled. All months StatCan publishes are taken (2008 on; the survey is the Monthly Electricity Supply and
Disposition Survey, 2151). Canada's receipts_total and deliveries_total are its trade with the United States only; a
province's are its trade with other provinces and the United States (StatCan's notes 3 and 7), so the provinces'
totals do not add to Canada's. StatCan's note 19: the survey's target population was widened for wind and solar, and
historical comparisons of generation want caution (it gives no date). A negative figure is StatCan's as published
(Alberta's deliveries in February 2016 and August 2018; session 2331's note).

    python warehouse/connectors/statcan_electricity_trade.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline, since StatCan revises it at the same address). The robots
file of www150.statcan.gc.ca asks a crawl delay of 2 seconds and disallows its framework and error paths, not /n1/ or a
.zip; it names no AI agent (session 2328). License: public (the Statistics Canada Open Licence: use, reproduce,
publish, distribute or sell, with attribution and without implying endorsement; see license_verdicts.csv). Quantities
only; no price is taken.
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

CONNECTOR = "statcan_electricity_trade"
SOURCE = "statcan:25-10-0016-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100016-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001601"
TABLE = "statcan_electricity_trade_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_total", "x_vector", "x_revised"]
AREAS = {"Canada": "CA", "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS", "New Brunswick": "NB",
         "Quebec": "QC", "Ontario": "ON", "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC", "Yukon": "YT",
         "Northwest Territories": "NT", "Nunavut": "NU"}
COMPONENTS = {
    "Total generation": "generation",
    "Total receipts": "receipts_total",
    "Receipts from other provinces": "receipts_other_provinces",
    "Purchased receipts from the United States": "receipts_us_purchased",
    "Other receipts from the United States": "receipts_us_other",
    "Total deliveries": "deliveries_total",
    "Deliveries to other provinces": "deliveries_other_provinces",
    "Deliveries to the United States": "deliveries_us",
    "Total firm deliveries": "deliveries_firm_total",
    "Firm deliveries to other provinces": "deliveries_firm_other_provinces",
    "Firm deliveries to the United States": "deliveries_firm_us",
    "Total non-firm deliveries": "deliveries_non_firm_total",
    "Non-firm deliveries to other provinces": "deliveries_non_firm_other_provinces",
    "Non-firm deliveries to the United States": "deliveries_non_firm_us",
    "Total other deliveries": "deliveries_other_total",
    "Other deliveries to the United States": "deliveries_other_us",
    "Total electricity available for use within specific geographic border": "available_for_use",
}


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100016.csv"]:
        raise RuntimeError(f"the zip does not hold 25100016.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Megawatt hours" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, comp = r["GEO"], r["Electric power, components"]
            if area not in AREAS or comp not in COMPONENTS:
                raise RuntimeError(f"an area or component not in the maps: {area!r} {comp!r}")
            if not re.fullmatch(r"\d{4}-\d{2}", r["REF_DATE"]):
                raise RuntimeError(f"a month that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in ("..", "x", "F"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code = AREAS[area]
            ent, var = f"statcan_trade:{code.lower()}", COMPONENTS[comp]
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01T00:00:00Z", value=float(r["VALUE"]),
                            unit="MWh", freq="P1M", geo="CA" if code == "CA" else f"CA-{code}", market="", node=f"{area}: {comp}",
                            x_total="yes" if comp.startswith("Total") else "", x_vector=r["VECTOR"], x_revised=(r["SYMBOL"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0016-01: electricity receipts, deliveries and availability by province, a month")
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
        neg = s[s.value < 0]
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0016-01, electric power generation, monthly receipts, deliveries and availability by province, "
            f"the trade with the United States and between provinces among them, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2328)",
            "Shape: series (docs/datastandard.md v0). entity statcan_trade:<area>; variable the component (generation, receipts_*, deliveries_*, available_for_use; MWh); freq P1M; "
            "ts_utc the month's first day; geo CA or CA-<province>; node the area and component as StatCan names them; x_total yes for StatCan's totals "
            "(never summed with their parts); x_vector; x_revised r where revised.",
            f"Figures StatCan marks .. (not available), x (suppressed for confidentiality) or F (too unreliable) have no row: "
            f"{', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled. Canada's receipts_total and deliveries_total are its trade with the United States only; "
            "a province's include its trade with other provinces, so the provinces' totals do not add to Canada's (StatCan's notes 3 and 7). StatCan's note 19: wind and solar were added to the "
            f"survey's population at a date it does not give; compare generation over the years with caution. {len(neg)} figures are negative, as StatCan publishes them"
            f"{' (' + '; '.join(f'{r.node} {r.ts_utc[:7]}' for r in neg.itertuples()) + ')' if len(neg) else ''}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_electricity_trade.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0016-01, Electric power generation, monthly receipts, deliveries and availability, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0016-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} areas; withheld {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0016-01, Electric power generation, "
                                    "monthly receipts, deliveries and availability", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
