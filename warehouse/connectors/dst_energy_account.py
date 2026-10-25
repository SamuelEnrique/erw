#!/usr/bin/env python3
"""Denmark's electricity supply each year from 1966 to 2025, its production and imports, and the wind, hydro and solar power
supplied, as Statistics Denmark (Danmarks Statistik) gives them in its Energy Account in specific units, StatBank table ENE1HT
(session 2756, chain 139, the session's own choice: a national statistics office the ERW did not hold, beside Energinet's hourly
production, held since session 2217).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/dst_dk_electricity_supply_annual.csv, from one
request to StatBank's open API (no key), in semicolon-separated CSV with each value's code and text:

    https://api.statbank.dk/v1/data/ENE1HT/CSV?lang=en&delimiter=Semicolon&valuePresentation=CodeAndValue
        &TILGANG=ETIL,EIMPORT,ETILVE,EPRODI&ENERGI1=EMEL,EMVIND,EMVAND,EMSOLK&Tid=*

    entity      dst_ene:dk
    variable    electricity_total_supply (ETIL, EMEL), electricity_imports (EIMPORT, EMEL), electricity_production (EPRODI,
                EMEL: the electricity produced in Denmark, from every fuel and from wind, water and sun); wind_power_supply,
                hydro_power_supply and solar_power_supply (ETILVE: the supply of renewable energy, of EMVIND, EMVAND and EMSOLK)
    unit        MWh (Statistics Denmark's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo DK; node the supply's and
                the energy type's codes and texts as given

The other cells asked for are not written: imports and the total production of wind, hydro and solar power, which StatBank gives
as 0 in every year, the renewable supply of electricity (0 in every year), and the total supply of wind, hydro and solar power,
which equals their renewable supply in every year (checked). Each of the twelve kept or checked cells' sixty years must be there,
each a whole number of GWh; a missing year, a cell given twice or a value not a whole number stops the run.

Checks, exact in every year: the electricity's total supply equals its production plus its imports; each renewable's total supply
equals its renewable supply; the cells left are 0. A check missed stops the run. Nothing is filled.

    python warehouse/connectors/dst_energy_account.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/dst_statbank/ and reused unless --fresh; --offline asks nothing.
www.dst.dk's and dst.dk's robots files close Sitecore and Extranet paths and give GPTBot a crawl delay, naming no Claude agent;
api.statbank.dk has no robots file (session 2756, reads 1498 to 1500). License: Statistics Denmark's terms ("You are free to
re-use and reproduce contents from dst.dk and statbank.dk. This includes even commercial use", with the source credited; "This
corresponds to the license known as Creative Commons, CC 4.0 BY", read 1501): public, crediting Statistics Denmark.
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "dst_dk_electricity_supply_annual"
CONNECTOR = "dst_statbank"
SOURCE = "dst:statbank_ene1ht"
HOST = "api.statbank.dk"
URL = ("https://api.statbank.dk/v1/data/ENE1HT/CSV?lang=en&delimiter=Semicolon&valuePresentation=CodeAndValue"
       "&TILGANG=ETIL,EIMPORT,ETILVE,EPRODI&ENERGI1=EMEL,EMVIND,EMVAND,EMSOLK&Tid=*")
PAGE = "https://www.statbank.dk/ENE1HT"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Statistics Denmark, StatBank table ENE1HT, Energy Account in specific units (detailed table), supply"
YEARS = list(range(1966, 2026))
KEEP = {("ETIL", "EMEL"): "electricity_total_supply", ("EIMPORT", "EMEL"): "electricity_imports",
        ("EPRODI", "EMEL"): "electricity_production", ("ETILVE", "EMVIND"): "wind_power_supply",
        ("ETILVE", "EMVAND"): "hydro_power_supply", ("ETILVE", "EMSOLK"): "solar_power_supply"}
RENEW = ("EMVIND", "EMVAND", "EMSOLK")
ZERO = [(s, e) for e in RENEW for s in ("EIMPORT", "EPRODI")] + [("ETILVE", "EMEL")]
X_COLS = []


def code(s):
    return str(s).split(" ", 1)[0]


def parse_csv(content):
    d = pd.read_csv(io.BytesIO(content), sep=";", encoding="utf-8-sig", dtype=str)
    if list(d.columns) != ["TILGANG", "ENERGI1", "TID", "INDHOLD"]:
        raise RuntimeError(f"the columns are {list(d.columns)}")
    cells, nodes = {}, {}
    for r in d.itertuples(index=False):
        s, e, y = code(r.TILGANG), code(r.ENERGI1), code(r.TID)
        if not y.isdigit():
            raise RuntimeError(f"a year not a year: {r.TID!r}")
        v = str(r.INDHOLD).strip()
        if not v.lstrip("-").isdigit():
            raise RuntimeError(f"{s} {e} {y}: not a whole number of GWh: {v!r}")
        k = (s, e, int(y))
        if k in cells:
            raise RuntimeError(f"{k} given twice")
        cells[k] = int(v)
        nodes[(s, e)] = f"{r.TILGANG}; {r.ENERGI1}"
    for s, e in list(KEEP) + ZERO + [("ETIL", x) for x in RENEW]:
        got = sorted(y for (a, b, y) in cells if (a, b) == (s, e))
        if got != YEARS:
            raise RuntimeError(f"{s} {e}: the years are not each year from 1966 to 2025")
    for y in YEARS:
        if cells[("ETIL", "EMEL", y)] != cells[("EPRODI", "EMEL", y)] + cells[("EIMPORT", "EMEL", y)]:
            raise RuntimeError(f"{y}: the electricity's total supply is not its production plus its imports")
        for x in RENEW:
            if cells[("ETIL", x, y)] != cells[("ETILVE", x, y)]:
                raise RuntimeError(f"{y} {x}: the total supply is not the renewable supply")
        for s, e in ZERO:
            if cells[(s, e, y)] != 0:
                raise RuntimeError(f"{y} {s} {e}: {cells[(s, e, y)]}, not 0")
    for (s, e, y), v in cells.items():
        if (s, e) in KEEP and v < 0:
            raise RuntimeError(f"{y} {s} {e}: negative")
    return cells, nodes


def parse(content, base):
    cells, nodes = parse_csv(content)
    rows = [dict(entity="dst_ene:dk", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=float(cells[(s, e, y)] * 1000), unit="MWh",
                 freq="P1Y", geo="DK", market="", node=nodes[(s, e)], **base) for (s, e), var in KEEP.items() for y in YEARS]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Denmark ENE1HT: Denmark's electricity supply a year from 1966")
    ap.add_argument("--offline", action="store_true", help="the saved extract only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the extract again")
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
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        p = t[t.variable == "electricity_production"].set_index("ts_utc").value
        w = t[t.variable == "wind_power_supply"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics Denmark, StatBank ENE1HT, Energy Account in specific units: Denmark's "
            f"electricity supply, production and imports, and its wind, hydro and solar power, {YEARS[0]} to {YEARS[-1]} (session 2756)",
            "Shape: series (docs/datastandard.md v0). entity dst_ene:dk; variable electricity_total_supply, electricity_imports, "
            "electricity_production, wind_power_supply, hydro_power_supply or solar_power_supply; unit MWh (GWh times 1,000); "
            "ts_utc the year's first day; freq P1Y; geo DK; node the StatBank codes and texts.",
            f"{len(t)} rows; electricity production and wind power, MWh: " + ", ".join(
                f"{k[:4]} {p[k]:,.0f} and {w[k]:,.0f}" for k in p.index if k[:4] in ("1966", "1990", "2025"))
            + ". Supply checked as production plus imports every year; zero cells left out; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/dst_energy_account.py; the extract retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the table: {PAGE})",
            "License: free re-use, commercial included, with the source credited (Statistics Denmark: \"corresponds to the license "
            "known as Creative Commons, CC 4.0 BY\"). Credit: Source: Statistics Denmark - StatBank.dk/ENE1HT.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Denmark (Danmarks Statistik)",
                                    report="StatBank ENE1HT, Energy Account in specific units (detailed table), supply",
                                    report_url=PAGE, document_list="https://api.statbank.dk/v1/tables", license="public",
                                    tables=[NAME])])  # free re-use with credit, as CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
