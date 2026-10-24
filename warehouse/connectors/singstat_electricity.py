#!/usr/bin/env python3
"""Singapore's electricity generation a month, and its generation and consumption by sector a year, as the Singapore
Department of Statistics publishes them in SingStat Table Builder (tables M890831 and M890841) (session 2308, chain 106:
the Energy Market Authority's own site, www.ema.gov.sg, answers an Incapsula bot challenge, and data.gov.sg's API lists
its datasets only page by page).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/singstat_singapore_electricity.csv, from
Table Builder's API (no key), one GET a table:

    https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890831   "Electricity Generation, Monthly"
    https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890841   "Electricity Generation And Consumption, Annual"

    entity      singstat:sg
    variable    the row's name in snake case, its table's code before it (m890831_<row>, m890841_<row>); node the row as
                SingStat writes it; x_table the table; x_series SingStat's series number (1, 1.1, ...)
    unit        MWh when the row's unit is GWh (times 1,000), else the row's own unit as given; ts_utc the month's or the
                year's first day; freq P1M or P1Y; geo SG

Every row of the two tables is taken; each table's own rows only (its totals are SingStat's, never sums made here). A
cell SingStat leaves blank, "na" or "-" has no row; nothing is filled. A table answered without rows, a column key that
is not a month ("2026 Aug") or a year ("2025"), a value that is not a number, a unit other than GWh (SingStat writes "Gigawatt Hours"),
or a row and period given twice stops the run. The vintage is each table's "dataLastUpdated".

    python warehouse/connectors/singstat_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests a run, each saved in warehouse/raw/singstat_electricity/ and fetched again unless --offline.
tablebuilder.singstat.gov.sg's robots file allows every path; www.singstat.gov.sg's asks a crawl delay of 2 seconds
(session 2308). License: public (session 2537). SingStat's terms of use, whose text the page holds in a script: "Use of
Datasets made available through the Services is subject to the terms of the Singapore Open Data Licence"; its clause 10
allows copying, distribution and derived products, for sale or otherwise, with the source credited; the header credits it.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "singstat_singapore_electricity"
CONNECTOR = "singstat_electricity"
SOURCE = "singstat:M890831_M890841"
HOST = "tablebuilder.singstat.gov.sg"
API = "https://tablebuilder.singstat.gov.sg/api/table/tabledata/"
PAGE = "https://tablebuilder.singstat.gov.sg/table/TS/M890831"
TABLES = {"M890831": "P1M", "M890841": "P1Y"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MONTHS = {m: i + 1 for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
BLANK = {"", "na", "-", "n.a.", "..", "x"}
GWH = {"GWh", "Gigawatt Hours"}   # the unit as SingStat names it (session 2308)
X_COLS = ["x_table", "x_series"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def period(key, freq):
    k = key.strip()
    if freq == "P1M":
        m = re.fullmatch(r"(\d{4}) ([A-Z][a-z]{2})", k)
        if not m or m.group(2) not in MONTHS:
            raise RuntimeError(f"a monthly column key not of the form 'YYYY Mon': {key!r}")
        return f"{m.group(1)}-{MONTHS[m.group(2)]:02d}-01T00:00:00Z"
    if not re.fullmatch(r"\d{4}", k):
        raise RuntimeError(f"an annual column key not a year: {key!r}")
    return f"{k}-01-01T00:00:00Z"


def parse(content, table, base):
    d = json.loads(content.decode("utf-8-sig") if isinstance(content, bytes) else content)
    data = d.get("Data") or {}
    rows = data.get("row") or []
    if not rows:
        raise RuntimeError(f"{table}: an answer without rows")
    freq = TABLES[table]
    out = []
    for r in rows:
        name = (r.get("rowText") or "").strip()
        unit = (r.get("uoM") or "").strip()
        if unit not in GWH:
            raise RuntimeError(f"{table}: {name!r} in {unit!r}, not GWh")
        for c in r.get("columns") or []:
            v = str(c.get("value", "")).strip()
            if v.lower() in BLANK:
                continue
            try:
                x = float(v.replace(",", ""))
            except ValueError:
                raise RuntimeError(f"{table}: {name!r} {c.get('key')!r}: not a number: {v!r}")
            out.append(dict(entity="singstat:sg", variable=f"{table.lower()}_{slug(name)}", ts_utc=period(c["key"], freq),
                            value=round(x * 1000, 3), unit="MWh", freq=freq, geo="SG", market="", node=name, **base,
                            x_table=table, x_series=str(r.get("seriesNo", ""))))
    return out


def updated(content):
    """The table's dataLastUpdated (dd/mm/yyyy) as an ISO time at 00:00Z, the rows' vintage; blank when it is not of that form."""
    d = json.loads(content.decode("utf-8-sig") if isinstance(content, bytes) else content)
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", str((d.get("Data") or {}).get("dataLastUpdated", "")).strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}T00:00:00Z" if m else ""


def main(argv=None):
    ap = argparse.ArgumentParser(description="SingStat Table Builder M890831 and M890841: Singapore's electricity generation and consumption")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
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
        rows, got = [], []
        for table in TABLES:
            url = API + table
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=updated(content))
            rows += parse(content, table, base)
            got.append(f"{table} {base['retrieved_at']}")
        t = pd.DataFrame(rows)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row and period given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): Singapore Department of Statistics, SingStat Table Builder M890831 (Electricity Generation, Monthly) "
            f"and M890841 (Electricity Generation And Consumption, Annual), {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2308)",
            "Shape: series (docs/datastandard.md v0). entity singstat:sg; variable <table>_<row in snake case>; unit MWh (the tables' GWh times "
            "1,000); ts_utc the month's or year's first day; freq P1M (M890831) or P1Y (M890841); geo SG; node the row as SingStat writes it; "
            "x_table the table; x_series SingStat's series number.",
            f"{len(t)} rows, {t.variable.nunique()} series. Every row of both tables is taken; a blank cell has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/singstat_electricity.py; the requests retrieved {'; '.join(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Singapore Department of Statistics, SingStat Table Builder, {PAGE}",
            f"  access: {API}<table>",
            "License: public (session 2537). SingStat's terms of use put its datasets under the Singapore Open Data Licence "
            "(https://data.gov.sg/open-data-licence) and grant a free, worldwide, revocable and non-exclusive right to copy and distribute the "
            "Contents and to derive products from them, for sale or otherwise, the source credited and no analysis presented as the "
            "Government's. Source: Singapore Department of Statistics (SingStat), SingStat Table Builder; the figures are SingStat's, scaled "
            "from GWh to MWh.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} series, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Singapore Department of Statistics (SingStat)",
                                    report="Table Builder M890831 and M890841: electricity generation, monthly; generation and consumption, annual",
                                    report_url=PAGE, document_list=API + "M890831", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
