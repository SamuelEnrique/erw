#!/usr/bin/env python3
"""Luxembourg's electricity imports by country of origin and exports by country of destination each year from 1933 to 2024, as
STATEC (Luxembourg's national statistics institute) gives them in its LUSTAT dataflow DF_A4208 "Electricity imports and exports
by country" (session 2776, chain 140, the session's own choice, the companion of session 2771's DF_A4203).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statec_lu_electricity_trade_annual.csv, from one
request to LUSTAT's SDMX service (.Stat Suite, no key), every key of the dataflow as CSV with labels:

    https://lustat.statec.lu/rest/data/LU1,DF_A4208,1.0/all?format=csvfilewithlabels

The dataflow gives each figure in TJ, ktep and GWh; this table takes the GWh rows (unit A03).

    entity      statec_trade:lu:<code>, STATEC's SPECIFICATION code lower-cased: l01 imports, l02 exports; sl01 to sl03 imports
                from Belgium, France and Germany; sl04 to sl06 exports to Belgium, France and Germany (RWE grid); ssl01 and
                ssl02 imports from Germany split into the Societe electrique de l'Our (SEO) and others
    variable    electricity_imports (l01, sl01 to sl03, ssl01, ssl02) or electricity_exports (l02, sl04 to sl06); unit MWh
                (STATEC's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo LU; node the code and STATEC's label

Checks that stop the run, within 0.5 GWh in every year that gives the parts: imports are sl01 to sl03; exports are sl04 to sl06.
Germany's split (ssl01 and ssl02 against sl03) is counted where it differs (1963 and 1969 in October 2026's file) and kept as
STATEC publishes it. A header not the service's, a unit, frequency or code not expected, a key given twice or a value not a
number stops the run. A missing observation has no row; nothing is filled.

    python warehouse/connectors/statec_electricity_trade.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statec/ and reused unless --fresh; --offline asks nothing. lustat.statec.lu has
no robots file (session 2776, read 1565). License: STATEC's legal notice (read 1564): CC0 1.0; public.
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

NAME = "statec_lu_electricity_trade_annual"
CONNECTOR = "statec"
SOURCE = "statec:lustat_df_a4208"
HOST = "lustat.statec.lu"
URL = "https://lustat.statec.lu/rest/data/LU1,DF_A4208,1.0/all?format=csvfilewithlabels"
PAGE = "https://lustat.statec.lu/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATEC, LUSTAT, DF_A4208 Electricity imports and exports by country"
IMPORTS = ["L01", "SL01", "SL02", "SL03", "SSL01", "SSL02"]
EXPORTS = ["L02", "SL04", "SL05", "SL06"]
CODES = IMPORTS + EXPORTS
TOL = 0.5  # GWh
X_COLS = []


def parse(content):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    for c in ("STRUCTURE_ID", "FREQ", "UNIT", "SPECIFICATION", "Specification", "TIME_PERIOD", "OBS_VALUE"):
        if c not in d.columns:
            raise RuntimeError(f"the service's CSV lacks {c}")
    if set(d.STRUCTURE_ID) != {"LU1:DF_A4208(1.0)"} or set(d.FREQ) != {"A"}:
        raise RuntimeError("not DF_A4208's annual file")
    bad = sorted(set(d.UNIT) - {"A01", "A02", "A03"}) + sorted(set(d.SPECIFICATION) - set(CODES))
    if bad:
        raise RuntimeError(f"a unit or code not expected: {bad}")
    vals, names, missing, seen = {}, {}, 0, set()
    for r in d[d.UNIT == "A03"].itertuples(index=False):
        code, year, v = r.SPECIFICATION, r.TIME_PERIOD, r.OBS_VALUE.strip()
        if not year.isdigit():
            raise RuntimeError(f"a period not a year: {year!r}")
        if (code, year) in seen:
            raise RuntimeError(f"{code} {year} given twice")
        seen.add((code, year))
        names[code] = r.Specification
        if v == "":
            missing += 1
            continue
        try:
            vals[(code, year)] = float(v)
        except ValueError:
            raise RuntimeError(f"{code} {year}: not a number: {v!r}")
    counted = []
    for y in sorted({y for _, y in vals}):
        get = lambda c: vals.get((c, y))
        for parent, kids, stop in (("L01", ["SL01", "SL02", "SL03"], True), ("L02", ["SL04", "SL05", "SL06"], True),
                                   ("SL03", ["SSL01", "SSL02"], False)):
            if get(parent) is None or all(get(k) is None for k in kids):
                continue
            s = sum(get(k) or 0.0 for k in kids)
            if abs(s - get(parent)) > TOL:
                if stop:
                    raise RuntimeError(f"{y} {parent}: its parts make {s:,.3f} GWh, it {get(parent):,.3f}")
                counted.append((y, parent, round(s - get(parent), 1)))
    return vals, names, missing, counted


def frame(vals, names, base):
    rows = [dict(entity=f"statec_trade:lu:{c.lower()}", variable="electricity_imports" if c in IMPORTS else "electricity_exports",
                 ts_utc=f"{y}-01-01T00:00:00Z", value=round(x * 1000.0, 3), unit="MWh", freq="P1Y", geo="LU", market="",
                 node=f"{c} {names[c]}", **base) for (c, y), x in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="STATEC DF_A4208: Luxembourg's electricity imports and exports by country a year")
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
        for y, p, dd in counted:
            log(f"  {p} less its parts: {-dd:+.1f} GWh in {y}, kept as STATEC publishes it")
        t = frame(vals, names, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        imp = {k[:4]: v for k, v in t[t.entity == "statec_trade:lu:l01"].set_index("ts_utc").value.items()}
        exp = {k[:4]: v for k, v in t[t.entity == "statec_trade:lu:l02"].set_index("ts_utc").value.items()}
        head = [
            "Energy Research Warehouse (ERW): STATEC, LUSTAT DF_A4208 Electricity imports and exports by country: Luxembourg's "
            f"electricity imports by origin and exports by destination, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2776)",
            "Shape: series (docs/datastandard.md v0). entity statec_trade:lu:<STATEC's code, lower-cased>; variable "
            "electricity_imports or electricity_exports; unit MWh (the GWh rows, times 1,000); ts_utc the year's first day; freq "
            "P1Y; geo LU; node the code and STATEC's label. l01 = sl01..sl03 (from Belgium, France, Germany); l02 = sl04..sl06 (to "
            "Belgium, France, Germany's RWE grid); sl03 = ssl01 (SEO) + ssl02 (others) where split.",
            f"{len(t)} rows; imports and exports, MWh: " + ", ".join(f"{y} {imp[y]:,.0f} and {exp[y]:,.0f}" for y in ("1990", "2024")
                                                                    if y in imp and y in exp)
            + f". {missing} observations not available have no row; imports and exports checked against their countries every "
            f"year; Germany's split differs in {len(counted)} years (" + ", ".join(y for y, _, _ in counted)
            + "), kept as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statec_electricity_trade.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the data explorer: {PAGE})",
            "License: CC0 1.0 (STATEC's legal notice, https://statistiques.public.lu/en/support/notice.html). Credit, as STATEC's "
            "guidelines ask: STATEC, LUSTAT DF_A4208; GWh written as MWh by the ERW.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; counted {counted}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="STATEC (Luxembourg)",
                                    report="LUSTAT DF_A4208 Electricity imports and exports by country", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
