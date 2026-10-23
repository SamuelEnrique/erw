#!/usr/bin/env python3
"""EIA's International Energy Statistics for every country and region, read from EIA's bulk file: each year's electricity
generation and capacity by source, consumption, imports, exports, net imports and distribution losses (session 909,
chain 051).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_world_electricity_annual.csv, from the
U.S. Energy Information Administration's bulk download of its International Energy Statistics:

    https://www.eia.gov/opendata/bulk/INTL.zip   (one file, INTL.txt: one JSON line a series, one a category)

The same records the API's route international gives (session 886's eia_international_electricity.py reads the U.S.,
Canada and Mexico there): 399,208 of them for electricity, 80 pages of the API's 5,000, against one request for the file.
A series id is INTL.<product>-<activity>-<country or region>-<unit>.<frequency>; only the annual series in billion kWh
(BKWH) and million kW (MK) are taken, which are electricity's (EIA's Btu, terajoule and oil-equivalent copies of the same
energy are not).

    entity    eia_intl:<EIA country or region code>:<EIA product id>, as session 886's table names them (2 electricity,
              27 nuclear, 28 fossil fuels, 29 renewables, 30 coal, 31 natural gas, 32 oil, 33 hydroelectricity, 37 wind,
              116 solar and the rest, PRODUCTS below)
    variable  generation, consumption, imports, exports, net_imports, distribution_losses (MWh: EIA's billion kWh times
              1,000,000) and capacity (MW: EIA's million kW times 1,000)
    ts_utc    the year's 1 January; freq P1Y; geo empty (EIA's three-letter codes and its regions are in the entity;
              no ISO 3166 code is guessed); node "<country or region>, <product>"; x_area country, former or region

A country or region's name is the part every one of its series' names ends with (EIA writes "<what>, <country>, Annual");
a code with fewer than two series names, a product, activity or unit not in the maps, or a key given twice stops the run.
A value EIA leaves empty or marks ("NA", "--", "ie") has no row; nothing is filled.

    python warehouse/connectors/eia_intl_bulk.py [--offline | --fresh] [--out-dir DIR]

Ceiling: one request (the file, saved in warehouse/raw/eia_intl_bulk/ and reused unless --fresh; --offline asks
nothing). EIA's robots file allows /opendata/ (it disallows /archive/). License: public (EIA, record 1 of
license_reads.csv; cite "U.S. Energy Information Administration, International Energy Statistics").
"""

import argparse
import datetime as dt
import io
import json
import os
import sys
import traceback
import zipfile
from collections import defaultdict

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_world_electricity_annual"
CONNECTOR = "eia_intl_bulk"
SOURCE = "eia:international_bulk"
URL = "https://www.eia.gov/opendata/bulk/INTL.zip"
PAGE = "https://www.eia.gov/international/data/world"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ACTIVITIES = {"12": "generation", "7": "capacity", "2": "consumption", "3": "imports", "4": "exports", "23": "net_imports",
              "9": "distribution_losses"}
UNITS = {"BKWH": ("MWh", 1e6), "MK": ("MW", 1e3)}
# the product names of session 886's table (EIA's productName in the API)
PRODUCTS = {"2": "Electricity", "27": "Nuclear", "28": "Fossil fuels", "29": "Renewables", "30": "Coal", "31": "Natural gas",
            "32": "Oil", "33": "Hydroelectricity", "34": "Non-hydroelectric renewables", "35": "Geothermal",
            "36": "Solar, tide, wave, fuel cell", "37": "Wind", "38": "Biomass and waste", "82": "Hydroelectric pumped storage",
            "116": "Solar", "117": "Tide and wave", "2890": "Other gases"}
# EIA's codes of four letters are its regions and groups, but for these former countries and parts of one
FORMER = {"CSK", "DDR", "DEUW", "SCG", "SUN", "YUG", "NLDA"}
PARTS = {"DEUO", "GBRO", "NLDO", "HITZ", "USIQ"}


def area_kind(code):
    if code in FORMER:
        return "former"
    if code in PARTS:
        return "part"
    return "country" if len(code) == 3 else "region"


def common_name(names):
    names = sorted(names)
    if len(names) < 2:
        raise RuntimeError(f"fewer than two series names to read a country's name from: {names}")
    s = names[0]
    for o in names[1:]:
        i = 0
        while i < min(len(s), len(o)) and s[-1 - i] == o[-1 - i]:
            i += 1
        s = s[len(s) - i:]
    if ", " not in s:
        raise RuntimeError(f"no common name in {names[:3]}")
    return s.split(", ", 1)[1].strip()


def read_series(content):
    z = zipfile.ZipFile(io.BytesIO(content))
    if "INTL.txt" not in z.namelist():
        raise RuntimeError(f"INTL.txt not in the file: {z.namelist()}")
    out = []
    with z.open("INTL.txt") as fh:
        for line in fh:
            d = json.loads(line)
            if "series_id" in d:
                out.append(d)
    return out


def rows(series, url, retrieved, vintage):
    names, keep = defaultdict(set), []
    for d in series:
        sid = d["series_id"]
        body, freq = sid.split(".")[1], sid.split(".")[-1]
        parts = body.split("-")
        if len(parts) != 4:
            raise RuntimeError(f"a series id not of four parts: {sid}")
        product, act, area, u = parts
        names[area].add(d["name"].rsplit(", ", 1)[0])
        if u not in UNITS or freq != "A":
            continue
        if act not in ACTIVITIES:
            raise RuntimeError(f"an activity not in the map: {sid} {d['name']}")
        if product not in PRODUCTS:
            raise RuntimeError(f"a product not in the map: {sid} {d['name']}")
        keep.append((product, act, area, u, d))
    area_name = {a: common_name(n) for a, n in names.items()}
    out = []
    for product, act, area, u, d in keep:
        unit, scale = UNITS[u]
        for period, v in d["data"]:
            v = pd.to_numeric(v, errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(entity=f"eia_intl:{area}:{product}", variable=ACTIVITIES[act], ts_utc=f"{period}-01-01T00:00:00Z",
                            value=float(v) * scale, unit=unit, freq="P1Y", geo="", market="",
                            node=f"{area_name[area]}, {PRODUCTS[product]}", source=SOURCE, source_url=url,
                            retrieved_at=retrieved, vintage=vintage, x_area=area_kind(area)))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t, len(keep)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's International Energy Statistics, every country's electricity (the bulk file)")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the file again, even one saved in warehouse/raw")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=600)
        retrieved, vintage = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        series = read_series(content)
        s, n_series = rows(series, URL, retrieved, vintage)
        cols = ip.SERIES_COLS + ["x_area"]
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        areas = s["entity"].str.split(":").str[1]
        kinds = s.assign(a=areas).drop_duplicates("a")["x_area"].value_counts()
        header = [
            "Energy Research Warehouse (ERW): EIA, International Energy Statistics, electricity of every country and region, a year, from EIA's bulk file (session 909)",
            "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country or region code>:<EIA product id: 2 electricity, 27 nuclear, "
            "28 fossil fuels, 29 renewables, 30 coal, 31 natural gas, 32 oil, 33 hydroelectricity, 37 wind, 116 solar, and the rest as node names them>; "
            "variables generation, consumption, imports, exports, net_imports, distribution_losses (MWh, EIA's billion kWh times 1,000,000) and "
            "capacity (MW, EIA's million kW times 1,000); a product's parts overlap (fossil fuels holds coal, gas and oil; renewables holds hydro, "
            "wind, solar and the rest): a sum takes one level; ts_utc the year's 1 January; freq P1Y; geo empty (no ISO code is guessed from EIA's); "
            "x_area country, former (a country that no longer exists: the Soviet Union, Yugoslavia, Czechoslovakia, the two Germanies, Serbia and "
            "Montenegro, the Netherlands Antilles), part (EIA's offshore and trade-zone parts of a country) or region (EIA's regions and groups, the "
            "world WORL among them): a sum over countries takes country and former only.",
            f"Years {span}; {n_series:,} series of EIA's, {len(s):,} rows; {s['entity'].str.split(':').str[1].nunique()} areas "
            f"({', '.join(f'{v} {k}' for k, v in kinds.items())}). Only annual series in billion kWh and million kW are taken. A value EIA leaves "
            "empty or marks (NA, --, ie) has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_intl_bulk.py; the file retrieved {retrieved}, last modified {vintage}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, International Energy Statistics (bulk download), {PAGE}",
            f"  access: {URL}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, International Energy Statistics").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="International Energy Statistics (bulk download)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} series, {span}")
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
