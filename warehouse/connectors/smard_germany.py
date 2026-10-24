#!/usr/bin/env python3
"""Germany's electricity generation by source and its grid load, a month from January 2015, as the Bundesnetzagentur
publishes them on SMARD (session 2230, chain 099: a source of the session's own choosing, Europe's largest grid beside the
U.S. ones).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/smard_germany_monthly.csv, from one POST to
SMARD's download centre (the form behind https://www.smard.de/en/downloadcenter/download-market-data), which answers a
zip of two semicolon-separated CSV files:

    Actual_generation_..._Month_1.csv    Start date; End date; one column a source (Biomass, Hydropower, Wind offshore,
                                         Wind onshore, Photovoltaics, Other renewable, Nuclear, Lignite, Hard coal, Fossil
                                         gas, Hydro pumped storage, Other conventional), "[MWh] Calculated resolutions"
    Actual_consumption_..._Month_2.csv   Start date; End date; grid load [MWh]

    entity      smard:de
    variable    generation_<source in snake case> or grid_load; node the column's name as SMARD writes it
    unit        MWh; ts_utc the month's first day (SMARD's Start date, a month in German time); freq P1M; geo DE

A month SMARD marks "-" has no row; nothing is filled. A zip without the two files, a header not of this form, a Start
date that is not the first of a month, a value that is not a number (commas as thousands separators allowed) or a month
given twice stops the run. SMARD's figures are the transmission system operators' as ENTSO-E receives them, verified by
the Bundesnetzagentur (its data use page).

    python warehouse/connectors/smard_germany.py [--offline] [--out-dir DIR]

Ceiling: one request (the POST), its answer saved in warehouse/raw/smard_germany/ and reused offline. www.smard.de has no
robots file (HTTP 404, session 2230). License: public (CC BY 4.0, SMARD's data use page: market data "is licensed under a
Creative Commons Attribution 4.0 International Licence"); attribution "Bundesnetzagentur | SMARD.de".
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "smard_germany_monthly"
CONNECTOR = "smard_germany"
SOURCE = "smard:market_data_month"
URL = "https://www.smard.de/nip-download-manager/nip/download/market-data"
PAGE = "https://www.smard.de/en/downloadcenter/download-market-data"
TERMS = "https://www.smard.de/en/datennutzung"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)", "Content-Type": "application/json"}
# SMARD's module ids for the realized generation by source and the grid load (its download form)
MODULES = [1001224, 1004066, 1004067, 1004068, 1001223, 1004069, 1004071, 1004070, 1001226, 1001228, 1001227, 1001225, 5000410]
SAVED = "market_data_month.zip"
COL = re.compile(r"^(.+) \[MWh\] Calculated resolutions$")
X_COLS = ["x_file"]


def body(t1):
    t0 = int(dt.datetime(2014, 12, 31, 23, tzinfo=dt.timezone.utc).timestamp() * 1000)  # 1 January 2015, 00:00 in Germany
    return {"request_form": [{"format": "CSV", "moduleIds": MODULES, "region": "DE", "timestamp_from": t0, "timestamp_to": t1,
                              "type": "discrete", "language": "en", "resolution": "month"}]}


def parse(content, base):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = z.namelist()
    gen = [n for n in names if n.startswith("Actual_generation_")]
    con = [n for n in names if n.startswith("Actual_consumption_")]
    if len(gen) != 1 or len(con) != 1:
        raise RuntimeError(f"the zip does not hold one generation and one consumption file: {names}")
    rows = []
    for n, prefix in ((gen[0], "generation_"), (con[0], "")):
        lines = z.read(n).decode("utf-8-sig").splitlines()
        head = lines[0].split(";")
        if head[:2] != ["Start date", "End date"]:
            raise RuntimeError(f"{n}: a header not 'Start date;End date;...': {head[:3]}")
        cols = []
        for c in head[2:]:
            m = COL.fullmatch(c.strip())
            if not m:
                raise RuntimeError(f"{n}: a column not '<name> [MWh] Calculated resolutions': {c!r}")
            cols.append((m.group(1), prefix + re.sub(r"[^a-z0-9]+", "_", m.group(1).lower()).strip("_")))
        for ln in lines[1:]:
            if not ln.strip():
                continue
            cells = ln.split(";")
            start = dt.datetime.strptime(cells[0].strip(), "%b %d, %Y")
            if start.day != 1:
                raise RuntimeError(f"{n}: a Start date not the first of a month: {cells[0]!r}")
            ts = start.strftime("%Y-%m-01T00:00:00Z")
            for (label, var), v in zip(cols, cells[2:]):
                v = v.strip()
                if v == "-" or v == "":
                    continue
                try:
                    value = float(v.replace(",", ""))
                except ValueError:
                    raise RuntimeError(f"{n} {ts[:7]} {label}: not a number: {v!r}")
                rows.append(dict(entity="smard:de", variable=var, ts_utc=ts, value=value, unit="MWh", freq="P1M", geo="DE", market="",
                                 node=label, **base, x_file=n))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no month in the files")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="SMARD: Germany's generation by source and grid load, a month")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("www.smard.de"):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        path = os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)
        meta_path = path + ".json"
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved answer at {path}")
            content = open(path, "rb").read()
            retrieved = json.load(open(meta_path, encoding="utf-8"))["retrieved_at"]
            log(f"  saved answer reused: {path} (retrieved {retrieved})")
        else:
            now = dt.datetime.now(dt.timezone.utc)
            q = body(int(now.timestamp() * 1000))
            r = requests.post(URL, data=json.dumps(q), headers=UA, timeout=120)
            if r.status_code != 200 or not r.content.startswith(b"PK"):
                raise RuntimeError(f"HTTP {r.status_code}, {len(r.content)} bytes, not a zip")
            retrieved = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            content = r.content
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(r.content)
            json.dump({"retrieved_at": retrieved, "url": URL, "body": q, "bytes": len(r.content)}, open(meta_path, "w", encoding="utf-8"))
            log(f"  POST {URL}: {len(r.content)} bytes, saved as {path}")
        base = dict(source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage="")
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable.str.startswith("generation_")]
        y = g.groupby(g.ts_utc.str[:4]).agg(v=("value", "sum"), n=("ts_utc", "nunique"))
        y = y[y.n == 12].v / 1e6
        head = [
            "Energy Research Warehouse (ERW): Bundesnetzagentur, SMARD, Germany's actual generation by source and grid load, a month, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2230)",
            "Shape: series (docs/datastandard.md v0). entity smard:de; variable generation_<source> (biomass, hydropower, wind_offshore, wind_onshore, "
            "photovoltaics, other_renewable, nuclear, lignite, hard_coal, fossil_gas, hydro_pumped_storage, other_conventional) or grid_load; unit MWh; "
            "ts_utc the month's first day (SMARD's Start date, a month in German time); freq P1M; geo DE; node the column as SMARD writes it.",
            f"{len(t)} rows; generation TWh a full year: " + ", ".join(f"{k} {v:.1f}" for k, v in y.items())
            + ". A month SMARD marks '-' has no row; nothing is filled. SMARD's figures are the transmission system operators' through ENTSO-E, "
            "verified by the Bundesnetzagentur.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/smard_germany.py; the answer retrieved {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} and its .json (the query; not in git)",
            f"Source: {SOURCE} Bundesnetzagentur, SMARD market data, {PAGE}",
            f"  access: one POST to {URL} (monthly, region DE, generation by source and grid load)",
            f"License: public (CC BY 4.0, {TERMS}). Attribution: Bundesnetzagentur | SMARD.de",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Bundesnetzagentur (SMARD)", report="SMARD market data: actual generation and grid load",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
