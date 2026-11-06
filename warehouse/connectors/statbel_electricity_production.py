#!/usr/bin/env python3
"""Belgium's gross electricity production by energy product each year from 2018 to 2025, as Statistics Belgium (Statbel)
gives it in its beSTAT table "Evolution Gross electricity production 2025" (session 2770, chain 140, the session's own choice:
a national statistics office the ERW did not hold, whose year runs one year past Eurostat's).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statbel_be_electricity_production_annual.csv, from
one request to beSTAT's export of the table's view (no key), a CSV:

    https://bestat.statbel.fgov.be/bestat/api/views/cd9605c7-3f71-4527-9404-40bfb81c8523/result/CSV

    entity      statbel_gep:be:total, or statbel_gep:be:<product group>:<product> (the two levels as slugs: nuclear_energy,
                solid_fossil_fuels, manufactered_gases, natural_gas, oil_and_petroleum_products, non_renewable_waste,
                renewables_and_biofuels, other_sources, each with its products, pumped hydro among the other sources)
    variable    gross_electricity_production; unit MWh (Statbel's GWh times 1,000); ts_utc the year's first day; freq P1Y;
                geo BE; node the two levels as Statbel writes them

Checks that stop the run: a header not the view's; an indicator other than gross electricity production; a year row not each year
from 2018 to 2025 for every product; a product given twice; a value not a number; the products not adding to the total within
0.5 GWh in a year. Nothing is filled.

    python warehouse/connectors/statbel_electricity_production.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statbel/ and reused unless --fresh; --offline asks nothing.
statbel.fgov.be's robots file closes Drupal's core, admin, search and user paths and names no Claude agent (session 2770, read
1552); bestat.statbel.fgov.be has no robots file (its root address refreshes to /bestat/robots.txt, which answers 404; reads
1556 and 1557). License: Statbel's CC BY 4.0 terms (read 1559): sharing and adapting for any use, commercial included, crediting
"Source: Statbel", linking the licence and stating changes.
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

NAME = "statbel_be_electricity_production_annual"
CONNECTOR = "statbel"
SOURCE = "statbel:bestat_gross_electricity_production"
HOST = "bestat.statbel.fgov.be"
URL = "https://bestat.statbel.fgov.be/bestat/api/views/cd9605c7-3f71-4527-9404-40bfb81c8523/result/CSV"
PAGE = "https://statbel.fgov.be/en/themes/energy/electricity-production"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Statbel (Directorate-General Statistics, Statistics Belgium), beSTAT, Evolution Gross electricity production 2025"
HEADER = ["All products", "Product Group", "Product Level 1", "Indicator Group", "Year", "Gigawatthour"]
YEARS = [str(y) for y in range(2018, 2026)]
TOL = 0.5  # GWh
X_COLS = []


def slug(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")


def parse(content):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(d.columns) != HEADER:
        raise RuntimeError(f"the header is not the view's: {list(d.columns)}")
    if set(d["Indicator Group"]) != {"Gross electricity production"}:
        raise RuntimeError(f"an indicator not expected: {sorted(set(d['Indicator Group']))}")
    vals = {}
    for r in d.itertuples(index=False):
        grp, prod, year, v = r[1].strip(), r[2].strip(), r[4].strip(), r[5].strip()
        key = ("total",) if not grp and not prod else (grp, prod)
        if not grp or not prod:
            if grp or prod:
                raise RuntimeError(f"a row with one level only: {grp!r} {prod!r}")
        try:
            x = float(v)
        except ValueError:
            raise RuntimeError(f"{key} {year}: not a number: {v!r}")
        if (key, year) in vals:
            raise RuntimeError(f"{key} {year} given twice")
        vals[(key, year)] = x
    keys = sorted({k for k, _ in vals})
    for k in keys:
        if sorted(y for kk, y in vals if kk == k) != YEARS:
            raise RuntimeError(f"{k}: the years are not each year from 2018 to 2025")
    if ("total",) not in keys:
        raise RuntimeError("no total row")
    for y in YEARS:
        s = sum(vals[(k, y)] for k in keys if k != ("total",))
        if abs(s - vals[(("total",), y)]) > TOL:
            raise RuntimeError(f"{y}: the products make {s:,.1f} GWh, the total {vals[(('total',), y)]:,.1f}")
    return vals, keys


def frame(vals, keys, base):
    rows = []
    for k in keys:
        ent = "statbel_gep:be:total" if k == ("total",) else f"statbel_gep:be:{slug(k[0])}:{slug(k[1])}"
        node = "All products" if k == ("total",) else f"{k[0]}: {k[1]}"
        for y in YEARS:
            rows.append(dict(entity=ent, variable="gross_electricity_production", ts_utc=f"{y}-01-01T00:00:00Z",
                             value=round(vals[(k, y)] * 1000.0, 3), unit="MWh", freq="P1Y", geo="BE", market="", node=node,
                             **base))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statbel: Belgium's gross electricity production by product, 2018 to 2025")
    ap.add_argument("--offline", action="store_true", help="the saved export only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the export again")
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
        vals, keys = parse(content)
        t = frame(vals, keys, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = {y: vals[(("total",), y)] for y in YEARS}
        head = [
            "Energy Research Warehouse (ERW): Statbel, beSTAT, Evolution Gross electricity production 2025: Belgium's gross "
            "electricity production by energy product, each year from 2018 to 2025 (session 2770)",
            "Shape: series (docs/datastandard.md v0). entity statbel_gep:be:total or statbel_gep:be:<product group>:<product>; "
            "variable gross_electricity_production; unit MWh (Statbel's GWh times 1,000); ts_utc the year's first day; freq P1Y; "
            "geo BE; node the product levels as Statbel writes them. Pumped hydro is a product of its own (other sources).",
            f"{len(t)} rows, {len(keys) - 1} products and the total; the total, GWh: " + ", ".join(f"{y} {tot[y]:,.1f}" for y in
                                                                                                    ("2018", "2021", "2025"))
            + f". The products checked against the total every year within {TOL:g} GWh; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statbel_electricity_production.py; the export retrieved "
            f"{base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            "License: CC BY 4.0 (https://statbel.fgov.be/en/cc-40). Credit: Source: Statbel; changed by the ERW (GWh written as MWh, "
            "reshaped).",
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
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Belgium (Statbel)",
                                    report="beSTAT: Evolution Gross electricity production 2025, by energy product",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
