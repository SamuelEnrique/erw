#!/usr/bin/env python3
"""Kosovo's electricity a month, from January 2022: gross production from thermal, hydro, and wind and solar plants,
imports, exports, gross electricity available, and consumption by sector, as the Kosovo Agency of Statistics (ASK)
publishes them in its ASKdata table "Electricity production and consumption" (tab01) (session 2524, chain 123: a source
of the session's own choosing; the ERW held Kosovo only in Eurostat's tables, which leave it out of commercial reuse).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ask_kosovo_electricity_monthly.csv, from
ASK's PxWeb API (no key), one JSON-stat 2.0 query by POST, every value of both dimensions selected:

    https://askdata.rks-gov.net/api/v1/en/ASKdata/Energy/Monthly%20indicators/tab01.px

    entity      ask:xk:<item>: thermal, hydro, wind_solar, total (the gross electricity available); households,
                commercial, industry, public_lighting_other, consumers_220_110kv, mining, total_consumption
    variable    gross_production (thermal, hydro, wind_solar), imports, exports, gross_available, consumption
    unit        MWh: the figures times 1,000. The dimension is named "MWH", but its figures carry three decimals
                (px decimals 3) and a year's gross electricity available sums to about 7.3 thousand: they are
                thousands of MWh (GWh). `eia_world_electricity_annual` confirms the scale: Kosovo's 2024 generation
                7.02 TWh, imports 3.16 and exports 2.62 TWh, against ASK's 6.75, 3.2 and 2.6 read so (session 2524)
    ts_utc      the month's first day, 00:00 UTC; freq P1M; geo XK
    node        the item as ASK labels it

A cell without a number has no row. An answer without the two dimensions, an item not in the map, a month not of the
form YYYYMnn or YYYYnn (ASK writes both), a value array not the size of the dimensions, or a key given twice stops the run. Nothing is filled.

    python warehouse/connectors/ask_kosovo_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/ask_kosovo_energy/query_tab01.json and read from there with
--offline. askdata.rks-gov.net and ask.rks-gov.net answer HTTP 404 for a robots file (session 2524). License: not settled.
No terms of reuse were found within the session's ceiling; Kosovo's administrative instruction 02/2023 sets the sale of
statistical data, and Eurostat's GEOSTAT conditions keep Kosovo's data its office's, commercial use by approval.
Internal until the terms are read or a ruling.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ask_kosovo_electricity_monthly"
CONNECTOR = "ask_kosovo_energy"
SOURCE = "ask:energy_tab01"
HOST = "askdata.rks-gov.net"
URL = "https://askdata.rks-gov.net/api/v1/en/ASKdata/Energy/Monthly%20indicators/tab01.px"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
DIMS = ["MWH", "Viti/muaji"]
ITEMS = {"Gross Production from Power Plants": ("thermal", "gross_production"),
         "Gross Production from Hydropower Plants": ("hydro", "gross_production"),
         "Gross Production from Wind and Solar": ("wind_solar", "gross_production"),
         "Import": ("total", "imports"), "Export": ("total", "exports"),
         "Gross Electricity Available": ("total", "gross_available"),
         "Households": ("households", "consumption"), "Commercial": ("commercial", "consumption"),
         "Industry": ("industry", "consumption"), "Public lighting & others": ("public_lighting_other", "consumption"),
         "Consumers 220-110kv": ("consumers_220_110kv", "consumption"), "Mining": ("mining", "consumption"),
         "Electricity consumption": ("total_consumption", "consumption")}
X_COLS = ["x_period"]


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def parse(js, base):
    dims = js.get("id") or []
    if dims != DIMS:
        raise RuntimeError(f"the dimensions are {dims}, not {DIMS}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    ilabel = js["dimension"]["MWH"]["category"]["label"]
    unknown = sorted(set(ilabel.values()) - set(ITEMS))
    if unknown:
        raise RuntimeError(f"an item not in the map: {unknown}")
    plabel = js["dimension"]["Viti/muaji"]["category"]["label"]
    rows, seen = [], set()
    for k, (ic, pc) in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        v = js["value"][k]
        if v is None:
            continue
        period = plabel.get(pc, pc)
        m = re.fullmatch(r"(\d{4})M?(\d{2})", period)          # ASK labels some months without the M (202308)
        if not m or not 1 <= int(m.group(2)) <= 12:
            raise RuntimeError(f"a month not of the form YYYYMnn or YYYYnn: {period!r}")
        label = ilabel[ic]
        item, var = ITEMS[label]
        key = (item, var, period)
        if key in seen:
            raise RuntimeError(f"{key} given twice")
        seen.add(key)
        rows.append(dict(entity=f"ask:xk:{item}", variable=var, ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="XK", market="", node=label, **base, x_period=period))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    return t


def get(offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, "query_tab01.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [{"code": c, "selection": {"filter": "all", "values": ["*"]}} for c in DIMS], "response": {"format": "json-stat2"}}
    r = requests.post(URL, json=body, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": URL, "query": body, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  POST {URL}: {len(r.content)} bytes, saved as {path}")
    time.sleep(2)
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASK: Kosovo's electricity production and consumption a month, from 2022")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
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
        js, at = get(args.offline, log)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=at, vintage=js.get("updated", "") or "")
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "gross_production"].assign(y=lambda d: d.ts_utc.str[:4]).groupby("y").agg(v=("value", "sum"), n=("ts_utc", "nunique"))
        head = [
            "Energy Research Warehouse (ERW): Kosovo Agency of Statistics (ASK), ASKdata, Electricity production and consumption (tab01), "
            f"Kosovo's electricity a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2524)",
            "Shape: series (docs/datastandard.md v0). entity ask:xk:<item>; variable gross_production (thermal, hydro, wind_solar), imports, exports, "
            "gross_available, consumption (by sector and total); unit MWh (ASK's thousands of MWh, its dimension named MWH, times 1,000); ts_utc the month's first day; freq P1M; geo XK; node ASK's label.",
            f"{len(t)} rows; gross production TWh, whole years: " + ", ".join(f"{y} {r['v'] / 1e6:.2f}" for y, r in g.iterrows() if r["n"] == 12)
            + ". A cell without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ask_kosovo_electricity.py; the answer retrieved {at} (updated {base['vintage'] or 'not given'})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_tab01.json (not in git)",
            f"Source: {SOURCE} Kosovo Agency of Statistics, ASKdata, Energy, Monthly indicators, tab01",
            f"  access: {URL} (one JSON-stat query by POST)",
            "License: internal (no terms of reuse found; Kosovo's statistics are its agency's, commercial use by approval).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Kosovo Agency of Statistics (ASK)",
                                    report="ASKdata, Energy, Monthly indicators: Electricity production and consumption (tab01)",
                                    report_url=URL, document_list="https://askdata.rks-gov.net/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
