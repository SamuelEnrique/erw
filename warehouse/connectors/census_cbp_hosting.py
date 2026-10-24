#!/usr/bin/env python3
"""The Census Bureau's County Business Patterns for NAICS 518210, data processing, hosting and related services (from
2022 "computing infrastructure providers, data processing, web hosting, and related services"): each state's
establishments, employment and annual payroll, a year (session 2160, chain 092: a source of the session's choosing,
the industry whose data centers are the ERW's sharpest lens on demand for power).

Energy Research Warehouse (ERW) connector. One series table from the CBP state files (zipped text, one a year):

    https://www2.census.gov/programs-surveys/cbp/datasets/<year>/cbp<yy>st.zip

    census_cbp_hosting_annual   entity census_cbp_518210:<state postal code>; variables establishments (count, the
               year's establishments), employment (count, the pay period including 12 March) and annual_payroll (USD,
               the Bureau's thousands times 1,000); ts_utc 1 January of the year; freq P1Y; geo US-<state>; node the state;
               x_emp_noise and x_ap_noise the Bureau's noise flags for employment and payroll (G low, H moderate, J high:
               the Bureau infuses noise to protect establishments' data); x_naics_vintage 2017 or 2022 (the NAICS edition
               the year's file uses)

Each file's header must name fipstate, naics, emp_nf, emp, ap_nf, ap and est; a file with an lfo column gives one row a
state for all legal forms ("-"), which is the one taken. A state given twice, a figure that is not a whole number or a
state code not in the map stops the run. A row the Bureau withholds (flag N with zero) is kept as the Bureau prints it,
with its flag; nothing is filled. The file is read a line at a time and only NAICS 518210's lines are kept.

    python warehouse/connectors/census_cbp_hosting.py [--offline] [--out-dir DIR] [--first YEAR] [--last YEAR]

Ceiling: one request a year (2012 to 2023 by default), two seconds apart, saved in warehouse/raw/census_cbp_hosting/ and
reused (a year's file is released once). www2.census.gov's robots file names only some crawlers, none of them every
reader. License: may be public (the Census Bureau, read 17); cite the U.S. Census Bureau, County Business Patterns.
"""

import argparse
import csv
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "census_cbp_hosting"
SOURCE = "census:cbp_state_518210"
HOST = "www2.census.gov"
BASE = "https://www2.census.gov/programs-surveys/cbp/datasets/"
TABLE = "census_cbp_hosting_annual"
FIRST, LAST = 2012, 2023
NAICS = "518210"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_emp_noise", "x_ap_noise", "x_naics_vintage"]
FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA",
        "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA",
        "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY",
        "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX",
        "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}
NEEDED = ["fipstate", "naics", "emp_nf", "emp", "ap_nf", "ap", "est"]


def url_of(year):
    return f"{BASE}{year}/cbp{year % 100:02d}st.zip"


def whole(x, where):
    s = str(x).strip()
    if not s.isdigit():
        raise RuntimeError(f"{where}: not a whole number: {x!r}")
    return int(s)


def parse(content, year, base):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.lower().endswith(".txt")]
    if len(names) != 1:
        raise RuntimeError(f"{year}: the zip holds not one text file: {z.namelist()}")
    with z.open(names[0]) as f:
        reader = csv.reader(io.TextIOWrapper(f, encoding="latin-1", newline=""))
        head = [h.strip().lower() for h in next(reader)]
        missing = [h for h in NEEDED if h not in head]
        if missing:
            raise RuntimeError(f"{year}: the header lacks {missing}: {head[:12]}")
        ix = {h: head.index(h) for h in NEEDED}
        lfo = head.index("lfo") if "lfo" in head else None
        out, seen = [], set()
        for r in reader:
            if len(r) <= ix["naics"] or r[ix["naics"]].strip() != NAICS:
                continue
            if lfo is not None and r[lfo].strip() != "-":
                continue
            fips = r[ix["fipstate"]].strip().zfill(2)
            if fips not in FIPS:
                raise RuntimeError(f"{year}: a state code not in the map: {fips!r}")
            if fips in seen:
                raise RuntimeError(f"{year}: state {fips} given twice")
            seen.add(fips)
            st = FIPS[fips]
            vals = {"establishments": (whole(r[ix["est"]], f"{year} {st} est"), "count"),
                    "employment": (whole(r[ix["emp"]], f"{year} {st} emp"), "count"),
                    "annual_payroll": (whole(r[ix["ap"]], f"{year} {st} ap") * 1000, "USD")}
            for var, (v, unit) in vals.items():
                out.append(dict(base, entity=f"census_cbp_518210:{st.lower()}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z",
                                value=float(v), unit=unit, freq="P1Y", geo=f"US-{st}", market="", node=st,
                                x_emp_noise=r[ix["emp_nf"]].strip(), x_ap_noise=r[ix["ap_nf"]].strip(),
                                x_naics_vintage="2022" if year >= 2022 else "2017"))
    if not out:
        raise RuntimeError(f"{year}: no line of NAICS {NAICS}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="County Business Patterns, NAICS 518210 (data processing and hosting), by state")
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
        rows, latest, counts = [], "", {}
        for year in range(args.first, args.last + 1):
            content, rec = ip.fetch_raw(CONNECTOR, url_of(year), log, offline=args.offline, headers=UA, timeout=300, pause=2)
            base = dict(source=SOURCE, source_url=url_of(year), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content, year, base)
            counts[year] = len(got) // 3
            log(f"  {year}: {counts[year]} states")
            rows += got
            latest = max(latest, base["retrieved_at"])
            del content
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Census Bureau, County Business Patterns, NAICS 518210 (data processing, hosting and related "
            f"services; from 2022 computing infrastructure providers, data processing, web hosting, and related services), by state, "
            f"{args.first} to {args.last} (session 2160)",
            "Shape: series (docs/datastandard.md v0). entity census_cbp_518210:<state>; variables establishments and employment (count; "
            "employment in the pay period including 12 March) and annual_payroll (USD, the Bureau's thousands times 1,000); freq P1Y; ts_utc "
            "1 January of the year; geo US-<state>; node the state; x_emp_noise and x_ap_noise (the Bureau's noise flags: G low, H moderate, "
            "J high, N not available); x_naics_vintage 2017 or 2022.",
            "All legal forms (the files' lfo \"-\"). States in each year: " + ", ".join(f"{y} {n}" for y, n in counts.items()) + ". The "
            "Bureau infuses noise into employment and payroll to protect establishments; a figure flagged N is kept as printed. NAICS 518210's "
            "2022 title adds computing infrastructure providers, so 2022 on is not strictly the same industry. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_cbp_hosting.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Census Bureau, County Business Patterns, state files, {BASE}",
            f"  access: {BASE}<year>/cbp<yy>st.zip, {args.first} to {args.last}",
            "License: may be public (the Census Bureau, see license_verdicts.csv; its name is not to imply endorsement). Cite the U.S. Census "
            "Bureau, County Business Patterns.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Census Bureau", report="County Business Patterns: state files, NAICS 518210",
                                    report_url=BASE, document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
