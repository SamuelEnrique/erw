#!/usr/bin/env python3
"""Eurostat's monthly exports of natural gas and of LNG by partner country (nrg_te_gasm): how much gas each European
country sent to each destination, a month from January 2016 (session 2469, chain 119: a second source of the session's
own choosing; the exports side of the gas imports by partner the ERW holds, `eurostat_gas_imports_monthly`, so Norway's
pipeline and LNG exports to each EU country, and the EU members' re-exports, are read as their senders report them).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_gas_exports_monthly.csv, from
Eurostat's statistics API (no key), filtered to terajoules of gross calorific value, as JSON-stat 2.0. The query is
answered asynchronously: the first answer asks to try again later, so the connector asks the same address again, a
minute apart, until the data come:

    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_gasm?format=JSON&lang=EN&unit=TJ_GCV&sinceTimePeriod=2016-01

    entity      eurostat_gas_exports:<Eurostat geo code>:<SIEC code>:<partner code> (G3000 natural gas, G3200 liquefied
                natural gas, a part of it; the exporting country, then the destination or Eurostat's partner aggregate as
                Eurostat codes it: TOTAL, NSP (not specified) and regional groups; the header lists them); node
                "<product> exports to <partner's English name>"
    variable    exports
    unit        MWh: Eurostat's terajoules of gross calorific value (TJ_GCV) times 277.7778 (1 TJ = 1,000,000 MJ and
                1 MWh = 3,600 MJ, an exact definition), as `eurostat_gas_imports_monthly` writes them
    ts_utc      the month's first day; freq P1M
    geo         the exporting country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for EU27_2020 and EA21
    x_*         Eurostat's geo, SIEC and partner codes, the partner's English name, the observation's flag

Exporting countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice); those left out are
named in the header. Every partner is kept, Eurostat's aggregates among them. G3200 (LNG) is a part of G3000, so the two
are never added. Values as published, zeros kept; a cell with no value has no row; nothing is filled. A product, unit or
frequency not expected, or a value not a number, stops the run.

    python warehouse/connectors/eurostat_gas_exports.py [--offline] [--out-dir DIR]

Ceiling: the address asked at most 10 times (a minute apart) until it answers with the data; reused with --offline from
warehouse/raw/eurostat_gas_exports_monthly/nrg_te_gasm_tj.json. ec.europa.eu's robots file disallows the old
/eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2469). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes is
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
import eurostat_res_capacity as erc  # noqa: E402  the same publisher's countries (KEPT, AGGREGATES, ISO) and terms

NAME = "eurostat_gas_exports_monthly"
CONNECTOR = "eurostat_gas_exports_monthly"
SOURCE = "eurostat:nrg_te_gasm"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_te_gasm/default/table"
URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_gasm?format=JSON&lang=EN"
       "&unit=TJ_GCV&sinceTimePeriod=2016-01")
SAVED = "nrg_te_gasm_tj.json"
TJ_TO_MWH = 1_000_000 / 3_600
PRODUCTS = {"G3000": "Natural gas", "G3200": "LNG"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_partner", "x_partner_name", "x_flag"]


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
    if js.get("id") != ["freq", "siec", "partner", "unit", "geo", "time"]:
        raise RuntimeError(f"the dimensions are not the six expected: {js.get('id')}")
    dims = {d: js["dimension"][d]["category"] for d in js["id"]}
    for d, want in (("freq", ["M"]), ("unit", ["TJ_GCV"])):
        if list(dims[d]["index"]) != want:
            raise RuntimeError(f"{d} is {list(dims[d]['index'])}, not {want}")
    if not set(dims["siec"]["index"]) <= set(PRODUCTS):
        raise RuntimeError(f"a product not expected: {set(dims['siec']['index']) - set(PRODUCTS)}")
    order = [sorted(dims[d]["index"], key=dims[d]["index"].get) for d in js["id"]]
    sizes = js["size"]
    status = js.get("status", {})
    partners = dims["partner"].get("label", {})
    left = sorted(set(dims["geo"]["index"]) - erc.KEPT)
    rows = []
    for key, v in js["value"].items():
        k = int(key)
        idx = []
        for s in reversed(sizes):
            idx.append(k % s)
            k //= s
        idx.reverse()
        code = {d: order[i][idx[i]] for i, d in enumerate(js["id"])}
        geo = code["geo"]
        if geo not in erc.KEPT:
            continue
        if not re.fullmatch(r"\d{4}-\d\d", code["time"]):
            raise RuntimeError(f"a period not a month: {code['time']!r}")
        if not isinstance(v, (int, float)):
            raise RuntimeError(f"a value that is not a number: {v!r}")
        p, s = code["partner"], code["siec"]
        rows.append((f"eurostat_gas_exports:{geo}:{s}:{p}", f"{code['time']}-01T00:00:00Z", round(float(v) * TJ_TO_MWH, 3),
                     "" if geo in erc.AGGREGATES else erc.ISO.get(geo, geo), f"{PRODUCTS[s]} exports to {partners.get(p, p)}",
                     geo, s, p, partners.get(p, p), status.get(key, "")))
    t = pd.DataFrame(rows, columns=["entity", "ts_utc", "value", "geo", "node", "x_geo_code", "x_siec", "x_partner", "x_partner_name", "x_flag"])
    t = t.assign(variable="exports", unit="MWh", freq="P1M", market="", source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage="")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t[COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True), left


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_te_gasm: natural gas and LNG exports by partner, European countries, a month")
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
        t, left = build(js, retrieved)
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        aggs = sorted(p for p in t.x_partner.unique() if len(p) > 2)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, natural gas exports - monthly data (nrg_te_gasm), natural gas and LNG by partner, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}, {len(countries)} European countries and the EU aggregates (session 2469)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_gas_exports:<Eurostat geo code>:<SIEC>:<partner code> (G3000 natural gas, G3200 LNG, a part of it: never add the two); variable exports; unit MWh (Eurostat's TJ of gross calorific value times 277.7778, as eurostat_gas_imports_monthly); "
            "ts_utc the month's first day; freq P1M; geo the exporting country's ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020 and EA21; node the product and the partner's name; x_ columns Eurostat's codes and the observation's status.",
            f"{len(t)} rows, {t.x_partner.nunique()} partners. Exporting countries left out by Eurostat's terms: {' '.join(left) or 'none'}. Every partner is kept, Eurostat's aggregates among them ({', '.join(aggs)}): TOTAL is every partner and NSP not specified; TOTAL and every group "
            "whose code does not end in _OTH overlap the named countries, so a sum over partners double counts unless they are left out. The partner code NA is Namibia: a reader that turns \"NA\" into a missing value (pandas by default) loses it. Values as published, zeros kept; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_gas_exports.py; the answer retrieved {retrieved}; Eurostat's update {js.get('updated', '')}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (not in git)",
            f"Source: {SOURCE} Eurostat, Natural gas exports - monthly data (nrg_te_gasm), terajoules of gross calorific value, {PAGE}",
            f"  access: {URL} (answered asynchronously: the same address asked again until the data come)",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_te_gasm. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the terajoules written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Natural gas exports - monthly data (nrg_te_gasm), natural gas and LNG by partner",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(countries)} countries, {t.x_partner.nunique()} partners; left out {left}")
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
