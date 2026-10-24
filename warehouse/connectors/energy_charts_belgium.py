#!/usr/bin/env python3
"""Belgium's public net electricity production by type, its load and its cross-border trading, an hour, from Energy-Charts
(Fraunhofer ISE) (session 2253, chain 102: Belgium's grid, in place of Elia's own open data, whose robots file disallows
its API and downloads to every reader but Google).

Energy Research Warehouse (ERW) connector. One series table from the Energy-Charts API, one request a calendar year
(Belgian local days), from 2020:

    https://api.energy-charts.info/public_power?country=be&start=<year>-01-01&end=<year>-12-31

    energy_charts_belgium_hourly   entity energy_charts:be:<production type as a slug> (nuclear, fossil_gas, solar,
               wind_offshore, wind_onshore, biomass, waste, hydro_run_of_river, hydro_pumped_storage,
               hydro_pumped_storage_consumption (negative, as given), battery (from 2025), fossil_oil, others,
               cross_border_electricity_trading, load, residual_load); variable public_net_power for a production type,
               load, residual_load or cross_border_trading for the others; value in MW as Energy-Charts gives it (the
               hour's mean power); ts_utc the hour's start (Energy-Charts' timestamps mark a period's beginning); freq
               PT1H; geo BE; x_type Energy-Charts' name

Energy-Charts' renewable shares of load and of generation (percentages it computes) are not taken. A blank figure has
no row and is counted (2026's nuclear in two blocks: May and June, and August and September).
A positive cross-border trading figure is an import (session 2261's note). The answer's hours must be an hour apart and each type's
series as long as the hours, or the run stops; so does a type not in the map, or an hour given twice. Nothing is filled.
The current year is asked to the last day ended at the run (Belgian time).

    python warehouse/connectors/energy_charts_belgium.py [--offline] [--out-dir DIR]

Ceiling: one request a year from 2020 (seven in 2026), 35 seconds apart: the API allows 2 requests a minute for each
client (its description, rate limiting). Each is asked again unless --offline. api.energy-charts.info has no robots file
(HTTP 404). License: CC BY 4.0 with attribution to Energy-Charts.info, as the API's description states ("Unless stated
otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license"); public since the
licenses' round recorded the verdict (session 2257). Energy-Charts compiles Belgium's figures from the operators' publications.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "energy_charts_belgium"
SOURCE = "energy_charts:public_power_be"
HOST = "api.energy-charts.info"
PAGE = "https://energy-charts.info/charts/power/chart.htm?l=en&c=BE"
TABLE = "energy_charts_belgium_hourly"
FIRST_YEAR = 2020
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TYPES = {"Nuclear", "Fossil gas", "Fossil oil", "Solar", "Wind offshore", "Wind onshore", "Biomass", "Waste", "Hydro Run-of-River",
         "Hydro pumped storage", "Hydro pumped storage consumption", "Battery", "Others"}
OTHER = {"Load": "load", "Residual load": "residual_load", "Cross border electricity trading": "cross_border_trading"}
SHARES = {"Renewable share of load", "Renewable share of generation"}
X_COLS = ["x_type"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def url_of(year, end=None):
    return f"https://api.energy-charts.info/public_power?country=be&start={year}-01-01&end={end or f'{year}-12-31'}"


def parse(content, year, base, counts):
    d = json.loads(content)
    u = d["unix_seconds"]
    if any(b - a != 3600 for a, b in zip(u, u[1:])):
        raise RuntimeError(f"{year}: the hours are not an hour apart")
    ts = [pd.Timestamp(x, unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ") for x in u]
    out = []
    for p in d["production_types"]:
        name = p["name"]
        if name in SHARES:
            counts["shares not taken"] = counts.get("shares not taken", 0) + len(p["data"])
            continue
        if name not in TYPES and name not in OTHER:
            raise RuntimeError(f"{year}: a type not in the map: {name!r}")
        if len(p["data"]) != len(u):
            raise RuntimeError(f"{year}: {name} has {len(p['data'])} figures for {len(u)} hours")
        var = OTHER.get(name, "public_net_power")
        for t, v in zip(ts, p["data"]):
            if v is None:
                counts[f"{name} blank"] = counts.get(f"{name} blank", 0) + 1
                continue
            out.append(dict(base, entity=f"energy_charts:be:{slug(name)}", variable=var, ts_utc=t, value=float(v), unit="MW", freq="PT1H",
                            geo="BE", market="", node=f"Belgium: {name}", x_type=name))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy-Charts: Belgium's public net production by type and its load, an hour")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--last-day", help="the current year's last day asked (YYYY-MM-DD); by default yesterday in Belgium")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    last = args.last_day or (pd.Timestamp(now).tz_convert("Europe/Brussels").normalize() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, counts, got = [], {}, []
        for year in range(FIRST_YEAR, int(last[:4]) + 1):
            url = url_of(year, last if year == int(last[:4]) else None)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=35)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(content, year, base, counts)
            got.append((year, base["retrieved_at"]))
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an hour given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): Energy-Charts (Fraunhofer ISE), Belgium's public net electricity production by type, load, residual "
            f"load and cross-border trading, an hour, {s.ts_utc.min()} to {s.ts_utc.max()} (session 2253)",
            "Shape: series (docs/datastandard.md v0). entity energy_charts:be:<type>; variable public_net_power, load, residual_load or "
            "cross_border_trading; unit MW (the hour's mean power, as Energy-Charts gives it); freq PT1H; ts_utc the hour's start; geo BE; "
            "x_type Energy-Charts' name.",
            f"Not taken, counted: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energy_charts_belgium.py; the years retrieved {', '.join(f'{y} {a}' for y, a in got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production, Belgium, {PAGE}",
            "  access: https://api.energy-charts.info/public_power?country=be, one calendar year a request",
            "License: public (CC BY 4.0, attribution to Energy-Charts.info, the API's description; see license_verdicts.csv). Source: Energy-Charts.info.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series, {s.ts_utc.min()} to {s.ts_utc.max()}; not taken {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Energy-Charts.info (Fraunhofer ISE)", report="Public net electricity production, Belgium (API public_power)",
                                    report_url=PAGE, document_list="https://api.energy-charts.info/openapi.json", license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
