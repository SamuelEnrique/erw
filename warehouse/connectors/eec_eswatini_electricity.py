#!/usr/bin/env python3
"""Eswatini's public grid a financial year: the energy the Eswatini Electricity Company (EEC) sold and sent out, its
internal generation, its imports and the generation bought from Ubombo Sugar, for the years ended 31 March 2025 and 2024,
as its Integrated Annual Report 2025 gives them on its page "Highlights and at-a-glance metrics" (session 2560, chain
126; the ERW held Eswatini only in EIA's international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eec_eswatini_electricity_annual.csv, from one
PDF (no key):

    https://eec.co.sz/aboutus/reports/docs/EEC_IAR25.pdf

The page's text runs its columns together, so it is read by order, not by place: its five figures in GWh ("<figure> GWh")
and their five figures for the year before ("(2024: <figure> GWh)") each come in one order, the order of their labels,
which must stand on the page in that order too: Energy Sold, Units Sent Out (Total Supply), Internal Generation,
Electricity Imports, Local Generation from Ubombo Sugar Ltd (USL). Any other count or order stops the run.

    entity      eec:sz:total (EEC's system)
    variable    sold, sent_out, internal_generation, imports, purchases_ubombo_sugar
    unit        MWh (EEC's GWh times 1,000); ts_utc the financial year's first day (1 April); freq P1Y; geo SZ
    node        EEC's label; x_fiscal_year the financial year (2024/25, 2023/24)

The percentages (system losses, the shares of supply) and the financial figures are not taken. The system losses' and
the trade with the Southern African Power Pool's figures in the report's text are not taken. Nothing is filled.

    python warehouse/connectors/eec_eswatini_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/eec_sz/ and reused unless --fresh; --offline asks nothing.
eec.co.sz and www.eec.co.sz have no robots file (session 2560). License: internal. EEC's terms of use: "Reproduction is
prohibited other than in accordance with the copyright notice", which reads "(c) 2026 Eswatini Electricity Company. All
rights reserved."; internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eec_eswatini_electricity_annual"
CONNECTOR = "eec_sz"
SOURCE = "eec:integrated_annual_report_2025"
HOST = "eec.co.sz"
URL = "https://eec.co.sz/aboutus/reports/docs/EEC_IAR25.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Eswatini Electricity Company (EEC), Integrated Annual Report 2025, Highlights and at-a-glance metrics"
PAGE_TITLE = "HIGHLIGHTS AND AT-A-GLANCE METRICS"
LABELS = [("Energy Sold", "sold"), ("Units Sent Out (Total Supply)", "sent_out"), ("Internal Generation", "internal_generation"),
          ("Electricity Imports", "imports"), ("from Ubombo Sugar Ltd (USL)", "purchases_ubombo_sugar")]
YEARS = [("2024/25", "2024-04-01T00:00:00Z"), ("2023/24", "2023-04-01T00:00:00Z")]
FIG = r"\d{1,3}(?:,\d{3})*(?:\.\d+)?"
X_COLS = ["x_fiscal_year"]


def parse_text(text, base):
    if PAGE_TITLE not in text:
        raise RuntimeError("the highlights page not found")
    places = []
    for label, _ in LABELS:
        if text.count(label) != 1:
            raise RuntimeError(f"the label {label!r} found {text.count(label)} times")
        places.append(text.index(label))
    if places != sorted(places):
        raise RuntimeError("the labels are not in their order")
    prior = [m for m in re.finditer(r"\(2024: (" + FIG + r") GWh\)", text)]
    now = [m for m in re.finditer(r"(?<![\d,.])(" + FIG + r") GWh(?!\))", text) if not text[:m.start()].endswith("(2024: ")]
    if len(now) != len(LABELS) or len(prior) != len(LABELS):
        raise RuntimeError(f"{len(now)} figures and {len(prior)} figures of the year before, not {len(LABELS)} each")
    rows = []
    for (label, item), m_now, m_prior in zip(LABELS, now, prior):
        for (fy, ts), m in zip(YEARS, (m_now, m_prior)):
            v = float(m.group(1).replace(",", ""))
            rows.append(dict(entity="eec:sz:total", variable=item, ts_utc=ts, value=round(v * 1000, 3), unit="MWh", freq="P1Y",
                             geo="SZ", market="", node=label, **base, x_fiscal_year=fy))
    return pd.DataFrame(rows)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg.extract_text() or "" for pg in pdf.pages[:12]]
    hits = [p for p in pages if PAGE_TITLE in p]
    if len(hits) != 1:
        raise RuntimeError(f"the highlights page found {len(hits)} times")
    return parse_text(hits[0], base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EEC: Eswatini's energy sold, sent out, generated and imported, a financial year")
    ap.add_argument("--offline", action="store_true", help="the saved report only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the report again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        v = {(x, fy): val for x, fy, val in zip(t.variable, t.x_fiscal_year, t.value)}
        head = [
            "Energy Research Warehouse (ERW): Eswatini Electricity Company (EEC), Integrated Annual Report 2025, highlights: energy sold, sent "
            "out, generated, imported and bought from Ubombo Sugar, the years ended 31 March 2025 and 2024 (session 2560)",
            "Shape: series (docs/datastandard.md v0). entity eec:sz:total (EEC's system); variable sold, sent_out, internal_generation, imports, "
            "purchases_ubombo_sugar; unit MWh (EEC's GWh times 1,000); ts_utc the financial year's first day (1 April); freq P1Y; geo SZ; node EEC's "
            "label; x_fiscal_year the financial year.",
            f"{len(t)} rows; in 2024/25 sent out {v[('sent_out', '2024/25')] / 1e3:.1f} GWh, imports {v[('imports', '2024/25')] / 1e3:.1f} GWh, "
            f"internal generation {v[('internal_generation', '2024/25')] / 1e3:.1f} GWh, sold {v[('sold', '2024/25')] / 1e3:.1f} GWh. "
            "Percentages and money are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eec_eswatini_electricity.py; the report retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: internal. EEC's terms of use prohibit reproduction other than under its copyright notice (all rights reserved); "
            f"internal until a ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Eswatini Electricity Company (EEC)",
                                    report="Integrated Annual Report 2025, highlights and at-a-glance metrics", report_url=URL,
                                    document_list="https://www.eec.co.sz/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
