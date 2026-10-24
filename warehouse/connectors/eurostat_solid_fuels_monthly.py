#!/usr/bin/env python3
"""Eurostat's monthly solid fuels supply (nrg_cb_sffm): each European country's hard coal, brown coal, coke oven coke,
peat and oil shale, every flow of the monthly balance, a month from January 2016 (session 2364, chain 110: a second source
of the session's own choosing, beside session 2363's monthly oil).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_solid_fuels_monthly.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), answered at once:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_sffm?format=SDMX-CSV&compressed=false&startPeriod=2016-01

    entity      eurostat_sff:<Eurostat geo code>:<SIEC code> (C0100 hard coal, C0200 brown coal, C0311 coke oven coke,
                P1100 peat, S2000 oil shale and oil sands); node the fuel and flow's English names
    variable    flow:<NRG_BAL code>, every flow the file gives a fuel (production IPRD, imports IMP and from outside the
                EU IMP_FROM_NEU, exports EXP, stocks and their change, gross inland deliveries, power plants' and coke
                ovens' intake TI_EHG_MAP and TI_CO, industry's and others' final consumption, as Eurostat codes them; each as
                published, no sum made here)
    unit        t (metric tons: Eurostat's thousand tonnes, THS_T, times 1,000, Decision 56); ts_utc the month's first day;
                freq P1M
    geo         the country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregate EU27_2020
    x_*         Eurostat's geo code, SIEC code and NRG_BAL code, the observation's flag and confidentiality status

Countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice); the United Kingdom and Kosovo
are left out and named in the header. Values as published; a blank value has no row; nothing is filled. A header not
Eurostat's, a unit other than THS_T, a frequency not monthly, a fuel or flow not among those named, a value that is not a
number or a key given twice stops the run.

    python warehouse/connectors/eurostat_solid_fuels_monthly.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_solid_fuels_monthly/ with --offline. ec.europa.eu's robots file
disallows the old /eurostat/SDMX/diss-web/rest/ and the search pages, not /eurostat/api/dissemination/, and names no AI
agent (session 2364). License: Eurostat's copyright notice (session 2123): reuse "for commercial or non-commercial purposes
is authorised provided the source is acknowledged"; source: Eurostat.
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import eurostat_res_capacity as erc  # noqa: E402  the same publisher's countries (KEPT, AGGREGATES, ISO) and terms

NAME = "eurostat_solid_fuels_monthly"
CONNECTOR = "eurostat_solid_fuels_monthly"
SOURCE = "eurostat:nrg_cb_sffm"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_sffm/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_sffm?format=SDMX-CSV&compressed=false&startPeriod=2016-01"
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
PRODUCTS = {"C0100": "Hard coal", "C0200": "Brown coal", "C0311": "Coke oven coke", "P1100": "Peat", "S2000": "Oil shale and oil sands"}
FLOWS = {  # Eurostat's NRG_BAL codelist, English (session 2364)
    "EXP": "Exports", "FC_IND": "Final consumption - industry sector", "FC_IND_IS": "Final consumption - industry sector - iron and steel",
    "FC_OTH": "Final consumption - other sectors", "GID_CAL": "Gross inland deliveries - calculated",
    "GID_OBS": "Gross inland deliveries - observed", "IMP": "Imports", "IMP_FROM_NEU": "Imports from outside EU",
    "IPRD": "Indigenous production", "RCV_RCY": "Recovered and recycled products", "STATDIFF": "Statistical differences",
    "STKCL_NAT": "Closing stocks on national territory", "STKOP_NAT": "Opening stocks on national territory",
    "STK_CHG": "Change in stock", "TI_CO": "Transformation input - coke ovens",
    "TI_EHG_MAP": "Transformation input - electricity and heat generation - main activity producers"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_nrg_bal", "x_flag", "x_conf_status"]


def build(text, retrieved, vintage):
    t = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t.columns)}")
    bad = (sorted(set(t.unit) - {"THS_T"}) + sorted(set(t.freq) - {"M"}) + sorted(set(t.nrg_bal) - set(FLOWS))
           + sorted(set(t.siec) - set(PRODUCTS)))
    if bad:
        raise RuntimeError(f"a unit, frequency, flow or fuel not expected: {bad}")
    left = sorted(set(t.geo) - erc.KEPT)
    t = t[t.geo.isin(erc.KEPT) & (t.OBS_VALUE.str.strip() != "")]
    bad = t[~t.TIME_PERIOD.str.fullmatch(r"\d{4}-\d\d")]
    if len(bad):
        raise RuntimeError(f"a period not a month: {bad.TIME_PERIOD.iloc[0]!r}")
    try:
        value = t.OBS_VALUE.astype(float) * 1000.0
    except ValueError as e:
        raise RuntimeError(f"a value that is not a number: {e}")
    geo = t.geo
    out = pd.DataFrame({
        "entity": "eurostat_sff:" + geo + ":" + t.siec, "variable": "flow:" + t.nrg_bal, "ts_utc": t.TIME_PERIOD + "-01T00:00:00Z",
        "value": value.round(3), "unit": "t", "freq": "P1M", "geo": geo.map(lambda g: "" if g in erc.AGGREGATES else erc.ISO.get(g, g)),
        "market": "", "node": t.siec.map(PRODUCTS) + ": " + t.nrg_bal.map(FLOWS), "source": SOURCE, "source_url": URL,
        "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": geo, "x_siec": t.siec, "x_nrg_bal": t.nrg_bal,
        "x_flag": t.OBS_FLAG.str.strip(), "x_conf_status": t.CONF_STATUS.str.strip()})
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), left, sorted(set(t["LAST UPDATE"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_sffm: monthly solid fuels supply, European countries")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=erc.UA, timeout=300)
        text = content.decode("utf-8", errors="replace")
        t, left, updated = build(text, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, monthly solid fuels supply (nrg_cb_sffm), {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}, {len(countries)} European countries and the EU (session 2364)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_sff:<Eurostat geo code>:<SIEC code> (C0100 hard coal, C0200 brown coal, C0311 coke oven coke, P1100 peat, "
            "S2000 oil shale and oil sands); variable flow:<NRG_BAL code>; unit t (Eurostat's thousand tonnes times 1,000); ts_utc the month's first day; freq P1M; geo ISO "
            "alpha-2 (Eurostat's EL is GR), blank for EU27_2020; node the fuel and flow.",
            f"{len(t)} rows. Countries: {' '.join(countries)}. Left out by Eurostat's terms (data for countries outside the EU, EFTA and the official candidates may not be reused commercially): "
            f"{' '.join(left) or 'none'}. Flows overlap (observed and calculated deliveries are two readings; industry holds iron and steel; imports hold those from outside the EU): "
            "a sum of rows double counts. Stock change is positive when coal is taken out of stock (opening less closing stocks), the "
            "opposite of the oil table's. EU27_2020 is Eurostat's sum of the members that report a cell (Malta and, for brown coal, "
            "Greece have no row in some months; session 2366). Values as published; a blank value has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_solid_fuels_monthly.py; the data retrieved {rec.get('retrieved_at') or ''}; Eurostat's last update {', '.join(updated)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Supply and transformation of solid fuels - monthly data (nrg_cb_sffm), {PAGE}",
            f"  access: {URL}",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_cb_sffm. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the values unchanged but for the thousand tonnes written as tonnes).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Supply and transformation of solid fuels - monthly data (nrg_cb_sffm)",
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
