#!/usr/bin/env python3
"""Eurostat's monthly supply, transformation and consumption of natural gas (nrg_cb_gasm): each European country's gas
production, imports, exports, stock changes, inland consumption and its uses, in energy, from 2015 (session 2329,
chain 108: Europe's gas demand, which the United States' LNG serves; a source of the session's own choosing, beside
eurostat_gas_imports_monthly).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_gas_balance_monthly.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 9 MB of SDMX-CSV):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01

    entity      eurostat_gas_balance:<Eurostat geo code> (SIEC G3000, natural gas, the data set's only product)
    variable    the balance item (Eurostat's NRG_BAL code and name):
                indigenous_production (IPRD), imports (IMP), exports (EXP), stock_change (STK_CHG_MG, stock changes as
                defined in MOS GAS), stock_change_cushion_gas (STK_CHG_CG), transfer_from_other_sources (TOS),
                inland_consumption_calculated (IC_CAL_MG, as defined in MOS GAS), inland_consumption_observed (IC_OBS),
                transformation_input_electricity_heat_main (TI_EHG_MAP, electricity and heat generation, main activity
                producers), final_consumption_industry (FC_IND), final_consumption_other (FC_OTH), distribution_losses
                (DL), international_maritime_bunkers (INTMARB), flared (FLARE), vented (VENT), statistical_differences
                (STATDIFF)
    unit        MWh: Eurostat's terajoules of gross calorific value (TJ_GCV) times 277.7778 (1 TJ = 1,000,000 MJ and
                1 MWh = 3,600 MJ, an exact definition); the file's million cubic metres (MIO_M3) are not taken
    ts_utc      the month's first day at 00:00:00Z; freq P1M; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank
                for Eurostat's aggregates EU27_2020 and EA21 (the file holds no EA20)
    x_*         Eurostat's geo and balance codes, the observation's flag (p provisional, e estimated, m, n) and
                confidentiality status (a cell marked C is blank in the file and so has no row: the column is empty in
                October 2026's file)

Countries kept: the EU's members, EFTA's and the official candidates, with the aggregates EU27_2020, EA21 and EA20, as
eurostat_gas_imports_monthly keeps them under Eurostat's terms (the United Kingdom and Kosovo left out); the file of
October 2026 has 38 such areas, Norway the only EFTA member among them, and no EA20 (session 2331's note). Eurostat's
LAST UPDATE column (its release, without a time zone) is named in the header; vintage stays blank. Zeros are
kept, as Eurostat prints them: in a balance a zero says an item is nil, and the header counts them. A blank has no row;
nothing is filled. Signs are Eurostat's: a stock change is positive when gas goes into storage (the EU's is positive
from April to October 2024 and negative in winter), so inland consumption calculated is production plus imports minus
exports minus the stock change (session 2329's check; transfers from other sources added where given). A
header not Eurostat's, a product, unit, frequency or balance item not expected, a value that is not a number or a key
given twice stops the run.

    python warehouse/connectors/eurostat_gas_balance.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_gas_balance/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2329). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source acknowledged;
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

NAME = "eurostat_gas_balance_monthly"
CONNECTOR = "eurostat_gas_balance"
SOURCE = "eurostat:nrg_cb_gasm"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_gasm/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
ITEMS = {"IPRD": "indigenous_production", "IMP": "imports", "EXP": "exports", "STK_CHG_MG": "stock_change",
         "STK_CHG_CG": "stock_change_cushion_gas", "TOS": "transfer_from_other_sources",
         "IC_CAL_MG": "inland_consumption_calculated", "IC_OBS": "inland_consumption_observed",
         "TI_EHG_MAP": "transformation_input_electricity_heat_main", "FC_IND": "final_consumption_industry",
         "FC_OTH": "final_consumption_other", "DL": "distribution_losses", "INTMARB": "international_maritime_bunkers",
         "FLARE": "flared", "VENT": "vented", "STATDIFF": "statistical_differences"}
TJ_TO_MWH = 1_000_000 / 3_600
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020", "EA21", "EA20"}
AGGREGATES = {"EU27_2020", "EA21", "EA20"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nrg_bal", "x_flag", "x_conf_status"]


def build(content, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"TJ_GCV", "MIO_M3"}) + sorted(set(t0.freq) - {"M"}) + sorted(set(t0.siec) - {"G3000"}) \
        + sorted(set(t0.nrg_bal) - set(ITEMS))
    if bad:
        raise RuntimeError(f"a unit, frequency, product or balance item not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[(t0.unit == "TJ_GCV") & t0.geo.isin(KEPT)].itertuples(index=False):
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
        if not re.fullmatch(r"\d{4}-\d{2}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a month: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_gas_balance:{r.geo}", "variable": ITEMS[r.nrg_bal],
                     "ts_utc": f"{r.TIME_PERIOD}-01T00:00:00Z", "value": round(value * TJ_TO_MWH, 3), "unit": "MWh",
                     "freq": "P1M", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} natural gas {r.nrg_bal}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_nrg_bal": r.nrg_bal,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_gasm: European supply, transformation and consumption of natural gas, a month")
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
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        t, counts = build(content, URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, supply, transformation and consumption of natural gas, monthly (nrg_cb_gasm), {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2329)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_gas_balance:<geo>; variable the balance item (indigenous_production, imports, exports, stock_change, inland_consumption_calculated, "
            "inland_consumption_observed, transformation_input_electricity_heat_main, final_consumption_industry, final_consumption_other, distribution_losses and the rest; x_nrg_bal Eurostat's code); "
            "unit MWh (Eurostat's TJ of gross calorific value times 277.7778); ts_utc the month's first day; freq P1M; geo ISO alpha-2 (EL is GR), blank for the aggregates EU27_2020 and EA21.",
            f"{len(t)} rows, {t.entity.nunique()} areas, {t.variable.nunique()} items. Zeros are kept as Eurostat prints them ({counts['zero']:,}); {counts['blank']:,} blanks have no row. "
            f"Areas left out by Eurostat's terms: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}. "
            "A cell Eurostat marks confidential (C) is blank and has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_gas_balance.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Supply, transformation and consumption of gas, monthly data (nrg_cb_gasm), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_gasm. Eurostat bears no responsibility for this reshaping (TJ written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Supply, transformation and consumption of gas, monthly data (nrg_cb_gasm)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros kept {counts['zero']:,}, blanks {counts['blank']:,}")
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
