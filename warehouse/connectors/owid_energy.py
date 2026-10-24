#!/usr/bin/env python3
"""Our World in Data's energy dataset, the columns whose every source the ERW's license record allows: each country's
and region's electricity demand and its power sector's greenhouse gas emissions, a year, from Ember's yearly electricity
data as Our World in Data compiles it (session 2126, chain 079: the world's electricity beside the United States').

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/owid_ember_electricity_annual.csv, from Our
World in Data's catalog (no key):

    https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.csv            one row a country or region and year
    https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.codebook.csv   each column's unit and sources

Of the dataset's 130 columns, most draw on the Energy Institute's Statistical Review, a population series or historical
sources the record holds no verdict for (session 2125). Three draw on Ember alone (its yearly electricity data, global
and European, CC BY 4.0, record 133), and two of them are taken:

    electricity_demand_twh       -> electricity_demand, MWh (Our World in Data's TWh times 1,000,000)
    electricity_emissions_mtco2eq -> electricity_emissions, tCO2e (its million tonnes of CO2 equivalent times 1,000,000)

The third Ember-only column, electricity_carbon_intensity_gco2eq_per_kwh, needs a CO2-equivalent intensity unit the data
standard does not hold (kgCO2/MWh is CO2 alone), and is not taken. Every run reads the codebook first: a taken column
whose sources are no longer exactly Ember's two data sets, or whose unit is no longer TWh or million tonnes, stops the run.

    entity      owid_energy:<ISO 3166-1 alpha-3 code>, or owid_energy:<the name in snake case> for a row with no ISO code:
                a region or aggregate (Our World in Data's own, such as World and Europe, or Ember's, named "(Ember)"),
                and Kosovo (owid_energy:kosovo), which the file gives no code
    ts_utc      the year's 1 January; freq P1Y; geo blank (the codes are alpha-3; node names the country or region)
    x_*         the ISO code and Our World in Data's column name

Values as published; a blank cell has no row; nothing is filled. A header without the columns named here, a year that
is not a year, a value that is not a number or a key given twice stops the run.

    python warehouse/connectors/owid_energy.py [--offline] [--out-dir DIR]

Ceiling: two requests (the codebook and the data), reused from warehouse/raw/owid_energy/ with --offline.
catalog.ourworldindata.org's robots file allows every path (session 2125, read 285). License: Our World in Data's own work
is CC BY 4.0 and its third-party data keep their producers' terms (record 284); Ember's are CC BY 4.0 (record 133). Cite
both: "Ember (2026); Our World in Data, energy dataset".
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

NAME = "owid_ember_electricity_annual"
CONNECTOR = "owid_energy"
SOURCE = "owid:energy"
PAGE = "https://ourworldindata.org/energy"
URL = "https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.csv"
CODEBOOK = "https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.codebook.csv"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EMBER = {"Ember \N{EN DASH} Yearly Electricity Data Europe", "Ember \N{EN DASH} Yearly Electricity Data"}
TAKEN = {"electricity_demand_twh": ("electricity_demand", "MWh", "terawatt-hours"),
         "electricity_emissions_mtco2eq": ("electricity_emissions", "tCO2e", "million tonnes")}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_iso_code", "x_owid_column"]


def check_codebook(text):
    """Each taken column's sources must be exactly Ember's two data sets (any year), and its unit the expected one."""
    c = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    for col, (_, _, unit_word) in TAKEN.items():
        row = c[c["column"] == col]
        if len(row) != 1:
            raise RuntimeError(f"the codebook has no single row for {col}")
        r = row.iloc[0]
        sources = {re.sub(r"\s*\(\d{4}\)$", "", s.strip()) for s in r["source"].split(";") if s.strip()}
        if sources != EMBER:
            raise RuntimeError(f"{col}: its sources are no longer Ember's alone: {sorted(sources)}")
        if unit_word not in r["unit"]:
            raise RuntimeError(f"{col}: its unit is no longer {unit_word}: {r['unit']!r}")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build(text, url, retrieved, vintage):
    t = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    missing = [c for c in ["country", "year", "iso_code", *TAKEN] if c not in t.columns]
    if missing:
        raise RuntimeError(f"the data lack the columns {missing}")
    rows = []
    for r in t.to_dict("records"):
        if not re.fullmatch(r"\d{4}", r["year"]):
            raise RuntimeError(f"{r['country']}: a year not a year: {r['year']!r}")
        iso = r["iso_code"].strip()
        entity = f"owid_energy:{iso}" if iso else f"owid_energy:{slug(r['country'])}"
        for col, (var, unit, _) in TAKEN.items():
            v = r[col].strip()
            if v == "":
                continue
            try:
                value = float(v) * 1_000_000
            except ValueError:
                raise RuntimeError(f"{r['country']} {r['year']} {col}: not a number: {v!r}")
            rows.append({"entity": entity, "variable": var, "ts_utc": f"{r['year']}-01-01T00:00:00Z", "value": round(value, 3),
                         "unit": unit, "freq": "P1Y", "geo": "", "market": "", "node": r["country"].strip(), "source": SOURCE,
                         "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_iso_code": iso,
                         "x_owid_column": col})
    out = pd.DataFrame(rows, columns=COLS)
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Our World in Data's energy dataset: Ember's electricity demand and emissions")
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
        if not args.offline and (ip.paused("owid") or ip.paused_host("catalog.ourworldindata.org")):
            raise RuntimeError("Our World in Data is paused (warehouse/metadata/paused_sources.csv): not requested")
        book, _ = ip.fetch_raw(CONNECTOR, CODEBOOK, log, offline=args.offline, headers=UA, timeout=120)
        check_codebook(book.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        t = build(content.decode("utf-8", errors="replace"), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        by = t.groupby("variable").agg(entities=("entity", "nunique"), start=("ts_utc", "min"), end=("ts_utc", "max"), rows=("entity", "size"))
        header = [
            "Energy Research Warehouse (ERW): Our World in Data, energy dataset, the columns from Ember alone: electricity demand and the power sector's greenhouse gas emissions by country and region, a year (session 2126)",
            "Shape: series (docs/datastandard.md v0). entity owid_energy:<ISO alpha-3>, or owid_energy:<region in snake case>; variable electricity_demand (MWh, Our World in Data's TWh times 1,000,000) "
            "or electricity_emissions (tCO2e, its million tonnes of CO2 equivalent times 1,000,000); ts_utc the year's 1 January; freq P1Y; geo blank; node the country or region's name.",
            f"{len(t)} rows: " + "; ".join(f"{v} {r.entities} countries and regions, {r.start[:4]} to {r.end[:4]}, {r.rows} rows" for v, r in by.iterrows())
            + ". The dataset's other columns draw on sources the license record holds no verdict for and are not taken, but for Ember's carbon intensity, left for its unit (gCO2e/kWh, not in the data standard). A blank cell has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/owid_energy.py; the data retrieved {rec.get('retrieved_at') or ''}"
            + (f", last modified {ip.vintage_of(rec)}" if ip.vintage_of(rec) else ""),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Our World in Data, energy dataset (based on Ember's Yearly Electricity Data and Yearly Electricity Data Europe, 2026), {PAGE}",
            f"  access: {URL}",
            f"  codebook: {CODEBOOK}",
            "License: public: Our World in Data's work is CC BY 4.0; Ember's data are CC BY 4.0. Cite: Ember (2026), Yearly Electricity Data; processed by Our World in Data.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Our World in Data",
                                    report="Energy dataset (owid_energy), Ember's electricity demand and emissions columns",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME]),
                               dict(source="ember:yearly_electricity", publisher="Ember",
                                    report="Yearly Electricity Data and Yearly Electricity Data Europe (through Our World in Data)",
                                    report_url="https://ember-energy.org/data/yearly-electricity-data/", document_list=URL,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} countries and regions")
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
