#!/usr/bin/env python3
"""Statistics Canada's installed electricity generating capacity by type of generation and class of producer, by province,
a year from 2006 (table 25-10-0022-01; session 2418, chain 114: a source of the session's own choosing, beside
statcan_electricity_trade and StatCan's generation tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statcan_generating_capacity_annual.csv,
from StatCan's full-table CSV (a zip), one request:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100022-eng.zip

    entity    statcan_cap:<area>:<class>: area ca or a province's or territory's two letters; class all (total all
              classes of electricity producer), public (public electric utilities), private (private electric
              utilities) or industry (industries)
    variable  capacity_<type>: total, hydraulic_turbine, wind_power_turbine, tidal_power_turbine, solar_power,
              geothermal, other_non_combustibles, total_thermal, conventional_steam_turbine, nuclear_steam_turbine,
              combustion_turbine, internal_combustion_turbine
    unit      MW: StatCan's kilowatts divided by 1,000
    ts_utc    the year's 1 January; freq P1Y; geo CA or CA-<province>
    x_*       StatCan's class and type names, the vector, its symbol (r revised) and terminated flag

A figure StatCan marks .. (not available) has no row; nothing is filled. 2012 has no row at all: StatCan's file gives ..
for all 322 of its figures. StatCan's notes (the metadata file): capacity is gross, "measured at the output terminals of
all generating units in a station, without deducting station service requirements" (note 3); from 2015 the survey's
population grew from 400 to 1,200 establishments, renewable companies added, so comparisons with earlier years need
caution (note 12); solar includes systems below 100 kW only from 2024 (note 7). No note says at what date in the year
capacity is counted. Ontario's solar capacity falls from 2,295.9 MW (2017) to 1,409.9 MW (2019) while its generation
rises; no note explains it (session 2415's note). Each class's types should add to its total,
and the thermal kinds to total thermal; the header counts the area, class and year cells where they do not, within
1 MW, kept as StatCan publishes them. An area, class, type, unit, status or year not as read, or a key given twice,
stops the run.

    python warehouse/connectors/statcan_generating_capacity.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/statcan_generating_capacity/ with --offline. www150.statcan.gc.ca's
robots file asks a crawl delay of 2 seconds and disallows paths ending .csv, not the /n1/tbl/csv/ zip, and names no AI
agent (session 2418). License: public (the Statistics Canada Open Licence; the record's verdict).
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

CONNECTOR = "statcan_generating_capacity"
SOURCE = "statcan:25-10-0022-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100022-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201"
TABLE = "statcan_generating_capacity_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_class", "x_type", "x_vector", "x_symbol", "x_terminated"]
AREAS = {"Canada": ("ca", "CA"), "Newfoundland and Labrador": ("nl", "CA-NL"), "Prince Edward Island": ("pe", "CA-PE"),
         "Nova Scotia": ("ns", "CA-NS"), "New Brunswick": ("nb", "CA-NB"), "Quebec": ("qc", "CA-QC"),
         "Ontario": ("on", "CA-ON"), "Manitoba": ("mb", "CA-MB"), "Saskatchewan": ("sk", "CA-SK"),
         "Alberta": ("ab", "CA-AB"), "British Columbia": ("bc", "CA-BC"), "Yukon": ("yt", "CA-YT"),
         "Northwest Territories": ("nt", "CA-NT"), "Nunavut": ("nu", "CA-NU")}
CLASSES = {"Total all classes of electricity producer": "all", "Electricity producer, public electric utilities": "public",
           "Electricity producer, private electric utilities": "private", "Electricity producer, industries": "industry"}
TYPES = {"Total installed capacity": "total", "Hydraulic turbine": "hydraulic_turbine", "Wind power turbine": "wind_power_turbine",
         "Tidal power turbine": "tidal_power_turbine", "Solar power": "solar_power", "Geothermal": "geothermal",
         "Other non-combustibles": "other_non_combustibles", "Total thermal": "total_thermal",
         "Conventional steam turbine": "conventional_steam_turbine", "Nuclear steam turbine": "nuclear_steam_turbine",
         "Combustion turbine": "combustion_turbine", "Internal combustion turbine": "internal_combustion_turbine"}
PARTS = {"total": ["hydraulic_turbine", "wind_power_turbine", "tidal_power_turbine", "solar_power", "geothermal",
                   "other_non_combustibles", "total_thermal"],
         "total_thermal": ["conventional_steam_turbine", "nuclear_steam_turbine", "combustion_turbine", "internal_combustion_turbine"]}
TOL = 1.0   # MW


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100022.csv"]:
        raise RuntimeError(f"the zip does not hold 25100022.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Kilowatts" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, cls, typ = r["GEO"], r["Class of electricity producer"], r["Type of electricity generation"]
            if area not in AREAS or cls not in CLASSES or typ not in TYPES:
                raise RuntimeError(f"an area, class or type not in the map: {area!r} {cls!r} {typ!r}")
            if not re.fullmatch(r"\d{4}", r["REF_DATE"]):
                raise RuntimeError(f"a year that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in ("..", "x", "F"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code, geo = AREAS[area]
            ent, var = f"statcan_cap:{code}:{CLASSES[cls]}", "capacity_" + TYPES[typ]
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01-01T00:00:00Z",
                            value=round(float(r["VALUE"]) / 1000.0, 3), unit="MW", freq="P1Y", geo=geo, market="",
                            node=f"{area}: {cls}: {typ}", x_class=cls, x_type=typ, x_vector=r["VECTOR"],
                            x_symbol=(r["SYMBOL"] or "").strip(), x_terminated=(r["TERMINATED"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def sum_check(s):
    """Each total against its parts, where the total has a row: the cells compared and those off by more than TOL MW."""
    w = s.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value", aggfunc="first")
    compared, off = 0, []
    for tot, parts in PARTS.items():
        col = "capacity_" + tot
        if col not in w.columns:
            continue
        have = [c for c in ("capacity_" + p for p in parts) if c in w.columns]
        for k, v in w[col].dropna().items():
            compared += 1
            gap = w.loc[k, have].fillna(0).sum() - v
            if abs(gap) > TOL:
                off.append((k[0], k[1][:4], tot, round(gap, 3)))
    return compared, off


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0022-01: installed generating capacity by type and class of producer, a year")
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
        compared, off = sum_check(s)
        for e, y, tot, gap in off:
            log(f"  the parts less {tot}: {gap:g} MW, {e} {y}")
        worst = max(off, key=lambda o: abs(o[3])) if off else None
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0022-01, installed plants, annual generating capacity by type of electricity generation and class of producer, by province, "
            f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2418)",
            "Shape: series (docs/datastandard.md v0). entity statcan_cap:<area>:<class> (class all, public utilities, private utilities or industry); variable capacity_<type> (total, hydraulic_turbine, wind_power_turbine, tidal_power_turbine, "
            "solar_power, geothermal, other_non_combustibles, total_thermal and its conventional_steam_turbine, nuclear_steam_turbine, combustion_turbine, internal_combustion_turbine); unit MW (StatCan's kilowatts divided by 1,000); "
            "freq P1Y; ts_utc the year's 1 January; geo CA or CA-<province>; x_class, x_type StatCan's names; x_vector; x_symbol r revised. Types and classes overlap (totals hold their parts): a sum takes one level. "
            "Capacity is gross, at the generators' terminals before station service (StatCan's note 3); the survey grew from 400 to 1,200 establishments in 2015 (note 12); solar below 100 kW counts only from 2024 (note 7); "
            "2012 has no figure (all .. in StatCan's file).",
            f"Figures StatCan marks .. (not available) have no row: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled. "
            f"The parts equal their total within {TOL:g} MW in {compared - len(off):,} of {compared:,} cells; the other {len(off)} are kept as StatCan publishes them and listed in the run log"
            + (f" (the largest {worst[3]:g} MW, {worst[0]} {worst[1]}, {worst[2]})." if worst else "."),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_generating_capacity.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0022-01, Installed plants, annual generating capacity by type of electricity generation, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0022-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series; withheld {counts}; sums off in {len(off)} of {compared}; worst {worst}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0022-01, Installed plants, annual "
                                    "generating capacity by type of electricity generation", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
