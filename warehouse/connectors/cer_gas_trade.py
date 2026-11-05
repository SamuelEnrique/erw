#!/usr/bin/env python3
"""The Canada Energy Regulator's natural gas trade: Canada's pipeline exports to the U.S. each month, in total and by the
U.S. region they cross into, its LNG exports, the export price, and its historical imports (session 910, chain 051:
Canada's own record of the flow EIA records as U.S. imports from Canada).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cer_gas_trade.csv, from the CER's Natural
Gas Trade Summary workbook (compiled from its monthly Commodity Statistics reports), linked from

    https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/natural-gas/statistics/natural-gas-trade-summary/index.html

    entity    cer_gas_trade:CA (Canada's pipeline trade with the U.S.), cer_gas_trade:CA:US_WEST, :US_MIDWEST, :US_EAST (the
              pipeline exports by the U.S. region of the border crossing, as the CER groups them), cer_gas_trade:CA:LNG
              (LNG exports, as their gaseous equivalent)
    variable  exports, imports (Mcf, the CER's thousand cubic feet), export_price, import_price (USD/MMBtu, the CER's U.S.
              dollars per million Btu)
    ts_utc    the month's first day; freq P1M; geo CA; node in words

Sheets read: "Fig. 1(m) Fig. 4(m)" (pipeline exports), "Fig. 2(m)" (by region), "Fig. 3(m)" (LNG exports), "Fig. 5(m)"
(the export price) and "ARCHIVED - Imports" (imports and their price; the CER removed later imports from its site). The
CER's cubic metres, its values in Canadian dollars and its prices in Canadian dollars per GJ are not taken (no such units
in the data standard). The archived sheet's LNG import columns repeat its gas import columns figure for figure, so they
are not taken either. The page says the import data after December 2022 have been removed from the site, yet the
sheet runs to December 2024; its months after December 2022 fall away from EIA's record of the same flow (to 14 percent
of it by December 2024, session 910), so the imports are taken to December 2022 only, as the page states, and the months
left out are counted in the header. A heading not as read stops the run; so does a key given twice. The CER notes that the latest
figures, with revisions, are on its Commodity Statistics pages; this table holds the workbook as published.

    python warehouse/connectors/cer_gas_trade.py [--offline]

Ceiling: two requests (the page and the workbook; both saved in warehouse/raw/cer_gas_trade/ and reused offline). The
CER's robots file allows these paths (disallowing /fracfocus and /bin). License: the CER's terms allow reproduction for
non-commercial purposes with the title, the author and a statement that it is a copy not produced with the CER's
endorsement; commercial redistribution needs the CER's written permission (license_reads.csv, session 887).
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

NAME = "cer_gas_trade"
CONNECTOR = "cer_gas_trade"
SOURCE = "cer:natural_gas_trade_summary"
PAGE = "https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/natural-gas/statistics/natural-gas-trade-summary/index.html"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# (sheet, the heading's start, entity, variable, unit, node)
COLUMNS = [
    ("Fig. 1(m) Fig. 4(m)", "Gas Export Volume / Volume d", "(Mcf / Kpi3)", "CA", "exports", "Mcf", "Canada, natural gas pipeline exports to the U.S."),
    ("Fig. 2(m)", "West / Ouest (Mcf / Kpi3)", "", "CA:US_WEST", "exports", "Mcf", "Canada, natural gas pipeline exports to the U.S. West"),
    ("Fig. 2(m)", "Midwest (Mcf / Kpi3)", "", "CA:US_MIDWEST", "exports", "Mcf", "Canada, natural gas pipeline exports to the U.S. Midwest"),
    ("Fig. 2(m)", "East / Est (Mcf / Kpi3)", "", "CA:US_EAST", "exports", "Mcf", "Canada, natural gas pipeline exports to the U.S. East"),
    ("Fig. 3(m)", "LNG Export Volume / Volume d", "(Mcf / Kpi3)", "CA:LNG", "exports", "Mcf", "Canada, LNG exports (gaseous equivalent)"),
    ("Fig. 5(m)", "Gas Export Price / Prix d", "($US per MMBtu / $US par MBtu)", "CA", "export_price", "USD/MMBtu", "Canada, natural gas export price"),
    ("ARCHIVED - Imports", "Gas Import Volume / Volume d", "(Mcf / Kpi3)", "CA", "imports", "Mcf", "Canada, natural gas imports from the U.S."),
    ("ARCHIVED - Imports", "Gas Import Price / Prix d", "($US per MMBtu / $US par MBtu)", "CA", "import_price", "USD/MMBtu", "Canada, natural gas import price"),
]
IMPORTS_TO = "2022-12-01T00:00:00Z"  # the page: "the import data after December 2022 has been removed from the website"


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def workbook_url(page_html):
    found = sorted(set(re.findall(r'href="([^"]*natural-gas-trade[^"]*\.xlsx)"', page_html)))
    if len(found) != 1:
        raise RuntimeError(f"the page links {len(found)} trade workbooks, not one: {found}")
    href = found[0]
    return href if href.startswith("http") else "https://www.cer-rec.gc.ca" + href


def column_of(frame, start, end):
    head = [text(v) for v in frame.iloc[0]]
    if head[0] != "Date":
        raise RuntimeError(f"a sheet's first heading is {head[0]!r}, not Date")
    hits = [c for c, h in enumerate(head) if h.startswith(start) and h.endswith(end)]
    if len(hits) != 1:
        raise RuntimeError(f"{len(hits)} headings start {start!r} and end {end!r}: {head}")
    return hits[0]


def sheet_rows(xl, base):
    out, frames, late = [], {}, 0
    for sheet, start, end, ent, var, unit, node in COLUMNS:
        if sheet not in frames:
            frames[sheet] = pd.read_excel(xl, sheet, header=None)
        f = frames[sheet]
        c = column_of(f, start, end)
        for _, r in f.iloc[1:].iterrows():
            d = pd.to_datetime(r[0], errors="coerce")
            if pd.isna(d):
                continue
            if d.day != 1:
                raise RuntimeError(f"{sheet}: a date not a month's first day: {r[0]!r}")
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            ts = d.strftime("%Y-%m-01T00:00:00Z")
            if var.startswith("import") and ts > IMPORTS_TO:
                late += 1
                continue
            out.append(dict(base, entity=f"cer_gas_trade:{ent}", variable=var, ts_utc=ts,
                            value=float(v), unit=unit, freq="P1M", geo="CA", node=node))
    return out, late


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Canada Energy Regulator's natural gas trade with the U.S.")
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
        if ip.paused_host("www.cer-rec.gc.ca"):
            raise RuntimeError("the Canada Energy Regulator is paused (paused_sources.csv): not asked")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook")
        xl = pd.ExcelFile(io.BytesIO(content))
        base = dict(market="", source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        got, late = sheet_rows(xl, base)
        s = pd.DataFrame(got)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s.loc[s.duplicated(['entity', 'variable', 'ts_utc']), 'entity'].head(3).tolist()}")
        s = s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        span = {f"{e} {v}": f"{g.ts_utc.min()[:7]} to {g.ts_utc.max()[:7]}" for (e, v), g in s.groupby(["entity", "variable"])}
        exp, imp = span["cer_gas_trade:CA exports"], span.get("cer_gas_trade:CA imports", "none")
        header = [
            "Energy Research Warehouse (ERW): the Canada Energy Regulator, Canada's natural gas trade with the U.S., a month: pipeline exports in total and by U.S. region, LNG exports, the export price, and historical imports (session 910)",
            "Shape: series (docs/datastandard.md v0). entity cer_gas_trade:CA (pipeline trade with the U.S.), cer_gas_trade:CA:US_WEST, :US_MIDWEST, :US_EAST "
            "(pipeline exports by the U.S. region of the border crossing; the three sum to CA's exports), cer_gas_trade:CA:LNG (LNG exports, gaseous "
            "equivalent); variables exports and imports (Mcf, the CER's thousand cubic feet) and export_price and import_price (USD/MMBtu, the CER's); "
            "ts_utc the month's first day; freq P1M; geo CA.",
            f"Pipeline exports {exp}; imports {imp}, as the page states (the CER's archived sheet; its {late} import and import price figures of later "
            "months, which fall away from EIA's record of the same flow, are not taken); "
            f"{len(s):,} rows. "
            "The CER's cubic metres, its values in Canadian dollars and its Canadian dollar prices are not taken (no such units in the data standard); "
            "the archived sheet's LNG import columns repeat its gas import columns figure for figure and are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cer_gas_trade.py (the workbook retrieved {rec.get('retrieved_at', '')}, last modified {base['vintage']})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Canada Energy Regulator, Natural Gas Trade Summary (compiled from the CER's monthly Commodity Statistics), {PAGE}",
            f"  access: {url}",
            "License: the CER's terms allow non-commercial reproduction with the title and author, stating that it is a copy not produced in affiliation "
            "with or with the endorsement of the CER; commercial redistribution needs the CER's written permission. This table is a copy of the version "
            "available at the CER website and has not been produced in affiliation with, or with the endorsement of, the CER.",
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Canada Energy Regulator (CER)", report="Natural Gas Trade Summary",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, pipeline exports {exp}, imports {imp}")
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
