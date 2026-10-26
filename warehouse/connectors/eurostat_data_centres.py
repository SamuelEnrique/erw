#!/usr/bin/env python3
"""Eurostat's data centres' electricity consumption (isoc_env_ict_nrg): each European country's data centres' electricity a
year, 2020 to 2024 so far (session 2799, chain 142, the session's own choice: the ERW holds data centre projects, sites and
queue positions, and no measured consumption).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_data_centre_electricity_annual.csv,
from Eurostat's SDMX 2.1 dissemination API (no key), one request (about 8 KB of SDMX-CSV, the whole dataset):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_env_ict_nrg?format=SDMX-CSV&compressed=false

    entity      eurostat_data_centres:<Eurostat geo code>
    variable    electricity_consumption (SIEC E7000, NACE Rev. 2 "DATAC", data centres)
    unit        MWh: Eurostat's GWh times 1,000
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR)
    node        "<geo code> data centres' electricity consumption"
    x_*         Eurostat's geo code, the observation's flag and confidentiality status

Eurostat's own dataset began with reference year 2020 and countries joined it year by year: 6 report 2020, 31 report 2024.
A confidential observation (status C, no value) has no row and is counted. **A zero is kept as Eurostat prints it and counted**:
some zeros cannot be measured absences (Denmark's 2020 to 2022, while it hosts large data centres), and the header names the
countries that give one, for a reader to treat with care; nothing is filled. Checks that stop the run: a header not Eurostat's;
a unit, frequency, product or activity not expected; a value not a number or negative; a period not a year; a key given twice.
Countries kept: the EU's members, EFTA's and the official candidates, as eurostat_electricity_consumption_annual keeps them
(none other is in the file so far; any other is left out and named).

    python warehouse/connectors/eurostat_data_centres.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_data_centres/ with --offline. ec.europa.eu's robots file disallows the
old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2799, read again, the
same file as session 2798's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source
acknowledged; source: Eurostat.
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

NAME = "eurostat_data_centre_electricity_annual"
CONNECTOR = "eurostat_data_centres"
SOURCE = "eurostat:isoc_env_ict_nrg"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/isoc_env_ict_nrg/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_env_ict_nrg?format=SDMX-CSV&compressed=false"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "unit", "siec", "nace_r2", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_flag", "x_conf_status"]


def build(content, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.siec) - {"E7000"}) \
        + sorted(set(t0.nace_r2) - {"DATAC"})
    if bad:
        raise RuntimeError(f"a unit, frequency, product or activity not expected: {bad}")
    counts = {"confidential": 0, "blank": 0, "zero": [], "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["confidential" if r.CONF_STATUS.strip() == "C" else "blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.TIME_PERIOD}: not a number: {v!r}")
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.TIME_PERIOD}: a negative consumption: {v!r}")
        if value == 0:
            counts["zero"].append((r.geo, r.TIME_PERIOD))
        rows.append({"entity": f"eurostat_data_centres:{r.geo}", "variable": "electricity_consumption",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": round(value * 1000.0, 3), "unit": "MWh",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} data centres' electricity consumption", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat isoc_env_ict_nrg: European data centres' electricity consumption, a year")
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
        for geo, year in counts["zero"]:
            log(f"  a zero, kept as Eurostat prints it: {geo} {year}")
        zero_geo = pd.Series([g for g, _ in counts["zero"]]).value_counts().sort_index()
        by_year = t.groupby(t.ts_utc.str[:4]).size()
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, data centres' electricity consumption, annual (isoc_env_ict_nrg, E7000, NACE DATAC), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2799)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_data_centres:<geo>; variable electricity_consumption; unit MWh (Eurostat's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR).",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas; countries a year: {', '.join(f'{y} {n}' for y, n in by_year.items())}. {counts['confidential']} confidential observations (status C) and {counts['blank']} other blanks have no row; nothing is filled. "
            f"{len(counts['zero'])} zeros are kept as Eurostat prints them, some of which cannot be measured absences (treat with care): {', '.join(f'{g} {n}' for g, n in zero_geo.items()) or 'none'}. "
            f"Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_data_centres.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Data centres' electricity consumption (isoc_env_ict_nrg), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, isoc_env_ict_nrg. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Data centres' electricity consumption (isoc_env_ict_nrg)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; confidential {counts['confidential']}, zeros kept {len(counts['zero'])}; left out {counts['left_out_geo']}")
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
