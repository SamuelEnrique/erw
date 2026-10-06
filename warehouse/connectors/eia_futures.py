#!/usr/bin/env python3
"""EIA's daily NYMEX futures prices, 2019 to the day EIA stopped publishing them (session 127, approved pull).

Energy Research Warehouse (ERW) connector. One series table,

    warehouse/output/eia_all_futures_prices.csv    futures_price per contract and trading day

from EIA's open data API (https://api.eia.gov/v2/), routes petroleum/pri/fut and natural-gas/pri/fut, frequency daily:
the official daily closing prices of the New York Mercantile Exchange for contracts 1 to 4 of crude oil (Cushing,
Oklahoma), New York Harbor No. 2 heating oil, New York Harbor reformulated RBOB regular gasoline and natural gas
(Henry Hub). node is the contract: 1 is the earliest delivery month, as EIA defines it.

    python warehouse/connectors/eia_futures.py              # 2019-01-01 to the newest day EIA holds
    python warehouse/connectors/eia_futures.py --offline    # from the raw files, no request

EIA'S SERIES END ON 5 APRIL 2024. Its pages say "Futures prices after April 5, 2024, are not available", and the
API's newest day for each of these sixteen series is 2024-04-05. The table is a closed history; this connector is not
in the daily run, and a rerun finds nothing new unless EIA resumes. EIA's other futures series (propane, and the
regular gasoline contract that RBOB replaced) ended in 2009 and 2006 and hold nothing from 2019.

LICENSE: internal, by this session's reading, for a person to rule. EIA's policy says its own publications are in the
public domain and may be used and distributed, and that items "contributed or licensed by private individuals,
companies, or organizations ... may be protected", needing "the written permission of the copyright owners" beyond
fair use. EIA names the source of these prices as the New York Mercantile Exchange, an exchange that licenses its
settlement prices, and EIA stopped republishing them. Nothing on EIA's pages forbids republishing these series in so
many words; nothing says they are EIA's own either. The passages are quoted in docs/methods/price_board_v4.md.

Ceiling: 600,000 rows for the session's pull (the rows the API returns, the session's probe of 72 rows included).
Values: EIA's, unchanged. A date EIA lists with no value is not written. Nothing is filled.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "eia_all_futures_prices"
API = "https://api.eia.gov/v2/"
START = "2019-01-01"
CEILING = 600_000
EXPLORED = 72            # session 127's probe: one row for the first and the last day of each of 36 daily series
PAGE = 5000
PUBLISHER = "U.S. Energy Information Administration (EIA)"
# source: (route, EIA's page, report)
SOURCES = {
    "eia:nymex_futures_petroleum": ("petroleum/pri/fut", "https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm",
                                    "NYMEX Futures Prices, crude oil and petroleum products, daily (ends 5 April 2024)"),
    "eia:nymex_futures_natural_gas": ("natural-gas/pri/fut", "https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm",
                                      "Natural Gas Futures Prices (NYMEX), daily (ends 5 April 2024)"),
}
EIA_UNITS = {"$/BBL": "USD/bbl", "$/GAL": "USD/gal", "$/MMBTU": "USD/MMBtu"}
# entity: (source, EIA series, unit, geo, contract, what it is)
SERIES = {}
for n in (1, 2, 3, 4):
    SERIES[f"eia:RCLC{n}"] = ("eia:nymex_futures_petroleum", f"RCLC{n}", "USD/bbl", "US-OK", n, "Crude oil, Cushing, Oklahoma")
    SERIES[f"eia:EER_EPD2F_PE{n}_Y35NY_DPG"] = ("eia:nymex_futures_petroleum", f"EER_EPD2F_PE{n}_Y35NY_DPG", "USD/gal", "US-NY", n, "No. 2 heating oil, New York Harbor")
    SERIES[f"eia:EER_EPMRR_PE{n}_Y35NY_DPG"] = ("eia:nymex_futures_petroleum", f"EER_EPMRR_PE{n}_Y35NY_DPG", "USD/gal", "US-NY", n, "Reformulated RBOB regular gasoline, New York Harbor")
    SERIES[f"eia:RNGC{n}"] = ("eia:nymex_futures_natural_gas", f"RNGC{n}", "USD/MMBtu", "US-LA", n, "Natural gas, Henry Hub")


def fetch(route, series, key, log, offline=False):
    """One series from START, as the API returns it: (rows, URL without the key, retrieved). Read from the raw files
    when an earlier run saved the answer (the series is closed)."""
    out, offset = [], 0
    while True:
        params = [("frequency", "daily"), ("data[0]", "value"), ("facets[series][]", series), ("start", START), ("sort[0][column]", "period"),
                  ("sort[0][direction]", "asc"), ("offset", str(offset)), ("length", str(PAGE))]
        public = requests.Request("GET", API + route + "/data/", params=params).prepare().url
        hit = ip.raw_cached("eia_futures", public)
        if hit:
            body, retrieved = json.loads(hit[0]), hit[1]["retrieved_at"]
            log(f"  raw file reused: {public}")
        else:
            if offline:
                raise RuntimeError(f"offline: {public} is not in warehouse/raw/eia_futures/")

            def call():
                r = requests.get(public, params=[("api_key", key)], timeout=120)
                if r.status_code != 200:
                    raise RuntimeError(f"EIA {route} {series} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
                return r
            r = ip.with_retries(f"EIA {route} {series} offset {offset}", call, log)
            body, retrieved = r.json(), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            ip.RAW.alias(public, r.content, r.headers)   # the answer is kept under the address without the key
            time.sleep(0.4)
        resp = body["response"]
        rows, total = resp.get("data", []), int(resp.get("total", 0))
        for row in rows:
            row["_url"], row["_retrieved"] = public, str(retrieved)
        out += rows
        log(f"  {series} offset {offset}: {len(rows)} rows (total {total})")
        offset += len(rows)
        if not rows or offset >= total:
            break
    if len(out) != total:
        raise RuntimeError(f"EIA {series}: got {len(out)} rows, API reported {total}")
    return out


def shape(entity, rows):
    """EIA's rows of one series as the table's rows; a date listed with no value is left out and counted."""
    source, series, unit, geo, contract, what = SERIES[entity]
    df = pd.DataFrame(rows)
    if df.empty:
        return df, 0
    got = {EIA_UNITS.get(u) for u in set(df["units"])}
    if got != {unit}:
        raise RuntimeError(f"{series}: EIA units {set(df['units'])}, expected {unit}")
    if df["period"].duplicated().any():
        raise RuntimeError(f"{series}: EIA lists a date more than once")
    value = pd.to_numeric(df["value"], errors="coerce")
    bad = df[value.isna() & df["value"].notna() & (df["value"].astype(str).str.strip() != "")]
    if len(bad):
        raise RuntimeError(f"{series}: values that are not numbers {list(bad['value'].unique()[:5])}")
    keep = value.notna()
    d = df[keep]
    return pd.DataFrame({
        "entity": entity, "variable": "futures_price",
        "ts_utc": pd.to_datetime(d["period"], format="%Y-%m-%d").dt.strftime("%Y-%m-%dT00:00:00Z").values,
        "value": value[keep].values, "unit": unit, "freq": "P1D", "geo": geo, "market": "nymex", "node": str(contract),
        "source": source, "source_url": d["_url"].values, "retrieved_at": d["_retrieved"].values, "vintage": "",
    }), int((~keep).sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's daily NYMEX futures prices, 2019 to 5 April 2024")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; no request is made")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia_futures_{run_id}.log"))
    results = []
    try:
        key = "" if args.offline else ip.load_key("EIA_API_KEY", log)
        if not args.offline:
            ip.RAW.open("eia_futures", run_id)
        frames, pulled, empty, ends = [], EXPLORED, 0, {}
        log(f"ERW eia_futures run {run_id}: {len(SERIES)} series from {START}; ceiling {CEILING:,} rows ({EXPLORED} read by the session's probe are counted)")
        for entity, (source, series, unit, geo, contract, what) in SERIES.items():
            if pulled + 1500 > CEILING:
                raise RuntimeError(f"{pulled:,} rows read; another series would risk the ceiling of {CEILING:,}: stopped")
            rows = fetch(SOURCES[source][0], series, key, log, args.offline)
            pulled += len(rows)
            s, n_empty = shape(entity, rows)
            empty += n_empty
            if len(s):
                frames.append(s)
                ends[entity] = s["ts_utc"].max()[:10]
            log(f"  {entity} ({what}, contract {contract}): {len(rows)} rows returned, {len(s)} values, newest {ends.get(entity, 'none')}; {pulled:,} rows in all")
        if pulled > CEILING:
            raise RuntimeError(f"{pulled:,} rows read, over the ceiling of {CEILING:,}: nothing written")
        table = pd.concat(frames, ignore_index=True)
        last = sorted(set(ends.values()))
        header = [
            "Energy Research Warehouse (ERW): EIA's daily NYMEX futures prices, contracts 1 to 4 of crude oil, heating oil, RBOB gasoline and natural gas, 2019 to the day EIA stopped publishing them (session 127)",
            "Shape: series (docs/datastandard.md v0). futures_price: the official daily closing price of the New York Mercantile Exchange as EIA published it, per contract (node 1 to 4: 1 is the earliest delivery month) and trading day; ts_utc is the trading date at 00:00:00Z; freq P1D. USD/bbl (crude oil), USD/gal (heating oil, gasoline), USD/MMBtu (natural gas).",
            f"EIA's series end on 5 April 2024 (\"Futures prices after April 5, 2024, are not available\"): the newest day held is {last[-1]}" + (f" (oldest newest {last[0]})" if len(last) > 1 else "") + ". A closed history, not a current price.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_futures.py",
            f"Run log: warehouse/output/logs/eia_futures_{run_id}.log",
            "Raw files: warehouse/raw/eia_futures/ (not in git; each run's manifest.csv lists each answer and its address, without the key)",
        ]
        for src, (route, page, report) in SOURCES.items():
            header.append(f"Source: {src} EIA, {report}, {page}")
            header.append(f"  access: {API}{route}/data/ (frequency daily, from {START})")
        header += [
            "Series: " + "; ".join(f"{e} = {v[5]}, contract {v[4]}" for e, v in SERIES.items()),
            f"Rows returned by the API: {pulled:,} of the {CEILING:,} ceiling, the session's probe included. Dates EIA lists with no value, not written: {empty}.",
            "License: internal, by session 127's reading, for a person to rule. EIA names the New York Mercantile Exchange as the source of these prices and stopped republishing them on 5 April 2024; its reuse policy says items licensed by companies \"may be protected\". Nothing on EIA's pages forbids republishing them in so many words. The passages are quoted in docs/methods/price_board_v4.md.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)   # a closed history, rebuilt whole from the answers
        ip.write_csv(table[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([dict(source=src, publisher=PUBLISHER, report=report, report_url=page, document_list=API + route + "/",
                                    license="internal", tables=[NAME]) for src, (route, page, report) in SOURCES.items()])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(table)} rows; {pulled} rows returned"))
        print(f"eia_futures: {len(table):,} values of {len(frames)} series, newest {last[-1]}; {pulled:,} rows returned of {CEILING:,}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia_futures FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia_futures", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
