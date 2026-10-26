#!/usr/bin/env python3
"""Eurostat's electric vehicle recharging pools, stations and points and their power output (road_if_rchev): each European
country's public recharging infrastructure a year, from 2019 (session 2804, chain 142, the session's own choice, beside
afdc_ev_charging_state_annual, session 2155, the US's by state).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_ev_recharging_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 36 KB of SDMX-CSV, the whole dataset) and the
TRA_INFR codelist (the infrastructure types' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchev?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/TRA_INFR?format=TSV

    entity      eurostat_ev_recharging:<Eurostat geo code>
    variable    the type and measure (ITEMS below): recharging_points, recharging_stations, recharging_pools and
                heavy_duty_pools (counts, Eurostat's NR), recharging_pools_power and heavy_duty_pools_power (the pools' power
                output, Eurostat's kW)
    unit        count, or MW (Eurostat's kW divided by 1,000)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR)
    node        "<geo code> <the TRA_INFR name>, <number or power output>"
    x_*         Eurostat's geo, infrastructure type and unit codes, the observation's flag (i: see Eurostat's metadata) and
                confidentiality status

Countries report from different years and not every measure: Germany's points from 2019, France's from 2021; a heavy-duty
pool's power is given by a few. Zeros are kept as Eurostat prints them (Estonia's heavy-duty pools before 2023, among others);
a blank has no row; nothing is filled. Checks that stop the run: a header not Eurostat's; a frequency, type or unit not
expected, or a type in a unit it is not read in; a value not a number or negative; a period not a year; a key given twice.
Countries kept: the EU's members, EFTA's and the official candidates, as eurostat_electricity_consumption_annual keeps them (the
United Kingdom left out, named in the header).

    python warehouse/connectors/eurostat_ev_recharging.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_ev_recharging/ with --offline. ec.europa.eu's robots file disallows
the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2804, read again,
the same file as session 2799's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the
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

NAME = "eurostat_ev_recharging_annual"
CONNECTOR = "eurostat_ev_recharging"
SOURCE = "eurostat:road_if_rchev"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/road_if_rchev/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchev?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/TRA_INFR?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "tra_infr", "geo", "unit", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
ITEMS = {("RCHRG_PNT", "NR"): ("recharging_points", "count"), ("RCHRG_STN", "NR"): ("recharging_stations", "count"),
         ("RCHRG_POOL", "NR"): ("recharging_pools", "count"), ("RCHRG_POOL", "KW"): ("recharging_pools_power", "MW"),
         ("RCHRG_POOL_HVY", "NR"): ("heavy_duty_pools", "count"), ("RCHRG_POOL_HVY", "KW"): ("heavy_duty_pools_power", "MW")}
MEASURE = {"NR": "number", "KW": "power output"}
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_tra_infr", "x_unit", "x_flag", "x_conf_status"]


def type_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the TRA_INFR codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if names.get("RCHRG_PNT") != "Recharging point" or any(k not in names for k, _ in ITEMS):
        raise RuntimeError("the TRA_INFR codelist is not Eurostat's, or lacks a recharging type")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.freq) - {"A"}) + sorted({f"{a} in {b}" for a, b in zip(t0.tra_infr, t0.unit)} - {f"{a} in {b}" for a, b in ITEMS})
    if bad:
        raise RuntimeError(f"a frequency, or a type in a unit, not expected: {bad}")
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
            raise RuntimeError(f"{r.geo} {r.tra_infr} {r.TIME_PERIOD}: not a number: {v!r}")
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.tra_infr} {r.TIME_PERIOD}: a negative value: {v!r}")
        if value == 0:
            counts["zero"] += 1
        variable, unit = ITEMS[(r.tra_infr, r.unit)]
        rows.append({"entity": f"eurostat_ev_recharging:{r.geo}", "variable": variable,
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z",
                     "value": round(value / 1000.0, 6) if unit == "MW" else value, "unit": unit,
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} {names[r.tra_infr]}, {MEASURE[r.unit]}", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_tra_infr": r.tra_infr, "x_unit": r.unit, "x_flag": r.OBS_FLAG.strip(),
                     "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat road_if_rchev: European EV recharging infrastructure, a year")
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
        t, counts = build(content, type_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        per = t.groupby("variable").x_geo_code.nunique()
        flagged = int((t.x_flag == "i").sum())
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, electric vehicle recharging pools, stations and points and their power output, annual (road_if_rchev), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2804)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_ev_recharging:<geo>; variable recharging_points, recharging_stations, recharging_pools, heavy_duty_pools (unit count, Eurostat's NR), recharging_pools_power, heavy_duty_pools_power (unit MW, Eurostat's kW divided by 1,000); "
            "ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR); x_tra_infr and x_unit Eurostat's codes.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas; areas a variable: {', '.join(f'{v} {n}' for v, n in per.items())}. Countries report from different years and not every measure. Zeros are kept as Eurostat prints them ({counts['zero']}); "
            f"{counts['blank']} blanks have no row; nothing is filled. {flagged} observations carry Eurostat's flag i (see its metadata), kept in x_flag. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. "
            f"Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_ev_recharging.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Electric vehicle recharging pools, stations and points and their power output (road_if_rchev), {PAGE}",
            f"  access: {URL} and the types' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, road_if_rchev. Eurostat bears no responsibility for this reshaping (kW written as MW).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Electric vehicle recharging pools, stations and points and their power output (road_if_rchev)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros kept {counts['zero']}, flagged i {flagged}; left out {counts['left_out_geo']}")
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
