#!/usr/bin/env python3
"""Eurostat's monthly crude oil imports by field of production, the EU as a whole (nrg_ti_coifpm, geo EU_V): for each of
the crude streams Europe buys (West Texas Intermediate, Bakken, Brent, Urals and the rest, 819 named by Eurostat), the
volume, its value and average price in USD, and its API gravity and sulphur content, a month from January 2016 (session
2427, chain 115: a second source of the session's own choosing, beside the crude oil imports by partner of session 2369;
it prices and grades the U.S. crude Europe buys).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_crude_imports_by_field_monthly.csv,
from Eurostat's statistics API (no key), filtered to the EU aggregate, as JSON-stat 2.0. The query is answered
asynchronously: the first answer asks to try again later, so the connector asks the same address again, a minute apart,
until the data come:

    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_coifpm?format=JSON&lang=EN&geo=EU_V&sinceTimePeriod=2016-01

    entity      eurostat_crude_field:EU:<Eurostat crude oil code> (TOTAL for every stream together); node the stream's
                English name as Eurostat gives it ("United States Texas - West Texas Intermediate (WTI)")
    variable    volume (kbbl: Eurostat's thousand barrels), value (USD: Eurostat's thousand USD times 1,000), price
                (USD/bbl: Eurostat's average price), api_gravity (degAPI), sulphur (pct: percent by weight)
    ts_utc      the month's first day; freq P1M; geo blank (the EU, an aggregate)
    x_*         Eurostat's crude oil code and name, the indicator's code, the observation's flag (JSON-stat status)

Eurostat's EU_V is "the European Union (aggregate changing according to the context)": the member states of the month.
Cells Eurostat marks confidential carry no value and have no row. A volume or value of 0 is kept (no import that month);
a price, API gravity or sulphur of 0 is not taken, since Eurostat writes 0 there for a stream with no import or a
confidential volume, which is no measurement (the header counts them). The reporting companies indicator has no value for
the EU and is not read. A dimension, frequency or indicator not expected, or a value not a number, stops the run.

    python warehouse/connectors/eurostat_crude_by_field.py [--offline] [--out-dir DIR]

Ceiling: the address asked at most 10 times (a minute apart) until it answers with the data; reused with --offline from
warehouse/raw/eurostat_crude_imports_by_field_monthly/nrg_ti_coifpm_eu.json. ec.europa.eu's robots file disallows the
old /eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI agent
(session 2427). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes is
authorised provided the source is acknowledged"; source: Eurostat.
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
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import eurostat_res_capacity as erc  # noqa: E402  the same publisher's terms and reader

NAME = "eurostat_crude_imports_by_field_monthly"
CONNECTOR = "eurostat_crude_imports_by_field_monthly"
SOURCE = "eurostat:nrg_ti_coifpm_eu"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_coifpm/default/table"
URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_coifpm?format=JSON&lang=EN"
       "&geo=EU_V&sinceTimePeriod=2016-01")
SAVED = "nrg_ti_coifpm_eu.json"
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_crudeoil", "x_indic_nrg", "x_flag"]
INDICATORS = {"VOL_THS_BBL": ("volume", "kbbl", 1.0, True), "VAL_THS_USD": ("value", "USD", 1000.0, True),
              "AVGPRC_USD_BBL": ("price", "USD/bbl", 1.0, False), "API_DEG": ("api_gravity", "degAPI", 1.0, False),
              "SULPH_PC": ("sulphur", "pct", 1.0, False), "CMPY_NR": (None, None, None, None)}


def fetch(log):
    for k in range(10):
        r = requests.get(URL, headers=erc.UA, timeout=600)
        if r.status_code == 200 and r.content.startswith(b'{"version"'):
            return r.content
        log(f"  try {k + 1}: HTTP {r.status_code} {r.content[:120]!r}")
        if r.status_code not in (200, 413):
            r.raise_for_status()
        time.sleep(60)
    raise RuntimeError("Eurostat did not answer with the data after 10 tries")


def build(js, retrieved):
    if js.get("id") != ["freq", "crudeoil", "indic_nrg", "geo", "time"]:
        raise RuntimeError(f"the dimensions are not the five expected: {js.get('id')}")
    dims = {d: js["dimension"][d]["category"] for d in js["id"]}
    if list(dims["freq"]["index"]) != ["M"] or list(dims["geo"]["index"]) != ["EU_V"]:
        raise RuntimeError(f"freq {list(dims['freq']['index'])} or geo {list(dims['geo']['index'])} not M and EU_V")
    if not set(dims["indic_nrg"]["index"]) <= set(INDICATORS):
        raise RuntimeError(f"an indicator not expected: {set(dims['indic_nrg']['index']) - set(INDICATORS)}")
    order = [sorted(dims[d]["index"], key=dims[d]["index"].get) for d in js["id"]]
    sizes = js["size"]
    status = js.get("status", {})
    names = dims["crudeoil"].get("label", {})
    rows, zeros = [], {}
    for key, v in js["value"].items():
        k = int(key)
        idx = []
        for s in reversed(sizes):
            idx.append(k % s)
            k //= s
        idx.reverse()
        code = {d: order[i][idx[i]] for i, d in enumerate(js["id"])}
        var, unit, factor, keep_zero = INDICATORS[code["indic_nrg"]]
        if var is None:
            raise RuntimeError(f"the reporting companies indicator has a value for the EU: {code}")
        if not re.fullmatch(r"\d{4}-\d\d", code["time"]):
            raise RuntimeError(f"a period not a month: {code['time']!r}")
        if not isinstance(v, (int, float)):
            raise RuntimeError(f"a value that is not a number: {v!r}")
        if v == 0 and not keep_zero:
            zeros[var] = zeros.get(var, 0) + 1
            continue
        c = code["crudeoil"]
        rows.append((f"eurostat_crude_field:EU:{c}", var, f"{code['time']}-01T00:00:00Z", round(float(v) * factor, 3), unit,
                     names.get(c, c), c, code["indic_nrg"], status.get(key, "")))
    t = pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value", "unit", "node", "x_crudeoil", "x_indic_nrg", "x_flag"])
    t = t.assign(freq="P1M", geo="", market="", source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage="")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), zeros


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ti_coifpm: the EU's crude oil imports by field of production, a month")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    path = os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)
    try:
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved answer at {path}")
            content = open(path, "rb").read()
            retrieved = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log(f"  saved answer reused: {path} ({len(content):,} bytes, saved {retrieved})")
        else:
            content = fetch(log)
            retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(content)
            log(f"  answer saved: {path} ({len(content):,} bytes)")
        js = json.loads(content.decode("utf-8"))
        t, zeros = build(js, retrieved)
        streams_from = t[t.x_crudeoil != "TOTAL"].ts_utc.min()[:7]
        months = pd.period_range(t.ts_utc.min()[:7], t.ts_utc.max()[:7], freq="M").strftime("%Y-%m")
        empty = sorted(set(months) - set(t.ts_utc.str[:7]))
        vol_last = t[t.variable == "volume"].ts_utc.max()[:7]
        api = t[t.variable == "api_gravity"].value
        high, top = int((api > 70).sum()), float(api.max())
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, crude oil imports by field of production - monthly data (nrg_ti_coifpm), the EU, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}: volume, value, price, API gravity and sulphur by crude stream (session 2427)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_crude_field:EU:<Eurostat crude oil code> (TOTAL every stream together); variable volume (kbbl), value (USD, Eurostat's thousand USD times 1,000), price (USD/bbl), api_gravity (degAPI), sulphur (pct by weight); "
            "ts_utc the month's first day; freq P1M; geo blank (the EU, Eurostat's EU_V: the member states of the month); node the stream's name as Eurostat gives it; x_crudeoil, x_indic_nrg, x_flag Eurostat's codes and the observation's status.",
            f"{len(t)} rows, {t.x_crudeoil.nunique() - 1} streams and their total (TOTAL). The streams begin in {streams_from}: before, only TOTAL's volume, value and price are given. "
            + (f"Months with no row at all: {', '.join(empty)}. " if empty else "")
            + f"Volume, value and price end in {vol_last}; API gravity and sulphur in {t.ts_utc.max()[:7]}. "
            + f"API gravity as published: {high} values above 70 degrees (the highest {top:,.1f}), beyond any crude oil's; they are kept, not corrected. "
            + "Confidential cells have no row. A volume or value of 0 is kept; a price, API gravity or sulphur of 0 is not taken (Eurostat writes 0 there for a stream with no import or a confidential volume): "
            + ", ".join(f"{n} {k}" for k, n in sorted(zeros.items())) + " left out. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_crude_by_field.py; the answer retrieved {retrieved}; Eurostat's update {js.get('updated', '')}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (not in git)",
            f"Source: {SOURCE} Eurostat, Crude oil imports by field of production - monthly data (nrg_ti_coifpm), the EU (EU_V), {PAGE}",
            f"  access: {URL} (answered asynchronously: the same address asked again until the data come)",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_ti_coifpm. Eurostat bears no responsibility for this reshaping (the rows filtered to the EU and renamed, the zero prices and grades left out, the values unchanged but for the thousand USD written as USD).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Crude oil imports by field of production - monthly data (nrg_ti_coifpm), the EU",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.x_crudeoil.nunique()} streams; zeros left out {zeros}")
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
