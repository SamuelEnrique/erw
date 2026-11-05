#!/usr/bin/env python3
"""Austria's, Switzerland's and Czechia's public net electricity production by type and their load, from Energy-Charts
(Fraunhofer ISE), from 2023 (session 2272, chain 103: a source of the session's own choosing, central Europe's grids in
place of their operators' own data, which refuse or bar the reader: APG's transparency platform does not answer, and
Swissgrid's legal information forbids public or commercial use without consent).

Energy Research Warehouse (ERW) connector. One series table from the Energy-Charts API, one request a country and
calendar year, the form chain 102's energy_charts_belgium.py uses for Belgium:

    https://api.energy-charts.info/public_power?country=<at|ch|cz>&start=<year>-01-01&end=<year>-12-31

    energy_charts_central_europe   entity energy_charts:<country>:<production type as a slug>; variable public_net_power for a
               production type, load, residual_load or cross_border_trading for the others; value in MW (as Energy-Charts
               gives it, the hour's mean power: a quarter-hour answer's four values averaged, an hour kept only when all
               four are given); ts_utc the hour's start (Energy-Charts' timestamps mark a period's beginning); freq PT1H;
               geo AT, CH or CZ; x_type Energy-Charts' name; x_resolution the answer's own spacing (PT1H or PT15M)

Energy-Charts' renewable shares (percentages it computes) are not taken. Each country's own production types are kept
as Energy-Charts names them. An hour with a blank figure (or a quarter hour missing) has no row and is counted. The
quarter hours are averaged so that the table is hourly throughout, as chain 102's Belgian table is (at full resolution
it would hold 3.7 million rows, a gigabyte). A year's timestamps must be evenly spaced at an
hour or a quarter hour and each type's series as long as the timestamps, or the run stops; so does an interval given
twice. Nothing is filled. The current year is asked to the last day ended at the run (Central European time).

    python warehouse/connectors/energy_charts_central.py [--offline] [--out-dir DIR] [--last-day YYYY-MM-DD]

Ceiling: one request a country and year from 2023 (twelve in 2026), 35 seconds apart: the API allows 2 requests a minute
for each client (its description, rate limiting). Each is asked again unless --offline. api.energy-charts.info has no
robots file (HTTP 404). License: CC BY 4.0 with attribution to Energy-Charts.info, as the API's description states
("Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license"); public
since chain 102's verdict for Energy-Charts reached main (session 2279). Energy-Charts compiles the countries'
figures from the operators' publications.
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

CONNECTOR = "energy_charts_central"
SOURCE = "energy_charts:public_power_at_ch_cz"
HOST = "api.energy-charts.info"
PAGE = "https://energy-charts.info/charts/power/chart.htm?l=en"
TABLE = "energy_charts_central_europe"
COUNTRIES = {"at": ("AT", "Austria"), "ch": ("CH", "Switzerland"), "cz": ("CZ", "Czechia")}
FIRST_YEAR = 2023
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
OTHER = {"Load": "load", "Residual load": "residual_load", "Cross border electricity trading": "cross_border_trading"}
SHARES = {"Renewable share of load", "Renewable share of generation"}
FREQ = {3600: "PT1H", 900: "PT15M"}  # the answers' spacings
X_COLS = ["x_type", "x_resolution"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def url_of(cc, year, end=None):
    return f"https://api.energy-charts.info/public_power?country={cc}&start={year}-01-01&end={end or f'{year}-12-31'}"


def parse(content, cc, year, base, counts):
    d = json.loads(content)
    u = d.get("unix_seconds")
    if not u or "production_types" not in d:
        raise RuntimeError(f"{cc} {year}: an answer without timestamps or production types")
    steps = {b - a for a, b in zip(u, u[1:])}
    if len(steps) != 1 or next(iter(steps)) not in FREQ:
        raise RuntimeError(f"{cc} {year}: the timestamps are not evenly an hour or a quarter hour apart: {sorted(steps)[:5]}")
    step = next(iter(steps))
    geo, name_c = COUNTRIES[cc]
    # a quarter-hour answer is averaged to the hour, an hour kept only when its four quarters are all given
    ts = [pd.Timestamp(x - x % 3600, unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ") for x in u]
    out = []
    for p in d["production_types"]:
        name = p["name"]
        if name in SHARES:
            counts["shares not taken"] = counts.get("shares not taken", 0) + len(p["data"])
            continue
        if len(p["data"]) != len(u):
            raise RuntimeError(f"{cc} {year}: {name} has {len(p['data'])} figures for {len(u)} timestamps")
        var = OTHER.get(name, "public_net_power")
        hours = {}
        for t, v in zip(ts, p["data"]):
            hours.setdefault(t, []).append(v)
        need = 3600 // step
        for t, vs in hours.items():
            if len(vs) != need or any(v is None for v in vs):
                counts[f"{cc} {name} hours not whole"] = counts.get(f"{cc} {name} hours not whole", 0) + 1
                continue
            out.append(dict(base, entity=f"energy_charts:{cc}:{slug(name)}", variable=var, ts_utc=t, value=round(sum(vs) / need, 3), unit="MW",
                            freq="PT1H", geo=geo, market="", node=f"{name_c}: {name}", x_type=name, x_resolution=FREQ[step]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy-Charts: Austria's, Switzerland's and Czechia's public net production by type and load")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--last-day", help="the current year's last day asked (YYYY-MM-DD); by default yesterday in Central European time")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    last = args.last_day or (pd.Timestamp(now).tz_convert("Europe/Vienna").normalize() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        rows, counts, got = [], {}, []
        for cc in COUNTRIES:
            for year in range(FIRST_YEAR, int(last[:4]) + 1):
                url = url_of(cc, year, last if year == int(last[:4]) else None)
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=35)
                base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                rows += parse(content, cc, year, base, counts)
                got.append(f"{cc} {year} {base['retrieved_at']}")
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an interval given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        fq = s.groupby("geo").x_resolution.agg(lambda x: ",".join(sorted(set(x)))).to_dict()
        head = [
            "Energy Research Warehouse (ERW): Energy-Charts (Fraunhofer ISE), Austria's, Switzerland's and Czechia's public net electricity production "
            f"by type, load, residual load and cross-border trading, {s.ts_utc.min()} to {s.ts_utc.max()} (session 2272)",
            "Shape: series (docs/datastandard.md v0). entity energy_charts:<at|ch|cz>:<type>; variable public_net_power, load, residual_load or "
            "cross_border_trading; unit MW (the hour's mean power: a quarter-hour answer's four values averaged, an hour kept only when all four are "
            "given); ts_utc the hour's start; freq PT1H; the answers' own spacing, x_resolution (" + ", ".join(f"{k} {v}" for k, v in sorted(fq.items()))
            + "); geo AT, CH or CZ; x_type Energy-Charts' name.",
            f"{len(s):,} rows, {s.entity.nunique()} series. Not taken, counted: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energy_charts_central.py; the requests retrieved {'; '.join(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production, {PAGE}",
            "  access: https://api.energy-charts.info/public_power?country=<at|ch|cz>, one calendar year a request",
            "License: public (CC BY 4.0, attribution to Energy-Charts.info, the API's description; the verdict recorded by chain 102).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series, {s.ts_utc.min()} to {s.ts_utc.max()}; freq {fq}; not taken {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Energy-Charts.info (Fraunhofer ISE)",
                                    report="Public net electricity production, Austria, Switzerland and Czechia (API public_power)",
                                    report_url=PAGE, document_list="https://api.energy-charts.info/openapi.json", license="public", tables=[TABLE])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
