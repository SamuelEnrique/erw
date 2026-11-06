#!/usr/bin/env python3
"""EIA-861: each utility's retail sales, revenue and customers by state and sector, a year (session 485, the owner's
instruction of 21 October 2026).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia861_utility_sales.csv, from the
U.S. Energy Information Administration's Form EIA-861 annual files (Sales_Ult_Cust_<year>.xlsx in f861<year>.zip,
sheets States and Territories):

    page   https://www.eia.gov/electricity/data/eia861/
    file   https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip   (the newest year; earlier years under archive/zip/)

    entity    eia861:<utility number>:<state>:<part>:<balancing authority code>, a row of EIA's sheet: one utility in one
              state, one part of the form (A bundled service, B energy only, C delivery only, D bundled by a power
              marketer) and one balancing authority (blank when EIA gives none)
    variable  <sector>_sales (MWh), <sector>_revenue (USD; EIA's thousand dollars times 1,000), <sector>_customers
              (count), for the sectors residential, commercial, industrial, transportation and total
    ts_utc    the data year's 1 January at 00:00:00Z; freq P1Y; geo US-<state>; node the utility's name
    x_*       EIA's own fields: utility number, state, part, service type, ownership, balancing authority, data type

Real data only: EIA marks each row O (observed) or I (imputed: the short-form utilities it estimates). Only observed
rows are taken. EIA's two aggregates are not utilities and are left out: 88888 ("Withheld", the retail power marketers
it does not name) and 99999 ("Adjustment <year>", imputed). A cell EIA leaves as "." has no row. A key repeated after
that stops the run.

    python warehouse/connectors/eia861_sales.py               # the newest year the page links
    python warehouse/connectors/eia861_sales.py --year 2024   # an earlier year, merged on (entity, variable, ts_utc)

Ceiling: two requests a year (the page and the zip; a zip already in warehouse/raw/eia861/ is reused). License: public
(EIA: "U.S. government publications are in the public domain", read 12 October 2026, record 1 of license_reads.csv;
cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia861_utility_sales"
CONNECTOR = "eia861"
SOURCE = "eia:eia861"
PAGE = "https://www.eia.gov/electricity/data/eia861/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SECTORS = ["residential", "commercial", "industrial", "transportation", "total"]
MEASURES = [("revenue", "USD", 1000.0), ("sales", "MWh", 1.0), ("customers", "count", 1.0)]
NOT_UTILITIES = {88888, 99999}
X_COLS = ["x_utility_number", "x_state", "x_part", "x_service_type", "x_ownership", "x_ba_code", "x_data_type"]


def zip_url(page_html, year=None):
    """The zip of the year asked, or of the newest year, as the page links it."""
    links = sorted(set(re.findall(r'href="((?:archive/)?zip/f861(\d{4})\.zip)"', page_html)), key=lambda x: x[1])
    if not links:
        raise RuntimeError("the EIA-861 page links no f861<year>.zip")
    pick = [l for l in links if year is None or int(l[1]) == year]
    if not pick:
        raise RuntimeError(f"the EIA-861 page links no zip for {year}")
    href, y = pick[-1]
    return PAGE + href, int(y)


CHARACTERISTICS = {"data year": "year", "utility number": "utility", "utility name": "name", "part": "part",
                   "service type": "service", "data type": "data_type", "state": "state", "ownership": "ownership",
                   "ba code": "ba", "ba_code": "ba"}


def columns(frame):
    """Session 495: the sheet's columns by their headings (its first three rows), not by position. 2019's sheet holds a
    "Short Form" column the other years do not, which a positional read shifted into every figure. Returns
    ({characteristic: column}, {(sector, measure): column}); a heading not understood is left out, and a characteristic
    or a sector's measure missing stops the run."""
    chars, figs, sector = {}, {}, None
    for c in range(frame.shape[1]):
        top, mid, low = (str(frame.iloc[r, c]).strip() for r in range(3))
        if top.upper() in {s.upper() for s in SECTORS}:
            sector = top.lower()
        name = low.split(chr(10))[0].strip().lower()   # "Data Type", before EIA's note on the next lines
        if name in CHARACTERISTICS:
            chars[CHARACTERISTICS[name]] = c
            continue
        m = mid.lower()
        measure = {"revenues": "revenue", "revenue": "revenue", "sales": "sales", "customers": "customers"}.get(m)
        if sector and measure:
            figs[(sector, measure)] = c
    missing = [k for k in ("year", "utility", "name", "part", "service", "data_type", "state", "ownership", "ba") if k not in chars]
    missing += [f"{s}_{m}" for s in SECTORS for m, _, _ in MEASURES if (s, m) not in figs]
    if missing:
        raise RuntimeError(f"the sheet's headings lack {missing}")
    return chars, figs


def sheet_rows(frame, year, url, retrieved):
    """One sheet (States or Territories), its three heading rows included, as the table's rows: observed utilities only,
    a row a figure, every column found by its heading."""
    ch, figs = columns(frame)
    d = frame.iloc[3:]
    d = d[pd.to_numeric(d[ch["year"]], errors="coerce").eq(year)]
    d = d[d[ch["data_type"]].astype(str).str.strip().eq("O")]
    d = d[~pd.to_numeric(d[ch["utility"]], errors="coerce").isin(NOT_UTILITIES)]
    text = lambda r, k: "" if pd.isna(r[ch[k]]) else str(r[ch[k]]).strip()  # noqa: E731
    out = []
    for _, r in d.iterrows():
        util, state, part, ba = int(r[ch["utility"]]), text(r, "state"), text(r, "part"), text(r, "ba")
        base = dict(entity=f"eia861:{util}:{state}:{part}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y", geo=f"US-{state}",
                    market="", node=text(r, "name"), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                    x_utility_number=str(util), x_state=state, x_part=part, x_service_type=text(r, "service"),
                    x_ownership=text(r, "ownership"), x_ba_code=ba, x_data_type="O")
        for sector in SECTORS:
            for measure, unit, scale in MEASURES:
                v = pd.to_numeric(r[figs[(sector, measure)]], errors="coerce")
                if pd.isna(v):      # "." in EIA's sheet: no value, no row
                    continue
                out.append(dict(base, variable=f"{sector}_{measure}", value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{year}: an (entity, variable, ts_utc) is given twice")
    return t


def years_held(path, year):
    """Session 690: the data years the table will hold once this run's year is merged in: the years of the file as it
    stands (its rows read whole, the header skipped by its leading "#" and never cut at a "#" inside a row: the names
    "Vera Irrigation District #15" and "Maricopa County M W C Dist #1" hold one) and this run's."""
    years = {year}
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            rows = csv.reader(ln for ln in f if not ln.startswith("#"))
            i = next(rows).index("ts_utc")
            years |= {int(r[i][:4]) for r in rows if r}
    return sorted(years)


def held_text(years):
    """'2015 to 2025' for a run of years without a gap, else the years listed."""
    if years == list(range(years[0], years[-1] + 1)):
        return f"{years[0]} to {years[-1]}" if len(years) > 1 else str(years[0])
    return ", ".join(str(y) for y in years)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utility sales, revenue and customers by state and sector")
    ap.add_argument("--year", type=int, help="the data year (default: the newest the page links)")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=args.year is None, headers=UA)  # a year asked: the saved page is enough
        url, year = zip_url(page.decode("utf-8", errors="replace"), args.year)
        content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
        book = zipfile.ZipFile(io.BytesIO(content)).read(f"Sales_Ult_Cust_{year}.xlsx")
        xl = pd.ExcelFile(io.BytesIO(book))
        sheets = [n for n in ("States", "Territories") if n in xl.sheet_names]
        if "States" not in sheets:
            raise RuntimeError(f"Sales_Ult_Cust_{year}.xlsx has no States sheet: {xl.sheet_names}")
        frames = [sheet_rows(pd.read_excel(xl, n, header=None), year, url, rec["retrieved_at"]) for n in sheets]
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"{year}: a row in both sheets")
        s = s[ip.SERIES_COLS + X_COLS]
        header = [
            "Energy Research Warehouse (ERW): EIA-861 retail sales, revenue and customers, each utility by state, part and sector, a year (session 485)",
            "Shape: series (docs/datastandard.md v0). entity eia861:<utility>:<state>:<part>:<balancing authority>; variables <sector>_sales (MWh), <sector>_revenue (USD, EIA's thousand dollars times 1,000), <sector>_customers (count), sectors residential, commercial, industrial, transportation and total; ts_utc the data year's 1 January; freq P1Y; node the utility's name.",
            f"Years held: {held_text(years_held(os.path.join(ip.OUT_DIR, NAME + '.csv'), year))} (this run wrote {year}; earlier runs' years are kept, merged on entity, variable, ts_utc). Observed rows only: EIA's imputed rows (data type I), its 88888 Withheld and 99999 Adjustment aggregates and its '.' cells are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_sales.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Sales_Ult_Cust), {PAGE}",
            f"  access: {url}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_csv(s, NAME, header, log, cols=ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        utilities = s["x_utility_number"].nunique()
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{year}: {len(s):,} rows, {utilities:,} utilities"))
        print(f"{NAME}: {year}, {len(s):,} rows, {s['entity'].nunique():,} rows of EIA's sheet, {utilities:,} utilities")
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
