#!/usr/bin/env python3
"""Statistics Canada's monthly electric power generation by province, class of producer and type of generation
(table 25-10-0015-01), in MWh (session 2176, chain 097: Canada's electricity, beside the U.S. grids it trades with).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100015-eng.zip

    statcan_electricity_generation_monthly   entity statcan_gen:<area>:<class>:<type> (area ca or a province or territory's
               postal code, lower case; class all, utilities or industries; type the generation type as a slug, totals
               included as StatCan publishes them); variable generation (MWh); ts_utc the month's first day; freq P1M;
               geo CA or CA-<province>; node the area, class and type as StatCan names them; x_class; x_type; x_total yes
               where the class or the type is one of StatCan's totals (never summed with its parts); x_vector StatCan's
               vector id; x_revised r where StatCan marks the figure revised

A figure StatCan marks ".." (not available) or "x" (suppressed to meet the Statistics Act's confidentiality) has no row,
and the header counts each. A unit other than megawatt hours, a scalar factor other than units, an area or label not in
the maps, or a key given twice stops the run. Nothing is filled. All months StatCan publishes are taken (2008 on).

    python warehouse/connectors/statcan_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline, since StatCan revises it at the same address). The robots
file of www150.statcan.gc.ca asks a crawl delay of 2 seconds and disallows its framework and error paths, not /n1/.
License: may be public (the Statistics Canada Open Licence: use, reproduce, publish, distribute or sell, with
attribution and without implying endorsement; see license_verdicts.csv). Quantities only; no price is taken.
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

CONNECTOR = "statcan_electricity"
SOURCE = "statcan:25-10-0015-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100015-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501"
TABLE = "statcan_electricity_generation_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_class", "x_type", "x_total", "x_vector", "x_revised"]
AREAS = {"Canada": "CA", "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS", "New Brunswick": "NB",
         "Quebec": "QC", "Ontario": "ON", "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC", "Yukon": "YT",
         "Northwest Territories": "NT", "Nunavut": "NU"}
CLASSES = {"Total all classes of electricity producer": "all", "Electricity producers, electric utilities": "utilities",
           "Electricity producers, industries": "industries"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100015.csv"]:
        raise RuntimeError(f"the zip does not hold 25100015.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Megawatt hours" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, cls, typ = r["GEO"], r["Class of electricity producer"], r["Type of electricity generation"]
            if area not in AREAS or cls not in CLASSES:
                raise RuntimeError(f"an area or class not in the maps: {area!r} {cls!r}")
            if not re.fullmatch(r"\d{4}-\d{2}", r["REF_DATE"]):
                raise RuntimeError(f"a month that does not read: {r['REF_DATE']!r}")
            status = r["STATUS"].strip()
            if status in ("..", "x", "F"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code = AREAS[area]
            ent = f"statcan_gen:{code.lower()}:{CLASSES[cls]}:{slug(typ)}"
            key = (ent, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            total = "yes" if (cls.startswith("Total") or typ.startswith("Total")) else ""
            out.append(dict(base, entity=ent, variable="generation", ts_utc=f"{r['REF_DATE']}-01T00:00:00Z", value=float(r["VALUE"]),
                            unit="MWh", freq="P1M", geo="CA" if code == "CA" else f"CA-{code}", market="", node=f"{area}: {cls}: {typ}",
                            x_class=CLASSES[cls], x_type=slug(typ), x_total=total, x_vector=r["VECTOR"], x_revised=r["SYMBOL"].strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0015-01: electricity generation by province, a month")
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
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0015-01, electric power generation, monthly generation by province, "
            f"class of producer and type of generation, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2176)",
            "Shape: series (docs/datastandard.md v0). entity statcan_gen:<area>:<class>:<type>; variable generation (MWh); freq P1M; ts_utc the "
            "month's first day; geo CA or CA-<province>; node the area, class and type as StatCan names them; x_class (all, utilities, "
            "industries); x_type; x_total yes for StatCan's totals (never summed with their parts); x_vector; x_revised r where revised.",
            f"Figures StatCan marks .. (not available) or x (suppressed for confidentiality) have no row: "
            f"{', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_electricity.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0015-01, Electric power generation, monthly generation by type of electricity, {PAGE}",
            f"  access: {URL}",
            "License: may be public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0015-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series; withheld {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0015-01, Electric power generation, "
                                    "monthly generation by type of electricity", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
