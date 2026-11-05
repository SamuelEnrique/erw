#!/usr/bin/env python3
"""Fiji's electricity, a year, 2011 to 2024: Energy Fiji Limited's (EFL) units produced and sold, and its sales by type of
consumer, as the Fiji Bureau of Statistics (FBoS) gives them in Key Statistics table 3.7[A] and in Appendix III of its
economic survey "Electricity 2024" (session 2492, chain 121).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/fbos_fiji_electricity_annual.csv, from two
PDFs (no key):

    https://www.statsfiji.gov.fj/download/138/table-3/827/3-7a_electricity.pdf
    https://www.statsfiji.gov.fj/download/271/electricity/5954/2024-electricity.pdf

Table 3.7[A] "Production and Sales of Electricity by Energy Fiji Ltd" gives, a year, the units produced and sold in kWh
(and the sales' value in Fiji dollars, not taken). Appendix III "Sales of Electricity by Type of Consumers" gives the
units sold to industrial, commercial, domestic and other consumers. Its heading reads "kwh (000's)", but its totals are
table 3.7[A]'s units sold in millions of kWh (740.9 for 2011's 740,873,951 kWh): each year's total is checked against
3.7[A] within 0.1 GWh and the run stops on a difference, so the figures are read as GWh. The appendix's totals are not
written; its value section (Fiji dollars) is not taken.

    entity      fbos:fj:efl (3.7[A]); fbos:fj:<consumer> (industrial, commercial, domestic, others) (Appendix III)
    variable    generation (units produced), sales (units sold)
    unit        MWh (kWh divided by 1,000; GWh times 1,000)
    ts_utc      the year's 1 January; freq P1Y; geo FJ
    node        the row as FBoS labels it

A cell "n/a" has no row. A table not found, a row with another number of cells, years not consecutive, or a key given
twice stops the run. Nothing is filled. EFL's figures cover its grids; Appendix V's production index includes the Fiji
Sugar Corporation's own generation, which is not taken.

    python warehouse/connectors/fbos_fiji_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests a run, saved in warehouse/raw/fbos_fiji_electricity/ and reused unless --fresh; --offline asks
nothing. www.statsfiji.gov.fj's robots file disallows nothing (session 2492). License: public with a citation. The
report's page ii: "Any table or material published in this Report may be reproduced and published without the Fiji
Bureau of Statistics' prior approval. However, the source of information should always be identified and acknowledged
in all modes of presentation."
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

NAME = "fbos_fiji_electricity_annual"
CONNECTOR = "fbos_fiji_electricity"
SOURCE = "fbos:electricity"
HOST = "www.statsfiji.gov.fj"
URL_KEY = "https://www.statsfiji.gov.fj/download/138/table-3/827/3-7a_electricity.pdf"
URL_REPORT = "https://www.statsfiji.gov.fj/download/271/electricity/5954/2024-electricity.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Fiji Bureau of Statistics, Key Statistics table 3.7[A] and Economic Surveys: Electricity 2024, Appendix III (source: Energy Fiji Ltd)"
CONSUMERS = ["industrial", "commercial", "domestic", "others"]
X_COLS = ["x_label"]


def text_of(content):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        return "\n".join(pg.extract_text() or "" for pg in pdf.pages)


def kwh(tok):
    if not re.fullmatch(r"\d{1,3}(,\d{3})+", tok):
        raise RuntimeError(f"not a figure of kWh: {tok!r}")
    return float(tok.replace(",", ""))


def year_rows(lines, width):
    """Consecutive lines that start with a year and hold `width` cells after it, from the first such line."""
    out = []
    for ln in lines:
        toks = ln.split()
        if toks and re.fullmatch(r"(19|20)\d\d", toks[0]):
            if len(toks) - 1 != width:
                if out:
                    break
                continue
            out.append(toks)
        elif out:
            break
    years = [int(r[0]) for r in out]
    if not out or years != list(range(years[0], years[0] + len(years))):
        raise RuntimeError(f"years not consecutive: {years}")
    return out


def parse_key(text, base, rows, seen):
    title = "Production and Sales of Electricity by Energy Fiji Ltd"
    if title not in text:
        raise RuntimeError("table 3.7[A] not found")
    sold = {}
    for toks in year_rows(text[text.index(title):].splitlines()[1:], 3):
        year = toks[0]
        for var, tok, label in (("generation", toks[1], "Units Produced (kwh)"), ("sales", toks[2], "Units Sold (kwh)")):
            add(rows, seen, "efl", var, year, kwh(tok) / 1000.0, label, base)
        sold[year] = kwh(toks[2]) / 1e6
    return sold


def parse_report(text, base, rows, seen, sold, counts):
    title = "Sales of Electricity by Type of Consumers"
    if title not in text or "Units Sold" not in text:
        raise RuntimeError("Appendix III not found")
    part = text[text.index(title):]
    part = part[part.index("Units Sold"):]
    end = part.find("Sales Value")
    for toks in year_rows(part[:end if end > 0 else len(part)].splitlines()[1:], 5):
        year = toks[0]
        figs = toks[1:]
        total = float(figs[4].replace(",", ""))
        if year not in sold:
            raise RuntimeError(f"{year}: in Appendix III, not in table 3.7[A]")
        if abs(total - sold[year]) > 0.1:
            raise RuntimeError(f"{year}: Appendix III's total {total} is not table 3.7[A]'s units sold {sold[year]:.1f} GWh")
        for c, tok in zip(CONSUMERS, figs[:4]):
            if tok.lower() == "n/a":
                counts["cells n/a"] = counts.get("cells n/a", 0) + 1
                continue
            if not re.fullmatch(r"\d{1,3}(,\d{3})*\.\d", tok):
                raise RuntimeError(f"{year} {c}: not a figure: {tok!r}")
            add(rows, seen, c, "sales", year, float(tok.replace(",", "")) * 1000.0, f"{c.capitalize()} Sales, Units Sold (GWh)",
                dict(base, source_url=URL_REPORT))


def add(rows, seen, item, var, year, value, label, base):
    key = (item, var, year)
    if key in seen:
        raise RuntimeError(f"{key} given twice")
    seen.add(key)
    rows.append(dict(entity=f"fbos:fj:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(value, 3), unit="MWh",
                     freq="P1Y", geo="FJ", market="", node=label, **base, x_label=label))


def parse(key_text, report_text, base_key, base_report, counts):
    rows, seen = [], set()
    sold = parse_key(key_text, base_key, rows, seen)
    parse_report(report_text, base_report, rows, seen, sold, counts)
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no figure")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="FBoS: Fiji's electricity production and sales, 2011 to 2024")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the files again")
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
        c1, r1 = ip.fetch_raw(CONNECTOR, URL_KEY, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        c2, r2 = ip.fetch_raw(CONNECTOR, URL_REPORT, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        b1 = dict(source=SOURCE, source_url=URL_KEY, retrieved_at=r1.get("retrieved_at") or "", vintage=ip.vintage_of(r1))
        b2 = dict(source=SOURCE, source_url=URL_REPORT, retrieved_at=r2.get("retrieved_at") or "", vintage=ip.vintage_of(r2))
        counts = {}
        t = parse(text_of(c1), text_of(c2), b1, b2, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[(t.variable == "generation")].set_index("ts_utc").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): Fiji Bureau of Statistics (FBoS), Key Statistics table 3.7[A] and Electricity 2024 Appendix III, "
            f"Energy Fiji Limited's units produced and sold, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2492)",
            "Shape: series (docs/datastandard.md v0). entity fbos:fj:efl (units produced and sold) or fbos:fj:<consumer> (industrial, commercial, domestic, others: "
            "units sold); variable generation or sales; unit MWh; ts_utc the year's 1 January; freq P1Y; geo FJ; node FBoS's row label. Appendix III's heading reads "
            "kwh (000's); its totals equal 3.7[A]'s units sold in GWh (checked a year), so its figures are read as GWh.",
            f"{len(t)} rows; generation TWh: " + ", ".join(f"{k[:4]} {v:.3f}" for k, v in g.items())
            + f". Not taken: the sales' value (FJD), Appendix III's totals (checked), cells n/a {counts.get('cells n/a', 0)}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/fbos_fiji_electricity.py; the files retrieved {b1['retrieved_at']} and {b2['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL_KEY}",
            f"  access: {URL_REPORT}",
            "License: public. The report's page ii: any table or material published in this Report may be reproduced and published without the Fiji Bureau "
            f"of Statistics' prior approval; the source should always be identified and acknowledged. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Fiji Bureau of Statistics (FBoS)",
                                    report="Key Statistics table 3.7[A] and Electricity 2024 Appendix III (Energy Fiji Ltd's production and sales)",
                                    report_url=URL_REPORT, document_list="https://www.statsfiji.gov.fj/wpfd_file/2024-electricity/",
                                    license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
