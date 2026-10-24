#!/usr/bin/env python3
"""Eurostat's annual supply, transformation and consumption of electricity (nrg_cb_e): each European country's gross and
net production, imports, exports, own use, losses and final consumption by sector, a year from 1990 (session 2454, chain
118: a source of the session's own choosing, beside eurostat_electricity_production_annual and the monthly flows of
eurostat_electricity_monthly).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_balance_annual.csv,
from Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (electricity, SIEC E7000, in GWh) and the
NRG_BAL codelist (the balance items' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV

    entity      eurostat_electricity_balance:<Eurostat geo code>
    variable    the balance item's code, lower case (gep gross electricity production, nep net, imp, exp, id
                inland demand, nrg_e energy sector own use and its parts, dl distribution losses, fc final consumption,
                fc_ind_e, fc_tra_e, fc_oth_e and their parts, and so on)
    unit        MWh: Eurostat's GWh times 1,000
    ts_utc      the year's 1 January; freq P1Y; geo the country's ISO alpha-2 (EL is GR), blank for EU27_2020
    node        "<geo code> electricity, <the item's name>"
    x_*         Eurostat's geo and balance codes, the observation's flag (p provisional, e estimated, d, b) and
                confidentiality status

The items overlap (totals hold their parts): a sum takes one level. Signs are Eurostat's (exports are positive). A blank
has no row; zeros are kept; nothing is filled. No sum is made here: the file's identities do not close (other sectors'
total, FC_OTH_E, is in the codelist but has no value, and the parts of final consumption fall short of it, by 9.5 TWh for
Germany in 2023; net production plus imports less exports differs from inland demand in 970 of 1,419 country years).
The run stops if net production is ever above gross production by more than 1 GWh (it never is).
Countries kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as eurostat_gas_balance_monthly
keeps them (the United Kingdom and Kosovo left out). A header not Eurostat's, a unit, frequency, product or item not
expected, a value that is not a number or a key given twice stops the run.

    python warehouse/connectors/eurostat_electricity_balance.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_electricity_balance/ with --offline. ec.europa.eu's robots
file disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2454). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source acknowledged;
source: Eurostat.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eurostat_electricity_balance_annual"
CONNECTOR = "eurostat_electricity_balance"
SOURCE = "eurostat:nrg_cb_e"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_e/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
TOL = 1.0   # GWh
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nrg_bal", "x_flag", "x_conf_status"]


def item_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the NRG_BAL codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if "GEP" not in names or "FC" not in names:
        raise RuntimeError("the NRG_BAL codelist is not Eurostat's")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.siec) - {"E7000"}) \
        + sorted(set(t0.nrg_bal) - set(names))
    if bad:
        raise RuntimeError(f"a unit, frequency, product or balance item not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: not a number: {v!r}")
        if value == 0:
            counts["zero"] += 1
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_electricity_balance:{r.geo}", "variable": r.nrg_bal.lower(),
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": round(value * 1000.0, 3), "unit": "MWh",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} electricity, {names[r.nrg_bal]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_nrg_bal": r.nrg_bal,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def nep_check(t):
    """Net production against gross: the country years compared; stops if net is above gross by more than TOL GWh."""
    p = t.assign(g=t.value / 1000.0).pivot_table(index=["x_geo_code", "ts_utc"], columns="x_nrg_bal", values="g", aggfunc="first")
    d = (p["NEP"] - p["GEP"]).dropna()
    if (d > TOL).any():
        k = d[d > TOL].index[0]
        raise RuntimeError(f"net production above gross by {d[k]:.3f} GWh: {k[0]} {k[1][:4]}")
    return len(d)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_e: European supply, transformation and consumption of electricity, a year")
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
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        codes, _ = ip.fetch_raw(CONNECTOR, CODES_URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=300)
        t, counts = build(content, item_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        compared = nep_check(t)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, supply, transformation and consumption of electricity, annual (nrg_cb_e), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2454)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_electricity_balance:<geo>; variable the NRG_BAL item's code in lower case (gep, nep, imp, exp, id, nrg_e and its parts, dl, fc, fc_ind_e, fc_tra_e, fc_oth_e and their parts); "
            "unit MWh (Eurostat's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; node the item's name; x_nrg_bal Eurostat's code; x_flag p provisional, e estimated. "
            "The items overlap (totals hold their parts): a sum takes one level. Exports are positive, as Eurostat prints them.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.variable.nunique()} items. Zeros are kept ({counts['zero']:,}); {counts['blank']:,} blanks have no row; nothing is filled. "
            f"Net production is never above gross in the {compared:,} country years that give both. No sum is made: the file's identities do not close (FC_OTH_E has no value). "
            f"Areas left out by Eurostat's terms: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electricity_balance.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Supply, transformation and consumption of electricity, annual data (nrg_cb_e), electricity (E7000) in GWh, {PAGE}",
            f"  access: {URL} and the items' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_e. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Supply, transformation and consumption of electricity, annual data (nrg_cb_e)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros {counts['zero']:,}, blanks {counts['blank']:,}; net below gross in {compared:,} country years; left out {counts['left_out_geo']}")
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
