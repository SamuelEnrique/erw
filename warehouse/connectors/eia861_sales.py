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


def sheet_rows(frame, year, url, retrieved):
    """One sheet (States or Territories) as the table's rows: observed utilities only, a row a figure."""
    d = frame[pd.to_numeric(frame[0], errors="coerce").eq(year)].copy()
    d = d[d[5].astype(str).str.strip().eq("O")]
    d = d[~pd.to_numeric(d[1], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state, part, ba = int(r[1]), str(r[6]).strip(), str(r[3]).strip(), "" if pd.isna(r[8]) else str(r[8]).strip()
        ent = f"eia861:{util}:{state}:{part}:{ba}"
        base = dict(entity=ent, ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y", geo=f"US-{state}", market="", node=str(r[2]).strip(),
                    source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                    x_utility_number=str(util), x_state=state, x_part=part, x_service_type=str(r[4]).strip(),
                    x_ownership="" if pd.isna(r[7]) else str(r[7]).strip(), x_ba_code=ba, x_data_type="O")
        for i, sector in enumerate(SECTORS):
            for j, (measure, unit, scale) in enumerate(MEASURES):
                v = pd.to_numeric(r[9 + 3 * i + j], errors="coerce")
                if pd.isna(v):      # "." in EIA's sheet: no value, no row
                    continue
                out.append(dict(base, variable=f"{sector}_{measure}", value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{year}: an (entity, variable, ts_utc) is given twice")
    return t


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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=UA)
        url, year = zip_url(page.decode("utf-8", errors="replace"), args.year)
        content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
        book = zipfile.ZipFile(io.BytesIO(content)).read(f"Sales_Ult_Cust_{year}.xlsx")
        frames = [sheet_rows(pd.read_excel(io.BytesIO(book), s, header=None, skiprows=3), year, url, rec["retrieved_at"]) for s in ("States", "Territories")]
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"{year}: a row in both sheets")
        s = s[ip.SERIES_COLS + X_COLS]
        header = [
            "Energy Research Warehouse (ERW): EIA-861 retail sales, revenue and customers, each utility by state, part and sector, a year (session 485)",
            "Shape: series (docs/datastandard.md v0). entity eia861:<utility>:<state>:<part>:<balancing authority>; variables <sector>_sales (MWh), <sector>_revenue (USD, EIA's thousand dollars times 1,000), <sector>_customers (count), sectors residential, commercial, industrial, transportation and total; ts_utc the data year's 1 January; freq P1Y; node the utility's name.",
            f"Years held: {year} (this run; earlier runs' years are kept, merged on entity, variable, ts_utc). Observed rows only: EIA's imputed rows (data type I), its 88888 Withheld and 99999 Adjustment aggregates and its '.' cells are not taken; nothing is filled.",
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
