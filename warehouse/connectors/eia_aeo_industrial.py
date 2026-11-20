#!/usr/bin/env python3
"""EIA's Annual Energy Outlook: energy use by industry, the industrial sub-sector tables, every case (session 8003, chain
501 step D2: energy use by industry).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_aeo_industrial.csv, from the U.S. Energy
Information Administration's API v2 (route aeo/<release>), the newest release the API lists (AEO2026 on 19 November
2026), in every case (scenario) it publishes. The tables, each an industry's energy use by fuel:

    Table 24 Refining (API tableId 35)     Table 25 Food (36)       Table 26 Paper (37)        Table 27 Bulk chemicals (38)
    Table 28 Glass (39)                    Table 29 Cement and lime (40)                       Table 30 Iron and steel (41)
    Table 31 Aluminum (42)                 Table 32 Metal-based durables (139)                 Table 33 Other manufacturing (140)
    Table 34 Nonmanufacturing (43)

    https://api.eia.gov/v2/aeo/<release>/data/?frequency=annual&data[]=value&facets[tableId][]=<id>&length=5000&offset=<n>

    entity    eia_aeo_<release>:<seriesId>.<h>:<scenario>, h the first six hex digits of the sha1 of the series' name (EIA gives
              one seriesId to two series, such as Bulk Chemical's total energy use and its hydrogen total); variable consumption; node the series' name; ts_utc the year's 1
              January; freq P1Y; unit TBtu (EIA's trillion Btu)
    x_*       the API's table id and the AEO's table number, scenario and its name, history flag, the industry

Only the series in trillion Btu are taken (the energy use by fuel); the tables' other series (generating capacity of
combined heat and power in GW, its generation in billion kWh, energy intensity per dollar of shipments, shipments in
dollars, carbon dioxide) are not, and the header counts them. These are EIA's projections, not observations (the
history flag says which years EIA marks as history): the header says so, and nothing is filled or interpolated.

    python warehouse/connectors/eia_aeo_industrial.py [--out-dir DIR]

Ceiling: 60 requests a run (the route list, the release's scenario list, then the pages of each table; a 429 or a 5xx
asked once more after 60 seconds; 3 seconds between requests). License: public (EIA, record 1 of license_reads.csv; cite
"U.S. Energy Information Administration, Annual Energy Outlook <release>").
"""

import argparse
import datetime as dt
import hashlib
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_aeo_industrial"
CONNECTOR = "eia_aeo_industrial"
SOURCE = "eia:aeo_industrial"
API = "https://api.eia.gov/v2/aeo/"
PAGE = "https://www.eia.gov/outlooks/aeo/"
# API tableId: (the AEO's table number, the industry)
TABLES = {"35": ("24", "refining"), "36": ("25", "food"), "37": ("26", "paper"), "38": ("27", "bulk_chemicals"),
          "39": ("28", "glass"), "40": ("29", "cement_and_lime"), "41": ("30", "iron_and_steel"), "42": ("31", "aluminum"),
          "139": ("32", "metal_based_durables"), "140": ("33", "other_manufacturing"), "43": ("34", "nonmanufacturing")}
CEILING = 60
PAUSE, RETRY_WAIT = 3, 60
TAKEN = {"trillion Btu": ("TBtu", 1.0)}
X_COLS = ["x_series_id", "x_table_id", "x_table", "x_industry", "x_scenario", "x_scenario_name", "x_history"]


def rows(data, release, url, retrieved):
    out, skipped = [], {}
    for r in data:
        if r["unit"] not in TAKEN:
            skipped[r["unit"]] = skipped.get(r["unit"], 0) + 1
            continue
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, factor = TAKEN[r["unit"]]
        num, ind = TABLES[str(r["tableId"])]
        h = hashlib.sha1(str(r.get("seriesName", "")).encode("utf-8")).hexdigest()[:6]
        out.append(dict(entity=f"eia_aeo_{release}:{r['seriesId']}.{h}:{r['scenario']}", variable="consumption",
                        ts_utc=f"{int(r['period'])}-01-01T00:00:00Z", value=float(v) * factor, unit=unit, freq="P1Y", geo="US",
                        market="", node=r.get("seriesName", ""), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                        x_series_id=r["seriesId"], x_table_id=str(r["tableId"]), x_table=num, x_industry=ind, x_scenario=r["scenario"],
                        x_scenario_name=r.get("scenarioDescription", ""), x_history=r.get("history", "")))
    return pd.DataFrame(out), skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA Annual Energy Outlook, the industrial sub-sector tables, every case")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
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
        if ip.paused_host("api.eia.gov"):
            raise RuntimeError("api.eia.gov is paused: no request made")
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
            offset, total = 0, None
            while total is None or offset < total:
                resp, url = get(f"{release}/data/", frequency="annual", **{"data[]": "value", "facets[tableId][]": table,
                                                                          "sort[0][column]": "seriesId", "sort[0][direction]": "asc",
                                                                          "sort[1][column]": "scenario", "sort[1][direction]": "asc",
                                                                          "sort[2][column]": "period", "sort[2][direction]": "asc",
                                                                          "length": 5000, "offset": offset})
                total = int(resp.get("total", 0))
                if not resp["data"]:
                    break
                t, sk = rows(resp["data"], release, ip.redact(url.split("&offset")[0]), retrieved)
                for k, v in sk.items():
                    skipped[k] = skipped.get(k, 0) + v
                frames.append(t)
                offset += len(resp["data"])
            if offset != total:
                raise RuntimeError(f"table {table}: {offset} rows read, the API says {total}")
            log(f"  table {table} (AEO Table {TABLES[table][0]}, {TABLES[table][1]}): {total:,} rows asked")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        dup = s.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if dup.any():
            raise RuntimeError(f"{int(dup.sum())} rows share a key, e.g. {s[dup].head(2)[['entity', 'node']].to_dict('records')}")
        missing = sorted(set(TABLES) - set(s["x_table_id"]))
        if missing:
            raise RuntimeError(f"tables with no energy row: {missing}")
        s = s[ip.SERIES_COLS + X_COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        header = [
            f"Energy Research Warehouse (ERW): EIA Annual Energy Outlook {release}, energy use by industry (the industrial sub-sector Tables 24 to 34), every case (session 8003, chain 501)",
            f"Shape: series (docs/datastandard.md v0). entity eia_aeo_{release}:<seriesId>.<h>:<case> (h: six hex digits of the sha1 of the series' name, since EIA gives one seriesId to two series); variable consumption; TBtu (EIA's trillion Btu); node the series' name; ts_utc the year's 1 January; freq P1Y. "
            "x_series_id (EIA's), x_table_id (the API's), x_table (the AEO's number), x_industry, x_scenario, x_scenario_name, x_history (EIA's flag: HISTORY or PROJECTION).",
            f"PROJECTIONS: EIA's, by case ({', '.join(cases)}); AEO{release} names no Reference case. Taken: the series in trillion Btu (energy use by fuel). Not taken: "
            + (", ".join(f"{n:,} rows in {u}" for u, n in sorted(skipped.items())) or "none") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_aeo_industrial.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Energy Outlook {release} (API v2, route aeo/{release}), {PAGE}",
            f"  access: {API}{release}/data/?frequency=annual&data[]=value&facets[tableId][]=<35 to 43, 139, 140>",
            f'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Energy Outlook {release}").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Energy Outlook (API v2): the industrial sub-sector tables, energy use by fuel", report_url=PAGE,
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
