#!/usr/bin/env python3
"""The Census Bureau's Building Permits Survey by state: new housing units, buildings and their value authorized by
building permits, by structure type (1 unit, 2 units, 3 and 4 units, 5 or more), a year (session 2149's chain 092,
session 2154: the new homes that add load to the grid).

Energy Research Warehouse (ERW) connector. One series table from the survey's annual state files (plain text, comma
separated):

    https://www2.census.gov/econ/bps/State/st<year>a.txt

    census_bps_state_annual   entity census_bps:<state postal code>; variables units_<type>, buildings_<type> (count) and
               value_<type> (USD: the Bureau's thousands of dollars times 1,000), type 1_unit, 2_units, 3_4_units or
               5_plus_units; ts_utc 1 January of the year; freq P1Y; geo US-<state>; node the state as the Bureau names
               it; x_fips the state's FIPS code; x_code the code the year's file gives it (Puerto Rico 43 and the Virgin
               Islands 52 in the 2015 file, 72 and 78 later): areas are matched by the Bureau's names

The figures are the Bureau's estimates (its columns before the "rep" columns, which hold the reported permits only; the
estimates add imputation for permit offices that did not report). Each file must hold the two header rows read below,
the states, DC, Puerto Rico, the Virgin Islands (and American Samoa from 2025), the regions, divisions and the United States; the states and DC
must sum to the United States row in every count, and in value within 10 thousand dollars (the Bureau rounds
each area's value), or the run stops. The regions, divisions and the United States are
checked and not kept. A row of another year, an area name not in the map or a figure that is not a whole number stops
the run. Nothing is filled. Months are not taken: the monthly files are one a month (about 140 from 2015), past a
session's ceiling; the current year's year-to-date file is not mixed into a yearly series.

    python warehouse/connectors/census_bps.py [--offline] [--out-dir DIR] [--first YEAR] [--last YEAR]

Ceiling: one request a year (2015 to 2025 by default), two seconds apart, saved in warehouse/raw/census_bps/ and reused
(a past year's file does not change). www2.census.gov's robots file names only some crawlers, none of them every
reader. License: may be public (the Census Bureau, read 17); cite the U.S. Census Bureau, Building Permits Survey.
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "census_bps"
SOURCE = "census:bps_state_annual"
HOST = "www2.census.gov"
BASE = "https://www2.census.gov/econ/bps/State/"
TABLE = "census_bps_state_annual"
FIRST, LAST = 2015, 2025
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_fips", "x_code"]
ROUNDING = 10  # thousands of dollars: the most the states' values may differ from the nation's, by rounding
TYPES = ["1_unit", "2_units", "3_4_units", "5_plus_units"]
HEAD1 = ["Survey", "FIPS", "Region", "Division", "State", "", "1-unit", "", "", "2-units", "", "", "3-4 units", "", "", "5+ units"]
HEAD2 = ["Date", "State", "Code", "Code", "Name"] + ["Bldgs", "Units", "Value"] * 8
FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA",
        "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA",
        "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY",
        "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX",
        "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY", "60": "AS", "72": "PR", "78": "VI"}
TERRITORIES = {"60", "72", "78"}  # American Samoa from the 2025 file
# the areas by the Bureau's names (its codes changed: Puerto Rico is 43 and the Virgin Islands 52 in the 2015 file)
NAMES = {"Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05", "California": "06", "Colorado": "08",
         "Connecticut": "09", "Delaware": "10", "District of Columbia": "11", "Florida": "12", "Georgia": "13", "Hawaii": "15",
         "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20", "Kentucky": "21", "Louisiana": "22",
         "Maine": "23", "Maryland": "24", "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28",
         "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32", "New Hampshire": "33", "New Jersey": "34",
         "New Mexico": "35", "New York": "36", "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40",
         "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46",
         "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50", "Virginia": "51", "Washington": "53",
         "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56", "American Samoa": "60", "Puerto Rico": "72",
         "Virgin Islands": "78"}


def whole(x, where):
    s = str(x).strip()
    if not s.lstrip("-").isdigit():
        raise RuntimeError(f"{where}: not a whole number: {x!r}")
    return int(s)


def parse(text, year, base, rounding):
    lines = text.splitlines()
    h1 = [c.strip() for c in lines[0].split(",")]
    h2 = [c.strip() for c in lines[1].split(",")]
    if h1[:16] != HEAD1 or h2 != HEAD2:
        raise RuntimeError(f"{year}: the header rows are not as read: {h1[:8]} / {h2[:8]}")
    out, total, seen = [], None, set()
    sums = [0] * 12
    for k, line in enumerate(lines[2:], start=3):
        f = [c.strip() for c in line.split(",")]
        if len(f) < 2 or not any(f):
            continue
        if len(f) != len(HEAD2):
            raise RuntimeError(f"{year} line {k}: {len(f)} fields, not {len(HEAD2)}")
        if f[0] != f"{year}99":
            raise RuntimeError(f"{year} line {k}: survey date {f[0]!r}, not {year}99")
        code, name = f[1], f[4]
        nums = [whole(x, f"{year} {name}") for x in f[5:17]]  # the estimates: four types of buildings, units, value
        if code == "US":
            total = nums
            continue
        if code[0] in "RD" and not code.isdigit():
            continue  # a region or division: not kept
        if name not in NAMES:
            raise RuntimeError(f"{year} line {k}: an area not in the map: {code!r} {name!r}")
        fips = NAMES[name]
        if fips in seen:
            raise RuntimeError(f"{year}: {name} given twice")
        seen.add(fips)
        if fips not in TERRITORIES:
            sums = [a + b for a, b in zip(sums, nums)]
        st = FIPS[fips]
        for i, t in enumerate(TYPES):
            for j, (var, unit, factor) in enumerate((("buildings", "count", 1), ("units", "count", 1), ("value", "USD", 1000))):
                out.append(dict(base, entity=f"census_bps:{st.lower()}", variable=f"{var}_{t}", ts_utc=f"{year}-01-01T00:00:00Z",
                                value=float(nums[3 * i + j] * factor), unit=unit, freq="P1Y", geo=f"US-{st}", market="", node=name,
                                x_fips=fips, x_code=code))
    if total is None:
        raise RuntimeError(f"{year}: no United States row")
    missing = sorted(set(FIPS) - TERRITORIES - seen)
    if missing:
        raise RuntimeError(f"{year}: states missing: {missing}")
    # the counts must match exactly; the values (thousands of dollars) are rounded by area, so within ROUNDING
    for i, (a, b) in enumerate(zip(sums, total)):
        if (i % 3 != 2 and a != b) or (i % 3 == 2 and abs(a - b) > ROUNDING):
            raise RuntimeError(f"{year}: the states and DC sum to {sums}, the United States row is {total}")
    rounding[year] = max(abs(a - b) for i, (a, b) in enumerate(zip(sums, total)) if i % 3 == 2)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Census Bureau's Building Permits Survey by state, a year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--first", type=int, default=FIRST)
    ap.add_argument("--last", type=int, default=LAST)
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
        rows, latest, rounding = [], "", {}
        for year in range(args.first, args.last + 1):
            url = f"{BASE}st{year}a.txt"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content.decode("latin-1"), year, base, rounding)
            log(f"  {year}: {len(got):,} rows")
            rows += got
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Census Bureau, Building Permits Survey, new housing units, buildings and value authorized by "
            f"building permits by state and structure type, {args.first} to {args.last}, a year (session 2154)",
            "Shape: series (docs/datastandard.md v0). entity census_bps:<state>; variables units_<type> and buildings_<type> (count), value_<type> "
            "(USD, the Bureau's thousands times 1,000), type 1_unit, 2_units, 3_4_units, 5_plus_units; freq P1Y; ts_utc 1 January; geo "
            "US-<state>; node the state; x_fips the state's FIPS code; x_code the code the year's file gives it.",
            f"The Bureau's estimates (with imputation for offices that did not report), not its reported-only columns. {s.entity.nunique()} areas: "
            "the states, DC, Puerto Rico, the Virgin Islands and, from 2025, American Samoa; the states and DC sum to the United States row in every count and year, and in "
            f"value within the Bureau's rounding (at most {max(rounding.values())} thousand dollars a year, checked); "
            "the regions, divisions and the nation are not kept. Years, not months. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_bps.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Census Bureau, Building Permits Survey, annual state files, {BASE}",
            f"  access: {BASE}st<year>a.txt, {args.first} to {args.last}",
            "License: may be public (the Census Bureau, see license_verdicts.csv; its name is not to imply endorsement). Cite the U.S. Census "
            "Bureau, Building Permits Survey.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} areas, {args.first} to {args.last}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Census Bureau", report="Building Permits Survey: annual state files",
                                    report_url=BASE, document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
