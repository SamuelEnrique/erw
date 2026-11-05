#!/usr/bin/env python3
"""Portugal's public net electricity production by type, load and cross-border trading, from Energy-Charts (Fraunhofer
ISE) (session 2282, chain 104: in place of Japan's areas' demand, which no host would give: TEPCO's refuses the reader,
Kansai's terms forbid reposting without permission, and OCCTO's area data sit behind its interactive system). A public
companion to ren_portugal_balance_annual, which is internal while REN states no terms.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/energy_charts_portugal_power.csv, from the
Energy-Charts API's public_power endpoint for country pt, one request a year (2 requests a minute a client):

    https://api.energy-charts.info/public_power?country=pt&start=<year>-01-01&end=<year>-12-31

Built as energy_charts_italy.py (session 2281): every production type and load in MW, the API's derived series (residual
load, renewable shares) left out, a null without a row, each file's own interval, the interval's start from unix
seconds.

    entity      energy_charts:PT; node Portugal; geo PT; unit MW

    python warehouse/connectors/energy_charts_portugal.py [--first 2020] [--last 2026] [--end 2026-10-22] [--offline] [--out-dir DIR]

Ceiling: one request a year, 31 seconds apart, reused from warehouse/raw/energy_charts_portugal/ with --offline.
api.energy-charts.info has no robots file (session 2281). License: CC BY 4.0, the API's description (read in session
2281): "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license.
Proper attribution to Energy-Charts.info as the source is required."
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "energy_charts_portugal_power"
CONNECTOR = "energy_charts_portugal"
SOURCE = "energy_charts:public_power_pt"
PAGE = "https://api.energy-charts.info/"
URL = "https://api.energy-charts.info/public_power?country=pt&start={a}&end={b}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
DERIVED = {"Residual load", "Renewable share of load", "Renewable share of generation"}
FREQ = {3600: "PT1H", 900: "PT15M"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def file_rows(body, url, retrieved, vintage):
    d = json.loads(body)
    secs, types = d.get("unix_seconds"), d.get("production_types")
    if not isinstance(secs, list) or not isinstance(types, list) or not secs:
        raise RuntimeError(f"{url}: the answer is not public_power's")
    steps = {b - a for a, b in zip(secs, secs[1:])}
    if len(steps) != 1 or next(iter(steps)) not in FREQ:
        raise RuntimeError(f"{url}: intervals not evenly spaced: {sorted(steps)[:5]}")
    freq = FREQ[next(iter(steps))]
    ts = [dt.datetime.fromtimestamp(s, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") for s in secs]
    out = []
    for p in types:
        name, data = p.get("name"), p.get("data")
        if name in DERIVED:
            continue
        if not isinstance(data, list) or len(data) != len(secs):
            raise RuntimeError(f"{url}: {name!r}: {len(data or [])} values for {len(secs)} intervals")
        var = snake(name)
        for t, v in zip(ts, data):
            if v is None:
                continue
            if not isinstance(v, (int, float)):
                raise RuntimeError(f"{url}: {name} {t}: not a number: {v!r}")
            out.append({"entity": "energy_charts:PT", "variable": var, "ts_utc": t, "value": float(v), "unit": "MW",
                        "freq": freq, "geo": "PT", "market": "", "node": "Portugal", "source": SOURCE, "source_url": url,
                        "retrieved_at": retrieved, "vintage": vintage})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"an interval given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy-Charts: Portugal's public net production by type and load")
    ap.add_argument("--first", type=int, default=2020)
    ap.add_argument("--last", type=int, default=2026)
    ap.add_argument("--end", default="2026-10-22", help="the last day asked in the last year")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
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
        if not args.offline and (ip.paused("energy_charts") or ip.paused_host("api.energy-charts.info")):
            raise RuntimeError("Energy-Charts is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for y in range(args.first, args.last + 1):
            url = URL.format(a=f"{y}-01-01", b=args.end if y == args.last else f"{y}-12-31")
            if got and not args.offline:
                time.sleep(31)  # the API's 2 requests a minute
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
            rows += file_rows(content.decode("utf-8"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((y, rec.get("retrieved_at") or ""))
        t = finish(rows)
        span = t.groupby("freq").ts_utc.agg(["min", "max", "nunique"])
        header = [
            f"Energy Research Warehouse (ERW): Energy-Charts (Fraunhofer ISE), Portugal's public net electricity production by type, load and cross-border trading, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2282)",
            "Shape: series (docs/datastandard.md v0). entity energy_charts:PT; variable the API's production type in snake case (load and cross_border_electricity_trading among them; consumption and exports negative); "
            "unit MW; ts_utc the interval's start; freq each file's own interval; geo PT. Residual load and the renewable shares, derived by the API, are not taken.",
            f"{len(t)} rows: " + "; ".join(f"{f} {int(r['nunique'])} intervals {r['min'][:10]} to {r['max'][:10]}" for f, r in span.iterrows())
            + ". A null has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energy_charts_portugal.py; the answers retrieved " + "; ".join(f"{y} {r}" for y, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy-Charts.info (Fraunhofer ISE), API, public_power, country pt, {PAGE}",
            f"  access: {URL.format(a='<year>-01-01', b='<year>-12-31')}",
            "License: public, CC BY 4.0 (the API's description). Source: Energy-Charts.info. The values are reshaped from wide to long; none is changed.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy-Charts.info (Fraunhofer ISE)",
                                    report="Energy-Charts API, public_power, Portugal", report_url=PAGE,
                                    document_list=URL.format(a="<year>-01-01", b="<year>-12-31"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
