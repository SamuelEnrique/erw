#!/usr/bin/env python3
"""Brazil's monthly electricity consumption and consumers by state, class of consumer (captive or free) and economic
sector, January 2011 to December 2025, as the Empresa de Pesquisa Energetica (EPE) publishes them as the raw data of its
Statistical Yearbook of Electricity ("Dados do Anuario Estatistico de Energia Eletrica") (session 2446, chain 117: a third
source of the session's own choosing; the ERW held Brazil's generation plants (ANEEL) and the grid's operation (ONS), not
its consumption).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/epe_brazil_consumption_monthly.csv, from one
workbook (no key), linked from https://www.epe.gov.br/pt/publicacoes-dados-abertos/dados-abertos/dados-do-anuario-estatistico-de-energia-eletrica:

    https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/dados-abertos/Documents/Dados%20brutos.xlsx

The workbook holds one row a month and a cell of EPE's breakdown (class of consumer, system, state, sector at three
levels, voltage at three levels, consumption band at two), with its consumers and its consumption in MWh. The rows are
disjoint, each a leaf of the breakdown. The table sums them over system, the sector's lower levels, voltage and band:

    entity      epe:br:<state>:<class>:<sector> (state the two-letter code in lower case; class captive or free; sector a
                slug of EPE's first level: residencial, comercial, industrial, rural, poder_publico, servico_publico,
                iluminacao_publica, consumo_proprio)
    variable    consumption (MWh, as EPE gives it) or consumers (count, the consumers of the month)
    ts_utc      the month's first day; freq P1M; geo BR-<state>
    node        the state, class and sector as EPE names them; x_rows the number of EPE's rows summed

A blank consumption or consumer count has no part in a sum, and a cell with neither has no row. Nothing is filled. A
header not as read, a date not of the form YYYYMM01, a class or a state not in the map, or a value that is not a number
stops the run.

    python warehouse/connectors/epe_brazil_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/epe_brazil_electricity/ and fetched again unless --offline.
www.epe.gov.br's robots file closes its system paths, .aspx pages and restricted areas only, and names no AI agent
(session 2446). License: CC BY 4.0. The site's footer: "Todo o conteudo deste site esta publicado sob a licenca Creative
Commons Atribuicao 4.0 Internacional (CC BY 4.0)"; public, with EPE named.
"""

import argparse
import collections
import datetime as dt
import io
import os
import re
import sys
import traceback
import unicodedata

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "epe_brazil_consumption_monthly"
CONNECTOR = "epe_brazil_electricity"
SOURCE = "epe:anuario_dados_brutos"
HOST = "www.epe.gov.br"
URL = "https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/dados-abertos/Documents/Dados%20brutos.xlsx"
PAGE = "https://www.epe.gov.br/pt/publicacoes-dados-abertos/dados-abertos/dados-do-anuario-estatistico-de-energia-eletrica"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["Data", "TipoConsumidor", "Sistema", "UF", "Setor Econômico - N1", "Setor Econômico - N2", "Setor Econômico - N3",
          "Tipo Tensão - N1", "Tipo Tensão - N2", "Tipo Tensão - N3", "Faixa de Consumo N1", "Faixa de Consumo N2", "Consumidores", "Consumo"]
CLASSES = {"Cativo": "captive", "Livre": "free"}
STATES = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split())
X_COLS = ["x_rows"]


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def num(v, where):
    if v is None or v == "":
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise RuntimeError(f"{where}: not a number: {v!r}")
    return float(v)


def parse(rows, base):
    """rows: the sheet's rows as tuples, the header first."""
    it = iter(rows)
    head = list(next(it))
    if head[:len(HEADER)] != HEADER:
        raise RuntimeError(f"a header not as read: {head}")
    ix = {h: i for i, h in enumerate(head)}
    cons, users, nrows = collections.Counter(), collections.Counter(), collections.Counter()
    seen_c, seen_u = set(), set()
    for r in it:
        if not any(v is not None for v in r):
            continue
        d = str(r[ix["Data"]])
        if not re.fullmatch(r"(19|20)\d\d(0[1-9]|1[0-2])01", d):
            raise RuntimeError(f"a date not of the form YYYYMM01: {d!r}")
        klass, uf, sector = r[ix["TipoConsumidor"]], r[ix["UF"]], r[ix["Setor Econômico - N1"]]
        if klass not in CLASSES:
            raise RuntimeError(f"a class not in the map: {klass!r}")
        if uf not in STATES:
            raise RuntimeError(f"a state not in the map: {uf!r}")
        key = (d, uf, klass, str(sector).strip())
        c = num(r[ix["Consumo"]], f"{d} {uf} consumption")
        u = num(r[ix["Consumidores"]], f"{d} {uf} consumers")
        nrows[key] += 1
        if c is not None:
            cons[key] += c
            seen_c.add(key)
        if u is not None:
            users[key] += u
            seen_u.add(key)
    out = []
    for key in sorted(nrows):
        d, uf, klass, sector = key
        ent = f"epe:br:{uf.lower()}:{CLASSES[klass]}:{slug(sector)}"
        common = dict(entity=ent, ts_utc=f"{d[:4]}-{d[4:6]}-01T00:00:00Z", freq="P1M", geo=f"BR-{uf}", market="",
                      node=f"{uf}: {klass}: {sector}", **base, x_rows=nrows[key])
        if key in seen_c:
            out.append(dict(common, variable="consumption", value=round(cons[key], 3), unit="MWh"))
        if key in seen_u:
            out.append(dict(common, variable="consumers", value=round(users[key], 3), unit="count"))
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the workbook")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a state, class, sector and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPE: Brazil's monthly electricity consumption by state, class and sector")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        if len(wb.worksheets) != 1:
            raise RuntimeError(f"the workbook holds {len(wb.worksheets)} sheets, not one")
        t = parse(wb.worksheets[0].iter_rows(values_only=True), base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        y = t[t.variable == "consumption"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.sum() / 1e6
        head = [
            "Energy Research Warehouse (ERW): Empresa de Pesquisa Energetica (EPE), Statistical Yearbook of Electricity, raw data: monthly consumption and consumers "
            f"by state, class and sector, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2446)",
            "Shape: series (docs/datastandard.md v0). entity epe:br:<state>:<captive|free>:<sector>; variable consumption (MWh) or consumers (count); ts_utc the month's first day; "
            "freq P1M; geo BR-<state>; node the state, class and sector as EPE names them; x_rows EPE's rows summed (over system, the sector's lower levels, voltage and band).",
            f"{len(t):,} rows, {t.entity.nunique()} series; consumption TWh a year: " + ", ".join(f"{k} {v:.1f}" for k, v in y.items())
            + ". A blank has no part in a sum; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epe_brazil_electricity.py; the workbook retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} EPE, Dados do Anuario Estatistico de Energia Eletrica, Dados Brutos, {PAGE}",
            f"  access: {URL}",
            "License: CC BY 4.0 (the site's footer: all its content under Creative Commons Atribuicao 4.0 Internacional); attribution: Empresa de Pesquisa Energetica (EPE).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t):,} rows, {t.entity.nunique()} series, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Empresa de Pesquisa Energetica (EPE)",
                                    report="Statistical Yearbook of Electricity, raw data (Dados Brutos)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
