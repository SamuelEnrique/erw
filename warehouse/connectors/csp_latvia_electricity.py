#!/usr/bin/env python3
"""Latvia's electricity production by source, imports, exports and supply to the internal market, a month from January
2006, as the Central Statistical Bureau of Latvia publishes it (table ENB010m) (session 2314, chain 106: a source of the
session's own choosing, Latvia beside session 2278's Estonia and session 2273's Finland).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/csp_latvia_electricity_monthly.csv, from the
Official Statistics Portal's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, to the
same address:

    https://data.stat.gov.lv/api/v1/en/OSP_PUB/START/NOZ/EN/ENB/ENB010m
    "Electricity production, imports, exports and consumption (million. kWh) by Indicator and Time period"

    entity      csp:lv
    variable    the indicator's English name in snake case, its leading dots dropped (total_gross_electricity_production,
                hydro_power_plants_hpp, combined_heat_and_power_plants_chp, wind_turbines, solar_power_plants,
                total_net_electricity_production, battery_energy_storage_system_bess, imports, exports,
                available_for_the_internal_market); node the name as CSP writes it; x_code its code (GEP, HPP, CHP, WT,
                SPP, NEP, BESS, IMP, EXP, INTM)
    unit        MWh (the table's million kWh, that is GWh, times 1,000); ts_utc the month's first day; freq P1M; geo LV

Totals are CSP's lines, never sums made here; a cell CSP leaves empty has no row; nothing is filled. A metadata without
the three variables, a unit other than million kWh, a month not of the form YYYYMmm, a value array not the size of the
dimensions, or an indicator and month given twice stops the run.

    python warehouse/connectors/csp_latvia_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/csp_latvia_electricity/ and reused
offline. data.stat.gov.lv has no robots file (HTTP 404); stat.gov.lv answers HTTP 403 to its robots file and was not
asked further (session 2314). License: not read (no licence text on the portal's pages; CSP's own site refused the
reader); internal until a read settles it.
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

NAME = "csp_latvia_electricity_monthly"
CONNECTOR = "csp_latvia_electricity"
SOURCE = "csp:ENB010m"
HOST = "data.stat.gov.lv"
TABLE_URL = "https://data.stat.gov.lv/api/v1/en/OSP_PUB/START/NOZ/EN/ENB/ENB010m"
PAGE = "https://data.stat.gov.lv/pxweb/en/OSP_PUB/START__NOZ__EN__ENB/ENB010m/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_ENB010m.json"
IND, CONT, TIME = "INDICATOR", "ContentsCode", "TIME"
UNIT = "million. kWh"
X_COLS = ["x_code"]


def slug(label):
    s = re.sub(r"^\.+", "", label.strip())
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def query(meta):
    v = {x["code"]: x for x in meta.get("variables", [])}
    if set(v) != {IND, CONT, TIME}:
        raise RuntimeError(f"the table's variables are not the three expected: {sorted(v)}")
    if v[CONT]["valueTexts"] != [UNIT]:
        raise RuntimeError(f"the table's unit is not {UNIT!r}: {v[CONT]['valueTexts']}")
    sel = [(IND, v[IND]["values"]), (CONT, v[CONT]["values"]), (TIME, v[TIME]["values"])]
    return {"query": [{"code": c, "selection": {"filter": "item", "values": vals}} for c, vals in sel], "response": {"format": "json-stat2"}}


def parse(js, base):
    dims = js.get("id")
    if sorted(dims or []) != sorted([IND, CONT, TIME]):
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
    labels = next(c[2] for c in cats if c[0] == IND)
    rows = []
    for k, combo in enumerate(itertools.product(*[c[1] for c in cats])):
        v = js["value"][k]
        if v is None:
            continue
        cell = dict(zip(dims, combo))
        m = re.fullmatch(r"(\d{4})M(\d\d)", cell[TIME])
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMmm: {cell[TIME]!r}")
        code = cell[IND]
        label = labels[code].strip()
        rows.append(dict(entity="csp:lv", variable=slug(label), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="LV", market="", node=label, **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an indicator and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="CSP table ENB010m: Latvia's electricity production, imports, exports and consumption, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
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
            meta = json.loads(mcontent.decode("utf-8-sig"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            js, retrieved = json.loads(r.content.decode("utf-8-sig")), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": js}, open(path, "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {path}")
        upd = js.get("updated", "") or ""
        if upd.startswith("9999"):      # a placeholder some PxWeb servers answer, not a date
            upd = ""
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage=upd)
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "total_gross_electricity_production"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): Central Statistical Bureau of Latvia, table ENB010m, Electricity production, imports, exports and "
            f"consumption, a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2314)",
            "Shape: series (docs/datastandard.md v0). entity csp:lv; variable the indicator in snake case (total_gross_electricity_production, "
            "its sources, total_net_electricity_production, battery_energy_storage_system_bess, imports, exports, available_for_the_internal_market); "
            "unit MWh (the table's million kWh times 1,000); ts_utc the month's first day; freq P1M; geo LV; node the indicator as CSP writes it; "
            "x_code its code.",
            f"{len(t)} rows, {t.variable.nunique()} indicators; gross production TWh a full year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items() if k >= "2015")
            + ". A cell left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/csp_latvia_electricity.py; the query answered {retrieved}; updated {base['vintage'] or 'not given'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} Central Statistical Bureau of Latvia, Official Statistics Portal, table ENB010m, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON-stat query by POST)",
            "License: internal (no licence text read: the portal's pages carry none, and stat.gov.lv refused the reader).",
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
            ip.update_sources([dict(source=SOURCE, publisher="Central Statistical Bureau of Latvia (CSP)",
                                    report="Table ENB010m: Electricity production, imports, exports and consumption (monthly)",
                                    report_url=PAGE, document_list=TABLE_URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
