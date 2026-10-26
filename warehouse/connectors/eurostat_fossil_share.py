#!/usr/bin/env python3
"""Eurostat's share of fossil fuels in gross available energy (nrg_ind_ffgae): each European country's dependence on fossil
fuels a year, from 1990 (session 2826, chain 144, the session's own choice, from session 2799's reading of Eurostat's dataflow
list).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_fossil_share_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 90 KB of SDMX-CSV, the whole dataset):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ffgae?format=SDMX-CSV&compressed=false

    entity      eurostat_fossil_share:<Eurostat geo code>
    variable    fossil_share_gross_available_energy; unit pct (Eurostat's PC)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                EU27_2020
    node        "<geo code> share of fossil fuels in gross available energy"
    x_*         Eurostat's geo code, the observation's flag and confidentiality status

A share outside 0 to 100 is kept as Eurostat publishes it and counted (Estonia's three, above 100, in its early
years). A blank has no row; nothing
is filled. Checks that stop the run: a header not Eurostat's; a frequency or unit not expected; a value not a number; a period
not a year; a key given twice. Countries kept: the EU's members, EFTA's and
the official candidates, with EU27_2020, as eurostat_import_dependency_annual keeps them (the United Kingdom and Kosovo left
out).

    python warehouse/connectors/eurostat_fossil_share.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_fossil_share/ with --offline. ec.europa.eu's robots file disallows the
old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2826, read again, the
same file as session 2821's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source
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

NAME = "eurostat_fossil_share_annual"
CONNECTOR = "eurostat_fossil_share"
SOURCE = "eurostat:nrg_ind_ffgae"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ffgae/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ffgae?format=SDMX-CSV&compressed=false"
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
    bad = sorted(set(t0.freq) - {"A"}) + sorted(set(t0.unit) - {"PC"})
    if bad:
        raise RuntimeError(f"a frequency or unit not expected: {bad}")
    counts = {"blank": 0, "outside": [], "left_out_geo": sorted(set(t0.geo) - KEPT), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
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
        if not 0 <= value <= 100:
            counts["outside"].append((r.geo, r.TIME_PERIOD, value))
        rows.append({"entity": f"eurostat_fossil_share:{r.geo}", "variable": "fossil_share_gross_available_energy",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "pct", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} share of fossil fuels in gross available energy", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_flag": r.OBS_FLAG.strip(),
                     "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ind_ffgae: the share of fossil fuels in gross available energy, a year")
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
        for x in counts["outside"]:
            log(f"  a share outside 0 to 100, kept as published: {x}")
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, share of fossil fuels in gross available energy, annual (nrg_ind_ffgae), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2826)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_fossil_share:<geo>; variable fossil_share_gross_available_energy; unit pct; ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas. {len(counts['outside'])} shares outside 0 to 100 kept as published, listed in the run log; {counts['blank']} blanks have no row; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_fossil_share.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Share of fossil fuels in gross available energy (nrg_ind_ffgae), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ind_ffgae. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Share of fossil fuels in gross available energy (nrg_ind_ffgae)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; outside {len(counts['outside'])}; blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
