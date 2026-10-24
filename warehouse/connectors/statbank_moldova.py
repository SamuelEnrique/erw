#!/usr/bin/env python3
"""Moldova's electricity a month from January 2015: production, imports, electricity acquired from other sources, stock
change, exports, gross inland consumption and the residential sector's consumption, as the National Bureau of Statistics
publishes it in StatBank (table ENE010100) (session 2358, chain 110: in Bangladesh's place, whose publishers' certificates
fail verification).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statbank_moldova_electricity_monthly.csv,
from StatBank's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST to the same address,
as chain 106's csp_latvia_electricity.py and session 2357's makstat_macedonia.py read theirs:

    https://statbank.statistica.md/PxWeb/api/v1/en/40 Statistica economica/15 ENE/serii lunare/ENE010100.px
    "Stocks, inputs and electricity consumption by Indicators, Years and Months"

    entity      statbank_md:md
    variable    production, imports, acquired_from_other_sources, stock_change, exports, gross_inland_consumption,
                residential_consumption ("of which: consumed in the residential sector"); node the indicator as StatBank
                writes it; x_code its code (1 to 7)
    unit        MWh: StatBank states no unit in the API; its figures are thousand kWh, which is MWh (session 2358: its
                exports equal Eurostat's for Moldova, median ratio 1.000 over 79 months, and its production, gross, is
                about 13 percent over Eurostat's net production); ts_utc the month's first day; freq P1M; geo MD

The bureau's "Import" leaves out the electricity bought from the Transnistrian region's plant, which it counts as
"acquired from other sources"; Eurostat counts both as imports (session 2358). A month StatBank leaves empty (those of 2026
not yet published) has no row; nothing is filled. A metadata without the three variables (Indicatori, Ani, Luni), an
indicator list not the seven expected, a value array not the size of the dimensions, or an indicator and month given twice
stops the run.

    python warehouse/connectors/statbank_moldova.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/statbank_moldova/ and reused offline.
statbank.statistica.md has no robots file (HTTP 404, session 2358). License: internal until the licenses' round reads the
National Bureau of Statistics' terms.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statbank_moldova_electricity_monthly"
CONNECTOR = "statbank_moldova"
SOURCE = "statbank_md:ENE010100"
HOST = "statbank.statistica.md"
TABLE_URL = "https://statbank.statistica.md/PxWeb/api/v1/en/40%20Statistica%20economica/15%20ENE/serii%20lunare/ENE010100.px"
PAGE = "https://statbank.statistica.md/PxWeb/pxweb/en/40%20Statistica%20economica/40%20Statistica%20economica__15%20ENE__serii%20lunare/ENE010100.px/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_ENE010100.json"
IND, YEAR, MONTH = "Indicatori", "Ani", "Luni"
INDICATORS = {"1": ("production", "Production"), "2": ("imports", "Import"),
              "3": ("acquired_from_other_sources", "Acquired from other sources"), "4": ("stock_change", "Stock change"),
              "5": ("exports", "Export"), "6": ("gross_inland_consumption", "Gross inland consumption"),
              "7": ("residential_consumption", "of which: consumed in the residential sector")}
X_COLS = ["x_code"]


def query(meta):
    v = {x["code"]: x for x in meta.get("variables", [])}
    if set(v) != {IND, YEAR, MONTH}:
        raise RuntimeError(f"the table's variables are not the three expected: {sorted(v)}")
    got = dict(zip(v[IND]["values"], v[IND]["valueTexts"]))
    if got != {k: lab for k, (_, lab) in INDICATORS.items()}:
        raise RuntimeError(f"the indicators are not the seven expected: {got}")
    if v[MONTH]["values"] != [f"{m:02d}" for m in range(1, 13)]:
        raise RuntimeError(f"the months are not 01 to 12: {v[MONTH]['values']}")
    return {"query": [{"code": c, "selection": {"filter": "item", "values": v[c]["values"]}} for c in (IND, YEAR, MONTH)],
            "response": {"format": "json-stat2"}}


def parse(js, base):
    dims = js.get("id")
    if dims != [IND, YEAR, MONTH]:
        raise RuntimeError(f"the answer's dimensions are not the three expected: {dims}")
    cats = []
    for d in dims:
        idx = js["dimension"][d]["category"]["index"]
        cats.append(sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx))
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    rows = []
    for k, (code, year, month) in enumerate(itertools.product(*cats)):
        v = js["value"][k]
        if v is None:
            continue
        var, label = INDICATORS[code]
        rows.append(dict(entity="statbank_md:md", variable=var, ts_utc=f"{year}-{month}-01T00:00:00Z", value=float(v), unit="MWh",
                         freq="P1M", geo="MD", market="", node=label, **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an indicator and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="StatBank ENE010100: Moldova's electricity, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
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
    path = os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved query at {path}")
            saved = json.load(open(path, encoding="utf-8"))
            meta, js, retrieved = saved["meta"], saved["answer"], saved["retrieved_at"]
            query(meta)
            log(f"  saved metadata and answer reused: {path} (retrieved {retrieved})")
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=90, pause=1)
            meta = json.loads(mcontent.decode("utf-8-sig"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            js, retrieved = json.loads(r.content.decode("utf-8-sig")), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": js}, open(path, "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {path}")
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage="")
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "production"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): National Bureau of Statistics of the Republic of Moldova, StatBank table ENE010100, Stocks, inputs "
            f"and electricity consumption, a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2358)",
            "Shape: series (docs/datastandard.md v0). entity statbank_md:md; variable production, imports, acquired_from_other_sources, "
            "stock_change, exports, gross_inland_consumption, residential_consumption; unit MWh (StatBank's thousand kWh: no unit in the "
            "API, its exports equal Eurostat's for Moldova, session 2358); ts_utc the month's first day; freq P1M; geo MD; node the "
            "indicator as StatBank writes it; x_code its code.",
            f"{len(t)} rows; production TWh a full year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items()) + ". The bureau's imports "
            "leave out the electricity bought from the Transnistrian region's plant, counted as acquired_from_other_sources (Eurostat "
            "counts both as imports). A month left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statbank_moldova.py; the query answered {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} National Bureau of Statistics of the Republic of Moldova, StatBank, Energy resources, monthly series, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON-stat query by POST)",
            "License: internal until the licenses' round reads the National Bureau of Statistics' terms. Source: National Bureau of Statistics of the Republic of Moldova.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} indicators, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="National Bureau of Statistics of the Republic of Moldova (StatBank)",
                                    report="StatBank table ENE010100: Stocks, inputs and electricity consumption, monthly",
                                    report_url=PAGE, document_list=TABLE_URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
