#!/usr/bin/env python3
"""EIA's Annual Energy Outlook by Electricity Market Module region: each of the 25 EMM regions' generating capacity,
additions and retirements by technology, generation by fuel, sales, prices and fuel use to 2050, in the AEO's baseline
case (session 913, chain 051: eia_aeo_electricity holds the national Tables 8 and 9 in every case).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_aeo_emm_regions.csv, from the U.S.
Energy Information Administration's API v2, route aeo/<release>, Table 54 (Electric Power Projections by Electricity
Market Module Region; the API's tableId 62), one case:

    https://api.eia.gov/v2/aeo/<release>/data/?frequency=annual&data[]=value&facets[tableId][]=62&facets[scenario][]=<case>

    entity    eia_aeo_<release>_emm:<regionId>:<seriesId>; regionId 5-1 to 5-25 the EMM regions, 5-0 the United States
    variable  value; node "<region>: <series name>"; ts_utc the projection year's 1 January; freq P1Y; geo empty (a region
              spans states) except US for 5-0
    unit      GW as MW (times 1,000); billion kWh as MWh (times 1,000,000); cents per kWh as USD/kWh (times 0.01); USD per
              MMBtu as given; quadrillion Btu as TBtu (times 1,000); x_dollar_year the AEO's real dollars (2025) or nominal
    x_*       the API's scenario and its name, history flag, region id and name

These are EIA's projections, not observations: the header says so, and nothing is filled or interpolated. The case is
AEO2026's Counterfactual Baseline (cb2026), the case EIA's tables lead with; AEO2026 names no Reference case. Table 54's
emissions (million short tons and short tons) are not taken: short tons are not in the standard's unit vocabulary. A
unit not in the map stops the run, as does a page count that does not reach the API's total.

    python warehouse/connectors/eia_aeo_regions.py [--offline | --fresh] [--case cb2026]

Ceiling: 17 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Annual Energy Outlook <release>").
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_aeo_emm_regions"
CONNECTOR = "eia_aeo_regions"
SOURCE = "eia:aeo_regions"
API = "https://api.eia.gov/v2/aeo/"
PAGE = "https://www.eia.gov/outlooks/aeo/"
RELEASE, TABLE, CASE = "2026", "62", "cb2026"
CEILING, PAUSE, RETRY_WAIT = 17, 3, 60
UNITS = {"GW": ("MW", 1000.0, ""), "BkWh": ("MWh", 1e6, ""), "nom cents/kWh": ("USD/kWh", 0.01, "nominal"),
         "nom $/MMBtu": ("USD/MMBtu", 1.0, "nominal"), "quads": ("TBtu", 1000.0, "")}
NOT_TAKEN = {"MMst": "million short tons", "st": "short tons"}
X_COLS = ["x_scenario", "x_scenario_name", "x_history", "x_region", "x_region_name", "x_dollar_year"]


def unit_of(u):
    """(the ERW's unit, the factor, the dollar year) for one of the API's units; None for a unit not taken."""
    if u in NOT_TAKEN:
        return None
    if u in UNITS:
        return UNITS[u]
    year, _, rest = u.partition(" ")
    if year.isdigit() and rest == "cents/kWh":   # "2025 cents/kWh": the AEO's real dollars
        return ("USD/kWh", 0.01, year)
    if year.isdigit() and rest == "$/MMBtu":
        return ("USD/MMBtu", 1.0, year)
    raise RuntimeError(f"a unit not in the map: {u!r}")


def rows(data, url, retrieved):
    out, skipped = [], {}
    for r in data:
        u = unit_of(r["unit"])
        if u is None:
            skipped[r["unit"]] = skipped.get(r["unit"], 0) + 1
            continue
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, factor, dollars = u
        region = r["regionId"]
        out.append(dict(entity=f"eia_aeo_{RELEASE}_emm:{region}:{r['seriesId']}", variable="value",
                        ts_utc=f"{int(r['period'])}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y",
                        geo="US" if region == "5-0" else "", market="", node=f"{r.get('regionName', '')}: {r.get('seriesName', '')}",
                        source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                        x_scenario=r["scenario"], x_scenario_name=r.get("scenarioDescription", ""), x_history=r.get("history", ""),
                        x_region=region, x_region_name=r.get("regionName", ""), x_dollar_year=dollars))
    return out, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA Annual Energy Outlook, Table 54 by EMM region, one case")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
    ap.add_argument("--case", default=CASE, help=f"the AEO case (default {CASE})")
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
    asked = [0]

    def get(params):
        url = requests.Request("GET", API + f"{RELEASE}/data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0])["response"], ip.redact(url)
        if args.offline:
            raise RuntimeError(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(url, timeout=180)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r.json()["response"], ip.redact(r.url)
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"EIA answered HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        got, skipped, offset, total = [], {}, 0, None
        while True:
            resp, url = get({"api_key": key, "frequency": "annual", "data[]": "value", "facets[tableId][]": TABLE,
                             "facets[scenario][]": args.case, "length": 5000, "offset": offset,
                             "sort[0][column]": "regionId", "sort[0][direction]": "asc",
                             "sort[1][column]": "seriesId", "sort[1][direction]": "asc",
                             "sort[2][column]": "period", "sort[2][direction]": "asc"})
            total = int(resp["total"])
            out, sk = rows(resp["data"], url.split("&length")[0], retrieved)
            got += out
            for k, v in sk.items():
                skipped[k] = skipped.get(k, 0) + v
            offset += len(resp["data"])
            log(f"  offset {offset:,} of {total:,}")
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} records read of the {total:,} EIA counts")
        s = pd.DataFrame(got)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        s = s[ip.SERIES_COLS + X_COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        regions = s[s.x_region != "5-0"].x_region.nunique()
        span = f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}"
        header = [
            f"Energy Research Warehouse (ERW): EIA Annual Energy Outlook {RELEASE}, Table 54, electric power projections by Electricity Market Module region, case {args.case} (session 913)",
            f"Shape: series (docs/datastandard.md v0). entity eia_aeo_{RELEASE}_emm:<regionId>:<seriesId> (regionId 5-1 to 5-25 the EMM regions, 5-0 the United States); "
            "variable value; node '<region>: <series name>'; ts_utc the year's 1 January; freq P1Y; geo empty for a region (it spans states), US for 5-0. "
            "GW given as MW, billion kWh as MWh, cents/kWh as USD/kWh, quads as TBtu, USD/MMBtu as given (x_dollar_year the AEO's real dollars or nominal). "
            "A series' parts overlap (a total and its technologies): a sum takes one level.",
            f"PROJECTIONS: EIA's, case {args.case} ({s.x_scenario_name.iloc[0]}); AEO{RELEASE} names no Reference case. Years {span}; {regions} regions and the U.S.; "
            f"{total:,} records of EIA's, {len(s):,} rows. Not taken: " + (", ".join(f"{n:,} rows in {NOT_TAKEN[u]}" for u, n in skipped.items()) or "none")
            + " (emissions; short tons are not in the standard's units). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_aeo_regions.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Energy Outlook {RELEASE}, Table 54 (API v2, route aeo/{RELEASE}, tableId {TABLE}), {PAGE}",
            f"  access: {API}{RELEASE}/data/?frequency=annual&data[]=value&facets[tableId][]={TABLE}&facets[scenario][]={args.case}",
            f'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Energy Outlook {RELEASE}").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Energy Outlook (API v2, Table 54 by EMM region)", report_url=PAGE,
                                    document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"AEO{RELEASE} {args.case}: {len(s):,} rows"))
        print(f"{NAME}: AEO{RELEASE} {args.case}, {len(s):,} rows, {s.entity.nunique():,} series, {span}; {asked[0]} requests; not taken {skipped}")
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
