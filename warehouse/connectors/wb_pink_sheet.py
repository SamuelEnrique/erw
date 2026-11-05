#!/usr/bin/env python3
"""The World Bank's commodity prices (the Pink Sheet): each month's price of crude oil, coal, natural gas and LNG, and of
the base metals, in nominal U.S. dollars, from 1960 (session 926, chain 052: the energy prices the world trades against,
beside imf_commodity_prices' metals).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/wb_commodity_prices_monthly.csv, from the
World Bank Commodity Price Data workbook (CMO Historical Data Monthly, sheet "Monthly Prices"), linked from

    https://www.worldbank.org/en/research/commodity-markets

    entity    wb_pink:<the series' name as a slug> (crude_oil_brent, coal_australian, natural_gas_us, copper, ...)
    variable  price; unit USD/bbl, USD/t (the sheet's $/mt) or USD/MMBtu as the sheet's second heading row gives it
    ts_utc    the month's first day (the sheet's 1960M01); freq P1M; geo empty (world markets); node the series' name

Taken: the energy columns (crude oil average, Brent, Dubai and WTI; Australian and South African coal; U.S. and European
natural gas; Japan's LNG) and the base metals priced per metric ton (aluminum, copper, lead, tin, nickel, zinc). Not
taken: the natural gas index (2010=100; no index unit in the data standard), the agricultural and fertilizer columns, iron
ore ($/dmtu) and the precious metals ($/troy oz). The workbook's "**" after a name (a note in its Description sheet) is
removed from the node and counted in the header. A heading or unit not as read, or a month not of the form 1960M01, stops
the run; the sheet's "…" (not available) has no row. Nothing is filled.

    python warehouse/connectors/wb_pink_sheet.py [--offline]

Ceiling: two requests (the page and the workbook; saved in warehouse/raw/wb_pink_sheet/ and reused offline, the page
asked again unless --offline). The World Bank's robots file allows the page; thedocs.worldbank.org has no robots file
(HTTP 404, session 926). License: CC BY 4.0, "unless indicated otherwise in the data or indicator metadata" (the World
Bank's Summary Terms of Use, read by session 926); cite "World Bank Commodity Price Data (The Pink Sheet)".
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

NAME = "wb_commodity_prices_monthly"
CONNECTOR = "wb_pink_sheet"
SOURCE = "worldbank:pink_sheet"
PAGE = "https://www.worldbank.org/en/research/commodity-markets"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "Monthly Prices"
TAKE = ["Crude oil, average", "Crude oil, Brent", "Crude oil, Dubai", "Crude oil, WTI", "Coal, Australian", "Coal, South African",
        "Natural gas, US", "Natural gas, Europe", "Liquefied natural gas, Japan", "Aluminum", "Copper", "Lead", "Tin", "Nickel", "Zinc"]
UNITS = {"($/bbl)": "USD/bbl", "($/mt)": "USD/t", "($/mmbtu)": "USD/MMBtu"}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def workbook_url(page_html):
    found = sorted(set(re.findall(r'href="([^"]*CMO-Historical-Data-Monthly\.xlsx)"', page_html)))
    if len(found) != 1:
        raise RuntimeError(f"the page links {len(found)} monthly data workbooks, not one: {found}")
    return found[0]


def rows(frame, base):
    head = None
    for i in range(min(15, len(frame))):
        if text(frame.iloc[i, 1]).startswith("Crude oil"):
            head = i
            break
    if head is None:
        raise RuntimeError("no heading row beginning 'Crude oil' in the sheet's first 15 rows")
    names = [text(v) for v in frame.iloc[head]]
    units = [text(v) for v in frame.iloc[head + 1]]
    cols, starred = {}, []
    for c, n in enumerate(names):
        plain = n.replace("*", "").strip()
        if plain in TAKE:
            if units[c] not in UNITS:
                raise RuntimeError(f"a unit not in the map for {plain!r}: {units[c]!r}")
            cols[plain] = c
            if "*" in n:
                starred.append(plain)
    missing = [n for n in TAKE if n not in cols]
    if missing:
        raise RuntimeError(f"columns not in the sheet: {missing}")
    out = []
    for _, r in frame.iloc[head + 2:].iterrows():
        m = text(r.iloc[0])
        if not m:
            continue
        mm = re.fullmatch(r"(\d{4})M(\d{2})", m)
        if not mm:
            raise RuntimeError(f"a month not of the form 1960M01: {m!r}")
        ts = f"{mm.group(1)}-{mm.group(2)}-01T00:00:00Z"
        for n, c in cols.items():
            v = pd.to_numeric(r.iloc[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, entity=f"wb_pink:{slug(n)}", variable="price", ts_utc=ts, value=float(v), unit=UNITS[units[c]],
                            freq="P1M", geo="", market="", node=n))
    return out, starred


def main(argv=None):
    ap = argparse.ArgumentParser(description="The World Bank's commodity prices (the Pink Sheet), energy and base metals")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook")
        frame = pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=None)
        updated = next((text(v) for v in frame.iloc[:6, 0] if text(v).startswith("Updated on")), "")
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        got, starred = rows(frame, base)
        s = pd.DataFrame(got)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        s = s[ip.SERIES_COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        span = f"{s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): the World Bank's commodity prices (the Pink Sheet), energy and base metals, a month, nominal U.S. dollars (session 926)",
            "Shape: series (docs/datastandard.md v0). entity wb_pink:<series name as a slug>; variable price; unit USD/bbl (crude oil), USD/t (coal and "
            "the metals, the sheet's $/mt) or USD/MMBtu (natural gas and LNG); ts_utc the month's first day; freq P1M; geo empty (world markets); node the series' name.",
            f"Months {span}; {s.entity.nunique()} series, {len(s):,} rows; the workbook '{updated}'. Not taken: the natural gas index (2010=100), the "
            "agricultural and fertilizer prices, iron ore and the precious metals. " + (f"A note mark (**) removed from {', '.join(starred)} "
            "(see the workbook's Description sheet). " if starred else "") + "The sheet's '…' (not available) has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/wb_pink_sheet.py (the workbook retrieved {rec.get('retrieved_at', '')}, last modified {base['vintage']})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} World Bank, World Bank Commodity Price Data (The Pink Sheet), {PAGE}",
            f"  access: {url}",
            "License: CC BY 4.0, unless indicated otherwise in the data (the World Bank's Summary Terms of Use); cite \"World Bank Commodity Price Data (The Pink Sheet)\".",
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="World Bank", report="World Bank Commodity Price Data (The Pink Sheet)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s.entity.nunique()} series, {span}")
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
