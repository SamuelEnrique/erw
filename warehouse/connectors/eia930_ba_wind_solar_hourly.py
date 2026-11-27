#!/usr/bin/env python3
"""EIA-930 hourly net generation from wind and from solar by balancing authority, July 2018 on (predict data request 10).

Energy Research Warehouse (ERW), session 10000 (chain 701), for Samuel's order of 27 November 2026 ("more places": the
wind and solar forecast, warehouse/predict/wind_solar.py, needs a long history by authority, which the warehouse held for
the 13 regions and CAISO's hubs only). Writes one series table,

    warehouse/output/eia930_ba_wind_solar_hourly.csv    net_generation_wind_mw, net_generation_solar_mw; partition column ba

from the same six-month files (EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv) that eia930_region_hourly.py saves and
eia930_region_fuel_hourly.py reads: their saved copies only, no request. Each authority's value is EIA's adjusted column
where the file prints one, else the reported column; from July 2024 EIA splits each source into "without" and "with
Integrated Battery Storage", and the two are summed (eia930_region_fuel_hourly.read_file, the same reading; this connector
imports it, the second that needs the code). An hour without a value is not written, and an authority's wind or solar
series is left out of a file in which every value is zero or missing (it has no plant of that source then).

    python warehouse/connectors/eia930_ba_wind_solar_hourly.py                    # the whole table, under the data lock
    python warehouse/connectors/eia930_ba_wind_solar_hourly.py --out-dir DIR      # a trial

The files are public (EIA, U.S. Government data).
"""
import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import eia930_region_fuel_hourly as rf  # noqa: E402

NAME = "eia930_ba_wind_solar_hourly"
CONNECTOR = NAME
SOURCE = rf.SOURCE
CEILING = 15_000_000
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "source_url", "retrieved_at", "vintage", "ba",
        "x_file"]
FUELS = {"wind": "net_generation_wind_mw", "solar": "net_generation_solar_mw"}


def file_rows(d, name, url, retrieved, lm):
    """The table's rows of one file read by rf.read_file: wind and solar by authority, an all-zero series left out."""
    parts = []
    for fuel, var in FUELS.items():
        x = d[["ba", "ts", fuel]].dropna(subset=[fuel])
        keep = x.groupby("ba")[fuel].transform(lambda v: (v != 0).any())
        x = x[keep]
        parts.append(pd.DataFrame({"entity": "eia930:" + x["ba"], "variable": var, "ts": x["ts"], "value": x[fuel],
                                   "ba": x["ba"].str.lower()}))
    out = pd.concat(parts, ignore_index=True)
    out["x_file"] = rf.tag(name)
    out["source_url"] = url
    out["retrieved_at"] = retrieved
    out["vintage"] = ip.utc_iso(pd.Timestamp(pd.to_datetime(lm, utc=True))) if lm else ""
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-930 wind and solar net generation by balancing authority, hourly")
    ap.add_argument("--out-dir", help="a trial: the table under this folder (the saved files are read from this copy)")
    a = ap.parse_args(argv)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        parts, lines = [], []
        for name in rf.files_between():
            got = rf.saved_copy(name)
            if not got:
                raise RuntimeError(f"no saved copy of {name}: run eia930_region_hourly.py --download-only first")
            path, retrieved, lm, url = got
            rows = file_rows(rf.read_file(path), name, url, retrieved, lm)
            parts.append(rows)
            lines.append(f"  {name}: {url}, Last-Modified {lm}, saved {retrieved}")
            log(f"  {name}: {len(rows):,} rows")
            print(f"  {name}: {len(rows):,} rows", flush=True)
        t = pd.concat(parts, ignore_index=True).drop_duplicates(["entity", "variable", "ts"], keep="last")
        if len(t) > CEILING:
            raise RuntimeError(f"{len(t)} rows would pass the ceiling of {CEILING}; nothing written")
        t = t.sort_values(["entity", "variable", "ts"])
        t["ts_utc"] = t["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        t["value"] = t["value"].map(lambda v: f"{v:g}")
        t["unit"], t["freq"], t["source"] = "MW", "PT1H", SOURCE
        header = [
            "Energy Research Warehouse (ERW): EIA-930 hourly net generation from wind and from solar by balancing authority, "
            "July 2018 on (session 10000, chain 701, predict data request 10)",
            "Shape: series (docs/datastandard.md v0), partition column ba (the authority, lowercase). net_generation_wind_mw "
            "and net_generation_solar_mw, MW (EIA's MWh per hour): the adjusted column where EIA prints one, else the "
            "reported; from July 2024 the without and with Integrated Battery Storage columns summed. ts_utc is the hour's "
            "start. An authority's series is left out of a file in which every value is zero or missing.",
            f"Rows: {len(t):,}; {t['entity'].nunique()} authorities; {t['ts_utc'].min()} to {t['ts_utc'].max()}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_ba_wind_solar_hourly.py, from the saved six-month files:",
            *lines,
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Source: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {rf.PAGE}",
            "License: public (U.S. Energy Information Administration).",
        ]
        ip.write_snapshot(t[COLS], NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="EIA-930 six-month files (Hourly Electric Grid Monitor)", report_url=rf.PAGE,
                                    document_list=rf.BASE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t):,} rows, {t['entity'].nunique()} authorities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not a.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
