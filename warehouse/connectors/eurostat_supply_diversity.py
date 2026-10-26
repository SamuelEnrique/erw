#!/usr/bin/env python3
"""Eurostat's diversity index of energy supply (nrg_ind_di): an index for each EU member's energy supply a year, from 1992
(session 2832, chain 144, the third own choice, from session 2799's reading of Eurostat's dataflow list). The file gives the
index without its method; the ERW writes it as Eurostat gives it and reads no direction into it beyond Eurostat's own metadata.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_supply_diversity_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 60 KB of SDMX-CSV, the whole dataset):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_di?format=SDMX-CSV&compressed=false

    entity      eurostat_supply_diversity:<Eurostat geo code>
    variable    supply_diversity_index; unit index (Eurostat's INX)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR)
    node        "<geo code> diversity index of energy supply"
    x_*         Eurostat's geo code, the observation's flag and confidentiality status

A blank has no row; nothing is filled. Checks that stop the run: a header not Eurostat's; a frequency or unit not expected; a
value not a number, or outside 0 to 1; a period not a year; a key given twice. Countries kept: the EU's members, EFTA's and the
official candidates, with EU27_2020, as eurostat_import_dependency_annual keeps them (the file holds the 27 members only).

    python warehouse/connectors/eurostat_supply_diversity.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_supply_diversity/ with --offline. ec.europa.eu's robots file disallows
the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2832, read again,
the same file as session 2827's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the
source acknowledged; source: Eurostat.
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

NAME = "eurostat_supply_diversity_annual"
CONNECTOR = "eurostat_supply_diversity"
SOURCE = "eurostat:nrg_ind_di"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_di/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_di?format=SDMX-CSV&compressed=false"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
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
    bad = sorted(set(t0.freq) - {"A"}) + sorted(set(t0.unit) - {"INX"})
    if bad:
        raise RuntimeError(f"a frequency or unit not expected: {bad}")
    counts = {"blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
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
            raise RuntimeError(f"{r.geo} {r.TIME_PERIOD}: not a number: {v!r}")
        if not 0 <= value <= 1:
            raise RuntimeError(f"{r.geo} {r.TIME_PERIOD}: an index outside 0 to 1: {v!r}")
        rows.append({"entity": f"eurostat_supply_diversity:{r.geo}", "variable": "supply_diversity_index",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "index", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} diversity index of energy supply", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_flag": r.OBS_FLAG.strip(),
                     "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ind_di: the diversity index of energy supply, a year")
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
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, diversity index of energy supply, annual (nrg_ind_di), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2832)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_supply_diversity:<geo>; variable supply_diversity_index; unit index (Eurostat's INX, as given); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR).",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas. {counts['blank']} blanks have no row; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_supply_diversity.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Diversity index of energy supply (nrg_ind_di), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ind_di. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Diversity index of energy supply (nrg_ind_di)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
