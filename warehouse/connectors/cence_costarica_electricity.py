#!/usr/bin/env python3
"""Costa Rica's official monthly generation by plant and source, from 2020, as the Centro Nacional de Control de Energia
(CENCE, the Instituto Costarricense de Electricidad's system operator, DOCSE) publishes it through its web services
(EnergiaMensualOficial) (session 2387, chain 113).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cence_costarica_generation_monthly.csv,
from one GET a year (no key):

    https://apps.grupoice.com/CenceWeb/data/sen/json/EnergiaMensualOficial?anno=<year>
    ("Consulta que devuelve el dato de generación mensual de energía en MWh de las plantas del SEN. Retorna solamente
    datos ya oficializados")

    entity      cence:<plant as a slug>
    variable    generation; interchange for CENCE's source "Intercambio" (the exchanges with the regional market, signed as
                CENCE gives them), which is not a plant's generation
    unit        MWh, as CENCE gives it; ts_utc the month's first day; freq P1M; geo CR
    node        the plant as CENCE names it; x_source CENCE's source (Hidro, Eólica, Solar, Geotérmica, Térmica,
                Biomasa, ...); x_company the operating company

Only official months are taken (CENCE's own word: the current and the previous month are under review, and this service
returns only data made official). A record without a number has no row; nothing is filled. An answer without data, a
record without its plant, month or year, a year other than the one asked, a month outside 1 to 12, or a plant and
month given twice stops the run.

    python warehouse/connectors/cence_costarica_electricity.py [--offline | --fresh] [--from 2020]

Ceiling: one request a year from 2020 to the current year, 2 seconds apart; a year an earlier run saved in
warehouse/raw is reused unless --fresh (a past year is official and no longer changes); --offline asks nothing.
apps.grupoice.com has no robots file (HTTP 404, session 2387). License: not settled. The answers carry "© 2025 ICE
Todos los Derechos Reservados" and grant no reuse; internal until a ruling or a reuse statement is read.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback
import unicodedata

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cence_costarica_generation_monthly"
CONNECTOR = "cence_electricity"
SOURCE = "cence:EnergiaMensualOficial"
HOST = "apps.grupoice.com"
API = "https://apps.grupoice.com/CenceWeb/data/sen/json/EnergiaMensualOficial"
PAGE = "https://apps.grupoice.com/CenceWeb/paginas/ServiciosWeb.html"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FIRST = 2020
CEILING, PAUSE = 8, 2
X_COLS = ["x_source", "x_company"]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(content, year, base):
    d = json.loads(content.decode("utf-8-sig") if isinstance(content, bytes) else content)
    data = d.get("data")
    if data is None:
        raise RuntimeError(f"{year}: an answer without data")
    out = []
    for r in data:
        plant, month, yr = r.get("Planta"), r.get("NMes"), r.get("Año")
        if not plant or month is None or yr is None:
            raise RuntimeError(f"{year}: a record without its plant, month or year: {r}")
        if int(yr) != year:
            raise RuntimeError(f"{year}: a record of another year: {yr}")
        if not 1 <= int(month) <= 12:
            raise RuntimeError(f"{year}: a month outside 1 to 12: {month}")
        v = r.get("MWh")
        if v is None or v == "":
            continue
        src = str(r.get("Fuente") or "").strip()
        out.append(dict(entity=f"cence:{slug(plant)}", variable="interchange" if src == "Intercambio" else "generation", ts_utc=f"{year}-{int(month):02d}-01T00:00:00Z", value=round(float(v), 3),
                        unit="MWh", freq="P1M", geo="CR", market="", node=plant.strip(), **base,
                        x_source=src, x_company=str(r.get("Empresa") or "").strip()))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="CENCE: Costa Rica's official monthly generation by plant")
    ap.add_argument("--offline", action="store_true", help="the saved years only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every year again, even one saved in warehouse/raw")
    ap.add_argument("--from", dest="first", type=int, default=FIRST)
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
    asked = [0]

    def get(year):
        url = requests.Request("GET", API, params={"anno": year}).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {url}")
            return hit
        if args.offline:
            raise RuntimeError(f"offline: {url} is not in warehouse/raw/{CONNECTOR}/")
        if asked[0] >= CEILING:
            raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
        asked[0] += 1
        return ip.fetch_raw(CONNECTOR, url, log, fresh=True, headers=UA, timeout=120, pause=PAUSE)

    try:
        rows, got = [], []
        for year in range(args.first, dt.date.today().year + 1):
            content, rec = get(year)
            url = requests.Request("GET", API, params={"anno": year}).prepare().url
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage="")
            rows += parse(content, year, base)
            got.append(f"{year} {base['retrieved_at']}")
        t = pd.DataFrame(rows)
        if t.empty:
            raise RuntimeError("no value in the answers")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            dup = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)].head(4)[["entity", "ts_utc"]].values.tolist()
            raise RuntimeError(f"a plant and month given twice: {dup}")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "generation"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.sum() / 1e6
        head = [
            "Energy Research Warehouse (ERW): CENCE (ICE's system operator, DOCSE), Costa Rica's official monthly generation by plant and source, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2387)",
            "Shape: series (docs/datastandard.md v0). entity cence:<plant>; variable generation (interchange for the source Intercambio); unit MWh; ts_utc the month's first day; freq P1M; geo CR; "
            "node the plant; x_source CENCE's source; x_company the operating company. Only official months (EnergiaMensualOficial).",
            f"{len(t)} rows, {t.entity.nunique()} plants; generation TWh a year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items())
            + ". A record without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cence_costarica_electricity.py; {asked[0]} requests of {CEILING}; the years retrieved {'; '.join(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Centro Nacional de Control de Energia (CENCE), Instituto Costarricense de Electricidad, web service EnergiaMensualOficial, {PAGE}",
            f"  access: {API}?anno=<year>",
            "License: internal (the answers carry \"© 2025 ICE Todos los Derechos Reservados\" and grant no reuse).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} plants, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; {asked[0]} requests")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Centro Nacional de Control de Energia (CENCE, ICE)",
                                    report="Web service EnergiaMensualOficial: official monthly generation by plant", report_url=PAGE,
                                    document_list=API, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
