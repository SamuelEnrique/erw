#!/usr/bin/env python3
"""Statistics Canada's annual energy consumption of the manufacturing industries by fuel and industry, Canada, a year from
1995 (table 25-10-0025-01, "Manufacturing industries, total annual energy fuel consumption in gigajoules, 31-33") (session
2483, chain 120: a second source of the session's own choosing; the industrial load beside the U.S. markets: each
manufacturing industry's electricity, natural gas and other fuels).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download (a zip):

    https://www150.statcan.gc.ca/n1/tbl/csv/25100025-eng.zip

    statcan_manufacturing_energy_annual   entity statcan_mfg:ca:<NAICS code> (the code in StatCan's brackets, or a slug
               of the name where it has none); variable consumption_<fuel> (the fuel as a slug: electricity,
               natural_gas, heavy_fuel_oil, middle_distillates, propane, coal, ...); unit MWh (StatCan's gigajoules
               divided by 3.6); ts_utc the year's 1 January; freq P1Y; geo CA; node the industry and fuel as StatCan names
               them; x_naics the industry's name; x_fuel the fuel; x_quality StatCan's quality grade A to E (A excellent,
               E use with caution); x_vector

A figure StatCan marks ".." (not available), "x" (suppressed to meet the Statistics Act's confidentiality) or "F" (too
unreliable to be published) has no row, and the header counts each. Industries nest (a three-digit subsector holds its
four-digit groups): a sum takes one level. A unit other than gigajoules, a scalar factor other than units, an area other
than Canada, a status not in the map, a year that does not read or a key given twice stops the run. Nothing is filled.

    python warehouse/connectors/statcan_manufacturing_energy.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline). The robots file of www150.statcan.gc.ca disallows paths
ending in .csv for every agent, not a .zip, and names no AI agent (session 2483). License: public (the Statistics Canada
Open Licence; see license_verdicts.csv). Quantities only.
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

CONNECTOR = "statcan_manufacturing_energy"
SOURCE = "statcan:25-10-0025-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100025-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002501"
TABLE = "statcan_manufacturing_energy_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_naics", "x_fuel", "x_quality", "x_vector"]
GJ_TO_MWH = 1 / 3.6
QUALITY = {"", "A", "B", "C", "D", "E"}
WITHHELD = {"..", "x", "F"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")


def code_of(naics):
    m = re.search(r"\[([0-9A-Z-]+)\]\s*$", naics)
    return m.group(1).lower() if m else slug(naics)


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100025.csv"]:
        raise RuntimeError(f"the zip does not hold 25100025.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Gigajoules" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            if r["GEO"] != "Canada":
                raise RuntimeError(f"an area other than Canada: {r['GEO']!r}")
            if not re.fullmatch(r"\d{4}", r["REF_DATE"]):
                raise RuntimeError(f"a year that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in WITHHELD:
                counts[status] = counts.get(status, 0) + 1
                continue
            if status not in QUALITY:
                raise RuntimeError(f"a status not in the map: {status!r}")
            naics, fuel = r["North American Industry Classification System (NAICS)"], r["Fuel type"]
            ent, var = f"statcan_mfg:ca:{code_of(naics)}", f"consumption_{slug(fuel)}"
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01-01T00:00:00Z",
                            value=round(float(r["VALUE"]) * GJ_TO_MWH, 3), unit="MWh", freq="P1Y", geo="CA", market="",
                            node=f"{naics}: {fuel}", x_naics=naics, x_fuel=fuel, x_quality=status, x_vector=r["VECTOR"]))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0025-01: manufacturing industries' energy consumption by fuel, a year")
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
        el = s[(s.entity == "statcan_mfg:ca:31-33") & (s.variable == "consumption_electricity")].set_index("ts_utc").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0025-01, Manufacturing industries, total annual energy fuel consumption, by industry and fuel, "
            f"Canada, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2483)",
            "Shape: series (docs/datastandard.md v0). entity statcan_mfg:ca:<NAICS code>; variable consumption_<fuel>; unit MWh (StatCan's gigajoules / 3.6); ts_utc the year's 1 January; "
            "freq P1Y; geo CA; x_naics, x_fuel StatCan's names; x_quality StatCan's grade A to E; x_vector. Industries nest: a sum takes one level.",
            f"{len(s):,} rows, {s.entity.nunique()} industries, {s.variable.nunique()} fuels; all manufacturing's electricity, TWh: "
            + ", ".join(f"{k[:4]} {v:.1f}" for k, v in el.items() if k[:4] in ("1995", "2005", "2015", "2020", "2023", "2024"))
            + f". Withheld (.. not available, x confidential, F too unreliable): {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_manufacturing_energy.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0025-01, Manufacturing industries, total annual energy fuel consumption in gigajoules, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0025-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} industries; withheld {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0025-01, Manufacturing industries, "
                                    "total annual energy fuel consumption in gigajoules", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
