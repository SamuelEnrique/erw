#!/usr/bin/env python3
"""Eurostat's monthly oil supply (nrg_cb_oilm): each European country's crude oil and main oil products, every flow of
the monthly balance, a month from January 2016 (session 2363, chain 110: a source of the session's own choosing, Europe's
oil month by month beside the ERW's EIA petroleum tables; Eurostat's monthly gas balance is chain 108's).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_oil_monthly.csv, from Eurostat's
SDMX 2.1 dissemination API (no key). The extract is too large to be answered at once: Eurostat queues it and answers with
a job key, whose status and then data are asked by GET from its asynchronous API:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_oilm?format=SDMX-CSV&compressed=false&startPeriod=2016-01
    https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/<key>      until AVAILABLE
    https://ec.europa.eu/eurostat/api/dissemination/1.0/async/data/<key>        the SDMX-CSV file (about 156 MB)

    entity      eurostat_oil:<Eurostat geo code>:<SIEC code>, seven products of the file's 33: O4100_TOT crude oil, O4600
                oil products (all), O4652XR5210B motor gasoline, O4671XR5220B gas oil and diesel oil, O4661XR5230B
                kerosene-type jet fuel (each without its biofuel portion), O4680 fuel oil, O4630 liquefied petroleum
                gases; node the product and flow's English names
    variable    flow:<NRG_BAL code>, every flow the file gives a product (imports IMP, exports EXP, indigenous production
                IPRD, refinery intake RI_OBS, refinery output TO_RPI_RO, gross inland deliveries GID_OBS and GID_CAL,
                stock change STK_CHG, international maritime bunkers INTMARB and aviation INTAVI_E, road transport
                FC_TRA_ROAD_E and the rest, as Eurostat codes them; each as published, no sum made here)
    unit        t (metric tons: Eurostat's thousand tonnes, THS_T, times 1,000, Decision 56); ts_utc the month's first day;
                freq P1M
    geo         the country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregate EU27_2020
    x_*         Eurostat's geo code, SIEC code and NRG_BAL code, the observation's flag and confidentiality status

Countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice: the EU, EFTA, the official
candidates and Eurostat's aggregates); the United Kingdom is left out and named in the header. Values as published; a
blank value has no row; nothing is filled. A header not Eurostat's, a unit other than THS_T, a frequency not monthly, a
flow not among the 26 named, a value that is not a number or a key given twice stops the run.

    python warehouse/connectors/eurostat_oil_monthly.py [--offline] [--out-dir DIR]

Ceiling: one query, its status asked at most 20 times (a minute apart) and its data once; reused with --offline from
warehouse/raw/eurostat_oil_monthly/nrg_cb_oilm_async.bin. ec.europa.eu's robots file disallows the old
/eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2363). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes is
authorised provided the source is acknowledged"; source: Eurostat.
"""

import argparse
import datetime as dt
import io
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

NAME = "eurostat_oil_monthly"
CONNECTOR = "eurostat_oil_monthly"
SOURCE = "eurostat:nrg_cb_oilm"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_oilm/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_oilm?format=SDMX-CSV&compressed=false&startPeriod=2016-01"
ASYNC = "https://ec.europa.eu/eurostat/api/dissemination/1.0/async/"
SAVED = "nrg_cb_oilm_async.bin"
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
PRODUCTS = {"O4100_TOT": "Crude oil", "O4600": "Oil products", "O4652XR5210B": "Motor gasoline (excluding biofuel portion)",
            "O4671XR5220B": "Gas oil and diesel oil (excluding biofuel portion)",
            "O4661XR5230B": "Kerosene-type jet fuel (excluding biofuel portion)", "O4680": "Fuel oil",
            "O4630": "Liquefied petroleum gases"}
FLOWS = {  # Eurostat's NRG_BAL codelist, English (session 2363)
    "BKFLOW": "Backflows", "DU": "Direct use", "EXP": "Exports",
    "FC_TRA_RAIL_DNAVI_E": "Final consumption - transport sector - rail and domestic navigation - energy use",
    "FC_TRA_ROAD_E": "Final consumption - transport sector - road - energy use", "GD_PI": "Gross deliveries to petrochemical industry",
    "GID_CAL": "Gross inland deliveries - calculated", "GID_OBS": "Gross inland deliveries - observed", "IMP": "Imports",
    "INTAVI_E": "International aviation - energy use", "INTMARB": "International maritime bunkers", "IPRD": "Indigenous production",
    "IT": "Interproduct transfers", "ND_TP": "Net deliveries of total products", "PPR": "Primary product receipts",
    "PT": "Products transferred", "RCV_RCY": "Recovered and recycled products", "RF": "Refinery fuel",
    "RI_CAL": "Refinery intake - calculated", "RI_OBS": "Refinery intake - observed", "RL": "Refinery losses",
    "STATDIFF": "Statistical differences", "STK_CHG": "Change in stock", "TI_EHG_MAP": "Transformation input - electricity and heat generation - main activity producers",
    "TOS": "Transfer from other sources", "TO_RPI_RO": "Transformation output - refineries and petrochemical industry - refinery output"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_nrg_bal", "x_flag", "x_conf_status"]


def fetch(log):
    """The extract by Eurostat's asynchronous route: the query, its status until AVAILABLE, its data."""
    r = requests.get(URL, headers=erc.UA, timeout=300)
    r.raise_for_status()
    if r.content.startswith(b"DATAFLOW"):
        return r.content
    key = re.findall(r"<id>([0-9a-f-]{36})</id>", r.text)
    if not key:
        raise RuntimeError(f"the query answered neither data nor a job key: {r.text[:200]!r}")
    key = key[0]
    log(f"  queued as {key}")
    for _ in range(20):
        time.sleep(60)
        s = requests.get(ASYNC + "status/" + key, headers=erc.UA, timeout=60)
        st = re.findall(r"<ns1:status>([A-Z_]+)</ns1:status>", s.text)
        log(f"  status {st}")
        if "AVAILABLE" in st:
            d = requests.get(ASYNC + "data/" + key, headers=erc.UA, timeout=900)
            d.raise_for_status()
            return d.content
    raise RuntimeError(f"job {key} not available after 20 minutes")


def build(text, retrieved):
    t = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t.columns)}")
    bad = sorted(set(t.unit) - {"THS_T"}) + sorted(set(t.freq) - {"M"}) + sorted(set(t.nrg_bal) - set(FLOWS))
    if bad:
        raise RuntimeError(f"a unit, frequency or flow not expected: {bad}")
    left = sorted(set(t.geo) - erc.KEPT)
    t = t[t.geo.isin(erc.KEPT) & t.siec.isin(PRODUCTS) & (t.OBS_VALUE.str.strip() != "")]
    bad = t[~t.TIME_PERIOD.str.fullmatch(r"\d{4}-\d\d")]
    if len(bad):
        raise RuntimeError(f"a period not a month: {bad.TIME_PERIOD.iloc[0]!r}")
    try:
        value = t.OBS_VALUE.astype(float) * 1000.0
    except ValueError as e:
        raise RuntimeError(f"a value that is not a number: {e}")
    geo = t.geo
    out = pd.DataFrame({
        "entity": "eurostat_oil:" + geo + ":" + t.siec, "variable": "flow:" + t.nrg_bal, "ts_utc": t.TIME_PERIOD + "-01T00:00:00Z",
        "value": value.round(3), "unit": "t", "freq": "P1M", "geo": geo.map(lambda g: "" if g in erc.AGGREGATES else erc.ISO.get(g, g)),
        "market": "", "node": t.siec.map(PRODUCTS) + ": " + t.nrg_bal.map(FLOWS), "source": SOURCE, "source_url": URL,
        "retrieved_at": retrieved, "vintage": "", "x_geo_code": geo, "x_siec": t.siec, "x_nrg_bal": t.nrg_bal,
        "x_flag": t.OBS_FLAG.str.strip(), "x_conf_status": t.CONF_STATUS.str.strip()})
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), left, sorted(set(t["LAST UPDATE"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_oilm: monthly oil supply, seven products, European countries")
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
                raise RuntimeError(f"offline: no saved extract at {path}")
            content = open(path, "rb").read()
            retrieved = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log(f"  saved extract reused: {path} ({len(content):,} bytes, saved {retrieved})")
        else:
            content = fetch(log)
            retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(content)
            log(f"  extract saved: {path} ({len(content):,} bytes)")
        text = content.decode("utf-8", errors="replace")
        t, left, updated = build(text, retrieved)  # Eurostat's LAST UPDATE (dd/mm/yy, its clock unstated) in the header, not vintage
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, monthly oil supply (nrg_cb_oilm), seven products, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}, {len(countries)} European countries and the EU (session 2363)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_oil:<Eurostat geo code>:<SIEC code> (O4100_TOT crude oil, O4600 oil products, O4652XR5210B motor gasoline, "
            "O4671XR5220B gas oil and diesel oil, O4661XR5230B kerosene-type jet fuel, each without its biofuel portion, O4680 fuel oil, O4630 LPG); variable flow:<NRG_BAL code>; "
            "unit t (Eurostat's thousand tonnes times 1,000); ts_utc the month's first day; freq P1M; geo ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020; node the product and flow.",
            f"{len(t)} rows. Countries: {' '.join(countries)}. Left out by Eurostat's terms (data for countries outside the EU, EFTA and the official candidates may not be reused commercially): "
            f"{' '.join(left) or 'none'}. The file's other 26 products (their parts and biofuel shares) are not taken. Products and flows overlap (O4600 holds the others; observed and "
            "calculated deliveries are two readings): a sum of rows double counts. Values as published; a blank value has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_oil_monthly.py; the extract retrieved {retrieved}; Eurostat's last update {', '.join(updated)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (not in git)",
            f"Source: {SOURCE} Eurostat, Supply and transformation of oil and petroleum products - monthly data (nrg_cb_oilm), {PAGE}",
            f"  access: {URL} (queued by Eurostat; its status and data by GET from {ASYNC})",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_cb_oilm. Eurostat bears no responsibility for this reshaping (the rows filtered by country and product and renamed, the values unchanged but for the thousand tonnes written as tonnes).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Supply and transformation of oil and petroleum products - monthly data (nrg_cb_oilm)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(countries)} countries; left out {left}")
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
