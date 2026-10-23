#!/usr/bin/env python3
"""EIA's International Energy Statistics for every country and region, read from EIA's bulk file: each year's electricity
generation and capacity by source, consumption, imports, exports, net imports and distribution losses (session 909,
chain 051), and each year's petroleum and natural gas production, consumption, trade and stocks (session 923, chain 052).

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

A second table, warehouse/output/eia_world_oil_gas_annual.csv (--table eia_world_oil_gas_annual), from the same file: the
annual series in thousand barrels a day (TBPD, as kbbl/d), billion cubic feet (BCF, as bcf) and million barrels (MBBL,
stocks, as kbbl times 1,000), with the activities production, consumption, imports, exports, stocks and bunker consumption
(13) and the products in OIL_GAS_PRODUCTS. EIA's copies of the same quantities in cubic metres, tonnes, Btu, terajoules and
oil equivalent are not taken. The file holds no reserves.

A third table, warehouse/output/eia_world_oil_monthly.csv (--table eia_world_oil_monthly), from the same file: the monthly
series (.M) of petroleum production (crude oil, NGPL, other liquids, refinery gain and their totals), refined products'
consumption (thousand barrels a day, as kbbl/d) and stocks (million barrels, as kbbl times 1,000); ts_utc the month's
first day. The OECD's imports by source and the tonne copies are not taken.

Two more tables (session 937, chain 053), from the same file: warehouse/output/eia_world_coal_annual.csv (--table
eia_world_coal_annual: coal and its kinds' production, consumption, imports and exports in thousand short tons, as
short_ton times 1,000, and coal reserves in million short tons, as short_ton times 1,000,000) and
warehouse/output/eia_world_energy_co2_annual.csv (--table eia_world_energy_co2_annual: total primary energy production and
consumption, in all and by source, in quadrillion Btu, as TBtu times 1,000, and energy-related CO2 emissions by fuel in
million metric tonnes, as tCO2 times 1,000,000). In these two, a series whose product or activity is not the table's
(the same units hold other products' copies) is passed over, not an error; the products' maps are below.

    python warehouse/connectors/eia_intl_bulk.py [--offline | --fresh] [--out-dir DIR] [--table NAME]

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
OIL_GAS_ACTIVITIES = {"1": "production", "2": "consumption", "3": "imports", "4": "exports", "5": "stocks",
                      "13": "bunker_consumption"}
OIL_GAS_UNITS = {"TBPD": ("kbbl/d", 1.0), "BCF": ("bcf", 1.0), "MBBL": ("kbbl", 1e3)}
# EIA's product names (the API's productName, as its series names give them)
OIL_GAS_PRODUCTS = {"3": "Gross natural gas", "26": "Dry natural gas", "43": "Vented and flared natural gas", "48": "Reinjected natural gas",
                    "5": "Petroleum and other liquids", "53": "Total petroleum and other liquids", "54": "Refined petroleum products",
                    "55": "Crude oil, NGPL, and other liquids", "56": "Refinery processing gain", "57": "Crude oil including lease condensate",
                    "58": "NGPL", "59": "Other liquids", "62": "Motor gasoline", "63": "Jet fuel", "64": "Kerosene",
                    "65": "Distillate fuel oil", "66": "Residual fuel oil", "67": "Liquefied petroleum gases (LPG)",
                    "68": "Other refined products", "79": "Biofuels", "80": "Ethanol", "81": "Biodiesel", "13": "LPG and ethane",
                    "6798": "LPG and ethane, refinery", "6799": "LPG, non-refinery", "6899": "LPG", "8399": "Ethane, non-refinery",
                    "8499": "Ethane"}
OIL_GAS = "eia_world_oil_gas_annual"
OIL_MONTHLY = "eia_world_oil_monthly"
IMPORTS_BY_SOURCE = {"78", "781", "782", "783", "784", "785", "786", "787", "788", "789"}  # the OECD's and seven importers' gross imports, by source: not taken
MONTHLY_PRODUCTS = {k: OIL_GAS_PRODUCTS[k] for k in ("5", "53", "54", "55", "56", "57", "58", "59")}
COAL = "eia_world_coal_annual"
COAL_PRODUCTS = {"7": "Coal", "11": "Anthracite", "12": "Bituminous", "14": "Lignite", "119": "Subbituminous", "130": "Metallurgical coal",
                 "21": "Metallurgical coke"}
ENERGY = "eia_world_energy_co2_annual"
ENERGY_PRODUCTS = {"44": "Total energy", "4411": "Total energy from coal", "4413": "Total energy from natural gas",
                   "4415": "Total energy from petroleum and other liquids", "4417": "Total energy from nuclear",
                   "4418": "Total energy from renewables and other", "4419": "Total energy from nuclear, renewables, and other",
                   "4008": "CO2 emissions, all fuels", "4002": "CO2 emissions, coal and coke", "4006": "CO2 emissions, petroleum and other liquids",
                   "4010": "CO2 emissions, consumed natural gas", "1": "CO2 emissions, coal and coke (by product)",
                   "5": "CO2 emissions, petroleum and other liquids (by product)", "3002": "CO2 emissions, natural gas"}
# the tables whose units other products share: a series not of the table's products or activities is passed over
LOOSE = {COAL, ENERGY}
# (activities, units, products, the series' frequency letter)
SPECS = {NAME: (ACTIVITIES, UNITS, PRODUCTS, "A"), OIL_GAS: (OIL_GAS_ACTIVITIES, OIL_GAS_UNITS, OIL_GAS_PRODUCTS, "A"),
         OIL_MONTHLY: ({"1": "production", "2": "consumption", "5": "stocks"}, {"TBPD": ("kbbl/d", 1.0), "MBBL": ("kbbl", 1e3)},
                       MONTHLY_PRODUCTS, "M"),
         COAL: ({"1": "production", "2": "consumption", "3": "imports", "4": "exports", "6": "reserves"},
                {"TST": ("short_ton", 1e3), "MST": ("short_ton", 1e6)}, COAL_PRODUCTS, "A"),
         ENERGY: ({"1": "production", "2": "consumption", "8": "emissions"}, {"QBTU": ("TBtu", 1e3), "MMTCD": ("tCO2", 1e6)},
                  ENERGY_PRODUCTS, "A")}
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


def rows(series, url, retrieved, vintage, table=NAME):
    activities, units, products, want = SPECS[table]
    names, keep = defaultdict(set), []
    for d in series:
        sid = d["series_id"]
        body, freq = sid.split(".")[1], sid.split(".")[-1]
        parts = body.split("-")
        if len(parts) != 4:
            raise RuntimeError(f"a series id not of four parts: {sid}")
        product, act, area, u = parts
        names[area].add(d["name"].rsplit(", ", 1)[0])
        if u not in units or freq != want:
            continue
        if table == OIL_MONTHLY and product in IMPORTS_BY_SOURCE:
            continue
        if table in LOOSE and (product not in products or act not in activities):
            continue
        if act not in activities:
            raise RuntimeError(f"an activity not in the map: {sid} {d['name']}")
        if product not in products:
            raise RuntimeError(f"a product not in the map: {sid} {d['name']}")
        keep.append((product, act, area, u, d))
    area_name = {a: common_name(n) for a, n in names.items()}
    out = []
    for product, act, area, u, d in keep:
        unit, scale = units[u]
        for period, v in d["data"]:
            v = pd.to_numeric(v, errors="coerce")
            if pd.isna(v):
                continue
            if want == "M":
                if len(period) != 6:
                    raise RuntimeError(f"a monthly period not of the form 202606: {period!r} in {d['series_id']}")
                ts, fq = f"{period[:4]}-{period[4:]}-01T00:00:00Z", "P1M"
            else:
                ts, fq = f"{period}-01-01T00:00:00Z", "P1Y"
            out.append(dict(entity=f"eia_intl:{area}:{product}", variable=activities[act], ts_utc=ts,
                            value=float(v) * scale, unit=unit, freq=fq, geo="", market="",
                            node=f"{area_name[area]}, {products[product]}", source=SOURCE, source_url=url,
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
    ap.add_argument("--table", default=NAME, choices=sorted(SPECS), help=f"the table to write (default {NAME})")
    args = ap.parse_args(argv)
    name = args.table
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
        s, n_series = rows(series, URL, retrieved, vintage, name)
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
        if name in (COAL, ENERGY):
            kinds_text = f"{s['entity'].str.split(':').str[1].nunique()} areas ({', '.join(f'{v} {k}' for k, v in kinds.items())})"
            if name == COAL:
                header[:3] = [
                    "Energy Research Warehouse (ERW): EIA, International Energy Statistics, coal of every country and region, a year, from EIA's bulk file (session 937)",
                    "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country or region code>:<EIA product id: 7 coal, 11 anthracite, 12 "
                    "bituminous, 14 lignite, 119 subbituminous, 130 metallurgical coal, 21 metallurgical coke>; variables production, consumption, imports, "
                    "exports (short_ton, EIA's thousand short tons times 1,000) and reserves (short_ton, EIA's million short tons times 1,000,000; product 7 "
                    "only); coal holds its kinds: a sum takes one level; ts_utc the year's 1 January; freq P1Y; geo empty; x_area as in "
                    "eia_world_electricity_annual: a sum over countries takes country and former only.",
                    f"Years {span}; {n_series:,} series of EIA's, {len(s):,} rows; {kinds_text}. Only annual series in thousand and million short tons "
                    "are taken (EIA's tonne, Btu, terajoule and oil-equivalent copies are not). A value EIA leaves empty or marks has no row; nothing is filled.",
                ]
            else:
                header[:3] = [
                    "Energy Research Warehouse (ERW): EIA, International Energy Statistics, total primary energy and energy-related CO2 emissions of every country and region, a year, from EIA's bulk file (session 937)",
                    "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country or region code>:<EIA product id: 44 total energy, 4411 to 4419 "
                    "total energy by source; 4008 CO2 from all fuels, 4002 coal and coke, 4006 petroleum and other liquids, 4010 consumed natural gas, and "
                    "EIA's by-product copies 1, 5 and 3002>; variables production and consumption (TBtu, EIA's quadrillion Btu times 1,000) and emissions "
                    "(tCO2, EIA's million metric tonnes of CO2 times 1,000,000); a total holds its parts: a sum takes one level; ts_utc the year's 1 January; "
                    "freq P1Y; geo empty; x_area as in eia_world_electricity_annual: a sum over countries takes country and former only.",
                    f"Years {span}; {n_series:,} series of EIA's, {len(s):,} rows; {kinds_text}. Only annual series in quadrillion Btu and million metric "
                    "tonnes of CO2 of these products are taken. A value EIA leaves empty or marks has no row; nothing is filled.",
                ]
        if name == OIL_MONTHLY:
            kinds_text = f"{s['entity'].str.split(':').str[1].nunique()} areas ({', '.join(f'{v} {k}' for k, v in kinds.items())})"
            span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
            header[:3] = [
                "Energy Research Warehouse (ERW): EIA, International Energy Statistics, petroleum production, consumption and stocks of every country and region, a month, from EIA's bulk file (session 929)",
                "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country or region code>:<EIA product id: 57 crude oil including lease "
                "condensate, 58 NGPL, 59 other liquids, 55 crude oil, NGPL and other liquids, 56 refinery processing gain, 53 total petroleum and other "
                "liquids, 54 refined petroleum products (consumption), 5 petroleum and other liquids (stocks)>; variables production and consumption "
                "(kbbl/d, EIA's thousand barrels a day) and stocks (kbbl, EIA's million barrels times 1,000); a product's parts overlap (55 holds 57, 58 "
                "and 59; 53 holds 55 and 56): a sum takes one level; ts_utc the month's first day; freq P1M; geo empty; x_area as in "
                "eia_world_electricity_annual: a sum over countries takes country and former only.",
                f"Months {span}; {n_series:,} series of EIA's, {len(s):,} rows; {kinds_text}. Only monthly series in thousand barrels a day and million "
                "barrels are taken (the OECD's imports by source and the tonne copies are not). A value EIA leaves empty or marks has no row; nothing is filled.",
            ]
        if name == OIL_GAS:
            kinds_text = f"{s['entity'].str.split(':').str[1].nunique()} areas ({', '.join(f'{v} {k}' for k, v in kinds.items())})"
            header[:3] = [
                "Energy Research Warehouse (ERW): EIA, International Energy Statistics, petroleum and natural gas of every country and region, a year, from EIA's bulk file (session 923)",
                "Shape: series (docs/datastandard.md v0). entity eia_intl:<EIA country or region code>:<EIA product id: 57 crude oil including lease "
                "condensate, 53 total petroleum and other liquids, 5 petroleum and other liquids (consumption, stocks), 54 refined petroleum products and "
                "62 to 68 each product, 79 to 81 biofuels, 13 and 6798 to 8499 LPG and ethane, 26 dry natural gas, 3 gross natural gas, 43 vented and "
                "flared, 48 reinjected, as node names them>; variables production, consumption, imports, exports, bunker_consumption (kbbl/d for liquids, "
                "EIA's thousand barrels a day; bcf for gas, EIA's billion cubic feet a year) and stocks (kbbl, EIA's million barrels times 1,000); a "
                "product's parts overlap (55 holds 57, 58 and 59; 53 holds 55 and 56): a sum takes one level; ts_utc the year's 1 January; freq P1Y; "
                "geo empty (no ISO code is guessed from EIA's); x_area country, former, part or region, as in eia_world_electricity_annual: a sum over "
                "countries takes country and former only.",
                f"Years {span}; {n_series:,} series of EIA's, {len(s):,} rows; {kinds_text}. Only annual series in thousand barrels a day, billion cubic "
                "feet and million barrels are taken (EIA's cubic metre, tonne, Btu, terajoule and oil-equivalent copies are not); the file holds no "
                "reserves. A value EIA leaves empty or marks (NA, --, ie) has no row; nothing is filled.",
            ]
        ip.write_snapshot(s, name, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="International Energy Statistics (bulk download)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[name])])
        results.append(dict(table=name, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{name}: {len(s):,} rows, {s['entity'].nunique()} series, {span}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=args.table, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
