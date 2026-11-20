#!/usr/bin/env python3
"""County population: the 2020 census count and the Census Bureau's yearly estimates of 1 July from 2018 on (session
7802, chain 401 part C, table 4).

Energy Research Warehouse (ERW) connector. One series table,

    warehouse/output/census_county_population.csv

from two products of the Bureau's Population Estimates Program on www2.census.gov:
  - the 2010 to 2020 intercensal county estimates, one file a state
    (datasets/2010-2020/intercensal/county/asrh/cc-est2020int-agesex-<state FIPS>.csv): YEAR 12, "4/1/2020 Census
    population" (the 2020 Modified Age and Race Census file), and YEAR 10 and 11, the estimates of 1 July 2018 and 2019;
  - the vintage 2025 county totals (datasets/2020-2025/counties/totals/co-est2025-alldata.csv): POPESTIMATE2020 to
    POPESTIMATE2025, the estimates of 1 July 2020 to 2025.

Rows: entity census:county:<state FIPS><county FIPS> (five digits), variables population_census_2020 (ts_utc
2020-04-01) and population_estimate (ts_utc 1 July of each year, 2018 to 2025), unit count, freq P1Y for the
estimates, x_product the file the row came from (intercensal 2010-2020, or vintage 2025), node the Bureau's county name,
x_state the state's name. Values are the Bureau's, unchanged. The two products are as the Bureau published them: 2018
and 2019 are intercensal estimates on 2020 boundaries, 2020 to 2025 the vintage 2025 series; they are not spliced or
adjusted. Connecticut: the vintage 2025 file counts its nine planning regions (09110 to 09190) where the intercensal
files count its eight former counties (09001 to 09015); each is kept under its own code. Public (U.S. Government work).

    python warehouse/connectors/census_county_population.py [--out-dir DIR]
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "census_county_population"
SOURCE_INT = "census:popest/intercensal_county_2010_2020"
SOURCE_V25 = "census:popest/co-est2025-alldata"
INT_BASE = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/county/asrh/"
INT_PAGE = "https://www.census.gov/data/datasets/time-series/demo/popest/intercensal-2010-2020-counties.html"
V25_URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv"
V25_PAGE = "https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-total.html"
UA = {"User-Agent": "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)"}
STATES = ["01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16", "17", "18", "19", "20", "21", "22",
          "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41",
          "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"]
INT_YEARS = {12: ("population_census_2020", "2020-04-01T00:00:00Z"), 10: ("population_estimate", "2018-07-01T00:00:00Z"),
             11: ("population_estimate", "2019-07-01T00:00:00Z")}
COLS = ip.SERIES_COLS + ["x_state", "x_product"]


def get(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=120)
            if r.status_code == 200 and r.content[:6] == b"SUMLEV":
                return r
            raise RuntimeError(f"{url}: HTTP {r.status_code}, {len(r.content)} bytes, not the CSV")
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW county population (session 7802)")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        ip.RAW.open(NAME, run_id)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        parts = []
        for st in STATES:
            url = f"{INT_BASE}cc-est2020int-agesex-{st}.csv"
            r = get(url)
            d = pd.read_csv(io.BytesIO(r.content), dtype=str, encoding="latin-1", usecols=["SUMLEV", "STATE", "COUNTY", "STNAME", "CTYNAME", "YEAR", "POPESTIMATE"])
            d = d[(d["SUMLEV"] == "050") & d["YEAR"].astype(int).isin(INT_YEARS)]
            parts.append(pd.DataFrame({
                "entity": "census:county:" + d["STATE"].str.zfill(2) + d["COUNTY"].str.zfill(3),
                "variable": d["YEAR"].astype(int).map(lambda y: INT_YEARS[y][0]),
                "ts_utc": d["YEAR"].astype(int).map(lambda y: INT_YEARS[y][1]), "value": pd.to_numeric(d["POPESTIMATE"]),
                "freq": d["YEAR"].astype(int).map(lambda y: "" if y == 12 else "P1Y"), "node": d["CTYNAME"],
                "x_state": d["STNAME"], "source": SOURCE_INT, "source_url": url, "x_product": "intercensal 2010-2020"}))
            log(f"  {url}: {len(d)} rows")
            time.sleep(1)
        r = get(V25_URL)
        v = pd.read_csv(io.BytesIO(r.content), dtype=str, encoding="latin-1")
        v = v[v["SUMLEV"] == "050"]
        log(f"  {V25_URL}: {len(v)} counties")
        for y in range(2020, 2026):
            parts.append(pd.DataFrame({
                "entity": "census:county:" + v["STATE"].str.zfill(2) + v["COUNTY"].str.zfill(3), "variable": "population_estimate",
                "ts_utc": f"{y}-07-01T00:00:00Z", "value": pd.to_numeric(v[f"POPESTIMATE{y}"]), "freq": "P1Y",
                "node": v["CTYNAME"], "x_state": v["STNAME"], "source": SOURCE_V25, "source_url": V25_URL,
                "x_product": "vintage 2025"}))
        s = pd.concat(parts, ignore_index=True)
        s["unit"], s["geo"], s["market"], s["retrieved_at"], s["vintage"] = "count", "", "", retrieved, ""
        # geo: the state's ISO 3166-2 code
        abbr = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
                "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
                "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
                "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}
        s["geo"] = "US-" + s["entity"].str[14:16].map(abbr)
        if s["geo"].isna().any() or s["value"].isna().any():
            raise RuntimeError("a row has no state code or no value")
        dup = s.duplicated(["entity", "variable", "ts_utc"]).sum()
        if dup:
            raise RuntimeError(f"{dup} duplicate (entity, variable, ts_utc) rows")
        header = [
            "Energy Research Warehouse (ERW): county population, the 2020 census count and the Census Bureau's estimates of 1 July "
            "2018 to 2025 (session 7802)",
            "Shape: series (docs/datastandard.md v0). entity census:county:<five-digit FIPS>; population_census_2020 (1 April "
            "2020, the 2020 Modified Age and Race Census file as the intercensal files print it) and population_estimate (1 July "
            "of each year), unit count. 2018 and 2019 from the 2010-2020 intercensal estimates, 2020 to 2025 from vintage 2025 "
            "(x_product); not spliced. Connecticut's planning regions (vintage 2025) and former counties (intercensal) each under "
            "their own code. Method: docs/methods/county_population_and_regions.md.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_county_population.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Raw files: warehouse/raw/{NAME}/<run>/ (not in git; manifest.csv lists each file and URL)",
            f"Source: {SOURCE_INT} 2010-2020 Intercensal County Population Estimates (by age group and sex), {INT_PAGE}",
            f"  files: {INT_BASE}cc-est2020int-agesex-<state FIPS>.csv, the 50 states and the District of Columbia",
            f"Source: {SOURCE_V25} County Population Totals, Vintage 2025 (co-est2025-alldata.csv), {V25_PAGE}",
            f"  file: {V25_URL}",
            "License: public (U.S. Census Bureau, U.S. Government work).",
        ]
        ip.write_csv(s[COLS], NAME, header, log, cols=COLS, key=["entity", "variable", "ts_utc"])
        ip.update_sources([
            dict(source=SOURCE_INT, publisher="U.S. Census Bureau", report="2010-2020 Intercensal County Population Estimates (by age group and sex)",
                 report_url=INT_PAGE, document_list=INT_BASE, license="public", tables=[NAME]),
            dict(source=SOURCE_V25, publisher="U.S. Census Bureau", report="County Population Totals, Vintage 2025",
                 report_url=V25_PAGE, document_list=V25_URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique():,} counties")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
