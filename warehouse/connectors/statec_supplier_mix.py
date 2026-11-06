#!/usr/bin/env python3
"""The national mix of the electricity provided to Luxembourg's end users each year from 2009 to 2024, by energy source, in
per cent, as STATEC (Luxembourg's national statistics institute) gives it in its LUSTAT dataflow DF_A4209 "National mix of
electricity provided to the end-users (in %)" (session 2785, chain 141, the session's own choice). The suppliers' disclosed mix,
not the generation in Luxembourg (which DF_A4203 gives, `statec_lu_electricity_generation_annual`): most of the electricity
Luxembourg's end users take is imported.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statec_lu_supplier_mix_annual.csv, from one
request to LUSTAT's SDMX service (.Stat Suite, no key), every key of the dataflow as CSV with labels:

    https://lustat.statec.lu/rest/data/LU1,DF_A4209,1.0/all?format=csvfilewithlabels

    entity      statec_mix:lu:<code>, STATEC's SPECIFICATION code lower-cased: l01 fossil, l02 nuclear, l03 renewable and l04
                other and unidentified sources; sl01 to sl04 hard coal, brown coal, natural gas and other fossil energies (oil,
                others); sl05 to sl09 biomass and biogas, wind, hydroelectricity, solar and other renewable sources
    variable    supply_mix_share; unit pct; ts_utc the year's first day; freq P1Y; geo LU; node the code and STATEC's label

Compared every year, within 0.15 percentage points (the shares are rounded to 0.1): the four groups make 100; fossil is sl01 to
sl04; renewable is sl05 to sl09. A difference is counted, listed in the run log and kept as published. A header not the
service's, a frequency or code not expected, a key given twice, a value not a number or outside 0 to 100 stops the run. A missing
observation has no row; nothing is filled.

    python warehouse/connectors/statec_supplier_mix.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statec/ and reused unless --fresh; --offline asks nothing. lustat.statec.lu has
no robots file (session 2785, read 1586). License: STATEC's legal notice (read 1564): CC0 1.0; public.
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

NAME = "statec_lu_supplier_mix_annual"
CONNECTOR = "statec"
SOURCE = "statec:lustat_df_a4209"
HOST = "lustat.statec.lu"
URL = "https://lustat.statec.lu/rest/data/LU1,DF_A4209,1.0/all?format=csvfilewithlabels"
PAGE = "https://lustat.statec.lu/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATEC, LUSTAT, DF_A4209 National mix of electricity provided to the end-users (in %)"
GROUPS = ["L01", "L02", "L03", "L04"]
CODES = GROUPS + ["SL01", "SL02", "SL03", "SL04", "SL05", "SL06", "SL07", "SL08", "SL09"]
SUMS = (("L01", ["SL01", "SL02", "SL03", "SL04"]), ("L03", ["SL05", "SL06", "SL07", "SL08", "SL09"]))
TOL = 0.15
X_COLS = []


def parse(content):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    for c in ("STRUCTURE_ID", "FREQ", "SPECIFICATION", "Specification", "TIME_PERIOD", "OBS_VALUE"):
        if c not in d.columns:
            raise RuntimeError(f"the service's CSV lacks {c}")
    if set(d.STRUCTURE_ID) != {"LU1:DF_A4209(1.0)"} or set(d.FREQ) != {"A"}:
        raise RuntimeError("not DF_A4209's annual file")
    bad = sorted(set(d.SPECIFICATION) - set(CODES))
    if bad:
        raise RuntimeError(f"a code not expected: {bad}")
    vals, names, missing, seen, counted = {}, {}, 0, set(), []
    for r in d.itertuples(index=False):
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
            x = float(v)
        except ValueError:
            raise RuntimeError(f"{code} {year}: not a number: {v!r}")
        if not 0 <= x <= 100:
            raise RuntimeError(f"{code} {year}: a share outside 0 to 100: {x}")
        vals[(code, year)] = x
    for y in sorted({y for _, y in vals}):
        get = lambda c: vals.get((c, y))
        if any(get(g) is not None for g in GROUPS):
            s = sum(get(g) or 0.0 for g in GROUPS)
            if abs(s - 100.0) > TOL:
                counted.append((y, "groups", round(s - 100.0, 2)))
        for parent, kids in SUMS:
            if get(parent) is None or all(get(k) is None for k in kids):
                continue
            s = sum(get(k) or 0.0 for k in kids)
            if abs(s - get(parent)) > TOL:
                counted.append((y, parent, round(s - get(parent), 2)))
    return vals, names, missing, counted


def frame(vals, names, base):
    rows = [dict(entity=f"statec_mix:lu:{c.lower()}", variable="supply_mix_share", ts_utc=f"{y}-01-01T00:00:00Z", value=x,
                 unit="pct", freq="P1Y", geo="LU", market="", node=f"{c} {names[c]}", **base) for (c, y), x in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="STATEC DF_A4209: the mix of electricity provided to Luxembourg's end users, a year")
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
            log(f"  {p} less 100 or its parts: {-dd:+.2f} points in {y}, kept as STATEC publishes it")
        t = frame(vals, names, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        ren = {k[:4]: v for k, v in t[t.entity == "statec_mix:lu:l03"].set_index("ts_utc").value.items()}
        head = [
            "Energy Research Warehouse (ERW): STATEC, LUSTAT DF_A4209: the national mix of the electricity provided to Luxembourg's "
            f"end users by energy source, in per cent, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2785); the suppliers' "
            "disclosed mix, not the generation in Luxembourg",
            "Shape: series (docs/datastandard.md v0). entity statec_mix:lu:<STATEC's code, lower-cased>; variable supply_mix_share; "
            "unit pct; ts_utc the year's first day; freq P1Y; geo LU; node the code and STATEC's label. l01 fossil = sl01..sl04; l03 "
            "renewable = sl05..sl09; l01..l04 make 100.",
            f"{len(t)} rows; the renewable share: " + ", ".join(f"{y} {ren[y]:.1f}" for y in ("2009", "2016", "2024") if y in ren)
            + f". {missing} observations missing have no row; the shares compared with 100 and their groups every year within "
            f"{TOL:g} points, {len(counted)} differences kept as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statec_supplier_mix.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the data explorer: {PAGE})",
            "License: CC0 1.0 (STATEC's legal notice, https://statistiques.public.lu/en/support/notice.html). Credit, as STATEC's "
            "guidelines ask: STATEC, LUSTAT DF_A4209.",
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
                                    report="LUSTAT DF_A4209 National mix of electricity provided to the end-users (in %)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
