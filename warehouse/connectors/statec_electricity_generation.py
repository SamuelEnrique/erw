#!/usr/bin/env python3
"""Luxembourg's electricity generation each year from 1928 to 2024, gross and net, by primary and secondary generation and by
type of plant, as STATEC (Luxembourg's national statistics institute) gives it in its LUSTAT dataflow DF_A4203 "Electricity
generation" (session 2771, chain 140, the session's own choice: a national statistics office the ERW did not hold, beside the
regulator ILR's electricity statistics, held since chain 076).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statec_lu_electricity_generation_annual.csv,
from one request to LUSTAT's SDMX service (.Stat Suite, no key), every key of the dataflow as CSV with labels:

    https://lustat.statec.lu/rest/data/LU1,DF_A4203,1.0/all?format=csvfilewithlabels

The dataflow gives each figure in three units (TJ, ktep and GWh); this table takes the GWh rows (unit A03), so the other two,
the same figures, are not written.

    entity      statec_elec:lu:<code>, STATEC's SPECIFICATION code lower-cased (l01 total gross generation, l02 net generation,
                sl01 gross primary generation, sl02 gross secondary generation, sl03 to sl07 hydro, wind, solar, thermal and
                combined heat and power, ssl01 to ssl05 the same five under primary and secondary generation, sssl01 of which
                pumping, sssl02 siderurgy, sssl03 biogas, sssl04 wood wastes, sssl05 pellets)
    variable    electricity_generation; unit MWh (STATEC's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo LU;
                node the code and STATEC's label

How the codes relate, as the data show it (counted in the header, not assumed): l01 is sl01 plus sl02; sl01 is ssl01 to ssl03;
sl02 is ssl04 and ssl05; l02 is sl03 to sl07 (the plant types net). A missing observation (STATEC's l, not available, z, not
applicable, or n) has no row; nothing is filled.

Checks that stop the run: a header not the service's; a unit, frequency or code not expected; a key given twice; a value not a
number; sl01 not ssl01 to ssl03, or sl02 not ssl04 and ssl05, within 0.5 GWh in a year that gives them. l01 against sl01 and
sl02, and l02 against sl03 to sl07, are counted where they differ (l02 in 1933 in October 2026's file), as STATEC publishes
them; a year with no parts is not compared.

    python warehouse/connectors/statec_electricity_generation.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statec/ and reused unless --fresh; --offline asks nothing.
lustat.statec.lu has no robots file (its address answers the data explorer's page); statistiques.public.lu's closes query strings
and search to * and names no Claude agent (session 2771, reads 1560 and 1561). License: STATEC's legal notice, linked from
LUSTAT (read 1564): published "without restriction, under the terms of the Universal Transfer in the Public Domain Creative
Commons CC0 1.0", with goodwill guidelines asking for the source and the links kept: public.
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

NAME = "statec_lu_electricity_generation_annual"
CONNECTOR = "statec"
SOURCE = "statec:lustat_df_a4203"
HOST = "lustat.statec.lu"
URL = "https://lustat.statec.lu/rest/data/LU1,DF_A4203,1.0/all?format=csvfilewithlabels"
PAGE = "https://lustat.statec.lu/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATEC, LUSTAT, DF_A4203 Electricity generation"
CODES = ["L01", "L02", "SL01", "SL02", "SL03", "SL04", "SL05", "SL06", "SL07", "SSL01", "SSL02", "SSL03", "SSL04", "SSL05",
         "SSSL01", "SSSL02", "SSSL03", "SSSL04", "SSSL05"]
TOL = 0.5  # GWh
X_COLS = []


def parse(content):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    for c in ("STRUCTURE_ID", "FREQ", "UNIT", "SPECIFICATION", "Specification", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS"):
        if c not in d.columns:
            raise RuntimeError(f"the service's CSV lacks {c}: {list(d.columns)[:12]}")
    if set(d.STRUCTURE_ID) != {"LU1:DF_A4203(1.0)"} or set(d.FREQ) != {"A"}:
        raise RuntimeError("not DF_A4203's annual file")
    bad = sorted(set(d.UNIT) - {"A01", "A02", "A03"}) + sorted(set(d.SPECIFICATION) - set(CODES))
    if bad:
        raise RuntimeError(f"a unit or code not expected: {bad}")
    g = d[d.UNIT == "A03"]
    vals, names, missing, seen = {}, {}, 0, set()
    for r in g.itertuples(index=False):
        code, year, v = r.SPECIFICATION, r.TIME_PERIOD, r.OBS_VALUE.strip()
        if not year.isdigit():
            raise RuntimeError(f"a period not a year: {year!r}")
        names[code] = r.Specification
        if (code, year) in seen:
            raise RuntimeError(f"{code} {year} given twice")
        seen.add((code, year))
        if v == "":
            missing += 1
            continue
        try:
            vals[(code, year)] = float(v)
        except ValueError:
            raise RuntimeError(f"{code} {year}: not a number: {v!r}")
    years = sorted({y for _, y in vals})
    counted = []
    for y in years:
        get = lambda c: vals.get((c, y))
        for parent, kids, stop in (("SL01", ["SSL01", "SSL02", "SSL03"], True), ("SL02", ["SSL04", "SSL05"], True),
                                   ("L01", ["SL01", "SL02"], False), ("L02", ["SL03", "SL04", "SL05", "SL06", "SL07"], False)):
            if get(parent) is None or all(get(k) is None for k in kids):
                continue
            s = sum(get(k) or 0.0 for k in kids)
            if abs(s - get(parent)) > TOL:
                if stop:
                    raise RuntimeError(f"{y} {parent}: its parts make {s:,.3f} GWh, it {get(parent):,.3f}")
                counted.append((y, parent, round(s - get(parent), 1)))
    return vals, names, missing, counted


def frame(vals, names, base):
    rows = [dict(entity=f"statec_elec:lu:{c.lower()}", variable="electricity_generation", ts_utc=f"{y}-01-01T00:00:00Z",
                 value=round(x * 1000.0, 3), unit="MWh", freq="P1Y", geo="LU", market="", node=f"{c} {names[c]}", **base)
            for (c, y), x in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="STATEC DF_A4203: Luxembourg's electricity generation a year from 1928")
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
        net = {k[:4]: v for k, v in t[t.entity == "statec_elec:lu:l02"].set_index("ts_utc").value.items()}
        head = [
            "Energy Research Warehouse (ERW): STATEC, LUSTAT DF_A4203 Electricity generation: Luxembourg's gross and net electricity "
            f"generation by primary and secondary generation and plant type, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2771)",
            "Shape: series (docs/datastandard.md v0). entity statec_elec:lu:<STATEC's code, lower-cased>; variable "
            "electricity_generation; unit MWh (the GWh rows, times 1,000; the TJ and ktep rows not written); ts_utc the year's first "
            "day; freq P1Y; geo LU; node the code and STATEC's label. l01 = sl01 + sl02; sl01 = ssl01..ssl03; sl02 = ssl04 + ssl05; "
            "l02 = sl03..sl07 (plant types, net).",
            f"{len(t)} rows; net generation, MWh: " + ", ".join(f"{y} {net[y]:,.0f}" for y in ("1928", "1990", "2024") if y in net)
            + f". {missing} observations not available have no row; sl01 and sl02 checked against their parts every year; "
            f"{len(counted)} years where l01 or l02 differs from its parts kept as published ("
            + ", ".join(f"{p} {y}" for y, p, _ in counted) + "); nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statec_electricity_generation.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the data explorer: {PAGE})",
            "License: CC0 1.0 (STATEC's legal notice, https://statistiques.public.lu/en/support/notice.html). Credit, as STATEC's "
            "guidelines ask: STATEC, LUSTAT DF_A4203; GWh written as MWh by the ERW.",
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
                                    report="LUSTAT DF_A4203 Electricity generation", report_url=PAGE, document_list=URL,
                                    license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
