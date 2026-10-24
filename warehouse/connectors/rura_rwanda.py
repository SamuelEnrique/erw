#!/usr/bin/env python3
"""Rwanda's electricity a quarter from July 2021: generation by plant, domestic generation, the regionally shared plants'
share, imports and the total, and electricity sold by customer category (exports among them), from the Rwanda Utilities
Regulatory Authority's quarterly Electricity Statistics Reports (session 2448, chain 118: Rwanda's generation).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/rura_rwanda_electricity_quarterly.csv,
from three reports (PDF, read with pdfplumber's table extraction), each covering five quarters, three requests:

    .../Energy_Statistics/Electricity_Statistics_Report_as_of_September_2022.pdf      (Q3 2021 to Q3 2022)
    .../Energy_Statistics/Electricity_Statistics_Report_as_of_the_First_Quarter_2023_.pdf (Q1 2022 to Q1 2023)
    .../Energy_Statistics/Electricity_Statistics_Report_as_of_the_Second_Quarter_2024.pdf (Q2 2023 to Q2 2024)
    (https://www.rura.rw/fileadmin/user_upload/RURA/Documents/Sectors/Energy/Energy_Statistics/, listed on
    https://www.rura.rw/sectors/energy/statistics)

    Table 1 "Domestic generation, regional shared and imports (kWh)": each plant's generation (entity rura:RW:<plant>,
        variable generation), and for entity rura:RW generation_domestic ("Total domestic generation"),
        generation_regional_shared ("Regional shared HPP"), imports, generation_total ("Total")
    Table 3 "Trends of electricity sold (kWh)": sales_<category> for each customer category (residential,
        non-residential, water pumping stations, water treatment plants, broadcasters, health facilities, telecom
        towers, hotels, commercial data centers, industries, street lights, Nasho own use, exports) and sales_total

    unit MWh (the reports' kWh divided by 1,000); ts_utc the quarter's first day; freq P3M; geo RW; node the plant or
    the line as the report names it. Source line of both tables: "EUCL-REG".

What the lines hold (session 2452's note): none of the reports defines "Regional shared HPP" or "Imports" or names the
plants; RURA's generation mix counts the regional line as hydro (Table 2 reproduces from Table 1 only that way). Sales
include exports as a category: generation_total less sales_exports equals RURA's "electricity supplied to the national
grid" in every quarter, and domestic sales fall 16 to 19 per cent short of it; the reports give no losses. The categories
grow over the reports: Q3 and Q4 2021 have ten and no total (the September 2022 report's figure gives their exports,
2,699 and 2,059 MWh, not taken); street lights and exports appear from Q1 2022; Nasho's own use (Nasho irrigation) from
Q2 2023.

A quarter two reports give is taken from the later report; the header counts the values that differ. A dash or a blank
cell has no row; nothing is filled. pdfplumber's rows are read, not the text layer, whose cells shift between rows.
Checks, each stopping the run: the plants add to the domestic total, and domestic, regional shared and imports to the
total, within 1 MWh; the categories add to the total sold within 1 MWh where a total is printed (the September 2022 report
prints ten categories and no total, street lights, Nasho's own use or exports, so Q3 and Q4 2021 have no sales_total and
those three categories); a table's quarters read as Qn YYYY; a value reads as a number. The system peak demand is given only in a figure and the prose, and is not taken.

    python warehouse/connectors/rura_rwanda.py [--offline] [--out-dir DIR]

Ceiling: three requests, reused from warehouse/raw/rura_rwanda/ with --offline. www.rura.rw's robots file disallows CMS
paths and a long list of named crawlers, none of them this reader or an AI agent (session 2448). License: internal until
a ruling: RURA's pages carry "(c) 2026 Rwanda Utilities Regulatory Authority" and state no terms of reuse.
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

NAME = "rura_rwanda_electricity_quarterly"
CONNECTOR = "rura_rwanda"
SOURCE = "rura:electricity_statistics_report"
PAGE = "https://www.rura.rw/sectors/energy/statistics"
BASE = "https://www.rura.rw/fileadmin/user_upload/RURA/Documents/Sectors/Energy/Energy_Statistics/"
REPORTS = ["Electricity_Statistics_Report_as_of_September_2022.pdf",               # oldest first: a later report wins
           "Electricity_Statistics_Report_as_of_the_First_Quarter_2023_.pdf",
           "Electricity_Statistics_Report_as_of_the_Second_Quarter_2024.pdf"]
TOTALS = {"total domestic generation": "generation_domestic", "regional shared hpp": "generation_regional_shared",
          "imports": "imports", "total": "generation_total"}
TOL = 1.0   # MWh
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def quarter(q, what):
    m = re.fullmatch(r"Q([1-4]) (20\d\d)", q.strip())
    if not m:
        raise RuntimeError(f"{what}: not a quarter: {q!r}")
    return f"{m.group(2)}-{3 * int(m.group(1)) - 2:02d}-01T00:00:00Z"


def num(s, what):
    s = (s or "").strip()
    if s in ("", "-"):
        return None
    if not re.fullmatch(r"\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(s.replace(",", "")) / 1000.0


def tables(content):
    """The plant table (its rows from every page it spans) and the sales table, each as (quarters, [(label, [values])])."""
    plants, sales, pq, sq = [], [], None, None
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            for t in page.extract_tables():
                rows = [[c.replace("\n", " ").strip() for c in r if c and c.strip()] for r in t]
                rows = [r for r in rows if r]
                if not rows:
                    continue
                head = rows[0]
                if head[0].lower() in ("plant name", "pant name"):
                    q = [quarter(x, "plant table") for x in head[1:]]
                    if pq and q != pq:
                        raise RuntimeError(f"the plant table's quarters differ across pages: {pq} {q}")
                    pq = q
                    plants += rows[1:]
                elif head[0].lower() == "customer category":
                    sq = [quarter(x, "sales table") for x in head[1:]]
                    sales += rows[1:]
    if not pq or not sq:
        raise RuntimeError(f"tables not found: plants {bool(pq)}, sales {bool(sq)}")
    return (pq, plants), (sq, sales)


def report_values(content, name):
    """{(entity, variable, ts): (MWh, node)} from one report, its sums checked."""
    (pq, prow), (sq, srow) = tables(content)
    out, plant_sum, tot = {}, {q: 0.0 for q in pq}, {}
    for r in prow:
        label, vals = r[0], r[1:]
        if len(vals) != len(pq):
            raise RuntimeError(f"{name} {label}: {len(vals)} values, not {len(pq)}")
        key = label.lower()
        for q, v in zip(pq, vals):
            x = num(v, f"{name} {label} {q[:7]}")
            if key in TOTALS:
                tot[(TOTALS[key], q)] = x
                if x is not None:
                    out[("rura:RW", TOTALS[key], q)] = (x, label)
            else:
                plant_sum[q] += x or 0
                if x is not None:
                    out[(f"rura:RW:{slug(label)}", "generation", q)] = (x, label)
    for q in pq:
        dom, reg, imp, total = (tot.get((v, q)) for v in ("generation_domestic", "generation_regional_shared", "imports", "generation_total"))
        if None in (dom, total):
            raise RuntimeError(f"{name} {q[:7]}: a total missing")
        if abs(plant_sum[q] - dom) > TOL:
            raise RuntimeError(f"{name} {q[:7]}: the plants add to {plant_sum[q]:.3f} MWh, domestic generation is {dom}")
        if abs(dom + (reg or 0) + (imp or 0) - total) > TOL:
            raise RuntimeError(f"{name} {q[:7]}: domestic, regional shared and imports add to {dom + (reg or 0) + (imp or 0):.3f}, the total is {total}")
    sold = {q: 0.0 for q in sq}
    total_sold = {}
    for r in srow:
        label, vals = r[0], r[1:]
        if len(vals) != len(sq):
            raise RuntimeError(f"{name} {label}: {len(vals)} values, not {len(sq)}")
        var = "sales_total" if label.lower() == "total" else "sales_" + slug(label)
        for q, v in zip(sq, vals):
            x = num(v, f"{name} {label} {q[:7]}")
            if var == "sales_total":
                total_sold[q] = x
            else:
                sold[q] += x or 0
            if x is not None:
                out[("rura:RW", var, q)] = (x, label)
    for q in sq:
        if total_sold.get(q) is None:
            continue   # the September 2022 report prints ten categories and no total (nor street lights, Nasho's own use or exports)
        if abs(sold[q] - total_sold[q]) > TOL:
            raise RuntimeError(f"{name} {q[:7]}: the categories add to {sold[q]:.3f} MWh, the total sold is {total_sold.get(q)}")
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="RURA Rwanda: electricity generation by plant, imports and sales, a quarter")
    ap.add_argument("--offline", action="store_true", help="the saved reports only, no request")
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
        if not args.offline and (ip.paused("rura") or ip.paused_host("www.rura.rw")):
            raise RuntimeError("RURA is paused (warehouse/metadata/paused_sources.csv): not requested")
        merged, diffs, got = {}, 0, []
        for rep in REPORTS:
            url = BASE + rep
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, pause=2, headers=UA, timeout=300)
            for key, (v, node) in report_values(content, rep).items():
                if key in merged and abs(merged[key][0] - v) > 1e-6:
                    diffs += 1
                    log(f"  {key[0]} {key[1]} {key[2][:7]}: {merged[key][0]} in an earlier report, {v} in {rep}")
                merged[key] = (v, node, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append(rec.get("retrieved_at") or "")
        rows = [dict(entity=e, variable=var, ts_utc=ts, value=round(v, 3), unit="MWh", freq="P3M", geo="RW", market="",
                     node=node, source=SOURCE, source_url=url, retrieved_at=ret, vintage=vin)
                for (e, var, ts), (v, node, url, ret, vin) in merged.items()]
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): Rwanda Utilities Regulatory Authority (RURA), Electricity Statistics Reports, generation by plant, imports and sales by customer category, a quarter, {t.ts_utc.min()[:7]} to {(pd.Timestamp(t.ts_utc.max()[:10]) + pd.DateOffset(months=2)).strftime('%Y-%m')} (session 2448)",
            "Shape: series (docs/datastandard.md v0). entity rura:RW:<plant> (variable generation) or rura:RW (generation_domestic, generation_regional_shared, imports, generation_total, sales_<customer category>, sales_total); "
            "unit MWh (the reports' kWh divided by 1,000); ts_utc the quarter's first day; freq P3M; geo RW; node the plant or line as the report names it. Sales include exports and Nasho's own use as categories; the regional shared line is hydro in RURA's own mix; the reports give no losses.",
            f"{len(t)} rows, {t.entity.nunique()} entities. The plants add to domestic generation, and domestic, regional shared and imports to the total, within 1 MWh; the categories add to the total sold within 1 MWh where a total is printed (Q3 and Q4 2021: ten categories and no total; street lights and exports from Q1 2022, Nasho's own use from Q2 2023). "
            f"A quarter two reports give is taken from the later report ({diffs} values differ, listed in the run log). A dash or blank has no row; nothing is filled. The system peak demand is in a figure only and is not taken.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/rura_rwanda.py; the reports retrieved {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Rwanda Utilities Regulatory Authority, Electricity Statistics Reports as of September 2022, the first quarter of 2023 and the second quarter of 2024, Table 1 (generation) and Table 3 (electricity sold), source line EUCL-REG, listed at {PAGE}",
            f"  access: {BASE}{REPORTS[-1]} and the two earlier reports",
            "License: internal. RURA's pages carry a copyright line and state no terms of reuse; internal until a ruling. Cite: Rwanda Utilities Regulatory Authority, Electricity Statistics Report.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Rwanda Utilities Regulatory Authority (RURA)",
                                    report="Electricity Statistics Reports (quarterly): generation by plant, imports, electricity sold by customer category",
                                    report_url=PAGE, document_list=BASE + REPORTS[-1], license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; {diffs} values differ between reports")
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
