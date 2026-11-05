#!/usr/bin/env python3
"""Curacao's electricity production a year, 2022 to 2024, as the Central Bureau of Statistics Curacao (CBS) gives it on its
statistics page "Manufacturing", from the Curacao Water and Power Company (Aqualectra) (session 2591, chain 128; the ERW
held Curacao only in EIA's international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cbs_curacao_electricity_annual.csv, from one
page (no key):

    https://www.cbs.cw/manufacturing-0

    entity      cbs_cw:aqualectra (Aqualectra's system, the island's public supply)
    variable    production
    unit        MWh (CBS's million kWh times 1,000); ts_utc the year's first day; freq P1Y; geo CW
    node        CBS's label

The page's table has two columns, "Water Production (1000 m 3)" and "Electricity Production (mln kWh)", and a row a year;
only the electricity column is taken. The page's text is read for the header and then each "<year> <water> <electricity>"
line up to its source line, which must name Aqualectra; the years must run without a gap. Nothing is filled.

    python warehouse/connectors/cbs_curacao_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/cbs_cw/ and reused unless --fresh; --offline asks nothing.
www.cbs.cw's robots file closes / to a list of named SEO agents only, none an AI agent's (session 2591). License: public.
CBS's disclaimer: its statistical data "may be used, downloaded for personal use or communicated to the public, simply on
condition that the source (Central Bureau of Statistics Curacao or CBS Curacao) be mentioned accurately and clearly"; the
figures are Aqualectra's, which the ERW cites as CBS's source.
"""

import argparse
import datetime as dt
import html
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cbs_curacao_electricity_annual"
CONNECTOR = "cbs_cw"
SOURCE = "cbs_cw:manufacturing_electricity_production"
HOST = "www.cbs.cw"
URL = "https://www.cbs.cw/manufacturing-0"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Central Bureau of Statistics Curacao (CBS Curacao), Manufacturing: electricity production (source: Curacao Water and Power Company, Aqualectra)"
HEAD = "Water Production (1000 m 3 ) Electricity Production (mln kWh)"
X_COLS = []


def page_text(content):
    t = content.decode("utf-8", "replace")
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", t)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


def parse_text(s, base):
    if s.count(HEAD) != 1:
        raise RuntimeError(f"the table's header found {s.count(HEAD)} times")
    body = s[s.index(HEAD) + len(HEAD):]
    end = body.find("Source:")
    if end < 0:
        raise RuntimeError("no source line after the table")
    src, body = body[end:end + 80], body[:end]
    if "Aqualectra" not in src:
        raise RuntimeError(f"the source is not Aqualectra: {src!r}")
    rows = re.findall(r"(\d{4}) (\d{1,3}(?:,\d{3})+) (\d+(?:\.\d+)?)", body)
    rest = re.sub(r"(\d{4}) (\d{1,3}(?:,\d{3})+) (\d+(?:\.\d+)?)", "", body).strip()
    if not rows or rest:
        raise RuntimeError(f"the table's rows are not years with two figures: {body!r}")
    years = [int(r[0]) for r in rows]
    if years != list(range(years[0], years[-1] + 1)):
        raise RuntimeError(f"the years are not a run: {years}")
    out = [dict(entity="cbs_cw:aqualectra", variable="production", ts_utc=f"{y}-01-01T00:00:00Z", value=round(float(e) * 1000, 3),
                unit="MWh", freq="P1Y", geo="CW", market="", node="Electricity Production (mln kWh)", **base)
           for y, (_, _, e) in zip(years, rows)]
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CBS Curacao: electricity production a year (Aqualectra)")
    ap.add_argument("--offline", action="store_true", help="the saved page only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the page again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse_text(page_text(content), base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["ts_utc"]).reset_index(drop=True)
        last = t.iloc[-1]
        head = [
            "Energy Research Warehouse (ERW): Central Bureau of Statistics Curacao (CBS), Manufacturing: Curacao's electricity "
            "production a year, from Aqualectra (session 2591)",
            "Shape: series (docs/datastandard.md v0). entity cbs_cw:aqualectra; variable production; unit MWh (CBS's million kWh times "
            "1,000); ts_utc the year's first day; freq P1Y; geo CW; node CBS's label.",
            f"{len(t)} rows, {t.ts_utc.min()[:4]} to {last.ts_utc[:4]}; {last.ts_utc[:4]} production {last.value / 1e3:,.1f} GWh. The water "
            "column is not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cbs_curacao_electricity.py; the page retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: public. CBS's disclaimer allows its statistical data to be used or communicated to the public on condition that "
            f"the source be mentioned accurately and clearly. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Central Bureau of Statistics Curacao (CBS)",
                                    report="Manufacturing: electricity production (source Aqualectra)", report_url=URL,
                                    document_list="https://www.cbs.cw/statistics", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
