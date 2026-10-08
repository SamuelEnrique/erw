#!/usr/bin/env python3
"""The Census Bureau's population of metropolitan areas, for the weights of the grids' weather stations (session 129,
approved pull: the Bureau's metropolitan-area population estimates, USD 0, ceiling 5,000 rows).

Energy Research Warehouse (ERW) connector. One series table,

    warehouse/output/census_metro_population.csv

from the Population Estimates Program's file of core based statistical areas, vintage 2025
(cbsa-est2025-alldata.csv: every metropolitan and micropolitan area, its metropolitan divisions and its counties, with
the estimates base of 1 April 2020 and the estimates of 1 July 2020 to 2025).

    python warehouse/connectors/census_metro_population.py              # the file (from the raw files once pulled)
    python warehouse/connectors/census_metro_population.py --offline

Rows written, for metropolitan statistical areas only:
  entity census:cbsa:<code>                the whole area
  entity census:cbsa:<code>:<state FIPS>   the part of the area in one state: the sum of the area's counties in that
                                           state, as the file lists them (written for every area, so a grid that
                                           holds part of an area can be weighted by that part)
  variables population_base_2020 (the estimates base, 1 April 2020; ts_utc 2020-04-01) and population_2025 (the
  estimate of 1 July 2025; ts_utc 2025-07-01), unit count. node is the Bureau's name for the area.

Ceiling: 5,000 rows, counted as the data rows of the file. Before the file is pulled its first 20,000 bytes are read
and its rows estimated from its size; the pull stops if the estimate passes the ceiling. Values are the Bureau's,
unchanged; the parts by state are sums of the Bureau's county rows. License: public (terms quoted in
docs/methods/demand_weather.md).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "census_metro_population"
URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/metro/totals/cbsa-est2025-alldata.csv"
PAGE = "https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-metro-and-micro-statistical-areas.html"
SOURCE = "census:popest_cbsa"
UA = {"User-Agent": "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)"}
CEILING = 5_000
MSA = "Metropolitan Statistical Area"
COUNTY = "County or equivalent"
VARS = (("population_base_2020", "ESTIMATESBASE2020", "2020-04-01T00:00:00Z"), ("population_2025", "POPESTIMATE2025", "2025-07-01T00:00:00Z"))


def estimate_rows(log):
    """The file's rows, estimated from its size and its first 20,000 bytes, before it is pulled."""
    size = int(requests.head(URL, headers=UA, timeout=60).headers["Content-Length"])
    part = requests.get(URL, headers={**UA, "Range": "bytes=0-19999"}, timeout=60).content.decode("latin-1").split("\n")
    whole = part[1:-1]
    est = round((size - len(part[0])) / (sum(len(x) + 1 for x in whole) / len(whole)))
    log(f"  {URL}: {size:,} bytes, about {est:,} rows by its first {len(whole)} rows")
    return est


def shape(text, url, retrieved):
    """The file as the table's rows, and the number of data rows the file holds."""
    d = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    n = len(d)
    need = {"CBSA", "MDIV", "STCOU", "NAME", "LSAD", "ESTIMATESBASE2020", "POPESTIMATE2025"}
    if not need <= set(d.columns):
        raise RuntimeError(f"the file's columns lack {sorted(need - set(d.columns))}")
    msa = d[d["LSAD"] == MSA]
    codes = set(msa["CBSA"])
    names = dict(zip(msa["CBSA"], msa["NAME"]))
    counties = d[(d["LSAD"] == COUNTY) & d["CBSA"].isin(codes)].copy()
    counties["state"] = counties["STCOU"].str[:2]
    rows = []
    for var, col, ts in VARS:
        for code, name, v in zip(msa["CBSA"], msa["NAME"], msa[col]):
            rows.append(dict(entity=f"census:cbsa:{code}", variable=var, ts_utc=ts, value=int(v), node=name, x_state="", x_counties=""))
        part = counties.assign(v=pd.to_numeric(counties[col])).groupby(["CBSA", "state"])["v"].agg(["sum", "size"]).reset_index()
        for code, state, v, k in zip(part["CBSA"], part["state"], part["sum"], part["size"]):
            rows.append(dict(entity=f"census:cbsa:{code}:{state}", variable=var, ts_utc=ts, value=int(v), node=names[code], x_state=state, x_counties=int(k)))
        # the counties of an area add to the area: the file's own check
        tot = part.groupby("CBSA")["sum"].sum()
        off = [c for c, v in zip(msa["CBSA"], msa[col]) if int(tot.get(c, -1)) != int(v)]
        if off:
            raise RuntimeError(f"{var}: the counties of {len(off)} areas do not add to the area (first {off[:3]})")
    t = pd.DataFrame(rows)
    t["unit"], t["freq"], t["geo"], t["market"] = "count", "", "US", ""
    t["source"], t["source_url"], t["retrieved_at"], t["vintage"] = SOURCE, url, retrieved, "2025"
    return t, n, len(msa)


def main(argv=None):
    ap = argparse.ArgumentParser(description="the Census Bureau's population of metropolitan areas")
    ap.add_argument("--offline", action="store_true", help="read the raw file only; no request is made")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        log(f"ERW {NAME} run {run_id}; ceiling {CEILING:,} rows")
        if not args.offline:
            if not ip.raw_cached(NAME, URL):
                # before the raw capture is opened: the two small requests of the estimate are not the file, and a
                # header request's empty answer must never be kept under the file's address
                est = estimate_rows(log)
                if est > CEILING:
                    raise RuntimeError(f"the file holds about {est:,} rows, over the ceiling of {CEILING:,}: not pulled")
            ip.RAW.open(NAME, run_id)
        blob, rec = ip.fetch_raw(NAME, URL, log, offline=args.offline, headers=UA)
        t, n, areas = shape(blob.decode("latin-1"), URL, ip.utc_iso(pd.Timestamp(str(rec["retrieved_at"]))))
        if n > CEILING:
            raise RuntimeError(f"the file holds {n:,} rows, over the ceiling of {CEILING:,}: nothing written")
        cols = ip.SERIES_COLS + ["x_state", "x_counties"]
        header = [
            "Energy Research Warehouse (ERW): the Census Bureau's population of metropolitan statistical areas, whole and by state part, the estimates base of 1 April 2020 and the estimate of 1 July 2025 (session 129)",
            "Shape: series (docs/datastandard.md v0). entity census:cbsa:<code> is a whole area; census:cbsa:<code>:<state FIPS> is its part in one state, the sum of the area's x_counties counties there as the file lists them. "
            "population_base_2020 (ts_utc 2020-04-01) and population_2025 (ts_utc 2025-07-01), unit count; node is the Bureau's name for the area; vintage 2025.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_metro_population.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Raw files: warehouse/raw/{NAME}/ (not in git; manifest.csv lists the file and its address)",
            f"Source: {SOURCE} U.S. Census Bureau, Population Estimates Program, Metropolitan and Micropolitan Statistical Areas Totals, vintage 2025, {PAGE}",
            f"  file: {URL}" + (f" (Last-Modified {rec['last_modified']})" if rec.get("last_modified") else ""),
            f"Rows in the file: {n:,} of the {CEILING:,} ceiling (areas, their divisions and their counties). Written: {areas} metropolitan statistical areas and their parts by state; micropolitan areas and divisions are not written.",
            "Values are the Bureau's, unchanged; a part by state is the sum of the Bureau's county rows, and every area's counties add to the area (checked each run).",
            "License: public. Cite: U.S. Census Bureau, Population Division, Annual Estimates of the Resident Population for Metropolitan Statistical Areas, vintage 2025. The Bureau's terms are quoted in docs/methods/demand_weather.md.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)
        ip.write_csv(t[cols], NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Census Bureau", report="Population Estimates Program, Metropolitan and Micropolitan Statistical Areas Totals (vintage 2025)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows; {n} rows in the file"))
        print(f"{NAME}: {len(t):,} rows written; {n:,} rows in the file of {CEILING:,} allowed; {areas} metropolitan areas")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
