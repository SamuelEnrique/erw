#!/usr/bin/env python3
"""Luxembourg's power stations each year from 1960 to 2024, their net maximum power (MW) and their number, by primary and
secondary generation and type of station, as STATEC (Luxembourg's national statistics institute) gives them in its LUSTAT
dataflow DF_A4201 "Net maximum power (in MWe) and units of the power stations" (session 2784, chain 141, the session's own
choice, beside chain 140's DF_A4203 generation and DF_A4208 trade).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statec_lu_power_capacity_annual.csv, from one
request to LUSTAT's SDMX service (.Stat Suite, no key), every key of the dataflow as CSV with labels:

    https://lustat.statec.lu/rest/data/LU1,DF_A4201,1.0/all?format=csvfilewithlabels

    entity      statec_cap:lu:<code>, STATEC's SPECIFICATION code lower-cased: l01 total; sl01 primary and sl02 secondary
                generation stations; ssl01 to ssl05 hydropower, wind, solar, classic thermal and combined heat and power
                stations; sssl01 to sssl06 pumping, large and micro (hydro), biomethanation, woodwaste and woodpellets stations
    variable    net_maximum_power (STATEC's C001, MWe, unit MW) or power_stations (C002, the number of units, unit count)
    ts_utc      the year's first day; freq P1Y; geo LU; node the code and STATEC's label

How the codes relate, compared in every year that gives the parts, within 0.5 MW and exactly for the counts: l01 is sl01 plus
sl02; sl01 is ssl01 to ssl03; sl02 is ssl04 and ssl05. STATEC's totals differ from their parts in a few years (the power in 2009,
the numbers of stations in 1996 to 2000, 2020, 2021 and 2024 in October 2026's file); these are counted, listed in the run log
and kept as published. The third level's parts are not checked against
their parents (pumping, large and micro stations do not sum to hydropower as published). A header not the service's, a variable,
frequency or code not expected, a key given twice or a value not a number stops the run. A missing observation (STATEC's
not available, not applicable) has no row; nothing is filled.

    python warehouse/connectors/statec_power_capacity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statec/ and reused unless --fresh; --offline asks nothing. lustat.statec.lu has
no robots file (session 2784, read 1582). License: STATEC's legal notice (read 1564): CC0 1.0; public.
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

NAME = "statec_lu_power_capacity_annual"
CONNECTOR = "statec"
SOURCE = "statec:lustat_df_a4201"
HOST = "lustat.statec.lu"
URL = "https://lustat.statec.lu/rest/data/LU1,DF_A4201,1.0/all?format=csvfilewithlabels"
PAGE = "https://lustat.statec.lu/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATEC, LUSTAT, DF_A4201 Net maximum power (in MWe) and units of the power stations"
VARS = {"C001": ("net_maximum_power", "MW", 0.5), "C002": ("power_stations", "count", 0.0)}
CODES = ["L01", "SL01", "SL02", "SSL01", "SSL02", "SSL03", "SSL04", "SSL05",
         "SSSL01", "SSSL02", "SSSL03", "SSSL04", "SSSL05", "SSSL06"]
SUMS = (("L01", ["SL01", "SL02"]), ("SL01", ["SSL01", "SSL02", "SSL03"]), ("SL02", ["SSL04", "SSL05"]))
X_COLS = []


def parse(content):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    for c in ("STRUCTURE_ID", "FREQ", "VARIABLES", "SPECIFICATION", "Specification", "TIME_PERIOD", "OBS_VALUE"):
        if c not in d.columns:
            raise RuntimeError(f"the service's CSV lacks {c}")
    if set(d.STRUCTURE_ID) != {"LU1:DF_A4201(1.0)"} or set(d.FREQ) != {"A"}:
        raise RuntimeError("not DF_A4201's annual file")
    bad = sorted(set(d.VARIABLES) - set(VARS)) + sorted(set(d.SPECIFICATION) - set(CODES))
    if bad:
        raise RuntimeError(f"a variable or code not expected: {bad}")
    vals, names, missing, seen, counted = {}, {}, 0, set(), []
    for r in d.itertuples(index=False):
        var, code, year, v = r.VARIABLES, r.SPECIFICATION, r.TIME_PERIOD, r.OBS_VALUE.strip()
        if not year.isdigit():
            raise RuntimeError(f"a period not a year: {year!r}")
        key = (var, code, year)
        if key in seen:
            raise RuntimeError(f"{key} given twice")
        seen.add(key)
        names[code] = r.Specification
        if v == "":
            missing += 1
            continue
        try:
            vals[key] = float(v)
        except ValueError:
            raise RuntimeError(f"{key}: not a number: {v!r}")
    for var, (_, _, tol) in VARS.items():
        for y in sorted({k[2] for k in vals}):
            get = lambda c: vals.get((var, c, y))
            for parent, kids in SUMS:
                if get(parent) is None or all(get(k) is None for k in kids):
                    continue
                s = sum(get(k) or 0.0 for k in kids)
                if abs(s - get(parent)) > tol + 1e-9:
                    counted.append((y, var, parent, round(s - get(parent), 3)))
    return vals, names, missing, counted


def frame(vals, names, base):
    rows = [dict(entity=f"statec_cap:lu:{c.lower()}", variable=VARS[v][0], ts_utc=f"{y}-01-01T00:00:00Z", value=round(x, 3),
                 unit=VARS[v][1], freq="P1Y", geo="LU", market="", node=f"{c} {names[c]}", **base)
            for (v, c, y), x in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="STATEC DF_A4201: Luxembourg's power stations' net maximum power and number, a year")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the file again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        vals, names, missing, counted = parse(content)
        for y, v, p_, dd in counted:
            log(f"  {v} {p_} less its parts: {-dd:+.3f} in {y}, kept as STATEC publishes it")
        t = frame(vals, names, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        mw = {k[:4]: v for k, v in t[(t.entity == "statec_cap:lu:l01") & (t.variable == "net_maximum_power")].set_index("ts_utc").value.items()}
        n = {k[:4]: v for k, v in t[(t.entity == "statec_cap:lu:l01") & (t.variable == "power_stations")].set_index("ts_utc").value.items()}
        head = [
            "Energy Research Warehouse (ERW): STATEC, LUSTAT DF_A4201: Luxembourg's power stations, net maximum power and number, by "
            f"primary and secondary generation and type, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2784)",
            "Shape: series (docs/datastandard.md v0). entity statec_cap:lu:<STATEC's code, lower-cased>; variable net_maximum_power "
            "(MW, STATEC's MWe) or power_stations (count); ts_utc the year's first day; freq P1Y; geo LU; node the code and STATEC's "
            "label. l01 = sl01 + sl02; sl01 = ssl01..ssl03 (hydropower, wind, solar); sl02 = ssl04 + ssl05 (classic thermal, CHP).",
            f"{len(t)} rows; the total, MW and stations: " + ", ".join(f"{y} {mw[y]:,.1f} and {n[y]:,.0f}" for y in ("1990", "2024")
                                                                     if y in mw and y in n)
            + f". {missing} observations not available have no row; the first two levels compared with their parts every year, "
            f"{len(counted)} differences kept as published (" + ", ".join(f"{p_} {v} {y}" for y, v, p_, _ in counted)
            + "); nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statec_power_capacity.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the data explorer: {PAGE})",
            "License: CC0 1.0 (STATEC's legal notice, https://statistiques.public.lu/en/support/notice.html). Credit, as STATEC's "
            "guidelines ask: STATEC, LUSTAT DF_A4201.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; counted {len(counted)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="STATEC (Luxembourg)",
                                    report="LUSTAT DF_A4201 Net maximum power (in MWe) and units of the power stations",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
