#!/usr/bin/env python3
"""Statistics Canada's monthly supply and disposition of crude oil and equivalent (table 25-10-0063-01) and of natural
gas (table 25-10-0086-01), by province, in cubic metres (session 2179, chain 097: Canada's oil and gas, the largest
source of the United States' imports of both).

Energy Research Warehouse (ERW) connector. One series table from the two tables' full CSV downloads:

    https://www150.statcan.gc.ca/n1/tbl/csv/25100063-eng.zip
    https://www150.statcan.gc.ca/n1/tbl/csv/25100086-eng.zip

    statcan_oil_gas_supply_monthly   entity statcan_oil:<area> or statcan_gas:<area> (area ca, atl for the Atlantic
               provinces, or a province or territory's postal code, lower case); variable the supply or disposition item
               as a slug (its parent's slug before it where StatCan gives one name twice, as the crude table's inventories
               by fields and plants, transporters and refineries; ", supply" and ", disposition" dropped; _customers after a
               count of customers); value in m3 (crude as StatCan gives it in cubic metres; gas in thousand cubic metres,
               written times 1,000) or count; ts_utc the month's first day; freq P1M; geo CA or CA-<province>; node the
               area and item as StatCan names them; x_product crude_oil or natural_gas; x_item; x_parent the item it is part
               of (never summed with it); x_area_total yes for Canada and the Atlantic provinces; x_table; x_vector;
               x_revised r where StatCan marks the figure revised

The crude table gives each figure in cubic metres and in barrels; the cubic metres are taken and every barrel figure is
checked against them (6.2898 barrels a cubic metre, to rounding), or the run stops. The gas table's gigajoules (no unit
in the standard for them yet) and its Canadian dollars (a currency other than USD is a standing question for the owner)
are not taken, and the header counts them. Table 25-10-0055-01, the gas table StatCan marks inactive and "replaced by"
25-10-0086-01, is not taken. A figure StatCan marks ".." (not available) or "x" (suppressed to meet the Statistics Act's
confidentiality) has no row, and the header counts each. A unit or scale not in the maps, an area or item not in the
table's own metadata, or a key given twice stops the run. Nothing is filled.

    python warehouse/connectors/statcan_oil_gas.py [--offline] [--out-dir DIR]

Ceiling: two requests (the zips, asked again unless --offline, since StatCan revises them at the same address), 2
seconds apart as the robots file of www150.statcan.gc.ca asks; it disallows its framework and error paths, not /n1/.
License: public (the Statistics Canada Open Licence: use, reproduce, publish, distribute or sell, with attribution and
without implying endorsement; see license_verdicts.csv). Quantities only; no price is taken.
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

CONNECTOR = "statcan_oil_gas"
HOST = "www150.statcan.gc.ca"
TABLE = "statcan_oil_gas_supply_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# product, StatCan's table, its file stem, its title
CUBES = [("crude_oil", "25-10-0063-01", "25100063", "Supply and disposition of crude oil and equivalent"),
         ("natural_gas", "25-10-0086-01", "25100086", "Natural gas supply and disposition, monthly")]
PREFIX = {"crude_oil": "statcan_oil", "natural_gas": "statcan_gas"}
X_COLS = ["x_product", "x_item", "x_parent", "x_area_total", "x_table", "x_vector", "x_revised"]
AREAS = {"Canada": "CA", "Atlantic provinces": "ATL", "Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS",
         "New Brunswick": "NB", "Quebec": "QC", "Ontario": "ON", "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB",
         "British Columbia": "BC", "Yukon": "YT", "Northwest Territories": "NT", "Nunavut": "NU"}
SCALES = {"units": 1, "thousands": 1000}
BBL_PER_M3 = 6.2898
NOT_TAKEN = {"Gigajoules", "Canadian dollars"}


def url_of(stem):
    return f"https://www150.statcan.gc.ca/n1/tbl/csv/{stem}-eng.zip"


def page_of(table_id):
    return "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=" + table_id.replace("-", "")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def members(meta):
    """The metadata file's members: {(dimension id, member id): (name, parent member id)}."""
    lines = meta.splitlines()
    k = [i for i, l in enumerate(lines) if "Parent Member ID" in l]
    if len(k) != 1:
        raise RuntimeError("the metadata file has no member list")
    out = {}
    for r in csv.reader(lines[k[0] + 1:]):
        if not r or not r[0].strip():
            break
        out[(r[0], r[3])] = (r[1], r[4])
    return out


def item_names(m):
    """Each item's variable: its slug, after its parent's where the table gives the name twice."""
    items = {mid: v for (dim, mid), v in m.items() if dim == "2"}
    clean = {mid: re.sub(r",\s*(supply|disposition)$", "", name.strip()) for mid, (name, _) in items.items()}
    names = [slug(n) for n in clean.values()]
    out = {}
    for mid, (name, parent) in items.items():
        s = slug(clean[mid])
        if names.count(s) > 1:
            if not parent:
                raise RuntimeError(f"an item named twice without a parent: {name!r}")
            s = slug(clean[parent]) + "_" + s
        out[mid] = s
    if len(set(out.values())) != len(out):
        raise RuntimeError("two items with one variable")
    return out, items


def parse(product, table_id, stem, content, base, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    if sorted(z.namelist()) != sorted([f"{stem}.csv", f"{stem}_MetaData.csv"]):
        raise RuntimeError(f"{table_id}: the zip does not hold its two files: {z.namelist()}")
    m = members(z.open(f"{stem}_MetaData.csv").read().decode("utf-8-sig"))
    var, items = item_names(m)
    areas = {mid: name for (dim, mid), (name, _) in m.items() if dim == "1"}
    out, seen, bbl = [], set(), {}
    with z.open(f"{stem}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline="")):
            g, i, u = r["COORDINATE"].split(".")
            if g not in areas or i not in items or areas[g] != r["GEO"] or items[i][0] != r["Supply and disposition"]:
                raise RuntimeError(f"{table_id}: a row not as its metadata: {r['COORDINATE']} {r['GEO']!r} {r['Supply and disposition']!r}")
            if r["GEO"] not in AREAS:
                raise RuntimeError(f"{table_id}: an area not in the map: {r['GEO']!r}")
            if not re.fullmatch(r"\d{4}-\d{2}", r["REF_DATE"]):
                raise RuntimeError(f"{table_id}: a month that does not read: {r['REF_DATE']!r}")
            uom, status = r["UOM"], r["STATUS"].strip()
            if status and status not in ("..", "x"):
                raise RuntimeError(f"{table_id}: a status not in the map: {status!r}")
            if r["SCALAR_FACTOR"] not in SCALES:
                raise RuntimeError(f"{table_id}: a scale not in the map: {r['SCALAR_FACTOR']!r}")
            key = (r["REF_DATE"], g, i)
            if uom in NOT_TAKEN:
                counts[f"{table_id} {uom} not taken"] = counts.get(f"{table_id} {uom} not taken", 0) + 1
                continue
            if product == "crude_oil" and uom == "Barrels":
                bbl[key] = (status, r["VALUE"])
                continue
            if uom == "Cubic metres":
                unit, suffix = "m3", ""
            elif uom == "Customers":
                unit, suffix = "count", "_customers"
            else:
                raise RuntimeError(f"{table_id}: a unit not in the map: {uom!r}")
            if status:
                counts[f"{table_id} {status}"] = counts.get(f"{table_id} {status}", 0) + 1
                if product == "crude_oil":
                    bbl.setdefault(("m3",) + key, (status, ""))
                continue
            code = AREAS[r["GEO"]]
            ent = f"{PREFIX[product]}:{code.lower()}"
            v = var[i] + suffix
            k = (ent, v, r["REF_DATE"])
            if k in seen:
                raise RuntimeError(f"{table_id}: {k} given twice")
            seen.add(k)
            value = float(r["VALUE"]) * SCALES[r["SCALAR_FACTOR"]]
            if product == "crude_oil":
                bbl.setdefault(("m3",) + key, ("", value))
            parent = items[i][1]
            out.append(dict(base, entity=ent, variable=v, ts_utc=f"{r['REF_DATE']}-01T00:00:00Z", value=round(value, 3), unit=unit, freq="P1M",
                            geo="CA" if code in ("CA", "ATL") else f"CA-{code}", market="", node=f"{r['GEO']}: {items[i][0]}",
                            x_product=product, x_item=items[i][0], x_parent=var[parent] if parent else "",
                            x_area_total="yes" if code in ("CA", "ATL") else "", x_table=table_id, x_vector=r["VECTOR"],
                            x_revised=r["SYMBOL"].strip()))
    if product == "crude_oil":
        check_barrels(table_id, bbl)
    if not out:
        raise RuntimeError(f"{table_id}: no row")
    return out


def check_barrels(table_id, bbl):
    """Each barrel figure beside its cubic metres: both withheld alike, or within rounding of 6.2898 barrels a cubic metre."""
    m3 = {k[1:]: v for k, v in bbl.items() if k[0] == "m3"}
    b = {k: v for k, v in bbl.items() if k[0] != "m3"}
    if set(m3) != set(b):
        raise RuntimeError(f"{table_id}: cubic metres and barrels not given for the same figures ({len(m3)} and {len(b)})")
    for k, (bs, bv) in b.items():
        ms, mv = m3[k]
        if bs != ms:
            raise RuntimeError(f"{table_id} {k}: withheld in one unit and not the other ({ms!r}, {bs!r})")
        if not bs and abs(float(bv) - mv * BBL_PER_M3) > 0.5 + abs(mv) * BBL_PER_M3 * 1e-4:
            raise RuntimeError(f"{table_id} {k}: {bv} barrels against {mv} cubic metres")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Canada 25-10-0063-01 and 25-10-0086-01: crude oil and natural gas supply, a month")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, counts, got = [], {}, []
        for product, table_id, stem, title in CUBES:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(stem), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=2)
            base = dict(source=f"statcan:{table_id}", source_url=url_of(stem), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(product, table_id, stem, content, base, counts)
            got.append((table_id, base["retrieved_at"]))
        s = pd.DataFrame(rows)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        span = {p: (g.ts_utc.min()[:7], g.ts_utc.max()[:7]) for p, g in s.groupby("x_product")}
        head = [
            "Energy Research Warehouse (ERW): Statistics Canada, tables 25-10-0063-01 (supply and disposition of crude oil and equivalent, "
            f"{span['crude_oil'][0]} to {span['crude_oil'][1]}) and 25-10-0086-01 (natural gas supply and disposition, {span['natural_gas'][0]} "
            f"to {span['natural_gas'][1]}), monthly, by province (session 2179)",
            "Shape: series (docs/datastandard.md v0). entity statcan_oil:<area> or statcan_gas:<area>; variable the item's slug; unit m3 (gas "
            "given in thousand m3, written times 1,000) or count (customers); freq P1M; ts_utc the month's first day; geo CA or CA-<province>; "
            "node the area and item as StatCan names them; x_product; x_item; x_parent the item it is part of (never summed with it); "
            "x_area_total yes for Canada and the Atlantic provinces; x_table; x_vector; x_revised r where revised.",
            "The crude table's barrels are checked against its cubic metres (6.2898 a cubic metre, to rounding), not kept. Not taken, counted: "
            f"{', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'} (.. not available, x suppressed for confidentiality). "
            "Table 25-10-0055-01, inactive and replaced by 25-10-0086-01, is not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statcan_oil_gas.py; the files retrieved {', '.join(f'{t} {a}' for t, a in got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        ] + [f"Source: statcan:{t} Statistics Canada, Table {t}, {title}, {page_of(t)}\n  access: {url_of(stem)}" for _, t, stem, title in CUBES] + [
            "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Tables 25-10-0063-01 "
            "and 25-10-0086-01. This does not constitute an endorsement by Statistics Canada of this product.",
        ]
        head = [l for h in head for l in h.split("\n")]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} entities, {s.groupby(['entity', 'variable']).ngroups} series; {span}; not taken {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=f"statcan:{t}", publisher="Statistics Canada", report=f"Table {t}, {title}", report_url=page_of(t),
                                    document_list=page_of(t), license="public", tables=[TABLE]) for _, t, _, title in CUBES])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
