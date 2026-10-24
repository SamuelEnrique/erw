#!/usr/bin/env python3
"""Finland's electricity supply and consumption, a month from January 1992, as Statistics Finland publishes it (StatFin
table 12su): generation by source (hydro, wind, solar, nuclear, combined heat and power and its kinds, condensing power),
net imports by country, and total consumption (session 2273, chain 103: a second source of the session's own choosing,
Finland beside Norway's and Sweden's tables of chain 099).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statfi_finland_electricity_monthly.csv, from
Statistics Finland's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, to the same
address:

    https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12su.px   "Supplies and total consumption of electricity by Month,
                                                                 Electricity production/supply and Information"

    entity      statfi:fi
    variable    the line's English name in snake case, its leading code dropped (total_electricity_consumption,
                total_electricity_generation, hydro_power, wind_power, solar_power, nuclear_power, combined_heat_and_power_chp,
                chp_district_heating, chp_industri, micro_chp, conventional_condensing_power, net_imports_of_electricity,
                norway, sweden, russia, estonia); node the name as Statistics Finland writes it; x_code its code (SSS, 1, ...)
    unit        MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo FI

Only the quantity in GWh (contentscode maara_gwh) is taken; the table's changes, cumulative sums and shares are not. The
net imports by country are signed as Statistics Finland gives them. Totals are its lines, never sums made here; a cell it
leaves empty has no row; nothing is filled. A metadata without the three variables, a month not of the form YYYYMmm, a
value array not the size of the dimensions or a line and month given twice stops the run.

    python warehouse/connectors/statfi_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/statfi_electricity/ (one address
serves both) and reused offline. pxdata.stat.fi has no robots file (HTTP 404); stat.fi's disallows a few paths not used
here (session 2273). License: CC BY 4.0, Statistics Finland's terms of use ("Statistics Finland's open data materials and
public content of the web service are covered by the Creative Commons Attribution 4.0 International licence"); source:
Statistics Finland.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statfi_finland_electricity_monthly"
CONNECTOR = "statfi_electricity"
SOURCE = "statfi:12su"
TABLE_URL = "https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12su.px"
PAGE = "https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__ehk/statfin_ehk_pxt_12su.px/"
TERMS = "https://stat.fi/en/about-us/get-to-know-statistics-finland/legislation/terms-of-use"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_12su.json"
DIMS = ("timeperiod_m", "energia_30_20200915", "contentscode")
X_COLS = ["x_code"]


def slug(label):
    s = re.sub(r"^[0-9.]+\s+|^SSS\s+", "", label.strip())
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def query(meta):
    codes = {v["code"]: v for v in meta.get("variables", [])}
    if set(codes) != set(DIMS):
        raise RuntimeError(f"the table's variables are not the three expected: {sorted(codes)}")
    if "maara_gwh" not in codes["contentscode"]["values"]:
        raise RuntimeError("no quantity in GWh among the table's contents")
    sel = [("timeperiod_m", codes["timeperiod_m"]["values"]), ("energia_30_20200915", codes["energia_30_20200915"]["values"]),
           ("contentscode", ["maara_gwh"])]
    return {"query": [{"code": c, "selection": {"filter": "item", "values": v}} for c, v in sel], "response": {"format": "json-stat2"}}


def parse(js, base):
    dims = js.get("id")
    if sorted(dims or []) != sorted(DIMS):
        raise RuntimeError(f"the answer's dimensions are not the three expected: {dims}")
    cats = []
    for d in dims:
        c = js["dimension"][d]["category"]
        idx = c["index"]
        codes = sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)
        cats.append((d, codes, c.get("label", {})))
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    labels = next(c[2] for c in cats if c[0] == "energia_30_20200915")
    rows = []
    for k, combo in enumerate(itertools.product(*[c[1] for c in cats])):
        v = js["value"][k]
        if v is None:
            continue
        cell = dict(zip(dims, combo))
        if cell["contentscode"] != "maara_gwh":
            raise RuntimeError(f"a content other than the quantity in GWh: {cell['contentscode']}")
        m = re.fullmatch(r"(\d{4})M(\d\d)", cell["timeperiod_m"])
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMmm: {cell['timeperiod_m']!r}")
        code = cell["energia_30_20200915"]
        label = labels[code]
        rows.append(dict(entity="statfi:fi", variable=slug(label), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="FI", market="", node=label.strip(), **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a line and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Finland table 12su: Finland's electricity supply and consumption, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("pxdata.stat.fi"):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved query at {path}")
            saved = json.load(open(path, encoding="utf-8"))
            meta, js, retrieved = saved["meta"], saved["answer"], saved["retrieved_at"]
            query(meta)
            log(f"  saved metadata and answer reused: {path} (retrieved {retrieved})")
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=60, pause=1)
            meta = json.loads(mcontent.decode("utf-8"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            js, retrieved = r.json(), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": js}, open(path, "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {path}")
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage=js.get("updated", "") or "")
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        c = t[t.variable == "total_electricity_consumption"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        c = c[c["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): Statistics Finland, StatFin table 12su, Supplies and total consumption of electricity, a month, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2273)",
            "Shape: series (docs/datastandard.md v0). entity statfi:fi; variable the line in snake case (total_electricity_consumption, "
            "total_electricity_generation and its sources, net_imports_of_electricity and its countries); unit MWh (the table's GWh times 1,000); "
            "ts_utc the month's first day; freq P1M; geo FI; node the line as Statistics Finland writes it; x_code its code.",
            f"{len(t)} rows, {t.variable.nunique()} lines; total consumption TWh a full year: " + ", ".join(f"{k} {v:.1f}" for k, v in c.items() if k >= "2015")
            + ". Only the quantity in GWh is taken. A cell left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statfi_electricity.py; the query answered {retrieved}; updated {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} Statistics Finland, StatFin, table 12su, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON-stat query by POST)",
            f"License: public (CC BY 4.0, {TERMS}). Source: Statistics Finland.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} lines, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Finland", report="StatFin table 12su: Supplies and total consumption of electricity, monthly",
                                    report_url=PAGE, document_list=TABLE_URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
