#!/usr/bin/env python3
"""Malawi's electricity sales, a year, 1992 to 2019: ESCOM's units sold in total and to power, general tariff and
domestic users and for export, as the National Statistical Office (NSO) gives them in table 10.1 of its Statistical
Year Book 2023 (session 2493, chain 121).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nso_malawi_electricity_sales_annual.csv,
from one PDF (no key):

    https://cms.nsomalawi.mw/api/download/230/Statistical_Year_Book_2023.pdf

Table "10.1 Number of Electricity Consumers and Units Sold by Type of User, 1992-2019" (source: ESCOM) is read by the
position of its words on the page: each quantity column is the span of its "Kwh" heading widened by 10 points a side,
and a figure's digit groups (written with spaces between thousands) are joined within that span, so a figure is never
split or merged by its spaces and no figure of a value column (Malawi kwacha, not taken) is read into a quantity.

    entity      nso:mw:<class> (total, power, general, domestic, exports)
    variable    sales
    unit        MWh (the table's millions of kWh times 1,000)
    ts_utc      the year's 1 January; freq P1Y; geo MW
    node        the column as NSO labels it

A cell marked "..." has no row. A figure not in the form of the table has no row and is counted in the header. The
years whose four classes do not sum to the total within 1 GWh are listed in the header (2010's power figure equals its
total, as printed); their figures are written as printed. The consumers' numbers and the sales' values are not taken.
A year book without the table, a heading without its five "Kwh" columns, or years not 1992 to 2019 in order stops the
run. Nothing is filled.

    python warehouse/connectors/nso_malawi_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/nso_malawi_yearbook/ and reused unless --fresh; --offline asks
nothing. cms.nsomalawi.mw and www.nsomalawi.mw answer HTTP 404 for a robots file (session 2493). License: not settled.
The year book states no terms of reuse; internal until a ruling.
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

NAME = "nso_malawi_electricity_sales_annual"
CONNECTOR = "nso_malawi_yearbook"
SOURCE = "nso_malawi:statistical_yearbook"
HOST = "cms.nsomalawi.mw"
URL = "https://cms.nsomalawi.mw/api/download/230/Statistical_Year_Book_2023.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TITLE = "10.1 Number of Electricity Consumers and Units Sold by Type of User"
CLASSES = ["total", "power", "general", "domestic", "exports"]
LABELS = {"total": "Total, Qty Kwh (mn)", "power": "Power, Qty Kwh (mn)", "general": "General Tarrif, Qty Kwh (mn)",
          "domestic": "Domestic, Qty Kwh (mn)", "exports": "Exports, Qty Kwh (mn)"}
YEARS = list(range(1992, 2020))
FORM = r"\d+(\.\d+)?|\d{1,3}( \d{3})+(\.\d+)?"
X_COLS = ["x_label"]


def lines_of(words):
    rows = {}
    for w in words:
        rows.setdefault(round(w["top"] / 3), []).append(w)
    return [sorted(rows[k], key=lambda w: w["x0"]) for k in sorted(rows)]


def parse_words(words, base, counts):
    lines = lines_of(words)
    kwh = next((ln for ln in lines if [w["text"] for w in ln] == ["Kwh"] * len(CLASSES)), None)
    if kwh is None:
        raise RuntimeError("no heading of the five Kwh columns")
    spans = [(w["x0"] - 10, w["x1"] + 10) for w in kwh]
    out, years = [], []
    for ln in lines:
        first = ln[0]["text"]
        if not re.fullmatch(r"(19|20)\d\d", first) or ln[0]["top"] < kwh[0]["top"]:
            continue
        year = int(first)
        years.append(year)
        for c, (a, b) in zip(CLASSES, spans):
            toks = [w["text"] for w in ln[1:] if w["x0"] >= a and w["x1"] <= b]
            cell = " ".join(toks)
            if not toks or set(cell.replace(" ", "")) <= {".", "…"}:
                continue
            if not re.fullmatch(FORM, cell):
                counts["cells out of form"] = counts.get("cells out of form", 0) + 1
                continue
            out.append(dict(entity=f"nso:mw:{c}", variable="sales", ts_utc=f"{year}-01-01T00:00:00Z",
                            value=round(float(cell.replace(" ", "")) * 1000, 3), unit="MWh", freq="P1Y", geo="MW", market="",
                            node=LABELS[c], **base, x_label=LABELS[c]))
    if years != YEARS:
        raise RuntimeError(f"years {years[:3]}...{years[-3:]}, not 1992 to 2019 in order")
    t = pd.DataFrame(out)
    if t.duplicated(["entity", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    w = t.pivot_table(index="ts_utc", columns="entity", values="value")
    parts = w[[f"nso:mw:{c}" for c in CLASSES[1:]]].sum(axis=1, min_count=4)
    off = [k[:4] for k in w.index if pd.notna(parts[k]) and abs(parts[k] - w.loc[k, "nso:mw:total"]) > 1000]
    counts["years whose classes do not sum to the total"] = ", ".join(off) or "none"
    return t


def parse(content, base, counts):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg for pg in pdf.pages if TITLE in (pg.extract_text() or "") and "Kwh" in (pg.extract_text() or "")]
        if len(pages) != 1:
            raise RuntimeError(f"table 10.1 found on {len(pages)} pages")
        return parse_words(pages[0].extract_words(), base, counts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NSO Malawi: ESCOM's units sold by type of user, 1992 to 2019")
    ap.add_argument("--offline", action="store_true", help="the saved year book only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the year book again")
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
        counts = {}
        t = parse(content, base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "nso:mw:total"].set_index("ts_utc").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): National Statistical Office of Malawi (NSO), Statistical Year Book 2023, table 10.1 (source: ESCOM), "
            f"Malawi's electricity units sold by type of user, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2493)",
            "Shape: series (docs/datastandard.md v0). entity nso:mw:<class> (total, power, general, domestic, exports); variable sales; unit MWh "
            "(the table's millions of kWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo MW; node NSO's column label. Figures as printed.",
            f"{len(t)} rows; total sales TWh: " + ", ".join(f"{k[:4]} {v:.2f}" for k, v in tot.items() if k[:4] in ("1992", "2000", "2010", "2017", "2018", "2019"))
            + f". Years whose classes do not sum to the total within 1 GWh: {counts.get('years whose classes do not sum to the total')}. "
            f"Not taken: cells ... (no row), cells out of form {counts.get('cells out of form', 0)}, the consumers' numbers, the values (MWK). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nso_malawi_electricity.py; the year book retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NSO Malawi, Statistical Year Book 2023, 10.1 Number of Electricity Consumers and Units Sold by Type of User, 1992-2019 (source: ESCOM)",
            f"  access: {URL}",
            "License: internal (the year book states no terms of reuse).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="National Statistical Office of Malawi (NSO)",
                                    report="Statistical Year Book 2023, table 10.1 (ESCOM's units sold by type of user)", report_url=URL,
                                    document_list=URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
