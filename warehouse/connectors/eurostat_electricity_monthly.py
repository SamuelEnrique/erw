#!/usr/bin/env python3
"""Eurostat's monthly electricity statistics: each European country's net electricity production by fuel (nrg_cb_pem)
and its electricity flows, imports, exports, the supply available to its internal market and its losses (nrg_cb_em), a
month from January 2016 (session 2225, chain 099: Europe's grids month by month beside the U.S. ones).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_monthly.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), as session 2123 took nrg_inf_epcrw:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_pem?format=SDMX-CSV&compressed=false&startPeriod=2016-01
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_em?format=SDMX-CSV&compressed=false&startPeriod=2016-01
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC      the fuels' English names
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL   the flows' English names

    entity      eurostat_elec:<Eurostat geo code>
    variable    net_production:<SIEC code> (nrg_cb_pem: TOTAL, the combustible fuels CF and their parts, nuclear N9000,
                the renewables RA000 and their parts, and the rest as Eurostat codes them; each as published, no sum made
                here), or flow:<NRG_BAL code> (nrg_cb_em, electricity E7000: IMP, IMP_FROM_EU, EXP, EXP_TO_EU, AIM the
                supply available for the internal market, DL distribution losses, TI_EHG_EPS)
    unit        MWh (Eurostat's GWh times 1,000); ts_utc the month's first day; freq P1M
    geo         the country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregate EU27_2020
    node        the SIEC or NRG_BAL code's English name
    x_*         Eurostat's geo code, the data set, the observation's flag and confidentiality status

nrg_cb_pem's rows in percent (unit PC, a fuel's share) are not taken: they are a ratio of the values kept. Countries kept
as in eurostat_res_capacity.py (its KEPT, by Eurostat's copyright notice: the EU, EFTA, the official candidates and
Eurostat's aggregates); the United Kingdom and Kosovo are left out and named in the header. Values as published; a blank
value has no row; nothing is filled. A header not Eurostat's, a unit other than GWh (or PC in nrg_cb_pem), a frequency
not monthly, a balance other than electricity's in nrg_cb_em, a value that is not a number or a key given twice stops the
run.

    python warehouse/connectors/eurostat_electricity_monthly.py [--offline] [--out-dir DIR]

Ceiling: four requests (the two data sets and the two codelists), reused from warehouse/raw/eurostat_cb_em/ with
--offline. ec.europa.eu's robots file disallows the old /eurostat/SDMX/diss-web/rest/ and the search pages, not
/eurostat/api/dissemination/ (sessions 2123 and 2225). License: Eurostat's copyright notice (session 2123): reuse "for
commercial or non-commercial purposes is authorised provided the source is acknowledged".
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

NAME = "eurostat_electricity_monthly"
CONNECTOR = "eurostat_cb_em"
SOURCE = "eurostat:nrg_cb_pem_nrg_cb_em"
API = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/"
PEM = API + "data/nrg_cb_pem?format=SDMX-CSV&compressed=false&startPeriod=2016-01"
EM = API + "data/nrg_cb_em?format=SDMX-CSV&compressed=false&startPeriod=2016-01"
SIEC = API + "codelist/ESTAT/SIEC"
NRG_BAL = API + "codelist/ESTAT/NRG_BAL"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_pem/default/table"
UA = erc.UA
HEAD_PEM = ["DATAFLOW", "LAST UPDATE", "freq", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
HEAD_EM = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
X_COLS = ["x_geo_code", "x_dataset", "x_flag", "x_conf_status"]


def rows_of(t, dataset, key_col, prefix, names, base):
    rows = []
    for r in t.to_dict("records"):
        v = r["OBS_VALUE"].strip()
        if v == "":
            continue
        try:
            value = float(v) * 1000
        except ValueError:
            raise RuntimeError(f"{dataset} {r['geo']} {r[key_col]} {r['TIME_PERIOD']}: not a number: {v!r}")
        if not re.fullmatch(r"\d{4}-\d\d", r["TIME_PERIOD"]):
            raise RuntimeError(f"{dataset}: a period not a month: {r['TIME_PERIOD']!r}")
        geo = r["geo"]
        rows.append(dict(entity=f"eurostat_elec:{geo}", variable=f"{prefix}:{r[key_col]}", ts_utc=f"{r['TIME_PERIOD']}-01T00:00:00Z",
                         value=round(value, 3), unit="MWh", freq="P1M", geo="" if geo in erc.AGGREGATES else erc.ISO.get(geo, geo),
                         market="", node=names.get(r[key_col], r[key_col]), **base, x_geo_code=geo, x_dataset=dataset,
                         x_flag=r["OBS_FLAG"].strip(), x_conf_status=r["CONF_STATUS"].strip()))
    return rows


def build(pem_text, em_text, siec_names, bal_names, base_pem, base_em):
    p = pd.read_csv(io.StringIO(pem_text), dtype=str, keep_default_na=False)
    e = pd.read_csv(io.StringIO(em_text), dtype=str, keep_default_na=False)
    if list(p.columns) != HEAD_PEM or list(e.columns) != HEAD_EM:
        raise RuntimeError(f"a header is not Eurostat's SDMX-CSV: {list(p.columns)} / {list(e.columns)}")
    bad = (sorted(set(p.unit) - {"GWH", "PC"}) + sorted(set(e.unit) - {"GWH"}) + sorted((set(p.freq) | set(e.freq)) - {"M"})
           + sorted(set(e.siec) - {"E7000"}))
    if bad:
        raise RuntimeError(f"a unit, frequency or balance not expected: {bad}")
    left = sorted((set(p.geo) | set(e.geo)) - erc.KEPT)
    p = p[p.geo.isin(erc.KEPT) & (p.unit == "GWH")]
    e = e[e.geo.isin(erc.KEPT)]
    rows = rows_of(p, "nrg_cb_pem", "siec", "net_production", siec_names, base_pem) + rows_of(e, "nrg_cb_em", "nrg_bal", "flow", bal_names, base_em)
    out = pd.DataFrame(rows)
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), left


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_pem and nrg_cb_em: electricity by European country, a month")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused("eurostat") or ip.paused_host("ec.europa.eu"):
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
    try:
        fetch = lambda u: ip.fetch_raw(CONNECTOR, u, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300, pause=1)  # noqa: E731
        siec, _ = fetch(SIEC)
        bal, _ = fetch(NRG_BAL)
        pem, rp = fetch(PEM)
        em, re_ = fetch(EM)
        pem_t, em_t = pem.decode("utf-8", errors="replace"), em.decode("utf-8", errors="replace")
        updated = sorted((set(re.findall(r"^[^,]*,([^,]*),", pem_t, re.M)) | set(re.findall(r"^[^,]*,([^,]*),", em_t, re.M))) - {"LAST UPDATE"})
        bp = dict(source=SOURCE, source_url=PEM, retrieved_at=rp.get("retrieved_at") or "", vintage=ip.vintage_of(rp))
        be = dict(source=SOURCE, source_url=EM, retrieved_at=re_.get("retrieved_at") or "", vintage=ip.vintage_of(re_))
        t, left = build(pem_t, em_t, erc.names(siec), erc.names(bal), bp, be)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols]
        countries = sorted(set(t.x_geo_code) - erc.AGGREGATES)
        last = t.ts_utc.max()[:7]
        head = [
            f"Energy Research Warehouse (ERW): Eurostat, monthly electricity statistics, net production by fuel (nrg_cb_pem) and the electricity flows "
            f"(nrg_cb_em), {t.ts_utc.min()[:7]} to {last}, {len(countries)} European countries and the EU (session 2225)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_elec:<Eurostat geo code>; variable net_production:<SIEC code> or flow:<NRG_BAL code> "
            "(imports, exports, the supply available for the internal market AIM, distribution losses DL, TI_EHG_EPS); unit MWh (Eurostat's GWh times "
            "1,000); ts_utc the month's first day; freq P1M; geo ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020; node the code's English name.",
            f"{len(t)} rows. Countries: {' '.join(countries)}. Left out by Eurostat's terms (data for countries outside the EU, EFTA and the official "
            f"candidates may not be reused commercially): {' '.join(left) or 'none'}. nrg_cb_pem's percent shares are not taken. Each fuel and flow as "
            "published, no sum made here; a blank value has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electricity_monthly.py; nrg_cb_pem retrieved {bp['retrieved_at']}, nrg_cb_em "
            f"{be['retrieved_at']}; Eurostat's last update {', '.join(updated)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Net electricity generation by type of fuel, monthly data (nrg_cb_pem) and Supply, transformation and "
            f"consumption of electricity, monthly data (nrg_cb_em), {PAGE}",
            f"  access: {PEM} ; {EM}",
            f"  names: {SIEC} ; {NRG_BAL}",
            f"License: public with acknowledgement (Eurostat's copyright notice, {erc.TERMS}). Cite: Eurostat, nrg_cb_pem and nrg_cb_em. Eurostat bears "
            "no responsibility for this reshaping (the rows filtered by country, GWh written as MWh).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(countries)} countries, to {last}; left out {left}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Net electricity generation by type of fuel, monthly (nrg_cb_pem); Supply, transformation and consumption of electricity, monthly (nrg_cb_em)",
                                    report_url=PAGE, document_list=PEM, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
