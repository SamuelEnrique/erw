#!/usr/bin/env python3
"""Brazil's electricity an hour by subsystem: hydro, thermal, wind and solar generation, load and net interchange, from
the Operador Nacional do Sistema Eletrico's open data (session 2240, chain 101: Brazil's generation by plant
type).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ons_brazil_balance_hourly.csv, from ONS's
dataset "Balanco de Energia nos Subsistemas" (dados.ons.org.br/dataset/balanco-energia-subsistema), one CSV a year on
ONS's open data bucket:

    https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_<year>.csv

Semicolon-separated, UTF-8, one line an hour and subsystem: id_subsistema, nom_subsistema, din_instante, val_gerhidraulica,
val_gertermica, val_gereolica, val_gersolar, val_carga, val_intercambio, each "em MWmed" (ONS's data dictionary: the
hour's mean MW). Taken as hydro, thermal, wind, solar, load and net_interchange (ONS's net interchange, positive an
export). As published, not reconciled (session 2240): net interchange equals generation minus load to within 1 MW in
about 96% of the hours, not all, and the four subsystems sum to SIN except in some hours, most of them in 2026, which
ONS is still making consistent.

    entity      ons:<subsystem> (N Norte, NE Nordeste, S Sul, SE Sudeste/Centro-Oeste, SIN the national interconnected
                system); node ONS's name; geo BR
    unit        MW (the hour's mean); ts_utc the hour's start in UTC; freq PT1H
    x_*         the hour in Brasilia time as ONS prints it

din_instante is Brasilia time (UTC-3, no daylight saving since 2019): ONS's files state no zone, but solar generation
peaks at 11:00 to 12:00 on their clock, local noon, not 15:00 (session 2240). An hour is placed at din_instante plus
three hours. Values as published; a blank has no row; nothing is filled. A header not ONS's, a subsystem not named here,
a stamp not in ONS's form, a value that is not a number or an hour given twice stops the run.

    python warehouse/connectors/ons_balance.py [--first 2020] [--last 2026] [--offline] [--out-dir DIR]

Ceiling: one request a year, reused from warehouse/raw/ons_balance/ with --offline. dados.ons.org.br's robots file
disallows /api/ and asks a crawl delay of 10 seconds (its dataset pages are allowed); the bucket has no robots file
(session 2240). License: CC BY, the dataset page: reuse, modification and adaptation allowed with credit to ONS and a
note of the changes made (here: reshaped from wide to long, the hour placed in UTC; no value changed).
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

NAME = "ons_brazil_balance_hourly"
CONNECTOR = "ons_balance"
SOURCE = "ons:balanco_energia_subsistema"
PAGE = "https://dados.ons.org.br/dataset/balanco-energia-subsistema"
URL = "https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_{year}.csv"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["id_subsistema", "nom_subsistema", "din_instante", "val_gerhidraulica", "val_gertermica", "val_gereolica",
          "val_gersolar", "val_carga", "val_intercambio"]
FIELDS = {"val_gerhidraulica": "hydro", "val_gertermica": "thermal", "val_gereolica": "wind", "val_gersolar": "solar",
          "val_carga": "load", "val_intercambio": "net_interchange"}
SUBSYSTEMS = {"N", "NE", "S", "SE", "SIN"}
OFFSET = pd.Timedelta(hours=3)  # Brasilia time, UTC-3, no daylight saving since 2019
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_brasilia_hour"]


def file_rows(text, url, retrieved, vintage):
    d = pd.read_csv(io.StringIO(text), sep=";", dtype=str, keep_default_na=False)
    if [c.strip() for c in d.columns] != HEADER:
        raise RuntimeError(f"{url}: the header is not ONS's: {list(d.columns)}")
    d.columns = HEADER
    sub = d.id_subsistema.str.strip()
    bad = sorted(set(sub) - SUBSYSTEMS)
    if bad:
        raise RuntimeError(f"{url}: a subsystem not named here: {bad}")
    stamp = d.din_instante.str.strip()
    if not stamp.str.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:00:00").all():
        raise RuntimeError(f"{url}: a stamp not in ONS's form: {stamp[~stamp.str.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:00:00')].iloc[0]!r}")
    ts = (pd.to_datetime(stamp, format="%Y-%m-%d %H:%M:%S") + OFFSET).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for col, var in FIELDS.items():
        raw = d[col].str.strip()
        keep = raw.ne("")
        val = pd.to_numeric(raw[keep], errors="coerce")
        if val.isna().any():
            raise RuntimeError(f"{url}: {col}: not a number: {raw[keep][val.isna()].iloc[0]!r}")
        part = pd.DataFrame({"entity": "ons:" + sub[keep], "variable": var, "ts_utc": ts[keep], "value": val.astype(float),
                             "unit": "MW", "freq": "PT1H", "geo": "BR", "market": "", "node": d.nom_subsistema[keep].str.strip(),
                             "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage,
                             "x_brasilia_hour": stamp[keep]})
        out.append(part)
    return pd.concat(out, ignore_index=True)


def finish(parts):
    t = pd.concat(parts, ignore_index=True)[COLS]
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"an hour given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ONS: Brazil's generation by source, load and interchange an hour, by subsystem")
    ap.add_argument("--first", type=int, default=2020)
    ap.add_argument("--last", type=int, default=2026)
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
        if not args.offline and (ip.paused("ons") or ip.paused_host("ons-aws-prod-opendata.s3.amazonaws.com")):
            raise RuntimeError("ONS is paused (warehouse/metadata/paused_sources.csv): not requested")
        parts, got = [], []
        for y in range(args.first, args.last + 1):
            url = URL.format(year=y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
            parts.append(file_rows(content.decode("utf-8-sig"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec)))
            got.append((y, rec.get("retrieved_at") or ""))
        t = finish(parts)
        span = t.groupby("entity").ts_utc.agg(["min", "max", "nunique"])
        header = [
            f"Energy Research Warehouse (ERW): ONS (Operador Nacional do Sistema Eletrico), Balanco de Energia nos Subsistemas, Brazil's generation by source, load and net interchange an hour by subsystem, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2240)",
            "Shape: series (docs/datastandard.md v0). entity ons:<subsystem> (N, NE, S, SE, SIN national); variable hydro, thermal, wind, solar, load, net_interchange (ONS's, positive an export; it can differ from generation minus load); "
            "unit MW, the hour's mean (ONS's MWmed); ts_utc the hour's start in UTC, from Brasilia time (UTC-3) as ONS prints it; freq PT1H; geo BR.",
            f"{len(t)} rows: " + "; ".join(f"{e} {int(r['nunique'])} hours" for e, r in span.iterrows())
            + ". ONS's files state no time zone: Brasilia time, as solar peaks at 11:00 to 12:00 on their clock. ONS revises its data after publication. A blank has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ons_balance.py; the files retrieved " + "; ".join(f"{y} {r}" for y, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} ONS, open data, Balanco de Energia nos Subsistemas (hourly), {PAGE}",
            f"  access: {URL.format(year='<year>')}",
            "License: public, CC BY (the dataset page): credit to ONS, changes noted (reshaped from wide to long, the hour placed in UTC; no value changed). Cite: ONS, Dados Abertos.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Operador Nacional do Sistema Eletrico (ONS)",
                                    report="Dados Abertos ONS, Balanco de Energia nos Subsistemas (hourly)",
                                    report_url=PAGE, document_list=URL.format(year="<year>"), license="public", tables=[NAME])])
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
