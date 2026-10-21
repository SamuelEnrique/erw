#!/usr/bin/env python3
"""EIA-861M: each sampled utility's retail sales, revenue and customers by state and sector, a month (session 511).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia861m_utility_sales_monthly.csv, from the
U.S. Energy Information Administration's Form EIA-861M monthly files (sales_ult_cust_<year>.xlsx, sheets
"Sales Ultimate Cust. -States" and "-Territory"):

    page   https://www.eia.gov/electricity/data/eia861m/
    file   https://www.eia.gov/electricity/data/eia861m/xls/sales_ult_cust_<year>.xlsx   (the current year; earlier
           years under archive/xls/)

    entity    eia861m:<utility number>:<state>, a utility of EIA's monthly sample in one state
    variable  <sector>_sales (MWh), <sector>_revenue (USD; EIA's thousand dollars times 1,000), <sector>_customers
              (count), for the sectors residential, commercial, industrial, transportation and total
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US-<state>; node the utility's name
    x_*       EIA's own fields: utility number, state, ownership, data status (Preliminary or Final)

Real data only: the form is a monthly sample. EIA estimates the utilities outside it as one row a state, "State
Adjustment <year>", and adds "State Total" and "US Total" rows that hold those estimates; none of the three is a utility
and none is taken. A sampled utility's figures are its own report. Every column is found by its heading (session 495's
lesson); a cell EIA leaves blank or "." has no row; a key given twice stops the run.

    python warehouse/connectors/eia861m_sales.py                 # 2025 and the current year
    python warehouse/connectors/eia861m_sales.py --years 2026    # the years asked
    python warehouse/connectors/eia861m_sales.py --offline       # from warehouse/raw/eia861m/ only, no request

Ceiling: six requests a run (the page and a file a year; a file already in warehouse/raw/eia861m/ is reused). License:
public (EIA: "U.S. government publications are in the public domain", record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Form EIA-861M").
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

NAME = "eia861m_utility_sales_monthly"
CONNECTOR = "eia861m"
SOURCE = "eia:eia861m"
PAGE = "https://www.eia.gov/electricity/data/eia861m/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SECTORS = ["residential", "commercial", "industrial", "transportation", "total"]
MEASURES = [("revenue", "USD", 1000.0), ("sales", "MWh", 1.0), ("customers", "count", 1.0)]
NOT_UTILITIES = re.compile(r"^(state adjustment|state total|us total)", re.I)
CEILING = 6
X_COLS = ["x_utility_number", "x_state", "x_ownership", "x_data_status"]
CHARACTERISTICS = {"year": "year", "month": "month", "utility number": "utility", "utility name": "name", "state": "state",
                   "ownership": "ownership", "data status": "status"}


def file_urls(page_html, years):
    """{year: the file's address}, as the page links sales_ult_cust_<year>.xlsx; a year it does not link stops the run."""
    links = {int(y): PAGE + href.lstrip("./") for href, y in re.findall(r'href="((?:\./)?(?:archive/)?xls/sales_ult_cust_(\d{4})\.xlsx)"', page_html)}
    missing = [y for y in years if y not in links]
    if missing:
        raise RuntimeError(f"the EIA-861M page links no sales_ult_cust file for {missing}")
    return {y: links[y] for y in years}


def columns(frame):
    """The sheet's columns by their headings (its first three rows). Returns ({characteristic: column},
    {(sector, measure): column}); a characteristic or a sector's measure missing stops the run."""
    chars, figs, sector = {}, {}, None
    for c in range(frame.shape[1]):
        top, mid, low = ("" if pd.isna(frame.iloc[r, c]) else str(frame.iloc[r, c]).strip() for r in range(3))
        if top.upper() in {s.upper() for s in SECTORS}:
            sector = top.lower()
        name = low.lower()
        if name in CHARACTERISTICS:
            chars[CHARACTERISTICS[name]] = c
            continue
        measure = {"revenue": "revenue", "revenues": "revenue", "sales": "sales", "customers": "customers"}.get(mid.lower())
        if sector and measure:
            figs[(sector, measure)] = c
    missing = [k for k in CHARACTERISTICS.values() if k not in chars]
    missing += [f"{s}_{m}" for s in SECTORS for m, _, _ in MEASURES if (s, m) not in figs]
    if missing:
        raise RuntimeError(f"the sheet's headings lack {missing}")
    return chars, figs


def sheet_rows(frame, year, url, retrieved):
    """One sheet, its three heading rows included, as the table's rows: sampled utilities only, a row a figure."""
    ch, figs = columns(frame)
    d = frame.iloc[3:]
    d = d[pd.to_numeric(d[ch["year"]], errors="coerce").eq(year)]
    d = d[~d[ch["name"]].astype(str).str.strip().str.match(NOT_UTILITIES)]
    text = lambda r, k: "" if pd.isna(r[ch[k]]) else str(r[ch[k]]).strip()  # noqa: E731
    out = []
    for _, r in d.iterrows():
        util, state, month = int(r[ch["utility"]]), text(r, "state"), int(r[ch["month"]])
        base = dict(entity=f"eia861m:{util}:{state}", ts_utc=f"{year}-{month:02d}-01T00:00:00Z", freq="P1M", geo=f"US-{state}",
                    market="", node=text(r, "name"), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                    x_utility_number=str(util), x_state=state, x_ownership=text(r, "ownership"), x_data_status=text(r, "status"))
        for sector in SECTORS:
            for measure, unit, scale in MEASURES:
                v = pd.to_numeric(r[figs[(sector, measure)]], errors="coerce")
                if pd.isna(v):
                    continue
                out.append(dict(base, variable=f"{sector}_{measure}", value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{year}: an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861M sampled utilities' monthly sales, revenue and customers by state and sector")
    ap.add_argument("--years", type=int, nargs="+", help="the data years (default: 2025 and the current year)")
    ap.add_argument("--offline", action="store_true", help="the page and the files from warehouse/raw only, no request")
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
        years = args.years or [2025, dt.datetime.now(dt.timezone.utc).year]
        if len(years) + 1 > CEILING:
            raise RuntimeError(f"{len(years)} years and the page would pass the ceiling of {CEILING} requests")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, offline=args.offline, headers=UA)
        urls = file_urls(page.decode("utf-8", errors="replace"), years)
        frames, vintages = [], []
        for y, url in urls.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
            if content[:2] != b"PK":
                raise RuntimeError(f"{url} is not a workbook")
            vintages.append(f"{y}: {rec.get('last_modified') or 'no Last-Modified'}")
            retrieved = rec.get("retrieved_at") or ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            book = pd.ExcelFile(io.BytesIO(content))
            for sheet in book.sheet_names:
                t = sheet_rows(pd.read_excel(book, sheet_name=sheet, header=None), y, url, retrieved)
                log(f"{y} {sheet}: {len(t):,} rows, {t['x_utility_number'].nunique() if len(t) else 0} utilities")
                frames.append(t)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in two sheets")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): Form EIA-861M, each sampled utility's retail sales, revenue and customers by state and sector, a month (session 511)",
            "Shape: series (docs/datastandard.md v0). entity eia861m:<utility number>:<state>; variable <sector>_sales (MWh), <sector>_revenue (USD, EIA's thousand dollars times 1,000) "
            "or <sector>_customers (count); ts_utc the month's first day; freq P1M; node the utility's name; x_* EIA's own fields.",
            f"The monthly sample's utilities only: EIA's State Adjustment (its estimate of the utilities outside the sample), State Total and US Total rows are not taken. Months {span}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861m_sales.py; files' Last-Modified {'; '.join(vintages)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861M, sales to ultimate customers, {PAGE}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861M").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861M, monthly sales to ultimate customers", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities, {span}")
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
