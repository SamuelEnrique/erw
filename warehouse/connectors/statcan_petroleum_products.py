#!/usr/bin/env python3
"""Statistics Canada's monthly supply and disposition of petroleum products by province (table 25-10-0081-01): field,
refinery and renewable production, imports, exports, inter-regional receipts, stock change, refinery inputs, products
supplied and ending stocks, for 31 products from natural gas liquids to asphalt, in cubic metres (session 2378, chain
112: a second source of the session's own choosing, beside statcan_oil_gas_supply_monthly's crude oil and gas).

Energy Research Warehouse (ERW) connector. One series table from the table's full CSV download:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100081-eng.zip

    statcan_petroleum_products_monthly   entity statcan_pp:<area>:<product> (area ca or a province or territory's
               postal code, lower case; product a slug of StatCan's name); variable the supply or disposition item
               (field_production, renewable_production, refinery_production, imports, net_interregional_receipts,
               adjustments, stock_change, refinery_inputs, exports, products_supplied, ending_stocks); unit m3; ts_utc
               the month's first day; freq P1M; geo CA or CA-<province>; node the area, item and product as StatCan
               names them; x_product StatCan's product; x_parent the product it is part of (blank for the three tops:
               hydrocarbon gas liquids, other liquids, finished petroleum products); x_total yes where the product has
               parts in the table (never summed with them); x_vector StatCan's vector id; x_revised r where revised

StatCan's metadata lists "Net inter-regional receipts, supply", but its file holds no such line in October 2026, so
the table has none. Stock change is positive for a build (StatCan's note 14, whose first sentence reads the other way;
the data follow the second, and products supplied subtracts it). Refinery and blender production and inputs are net
figures and can be negative (note 13). Products supplied and adjustments are Canada's only; renewable production, field
production and ending stocks are given for a few areas (session 2380's note).

A figure StatCan marks ".." (not available), "x" (suppressed to meet the Statistics Act's confidentiality) or "F" (too
unreliable to be published) has no row, and the header counts each. A unit other than cubic metres, a scalar factor
other than units, an area, item or product not in the maps, a month that does not read or a key given twice stops the
run. Nothing is filled. The table starts in January 2019 (its surveys: Monthly Refined Petroleum Products, Crude Oil
and Natural Gas, the Monthly Renewable Fuel and Hydrogen Survey, trade and the Monthly Energy Transportation and
Storage Survey).

    python warehouse/connectors/statcan_petroleum_products.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip, asked again unless --offline, since StatCan revises it at the same address). The robots
file of www150.statcan.gc.ca asks a crawl delay of 2 seconds and disallows its framework and error paths, not /n1/ or a
.zip; it names no AI agent (session 2378). License: public (the Statistics Canada Open Licence: use, reproduce,
publish, distribute or sell, with attribution and without implying endorsement; see license_verdicts.csv). Quantities
only; no price is taken.
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "statcan_petroleum_products"
SOURCE = "statcan:25-10-0081-01"
HOST = "www150.statcan.gc.ca"
URL = "https://www150.statcan.gc.ca/n1/tbl/csv/25100081-eng.zip"
PAGE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008101"
TABLE = "statcan_petroleum_products_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_product", "x_parent", "x_total", "x_vector", "x_revised"]
AREAS = {"Canada": "CA", "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS", "New Brunswick": "NB",
         "Quebec": "QC", "Ontario": "ON", "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC", "Yukon": "YT",
         "Northwest Territories": "NT", "Nunavut": "NU"}
ITEMS = {"Field production, supply": "field_production", "Renewable fuel plant net production, supply": "renewable_production",
         "Refinery and blender net production, supply": "refinery_production", "Imports, supply": "imports",
         "Net inter-regional receipts, supply": "net_interregional_receipts", "Adjustments, supply": "adjustments",
         "Stock change, disposition": "stock_change", "Refinery and blender net inputs, disposition": "refinery_inputs",
         "Exports, disposition": "exports", "Products supplied, disposition": "products_supplied", "Ending stocks": "ending_stocks"}
# StatCan's products and the product each is part of (the metadata's parent member ids, session 2378)
PARENTS = {"Hydrocarbon gas liquids": "", "Natural gas liquids": "Hydrocarbon gas liquids", "Ethane": "Natural gas liquids",
           "Propane": "Natural gas liquids", "Butane": "Natural gas liquids", "Pentanes plus": "Natural gas liquids",
           "Refinery olefins": "Hydrocarbon gas liquids", "Other liquids": "", "Hydrogen": "Other liquids",
           "Renewable fuels": "Other liquids", "Fuel ethanol": "Renewable fuels", "Renewable fuels except fuel ethanol": "Renewable fuels",
           "Other hydrocarbons": "Other liquids", "Unfinished oils": "Other liquids", "Motor gasoline blending components": "Other liquids",
           "Aviation gasoline blending components": "Other liquids", "Finished petroleum products": "",
           "Finished motor gasoline": "Finished petroleum products", "Finished aviation gasoline": "Finished petroleum products",
           "Kerosene-type jet fuel": "Finished petroleum products", "Kerosene": "Finished petroleum products",
           "Distillate fuel oil": "Finished petroleum products", "Residual fuel oil": "Finished petroleum products",
           "Petrochemical feedstocks": "Finished petroleum products", "Special naphthas": "Finished petroleum products",
           "Lubricants": "Finished petroleum products", "Waxes": "Finished petroleum products", "Petroleum coke": "Finished petroleum products",
           "Asphalt": "Finished petroleum products", "Still gas": "Finished petroleum products", "Miscellaneous products": "Finished petroleum products"}
HAS_PARTS = {p for p in PARENTS.values() if p}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
    if names != ["25100081.csv"]:
        raise RuntimeError(f"the zip does not hold 25100081.csv alone: {z.namelist()}")
    out, seen = [], set()
    with z.open(names[0]) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            if r["UOM"] != "Cubic metres" or r["SCALAR_FACTOR"] != "units":
                raise RuntimeError(f"a unit not as read: {r['UOM']!r} {r['SCALAR_FACTOR']!r}")
            area, item, prod = r["GEO"], r["Supply and disposition"], r["Products"]
            if area not in AREAS or item not in ITEMS or prod not in PARENTS:
                raise RuntimeError(f"an area, item or product not in the maps: {area!r} {item!r} {prod!r}")
            if not re.fullmatch(r"\d{4}-\d{2}", r["REF_DATE"]):
                raise RuntimeError(f"a month that does not read: {r['REF_DATE']!r}")
            status = (r["STATUS"] or "").strip()
            if status in ("..", "x", "F"):
                counts[status] = counts.get(status, 0) + 1
                continue
            if status:
                raise RuntimeError(f"a status not in the map: {status!r}")
            code = AREAS[area]
            ent, var = f"statcan_pp:{code.lower()}:{slug(prod)}", ITEMS[item]
            key = (ent, var, r["REF_DATE"])
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(base, entity=ent, variable=var, ts_utc=f"{r['REF_DATE']}-01T00:00:00Z", value=float(r["VALUE"]),
                            unit="m3", freq="P1M", geo="CA" if code == "CA" else f"CA-{code}", market="", node=f"{area}: {item}: {prod}",
                            x_product=prod, x_parent=PARENTS[prod], x_total="yes" if prod in HAS_PARTS else "",
                            x_vector=r["VECTOR"], x_revised=(r["SYMBOL"] or "").strip()))
    if not out:
        raise RuntimeError("no row")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0081-01: petroleum products by supply and disposition, a month")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=2)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        s = pd.DataFrame(parse(content, base, counts))
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, table 25-10-0081-01, petroleum products by supply and disposition, monthly, by province, "
            f"{s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2378)",
            "Shape: series (docs/datastandard.md v0). entity statcan_pp:<area>:<product>; variable the supply or disposition item (field_production, renewable_production, refinery_production, imports, "
            "net_interregional_receipts, adjustments, stock_change, refinery_inputs, exports, products_supplied, ending_stocks); unit m3; freq P1M; ts_utc the month's first day; geo CA or CA-<province>; "
            "x_product; x_parent the product it is part of; x_total yes for a product with parts (never summed with them); x_vector; x_revised r where revised. "
            "Stock change is positive for a build; refinery production and inputs are net and can be negative; products supplied and adjustments are Canada's only; StatCan lists net inter-regional receipts but publishes none.",
            f"Figures StatCan marks .. (not available), x (suppressed for confidentiality) or F (too unreliable) have no row: "
            f"{', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_petroleum_products.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Canada, Table 25-10-0081-01, Petroleum products by supply and disposition, monthly, {PAGE}",
            f"  access: {URL}",
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table "
            "25-10-0081-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series; withheld {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Canada", report="Table 25-10-0081-01, Petroleum products by "
                                    "supply and disposition, monthly", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
