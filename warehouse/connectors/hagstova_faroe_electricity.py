#!/usr/bin/env python3
"""The Faroe Islands' electricity, a year: SEV's production by source (thermal, hydro, wind, solar, biogas, tidal),
1990 to 2025, and its sales by consumer group, 1997 to 2025, as Statistics Faroe Islands (Hagstova Foroya) publishes
them in tables UO03020 and UO03030 (session 2502, chain 121: a source of the session's own choosing; the ERW held no
Faroese source).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/hagstova_faroe_electricity_annual.csv,
from Statistics Faroe Islands' PxWeb API (no key), one JSON-stat 2.0 query a table by POST, every category and every
year selected (an empty query returns only the total, the category dimension eliminated):

    https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elgerd.px
        "UO03020 Electricity production of SEV by hydro, wind and thermal in MWh (1990-2025)"
    https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elsola.px
        "UO03030 Electricity sales of SEV in MWh (1997-2025)"

    entity      hagstova:fo:<item> (total, thermal, hydro, wind, solar, biogas, tidal; total_sales and the eight consumer
                groups: fisheries_aquaculture, production_construction, shops_hotels, transport_communication,
                finance_business_services, public_private_services, street_lights, households)
    variable    generation (UO03020) or sales (UO03030)
    unit        MWh, as given
    ts_utc      the year's first day; freq P1Y; geo FO
    node        the category as Statistics Faroe Islands names it; x_table the table's code

SEV is the Faroe Islands' public power company. A cell without a number has no row; nothing is filled. A table without
its year and category dimensions, a category not in the map, a year not of four digits, a value array not the size of
the dimensions, or a key given twice stops the run.

    python warehouse/connectors/hagstova_faroe_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests a run, saved in warehouse/raw/hagstova_faroe_energy/ (query_<table>.json, the answer with its
time of retrieval) and read from there with --offline. statbank.hagstova.fo has no robots file (HTTP 404, session 2502).
License: CC BY 4.0, Statistics Faroe Islands' terms of use (hagstova.fo/en/terms-use: statistical data and tables, the
statbank and its API included, for any purpose, commercial included, with Statistics Faroe Islands credited as the
source): public.
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

NAME = "hagstova_faroe_electricity_annual"
CONNECTOR = "hagstova_faroe_energy"
SOURCE = "hagstova:UO03"
HOST = "statbank.hagstova.fo"
BASE = "https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/"
PAGE = "https://statbank.hagstova.fo/pxweb/en/H2/H2__UO__UO03/"
TERMS = "https://hagstova.fo/en/terms-use"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# table -> (its code, the category dimension's label, the variable, {category label: item})
TABLES = {
    "ork_elgerd": ("UO03020", "production", "generation",
                   {"Total": "total", "Thermal": "thermal", "Hydro": "hydro", "Wind": "wind", "Solar PV": "solar", "Biogas": "biogas",
                    "Tidal energy": "tidal"}),
    "ork_elsola": ("UO03030", "consumer groups", "sales",
                   {"Total sale of electricity": "total_sales", "Agric., fish. ind., aquac., ressource comp.": "fisheries_aquaculture",
                    "Production and construction": "production_construction", "Shops, restaurants and hotels, etc.": "shops_hotels",
                    "Transport, mail, and communication": "transport_communication",
                    "Finance, insurance a.o. industrial serv.": "finance_business_services",
                    "Publ. and priv. serv., church., meet. h., etc.": "public_private_services", "Street lights": "street_lights",
                    "Houses, apts, summer and boat houses": "households"}),
}
X_COLS = ["x_table"]


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def parse(js, table, base):
    code, cat_label, variable, items = TABLES[table]
    dims = js.get("id") or []
    labels = {d: (js["dimension"][d].get("label") or d) for d in dims}
    year = [d for d in dims if labels[d] == "year"]
    cat = [d for d in dims if labels[d] == cat_label]
    if len(year) != 1 or len(cat) != 1 or len(dims) != 2:
        raise RuntimeError(f"{code}: the dimensions are not year and {cat_label}: {[labels[d] for d in dims]}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{code}: {len(js['value'])} values for dimensions of size {js['size']}")
    clabel = js["dimension"][cat[0]]["category"]["label"]
    unknown = sorted(set(clabel.values()) - set(items))
    if unknown:
        raise RuntimeError(f"{code}: a category not in the map: {unknown}")
    ylabel = js["dimension"][year[0]]["category"]["label"]
    rows = []
    for k, combo in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        cell = dict(zip(dims, combo))
        v = js["value"][k]
        if v is None:
            continue
        y = ylabel.get(cell[year[0]], cell[year[0]])
        if not re.fullmatch(r"\d{4}", str(y)):
            raise RuntimeError(f"{code}: a year not of four digits: {y!r}")
        label = clabel[cell[cat[0]]]
        rows.append(dict(entity=f"hagstova:fo:{items[label]}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(float(v), 3),
                         unit="MWh", freq="P1Y", geo="FO", market="", node=label, **base, x_table=code))
    return rows


def get(table, offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, f"query_{table}.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [{"code": c, "selection": {"filter": "all", "values": ["*"]}} for c in (TABLES[table][1], "year")],
            "response": {"format": "json-stat2"}}
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
    ap = argparse.ArgumentParser(description="Statistics Faroe Islands: SEV's electricity production and sales")
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
            base = dict(source=SOURCE, source_url=BASE + table + ".px", retrieved_at=at, vintage="")   # the answer's "updated" is a placeholder (2000-01-01)
            rows += parse(js, table, base)
            got.append(f"{TABLES[table][0]} {at}")
        t = pd.DataFrame(rows)
        if t.empty:
            raise RuntimeError("no value in the answers")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[(t.variable == "generation") & (t.entity == "hagstova:fo:total")].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics Faroe Islands (Hagstova Foroya), tables UO03020 and UO03030, SEV's electricity production by source "
            f"and sales by consumer group, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2502)",
            "Shape: series (docs/datastandard.md v0). entity hagstova:fo:<item>; variable generation (UO03020, by source) or sales (UO03030, by consumer group); "
            "unit MWh as given; ts_utc the year's first day; freq P1Y; geo FO; node the category as Statistics Faroe Islands names it; x_table the table.",
            f"{len(t)} rows; generation GWh: " + ", ".join(f"{k[:4]} {v / 1e3:.1f}" for k, v in g.items() if k[:4] in ("1990", "2000", "2010", "2020", "2025"))
            + ". A cell without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/hagstova_faroe_electricity.py; " + "; ".join(got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_<table>.json (not in git)",
            f"Source: {SOURCE} Statistics Faroe Islands (Hagstova Foroya), {PAGE}",
            f"  access: {BASE}<table>.px (one JSON-stat query a table by POST)",
            f"License: CC BY 4.0 (Statistics Faroe Islands' terms of use, {TERMS}); credit: Statistics Faroe Islands.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Faroe Islands (Hagstova Foroya)",
                                    report="Tables UO03020 (SEV's electricity production by source) and UO03030 (SEV's electricity sales by consumer group)",
                                    report_url=PAGE, document_list=BASE, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
