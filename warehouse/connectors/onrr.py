#!/usr/bin/env python3
"""The Office of Natural Resources Revenue's public data: oil, gas and coal produced on federal and Native American
lands, a month, nationally; production on federal lands by state and county, a year; and the revenue ONRR collects
(royalties, rents, bonuses and the rest) by county, revenue type, lease type and commodity, a month (session 951, chain
054: the federal side of the U.S. production the ERW holds from EIA and BOEM).

Energy Research Warehouse (ERW) connector. Three series tables, from the files of ONRR's Natural Resources Revenue Data
(revenuedata.doi.gov, which serves them from revenuedata.onrr.gov):

    onrr_production_monthly   monthly_production.csv: entity onrr_production:<federal|native_american>:<onshore|offshore>:
                              <oil|gas|coal>; variable production; unit bbl, Mcf or short_ton (ONRR's tons); freq P1M; geo US
    onrr_production_annual    calendar_year_production.csv: entity onrr_production:<class>:<category>:<county FIPS code and
                              name, or the offshore region>:<product>; the energy products only (oil, gas, coal and its kinds, and
                              geothermal electricity, ONRR's kilowatt hours as MWh); freq P1Y; geo US-<state> or empty
    onrr_revenue_monthly      monthly_revenue.csv: entity onrr_revenue:<class>:<category>:<FIPS, region or none>:<revenue
                              type>:<lease type>:<commodity>:<product>; variable revenue; unit USD; freq P1M; geo US-<state> or
                              empty; negative values (ONRR's adjustments) kept

x_* columns keep ONRR's own fields: land class and category, state, county, FIPS code, offshore region, and in the
revenue table the revenue type, mineral lease type, commodity and product. A heading not as read, a key given twice or a
product not in the maps stops the run; nothing is filled.

    python warehouse/connectors/onrr.py [--offline] [--table NAME]

Ceiling: three requests (the files, saved in warehouse/raw/onrr/ and reused offline). ONRR's robots file disallows only
/patterns/ on both hosts. License: a work of the U.S. Department of the Interior; see license_verdicts.csv.
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

CONNECTOR = "onrr"
SOURCE = "onrr:revenue_data"
PAGE = "https://revenuedata.doi.gov/downloads/"
BASE = "https://revenuedata.onrr.gov/downloads/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MONTHLY, ANNUAL, REVENUE = "onrr_production_monthly", "onrr_production_annual", "onrr_revenue_monthly"
FILES = {MONTHLY: "monthly_production.csv", ANNUAL: "calendar_year_production.csv", REVENUE: "monthly_revenue.csv"}
HEADS = {MONTHLY: ["Date", "Land Class", "Land Category", "Commodity", "Volume"],
         ANNUAL: ["Calendar Year", "Land Class", "Land Category", "State", "County", "FIPS Code", "Offshore Region", "Product", "Volume"],
         REVENUE: ["Date", "Land Class", "Land Category", "State", "County", "FIPS Code", "Offshore Region", "Revenue Type",
                   "Mineral Lease Type", "Commodity", "Product", "Revenue"]}
MONTHLY_COMMODITIES = {"Oil Prod Vol (bbl)": ("oil", "bbl"), "Gas Prod Vol (mcf)": ("gas", "Mcf"), "Coal Prod Vol (tons)": ("coal", "short_ton")}
# the energy products of the annual file, with the unit and the scale; the minerals (salt, potash, soda ash and the rest)
# and geothermal's direct use and steam are left out
ANNUAL_PRODUCTS = {"Oil (bbl)": ("bbl", 1.0), "Gas (mcf)": ("Mcf", 1.0), "Coal (ton)": ("short_ton", 1.0),
                   "Coal-bituminous-raw (ton)": ("short_ton", 1.0), "Coal waste (sub-econ) (ton)": ("short_ton", 1.0),
                   "Coal-fines circuit (ton)": ("short_ton", 1.0),
                   "Geothermal - electrical generation (kilowatt hours)": ("MWh", 1e-3)}
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
          "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
          "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
          "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
          "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
          "Wyoming": "WY"}
PLACE_COLS = ["x_land_class", "x_land_category", "x_state", "x_county", "x_fips", "x_offshore_region"]
X_COLS = {MONTHLY: ["x_land_class", "x_land_category", "x_commodity"], ANNUAL: PLACE_COLS + ["x_product"],
          REVENUE: PLACE_COLS + ["x_revenue_type", "x_lease_type", "x_commodity", "x_product"]}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def geo_of(state):
    if not state:
        return ""
    if state not in STATES:
        raise RuntimeError(f"a state not in the map: {state!r}")
    return f"US-{STATES[state]}"


def place(r):
    # one FIPS code can carry two of ONRR's county names (Kenai (Post) and Kenai (Pre)): the name is part of the key
    if r["FIPS Code"]:
        return f"{r['FIPS Code']}_{slug(r['County'])}"
    return slug(r["Offshore Region"]) or "none"


def places(r):
    return {"x_land_class": r["Land Class"], "x_land_category": r["Land Category"], "x_state": r["State"], "x_county": r["County"],
            "x_fips": r["FIPS Code"], "x_offshore_region": r["Offshore Region"]}


def month(s):
    d = dt.datetime.strptime(s, "%m/%d/%Y")
    if d.day != 1:
        raise RuntimeError(f"a month not on its first day: {s}")
    return d.strftime("%Y-%m-01T00:00:00Z")


def build(name, frame, base):
    if list(frame.columns) != HEADS[name]:
        raise RuntimeError(f"{FILES[name]}: headings not as read: {list(frame.columns)}")
    rows = []
    for _, r in frame.iterrows():
        cls, cat = slug(r["Land Class"]), slug(r["Land Category"])
        if name == MONTHLY:
            if r["Commodity"] not in MONTHLY_COMMODITIES:
                raise RuntimeError(f"a commodity not in the map: {r['Commodity']!r}")
            what, unit = MONTHLY_COMMODITIES[r["Commodity"]]
            rows.append(dict(base, entity=f"onrr_production:{cls}:{cat}:{what}", variable="production", ts_utc=month(r["Date"]),
                             value=float(r["Volume"]), unit=unit, freq="P1M", geo="US", market="", node=f"{r['Land Class']} {r['Land Category']}, {what}",
                             x_land_class=r["Land Class"], x_land_category=r["Land Category"], x_commodity=r["Commodity"]))
        elif name == ANNUAL:
            if r["Product"] not in ANNUAL_PRODUCTS:
                continue
            unit, scale = ANNUAL_PRODUCTS[r["Product"]]
            where = f"{r['County']}, {r['State']}" if r["State"] else (r["Offshore Region"] or "no place")
            rows.append(dict(base, entity=f"onrr_production:{cls}:{cat}:{place(r)}:{slug(r['Product'])}", variable="production",
                             ts_utc=f"{int(r['Calendar Year'])}-01-01T00:00:00Z", value=float(r["Volume"]) * scale, unit=unit, freq="P1Y",
                             geo=geo_of(r["State"]), market="", node=f"{where}: {r['Product']}", x_product=r["Product"], **places(r)))
        else:
            where = f"{r['County']}, {r['State']}" if r["State"] else (r["Offshore Region"] or r["Land Category"])
            key = ":".join(slug(r[c]) or "none" for c in ("Revenue Type", "Mineral Lease Type", "Commodity", "Product"))
            rows.append(dict(base, entity=f"onrr_revenue:{cls}:{cat}:{place(r)}:{key}", variable="revenue", ts_utc=month(r["Date"]),
                             value=float(r["Revenue"]), unit="USD", freq="P1M", geo=geo_of(r["State"]), market="",
                             node=f"{where}: {r['Revenue Type']}, {r['Commodity']}" + (f", {r['Product']}" if r["Product"] else ""),
                             x_revenue_type=r["Revenue Type"], x_lease_type=r["Mineral Lease Type"], x_commodity=r["Commodity"],
                             x_product=r["Product"], **places(r)))
    t = pd.DataFrame(rows)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        d = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)].head(3)
        raise RuntimeError(f"a key given twice: {d[['entity', 'ts_utc']].values.tolist()}")
    return t


def header(name, s, run_id, base):
    span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}" if name != ANNUAL else f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
    title = {MONTHLY: "oil, gas and coal produced on federal and Native American lands, a month, nationally",
             ANNUAL: "energy produced on federal lands by state and county (and offshore region), a year",
             REVENUE: "the revenue ONRR collects (royalties, rents, bonuses and the rest) by county, revenue type, lease type and commodity, a month"}[name]
    shape = {MONTHLY: "entity onrr_production:<federal|native_american>:<onshore|offshore>:<oil|gas|coal>; variable production; unit bbl, "
                      "Mcf or short_ton (ONRR's tons); freq P1M; geo US",
             ANNUAL: "entity onrr_production:<class>:<category>:<county FIPS code or offshore region>:<product>; variable production; units bbl, "
                     "Mcf, short_ton (ONRR's tons), MWh (geothermal electricity: ONRR's kilowatt hours over 1,000); freq P1Y; geo US-<state> or empty "
                     "(offshore); the minerals and geothermal's direct use are not taken",
             REVENUE: "entity onrr_revenue:<class>:<category>:<county FIPS code, offshore region or none>:<revenue type>:<lease type>:<commodity>:"
                      "<product>; variable revenue; unit USD; freq P1M; geo US-<state> or empty; a negative value (ONRR's adjustment) kept"}[name]
    return [
        f"Energy Research Warehouse (ERW): Office of Natural Resources Revenue (ONRR), {title} (session 951)",
        f"Shape: series (docs/datastandard.md v0). {shape}; x_* ONRR's own fields.",
        f"{span}; {len(s):,} rows, {s['entity'].nunique():,} series. Values as ONRR publishes them; nothing is filled.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/onrr.py; the file retrieved {base['retrieved_at']}, last modified {base['vintage']}",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        f"Source: {SOURCE} U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads, {PAGE}",
        f"  access: {BASE}{FILES[name]}",
        "License: a work of the U.S. Department of the Interior (see license_verdicts.csv); cite ONRR, Natural Resources Revenue Data.",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ONRR's federal production and revenue")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--table", choices=sorted(FILES), action="append", help="the table(s) to write (default all three)")
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
    for name in args.table or [MONTHLY, ANNUAL, REVENUE]:
        url = BASE + FILES[name]
        try:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            frame = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
            s = build(name, frame, base)
            cols = ip.SERIES_COLS + X_COLS[name]
            s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
            ip.write_snapshot(s, name, header(name, s, run_id, base), log, cols)
            results.append(dict(table=name, market="all", status="ok", detail=f"{len(s):,} rows"))
            print(f"{name}: {len(s):,} rows, {s['entity'].nunique():,} series")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"{name} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ok = [r["table"] for r in results if r["status"] == "ok"]
        if ok:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR)",
                                    report="Natural Resources Revenue Data (production and revenue downloads)", report_url=PAGE,
                                    document_list=BASE, license="public", tables=ok)])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
