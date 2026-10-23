#!/usr/bin/env python3
"""EIA's International Energy Outlook 2023: projections to 2050 of each world region's primary energy consumption, in all
and by fuel, its energy-related CO2 emissions, and its net electricity generation and generating capacity by fuel, the
reference case (session 978, chain 055: the outlook beside eia_world_energy_co2_annual and
eia_world_electricity_annual's history).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_ieo_projections.csv, from the EIA API v2
route ieo/2023, tables 1 (primary energy consumption by region), 2 (by region and fuel), 10 (CO2 emissions by region),
20 (net electricity generation by region and fuel) and 21 (installed generating capacity by region and fuel), scenario
Reference:

    https://api.eia.gov/v2/ieo/2023/data/

    entity    eia_ieo2023:<tableId>:<regionId>:<seriesId> (regionId 0-0 for EIA's tables by series, 6-n by region); variable consumption (tables 1, 2), emissions (10), generation (20),
              capacity (21); unit TBtu (EIA's quad Btu times 1,000), tCO2 (million metric tons times 1,000,000), MWh
              (billion kWh times 1,000,000), MW (gigawatts times 1,000); ts_utc the year's 1 January; freq P1Y; geo empty; node
              EIA's series name ("<what> : <region> : <fuel>"); x_history HISTORY or PROJECTION, x_scenario, x_table

A unit not in the map, a table or scenario not asked for, or an (entity, year) given twice stops the run; a value EIA
leaves empty has no row; nothing is filled.

    python warehouse/connectors/eia_ieo.py [--offline]

Ceiling: four requests (the pages, 5,000 rows each, saved in warehouse/raw/eia_ieo/ with the key removed from their
addresses and reused offline). The key comes from EIA_API_KEY. api.eia.gov has no robots file (HTTP 403, no key).
License: public (EIA, record 1 of license_reads.csv).
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

NAME = "eia_ieo_projections"
CONNECTOR = "eia_ieo"
SOURCE = "eia:ieo/2023"
PAGE = "https://www.eia.gov/ieo/"
API = "https://api.eia.gov/v2/ieo/2023/data/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TABLES = {"1": "consumption", "2": "consumption", "10": "emissions", "20": "generation", "21": "capacity"}
SCENARIO = "Reference"
UNITS = {"quad Btu": ("TBtu", 1e3), "MMmt": ("tCO2", 1e6), "bill kWh": ("MWh", 1e6), "gigawatts": ("MW", 1e3)}
LENGTH = 5000
X_COLS = ["x_history", "x_scenario", "x_table"]


def url_of(key, offset):
    p = [("api_key", key), ("frequency", "annual"), ("data[0]", "value"), ("facets[scenario][]", SCENARIO)]
    p += [("facets[tableId][]", t) for t in TABLES]
    # every facet in the sort, so pages do not overlap (session 978: sorted without the region, two pages shared six rows)
    p += [("sort[0][column]", "tableId"), ("sort[0][direction]", "asc"), ("sort[1][column]", "regionId"), ("sort[1][direction]", "asc"),
          ("sort[2][column]", "seriesId"), ("sort[2][direction]", "asc"), ("sort[3][column]", "period"), ("sort[3][direction]", "asc"),
          ("offset", str(offset)), ("length", str(LENGTH))]
    return requests.Request("GET", API, params=p).prepare().url


def rows(data, base):
    out, units = [], set()
    for d in data:
        t = str(d["tableId"])
        if t not in TABLES or d["scenario"] != SCENARIO:
            raise RuntimeError(f"a table or scenario not asked for: {t} {d['scenario']}")
        if d["unit"] not in UNITS:
            raise RuntimeError(f"a unit not in the map: {d['unit']!r} ({d['seriesId']})")
        v = pd.to_numeric(d.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, scale = UNITS[d["unit"]]
        units.add(d["unit"])
        out.append(dict(base, entity=f"eia_ieo2023:{t}:{d['regionId']}:{d['seriesId']}", variable=TABLES[t], ts_utc=f"{int(d['period'])}-01-01T00:00:00Z",
                        value=round(float(v) * scale, 6), unit=unit, freq="P1Y", geo="", market="", node=d["seriesName"] if d["regionId"] == "0-0" else f"{d['seriesName']} : {d['regionName'].strip()}",
                        x_history=d["history"], x_scenario=d["scenario"], x_table=d["tableName"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's International Energy Outlook 2023, the reference case")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is empty")
        out, offset, total, got = [], 0, None, []
        while total is None or offset < total:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(key, offset), log, offline=args.offline, headers=UA, timeout=120)
            body = json.loads(content.decode("utf-8"))["response"]
            total = int(body["total"])
            data = body.get("data", [])
            if not data:
                raise RuntimeError(f"an empty page at offset {offset} of {total}")
            base = dict(source=SOURCE, source_url=ip.redact(url_of(key, offset)), retrieved_at=rec.get("retrieved_at") or "", vintage="")
            got.append(base["retrieved_at"])
            out += rows(data, base)
            offset += len(data)
            if not rec.get("cached"):
                time.sleep(2)
        s = pd.DataFrame(out)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, year) given twice: the pages overlap")
        if offset != total:
            raise RuntimeError(f"{offset} rows read of EIA's {total}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        k = s.groupby("variable").entity.nunique().to_dict()
        header = [
            "Energy Research Warehouse (ERW): EIA, International Energy Outlook 2023, reference case: world regions' primary energy consumption (in all and by fuel), energy-related CO2 emissions, and net electricity generation and capacity by fuel, to 2050 (session 978)",
            "Shape: series (docs/datastandard.md v0). entity eia_ieo2023:<tableId>:<regionId>:<seriesId>; variable consumption (TBtu: EIA's quad Btu times 1,000), "
            "emissions (tCO2: million metric tons times 1,000,000), generation (MWh: billion kWh times 1,000,000), capacity (MW: gigawatts times 1,000); ts_utc the "
            "year's 1 January; freq P1Y; geo empty; node EIA's series name, '<what> : <region> : <fuel>'; x_history HISTORY or PROJECTION. A total holds its "
            "parts: a sum takes one level.",
            f"{len(s):,} rows, years {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}; series by variable: {', '.join(f'{v} {n}' for n, v in k.items())}. "
            f"EIA's total for the five tables: {total:,} rows. A projection is EIA's model result of 2023, not an observation. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_ieo.py via the EIA API v2; the pages retrieved {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; the key removed from each address)",
            f"Source: {SOURCE} U.S. Energy Information Administration, International Energy Outlook 2023 (World Energy Projection System), {PAGE}",
            f"  access: {API} (tables {', '.join(TABLES)}, scenario {SCENARIO})",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, International Energy Outlook 2023").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="International Energy Outlook 2023 (tables 1, 2, 10, 20, 21, reference case)", report_url=PAGE,
                                    document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows of {total:,}; {k}")
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
