#!/usr/bin/env python3
"""Statistics Canada's annual supply and demand of primary and secondary energy by province and fuel (table 25-10-0029-01,
the Report on Energy Supply and Demand): production, trade, transformation to electricity, coke and refined products,
and final use by sector, for 29 fuels, a year from 1995 (session 2383, chain 112: a third source of the session's own
choosing, the yearly balance behind statcan_electricity_trade_monthly and statcan_petroleum_products_monthly).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100029-eng.zip

    statcan_energy_balance_annual   entity statcan_eb:<area>:<fuel> (area ca, atl for the Atlantic provinces, ter for
               Yukon, the Northwest Territories and Nunavut together, or a province or territory's postal code, lower
               case; fuel a slug of StatCan's fuel type); variable a slug of the supply and demand line (production,
               exports, imports, net_supply, transformed_to_electricity_by_utilities, energy_use_final_demand,
               residential, total_transportation, ...); unit MWh (StatCan's terajoules times 1,000,000/3,600); ts_utc
               the year's 1 January; freq P1Y; geo CA, CA-<province> or blank for the two groups of provinces or
               territories; node the area, fuel and line as StatCan names them; x_fuel and x_line StatCan's names;
               x_vector; x_terminated t where StatCan has ended the series

Signs (session 2380's note): exports, stock variation (positive for a build) and the transformation lines are
positive and subtracted, except steam's own "transformed to steam generation", which is its output and negative;
inter-regional and inter-product transfers and other adjustments are signed and added (Canada's inter-regional line is
not zero in every year). The statistical difference is net supply less producer consumption, non-energy use and final
demand; final demand is the six sectors without it, though StatCan's metadata lists it under final demand. Electricity's
demand lines sit under "Primary electricity, hydro and nuclear" and cover all electricity; "Secondary electricity,
thermal" has production, availability and net supply only. Primary electricity's statistical difference includes the
secondary net supply from 2010, leaves it out in 2005 to 2009 (about -100 TWh for Canada each year, not a measured
imbalance) and has no value before 2005. By the figures, primary electricity's production holds wind, solar and tidal
too: from 2016 to 2024 it exceeds statcan_electricity_generation_monthly's hydraulic and nuclear turbines by those
sources' generation within 4 TWh a year; StatCan does not say so. Anthracite has no value in any line.

StatCan's fuels and lines overlap: totals (total primary and secondary energy, primary energy, total coal, total refined
petroleum products; net supply, energy use final demand, total industrial, total transportation and the like) hold
their parts, and a sum takes one level. A figure StatCan marks ".." (not available), "x" (suppressed to meet the
Statistics Act's confidentiality) or "F" (too unreliable) has no row, and the header counts each. A unit other than
terajoules, a scalar factor other than units, an area not in the map, a year that does not read or a key given twice
stops the run. Nothing is filled.

    python warehouse/connectors/statcan_energy_balance.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline, since StatCan revises it at the same address). The robots
file of www150.statcan.gc.ca asks a crawl delay of 2 seconds and disallows its framework and error paths, not /n1/ or a
.zip; it names no AI agent (session 2383). License: public (the Statistics Canada Open Licence: use, reproduce,
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

CONNECTOR = "statcan_energy_balance"
SOURCE = "statcan:25-10-0029-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100029-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002901"
TABLE = "statcan_energy_balance_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_fuel", "x_line", "x_vector", "x_terminated"]
TJ_TO_MWH = 1_000_000 / 3_600
AREAS = {"Canada": ("ca", "CA"), "Atlantic provinces": ("atl", ""), "Newfoundland and Labrador": ("nl", "CA-NL"),
         "Prince Edward Island": ("pe", "CA-PE"), "Nova Scotia": ("ns", "CA-NS"), "New Brunswick": ("nb", "CA-NB"),
         "Quebec": ("qc", "CA-QC"), "Ontario": ("on", "CA-ON"), "Manitoba": ("mb", "CA-MB"), "Saskatchewan": ("sk", "CA-SK"),
         "Alberta": ("ab", "CA-AB"), "British Columbia": ("bc", "CA-BC"),
         "Yukon, Northwest Territories and Nunavut": ("ter", ""), "Yukon": ("yt", "CA-YT"),
         "Northwest Territories": ("nt", "CA-NT"), "Nunavut": ("nu", "CA-NU")}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100029.csv"]:
        raise RuntimeError(f"the zip does not hold 25100029.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Terajoules" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, fuel, line = r["GEO"], r["Fuel type"], r["Supply and demand characteristics"]
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
            ent, var = f"statcan_eb:{code}:{slug(fuel)}", slug(line)
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01-01T00:00:00Z",
                            value=round(float(r["VALUE"]) * TJ_TO_MWH, 3), unit="MWh", freq="P1Y", geo=geo, market="",
                            node=f"{area}: {fuel}: {line}", x_fuel=fuel, x_line=line, x_vector=r["VECTOR"],
                            x_terminated=(r["TERMINATED"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0029-01: supply and demand of primary and secondary energy, a year")
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
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0029-01, supply and demand of primary and secondary energy, by province and fuel, a year, "
            f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2383)",
            "Shape: series (docs/datastandard.md v0). entity statcan_eb:<area>:<fuel>; variable the supply and demand line as a slug; unit MWh (StatCan's terajoules times 1,000,000/3,600); freq P1Y; "
            "ts_utc the year's 1 January; geo CA, CA-<province>, or blank for the Atlantic provinces (atl) and the three territories together (ter); x_fuel, x_line StatCan's names; x_vector; x_terminated t for an ended series. "
            "Fuels and lines overlap (totals hold their parts): a sum takes one level. Exports, stock variation (positive for a build) and transformation are subtracted; transfers and adjustments are signed and added; "
            "the statistical difference is not part of final demand. Electricity's demand lines, under primary electricity, cover all electricity; its statistical difference leaves out secondary net supply in 2005 to 2009. "
            "Primary electricity's production appears to hold wind, solar and tidal too (StatCan does not say).",
            f"Figures StatCan marks .. (not available), x (suppressed for confidentiality) or F (too unreliable) have no row: "
            f"{', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_energy_balance.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0029-01, Supply and demand of primary and secondary energy in terajoules, annual, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0029-01. This does not constitute an endorsement by Statistics Canada of this product.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0029-01, Supply and demand of "
                                    "primary and secondary energy in terajoules, annual", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
