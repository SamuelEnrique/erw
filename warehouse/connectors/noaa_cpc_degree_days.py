#!/usr/bin/env python3
"""NOAA's Climate Prediction Center: population-weighted heating and cooling degree days, a day, for each of the 48
contiguous states and for CPC's population regions (the census divisions and the contiguous United States) (session 2006,
chain 056: the weather term of heating and cooling demand, which the ERW held only as station temperatures).

Energy Research Warehouse (ERW) connector. One series table from CPC's degree day files:

    https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/<YEAR>/StatesCONUS.Heating.txt   (and .Cooling.txt)
    https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/<YEAR>/Population.Heating.txt    (and .Cooling.txt)

    noaa_cpc_degree_days_daily   entity cpc_dd:<region>; variables hdd and cdd (unit degF-day: degree days at 65 F, CPC's
                                 population-weighted figure); ts_utc the day (00:00 UTC of the calendar day CPC labels);
                                 freq P1D; geo US-<state> for a state, US for the contiguous states, empty for a census
                                 division (cpc_dd:division_<n>, the number as CPC's file writes it, 1 to 9); node CPC's
                                 region as written; x_regions StatesCONUS or Population (CPC's region set)

Each file's first three lines must name the product ("Daily Heating Degree Days" or "Daily Cooling Degree Days"), the
region set (StatesCONUS, or CensusDivisions in the Population files) and the weights ("Population"); the fourth is "Region|YYYYMMDD|...". A line of a region repeated, a date not
YYYYMMDD, a value not a whole number of at least zero, or an (entity, variable, ts_utc) given twice stops the run; an empty
cell has no row; nothing is filled. The current year's files grow each day and are fetched again on each run.

    python warehouse/connectors/noaa_cpc_degree_days.py [--offline] [--out-dir DIR] [--years 2024 2025 2026]

Ceiling: four requests a year (twelve for the three years by default), saved in warehouse/raw/noaa_cpc_degree_days/ and
reused offline. ftp.cpc.ncep.noaa.gov has no robots file (HTTP 404). License: public (the National Weather Service's
pages, read 8 of license_reads.csv: "in the public domain, unless specifically noted otherwise"; CPC is part of the
NWS's National Centers for Environmental Prediction).
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "noaa_cpc_degree_days"
SOURCE = "noaa:cpc_degree_days"
BASE = "https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/"
TABLE = "noaa_cpc_degree_days_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = [2024, 2025, 2026]
SETS = ["StatesCONUS", "Population"]
REGION_SETS = {"StatesCONUS": "StatesCONUS", "Population": "CensusDivisions"}  # the file's "Regions:" line
KINDS = {"Heating": ("hdd", "Daily Heating Degree Days"), "Cooling": ("cdd", "Daily Cooling Degree Days")}
STATES = {
    "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN",
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT",
    "VA", "VT", "WA", "WI", "WV", "WY",
}
X_COLS = ["x_regions"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(text, region_set, kind, base):
    """The rows of one file."""
    var, product = KINDS[kind]
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    want = [f"Product: {product}", f"Regions: CPC::Regions::{REGION_SETS[region_set]}", "Weights: Population"]
    if [ln.strip() for ln in lines[:3]] != want:
        raise RuntimeError(f"{region_set}.{kind}: the first lines are not as read: {lines[:3]}")
    head = lines[3].split("|")
    if head[0] != "Region":
        raise RuntimeError(f"{region_set}.{kind}: no 'Region|' line")
    days = []
    for d in head[1:]:
        if d == "":
            days.append(None)
            continue
        if not re.fullmatch(r"\d{8}", d):
            raise RuntimeError(f"{region_set}.{kind}: a date not YYYYMMDD: {d!r}")
        days.append(f"{d[:4]}-{d[4:6]}-{d[6:]}T00:00:00Z")
    out, seen = [], set()
    for ln in lines[4:]:
        if not ln.strip():
            continue
        cells = ln.split("|")
        region = cells[0].strip()
        if region in seen:
            raise RuntimeError(f"{region_set}.{kind}: region {region} given twice")
        seen.add(region)
        if region_set == "StatesCONUS":
            if region not in STATES:
                raise RuntimeError(f"a state not in the map: {region}")
            geo, ent = f"US-{region}", f"cpc_dd:{region}"
        else:
            geo = "US" if region.upper() == "CONUS" else ""
            # the Population files number the census divisions (1 to 9) and name CONUS; a number is written division_<n>
            ent = f"cpc_dd:division_{region}" if region.isdigit() else f"cpc_dd:{slug(region)}"
        for ts, v in zip(days, cells[1:]):
            v = v.strip()
            if ts is None or v == "":
                continue
            if not re.fullmatch(r"\d+", v):
                raise RuntimeError(f"{region_set}.{kind}: {region} on {ts[:10]}: a value not a whole number of at least zero: {v!r}")
            out.append(dict(base, entity=ent, variable=var, ts_utc=ts, value=float(v), unit="degF-day", freq="P1D", geo=geo, market="",
                            node=region, x_regions=region_set))
    if not out:
        raise RuntimeError(f"{region_set}.{kind}: no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="CPC's population-weighted degree days, a day, by state and region")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", type=int, nargs="+", default=YEARS)
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
    this_year = dt.datetime.now(dt.timezone.utc).year
    try:
        rows, urls, latest = [], [], ""
        for y in sorted(args.years):
            for region_set in SETS:
                for kind in KINDS:
                    url = f"{BASE}{y}/{region_set}.{kind}.txt"
                    content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=(y == this_year and not args.offline),
                                                headers=UA, timeout=60, pause=1)
                    base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                    rows += parse(content.decode("utf-8", errors="replace"), region_set, kind, base)
                    urls.append(url)
                    latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"an (entity, variable, ts_utc) given twice: {s[s.duplicated(['entity', 'variable', 'ts_utc'])].entity.head(3).tolist()}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): NOAA, National Weather Service, Climate Prediction Center, population-weighted heating and cooling degree "
            "days, a day, for the 48 contiguous states and for CPC's population regions (session 2006)",
            "Shape: series (docs/datastandard.md v0). entity cpc_dd:<state>, cpc_dd:division_<n> (a census division as CPC numbers it, 1 to 9) or cpc_dd:conus; variables hdd and cdd; unit degF-day (degree days at "
            "65 F, weighted by population as CPC computes them); freq P1D; ts_utc the day CPC labels; geo US-<state>, US for CONUS, empty for a census "
            "division; x_regions StatesCONUS or Population.",
            f"{s.entity.nunique()} regions; {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}; years {', '.join(str(y) for y in sorted(args.years))}. "
            "An empty cell has no row. Nothing is filled. The current year's files grow each day.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_cpc_degree_days.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA Climate Prediction Center, Degree Days Statistics, {BASE}",
            f"  access: {BASE}<YEAR>/{{StatesCONUS,Population}}.{{Heating,Cooling}}.txt ({len(urls)} files)",
            'License: public (National Weather Service: "in the public domain, unless specifically noted otherwise"; cite "NOAA Climate Prediction Center").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} regions, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="NOAA National Weather Service, Climate Prediction Center",
                                    report="Degree Days Statistics: population-weighted daily heating and cooling degree days", report_url=BASE,
                                    document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
