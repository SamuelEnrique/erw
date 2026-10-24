#!/usr/bin/env python3
"""Greenland's electricity, a year: renewable production and consumption by source (hydropower, waste), 1996 on, and the
electricity Nukissiorfiit (the national utility) sold by location and rate, 2004 on, as Statistics Greenland publishes
them in Statbank tables ENX3VVE and ENX4NUK (session 2510, chain 122: a source of the session's own choosing; the ERW
held no Greenlandic source).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statgl_greenland_electricity_annual.csv,
from Statistics Greenland's PxWeb API (no key), one JSON-stat 2.0 query a table by POST, every value of every dimension
selected:

    https://bank.stat.gl/api/v1/en/Greenland/EN/EN20/ENX3VVE.px
        "Production and consumption of renewable energy etc. use by source, type and time" (unit MWh taken, TJ not)
    https://bank.stat.gl/api/v1/en/Greenland/EN/EN20/ENX4NUK.px
        "Electricity, water and heat sold by Nukissiorfiit by location, product and time" (the three electricity products
        taken: normal rates, fishing industry rates, electric heating; district heating and water not)

    entity      statgl:gl:<source> (total, hydropower, waste) for ENX3VVE; statgl:gl:<location> (total_sales, towns,
                settlements, a municipality, a town, a municipality's settlements) for ENX4NUK
    variable    renewable_production, renewable_consumption (ENX3VVE); sales_normal_rates, sales_fishing_industry_rates,
                sales_electric_heating (ENX4NUK)
    unit        MWh (ENX3VVE as given; ENX4NUK's kWh divided by 1,000)
    ts_utc      the year's first day; freq P1Y; geo GL
    node        the category labels as Statistics Greenland gives them; x_table the table's code

A location's slug is its label folded to ASCII: lower case, "- here of in towns" to `towns`, "- Nuuk town" to
`nuuk_town`, "- Settlements in Kommune Kujalleq" to `settlements_in_kommune_kujalleq`. A cell without a number has no
row. A table without its expected dimensions, a value array not the size of the dimensions, a year not of four digits,
or a key given twice stops the run. Nothing is filled.

    python warehouse/connectors/statgl_greenland_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests a run, saved in warehouse/raw/statgl_energy/ (query_<table>.json) and read from there with
--offline. bank.stat.gl and stat.gl have no robots file (session 2510); stat.gl's llms.txt asks agents to use the
Statbank API and to cite the Statbank with a link to the table. License: not settled. No page of terms for the
statistics was found; the "CC-BY-4.0" in Statistics Greenland's agent profile licenses that profile. Internal until the
terms are read or a ruling.
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
import unicodedata

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statgl_greenland_electricity_annual"
CONNECTOR = "statgl_energy"
SOURCE = "statgl:ENX3VVE_ENX4NUK"
HOST = "bank.stat.gl"
BASE = "https://bank.stat.gl/api/v1/en/Greenland/EN/EN20/"
PAGE = "https://bank.stat.gl/pxweb/en/Greenland/Greenland__EN__EN20/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TABLES = {"ENX3VVE": ["unit", "type", "source", "time"], "ENX4NUK": ["product", "location", "time"]}
VVE_TYPE = {"Production": "renewable_production", "Consumption": "renewable_consumption"}
NUK_PRODUCT = {"Electricity, normal rates [kWh]": "sales_normal_rates", "Electricity, fishingindustry rates [kWh]": "sales_fishing_industry_rates",
               "Electric heating [kWh]": "sales_electric_heating"}
X_COLS = ["x_table"]


def slug(label):
    s = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode().lower()
    s = s.replace("- here of in ", "").strip(" -")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def cells(js, table):
    dims = js.get("id") or []
    if [d.lower() for d in dims] != TABLES[table]:
        raise RuntimeError(f"{table}: the dimensions are {dims}, not {TABLES[table]}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{table}: {len(js['value'])} values for dimensions of size {js['size']}")
    labels = {d: js["dimension"][d]["category"].get("label", {}) for d in dims}
    for k, combo in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        yield {d.lower(): labels[d].get(c, c) for d, c in zip(dims, combo)}, js["value"][k]


def parse(js, table, base):
    rows = []
    for cell, v in cells(js, table):
        if v is None:
            continue
        year = str(cell["time"])
        if not re.fullmatch(r"\d{4}", year):
            raise RuntimeError(f"{table}: a year not of four digits: {year!r}")
        if table == "ENX3VVE":
            if cell["unit"] != "MWh":
                continue
            var, item, value = VVE_TYPE[cell["type"]], slug(cell["source"]), float(v)
            node = f"{cell['source']}, {cell['type']} (MWh)"
        else:
            if cell["product"] not in NUK_PRODUCT:
                continue
            var, item, value = NUK_PRODUCT[cell["product"]], slug(cell["location"]), float(v) / 1000.0
            node = f"{cell['location'].strip(' -')}, {cell['product']}"
        rows.append(dict(entity=f"statgl:gl:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(value, 3), unit="MWh",
                         freq="P1Y", geo="GL", market="", node=node, **base, x_table=table))
    return rows


def get(table, offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, f"query_{table}.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [{"code": c, "selection": {"filter": "all", "values": ["*"]}} for c in TABLES[table]],
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
    ap = argparse.ArgumentParser(description="Statistics Greenland: renewable electricity and Nukissiorfiit's sales")
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
            base = dict(source=SOURCE, source_url=BASE + table + ".px", retrieved_at=at, vintage=js.get("updated", "") or "")
            rows += parse(js, table, base)
            got.append(f"{table} {at} (updated {base['vintage'] or 'not given'})")
        t = pd.DataFrame(rows)
        if t.empty:
            raise RuntimeError("no value in the answers")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        h = t[(t.variable == "renewable_production") & (t.entity == "statgl:gl:hydropower")].set_index("ts_utc").value / 1e3
        s = t[(t.variable == "sales_normal_rates") & (t.entity == "statgl:gl:total_sales")].set_index("ts_utc").value / 1e3
        head = [
            "Energy Research Warehouse (ERW): Statistics Greenland, Statbank tables ENX3VVE and ENX4NUK, renewable production and consumption by source "
            f"and Nukissiorfiit's electricity sales by location, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2510)",
            "Shape: series (docs/datastandard.md v0). entity statgl:gl:<source or location>; variable renewable_production, renewable_consumption (ENX3VVE, MWh), "
            "sales_normal_rates, sales_fishing_industry_rates, sales_electric_heating (ENX4NUK, MWh from kWh); ts_utc the year's first day; freq P1Y; geo GL; "
            "node the categories as Statistics Greenland labels them; x_table the table.",
            f"{len(t)} rows; hydropower production GWh: " + ", ".join(f"{k[:4]} {v:.0f}" for k, v in h.items() if k[:4] in ("1996", "2005", "2015", "2020") or k == h.index.max())
            + "; sales at normal rates GWh: " + ", ".join(f"{k[:4]} {v:.0f}" for k, v in s.items() if k[:4] in ("2004", "2015") or k == s.index.max())
            + ". Not taken: TJ (ENX3VVE), district heating and water (ENX4NUK). A cell without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statgl_greenland_electricity.py; " + "; ".join(got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_<table>.json (not in git)",
            f"Source: {SOURCE} Statistics Greenland Statbank, {PAGE}ENX3VVE.px and ENX4NUK.px",
            f"  access: {BASE}<table>.px (one JSON-stat query a table by POST)",
            "License: internal (no terms for the statistics read; Statistics Greenland asks that the Statbank be cited with a link).",
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
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Greenland (Gronlands Statistik)",
                                    report="Statbank tables ENX3VVE (renewable energy production and consumption) and ENX4NUK (Nukissiorfiit's sales)",
                                    report_url=PAGE, document_list=BASE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
