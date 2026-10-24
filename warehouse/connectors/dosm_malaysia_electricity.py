#!/usr/bin/env python3
"""Malaysia's electricity supply and consumption a month, by sector, from the Department of Statistics Malaysia's sets on
the national open data portal (session 2322, chain 108: Malaysia's electricity supply and consumption).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/dosm_malaysia_electricity_monthly.csv,
from two CSV files of data.gov.my's catalogue (pages data-catalogue/electricity_supply and electricity_consumption),
one request each:

    https://storage.data.gov.my/energy/electricity_supply.csv        date,sector,supply
    https://storage.data.gov.my/energy/electricity_consumption.csv   date,sector,consumption

Each row is a month (date the month's first day) and a sector, the value "in millions of kilowatt-hours (MKWh)" (the
catalogue's variable definitions). The variables are the file's name and the sector:

    supply_total, supply_local (with supply_local_public and supply_local_private: public and private installations),
    supply_imports, supply_distribution; consumption_total, consumption_local (with consumption_local_commercial, which
    includes industry and mining, and consumption_local_domestic, which includes public lighting), consumption_exports,
    consumption_losses

    entity      dosm:MY; geo MY; node Malaysia; unit MWh (the files' GWh times 1,000, an exact factor); ts_utc the
                month's first day at 00:00:00Z; freq P1M

The catalogue says the figures are compiled from the operational records of Tenaga Nasional Berhad (Peninsular
Malaysia), Sabah Electricity and Sarawak Energy, with the independent producers', and that the latest six months are
provisional. A header not DOSM's, a sector not in the map, a date not a month's first day, a value that is not a number
or a month and sector given twice stops the run.

    python warehouse/connectors/dosm_malaysia_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/dosm_malaysia_electricity/ with --offline. data.gov.my's robots file
allows every path to every agent and names no AI agent; storage.data.gov.my has none (404) (session 2322). License:
CC BY 4.0, as each dataset's page states ("This data is made open under the Creative Commons Attribution 4.0
International License"). Cite: Department of Statistics Malaysia, data.gov.my.
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

NAME = "dosm_malaysia_electricity_monthly"
CONNECTOR = "dosm_malaysia_electricity"
SOURCE = "dosm:electricity_supply_consumption"
PAGE = "https://data.gov.my/data-catalogue/electricity_supply"
FILES = {"supply": "https://storage.data.gov.my/energy/electricity_supply.csv",
         "consumption": "https://storage.data.gov.my/energy/electricity_consumption.csv"}
SECTORS = {"supply": {"total", "local", "local_public", "local_private", "imports", "distribution"},
           "consumption": {"total", "local", "local_commercial", "local_domestic", "exports", "losses"}}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def file_rows(kind, text, url, retrieved, vintage):
    rows = list(csv.reader(io.StringIO(text)))
    head = [h.strip() for h in rows[0]] if rows else []
    if head != ["date", "sector", kind]:
        raise RuntimeError(f"{url}: the header is not DOSM's {kind} file: {head}")
    out = []
    for r in rows[1:]:
        if not r or not "".join(r).strip():
            continue
        date, sector, cell = (x.strip() for x in r[:3])
        if not re.fullmatch(r"\d{4}-\d\d-01", date):
            raise RuntimeError(f"{url}: a date not a month's first day: {date!r}")
        if sector not in SECTORS[kind]:
            raise RuntimeError(f"{url}: a sector not in the map: {sector!r}")
        try:
            value = float(cell) * 1000.0
        except ValueError:
            raise RuntimeError(f"{url}: {date} {sector}: not a number: {cell!r}")
        out.append({"entity": "dosm:MY", "variable": f"{kind}_{sector}", "ts_utc": f"{date}T00:00:00Z", "value": value,
                    "unit": "MWh", "freq": "P1M", "geo": "MY", "market": "", "node": "Malaysia", "source": SOURCE,
                    "source_url": url, "retrieved_at": retrieved, "vintage": vintage})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a month given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DOSM (data.gov.my): Malaysia's electricity supply and consumption a month")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if not args.offline and (ip.paused("dosm") or ip.paused_host("storage.data.gov.my")):
            raise RuntimeError("DOSM is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for kind, url in FILES.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
            rows += file_rows(kind, content.decode("utf-8-sig"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((kind, rec.get("retrieved_at") or ""))
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): Department of Statistics Malaysia (data.gov.my), Malaysia's electricity supply and consumption a month by sector, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2322)",
            "Shape: series (docs/datastandard.md v0). entity dosm:MY; variable the file and its sector (supply_total, supply_local, supply_local_public, supply_local_private, supply_imports, supply_distribution; "
            "consumption_total, consumption_local, consumption_local_commercial, consumption_local_domestic, consumption_exports, consumption_losses); unit MWh (DOSM's million kWh times 1,000); "
            "ts_utc the month's first day; freq P1M; geo MY. Commercial includes industry and mining; domestic includes public lighting. The latest six months are provisional (DOSM).",
            f"{len(t)} rows, {t.variable.nunique()} variables. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/dosm_malaysia_electricity.py; the files retrieved " + "; ".join(f"{k} {r}" for k, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Department of Statistics Malaysia, Monthly Electricity Supply and Monthly Electricity Consumption (compiled from TNB, SESB, Sarawak Energy and the Energy Commission), {PAGE}",
            f"  access: {FILES['supply']} and {FILES['consumption']}",
            "License: public, CC BY 4.0 (each dataset's page on data.gov.my). Cite: Department of Statistics Malaysia, data.gov.my.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Department of Statistics Malaysia (DOSM)",
                                    report="Monthly Electricity Supply and Monthly Electricity Consumption, by sector (data.gov.my catalogue)",
                                    report_url=PAGE, document_list=" ".join(FILES.values()), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
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
