#!/usr/bin/env python3
"""Eurostat's energy import origin concentration index by fuel (nrg_ind_ioc): how concentrated each EU country's imports of
each fuel are on few countries of origin, a year from 2015, an index from 0 (spread over many origins) to 1 (one origin)
(session 2827, chain 144, the second own choice, from session 2799's reading of Eurostat's dataflow list).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_import_concentration_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 470 KB of SDMX-CSV, the whole dataset) and the
SIEC codelist (the fuels' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ioc?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC?format=TSV

    entity      eurostat_ioc:<Eurostat geo code>:<SIEC code> (TOTAL, electricity E7000, natural gas G3000, crude oil, the oil
                products, coal and its products, peat, heat, the liquid biofuels)
    variable    import_origin_concentration; unit index (Eurostat's INX, 0 to 1)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR)
    node        "<geo code> import origin concentration, <the SIEC name>"
    x_*         Eurostat's geo and SIEC codes, the observation's flag and confidentiality status

A blank has no row; zeros and ones are kept; nothing is filled. Checks that stop the run: a header not Eurostat's; a frequency,
unit or product not expected; a value not a number, or outside 0 to 1; a period not a year; a key given twice. Countries kept:
the EU's members, EFTA's and the official candidates, as eurostat_import_dependency_annual keeps them (the file holds the 27
members only).

    python warehouse/connectors/eurostat_import_concentration.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_import_concentration/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2827,
read again, the same file as session 2826's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
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

NAME = "eurostat_import_concentration_annual"
CONNECTOR = "eurostat_import_concentration"
SOURCE = "eurostat:nrg_ind_ioc"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ioc/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ioc?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
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
    if names.get("E7000") != "Electricity" or names.get("G3000") != "Natural gas":
        raise RuntimeError("the SIEC codelist is not Eurostat's")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.freq) - {"A"}) + sorted(set(t0.unit) - {"INX"}) + sorted(set(t0.siec) - set(names))
    if bad:
        raise RuntimeError(f"a frequency, unit or product not expected: {bad}")
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
            raise RuntimeError(f"{r.geo} {r.siec} {r.TIME_PERIOD}: not a number: {v!r}")
        if not 0 <= value <= 1:
            raise RuntimeError(f"{r.geo} {r.siec} {r.TIME_PERIOD}: an index outside 0 to 1: {v!r}")
        rows.append({"entity": f"eurostat_ioc:{r.geo}:{r.siec}", "variable": "import_origin_concentration",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "index", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} import origin concentration, {names[r.siec]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_siec": r.siec,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    counts["ones"] = int((t.value == 1).sum())
    counts["zeros"] = int((t.value == 0).sum())
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ind_ioc: the EU's energy import origin concentration by fuel, a year")
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
        codes, _ = ip.fetch_raw(CONNECTOR, CODES_URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=180)
        t, counts = build(content, siec_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, energy import origin concentration index by fuel, annual (nrg_ind_ioc), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2827)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_ioc:<geo>:<SIEC code>; variable import_origin_concentration; unit index (0 spread over many origins, 1 one origin); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR); x_siec Eurostat's code.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.x_siec.nunique()} fuels. {counts['ones']:,} values of 1 (one origin) and {counts['zeros']} of 0 kept; {counts['blank']} blanks have no row; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. "
            f"Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_import_concentration.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Energy import origin concentration index by fuel (nrg_ind_ioc), {PAGE}",
            f"  access: {URL} and the fuels' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ind_ioc. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Energy import origin concentration index by fuel (nrg_ind_ioc)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; ones {counts['ones']}, zeros {counts['zeros']}, blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
