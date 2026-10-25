#!/usr/bin/env python3
"""Eurostat's electricity production capacities by main fuel groups and operator (nrg_inf_epc): each European country's
net maximum electrical capacity, with the capacity commissioned and decommissioned in the year, by fuel group, for main
activity producers, autoproducers and both, a year from 1990 (session 2356, chain 105: Europe's whole capacity, fossil and
nuclear included, beside the renewables and wastes of eurostat_renewable_capacity_annual).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_capacity_annual.csv,
from Eurostat's SDMX 2.1 dissemination API (no key), as sessions 2123 and 2225 took nrg_inf_epcrw and nrg_cb_pem:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epc?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC         the fuels' English names

    entity      eurostat_epc:<Eurostat geo code>:<SIEC code> (TOTAL, CF combustible fuels and its groups, C0000 coal, G3000
                natural gas, O4000 oil, N9000 "nuclear fuels and other fuels n.e.c." (in effect nuclear: in 2024 above zero only in
                the members with nuclear plants), RA100 hydro and its kinds, RA300 wind, RA420 solar photovoltaic,
                R5000_W6000 biofuels and waste, HYD hydrogen and the rest, as node names them; each as published, no sum
                made here)
    variable    net_capacity, net_capacity_commissioned or net_capacity_decommissioned (Eurostat's CAP_NET_ELC,
                CAP_NET_ELC_C and CAP_NET_ELC_DCM), each _total, _main_producers or _autoproducers (operator TOTAL,
                PRR_MAIN, PRR_AUTO)
    unit        MW; ts_utc the year's 1 January; freq P1Y
    geo         the country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregates EU27_2020 and
                EA21, Eurostat's own totals, never a sum made here
    node        the SIEC code's English name
    x_*         Eurostat's geo code, SIEC code, plant technology and operator codes, the observation's flag and
                confidentiality status

Countries kept as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice: the EU, EFTA, the official
candidates and Eurostat's aggregates); Kosovo (XK), a potential candidate, is left out and named in the header. Values
as published, zeros kept; a blank value has no row; nothing is filled. A header not Eurostat's, a unit not MW, a frequency
not annual, a plant technology or operator not one of the three, a value that is not a number or a key given twice stops
the run.

    python warehouse/connectors/eurostat_capacity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the data and the codelist), reused from warehouse/raw/eurostat_capacity/ with --offline.
ec.europa.eu's robots file disallows the old /eurostat/SDMX/diss-web/rest/ and the search pages, not
/eurostat/api/dissemination/, and names no AI agent (session 2356). License: Eurostat's copyright notice (session 2123):
reuse "for commercial or non-commercial purposes is authorised provided the source is acknowledged"; source: Eurostat.
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
import eurostat_res_capacity as erc  # noqa: E402  the same publisher's countries (KEPT, AGGREGATES, ISO) and names()

NAME = "eurostat_electricity_capacity_annual"
CONNECTOR = "eurostat_capacity"
SOURCE = "eurostat:nrg_inf_epc"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_epc/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epc?format=SDMX-CSV&compressed=false"
CODELIST = erc.CODELIST
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "siec", "plant_tec", "operator", "unit", "geo", "TIME_PERIOD", "OBS_VALUE",
          "OBS_FLAG", "CONF_STATUS"]
TECS = {"CAP_NET_ELC": "net_capacity", "CAP_NET_ELC_C": "net_capacity_commissioned", "CAP_NET_ELC_DCM": "net_capacity_decommissioned"}
OPERATORS = {"TOTAL": "total", "PRR_MAIN": "main_producers", "PRR_AUTO": "autoproducers"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_plant_tec", "x_operator", "x_flag", "x_conf_status"]


def build(csv_text, siec_names, url, retrieved, vintage):
    t = pd.read_csv(io.StringIO(csv_text), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t.columns)}")
    bad = (sorted(set(t.unit) - {"MW"}) + sorted(set(t.freq) - {"A"}) + sorted(set(t.plant_tec) - set(TECS))
           + sorted(set(t.operator) - set(OPERATORS)))
    if bad:
        raise RuntimeError(f"a unit, frequency, plant technology or operator not expected: {bad}")
    left = sorted(set(t.geo) - erc.KEPT)
    t = t[t.geo.isin(erc.KEPT)]
    rows = []
    for r in t.to_dict("records"):
        v = r["OBS_VALUE"].strip()
        if v == "":
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r['geo']} {r['siec']} {r['TIME_PERIOD']}: not a number: {v!r}")
        if not re.fullmatch(r"\d{4}", r["TIME_PERIOD"]):
            raise RuntimeError(f"a period not a year: {r['TIME_PERIOD']!r}")
        geo = r["geo"]
        rows.append({"entity": f"eurostat_epc:{geo}:{r['siec']}", "variable": f"{TECS[r['plant_tec']]}_{OPERATORS[r['operator']]}",
                     "ts_utc": f"{r['TIME_PERIOD']}-01-01T00:00:00Z", "value": value, "unit": "MW", "freq": "P1Y",
                     "geo": "" if geo in erc.AGGREGATES else erc.ISO.get(geo, geo), "market": "",
                     "node": siec_names.get(r["siec"], r["siec"]), "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": geo, "x_siec": r["siec"],
                     "x_plant_tec": r["plant_tec"], "x_operator": r["operator"], "x_flag": r["OBS_FLAG"].strip(),
                     "x_conf_status": r["CONF_STATUS"].strip()})
    out = pd.DataFrame(rows, columns=COLS)
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), left


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_inf_epc: electricity capacity by fuel group and operator, European countries")
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
        codes, _ = ip.fetch_raw(CONNECTOR, CODELIST, log, offline=args.offline, headers=erc.UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=erc.UA, timeout=300)
        text = content.decode("utf-8", errors="replace")
        updated = sorted(set(re.findall(r"^[^,]*,([^,]*),", text, re.M)) - {"LAST UPDATE"})
        t, left = build(text, erc.names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, electricity production capacities by main fuel groups and operator (nrg_inf_epc), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}, {len(countries)} European countries and the EU aggregates (session 2356)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_epc:<Eurostat geo code>:<SIEC code>; variable net_capacity, net_capacity_commissioned or net_capacity_decommissioned, "
            "each _total, _main_producers or _autoproducers; unit MW; ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (Eurostat's EL is GR), blank for Eurostat's own aggregates "
            "EU27_2020 and EA21; node the SIEC code's English name.",
            f"{len(t)} rows. Countries: {' '.join(countries)}. Left out by Eurostat's terms (data for countries outside the EU, EFTA and the official candidates may not be reused commercially): "
            f"{' '.join(left) or 'none'}. Fuel groups overlap (TOTAL, CF and its groups, RA100 and its kinds): a sum of rows double counts. "
            "Commissioned and decommissioned capacity is given for 23 of the 27 fuel codes (not TOTAL, RA100, RA300 or RA420) and in most "
            "countries only from 2020 to 2022. EU27_2020 and EA21 are the reporting members' sum where a member has no row. Germany's 2021 "
            "total is 60,036 MW short of its parts (exactly its solar photovoltaic), as published, and so are the EU's and the euro area's "
            "2021 totals (session 2366). Values as published, zeros kept; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_capacity.py; the data retrieved {rec.get('retrieved_at') or ''}; Eurostat's last update {', '.join(updated)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Electricity production capacities by main fuel groups and operator (nrg_inf_epc), {PAGE}",
            f"  access: {URL}",
            f"  names: {CODELIST}",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_inf_epc. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the values unchanged).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Electricity production capacities by main fuel groups and operator (nrg_inf_epc)",
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
