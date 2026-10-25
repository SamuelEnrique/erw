#!/usr/bin/env python3
"""Luxembourg's electricity sector statistics, as the Institut Luxembourgeois de Regulation (ILR, the regulator) publishes
them on the national open data portal: the electricity withdrawn each month by class of customer, the customers at the
year's end, and by source of energy a year the installed capacity, the volume injected, the national production, the
installations connected and the self-consumers' figures, with the imports and exports by neighbour (session 2392,
chain 113: a source of the session's own choosing; the ERW held Luxembourg only in Eurostat's and Ember's tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ilr_luxembourg_electricity.csv, from the
data set "Donnees statistiques du secteur d'electricite (ILR)" (no key):

    https://data.public.lu/api/1/datasets/667bbcc61ceeb0f9faecfd4b/    the data set's record: its xlsx resource's address
    https://download.data.public.lu/resources/donnees-statistiques-du-secteur-delectricite-ilr/<stamp>/...xlsx

The workbook ("Tableau de bord du secteur d'electricite") has one sheet a subject; each block a title row, a header row of
years or months, then one row a class or a source. The blocks taken (BLOCKS below):

    sheet 1   customers at 31 December by class (count, P1Y); electricity withdrawn by class, kWh, each month (P1M)
    sheet 2   by source: installed capacity (kW), volume injected (kWh), connections (count), national production (kWh)
    sheet 3   self-consumers and sharing groups by source: number, installed capacity, volume self-consumed or shared,
              volume injected
    sheet 7   imports and exports by neighbour, a year (kWh)

    entity      ilr:lu:<block's class, source or neighbour as a slug> ("total" for ILR's own totals)
    variable    the block (customers, withdrawal, capacity, injection, connections, generation, self_consumers,
                self_consumption_capacity, self_consumption, self_consumer_injection, import, export)
    unit        MWh for energy (kWh / 1,000), MW for capacity (kW / 1,000), count for numbers
    ts_utc      the month's or the year's first day; freq P1M or P1Y; geo LU
    node        the class, source or neighbour as ILR names it; x_block the sheet and the block's title; x_status
                "provisional" for a month of the year ILR calls provisional (its note on sheet 1), else blank

Totals and parts are ILR's: a sum takes one level. A blank cell has no row; nothing is filled. Not taken, and said in the
header: sheet 7's monthly import and export, whose October to December 2025 run the other way from the annual totals
(the annual import from Germany equals the monthly imports to September plus the monthly exports from October; session
2392), the battery sheet (power in kVA), the shares, switching rates, prices and the planning sheet. A block whose title
is not found, a header that is not years or months, a value that is not a number, or a row given twice stops the run.

    python warehouse/connectors/ilr_luxembourg_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests a run (the record, then the workbook), saved in warehouse/raw/ilr_electricity/; --offline asks
nothing. data.public.lu has no robots file (HTTP 404) and download.data.public.lu's allows every path (session 2392).
License: CC BY (the data set's licence field, "cc-by"): public, with ILR named.
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import traceback
import unicodedata

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ilr_luxembourg_electricity"
CONNECTOR = "ilr_electricity"
SOURCE = "ilr:donnees-statistiques-electricite"
HOSTS = ("data.public.lu", "download.data.public.lu")
RECORD = "https://data.public.lu/api/1/datasets/667bbcc61ceeb0f9faecfd4b/"
PAGE = "https://data.public.lu/fr/datasets/donnees-statistiques-du-secteur-delectricite-ilr/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MONTHS = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
# (sheet's number, the block's title as it begins, variable, unit as ILR gives it, the block's form)
BLOCKS = [
    ("1.", "Nombre de clients au 31/12", "customers", "count", "classes_by_year"),
    ("1.", "Electricité prélevée en kWh", "withdrawal", "kWh", "monthly"),
    ("2.", "Puissance installée par source", "capacity", "kW", "years"),
    ("2.", "Volume injecté en kWh", "injection", "kWh", "years"),
    ("2.", "Nombre de raccordement", "connections", "count", "years"),
    ("2.", "Production nationale en kWh", "generation", "kWh", "years"),
    ("3.", "Nombre d'autoconsommateurs", "self_consumers", "count", "years"),
    ("3.", "Puissance installée des autoconsommateurs", "self_consumption_capacity", "kW", "years"),
    ("3.", "Volume autoconsommée ou partagé", "self_consumption", "kWh", "years"),
    ("3.", "Volume injecté des autoconsommateurs", "self_consumer_injection", "kWh", "years"),
    ("7.", "Données annuelles: Import - Export", "trade", "kWh", "trade"),
]
UNITS = {"kWh": ("MWh", 1e-3), "kW": ("MW", 1e-3), "count": ("count", 1.0)}
X_COLS = ["x_block", "x_status"]


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def text(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def year_of(v):
    t = text(v)
    return int(t) if re.fullmatch(r"(19|20)\d\d", t) else None


def num(v, where):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise RuntimeError(f"{where}: not a number: {v!r}")
    return float(v)


def find(rows, title, sheet):
    hits = [i for i, r in enumerate(rows) if text(r[0]).startswith(title)]
    if len(hits) != 1:
        raise RuntimeError(f"sheet {sheet}: the block {title!r} found {len(hits)} times")
    return hits[0]


def header(rows, i, sheet, title):
    """The first row after the title whose cells after the first are years: {column: year}."""
    for j in range(i + 1, min(i + 6, len(rows))):
        cols = {k: year_of(v) for k, v in enumerate(rows[j]) if k > 0 and v is not None}
        if cols and all(y is not None for y in cols.values()):
            return j, cols
    raise RuntimeError(f"sheet {sheet}: the block {title!r} has no header of years")


def body(rows, j):
    """The rows after the header up to the first blank row or the next title."""
    out = []
    for r in rows[j + 1:]:
        if not any(v is not None for v in r):
            break
        out.append(r)
    return out


def parse(content, base, counts):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    sheets = {ws.title.split(" ")[0]: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    out = []

    def add(variable, unit_in, key, label, ts, freq, value, block, status=""):
        unit, f = UNITS[unit_in]
        out.append(dict(entity=f"ilr:lu:{slug(key)}", variable=variable, ts_utc=f"{ts}T00:00:00Z", value=round(value * f, 6),
                        unit=unit, freq=freq, geo="LU", market="", node=label, **base, x_block=block, x_status=status))

    for sheet, title, variable, unit_in, form in BLOCKS:
        rows = sheets.get(sheet)
        if rows is None:
            raise RuntimeError(f"no sheet {sheet}")
        width = max(len(r) for r in rows)
        rows = [r + [None] * (width - len(r)) for r in rows]
        i = find(rows, title, sheet)
        block = f"{sheet} {text(rows[i][0])}"[:120]
        if form == "monthly":
            note = text(rows[i][1])
            provisional = "année en cours sont provisoires" in note
            j = next((k for k in range(i + 1, min(i + 6, len(rows))) if [slug(v) for v in rows[k][1:13]] == MONTHS), None)
            if j is None:
                raise RuntimeError(f"sheet {sheet}: the block {title!r} has no header of months")
            year, last = None, max(year_of(r[0]) or 0 for r in rows[j + 1:])
            for r in rows[j + 1:]:
                if not any(v is not None for v in r):
                    continue
                if year_of(r[0]) is not None and all(v is None for v in r[1:]):
                    year = year_of(r[0])
                    continue
                if year is None:
                    raise RuntimeError(f"sheet {sheet}: a row before its year: {r[0]!r}")
                label = text(r[0])
                for m in range(12):
                    v = r[1 + m]
                    if v is None:
                        continue
                    add(variable, unit_in, label, label, f"{year}-{m + 1:02d}-01", "P1M", num(v, f"{block} {year}-{m + 1:02d} {label}"),
                        block, "provisional" if provisional and year == last else "")
        elif form == "classes_by_year":
            j = i + 1 + next(k for k, r in enumerate(rows[i + 1:i + 6]) if any(v is not None for v in r))
            names = {k: text(v) for k, v in enumerate(rows[j]) if k > 0 and v is not None}
            if not names:
                raise RuntimeError(f"sheet {sheet}: the block {title!r} has no header of classes")
            for r in body(rows, j):
                year = year_of(r[0])
                if year is None:
                    raise RuntimeError(f"sheet {sheet}: {title!r}: a row that is not a year: {r[0]!r}")
                for k, label in names.items():
                    if r[k] is not None:
                        add(variable, unit_in, label, label, f"{year}-01-01", "P1Y", num(r[k], f"{block} {year} {label}"), block)
        elif form == "years":
            j, cols = header(rows, i, sheet, title)
            for r in body(rows, j):
                label = text(r[0])
                for k, year in cols.items():
                    if r[k] is not None:
                        add(variable, unit_in, label, label, f"{year}-01-01", "P1Y", num(r[k], f"{block} {year} {label}"), block)
        elif form == "trade":
            j, cols = header(rows, i, sheet, title)
            direction = None
            for r in body(rows, j):
                label = text(r[0])
                if all(v is None for v in r[1:]) and label in ("Export", "Import"):
                    direction = label.lower()
                    continue
                if direction is None:
                    raise RuntimeError(f"sheet {sheet}: a neighbour before Import or Export: {label!r}")
                for k, year in cols.items():
                    if r[k] is not None:
                        add(direction, unit_in, label, label, f"{year}-01-01", "P1Y", num(r[k], f"{block} {year} {direction} {label}"), block)
            counts["sheet 7's monthly import and export not taken"] = 1
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the workbook")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        dup = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)].head(4)[["entity", "variable", "ts_utc"]].values.tolist()
        raise RuntimeError(f"a row given twice: {dup}")
    return t


def xlsx_of(record):
    d = json.loads(record.decode("utf-8") if isinstance(record, bytes) else record)
    xs = [r for r in d.get("resources", []) if str(r.get("format", "")).lower() == "xlsx" or str(r.get("url", "")).endswith(".xlsx")]
    if len(xs) != 1:
        raise RuntimeError(f"the data set's record lists {len(xs)} xlsx resources")
    return xs[0]["url"], d.get("license", "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ILR: Luxembourg's electricity sector statistics")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or any(ip.paused_host(h) for h in HOSTS):
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
        record, _ = ip.fetch_raw(CONNECTOR, RECORD, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        url, licence = xlsx_of(record)
        if licence != "cc-by":
            raise RuntimeError(f"the data set's licence is {licence!r}, not cc-by: the table's license is to be read again")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        t = parse(content, base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t.sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)[cols]
        m = t[t.freq == "P1M"]
        head = [
            "Energy Research Warehouse (ERW): ILR (Institut Luxembourgeois de Regulation), Luxembourg's electricity sector statistics, "
            f"{t.ts_utc.min()[:4]} to {t.ts_utc.max()[:7]} (session 2392)",
            "Shape: series (docs/datastandard.md v0). entity ilr:lu:<class, source or neighbour>; variable the block; unit MWh (kWh / 1,000), MW (kW / 1,000) or count; "
            "ts_utc the month's or the year's first day (customers: at 31 December of the year); freq P1M or P1Y; geo LU; node ILR's label; x_block the sheet and block; "
            "x_status provisional for the current year's months. Totals and parts are ILR's: a sum takes one level.",
            f"{len(t)} rows: " + ", ".join(f"{v} {n}" for v, n in t.variable.value_counts().sort_index().items())
            + f"; monthly withdrawals {m.ts_utc.min()[:7]} to {m.ts_utc.max()[:7]}. A blank has no row; nothing is filled.",
            "Not taken: sheet 7's monthly import and export (October to December 2025 run the other way from the annual totals), the battery sheet (kVA), "
            "the shares, switching rates, prices and the planning sheet.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ilr_luxembourg_electricity.py; the workbook retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} ILR, Donnees statistiques du secteur d'electricite (Tableau de bord), data.public.lu, {PAGE}",
            f"  access: {RECORD} (the record), {url}",
            "License: CC BY (the data set's licence on data.public.lu, cc-by); attribution: Institut Luxembourgeois de Regulation (ILR).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Institut Luxembourgeois de Regulation (ILR)",
                                    report="Donnees statistiques du secteur d'electricite (data.public.lu)", report_url=PAGE,
                                    document_list=RECORD, license="public", tables=[NAME])])  # CC BY
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
