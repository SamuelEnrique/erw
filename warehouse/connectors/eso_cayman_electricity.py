#!/usr/bin/env python3
"""Grand Cayman's electricity a year since 1996: the public utility's capacity, production and consumption by class, as the
Cayman Islands' Economics and Statistics Office (ESO) gives them in Table 20.01 ("Electricity Production in Grand Cayman") of its
Compendium of Statistics 2024, chapter 20, Energy and Water Supply, from Caribbean Utilities Company's figures (session 2633,
chain 131; the ERW held the Cayman Islands in no table but EIA's international one).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eso_cayman_electricity_annual.csv, from one
workbook (no key):

    https://www.eso.ky/storage/right_page_docums/uploadFilePdf/458/Chapter%2020%20-%20Energy%20and%20Water%20Supply.XLS

    entity      eso:ky:<item>: capacity (variable capacity, MW), production (generation, MWh), and consumption by class:
                residential, industrial_commercial, public_lighting and consumption_total (consumption, MWh)
    unit        MW or MWh as the table's columns state; ts_utc the year's first day; freq P1Y; geo KY
    node        the table's column heading

The sheet ".01" is read by its title ("Electricity Production in Grand Cayman, ...") and its header row (Year, Capacity (Mws)*,
Production (Mwhrs)**, Residential, Industrial/ Commercial, Public Lighting, Total, Percent Change); every later row with a year is
a year, the sheet's blank spacing rows skipped, to the first other row (its note), the years running without a gap. Check: each year's three classes add to its total within
1 MWh. The percent change is not taken. The table excludes private generators (its note); Hurricane Ivan lowered 2004's capacity.
Table 20.02 (the Sister Islands, ending in 2016) and the water tables are not taken. Nothing is filled.

    python warehouse/connectors/eso_cayman_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/eso_ky/ and reused unless --fresh; --offline asks nothing. www.eso.ky's
robots file names * with no rule (session 2633). License: internal. ESO's site reads "COPYRIGHT (c) 2026 ESO The Economics and
Statistics Office. ALL RIGHTS RESERVED." and links no terms of reuse; internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eso_cayman_electricity_annual"
CONNECTOR = "eso_ky"
SOURCE = "eso_ky:compendium_2024_table_20_01"
HOST = "www.eso.ky"
URL = "https://www.eso.ky/storage/right_page_docums/uploadFilePdf/458/Chapter%2020%20-%20Energy%20and%20Water%20Supply.XLS"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Economics and Statistics Office, Cayman Islands, Compendium of Statistics 2024, Table 20.01: Electricity Production in "
            "Grand Cayman (source: Caribbean Utilities Company Ltd)")
TITLE = "Electricity Production in Grand Cayman"
HEADER = ["Year", "Capacity (Mws)*", "Production (Mwhrs)**", "Residential", "Industrial/ Commercial", "Public Lighting", "Total",
          "Percent Change"]
COLS = [("Capacity (Mws)*", "capacity", "capacity", "MW"), ("Production (Mwhrs)**", "production", "generation", "MWh"),
        ("Residential", "residential", "consumption", "MWh"), ("Industrial/ Commercial", "industrial_commercial", "consumption", "MWh"),
        ("Public Lighting", "public_lighting", "consumption", "MWh"), ("Total", "consumption_total", "consumption", "MWh")]
X_COLS = []


def num(v, where):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    raise RuntimeError(f"{where}: not a figure: {v!r}")


def parse_rows(rows):
    at = [i for i, r in enumerate(rows) if any(isinstance(v, str) and v.strip().startswith(TITLE) for v in r)]
    if len(at) != 1:
        raise RuntimeError(f"the title found {len(at)} times")
    hd = [i for i, r in enumerate(rows) if "Year" in [str(v).strip() for v in r]]
    if len(hd) != 1:
        raise RuntimeError("the header row not found once")
    h = [str(v).strip() for v in rows[hd[0]]]
    c0 = h.index("Year")
    if h[c0:c0 + len(HEADER)] != HEADER:
        raise RuntimeError(f"the header is {h[c0:]}")
    years = []
    for r in rows[hd[0] + 1:]:
        y = r[c0]
        if all(str(v).strip() == "" for v in r):
            continue  # the sheet's blank spacing rows, after the header and between groups of years
        if not isinstance(y, float) or y != int(y):
            break
        y = int(y)
        v = [num(r[c0 + 1 + j], f"{y} {HEADER[1 + j]}") for j in range(6)]
        if abs(v[2] + v[3] + v[4] - v[5]) > 1:
            raise RuntimeError(f"{y}: the classes make {v[2] + v[3] + v[4]:.0f} MWh, the total {v[5]}")
        years.append((y, v))
    ys = [y for y, _ in years]
    if not ys or ys != list(range(ys[0], ys[0] + len(ys))):
        raise RuntimeError(f"the years do not run without a gap: {ys[:3]} ... {ys[-3:]}")
    return years


def parse(content, base):
    wb = xlrd.open_workbook(file_contents=content)
    if ".01" not in wb.sheet_names():
        raise RuntimeError(f"no sheet .01: {wb.sheet_names()}")
    sh = wb.sheet_by_name(".01")
    return frame(parse_rows([sh.row_values(i) for i in range(sh.nrows)]), base)


def frame(years, base):
    out = [dict(entity=f"eso:ky:{item}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v[j], 3), unit=unit, freq="P1Y",
                geo="KY", market="", node=label.rstrip("*"), **base)
           for y, v in years for j, (label, item, variable, unit) in enumerate(COLS)]
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ESO: Grand Cayman's electricity capacity, production and consumption a year")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbook again")
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
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        pr = t[t.entity == "eso:ky:production"]
        head = [
            "Energy Research Warehouse (ERW): Economics and Statistics Office, Cayman Islands, Compendium of Statistics 2024, Table "
            "20.01: Grand Cayman's electricity capacity, production and consumption by class a year (session 2633)",
            "Shape: series (docs/datastandard.md v0). entity eso:ky:<item> (capacity, production, residential, industrial_commercial, "
            "public_lighting, consumption_total); variable capacity, generation or consumption; unit MW (capacity) or MWh; ts_utc the "
            "year's first day; freq P1Y; geo KY; node the table's column.",
            f"{len(t)} rows; production {pr.value.iloc[0]:,.0f} MWh in {pr.ts_utc.iloc[0][:4]}, {pr.value.iloc[-1]:,.0f} MWh in "
            f"{pr.ts_utc.iloc[-1][:4]}. Classes checked against the total each year; private generators excluded (the table's note); "
            "nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eso_cayman_electricity.py; the workbook retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. ESO's site states only its copyright line; internal until a ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Economics and Statistics Office, Cayman Islands (ESO)",
                                    report="Compendium of Statistics 2024, Table 20.01: Electricity Production in Grand Cayman",
                                    report_url=URL, document_list="https://www.eso.ky/utilities.html", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
