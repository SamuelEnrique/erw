#!/usr/bin/env python3
"""EIA-861: the delivery-only companies (Texas's wires utilities), their delivery revenue, energy delivered and
customers by sector, a year (session 853, chain 046: a Texas wires utility's own revenue, which eia861_utility_sales
lacks because EIA files these companies apart).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia861_delivery_only.csv, from the
U.S. Energy Information Administration's Form EIA-861 annual files (Delivery_Companies_<year>.xlsx in f861<year>.zip,
sheet "Delivery Companies", from 2020), the zips eia861_sales.py saved:

    page   https://www.eia.gov/electricity/data/eia861/
    file   https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip   (earlier years under archive/zip/)

The sheet has the layout of Sales_Ult_Cust's (part C, service type Delivery), so it is read by eia861_sales.py's own
sheet_rows: the same entity (eia861:<utility>:<state>:C:<balancing authority>), variables (<sector>_revenue in USD,
EIA's thousand dollars times 1,000, here the delivery revenue; <sector>_sales in MWh, the energy delivered;
<sector>_customers), observed rows only, "." cells without a row. On 23 October 2026 the file held the Texas
transmission and distribution utilities only (6 a year to 2023, 7 from 2024), none of them in eia861_utility_sales;
a key found in both tables would be a fault and stops the run when --check-sales names that table.

    python warehouse/connectors/eia861_delivery.py --years 2020 2021 2022 2023 2024 2025 --offline

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/. EIA's robots
file disallows /archive/ (session 666): a year there is read only from a zip already saved. License: public (EIA,
record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import PAGE, UA, X_COLS, held_text, sheet_rows, zip_url  # noqa: E402  the sales table's reader

NAME = "eia861_delivery_only"
CONNECTOR = "eia861"   # the raw files of the EIA-861 zips are shared with eia861_sales.py
SOURCE = "eia:eia861:delivery_companies"
SHEET = "Delivery Companies"


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 delivery-only companies: delivery revenue, energy and customers by sector")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years (the file starts with 2020)")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--check-sales", help="eia861_utility_sales.csv: stop if a key of this table is also there")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_delivery_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames, urls = [], []
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            if content[:2] != b"PK":
                raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
            name = f"Delivery_Companies_{year}.xlsx"
            if name not in zipfile.ZipFile(io.BytesIO(content)).namelist():
                raise RuntimeError(f"f861{year}.zip holds no {name}")
            xl = pd.ExcelFile(io.BytesIO(zipfile.ZipFile(io.BytesIO(content)).read(name)))
            t = sheet_rows(pd.read_excel(xl, SHEET, header=None), year, url, rec["retrieved_at"])
            if len(t) and not t["x_part"].eq("C").all():
                raise RuntimeError(f"{year}: a row of the delivery companies' file is not part C")
            log(f"{year}: {len(t):,} rows, {t['x_utility_number'].nunique()} companies")
            frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        s["source"] = SOURCE   # session 865: the sales reader names the form; this table names its file, as its header does
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        if args.check_sales:
            with open(args.check_sales, encoding="utf-8") as f:
                n = sum(1 for ln in f if ln.startswith("#"))
            sales = pd.read_csv(args.check_sales, skiprows=n, usecols=["entity", "ts_utc"], dtype=str, keep_default_na=False)
            both = set(zip(s["entity"], s["ts_utc"])) & set(zip(sales["entity"], sales["ts_utc"]))
            if both:
                raise RuntimeError(f"{len(both)} keys are in eia861_utility_sales too: {sorted(both)[:3]}")
            log("no key is in eia861_utility_sales too")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        years = sorted({int(t[:4]) for t in s["ts_utc"]})
        header = [
            "Energy Research Warehouse (ERW): EIA-861 delivery-only companies (Texas's transmission and distribution utilities): delivery revenue, energy delivered and customers by sector, a year (session 853)",
            "Shape: series (docs/datastandard.md v0). entity eia861:<utility>:<state>:C:<balancing authority>, as eia861_utility_sales; variables <sector>_revenue (USD, EIA's thousand dollars times 1,000: delivery revenue), "
            "<sector>_sales (MWh: energy delivered), <sector>_customers (count); ts_utc the data year's 1 January; freq P1Y; node the company's name.",
            f"Years held: {held_text(years)}. Observed rows only; a '.' cell has no row; nothing is filled. EIA files these companies apart from Sales_Ult_Cust, so none is in eia861_utility_sales.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_delivery.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_delivery_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Delivery_Companies_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, delivery companies", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique()} companies")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_delivery FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_delivery", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
