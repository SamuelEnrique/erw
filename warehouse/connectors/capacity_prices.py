#!/usr/bin/env python3
"""Capacity auction clearing prices: PJM RPM Base Residual Auction, per LDA and delivery year.

Energy Research Warehouse (ERW) connector, session 7 (docs/price-sources.md,
section 7). Writes warehouse/output/pjm_rpm_capacity_prices.csv, a `series`
table:

    entity    pjm:<LDA as PJM names it>        (pjm:RTO, pjm:MAAC, pjm:COMED, ...)
    variable  capacity_price_usd_per_mw_day
    unit      USD/MW-day
    freq      P1Y; ts_utc is the start of the delivery year, June 1 00:00:00Z
    market    bra (Base Residual Auction; incremental auctions are not included)
    node      the LDA

    python warehouse/connectors/capacity_prices.py

Source: PJM's "Resource Clearing Prices for all RPM Auctions held to date"
workbook, linked from https://www.pjm.com/markets-and-operations/rpm. One
number per LDA per delivery year: the headline product, which is the only
product before 2014/15, "Annual" from 2014/15 to 2017/18, and "CP" (Capacity
Performance) from 2018/19. The Extended Summer, Limited and Base products are
not written. A cell marked "**" (PJM: "LDA was not modeled") is not a price
and is omitted; nothing is filled from the parent LDA.

License: PJM's data terms bar non-members from republishing, so the table is
internal (license_of marks every pjm: source internal). ISO-NE FCA and MISO PRA
prices need written permission for non-personal use and are not collected
(docs/price-sources.md; SESSION_7_REPORT.md). The session 7 prompt calls the
table `capacity_prices`; that name has two parts and the naming rule needs
three, so the PJM table is pjm_rpm_capacity_prices and other ISOs would get
their own tables with the same variable.

The workbook layout is checked, not assumed: the LDA header row, the "DY yy/yy"
block labels and every BRA cell must parse, or the run fails and writes nothing.
"""

import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "pjm_rpm_capacity_prices"
URL = ("https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/"
       "rpm-auctions-resource-clearing-price-summary.xlsx")
PAGE = "https://www.pjm.com/markets-and-operations/rpm"
SOURCE = "pjm:rpm-clearing-price-summary"
REPORT = "RPM Resource Clearing Prices for all RPM Auctions held to date"
HEADLINE = {"*", "annual", "cp"}          # the product written per delivery year
OTHER = {"ext summer", "limited", "base gen", "base dr/ee"}
NOT_MODELED = "**"


def parse(raw, log):
    """(delivery year start, LDA, price) for every BRA headline cell."""
    x = pd.read_excel(io.BytesIO(raw), header=None, dtype=str)
    hdr = x.index[x[1].astype(str).str.strip().str.startswith("Capacity Product Type")]
    if len(hdr) != 1:
        raise RuntimeError("PJM workbook: no single 'Capacity Product Type' header row; layout changed")
    h = int(hdr[0])
    ldas = {c: str(x.at[h, c]).strip() for c in x.columns[2:] if str(x.at[h, c]).strip() not in ("", "nan")}
    if ldas.get(2) != "RTO":
        raise RuntimeError(f"PJM workbook: first LDA column is {ldas.get(2)!r}, expected 'RTO'")
    rows, dy, seen = [], None, set()
    for i in range(h + 1, len(x)):
        label = str(x.at[i, 0]).strip()
        m = re.match(r"^DY ?(\d{2})/(\d{2})$", label)
        if m:
            y0, y1 = 2000 + int(m.group(1)), 2000 + int(m.group(2))
            if y1 != y0 + 1:
                raise RuntimeError(f"PJM workbook row {i}: odd delivery year label {label!r}")
            dy = y0
            continue
        if label != "BRA":
            continue
        if dy is None:
            raise RuntimeError(f"PJM workbook row {i}: BRA row before any 'DY' label")
        product = str(x.at[i, 1]).strip().lower()
        if product in OTHER:
            continue
        if product not in HEADLINE:
            raise RuntimeError(f"PJM workbook row {i}: unknown product {x.at[i, 1]!r} for DY {dy}")
        if dy in seen:
            raise RuntimeError(f"PJM workbook: two headline BRA rows for DY {dy}")
        seen.add(dy)
        for c, lda in ldas.items():
            v = str(x.at[i, c]).strip()
            if v in ("", "nan", NOT_MODELED):
                continue
            try:
                price = round(float(v), 2)  # the sheet stores 95.78999999999999 for 95.79
            except ValueError:
                raise RuntimeError(f"PJM workbook DY {dy} {lda}: not a price: {v!r}")
            rows.append((dy, lda, price))
    if not rows:
        raise RuntimeError("PJM workbook: no BRA prices parsed")
    log(f"  parsed {len(rows)} BRA headline prices, delivery years {min(seen)}/{min(seen) + 1} "
        f"to {max(seen)}/{max(seen) + 1}, {len(ldas)} LDA columns")
    return rows, max(seen)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"capacity_prices_{run_id}.log"))
    ip.RAW.open("capacity_prices", run_id)
    results = []
    try:
        def call():
            r = requests.get(URL, timeout=120, headers={"User-Agent": "Mozilla/5.0 (ERW research warehouse)"})
            if r.status_code != 200:
                raise RuntimeError(f"PJM workbook HTTP {r.status_code}")
            return r
        r = ip.with_retries("PJM RPM clearing price workbook", call, log)
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        log(f"GET {URL}: {len(r.content)} bytes")
        rows, newest = parse(r.content, log)
        this_year = dt.date.today().year
        if newest < this_year:
            raise RuntimeError(f"newest BRA delivery year {newest}/{newest + 1} starts before {this_year}; "
                               "PJM holds each BRA years ahead, so the workbook looks stale")
        s = pd.DataFrame({
            "entity": [f"pjm:{lda}" for _, lda, _ in rows],
            "variable": "capacity_price_usd_per_mw_day",
            "ts_utc": [f"{dy}-06-01T00:00:00Z" for dy, _, _ in rows],
            "value": [p for _, _, p in rows],
            "unit": "USD/MW-day", "freq": "P1Y", "geo": "US", "market": "bra",
            "node": [lda for _, lda, _ in rows],
            "source": SOURCE, "source_url": URL, "retrieved_at": got, "vintage": "",
        }).sort_values(["entity", "ts_utc"])
        header = [
            "Energy Research Warehouse (ERW): PJM RPM Base Residual Auction clearing prices by LDA",
            "Shape: series (docs/datastandard.md v0). freq P1Y: ts_utc is the start of the delivery "
            "year (June 1, 00:00:00Z). Headline product only: the single product to 2013/14, Annual "
            "2014/15 to 2017/18, CP from 2018/19. '**' cells (LDA not modeled) are omitted.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/capacity_prices.py",
            f"Run log: warehouse/output/logs/capacity_prices_{run_id}.log",
            f"Raw files: warehouse/raw/capacity_prices/{run_id}/ (not in git)",
            f"Source: {SOURCE} PJM Interconnection, {REPORT} (linked from {PAGE}), {URL}",
            "License: internal. PJM data terms bar non-members from republishing.",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="PJM Interconnection", report=REPORT,
                                report_url=PAGE, document_list=URL, tables=[NAME])])
        results.append(dict(table=NAME, market="bra", status="ok", detail=""))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"capacity_prices {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="bra", status="failed", detail=last[:300]))
    ip.write_status("capacity_prices", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"capacity_prices run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
