#!/usr/bin/env python3
"""The USGS's earthquake catalog (ComCat) for Oklahoma, Kansas, Texas and New Mexico: every earthquake of magnitude 2.5
and above from 2010, with its time, place, depth and magnitude (session 2120, chain 079: the earthquakes the oil fields'
wastewater injection sets off, beside the states' oil and gas production).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/usgs_comcat_earthquakes_south_central.csv,
from the FDSN event service's CSV answer to one query (no key):

    https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake&orderby=time-asc
        &starttime=2010-01-01&endtime=<END>&minmagnitude=2.5
        &minlatitude=25.8&maxlatitude=40.0&minlongitude=-109.06&maxlongitude=-93.5

The box is the four states' bounding box, so it also holds parts of Colorado, Arkansas, Louisiana, Missouri, Oklahoma's
other neighbours and northern Mexico; nothing is cut from it, because an event's place names its nearest town, which can
lie across a state line. x_place_state is the state or country the place names after its last comma, in full where the
catalog gives a postal code ("2 km E of Choctaw, OK"); a place such as "western Texas" is read as the state it names, and
one that names no single state ("Texas-Chihuahua border region") is blank. The service answers
at most 20,000 events a query; the count for the box was 16,050 on 23 October 2026, and an answer of 20,000 rows stops
the run (the box would need splitting).

    event_id     usgs_comcat:<the catalog's event id> (the preferred id, stable while the USGS keeps it)
    event_date   the origin time in UTC to the second (YYYY-MM-DDTHH:MM:SSZ); x_time_utc keeps the catalog's milliseconds
    event_type   earthquake (the query asks for earthquakes only: quarry blasts and explosions are left out)
    status       the catalog's review status (reviewed or automatic)
    x_*          latitude and longitude (degrees), depth (km), magnitude and its type, the place, the state the place names,
                 the contributing network, the location and magnitude sources, the station count, the azimuthal gap, the
                 errors as published, and the event's last update in the catalog

Values as published; a blank stays blank; nothing is filled. A header not the catalog's, an event given twice, a time not
the catalog's format or a magnitude below 2.5 stops the run.

    python warehouse/connectors/usgs_earthquakes.py [--end YYYY-MM-DD] [--offline] [--out-dir DIR]

Ceiling: one request (the query, reused from warehouse/raw/usgs_earthquakes/ with --offline). earthquake.usgs.gov has no
robots file (HTTP 404, session 2120). License: USGS-authored data in the U.S. public domain (USGS, read 87).
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

NAME = "usgs_comcat_earthquakes_south_central"
CONNECTOR = "usgs_earthquakes"
SOURCE = "usgs:comcat"
PAGE = "https://earthquake.usgs.gov/fdsnws/event/1/"
BOX = dict(minlatitude="25.8", maxlatitude="40.0", minlongitude="-109.06", maxlongitude="-93.5")
START = "2010-01-01"
MIN_MAG = 2.5
LIMIT = 20000
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
X_COLS = ["x_time_utc", "x_latitude", "x_longitude", "x_depth_km", "x_magnitude", "x_magnitude_type", "x_place",
          "x_place_state", "x_net", "x_location_source", "x_magnitude_source", "x_stations", "x_gap_degrees",
          "x_horizontal_error_km", "x_depth_error_km", "x_magnitude_error", "x_updated_utc"]
HEADER = ["time", "latitude", "longitude", "depth", "mag", "magType", "nst", "gap", "dmin", "rms", "net", "id", "updated",
          "place", "type", "horizontalError", "depthError", "magError", "magNst", "status", "locationSource", "magSource"]
STATES = {"Alabama", "Arizona", "Arkansas", "California", "Colorado", "Kansas", "Louisiana", "Mississippi", "Missouri",
          "Nebraska", "Nevada", "New Mexico", "Oklahoma", "Tennessee", "Texas", "Utah", "Wyoming", "Mexico"}
POSTAL = {"AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "KS": "Kansas",
          "LA": "Louisiana", "MS": "Mississippi", "MO": "Missouri", "NE": "Nebraska", "NV": "Nevada", "NM": "New Mexico",
          "OK": "Oklahoma", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "WY": "Wyoming"}
TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z")


def query_url(end):
    q = dict(format="csv", eventtype="earthquake", orderby="time-asc", starttime=START, endtime=end,
             minmagnitude=f"{MIN_MAG}", **BOX)
    return PAGE + "query?" + "&".join(f"{k}={v}" for k, v in q.items())


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def place_state(place):
    p = text(place)
    tail = p.rsplit(",", 1)[-1].strip() if "," in p else ""
    if tail in STATES:
        return tail
    if tail in POSTAL:
        return POSTAL[tail]
    for s in sorted(STATES, key=len, reverse=True):
        if p == s or re.fullmatch(rf"(northern|southern|eastern|western|central|north|south|east|west)[a-z ]* {s}", p, re.I):
            return s
    return ""


def build(content, url, retrieved):
    t = pd.read_csv(io.StringIO(content), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not the catalog's: {list(t.columns)}")
    if len(t) >= LIMIT:
        raise RuntimeError(f"{len(t)} events, the service's limit: the box must be split")
    out = []
    for r in t.to_dict("records"):
        when = text(r["time"])
        if not TIME.fullmatch(when):
            raise RuntimeError(f"{r['id']}: a time not the catalog's format: {when!r}")
        if text(r["type"]) != "earthquake":
            raise RuntimeError(f"{r['id']}: an event of type {r['type']!r} in an earthquakes-only answer")
        if float(r["mag"]) < MIN_MAG:
            raise RuntimeError(f"{r['id']}: magnitude {r['mag']} below {MIN_MAG}")
        out.append({"event_id": f"usgs_comcat:{text(r['id'])}", "event_date": when[:19] + "Z", "event_type": "earthquake",
                    "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "", "status": text(r["status"]),
                    "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "x_time_utc": when,
                    "x_latitude": text(r["latitude"]), "x_longitude": text(r["longitude"]), "x_depth_km": text(r["depth"]),
                    "x_magnitude": text(r["mag"]), "x_magnitude_type": text(r["magType"]), "x_place": text(r["place"]),
                    "x_place_state": place_state(r["place"]), "x_net": text(r["net"]),
                    "x_location_source": text(r["locationSource"]), "x_magnitude_source": text(r["magSource"]),
                    "x_stations": text(r["nst"]), "x_gap_degrees": text(r["gap"]),
                    "x_horizontal_error_km": text(r["horizontalError"]), "x_depth_error_km": text(r["depthError"]),
                    "x_magnitude_error": text(r["magError"]), "x_updated_utc": text(r["updated"])})
    t = pd.DataFrame(out, columns=EVENT_COLS + X_COLS)
    twice = t.event_id[t.event_id.duplicated()]
    if len(twice):
        raise RuntimeError(f"an event given twice: {list(twice)[:3]}")
    return t.sort_values(["event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="USGS ComCat earthquakes, magnitude 2.5 and above, OK, KS, TX and NM's box, 2010 on")
    ap.add_argument("--end", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
                    help="the query's endtime (a UTC day, not included); the same day reuses the saved answer")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.end):
        ap.error("--end is a day, YYYY-MM-DD")
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    url = query_url(args.end)
    try:
        if not args.offline and (ip.paused("usgs") or ip.paused_host("earthquake.usgs.gov")):
            raise RuntimeError("the USGS is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        t = build(content.decode("utf-8", errors="replace"), url, rec.get("retrieved_at") or "")
        years = t.event_date.str[:4]
        ok = t[t.x_place_state == "Oklahoma"].groupby(years).size()
        peak = ok.idxmax() if len(ok) else ""
        by = t.x_place_state.replace("", "(none named)").value_counts()
        header = [
            f"Energy Research Warehouse (ERW): USGS ComCat earthquakes of magnitude 2.5 and above, {START} to {args.end} (not included), in the bounding box of Oklahoma, Kansas, Texas and New Mexico (session 2120)",
            "Shape: events (docs/datastandard.md v0). event_id usgs_comcat:<catalog id>; event_date the origin time in UTC to the second; event_type earthquake; status the "
            "catalog's review status; x_latitude and x_longitude degrees, x_depth_km km, x_magnitude with x_magnitude_type; x_place_state the state or country the place names.",
            f"{len(t)} earthquakes, magnitude {pd.to_numeric(t.x_magnitude).min():.2f} to {pd.to_numeric(t.x_magnitude).max():.2f}; by the place's state: "
            + "; ".join(f"{k} {v}" for k, v in by.head(10).items())
            + (f". Oklahoma's most in one year: {ok.max()} in {peak}" if len(ok) else "")
            + ". The box (latitude 25.8 to 40.0, longitude -109.06 to -93.5) also holds parts of the neighbouring states and northern Mexico; nothing is cut. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usgs_earthquakes.py; the answer retrieved {rec.get('retrieved_at') or ''}"
            + (f", last modified {ip.vintage_of(rec)}" if ip.vintage_of(rec) else " (the service gave no last-modified time)"),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Geological Survey (USGS) Earthquake Hazards Program, ANSS Comprehensive Earthquake Catalog (ComCat), FDSN event web service, {PAGE}",
            f"  access: {url}",
            "License: USGS-authored data, in the U.S. public domain. Cite: U.S. Geological Survey, Earthquake Hazards Program, ANSS Comprehensive Catalog (ComCat), doi:10.5066/F7MS3QZH.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Geological Survey (USGS), Earthquake Hazards Program",
                                    report="ANSS Comprehensive Earthquake Catalog (ComCat), FDSN event web service",
                                    report_url=PAGE, document_list=url, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} events"))
        print(f"{NAME}: {len(t)} events; Oklahoma by year: " + ", ".join(f"{k} {v}" for k, v in ok.items()))
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
