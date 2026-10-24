#!/usr/bin/env python3
"""Eurostat's gross electricity production by fuel (nrg_bal_peh, GEP): each European country's electricity generated a
year from each energy product, all producers, from 1990 (session 2413, chain 114: a source of the session's own
choosing, beside eurostat_electricity_capacity_annual).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_production_annual.csv,
from Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 7 MB of SDMX-CSV, one balance item and
one unit) and the SIEC codelist (the products' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_peh/A.GEP..GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC?format=TSV

    entity      eurostat_electricity_production:<Eurostat geo code>:<SIEC code>
    variable    gross_electricity_production (GEP, all producers: main activity and autoproducers, electricity only and
                combined heat and power)
    unit        MWh: Eurostat's GWh times 1,000
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank
                for Eurostat's aggregate EU27_2020
    node        "<geo code> gross electricity production, <the SIEC name>"
    x_*         Eurostat's geo and SIEC codes, the observation's flag and confidentiality status

The 75 products are Eurostat's SIEC codes, a hierarchy whose levels overlap (TOTAL; solid fossil fuels C0000X0350-0370 and
its coals; natural gas G3000; renewables RA000 and its hydro RA100, wind RA300, solar RA400s and biofuels; nuclear N900H;
and so on): a sum takes one level. Eurostat's TOTAL is the sum of its top groups (solid fossil fuels, manufactured gases,
peat, oil shale, natural gas, oil, renewables, non-renewable waste, nuclear, heat from other sources, other fuels) plus
pumped hydro (RA130), which renewables leave out; the header counts the country years where that does not hold within 1
GWh, kept as Eurostat publishes them. Countries kept: the EU's members, EFTA's and the official candidates, with
EU27_2020, as eurostat_gas_balance_monthly keeps them (the United Kingdom and Kosovo left out). A blank (Eurostat's flag
m, missing) has no row; zeros are kept; nothing is filled. A header not Eurostat's, a balance item, unit, frequency or
product not expected, a value that is not a number or a key given twice stops the run.

    python warehouse/connectors/eurostat_electricity_production.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_electricity_production/ with --offline. ec.europa.eu's robots
file disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no AI agent (session
2413). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source acknowledged;
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

NAME = "eurostat_electricity_production_annual"
CONNECTOR = "eurostat_electricity_production"
SOURCE = "eurostat:nrg_bal_peh"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_peh/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_peh/A.GEP..GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990"
SIEC_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
TOP = ["C0000X0350-0370", "C0350-0370", "P1000", "S2000", "G3000", "O4000XBIO", "RA000", "W6100_6220", "N900H",
       "H8000", "X9900", "RA130"]
TOL = 1.0   # GWh
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_flag", "x_conf_status"]


def siec_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the SIEC codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if names.get("TOTAL") != "Total" or "G3000" not in names:
        raise RuntimeError("the SIEC codelist is not Eurostat's")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.nrg_bal) - {"GEP"}) \
        + sorted(set(t0.siec) - set(names))
    if bad:
        raise RuntimeError(f"a unit, frequency, balance item or product not expected: {bad}")
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
            raise RuntimeError(f"{r.geo} {r.siec} {r.TIME_PERIOD}: not a number: {v!r}")
        if value == 0:
            counts["zero"] += 1
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_electricity_production:{r.geo}:{r.siec}", "variable": "gross_electricity_production",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": round(value * 1000.0, 3), "unit": "MWh",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} gross electricity production, {names[r.siec]}", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_siec": r.siec, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def total_check(t):
    """Eurostat's TOTAL against its top groups plus pumped hydro: the country years compared and those off by more than TOL GWh."""
    p = t.assign(gwh=t.value / 1000.0).pivot_table(index=["x_geo_code", "ts_utc"], columns="x_siec", values="gwh", aggfunc="first")
    cols = [c for c in TOP if c in p.columns]
    d = (p[cols].fillna(0).sum(axis=1) - p["TOTAL"]).dropna()
    return len(d), d[d.abs() > TOL]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_bal_peh: European gross electricity production by fuel, a year")
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
        codes, _ = ip.fetch_raw(CONNECTOR, SIEC_URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=300)
        t, counts = build(content, siec_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        compared, off = total_check(t)
        for (geo, ts), g in off.sort_values().items():
            log(f"  the top groups plus pumped hydro less TOTAL: {g:.3f} GWh, {geo} {ts[:4]}")
        worst = f"; the largest {off.abs().max():.1f} GWh ({off.abs().idxmax()[0]} {off.abs().idxmax()[1][:4]})" if len(off) else ""
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, gross electricity production by fuel, all producers, annual (nrg_bal_peh, GEP), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2413)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_electricity_production:<geo>:<SIEC>; variable gross_electricity_production; unit MWh (Eurostat's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; "
            "geo ISO alpha-2 (EL is GR), blank for EU27_2020; node the SIEC product's name; x_siec Eurostat's product code. The products are a hierarchy whose levels overlap: a sum takes one level.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.x_siec.nunique()} products. Zeros are kept as Eurostat prints them ({counts['zero']:,}); {counts['blank']:,} blanks (flag m, missing) have no row; nothing is filled. "
            f"TOTAL equals its top groups plus pumped hydro (RA130) within {TOL:g} GWh in {compared - len(off):,} of {compared:,} country years; the other {len(off)} are kept as Eurostat publishes them and listed in the run log{worst}. "
            f"Areas left out by Eurostat's terms: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electricity_production.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Production of electricity and derived heat by type of fuel (nrg_bal_peh), gross electricity production, {PAGE}",
            f"  access: {URL} and the SIEC names from {SIEC_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_bal_peh. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Production of electricity and derived heat by type of fuel (nrg_bal_peh), gross electricity production",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros kept {counts['zero']:,}, blanks {counts['blank']:,}; TOTAL off in {len(off)} of {compared:,}{worst}; left out {counts['left_out_geo']}")
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
