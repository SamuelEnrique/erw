#!/usr/bin/env python3
"""EIA's Annual Energy Outlook: electricity supply, prices and generating capacity to 2050, every case (session 490).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_aeo_electricity.csv, from the U.S.
Energy Information Administration's API v2 (route aeo/<release>), Tables 8 (Electricity Supply, Disposition, Prices,
and Emissions) and 9 (Electricity Generating Capacity) of the newest release the API lists (AEO2026 on 21 October
2026), in every case (scenario) it publishes, each named:

    https://api.eia.gov/v2/aeo/<release>/data/?frequency=annual&data[]=value&facets[tableId][]=<8|9>&facets[scenario][]=<case>

    entity    eia_aeo_<release>:<seriesId>:<scenario>; the series' own id and the case's id (cb2026, higheldmd, ...)
    variable  value; node the series' name; ts_utc the projection year's 1 January; freq P1Y
    unit      GW as MW (times 1,000); billion kWh as MWh (times 1,000,000); cents per kWh as USD/kWh (times 0.01), with
              x_dollar_year the AEO's real dollars (2025) or "nominal"
    x_*       the API's table, scenario and its name, history flag, region

These are EIA's projections, not observations: the header says so, and nothing is filled or interpolated. AEO2026 names
no "Reference case"; its cases are taken as EIA names them. Table 8's emissions (million short tons and short tons) are
not taken: short tons are not in the standard's unit vocabulary; the header says so. A unit not in the map stops the run.

    python warehouse/connectors/eia_aeo.py

Ceiling: 40 requests a run (the route list, the release's scenario list, then one request a table and case; a 5xx is
asked once more after 60 seconds; 3 seconds between requests). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Annual Energy Outlook <release>").
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_aeo_electricity"
CONNECTOR = "eia_aeo"
SOURCE = "eia:aeo"
API = "https://api.eia.gov/v2/aeo/"
PAGE = "https://www.eia.gov/outlooks/aeo/"
TABLES = ["8", "9"]
CEILING = 40
PAUSE, RETRY_WAIT = 3, 60  # seconds before each request, and before the one retry of a 429 or a 5xx (session 490: EIA answered 429 while the daily run used the same key)
UNITS = {"GW": ("MW", 1000.0, ""), "BkWh": ("MWh", 1e6, ""), "nom cents/kWh": ("USD/kWh", 0.01, "nominal"),
         "cents/kWh": ("USD/kWh", 0.01, "nominal")}
NOT_TAKEN = {"MMst": "million short tons", "st": "short tons"}
X_COLS = ["x_table", "x_scenario", "x_scenario_name", "x_history", "x_region", "x_dollar_year"]


def unit_of(u, release_dollar_year=None):
    """(the ERW's unit, the factor, the dollar year) for one of the API's units; None for a unit not taken."""
    if u in NOT_TAKEN:
        return None
    if u in UNITS:
        return UNITS[u]
    if u.endswith(" cents/kWh") and u.split(" ")[0].isdigit():   # "2025 cents/kWh": the AEO's real dollars
        return ("USD/kWh", 0.01, u.split(" ")[0])
    raise RuntimeError(f"a unit not in the map: {u!r}")


def rows(data, release, url, retrieved):
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
        out.append(dict(entity=f"eia_aeo_{release}:{r['seriesId']}:{r['scenario']}", variable="value",
                        ts_utc=f"{int(r['period'])}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y", geo="US",
                        market="", node=r.get("seriesName", ""), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                        x_table=r["tableId"], x_scenario=r["scenario"], x_scenario_name=r.get("scenarioDescription", ""),
                        x_history=r.get("history", ""), x_region=r.get("regionId", ""), x_dollar_year=dollars))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA Annual Energy Outlook, electricity Tables 8 and 9, every case")
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

    def get(path, **params):
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(API + path, params=dict(api_key=key, **params), timeout=120)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r.json()["response"], r.url
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"EIA answered HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        routes, _ = get("")
        release = max((x["id"] for x in routes["routes"] if x["id"].isdigit()), key=int)
        scen, _ = get(f"{release}/facet/scenario/")
        cases = sorted(f["id"] for f in scen["facets"])
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, skipped = [], {}
        for table in TABLES:
            for case in cases:
                resp, url = get(f"{release}/data/", frequency="annual", **{"data[]": "value", "facets[tableId][]": table,
                                                                          "facets[scenario][]": case, "length": 5000})
                if int(resp.get("total", 0)) > len(resp["data"]):
                    raise RuntimeError(f"table {table}, {case}: {resp['total']} rows, more than one page")
                t, sk = rows(resp["data"], release, ip.redact(url), retrieved)
                for k, v in sk.items():
                    skipped[k] = skipped.get(k, 0) + v
                frames.append(t)
                log(f"  table {table}, {case}: {len(t):,} rows")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)[ip.SERIES_COLS + X_COLS]
        header = [
            f"Energy Research Warehouse (ERW): EIA Annual Energy Outlook {release}, electricity Tables 8 and 9, every case (session 490)",
            f"Shape: series (docs/datastandard.md v0). entity eia_aeo_{release}:<seriesId>:<case>; variable value; node the series' name; ts_utc the year's 1 January; freq P1Y. GW given as MW, billion kWh as MWh, cents/kWh as USD/kWh (x_dollar_year the AEO's real dollars or nominal).",
            f"PROJECTIONS: EIA's, by case ({', '.join(cases)}); AEO{release} names no Reference case. Not taken: " + (", ".join(f"{n:,} rows in {NOT_TAKEN[u]}" for u, n in skipped.items()) or "none") + " (Table 8's emissions; short tons are not in the standard's units). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_aeo.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Energy Outlook {release} (API v2, route aeo/{release}), {PAGE}",
            f"  access: {API}{release}/data/?frequency=annual&data[]=value&facets[tableId][]=<8|9>&facets[scenario][]=<case>",
            f'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Energy Outlook {release}").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Energy Outlook (API v2, Tables 8 and 9)", report_url=PAGE,
                                    document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"AEO{release}: {len(s):,} rows, {len(cases)} cases"))
        print(f"{NAME}: AEO{release}, {len(s):,} rows, {s['entity'].nunique():,} series by case, {len(cases)} cases; {asked[0]} requests; not taken {skipped}")
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
