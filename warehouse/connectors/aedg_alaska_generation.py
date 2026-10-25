#!/usr/bin/env python3
"""Alaska's electricity generation a month by service area and fuel, 2001 to 2021, as the Alaska Energy Data Gateway (the
Alaska Center for Energy and Power, University of Alaska Fairbanks) publishes it in its dataset "Monthly Electrical Generation
By Community" (v3.0), compiled from the Alaska Energy Statistics workbooks: the Alaska Energy Authority's Power Cost
Equalization (PCE) reports and plants' reports to EIA (session 2665, chain 133, the session's second own choice; the ERW held
Alaska's small grids only where their plants report to EIA).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/aedg_alaska_generation_monthly.csv, from one JSON
answer (no key):

    https://akenergygateway.alaska.edu/explore/data/public_monthly_generation/datasets/public_monthly_generation

    entity      aedg:ak:<service area>:<fuel> (the Gateway's service_area_geom_id and its fuel_type, as a slug)
    variable    generation
    unit        MWh, as published; ts_utc the month's first day; freq P1M; geo US-AK
    node        the service area's communities: the first in alphabetical order and how many others share its grid

The Gateway gives one record a community, month and fuel, and reports each grid's generation for every community on it, so the
same figure repeats. The connector keeps one row a service area, month and fuel, and stops if the communities of a service area
disagree on a figure. Its own check found no plant set under two service areas, so service areas do not double a grid. Kept as
published: negative figures (net generation, and the storage row's own use, "Electricity used for Energy Storage"), and the
fuel left blank in 123 service-area months (item fuel_not_given). Records with no year (communities without data) have no row.
The PCE fuel price is not taken. A count of records not the answer's total, a fuel not in the map, a month not 1 to 12 or a year
not of four digits stops the run. Nothing is filled. The table is not all of Alaska: in 2021 its service areas make 5.1 TWh, and
EIA's state total is 6.6 TWh.

    python warehouse/connectors/aedg_alaska_generation.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run (about 38 MB), saved in warehouse/raw/aedg_ak/ and reused unless --fresh; --offline asks nothing.
akenergygateway.alaska.edu's robots file closes `/search` to every reader and `/` to GPTBot and some search engines' crawlers by
name; the ERW's reader is not named (session 2665). License: CC BY 4.0 (the dataset's page): public.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "aedg_alaska_generation_monthly"
CONNECTOR = "aedg_ak"
SOURCE = "aedg_ak:public_monthly_generation_v3"
HOST = "akenergygateway.alaska.edu"
URL = "https://akenergygateway.alaska.edu/explore/data/public_monthly_generation/datasets/public_monthly_generation"
PAGE = "https://akenergygateway.alaska.edu/explore/data/public_monthly_generation"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Alaska Center for Energy and Power (ACEP) at the University of Alaska Fairbanks (UAF). Monthly Electrical Generation By "
            "Community. Version v3.0. Alaska Energy Data Gateway, 2026")
FUELS = {"Distillate Fuel Oil": "distillate_oil", "Water at Hydroelectric Turbine": "hydro", "Natural Gas": "natural_gas",
         "Jet Fuel": "jet_fuel", "Wind": "wind", "Coal": "coal", "Waste Oil": "waste_oil", "Residual Fuel Oil": "residual_oil",
         "Wood Waste Solids": "wood_waste", "Landfill Gas": "landfill_gas", "Electricity used for Energy Storage": "storage",
         "Other Gas": "other_gas", "Solar": "solar", "Agricultural By-Products": "agricultural_byproducts",
         "Other Biomass Liquids": "other_biomass_liquids", None: "fuel_not_given"}
FIELDS = ["fips_code", "name", "aea_plant_ids", "service_area_geom_id", "year", "month", "fuel_type", "service_area_pce_fuel_price",
          "service_area_generation_mwh"]
X_COLS = []


def parse(js, base):
    data = js.get("data")
    if not isinstance(data, list) or js.get("recordsTotal") != len(data):
        raise RuntimeError(f"{len(data or [])} records for a total of {js.get('recordsTotal')}")
    t = pd.DataFrame(data)
    if list(t.columns) != FIELDS:
        raise RuntimeError(f"the fields are {list(t.columns)}")
    t = t[t.year.notna()].copy()
    if t.service_area_geom_id.isna().any():
        raise RuntimeError("a record with a year and no service area")
    bad = sorted(set(t.fuel_type.dropna()) - set(k for k in FUELS if k))
    if bad:
        raise RuntimeError(f"a fuel not in the map: {bad}")
    if not t.year.astype(str).str.fullmatch(r"\d{4}").all():
        raise RuntimeError("a year not of four digits")
    m = pd.to_numeric(t.month, errors="coerce")
    if m.isna().any() or not m.between(1, 12).all() or (m != m.round()).any():
        raise RuntimeError("a month not 1 to 12")
    t["mwh"] = pd.to_numeric(t.service_area_generation_mwh, errors="coerce")
    t = t[t.mwh.notna()]
    t["fuel"] = t.fuel_type.map(lambda f: FUELS[None if pd.isna(f) else f])
    t["month"] = m.astype(int)
    key = ["service_area_geom_id", "year", "month", "fuel"]
    if (t.groupby(key).mwh.nunique() > 1).any():
        raise RuntimeError("the communities of a service area disagree on a month's figure")
    names = t.groupby("service_area_geom_id").name.apply(lambda s: sorted(set(s)))
    node = {sa: (n[0] if len(n) == 1 else f"{n[0]} and {len(n) - 1} other communities") for sa, n in names.items()}
    u = t.drop_duplicates(key)
    return pd.DataFrame(dict(entity="aedg:ak:" + u.service_area_geom_id + ":" + u.fuel, variable="generation",
                             ts_utc=u.year.astype(str) + "-" + u.month.map("{:02d}".format) + "-01T00:00:00Z", value=u.mwh.round(3),
                             unit="MWh", freq="P1M", geo="US-AK", market="", node=u.service_area_geom_id.map(node), **base))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Alaska Energy Data Gateway: Alaska's generation a month by service area and fuel")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the answer again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage="")
        t = parse(json.loads(content.decode("utf-8-sig")), base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        yr = t.groupby(t.ts_utc.str[:4]).value.sum()
        head = [
            "Energy Research Warehouse (ERW): Alaska Energy Data Gateway (ACEP, University of Alaska Fairbanks), Monthly Electrical "
            f"Generation By Community v3.0: Alaska's generation a month by service area and fuel, {t.ts_utc.min()[:4]} to "
            f"{t.ts_utc.max()[:4]}, from AEA's PCE reports and plants' reports to EIA (session 2665)",
            "Shape: series (docs/datastandard.md v0). entity aedg:ak:<service area>:<fuel>; variable generation; unit MWh; ts_utc the "
            "month's first day; freq P1M; geo US-AK; node the service area's first community and how many others share its grid.",
            f"{len(t)} rows, {t.entity.str.split(':').str[2].nunique()} service areas; the sum, TWh: "
            + ", ".join(f"{k} {v / 1e6:.2f}" for k, v in yr.items() if k in ("2001", "2011", "2021"))
            + ". One row a service area, month and fuel (the communities' repeats dropped, checked equal); negatives as published; "
            "not all of Alaska (EIA's 2021 total is 6.6 TWh); nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/aedg_alaska_generation.py; the answer retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the dataset's page: {PAGE})",
            f"License: CC BY 4.0 (the dataset's page). Cite: {CITATION}, {PAGE}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Alaska Energy Data Gateway (ACEP, University of Alaska Fairbanks)",
                                    report="Monthly Electrical Generation By Community, v3.0", report_url=PAGE,
                                    document_list="https://akenergygateway.alaska.edu/explore/data", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
