#!/usr/bin/env python3
"""NOAA's Storm Events Database: the storms that take power lines down, one row an event, from 2015 (session 2042,
chain 059: the weather behind the grid's disturbances and outages).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/noaa_ncei_storm_events.csv, from the yearly
details files of the National Centers for Environmental Information's Storm Events Database bulk directory:

    https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d<YEAR>_c<YYYYMMDD>.csv.gz

The records are the National Weather Service's Storm Data, as NCEI publishes them. Only the event types that take
lines down or strain the grid are kept (TYPES below: wind, winter, tropical, tornado, wildfire, heat, cold, lightning
and storm surge); hail, floods, marine and the rest are not taken. The narratives are not taken.

    event_id     noaa_storm:<EVENT_ID>, NCEI's own identifier
    event_date   the event's begin time in UTC: NCEI's BEGIN_YEARMONTH, BEGIN_DAY and BEGIN_TIME are local standard
                 time in the zone CZ_TIMEZONE names (EST-5, CST-6 and the rest: the offset is the zone's own number of
                 hours from UTC, with no daylight saving), and the offset is subtracted. x_begin_local keeps NCEI's time
    event_type   NCEI's EVENT_TYPE in snake case (thunderstorm_wind, ice_storm, hurricane_typhoon); x_noaa_event_type
                 keeps NCEI's words
    status       empty; parties, entity_ids, mw, price and currency empty
    x_*          the episode, the state (name, FIPS and ISO 3166-2 code), the county or forecast zone, the forecast
                 office, the end time (local and UTC), the property and crop damage in USD (NCEI's "10.00K", "1.5M" and
                 "2B" read as thousands, millions and billions of dollars; an empty cell stays empty), the injuries and
                 deaths, the magnitude (knots for wind, an F or EF scale for tornadoes), the tornado's path, the begin
                 and end points, NCEI's data source code and the file's creation date (its c<YYYYMMDD>)

Values as NCEI publishes them; a blank stays blank; nothing is filled. A heading not in the map, a zone not in the
form EST-5, a damage figure not in NCEI's form or an event given twice stops the run.

    python warehouse/connectors/noaa_storm_events.py [--offline] [--first-year 2015] [--listing FILE] [--out-dir DIR]

Ceiling: one request for the directory listing (fresh each run) and one a year's file (named by its creation date,
so a revised file is a new name and is fetched; an unchanged one is reused from warehouse/raw/noaa_storm_events/).
--listing reads the listing from a saved copy instead (the session's probe asked for it). NCEI's robots file
(www.ncei.noaa.gov/robots.txt) disallows /data* and /orders* and parts of /access/crn/; /pub/data/swdi/ is not among
them. License: the Storm Data are the National Weather Service's records, in the public domain (NWS's notice, read 8;
NCEI's restriction on ISD's non-U.S. stations, read 9, does not reach these U.S. records).
"""

import argparse
import datetime as dt
import gzip
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "noaa_ncei_storm_events"
CONNECTOR = "noaa_storm_events"
SOURCE = "noaa:storm_events"
PAGE = "https://www.ncei.noaa.gov/stormevents/"
DIR = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FILE_RE = re.compile(r'href="(StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz)"')
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
# the event types kept: those that take lines down or strain the grid, in NCEI's own words
TYPES = ["Thunderstorm Wind", "High Wind", "Strong Wind", "Ice Storm", "Winter Storm", "Blizzard", "Heavy Snow",
         "Hurricane", "Hurricane (Typhoon)", "Tropical Storm", "Tropical Depression", "Storm Surge/Tide", "Tornado",
         "Wildfire", "Heat", "Excessive Heat", "Extreme Cold/Wind Chill", "Cold/Wind Chill", "Lightning"]
# NCEI's headings (Storm-Data-Bulk-csv-Format.pdf): those kept, renamed, and those read but not kept
FIELDS = {"EPISODE_ID": "x_episode_id", "STATE": "x_state", "STATE_FIPS": "x_state_fips", "CZ_TYPE": "x_cz_type",
          "CZ_FIPS": "x_cz_fips", "CZ_NAME": "x_cz_name", "WFO": "x_wfo", "CZ_TIMEZONE": "x_timezone",
          "INJURIES_DIRECT": "x_injuries_direct", "INJURIES_INDIRECT": "x_injuries_indirect",
          "DEATHS_DIRECT": "x_deaths_direct", "DEATHS_INDIRECT": "x_deaths_indirect", "MAGNITUDE": "x_magnitude",
          "MAGNITUDE_TYPE": "x_magnitude_type", "TOR_F_SCALE": "x_tor_f_scale", "TOR_LENGTH": "x_tor_length_mi",
          "TOR_WIDTH": "x_tor_width_yd", "BEGIN_LAT": "x_begin_lat", "BEGIN_LON": "x_begin_lon", "END_LAT": "x_end_lat",
          "END_LON": "x_end_lon", "DATA_SOURCE": "x_data_source"}
USED = {"BEGIN_YEARMONTH", "BEGIN_DAY", "BEGIN_TIME", "END_YEARMONTH", "END_DAY", "END_TIME", "EVENT_ID", "EVENT_TYPE",
        "DAMAGE_PROPERTY", "DAMAGE_CROPS"}
NOT_TAKEN = {"YEAR", "MONTH_NAME", "BEGIN_DATE_TIME", "END_DATE_TIME", "SOURCE", "FLOOD_CAUSE", "CATEGORY",
             "TOR_OTHER_WFO", "TOR_OTHER_CZ_STATE", "TOR_OTHER_CZ_FIPS", "TOR_OTHER_CZ_NAME", "BEGIN_RANGE",
             "BEGIN_AZIMUTH", "BEGIN_LOCATION", "END_RANGE", "END_AZIMUTH", "END_LOCATION", "EPISODE_NARRATIVE",
             "EVENT_NARRATIVE"}
X_COLS = ["x_noaa_event_type", "x_geo", "x_begin_local", "x_end_local", "x_end_utc", "x_damage_property_usd",
          "x_damage_crops_usd"] + list(FIELDS.values()) + ["x_file_created"]
# state FIPS to ISO 3166-2 (the 50 states, DC and the territories NCEI reports); a code not here leaves x_geo empty
FIPS = {1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI",
        16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD", 25: "MA", 26: "MI",
        27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE", 32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC",
        38: "ND", 39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT",
        50: "VT", 51: "VA", 53: "WA", 54: "WV", 55: "WI", 56: "WY", 60: "AS", 66: "GU", 69: "MP", 72: "PR", 78: "VI"}
ZONE_RE = re.compile(r"^([A-Z]{2,5})(-?\d{1,2})$")
DAMAGE_RE = re.compile(r"^(\d+(?:\.\d+)?)?([KMB]?)$")
SCALE = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def snake(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")


def damage(v):
    """NCEI's damage in dollars: "10.00K" 10000, "1.5M" 1500000, "2B"; "K" alone is zero dollars (NCEI's form for
    none); an empty cell stays empty."""
    s = text(v).upper()
    if not s:
        return ""
    m = DAMAGE_RE.match(s)
    if not m:
        raise RuntimeError(f"a damage figure not in NCEI's form: {v!r}")
    num = float(m.group(1)) if m.group(1) else 0.0
    return f"{num * SCALE[m.group(2)]:.0f}"


def offset(zone):
    """Hours east of UTC of NCEI's zone (EST-5 is -5); no daylight saving: NCEI's times are local standard time."""
    m = ZONE_RE.match(text(zone).upper())
    if not m:
        raise RuntimeError(f"a time zone not in NCEI's form: {zone!r}")
    return int(m.group(2))


def local(ym, d, hm):
    ym, d, hm = text(ym), text(d), text(hm).zfill(4)
    if not (re.fullmatch(r"\d{6}", ym) and re.fullmatch(r"\d{1,2}", d) and re.fullmatch(r"\d{4}", hm)):
        raise RuntimeError(f"not a time in NCEI's form: {ym!r} {d!r} {hm!r}")
    return dt.datetime(int(ym[:4]), int(ym[4:]), int(d), int(hm[:2]), int(hm[2:]))


def listing(html):
    """The newest details file of each year the directory lists: {year: (file name, creation date)}."""
    out = {}
    for name, year, created in FILE_RE.findall(html):
        y = int(year)
        if y not in out or created > out[y][1]:
            out[y] = (name, created)
    if not out:
        raise RuntimeError("the directory lists no details file")
    return out


def events(frame, url, retrieved, created):
    unknown = [c for c in frame.columns if c not in FIELDS and c not in USED and c not in NOT_TAKEN]
    if unknown:
        raise RuntimeError(f"{url}: headings not in the map: {unknown}")
    missing = [c for c in list(FIELDS) + sorted(USED) if c not in frame.columns]
    if missing:
        raise RuntimeError(f"{url}: headings missing: {missing}")
    f = frame[frame["EVENT_TYPE"].map(text).isin(TYPES)]
    out = []
    for r in f.to_dict("records"):
        eid = text(r["EVENT_ID"])
        if not re.fullmatch(r"\d+", eid):
            raise RuntimeError(f"{url}: an event id not a number: {eid!r}")
        hours = offset(r["CZ_TIMEZONE"])
        b = local(r["BEGIN_YEARMONTH"], r["BEGIN_DAY"], r["BEGIN_TIME"])
        e = local(r["END_YEARMONTH"], r["END_DAY"], r["END_TIME"])
        fips = pd.to_numeric(text(r["STATE_FIPS"]), errors="coerce")
        row = {"event_id": f"noaa_storm:{eid}", "event_date": (b - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "event_type": snake(text(r["EVENT_TYPE"])), "parties": "", "entity_ids": "", "mw": "", "price": "",
               "currency": "", "status": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
               "x_noaa_event_type": text(r["EVENT_TYPE"]),
               "x_geo": f"US-{FIPS[int(fips)]}" if not pd.isna(fips) and int(fips) in FIPS else "",
               "x_begin_local": b.strftime("%Y-%m-%dT%H:%M:%S"), "x_end_local": e.strftime("%Y-%m-%dT%H:%M:%S"),
               "x_end_utc": (e - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "x_damage_property_usd": damage(r["DAMAGE_PROPERTY"]), "x_damage_crops_usd": damage(r["DAMAGE_CROPS"]),
               "x_file_created": f"{created[:4]}-{created[4:6]}-{created[6:]}"}
        for k, v in FIELDS.items():
            row[v] = text(r[k])
        out.append(row)
    return out


def build(frames):
    """frames: [(DataFrame, url, retrieved, created)], one a year. Returns the table, sorted."""
    rows = []
    for frame, url, retrieved, created in frames:
        rows.extend(events(frame, url, retrieved, created))
    t = pd.DataFrame(rows, columns=EVENT_COLS + X_COLS)
    twice = t.event_id[t.event_id.duplicated()]
    if len(twice):
        raise RuntimeError(f"an event given twice: {list(twice.unique()[:5])}")
    return t.sort_values(["event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA NCEI's Storm Events Database, the grid's storm types, from 2015")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--first-year", type=int, default=2015)
    ap.add_argument("--listing", help="the directory listing from this saved file, not asked")
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
        if args.listing:
            with open(args.listing, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
            log(f"  the listing read from {args.listing}")
        else:
            content, _ = ip.fetch_raw(CONNECTOR, DIR, log, offline=args.offline, fresh=True, headers=UA, timeout=120)
            html = content.decode("utf-8", errors="replace")
        files = {y: v for y, v in listing(html).items() if y >= args.first_year}
        frames = []
        for year in sorted(files):
            name, created = files[year]
            url = DIR + name
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
            if content[:2] != b"\x1f\x8b":
                raise RuntimeError(f"{url} is not a gzip file")
            frame = pd.read_csv(io.BytesIO(gzip.decompress(content)), dtype=str, keep_default_na=False)
            frames.append((frame, url, rec.get("retrieved_at") or "", created))
            log(f"  {year}: {len(frame)} events in the file")
        t = build(frames)
        years = pd.to_datetime(t.event_date).dt.year
        by = t.groupby("event_type").size().sort_values(ascending=False)
        header = [
            f"Energy Research Warehouse (ERW): NOAA NCEI Storm Events Database, the event types that take power lines down or strain the grid, {years.min()} to {years.max()} (session 2042)",
            "Shape: events (docs/datastandard.md v0). event_id noaa_storm:<EVENT_ID>; event_date the begin time in UTC (NCEI's local standard time less the "
            "offset its CZ_TIMEZONE names, no daylight saving; x_begin_local keeps NCEI's); event_type NCEI's EVENT_TYPE in snake case (x_noaa_event_type its "
            "words); x_damage_property_usd and x_damage_crops_usd NCEI's K, M and B figures in dollars; x_geo the state's ISO 3166-2 code from its FIPS.",
            f"{len(t)} events of {len(TYPES)} types: " + "; ".join(f"{k} {v}" for k, v in by.items()) + ". Hail, floods, marine and the other types, "
            "and the narratives, are not taken. Values as published; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_storm_events.py; the files: "
            + ", ".join(f"{y} c{files[y][1]}" for y in sorted(files)),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA National Centers for Environmental Information, Storm Events Database (the National Weather Service's Storm Data), {PAGE}",
            f"  access: {DIR}StormEvents_details-ftp_v1.0_d<YEAR>_c<YYYYMMDD>.csv.gz",
            "License: the National Weather Service's records, in the public domain (NWS's notice: may be used without charge for any lawful purpose, "
            "not claimed as one's own, no endorsement implied, a modified copy not presented as official).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="National Oceanic and Atmospheric Administration (NOAA), National Centers for Environmental Information (NCEI)",
                                    report="Storm Events Database, bulk details files", report_url=PAGE,
                                    document_list=DIR, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} events"))
        print(f"{NAME}: {len(t)} events, {years.min()} to {years.max()}")
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
