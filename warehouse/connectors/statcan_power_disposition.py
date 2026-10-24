#!/usr/bin/env python3
"""Statistics Canada's annual supply and disposition of electric power by province and territory, a year from 2005
(table 25-10-0021-01, "Electric power, electric utilities and industry, annual supply and disposition"): generation,
imports from and exports to the United States, interprovincial receipts and deliveries, the electricity available, the
producers' own use and the sales to ultimate customers by sector (session 2441, chain 117: a second source of the
session's own choosing; it adds each province's balance and its sales by sector to the held monthly trade table
25-10-0016-01).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download (a zip):

    https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip

    statcan_power_disposition_annual   entity statcan_pd:<area> (ca or a province or territory's postal code, lower
               case); variable a slug of StatCan's component (total_generation_of_electricity,
               total_exports_of_electricity_to_the_united_states, interprovincial_deliveries_of_electricity_firm,
               residential_sales_of_electricity, electricity_used_by_producers, ...); unit MWh, as StatCan gives it;
               ts_utc the year's 1 January; freq P1Y; geo CA or CA-<province>; node the area and component as StatCan
               names them; x_component StatCan's name; x_vector; x_revised r where StatCan marks the figure revised

Only the estimate "Electricity quantity" is taken. The estimate "Electricity value" (Canadian dollars, thousands) is not
taken: a foreign country's prices and values are a standing question for the owner. Its rows are counted in the header.
StatCan's components overlap: the totals (total generation, total exports, total imports, total interprovincial
deliveries and receipts, total sales) hold their parts. A sum takes one level. A figure StatCan marks ".." (not
available) or "x" (suppressed to meet the Statistics Act's confidentiality) has no row and is counted. A quantity in a
unit other than megawatt hours, a scalar factor other than units, an estimate, area or status not in the map, a year
that does not read or a key given twice stops the run. Nothing is filled.

    python warehouse/connectors/statcan_power_disposition.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline, since StatCan revises it at the same address). The robots
file of www150.statcan.gc.ca disallows paths ending in .csv for every agent, not a .zip, and names no AI agent (session
2441). License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Quantities only.
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

CONNECTOR = "statcan_power_disposition"
SOURCE = "statcan:25-10-0021-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002101"
TABLE = "statcan_power_disposition_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_component", "x_vector", "x_revised"]
AREAS = {"Canada": ("ca", "CA"), "Newfoundland and Labrador": ("nl", "CA-NL"), "Prince Edward Island": ("pe", "CA-PE"),
         "Nova Scotia": ("ns", "CA-NS"), "New Brunswick": ("nb", "CA-NB"), "Quebec": ("qc", "CA-QC"), "Ontario": ("on", "CA-ON"),
         "Manitoba": ("mb", "CA-MB"), "Saskatchewan": ("sk", "CA-SK"), "Alberta": ("ab", "CA-AB"), "British Columbia": ("bc", "CA-BC"),
         "Yukon": ("yt", "CA-YT"), "Northwest Territories": ("nt", "CA-NT"), "Nunavut": ("nu", "CA-NU")}
ESTIMATES = {"Electricity quantity", "Electricity value"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100021.csv"]:
        raise RuntimeError(f"the zip does not hold 25100021.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            est = r["Estimates"]
            if est not in ESTIMATES:
                raise RuntimeError(f"an estimate not in the map: {est!r}")
            if est == "Electricity value":
                counts["value rows not taken"] = counts.get("value rows not taken", 0) + 1
                continue
            if r["UOM"] != "Megawatt hours" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, comp = r["GEO"], r["Electric power, components"]
            if area not in AREAS:
                raise RuntimeError(f"an area not in the map: {area!r}")
            if not re.fullmatch(r"\d{4}", r["REF_DATE"]):
                raise RuntimeError(f"a year that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in ("..", "x"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code, geo = AREAS[area]
            ent, var = f"statcan_pd:{code}", slug(comp)
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01-01T00:00:00Z", value=round(float(r["VALUE"]), 3),
                            unit="MWh", freq="P1Y", geo=geo, market="", node=f"{area}: {comp}", x_component=comp,
                            x_vector=r["VECTOR"], x_revised=(r["SYMBOL"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0021-01: annual supply and disposition of electric power")
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
        g = s[(s.entity == "statcan_pd:ca") & (s.variable == "total_generation_of_electricity")].set_index("ts_utc").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition, "
            f"by province, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2441)",
            "Shape: series (docs/datastandard.md v0). entity statcan_pd:<area>; variable the component as a slug; unit MWh; ts_utc the year's 1 January; freq P1Y; "
            "geo CA or CA-<province>; x_component StatCan's name; x_vector; x_revised r where StatCan marks a revision. The totals hold their parts: a sum takes one level. "
            "Only the estimate Electricity quantity; Electricity value (Canadian dollars) is not taken.",
            f"{len(s):,} rows; Canada's total generation TWh: " + ", ".join(f"{k[:4]} {v:.1f}" for k, v in g.items() if k[:4] in ("2005", "2010", "2015", "2020", "2023", "2024"))
            + f". Not taken or withheld: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'} (.. not available, x suppressed for confidentiality). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_power_disposition.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0021-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.variable.nunique()} components; not taken or withheld {counts}")
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
