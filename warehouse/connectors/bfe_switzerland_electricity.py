#!/usr/bin/env python3
"""Switzerland's electricity balance a month from January 2000, as the Swiss Federal Office of Energy (SFOE, BFE)
publishes it on opendata.swiss ("ENSTAT: Elektrizitätsbilanz der Schweiz - Monatswerte-CSV") (session 2343, chain 109:
a second source of the session's own choosing; it adds imports, exports, consumption and losses to session 2272's
hourly production of Energy-Charts).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/bfe_switzerland_electricity_monthly.csv,
from one CSV (no key):

    https://www.bfe-ogd.ch/ogd35/ogd35_schweizerische_elektrizitaetsbilanz_monatswerte.csv

    entity      bfe:ch
    variable    one a column (English, from SFOE's German): run_of_river_generation, storage_hydro_generation,
                nuclear_generation, other_generation, thermal_generation, wind_generation, solar_generation,
                national_generation, pumped_storage_consumption, net_generation, imports, exports,
                national_consumption, losses, final_consumption; node SFOE's column name
    unit        MWh (the file's GWh times 1,000); ts_utc the month's first day; freq P1M; geo CH
    x_final     SFOE's "Definitiv": 1 for a final month, 0 for a provisional one

A cell SFOE writes NULL has no row (other_generation ends where thermal, wind and solar begin); nothing is filled. A
header other than the one read in session 2343, a month or a year that is not a number, a value that is not a number, or
a month given twice stops the run.

    python warehouse/connectors/bfe_switzerland_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/bfe_electricity/ and fetched again unless --offline. opendata.swiss
and www.bfe-ogd.ch have no robots file (HTTP 404, session 2343). License: opendata.swiss's terms "Open use. Must provide
the source" ("You may use this dataset for commercial purposes. You must provide the source (author, title and link to
the dataset)"); source: Swiss Federal Office of Energy.
"""

import argparse
import csv
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "bfe_switzerland_electricity_monthly"
CONNECTOR = "bfe_electricity"
SOURCE = "bfe:ogd35"
HOST = "www.bfe-ogd.ch"
URL = "https://www.bfe-ogd.ch/ogd35/ogd35_schweizerische_elektrizitaetsbilanz_monatswerte.csv"
PAGE = "https://opendata.swiss/en/dataset/enstat-elektrizitatsbilanz-der-schweiz-monatswerte-csv"
TERMS = "https://opendata.swiss/en/terms-of-use"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLUMNS = {
    "Erzeugung_Laufwerk_GWh": "run_of_river_generation",
    "Erzeugung_Speicherwerk_GWh": "storage_hydro_generation",
    "Erzeugung_Kernkraftwerk_GWh": "nuclear_generation",
    "Erzeugung_andere_GWh": "other_generation",
    "Erzeugung_Thermische_GWh": "thermal_generation",
    "Erzeugung_Windkraft_GWh": "wind_generation",
    "Erzeugung_Photovoltaik_GWh": "solar_generation",
    "Landeserzeugung_GWh": "national_generation",
    "Verbrauch_Speicherpumpen_GWh": "pumped_storage_consumption",
    "Erzeugung_netto_GWh": "net_generation",
    "Einfuhr_GWh": "imports",
    "Ausfuhr_GWh": "exports",
    "Landesverbrauch_GWh": "national_consumption",
    "Verluste_GWh": "losses",
    "Endverbrauch_GWh": "final_consumption",
}
HEADER = ["Jahr", "Monat", "Definitiv"] + list(COLUMNS)
X_COLS = ["x_final"]


def parse(content, base):
    text = content.decode("utf-8-sig") if isinstance(content, bytes) else content
    r = list(csv.reader(io.StringIO(text)))
    if not r or r[0] != HEADER:
        raise RuntimeError(f"the file's header is not the one expected: {r[0] if r else None}")
    out = []
    for line in r[1:]:
        if not line:
            continue
        rec = dict(zip(HEADER, line))
        y, m = int(rec["Jahr"]), int(rec["Monat"])
        if not 1 <= m <= 12:
            raise RuntimeError(f"a month not 1 to 12: {rec['Monat']!r}")
        final = rec["Definitiv"].strip()
        if final not in ("0", "1"):
            raise RuntimeError(f"Definitiv not 0 or 1: {final!r}")
        for col, var in COLUMNS.items():
            v = rec[col].strip()
            if v in ("", "NULL"):
                continue
            try:
                x = float(v)
            except ValueError:
                raise RuntimeError(f"{y}-{m:02d} {col}: not a number: {v!r}")
            out.append(dict(entity="bfe:ch", variable=var, ts_utc=f"{y}-{m:02d}-01T00:00:00Z", value=round(x * 1000, 3), unit="MWh",
                            freq="P1M", geo="CH", market="", node=col, **base, x_final=final))
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the file")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="SFOE: Switzerland's electricity balance, a month")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "national_consumption"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        prov = t[t.x_final == "0"].ts_utc
        head = [
            "Energy Research Warehouse (ERW): Swiss Federal Office of Energy (SFOE), ENSTAT electricity balance of Switzerland, a month, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2343)",
            "Shape: series (docs/datastandard.md v0). entity bfe:ch; variable one a column of SFOE's (generation by kind, national_generation, "
            "pumped_storage_consumption, net_generation, imports, exports, national_consumption, losses, final_consumption); unit MWh (the file's GWh "
            "times 1,000); ts_utc the month's first day; freq P1M; geo CH; node SFOE's column; x_final SFOE's Definitiv (1 final, 0 provisional).",
            f"{len(t)} rows; national consumption TWh a full year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items() if k >= "2015")
            + (f". Provisional months: {prov.min()[:7]} to {prov.max()[:7]}" if len(prov) else ". No provisional month")
            + ". A NULL cell has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bfe_switzerland_electricity.py; the file retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Swiss Federal Office of Energy, ENSTAT: Elektrizitaetsbilanz der Schweiz - Monatswerte-CSV, {PAGE}",
            f"  access: {URL}",
            f"License: public (opendata.swiss, Open use. Must provide the source, {TERMS}). Source: Swiss Federal Office of Energy.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Swiss Federal Office of Energy (SFOE)",
                                    report="ENSTAT: Electricity balance of Switzerland, monthly values (CSV)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
