#!/usr/bin/env python3
"""Austria's monthly electricity statistics, as E-Control (Energie-Control Austria, the regulator) publishes them in its
download area: generation by kind, imports and exports by neighbour, consumption, losses, storage content and the
other monthly series of the "Betriebsstatistik" (session 2391, chain 113: a source of the session's own choosing; it adds
trade, consumption and storage to session 2272's hourly public net production of Energy-Charts).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/econtrol_austria_electricity_monthly.csv,
from one CSV (no key), linked from https://www.e-control.at/statistik/e-statistik/data:

    https://www.e-control.at/documents/1785851/8165594/el_dataset_mn.csv   ("Zeitreihen mit monatlichen Daten")

The file is wide: one column a series, described by its metadata rows (TS_ID, ZA, KOMP, Gliederung1 to 3, VO, REG, N,
EHB, KAT, UNIT), then one row a month ("YYYY-MM"), semicolon-separated with decimal commas.

    entity      econtrol:at:<TS_ID without "#">
    variable    KOMP (the component) in snake case
    unit        as the series' UNIT row gives it, MWh or MW; a series in any other unit (the generation coefficient,
                "[1]") is not taken and is counted
    ts_utc      the month's first day; freq P1M; geo AT
    node        the series' description: KOMP and its breakdowns (Gliederung1 to 3) and its scope (N), as E-Control writes
                them
    x_ts_id, x_breakdown, x_scope, x_category   E-Control's TS_ID, its breakdowns joined, N and KAT

Totals and parts are E-Control's: a sum takes one level. A blank cell has no row; nothing is filled. A series the file
gives twice (two columns with one TS_ID) is kept once when the columns are equal; unequal, the run stops. The file is
read as UTF-8, else as Windows-1252 (the encoding E-Control served in session 2391). A metadata row
missing, a month not of the form YYYY-MM, a value that is not a number, or a series and month given twice stops the run.

    python warehouse/connectors/econtrol_austria_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/econtrol_electricity/ and fetched again unless --offline. E-Control's
robots file closes its services, login and /home paths only (session 2391). License: not settled. The site carries
"Copyright 2026 © E-Control" and grants no reuse; internal until a ruling or a reuse statement is read.
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback
import unicodedata

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "econtrol_austria_electricity_monthly"
CONNECTOR = "econtrol_electricity"
SOURCE = "econtrol:el_dataset_mn"
HOST = "www.e-control.at"
URL = "https://www.e-control.at/documents/1785851/8165594/el_dataset_mn.csv"
PAGE = "https://www.e-control.at/statistik/e-statistik/data"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
META = ["TS_ID", "ZA", "KOMP", "Gliederung1", "Gliederung2", "Gliederung3", "VO", "REG", "N", "EHB", "KAT", "UNIT"]
UNITS = {"MWh": "MWh", "MW": "MW"}
X_COLS = ["x_ts_id", "x_breakdown", "x_scope", "x_category"]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def number(v):
    return float(v.strip().replace(".", "").replace(",", ".")) if "," in v else float(v.strip())


def parse(content, base, counts):
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("cp1252")      # the file E-Control serves is in Windows-1252 (session 2391)
    else:
        text = content
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    meta = {r[0].strip(): r[1:] for r in rows if r and r[0].strip() in META}
    missing = [m for m in META if m not in meta]
    if missing:
        raise RuntimeError(f"metadata rows missing: {missing}")
    n = len(meta["TS_ID"])
    series, first = [], {}
    data = [r for r in rows if r and re.fullmatch(r"\d{4}-\d\d", r[0].strip())]
    for j in range(n):
        tsid = meta["TS_ID"][j].strip()
        if tsid in first:      # a series given twice in the file: kept once, and only if the two columns are equal
            if [r[j + 1] if j + 1 < len(r) else "" for r in data] != [r[first[tsid] + 1] if first[tsid] + 1 < len(r) else "" for r in data]:
                raise RuntimeError(f"series {tsid} is given twice with different values")
            counts["series given twice, kept once"] = counts.get("series given twice, kept once", 0) + 1
            series.append(None)
            continue
        first[tsid] = j
        unit = meta["UNIT"][j].strip()
        if unit not in UNITS:
            counts[f"series in {unit or 'no unit'} not taken"] = counts.get(f"series in {unit or 'no unit'} not taken", 0) + 1
            series.append(None)
            continue
        parts = [meta[k][j].strip() for k in ("Gliederung1", "Gliederung2", "Gliederung3") if meta[k][j].strip() not in ("", "_")]
        komp = meta["KOMP"][j].strip()
        series.append(dict(ts_id=meta["TS_ID"][j].strip().lstrip("#"), komp=komp, unit=UNITS[unit], breakdown="/".join(parts),
                           scope=meta["N"][j].strip(), category=meta["KAT"][j].strip()))
    out = []
    for r in rows:
        if not r or not re.fullmatch(r"\d{4}-\d\d", r[0].strip()):
            if r and r[0].strip() not in META and r[0].strip() not in ("Header & Timestamp", "aktualisiert") and r[0].strip():
                raise RuntimeError(f"a row neither metadata nor a month: {r[0]!r}")
            continue
        month = r[0].strip()
        if not 1 <= int(month[5:]) <= 12:
            raise RuntimeError(f"a month out of range: {month}")
        for j, s in enumerate(series):
            if s is None or j + 1 >= len(r):
                continue
            v = r[j + 1].strip()
            if not v:
                continue
            try:
                x = number(v)
            except ValueError:
                raise RuntimeError(f"{month} series {s['ts_id']}: not a number: {v!r}")
            node = " | ".join(p for p in (s["komp"], s["breakdown"], s["scope"]) if p)
            out.append(dict(entity=f"econtrol:at:{s['ts_id']}", variable=slug(s["komp"]), ts_utc=f"{month}-01T00:00:00Z", value=round(x, 3),
                            unit=s["unit"], freq="P1M", geo="AT", market="", node=node, **base, x_ts_id=s["ts_id"],
                            x_breakdown=s["breakdown"], x_scope=s["scope"], x_category=s["category"]))
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the file")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a series and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="E-Control: Austria's monthly electricity statistics")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        t = parse(content, base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): E-Control (Energie-Control Austria), monthly electricity statistics (el_dataset_mn), "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2391)",
            "Shape: series (docs/datastandard.md v0). entity econtrol:at:<TS_ID>; variable the component (KOMP) in snake case; unit MWh or MW as the "
            "series gives it; ts_utc the month's first day; freq P1M; geo AT; node the component, its breakdowns and its scope; x_ts_id, x_breakdown, "
            "x_scope, x_category E-Control's codes. Totals and parts are E-Control's: a sum takes one level.",
            f"{len(t)} rows, {t.entity.nunique()} series. Not taken, counted: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none")
            + ". A blank has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/econtrol_austria_electricity.py; the file retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} E-Control, Elektrizitaetsstatistik, Downloadbereich, Zeitreihen mit monatlichen Daten, {PAGE}",
            f"  access: {URL}",
            "License: internal (\"Copyright 2026 © E-Control\"; no reuse statement read).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} series, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; not taken {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="E-Control (Energie-Control Austria)", report="Electricity statistics, monthly time series (el_dataset_mn.csv)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
