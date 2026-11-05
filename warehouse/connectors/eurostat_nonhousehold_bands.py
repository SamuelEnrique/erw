#!/usr/bin/env python3
"""Eurostat's non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v): the share of each European
country's non-household electricity used by consumers in each of the seven price-statistics bands, IA (under 20 MWh a year) to
IG (150,000 MWh and over), a year from 2017 (session 2820, chain 144, in place of MAVIR, whose www and bare robots files
disallow every path to every reader).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_nonhousehold_bands_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 190 KB of SDMX-CSV, the whole dataset):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_pc_205_v?format=SDMX-CSV&compressed=false

    entity      eurostat_nonhh_bands:<Eurostat geo code>:<the NRG_CONS band code>
    variable    consumption_share; unit pct (the band's share of the country's non-household consumption, as Eurostat
                gives it)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregates (EU27_2020, EA)
    node        "<geo code> non-household electricity, <the band>"
    x_*         Eurostat's geo and band codes, the observation's flag and confidentiality status

The bands' names are the NRG_CONS codelist's (session 2820 read it, read 1634), written here in ASCII. They are the bands of
Eurostat's non-household electricity prices (nrg_pc_205, in EUR, not taken): the volumes tell how much of a country's use each
price band stands for. The seven bands are compared with 100 in every country year that gives all seven, within 0.5 points; a
case off is counted in the header and listed in the run log, kept as published. A blank has no row; zeros are kept; nothing is
filled. Checks that stop the run: a header not Eurostat's; a frequency, product, unit or band not expected; a value not a
number, or outside 0 to 100; a period not a year; a key given twice. Countries kept: the EU's members, EFTA's and the official
candidates, with EU27_2020 and the euro area, as eurostat_electricity_consumption_annual keeps them (Kosovo left out).

    python warehouse/connectors/eurostat_nonhousehold_bands.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_nonhousehold_bands/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2820,
read again, the same file as session 2818's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
with the source acknowledged; source: Eurostat.
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

NAME = "eurostat_nonhousehold_bands_annual"
CONNECTOR = "eurostat_nonhousehold_bands"
SOURCE = "eurostat:nrg_pc_205_v"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205_v/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_pc_205_v?format=SDMX-CSV&compressed=false"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_cons", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
BANDS = {"MWH_LT20": "band IA, less than 20 MWh a year", "MWH20-499": "band IB, 20 to 499 MWh",
         "MWH500-1999": "band IC, 500 to 1,999 MWh", "MWH2000-19999": "band ID, 2,000 to 19,999 MWh",
         "MWH20000-69999": "band IE, 20,000 to 69,999 MWh", "MWH70000-149999": "band IF, 70,000 to 149,999 MWh",
         "MWH_GE150000": "band IG, 150,000 MWh or over"}
TOL = 0.5   # points
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020", "EA"}
AGGREGATES = {"EU27_2020", "EA"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nrg_cons", "x_flag", "x_conf_status"]


def build(content, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = (sorted(set(t0.freq) - {"A"}) + sorted(set(t0.siec) - {"E7000"}) + sorted(set(t0.unit) - {"PC"})
           + sorted(set(t0.nrg_cons) - set(BANDS)))
    if bad:
        raise RuntimeError(f"a frequency, product, unit or band not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nrg_cons} {r.TIME_PERIOD}: not a number: {v!r}")
        if not 0 <= value <= 100:
            raise RuntimeError(f"{r.geo} {r.nrg_cons} {r.TIME_PERIOD}: a share outside 0 to 100: {v!r}")
        if value == 0:
            counts["zero"] += 1
        rows.append({"entity": f"eurostat_nonhh_bands:{r.geo}:{r.nrg_cons}", "variable": "consumption_share",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "pct", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} non-household electricity, {BANDS[r.nrg_cons]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_nrg_cons": r.nrg_cons,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """The seven bands against 100: (country years with all seven, those off by more than TOL)."""
    g = t.groupby(["x_geo_code", "ts_utc"]).value.agg(["size", "sum"])
    whole = g[g["size"] == len(BANDS)]
    off = whole[(whole["sum"] - 100).abs() > TOL]
    return len(whole), [(k[0], k[1][:4], round(float(s), 3)) for k, s in off["sum"].items()]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_pc_205_v: non-household electricity by consumption band, a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180)
        t, counts = build(content, URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        n, off = checks(t)
        for x in off:
            log(f"  the seven bands do not make 100, kept as published: {x}")
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, non-household consumption volumes of electricity by consumption bands, annual (nrg_pc_205_v): each band's share of non-household consumption, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2820)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_nonhh_bands:<geo>:<band> (MWH_LT20 band IA under 20 MWh a year, MWH20-499 IB, MWH500-1999 IC, MWH2000-19999 ID, MWH20000-69999 IE, MWH70000-149999 IF, MWH_GE150000 IG 150,000 MWh and over); variable consumption_share; unit pct; "
            "ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020 and EA; x_nrg_cons Eurostat's code.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas. The seven bands make 100 within {TOL:g} points in {n - len(off)} of {n} country years that give all seven; the others kept as published and listed in the run log. Zeros are kept ({counts['zero']}); {counts['blank']} blanks have no row; nothing is filled. "
            f"Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_nonhousehold_bands.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_pc_205_v. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; bands make 100 in {n - len(off)} of {n}; zeros {counts['zero']}, blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
