#!/usr/bin/env python3
"""EIA-930 hourly demand and net generation before the hourly extracts begin, from EIA's six-month files (session 49,
approved pull d).

Energy Research Warehouse (ERW) connector. Writes one series table,

    warehouse/output/eia930_all_history.csv    demand_mw, net_generation_mw; partition column ba

from EIA's EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv (https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/), for
the seven ISO balancing authorities (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP). US48 is not a balancing authority in
these files. Approved: 2018-01-01 to 2018-06-30, which restores COVID-19's 728-day baseline (2018-03-04 to 2018-06-03)
in event_window_daily; the hourly extracts of the BA workbooks begin 2018-06-30. Ceiling 100,000 rows.

    python warehouse/connectors/eia930_history.py --file EIA930_BALANCE_2018_Jan_Jun.csv [--from-raw]

Columns used: "UTC Time at End of Hour" (ts_utc is it minus one hour, the hour's start), "Demand (MW) (Adjusted)" and
"Net Generation (MW) (Adjusted)", EIA's published series after its own cleaning (the "Demand (MW)" column is the value
as the BA submitted it). An hour without a value is not written; a BA-day missing any hour is counted in run_status.
The file is public (EIA, U.S. Government data).
"""

import argparse
import datetime as dt
import glob
import io
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "eia930_all_history"
BASE = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"
SOURCE = "eia:gridmonitor/sixMonthFiles"
CEILING = 100_000
BAS = {"CISO": ("ciso", "US-CA"), "ERCO": ("erco", "US-TX"), "ISNE": ("isne", "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"),
       "MISO": ("miso", "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI"),
       "NYIS": ("nyis", "US-NY"),
       "PJM": ("pjm", "US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV"),
       "SWPP": ("swpp", "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY")}
COLS = {"Demand (MW) (Adjusted)": "demand_mw", "Net Generation (MW) (Adjusted)": "net_generation_mw"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 six-month files (session 49)")
    ap.add_argument("--file", required=True, help="e.g. EIA930_BALANCE_2018_Jan_Jun.csv")
    ap.add_argument("--from-raw", action="store_true", help="read the newest saved copy under warehouse/raw/eia930_history/")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_history_{run_id}.log"))
    url = BASE + args.file
    results = []
    try:
        if args.from_raw:
            saved = sorted(glob.glob(os.path.join(ip.RAW_DIR, "eia930_history", "*", f"*_{args.file}")))
            if not saved:
                raise RuntimeError(f"no saved copy of {args.file} under warehouse/raw/eia930_history/")
            path = saved[-1]
            with open(os.path.join(os.path.dirname(path), "manifest.csv"), encoding="utf-8") as f:
                man = pd.read_csv(f, dtype=str)
            m = man[man["file"] == os.path.basename(path)].iloc[-1]
            retrieved, lm = pd.Timestamp(m["retrieved_at"]).strftime("%Y-%m-%dT%H:%M:%SZ"), m["last_modified"]
            content = open(path, "rb").read()
            log(f"read {os.path.relpath(path, ip.ROOT)} (downloaded {retrieved}, Last-Modified {lm}) from {url}")
        else:
            ip.RAW.open("eia930_history", run_id)
            r = requests.get(url, timeout=300)
            if r.status_code != 200 or not r.content.startswith(b"Balancing"):
                raise RuntimeError(f"{url}: HTTP {r.status_code}, {len(r.content)} bytes, not the CSV")
            content, retrieved, lm = r.content, ip.utc_iso(pd.Timestamp.now(tz="UTC")), r.headers.get("Last-Modified")
            log(f"downloaded {url}: {len(content):,} bytes, Last-Modified {lm}")
        df = pd.read_csv(io.BytesIO(content), dtype=str, usecols=["Balancing Authority", "UTC Time at End of Hour", *COLS])
        df = df[df["Balancing Authority"].isin(BAS)]
        end = pd.to_datetime(df["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True)
        df["ts"] = end - pd.Timedelta(hours=1)
        long = df.melt(id_vars=["Balancing Authority", "ts"], value_vars=list(COLS), var_name="col", value_name="v")
        long["v"] = pd.to_numeric(long["v"].str.replace(",", ""), errors="coerce")
        missing = long["v"].isna().sum()
        long = long.dropna(subset=["v"])
        if len(long) > CEILING:
            raise RuntimeError(f"{len(long)} rows, over the {CEILING} ceiling: not written")
        s = pd.DataFrame({
            "entity": "eia930:" + long["Balancing Authority"], "variable": long["col"].map(COLS),
            "ts_utc": long["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": long["v"].map(lambda v: f"{v:g}"), "unit": "MW",
            "freq": "PT1H", "geo": long["Balancing Authority"].map(lambda b: BAS[b][1]), "market": "", "node": "",
            "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": lm or "",
            "ba": long["Balancing Authority"].map(lambda b: BAS[b][0])})
        s["value"] = pd.to_numeric(s["value"])
        if lm:  # the file's Last-Modified as the vintage, ISO 8601 UTC
            s["vintage"] = ip.utc_iso(pd.Timestamp(pd.to_datetime(lm, utc=True)))
        cols = ip.SERIES_COLS + ["ba"]
        header = [
            "Energy Research Warehouse (ERW): EIA-930 hourly demand and net generation from EIA's six-month files, the seven "
            "ISO balancing authorities (session 49)",
            "Shape: series (docs/datastandard.md v0), partition column ba. demand_mw and net_generation_mw, MW (EIA's MWh per "
            "hour): the file's Adjusted columns, EIA's published series. ts_utc is the hour's start (the file's UTC Time at "
            "End of Hour minus one hour).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_history.py; file downloaded {retrieved}",
            f"Run log: warehouse/output/logs/eia930_history_{run_id}.log",
            "Raw files: warehouse/raw/eia930_history/<run>/ (not in git; manifest.csv lists each file and URL)",
            f"Source: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {PAGE}",
            f"  file: {url} (Last-Modified {lm})",
            f"Hours without a value are not written: {int(missing)} BA-hour values were empty.",
            "License: public (U.S. Energy Information Administration).",
        ]
        ip.write_csv(s[cols], NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                report="EIA-930 six-month files (Hourly Electric Grid Monitor)", report_url=PAGE,
                                document_list=BASE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market=args.file, status="ok", detail=f"{len(s)} rows; {int(missing)} empty values"))
        print(f"eia930_history: {len(s):,} rows from {args.file}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia930_history FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market=args.file, status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia930_history", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
