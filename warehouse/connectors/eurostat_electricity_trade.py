#!/usr/bin/env python3
"""Eurostat's annual electricity imports and exports by partner country (nrg_ti_eh and nrg_te_eh, electricity only): how
much electricity each European country bought from and sold to each neighbour, a year from 2010 (session 2432, chain 115:
a third source of the session's own choosing, beside the monthly electricity balance the ERW holds, which gives each
country's imports and exports in total but not by partner). Eurostat publishes the trade by partner a year only.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_trade_annual.csv,
from Eurostat's statistics API (no key), filtered to electricity, as JSON-stat 2.0, two requests (each answered at once in
session 2432; an asynchronous answer is asked again, as the crude oil connector does):

    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010
    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010

    entity      eurostat_elec_trade:<Eurostat geo code>:<partner code> (the reporting country, then its trading partner or
                Eurostat's partner aggregate: TOTAL, the EU, extra-EU and the like); node "Electricity trade with
                <partner's English name>"
    variable    imports (nrg_ti_eh), exports (nrg_te_eh)
    unit        MWh (Eurostat's GWh times 1,000; the same figures in TJ are not taken); ts_utc the year's 1 January; freq P1Y
    geo         the reporting country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for EU27_2020 and EA21
    x_*         Eurostat's geo and partner codes, the partner's English name, the observation's flag (JSON-stat status)

Reporting countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice); those left out are
named in the header. Every partner is kept, Eurostat's aggregates among them (a sum over partners double counts).
Values as published, zeros kept; a cell with no value has no row; nothing is filled. A dataset not electricity, a unit
other than GWH and TJ, a frequency not annual or a value not a number stops the run. One country's imports from a
partner need not equal the partner's exports to it: each is as its own country reports.

    python warehouse/connectors/eurostat_electricity_trade.py [--offline] [--out-dir DIR]

Ceiling: each address asked at most 10 times (a minute apart) until it answers with the data; reused with --offline from
warehouse/raw/eurostat_electricity_trade_annual/. ec.europa.eu's robots file disallows the old
/eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2432). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes is
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

NAME = "eurostat_electricity_trade_annual"
CONNECTOR = "eurostat_electricity_trade_annual"
SOURCE = "eurostat:nrg_ti_eh_nrg_te_eh"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_eh/default/table"
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{}?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010"
FLOWS = {"imports": ("nrg_ti_eh", "nrg_ti_eh_e7000.json"), "exports": ("nrg_te_eh", "nrg_te_eh_e7000.json")}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_partner", "x_partner_name", "x_flag"]


def fetch(url, log):
    for k in range(10):
        r = requests.get(url, headers=erc.UA, timeout=600)
        if r.status_code == 200 and r.content.startswith(b'{"version"'):
            return r.content
        log(f"  try {k + 1}: HTTP {r.status_code} {r.content[:120]!r}")
        if r.status_code not in (200, 413):
            r.raise_for_status()
        time.sleep(60)
    raise RuntimeError("Eurostat did not answer with the data after 10 tries")


def build(js, variable, url, retrieved):
    if js.get("id") != ["freq", "siec", "partner", "unit", "geo", "time"]:
        raise RuntimeError(f"the dimensions are not the six expected: {js.get('id')}")
    dims = {d: js["dimension"][d]["category"] for d in js["id"]}
    if list(dims["freq"]["index"]) != ["A"] or list(dims["siec"]["index"]) != ["E7000"]:
        raise RuntimeError(f"freq {list(dims['freq']['index'])} or siec {list(dims['siec']['index'])} not A and E7000")
    if "GWH" not in dims["unit"]["index"] or not set(dims["unit"]["index"]) <= {"GWH", "TJ"}:
        raise RuntimeError(f"the units are not GWH and TJ: {list(dims['unit']['index'])}")
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
        if code["unit"] != "GWH":
            continue
        geo = code["geo"]
        if geo not in erc.KEPT:
            continue
        if not re.fullmatch(r"\d{4}", code["time"]):
            raise RuntimeError(f"a period not a year: {code['time']!r}")
        if not isinstance(v, (int, float)):
            raise RuntimeError(f"a value that is not a number: {v!r}")
        p = code["partner"]
        rows.append((f"eurostat_elec_trade:{geo}:{p}", variable, f"{code['time']}-01-01T00:00:00Z", round(float(v) * 1000.0, 3),
                     "" if geo in erc.AGGREGATES else erc.ISO.get(geo, geo), f"Electricity trade with {partners.get(p, p)}",
                     geo, p, partners.get(p, p), status.get(key, ""), url))
    t = pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value", "geo", "node", "x_geo_code", "x_partner", "x_partner_name", "x_flag", "source_url"])
    return t.assign(unit="MWh", freq="P1Y", market="", source=SOURCE, retrieved_at=retrieved, vintage=""), left


def finish(parts):
    t = pd.concat(parts, ignore_index=True)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ti_eh and nrg_te_eh: electricity imports and exports by partner, a year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
    try:
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        parts, left, updated, got = [], set(), {}, {}
        for variable, (code, saved) in FLOWS.items():
            url = BASE.format(code)
            path = os.path.join(ip.RAW_DIR, CONNECTOR, saved)
            if args.offline:
                if not os.path.exists(path):
                    raise RuntimeError(f"offline: no saved answer at {path}")
                content = open(path, "rb").read()
                retrieved = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                log(f"  saved answer reused: {path} ({len(content):,} bytes, saved {retrieved})")
            else:
                content = fetch(url, log)
                retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "wb").write(content)
                log(f"  answer saved: {path} ({len(content):,} bytes)")
            js = json.loads(content.decode("utf-8"))
            t, l = build(js, variable, url, retrieved)
            parts.append(t)
            left |= set(l)
            updated[code], got[code] = js.get("updated", ""), retrieved
        t = finish(parts)
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, electricity imports (nrg_ti_eh) and exports (nrg_te_eh) by partner, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}, {len(countries)} European countries and the EU aggregates (session 2432)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_elec_trade:<Eurostat geo code>:<partner code>; variable imports or exports; unit MWh (Eurostat's GWh times 1,000); "
            "ts_utc the year's 1 January; freq P1Y; geo the reporting country's ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020 and EA21; node the partner's name; "
            "x_partner and x_partner_name Eurostat's partner code and name; x_flag the observation's status. Each country's figures are as it reports them: one country's imports from a partner need not equal the partner's exports to it.",
            f"{len(t)} rows, {t.x_partner.nunique()} partners. Reporting countries left out by Eurostat's terms: {' '.join(sorted(left)) or 'none'}. Every partner is kept, Eurostat's "
            "aggregates among them (TOTAL, the EU, extra-EU and the like): a sum over partners double counts. The partner code NA is Namibia: a reader that turns "
            "\"NA\" into a missing value (pandas by default) loses it. Values as published, zeros kept; nothing is filled. Eurostat publishes this trade a year only.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electricity_trade.py; the answers retrieved " + ", ".join(f"{k} {v}" for k, v in got.items())
            + "; Eurostat's update " + ", ".join(f"{k} {v}" for k, v in updated.items()),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Electricity and derived heat imports (nrg_ti_eh) and exports (nrg_te_eh), electricity (E7000), {PAGE}",
            "  access: " + " and ".join(BASE.format(c) for c, _ in FLOWS.values()),
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_ti_eh and nrg_te_eh. Eurostat bears no responsibility for this reshaping (the rows filtered to electricity in GWh and by country and renamed, the values unchanged but for the GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Electricity and derived heat imports (nrg_ti_eh) and exports (nrg_te_eh), electricity by partner",
                                    report_url=PAGE, document_list=BASE.format("nrg_ti_eh"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(countries)} countries, {t.x_partner.nunique()} partners; left out {sorted(left)}")
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
