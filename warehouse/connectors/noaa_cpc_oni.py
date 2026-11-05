#!/usr/bin/env python3
"""NOAA's Climate Prediction Center's Oceanic Nino Index: the three-month running mean of the Nino 3.4 sea surface
temperature and its anomaly, a month from 1950 (session 2092, chain 068: the Pacific's signal for the coming winter's
heating and cooling demand).

Energy Research Warehouse (ERW) connector. One series table from CPC's ONI text file:

    https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt   SEAS YR TOTAL ANOM, one line a three-month season (DJF,
                                                                 JFM, ... NDJ) and year

    noaa_cpc_oni_monthly   entity cpc:oni_nino34; variables oni_anomaly (ANOM, the ONI itself) and nino34_sst (TOTAL, the
                           season's mean sea surface temperature), unit degC (Decision 62); ts_utc the first day of the
                           season's middle month (DJF 1950 is January 1950, NDJ 1950 is December 1950: CPC's YR is the
                           middle month's year); freq P1M; geo empty; x_season CPC's three letters

CPC revises the ONI's recent seasons as its base period moves; each run replaces the table whole. A line not of the
form above, a season not one of CPC's twelve, or a season and year given twice stops the run. Nothing is filled. CPC's
probabilistic ENSO outlook is not taken: it is published in the ENSO discussion, not as a data file.

    python warehouse/connectors/noaa_cpc_oni.py [--offline] [--out-dir DIR]

Ceiling: one request, saved in warehouse/raw/noaa_cpc_oni/ and reused offline (asked fresh when not offline: the file
keeps its address as it grows). www.cpc.ncep.noaa.gov has no robots file. License: public (the National Weather Service's
products are in the public domain, as for CPC's degree days, noaa_cpc_degree_days_daily).
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

CONNECTOR = "noaa_cpc_oni"
SOURCE = "noaa:cpc_oni"
URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
PAGE = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php"
TABLE = "noaa_cpc_oni_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SEASON_MID = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
X_COLS = ["x_season"]
LINE = re.compile(r"^\s*([A-Z]{3})\s+(\d{4})\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$")


def parse(text, base):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines or lines[0].split() != ["SEAS", "YR", "TOTAL", "ANOM"]:
        raise RuntimeError(f"the file's first line is not SEAS YR TOTAL ANOM: {lines[:1]}")
    rows, seen = [], set()
    for ln in lines[1:]:
        m = LINE.match(ln)
        if not m:
            raise RuntimeError(f"a line not of the form SEAS YR TOTAL ANOM: {ln!r}")
        seas, yr, total, anom = m.groups()
        if seas not in SEASON_MID:
            raise RuntimeError(f"a season not one of CPC's twelve: {seas}")
        if (seas, yr) in seen:
            raise RuntimeError(f"a season given twice: {seas} {yr}")
        seen.add((seas, yr))
        ts = f"{yr}-{SEASON_MID[seas]:02d}-01T00:00:00Z"
        for var, v in (("oni_anomaly", anom), ("nino34_sst", total)):
            rows.append(dict(entity="cpc:oni_nino34", variable=var, ts_utc=ts, value=float(v), unit="degC", freq="P1M", geo="", market="",
                             node="Nino 3.4", **base, x_season=seas))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA CPC's Oceanic Nino Index, a month from 1950")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s = parse(content.decode("utf-8", errors="replace"), base)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a month given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        last = s[s.variable == "oni_anomaly"].iloc[-1]
        head = [
            "Energy Research Warehouse (ERW): NOAA National Weather Service, Climate Prediction Center, Oceanic Nino Index (ONI): the three-month "
            "running mean of the Nino 3.4 sea surface temperature and its anomaly, a month from 1950 (session 2092)",
            "Shape: series (docs/datastandard.md v0). entity cpc:oni_nino34; variables oni_anomaly (CPC's ANOM, the index) and nino34_sst (TOTAL); "
            "unit degC (Decision 62); ts_utc the first day of the three-month season's middle month (CPC's YR is that month's year); freq P1M; "
            "x_season CPC's three letters.",
            f"{len(s)} rows, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}; the latest season {last.x_season} {last.ts_utc[:4]}: ONI {last.value:+.2f}. "
            "CPC revises recent seasons; each run replaces the table. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_cpc_oni.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA Climate Prediction Center, Cold and Warm Episodes by Season (ONI), {PAGE}",
            f"  access: {URL}",
            'License: public (National Weather Service: "in the public domain, unless specifically noted otherwise"; cite "NOAA Climate Prediction Center").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="NOAA National Weather Service, Climate Prediction Center",
                                    report="Oceanic Nino Index (ONI): Cold and Warm Episodes by Season", report_url=PAGE, document_list=URL,
                                    license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
