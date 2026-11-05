#!/usr/bin/env python3
"""The Census Bureau's Quarterly Services Survey (QSS), its annual benchmark dataset: the quarterly revenue and expenses
of the utilities (NAICS 22: electric power, natural gas distribution, water) and of data processing, hosting and related
services (NAICS 518, the data center industry), from 2003 (session 2264, chain 102: what the utilities and the hosting
industry take in and spend, quarter by quarter).

Energy Research Warehouse (ERW) connector. One series table from the benchmark dataset (the Census Bureau's economic
time series format: sections of categories, data types, error types, periods and data), the latest year's:

    https://www2.census.gov/services/qss/2024/qss-mf-24.csv   (fourth quarter 2003 to fourth quarter 2024)

    census_qss_utilities_hosting_quarterly   entity census_qss:<NAICS code> (22, 2211, 2212, 2213, 518); variable the
               data type's description as a slug (total_revenue, total_expenses, revenue_from_businesses,
               revenue_from_governments, revenue_from_households, and the others QSS gives in dollars), with _sa where the
               figure is seasonally adjusted; value in USD (the Census Bureau's millions times 1,000,000); ts_utc the
               quarter's first day; freq P3M; geo US; node the category as the Census Bureau names it; x_cv the
               coefficient of variation QSS gives for that figure (percent), where it gives one

Percent changes are not taken (they follow from the levels). A figure QSS marks S, N or Z, or leaves out, has no row,
counted in the header. The dataset must hold its sections (CATEGORIES, DATA TYPES, ERROR TYPES, TIME PERIODS, DATA), the
five categories by their codes, and periods as Qn-YYYY; a key given twice or a figure that does not read stops the run.
Nothing is filled. The quarters after the benchmark's last are in the current release's workbook, not taken here.

    python warehouse/connectors/census_qss.py [--offline] [--out-dir DIR]

Ceiling: one request (the dataset, asked again unless --offline). www2.census.gov's robots file sets rules for named
crawlers only (none for others); www.census.gov has no robots file. License: public (the Census Bureau's verdict on
record; a work of the U.S. government).
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "census_qss"
SOURCE = "census:qss_benchmark"
HOST = "www2.census.gov"
PAGE = "https://www.census.gov/services/qss/benchmark.html"
URL = "https://www2.census.gov/services/qss/2024/qss-mf-24.csv"
TABLE = "census_qss_utilities_hosting_quarterly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CATS = {"22T": "22", "2211T": "2211", "22121T": "2212", "2213T": "2213", "518T": "518"}
X_COLS = ["x_cv"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def sections(text):
    out = {}
    for block in text.replace("\r\n", "\n").split("\n\n"):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        if lines:
            out[lines[0].strip()] = lines[1:]
    return out


def parse(content, base, counts):
    sec = sections(content.decode("utf-8-sig", errors="replace"))
    need = ["CATEGORIES", "DATA TYPES", "ERROR TYPES", "TIME PERIODS", "DATA"]
    if [k for k in need if k not in sec]:
        raise RuntimeError(f"sections not as read: {list(sec)}")
    rd = lambda k: list(csv.DictReader(io.StringIO("\n".join(sec[k]))))
    cats = {r["cat_idx"]: (r["cat_code"], r["cat_desc"]) for r in rd("CATEGORIES")}
    want = {i: c for i, c in cats.items() if c[0] in CATS}
    if sorted(c[0] for c in want.values()) != sorted(CATS):
        raise RuntimeError(f"categories not as read: {[c[0] for c in want.values()]}")
    dts = {r["dt_idx"]: r for r in rd("DATA TYPES")}
    ets = {r["et_idx"]: r for r in rd("ERROR TYPES")}
    pers = {}
    for r in rd("TIME PERIODS"):
        m = re.fullmatch(r"Q([1-4])-(\d{4})", r["per_name"])
        if not m:
            raise RuntimeError(f"a period that does not read: {r['per_name']!r}")
        pers[r["per_idx"]] = f"{m.group(2)}-{3 * int(m.group(1)) - 2:02d}-01T00:00:00Z"
    values, cvs = {}, {}
    for r in rd("DATA"):
        if r["cat_idx"] not in want or r["geo_idx"] != "1":
            continue
        ts = pers[r["per_idx"]]
        if r["dt_idx"] != "0":
            d = dts[r["dt_idx"]]
            if d["dt_unit"] != "MLN$":
                continue
            key = (r["cat_idx"], d["dt_code"], r["is_adj"], ts)
            if key in values:
                raise RuntimeError(f"{key} given twice")
            values[key] = (r["val"], d["dt_desc"])
        else:
            e = ets[r["et_idx"]]
            if not e["err_code"].startswith("E_") or e["err_unit"] != "PCT" or "Coefficient" not in e["err_desc"]:
                continue
            cvs[(r["cat_idx"], e["err_code"][2:], r["is_adj"], ts)] = r["val"]
    out = []
    for (ci, code, adj, ts), (v, desc) in values.items():
        try:
            x = float(v)
        except ValueError:
            counts[f"marked {v}"] = counts.get(f"marked {v}", 0) + 1
            continue
        naics = CATS[want[ci][0]]
        cv = cvs.get((ci, code, adj, ts), "")
        out.append(dict(base, entity=f"census_qss:{naics}", variable=slug(desc) + ("_sa" if adj == "1" else ""), ts_utc=ts, value=x * 1e6, unit="USD",
                        freq="P3M", geo="US", market="", node=want[ci][1], x_cv=cv if re.fullmatch(r"[0-9.]+", str(cv)) else ""))
    if not out:
        raise RuntimeError("no figure")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Census Bureau QSS benchmark: utilities' and hosting's revenue and expenses, a quarter")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        s = pd.DataFrame(parse(content, base, counts))
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): U.S. Census Bureau, Quarterly Services Survey, 2024 benchmark dataset, the revenue and expenses of "
            f"the utilities (NAICS 22, 2211, 2212, 2213) and of data processing and hosting (518), {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2264)",
            "Shape: series (docs/datastandard.md v0). entity census_qss:<NAICS>; variable the data type as a slug (total_revenue, total_expenses, "
            "revenue_from_businesses, revenue_from_governments, revenue_from_households, ...), _sa where seasonally adjusted; unit USD (millions "
            "times 1,000,000); freq P3M; ts_utc the quarter's first day; geo US; x_cv the coefficient of variation, percent, where QSS gives one.",
            f"Not taken: percent changes; figures marked or left out: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. "
            "Quarters after the benchmark's last are in the current release, not here. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_qss.py; the dataset retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Census Bureau, Quarterly Services Survey, Historical Annual Benchmark Dataset (2024), {PAGE}",
            f"  access: {URL}",
            "License: public (a work of the U.S. government; see license_verdicts.csv). Source: U.S. Census Bureau, Quarterly Services Survey.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} industries, {s.variable.nunique()} variables, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Census Bureau", report="Quarterly Services Survey, Historical Annual Benchmark Dataset (2024)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
