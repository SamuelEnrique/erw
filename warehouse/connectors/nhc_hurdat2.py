#!/usr/bin/env python3
"""The National Hurricane Center's best tracks (HURDAT2): every tropical and subtropical cyclone's six-hourly fixes in the
Atlantic and the Northeast and North Central Pacific, with the landfalls the files mark, from 2000 (session 2059, chain
066: the hurricanes that cross the Gulf's refineries and terminals and the coasts' grids).

Energy Research Warehouse (ERW) connector. One events table from the two text files of www.nhc.noaa.gov/data/hurdat/:

    https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-092326.txt          Atlantic, 1851 to 2025
    https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2025-092926.txt    Northeast and North Central Pacific, 1949 to 2025

    nhc_hurdat2_track_points   event_id nhc:<storm id>:<YYYYMMDDHHMM> (the storm's ATCF id, e.g. AL092008); event_date
                               the fix's UTC day; event_type the system's status in snake case (hurricane, tropical_storm,
                               tropical_depression, subtropical_storm, subtropical_depression, extratropical, low,
                               disturbance, wave); parties NHC; x_storm_id; x_storm_name; x_basin (atlantic or
                               pacific); x_time_utc (HHMM); x_record (the file's record identifier: L a landfall, I an
                               intensity peak, P a minimum pressure, ... or empty); x_landfall (1 where x_record is L);
                               x_lat, x_lon (decimal degrees, north and east positive); x_max_wind_kt (knots);
                               x_min_pressure_mb (millibars, empty where the file writes -999)

Each storm's header line must give its id, name and number of fix lines, and that many lines must follow; a status not
in the map, a position or wind that does not read, or an event_id given twice stops the run. A storm whose season is
before 2000 is left out. The wind radii columns are not taken. Nothing is filled.

    python warehouse/connectors/nhc_hurdat2.py [--offline] [--out-dir DIR] [--since 2000]

Ceiling: one request a basin's file (two); the next season's files are new names, read from the folder's listing by a
session. www.nhc.noaa.gov's robots file disallows nothing. License: public (NOAA's National Weather Service pages are in
the public domain, read 8; cite "NOAA National Hurricane Center, HURDAT2").
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "nhc_hurdat2"
SOURCE = "nhc:hurdat2"
PAGE = "https://www.nhc.noaa.gov/data/#hurdat"
BASE = "https://www.nhc.noaa.gov/data/hurdat/"
FILES = {"atlantic": "hurdat2-1851-2025-092326.txt", "pacific": "hurdat2-nepac-1949-2025-092926.txt"}
TABLE = "nhc_hurdat2_track_points"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_storm_id", "x_storm_name", "x_basin", "x_time_utc", "x_record", "x_landfall", "x_lat", "x_lon", "x_max_wind_kt",
          "x_min_pressure_mb", "retrieved_at", "vintage"]
STATUS = {"HU": "hurricane", "TS": "tropical_storm", "TD": "tropical_depression", "SS": "subtropical_storm", "SD": "subtropical_depression",
          "EX": "extratropical", "LO": "low", "DB": "disturbance", "WV": "wave"}


def coord(s, what):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([NSEW])", s.strip())
    if not m:
        raise RuntimeError(f"{what}: a position that does not read: {s!r}")
    v = float(m.group(1))
    return -v if m.group(2) in "SW" else v


def parse(text, basin, base, since):
    lines = [l for l in text.replace("\r", "").split("\n") if l.strip()]
    out, i = [], 0
    while i < len(lines):
        h = [c.strip() for c in lines[i].split(",")]
        if len(h) < 3 or not re.fullmatch(r"[A-Z]{2}\d{6}", h[0]) or not h[2].isdigit():
            raise RuntimeError(f"{basin} line {i + 1}: not a storm's header: {lines[i][:60]!r}")
        sid, name, n = h[0], h[1], int(h[2])
        fixes = lines[i + 1:i + 1 + n]
        if len(fixes) != n:
            raise RuntimeError(f"{basin} {sid}: {n} fix lines announced, {len(fixes)} found")
        i += 1 + n
        if int(sid[-4:]) < since:
            continue
        for f in fixes:
            c = [x.strip() for x in f.split(",")]
            if len(c) < 8 or not re.fullmatch(r"\d{8}", c[0]) or not re.fullmatch(r"\d{4}", c[1]):
                raise RuntimeError(f"{basin} {sid}: a fix line that does not read: {f[:60]!r}")
            if c[3] not in STATUS:
                raise RuntimeError(f"{basin} {sid} {c[0]} {c[1]}: a status not in the map: {c[3]!r}")
            try:
                wind = int(c[6])
                pres = int(c[7])
            except ValueError:
                raise RuntimeError(f"{basin} {sid} {c[0]} {c[1]}: a wind or pressure that does not read: {c[6]!r} {c[7]!r}")
            out.append(dict(base, event_id=f"nhc:{sid}:{c[0]}{c[1]}", event_date=f"{c[0][:4]}-{c[0][4:6]}-{c[0][6:]}", event_type=STATUS[c[3]],
                            parties="NHC", entity_ids="", mw="", price="", currency="", status="", x_storm_id=sid, x_storm_name=name,
                            x_basin=basin, x_time_utc=c[1], x_record=c[2], x_landfall="1" if c[2] == "L" else "0",
                            x_lat=coord(c[4], sid), x_lon=coord(c[5], sid), x_max_wind_kt="" if wind < 0 else wind,
                            x_min_pressure_mb="" if pres < 0 else pres))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NHC's HURDAT2 best tracks, the fixes of every storm from 2000")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--since", type=int, default=2000)
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
        rows, urls, latest = [], [], ""
        for basin, name in FILES.items():
            url = BASE + name
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=180, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content.decode("utf-8", errors="replace"), basin, base, args.since)
            log(f"  {basin}: {len(got)} fixes")
            rows += got
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
        t = pd.DataFrame(rows)
        dup = t.event_id.duplicated(keep=False)
        if dup.any():
            raise RuntimeError(f"an event_id given twice: {t[dup].event_id.head(5).tolist()}")
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        n_storms = t.x_storm_id.nunique()
        n_land = int((t.x_landfall == "1").sum())
        head = [
            "Energy Research Warehouse (ERW): NOAA National Hurricane Center, HURDAT2 best tracks: the six-hourly fixes of every cyclone in the "
            f"Atlantic and the Northeast and North Central Pacific from {args.since}, with the landfalls the files mark (session 2059)",
            "Shape: events (docs/datastandard.md v0). event_id nhc:<storm id>:<YYYYMMDDHHMM>; event_date the fix's UTC day; event_type the "
            "system's status; parties NHC; x_storm_id, x_storm_name, x_basin, x_time_utc, x_record (L a landfall), x_landfall, x_lat and x_lon "
            "(decimal degrees, north and east positive), x_max_wind_kt (knots), x_min_pressure_mb (millibars, empty where the file has -999).",
            f"{len(t)} fixes of {n_storms} storms, {t.event_date.min()} to {t.event_date.max()}; {n_land} landfall records. The wind radii are not "
            "taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nhc_hurdat2.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA National Hurricane Center, HURDAT2 (the best track data), {PAGE}",
            f"  access: {', '.join(urls)}",
            "License: public (NOAA National Weather Service: in the public domain; cite NOAA National Hurricane Center, HURDAT2).",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t)} fixes, {n_storms} storms, {n_land} landfalls")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="NOAA National Weather Service, National Hurricane Center",
                                    report="HURDAT2: best track data, Atlantic and Northeast and North Central Pacific", report_url=PAGE,
                                    document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
