#!/usr/bin/env python3
"""Iceland's installed capacity and annual generation of the public power plants, 1976 to 2019, as Statistics Iceland
(Hagstofa Islands) publishes them from the National Energy Authority's figures (table IDN02101) (session
2397, chain 113: a source of the session's own choosing; the ERW held Iceland only in Eurostat's capacity table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/hagstofa_iceland_power_annual.csv, from
Statistics Iceland's PxWeb API (no key), one JSON-stat 2.0 query by POST (an empty query: every value):

    https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/4_orkumal/2_framleidslaognotkun/IDN02101.px
        "Installed capacity and generation in public power plants 1976-2019"

    entity      hagstofa:is
    variable    capacity ("Installed capacity at end of period, MW"); generation ("Annual generation of energy, GWh")
    unit        MW as given; MWh (GWh times 1,000)
    ts_utc      the year's first day (the capacity is at the year's end); freq P1Y; geo IS
    node        the measure as Statistics Iceland names it; x_table the table's code

Not taken: IDN02101's second unit ("Hlutfall", a share, 100 in every cell); and the earlier table IDN02100 (1904 to
1975), whose figures run about twice IDN02101's where the two meet (1975: 992.4 MW and 4,591 GWh; 1976: 502.7 MW and
2,421.4 GWh; session 2397), not explained by either table, so not joined to it. The parser reads either table. A cell without a number has no row; nothing
is filled. A table without the year and energy dimensions, an energy label not the two expected, a year not of four
digits, a value array not the size of the dimensions, or a measure and year given twice stops the run.

    python warehouse/connectors/hagstofa_iceland_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/hagstofa_energy/ (query_<table>.json, the answer with its time of
retrieval) and read from there with --offline. px.hagstofa.is has no robots file (HTTP 404, session 2397). License:
CC BY 4.0, Statistics Iceland's terms of use (statice.is, "Open data access"): public, with Statistics Iceland credited.
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

NAME = "hagstofa_iceland_power_annual"
CONNECTOR = "hagstofa_energy"
SOURCE = "hagstofa:IDN02101"
HOST = "px.hagstofa.is"
BASE = "https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/4_orkumal/2_framleidslaognotkun/"
PAGE = "https://px.hagstofa.is/pxen/pxweb/en/Umhverfi/Umhverfi__4_orkumal__2_framleidslaognotkun/"
TERMS = "https://statice.is/publications/open-data-access/"
TABLES = ["IDN02101"]   # IDN02100 (1904 to 1975) not taken: see the docstring
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MEASURES = {"Installed capacity at end of period, MW": ("capacity", "MW", 1.0),
            "Annual generation of energy, GWh": ("generation", "MWh", 1000.0)}
X_COLS = ["x_table"]


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def parse(js, table, base):
    dims = js.get("id") or []
    labels = {d: (js["dimension"][d].get("label") or d) for d in dims}
    year = [d for d in dims if labels[d] == "Year"]
    energy = [d for d in dims if labels[d] == "Energy"]
    unit = [d for d in dims if labels[d] == "Unit"]
    if len(year) != 1 or len(energy) != 1 or len(dims) != 2 + len(unit):
        raise RuntimeError(f"{table}: the dimensions are not Year, Energy (and Unit): {[labels[d] for d in dims]}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{table}: {len(js['value'])} values for dimensions of size {js['size']}")
    elabel = js["dimension"][energy[0]]["category"]["label"]
    if set(elabel.values()) != set(MEASURES):
        raise RuntimeError(f"{table}: the energy labels are not the two expected: {sorted(elabel.values())}")
    keep_unit = None
    if unit:
        ulabel = js["dimension"][unit[0]]["category"]["label"]
        q = [k for k, v in ulabel.items() if v == "Magn"]
        if len(q) != 1:
            raise RuntimeError(f"{table}: no single unit Magn (quantity): {ulabel}")
        keep_unit = q[0]
    rows = []
    for k, combo in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        cell = dict(zip(dims, combo))
        if unit and cell[unit[0]] != keep_unit:
            continue
        v = js["value"][k]
        if v is None:
            continue
        y = js["dimension"][year[0]]["category"]["label"].get(cell[year[0]], cell[year[0]])
        if not re.fullmatch(r"\d{4}", str(y)):
            raise RuntimeError(f"{table}: a year not of four digits: {y!r}")
        label = elabel[cell[energy[0]]]
        variable, u, f = MEASURES[label]
        rows.append(dict(entity="hagstofa:is", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(float(v) * f, 3), unit=u,
                         freq="P1Y", geo="IS", market="", node=label, **base, x_table=table))
    return rows


def get(table, offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, f"query_{table}.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [], "response": {"format": "json-stat2"}}
    r = requests.post(BASE + table + ".px", json=body, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {table}")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": BASE + table + ".px", "query": body, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  POST {BASE}{table}.px: {len(r.content)} bytes, saved as {path}")
    time.sleep(2)
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Iceland: the public power plants' capacity and generation, 1976 to 2019")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
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
        rows, got = [], []
        for table in TABLES:
            js, at = get(table, args.offline, log)
            upd = js.get("updated", "") or ""
            base = dict(source=SOURCE, source_url=BASE + table + ".px", retrieved_at=at, vintage="" if upd.startswith("9999") else upd)
            rows += parse(js, table, base)
            got.append(f"{table} {at} (updated {base['vintage'] or 'not given'}; source: {js.get('source') or 'not given'})")
        t = pd.DataFrame(rows)
        if t.empty:
            raise RuntimeError("no value in the answers")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a measure and year given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "generation"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics Iceland, table IDN02101, installed capacity and generation in public power plants, "
            f"{t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2397)",
            "Shape: series (docs/datastandard.md v0). entity hagstofa:is; variable capacity (MW, at the year's end) or generation (MWh, the table's GWh times 1,000); "
            "ts_utc the year's first day; freq P1Y; geo IS; node the measure as Statistics Iceland names it; x_table the table.",
            f"{len(t)} rows; generation TWh: " + ", ".join(f"{k[:4]} {v / 1e6:.2f}" for k, v in g.items() if k[:4] in ("1976", "1990", "2000", "2010", "2019"))
            + ". Not taken: the share (Hlutfall), and table IDN02100 (1904 to 1975), about twice IDN02101's level where they meet. A cell without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/hagstofa_iceland_electricity.py; " + "; ".join(got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_<table>.json (not in git)",
            f"Source: {SOURCE} Statistics Iceland (Hagstofa Islands), from the National Energy Authority, {PAGE}",
            f"  access: {BASE}<table>.px (one JSON-stat query a table by POST)",
            f"License: CC BY 4.0 (Statistics Iceland's terms of use, {TERMS}); credit: Statistics Iceland.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Iceland (Hagstofa Islands)",
                                    report="Table IDN02101: installed capacity and generation in public power plants",
                                    report_url=PAGE, document_list=BASE, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
