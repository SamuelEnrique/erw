#!/usr/bin/env python3
"""Eurostat's annual imports of hard coal by partner country (nrg_ti_sff, hard coal only): how much hard coal each
European country imported from each country of origin, a year from 2010 (session 2426, chain 115: a source of the
session's own choosing, beside the crude oil imports by partner of session 2369; it shows, among the rest, U.S. coal
going to Europe). Eurostat publishes solid fuel imports by partner only a year: there is no monthly data set (its table
of contents, read in session 2426, lists nrg_ti_sff and nrg_te_sff, annual, and no monthly one).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_hard_coal_imports_annual.csv, from
Eurostat's statistics API (no key), filtered to hard coal, as JSON-stat 2.0, one request (answered at once in session
2426; an asynchronous answer is asked again, as the crude oil connector does):

    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_sff?format=JSON&lang=EN&siec=C0100&sinceTimePeriod=2010

    entity      eurostat_coal_imp:<Eurostat geo code>:<partner code> (the importing country, then the country of origin or
                Eurostat's partner aggregate as Eurostat codes it: TOTAL, NSP (not specified) and six regional "other" groups; the header lists them); node "Hard
                coal imports from <partner's English name>"
    variable    imports
    unit        t (metric tons: Eurostat's thousand tonnes, THS_T, times 1,000, Decision 56); ts_utc the year's 1 January;
                freq P1Y
    geo         the importing country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregates
                EU27_2020 and EA21
    x_*         Eurostat's geo and partner codes, the partner's English name, the observation's flag (JSON-stat status)

Hard coal is Eurostat's SIEC C0100: anthracite, coking coal, other bituminous coal and sub-bituminous coal. Importing
countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice); those left out are named in the
header. Every partner is kept, Eurostat's aggregates among them (a sum over partners double counts). Values as published,
zeros kept; a cell with no value has no row; nothing is filled. A dataset not hard coal in thousand tonnes, annual, or a
value not a number stops the run.

    python warehouse/connectors/eurostat_coal_imports.py [--offline] [--out-dir DIR]

Ceiling: the address asked at most 10 times (a minute apart) until it answers with the data; reused with --offline from
warehouse/raw/eurostat_hard_coal_imports_annual/nrg_ti_sff_c0100.json. ec.europa.eu's robots file disallows the old
/eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2426). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes is
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

NAME = "eurostat_hard_coal_imports_annual"
CONNECTOR = "eurostat_hard_coal_imports_annual"
SOURCE = "eurostat:nrg_ti_sff_c0100"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_sff/default/table"
URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_sff?format=JSON&lang=EN"
       "&siec=C0100&sinceTimePeriod=2010")
SAVED = "nrg_ti_sff_c0100.json"
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_partner", "x_partner_name", "x_flag"]


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
    for d, want in (("freq", ["A"]), ("siec", ["C0100"]), ("unit", ["THS_T"])):
        if list(dims[d]["index"]) != want:
            raise RuntimeError(f"{d} is {list(dims[d]['index'])}, not {want}")
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
        if not re.fullmatch(r"\d{4}", code["time"]):
            raise RuntimeError(f"a period not a year: {code['time']!r}")
        if not isinstance(v, (int, float)):
            raise RuntimeError(f"a value that is not a number: {v!r}")
        p = code["partner"]
        rows.append((f"eurostat_coal_imp:{geo}:{p}", f"{code['time']}-01-01T00:00:00Z", round(float(v) * 1000.0, 3),
                     "" if geo in erc.AGGREGATES else erc.ISO.get(geo, geo), f"Hard coal imports from {partners.get(p, p)}",
                     geo, p, partners.get(p, p), status.get(key, "")))
    t = pd.DataFrame(rows, columns=["entity", "ts_utc", "value", "geo", "node", "x_geo_code", "x_partner", "x_partner_name", "x_flag"])
    t = t.assign(variable="imports", unit="t", freq="P1Y", market="", source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage="")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t[COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True), left


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ti_sff: hard coal imports by partner, European countries, a year")
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
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, solid fossil fuels imports (nrg_ti_sff), hard coal by partner, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}, {len(countries)} European countries and the EU aggregates (session 2426)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_coal_imp:<Eurostat geo code>:<partner code>; variable imports; unit t (Eurostat's thousand tonnes times 1,000); "
            "ts_utc the year's 1 January; freq P1Y; geo the importing country's ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020 and EA21; node the partner's name; "
            "x_partner and x_partner_name Eurostat's partner code and name; x_flag the observation's status. Hard coal is Eurostat's SIEC C0100 (anthracite, coking coal, other bituminous and sub-bituminous coal).",
            f"{len(t)} rows, {t.x_partner.nunique()} partners. Importing countries left out by Eurostat's terms: {' '.join(left) or 'none'}. Every partner is kept, Eurostat's "
            f"aggregates among them ({', '.join(sorted(p for p in t.x_partner.unique() if len(p) > 2))}): TOTAL is every partner and NSP not specified; TOTAL and every group whose code does not end in _OTH overlap the named countries, so a sum over partners double counts unless they are left out. The partner code NA is Namibia: a reader that turns "
            "\"NA\" into a missing value (pandas by default) loses it. Values as published, zeros kept; nothing is filled. Eurostat publishes these imports a year only.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_coal_imports.py; the answer retrieved {retrieved}; Eurostat's update {js.get('updated', '')}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (not in git)",
            f"Source: {SOURCE} Eurostat, Solid fossil fuels imports (nrg_ti_sff), hard coal (C0100), {PAGE}",
            f"  access: {URL}",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_ti_sff. Eurostat bears no responsibility for this reshaping (the rows filtered to hard coal and by country and renamed, the values unchanged but for the thousand tonnes written as tonnes).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Solid fossil fuels imports (nrg_ti_sff), hard coal by partner",
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
