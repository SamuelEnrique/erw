#!/usr/bin/env python3
"""The Natural Resources Conservation Service's SNOTEL network: the snow water equivalent, a day, at twenty high stations
above the Colorado's, the Columbia's and California's reservoirs (session 2149, chain 092: the snow behind the West's dams,
which fills the reservoirs the hydro fleet runs on).

Energy Research Warehouse (ERW) connector. One series table from NRCS's Air and Water Database REST service (no key):

    https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations?stationTriplets=<triplets>     the stations' metadata
    https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data?stationTriplets=<triplets>&elements=WTEQ&duration=DAILY&...

    nrcs_snotel_swe_daily   entity snotel:<station id>:<state>; variable snow_water_equivalent (in: inches of water, as
               NRCS stores WTEQ); ts_utc the day written as 00:00 UTC (SNOTEL's days are the station's local standard time);
               freq P1D; geo US-<state>; node the station's name; x_basin colorado, columbia or california (the group the
               station was chosen for); x_huc the station's 12-digit hydrologic unit; x_elevation_ft; x_lat; x_lon

The twenty stations are the highest of each basin's SNOTEL stations with a record from before October 2014 (session
2149 chose them from NRCS's station list): above Lake Powell, nine in the Colorado headwaters, the White and Yampa, the
Green and the lower Green; on the Columbia, seven in the Kootenai and Pend Oreille, the upper Columbia and the Yakima; in
California, four in the Sacramento and San Joaquin basins. An answer that does not hold every station asked, a station
without WTEQ, a unit other than inches or a day given twice stops the run. A day with no value has no row and is counted.
Nothing is filled.

    python warehouse/connectors/nrcs_snotel.py [--offline] [--out-dir DIR]

Ceiling: four requests (the metadata and one a basin), saved in warehouse/raw/nrcs_snotel/; asked again unless --offline,
since the addresses stay as days are added. wcc.sc.egov.usda.gov has no robots file (HTTP 404). License: not settled
(NRCS's own policies page answered 404 in session 2149; for session 2153's licenses round), so internal until a verdict.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "nrcs_snotel"
SOURCE = "nrcs:awdb_snotel"
HOST = "wcc.sc.egov.usda.gov"
API = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/"
START, END = "2015-01-01", None  # END: today, UTC
TABLE = "nrcs_snotel_swe_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_basin", "x_huc", "x_elevation_ft", "x_lat", "x_lon"]
BASINS = {
    "colorado": ["485:CO:SNTL", "335:CO:SNTL", "1186:CO:SNTL", "505:CO:SNTL", "825:CO:SNTL", "717:CO:SNTL", "1117:UT:SNTL",
                 "790:UT:SNTL", "1249:UT:SNTL"],
    "columbia": ["313:MT:SNTL", "727:MT:SNTL", "850:MT:SNTL", "606:WA:SNTL", "832:WA:SNTL", "502:WA:SNTL", "692:WA:SNTL"],
    "california": ["1067:CA:SNTL", "391:CA:SNTL", "428:CA:SNTL", "356:CA:SNTL"],
}


def data_url(triplets, end):
    return f"{API}data?stationTriplets={'%2C'.join(triplets)}&elements=WTEQ&duration=DAILY&beginDate={START}&endDate={end}"


def meta_url():
    return (f"{API}stations?stationTriplets={'%2C'.join(t for b in BASINS.values() for t in b)}&returnForecastPointMetadata=false"
            "&returnReservoirMetadata=false&returnStationElements=false")


def parse_meta(d):
    m = {x["stationTriplet"]: x for x in d}
    missing = sorted(set(t for b in BASINS.values() for t in b) - set(m))
    if missing:
        raise RuntimeError(f"the station list lacks {missing}")
    return m


def parse(d, basin, meta, base, missing):
    got = {x["stationTriplet"]: x for x in d}
    asked = BASINS[basin]
    if sorted(got) != sorted(asked):
        raise RuntimeError(f"{basin}: the answer holds {sorted(got)}, not the stations asked")
    out = []
    for trip in asked:
        els = [e for e in got[trip].get("data", []) if e.get("stationElement", {}).get("elementCode") == "WTEQ"]
        if len(els) != 1:
            raise RuntimeError(f"{trip}: {len(els)} WTEQ series")
        el = els[0]
        unit = el["stationElement"].get("storedUnitCode")
        if unit != "in":
            raise RuntimeError(f"{trip}: WTEQ in {unit!r}, not inches")
        sid, st, _ = trip.split(":")
        m = meta[trip]
        seen = set()
        for v in el.get("values", []):
            day = v.get("date", "")[:10]
            if day in seen:
                raise RuntimeError(f"{trip}: {day} given twice")
            seen.add(day)
            if v.get("value") is None:
                missing[trip] = missing.get(trip, 0) + 1
                continue
            out.append(dict(base, entity=f"snotel:{sid}:{st.lower()}", variable="snow_water_equivalent", ts_utc=f"{day}T00:00:00Z",
                            value=float(v["value"]), unit="in", freq="P1D", geo=f"US-{st}", market="", node=m["name"], x_basin=basin,
                            x_huc=str(m.get("huc", "")), x_elevation_ft=m.get("elevation"), x_lat=m.get("latitude"), x_lon=m.get("longitude")))
        if not seen:
            raise RuntimeError(f"{trip}: no day")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NRCS SNOTEL: the daily snow water equivalent at twenty stations above the West's reservoirs")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--end", help="the last day asked (default: today, UTC; a saved answer is found by its address)")
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
    end = args.end or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        mc, _ = ip.fetch_raw(CONNECTOR, meta_url(), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        meta = parse_meta(json.loads(mc))
        rows, missing, latest = [], {}, ""
        for basin, trips in BASINS.items():
            url = data_url(trips, end)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(json.loads(content), basin, meta, base, missing)
            log(f"  {basin}: {len(got):,} station-days from {len(trips)} stations")
            rows += got
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        gaps = sum(missing.values())
        head = [
            "Energy Research Warehouse (ERW): NRCS SNOTEL, the daily snow water equivalent at twenty high stations above the Colorado's, the "
            f"Columbia's and California's reservoirs, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]} (session 2149)",
            "Shape: series (docs/datastandard.md v0). entity snotel:<station id>:<state>; variable snow_water_equivalent (in, inches of water, "
            "NRCS's WTEQ); freq P1D; ts_utc the station's day written as 00:00 UTC; geo US-<state>; node the station's name; x_basin colorado, "
            "columbia or california; x_huc; x_elevation_ft; x_lat; x_lon.",
            f"The stations: the highest of each basin's with a record from before October 2014 (session 2149). Days with no value have no row: "
            f"{gaps:,}. NRCS's values are provisional for the current water year and revised by its quality control. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrcs_snotel.py; the latest answer retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} USDA Natural Resources Conservation Service, National Water and Climate Center, Air and Water Database (SNOTEL), {API}",
            f"  access: {API}data?stationTriplets=<triplets>&elements=WTEQ&duration=DAILY&beginDate={START}&endDate={end}",
            "License: not settled (NRCS's terms were not found in session 2149; for the licenses round), held internal until a verdict. Cite "
            "the USDA Natural Resources Conservation Service.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} stations; days without a value {gaps:,}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="USDA Natural Resources Conservation Service (NRCS)",
                                    report="Air and Water Database (AWDB) REST service: SNOTEL daily snow water equivalent (WTEQ)",
                                    report_url=API, document_list=API, license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
