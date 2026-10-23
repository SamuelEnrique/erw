#!/usr/bin/env python3
"""NOAA's U.S. Climate Reference Network (USCRN): the sunlight measured at stations near California's and Texas's solar
fleets, each month's average daily total global solar radiation (session 2107, chain 069: the sunlight solar runs on,
taken from NOAA's own network because NASA POWER's robots file disallows its API).

Energy Research Warehouse (ERW) connector. One series table from USCRN's monthly01 product, one fixed-width file a
station, with the product's headers.txt read to check the columns:

    https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-<station>.txt

    noaa_uscrn_solar_monthly   entity uscrn:<WBAN number>; variable solar_radiation (MJ/m2-day: the month's average of
               daily total global solar radiation, MJ per square meter a day, NOAA's SOLRAD_MONTHLY_AVG); ts_utc the first
               day of the month (NOAA's months are local standard time); freq P1M; geo US-<state>; ba the grid the station
               sits in (ciso or erco); node the station's name; x_station the file's station name; x_lat and x_lon (WGS-84,
               NOAA's); x_logger the datalogger program's version at the month's end

NOAA's note H: a month's value is valid only with fewer than 4 consecutive and no more than 5 total daily values
missing; a month that fails is written -9999.0 and has no row here, and the header counts them. A heading of
headers.txt not as read, a line that does not split into the 15 fields, a station's WBAN number or place changing
within its file, or a month given twice stops the run. Nothing is filled.

    python warehouse/connectors/noaa_uscrn.py [--offline] [--out-dir DIR]

Ceiling: nine requests (headers.txt and the eight stations' files, saved in warehouse/raw/noaa_uscrn/ and reused
offline; asked again unless --offline, since each file keeps its address as its months are added). NCEI's robots file disallows /data* and /orders* and some /access/crn/ paths, not /pub/. License: may be public
(NOAA NCEI, read 9: its restriction applies to the non-U.S. data in ISD; USCRN is NOAA's own U.S. network).
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "noaa_uscrn"
SOURCE = "noaa:uscrn_monthly01"
HOST = "www.ncei.noaa.gov"
BASE = "https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/"
TABLE = "noaa_uscrn_solar_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_station", "x_lat", "x_lon", "x_logger"]
HEADS = ["WBANNO", "LST_YRMO", "CRX_VN_MONTHLY", "PRECISE_LONGITUDE", "PRECISE_LATITUDE", "T_MONTHLY_MAX", "T_MONTHLY_MIN",
         "T_MONTHLY_MEAN", "T_MONTHLY_AVG", "P_MONTHLY_CALC", "SOLRAD_MONTHLY_AVG", "SUR_TEMP_MONTHLY_TYPE", "SUR_TEMP_MONTHLY_MAX",
         "SUR_TEMP_MONTHLY_MIN", "SUR_TEMP_MONTHLY_AVG"]
SOLRAD = HEADS.index("SOLRAD_MONTHLY_AVG")
# the stations: near the solar fleets of CAISO's southern and central California and ERCOT's West and Central Texas
STATIONS = {"CA_Fallbrook_5_NE": ("CA", "ciso"), "CA_Merced_23_WSW": ("CA", "ciso"), "CA_Stovepipe_Wells_1_SW": ("CA", "ciso"),
            "CA_Redding_12_WNW": ("CA", "ciso"), "TX_Monahans_6_ENE": ("TX", "erco"), "TX_Austin_33_NW": ("TX", "erco"),
            "TX_Bronte_11_NNE": ("TX", "erco"), "TX_Edinburg_17_NNE": ("TX", "erco")}
MISSING = -9999.0


def check_heads(text):
    lines = [l.split() for l in text.splitlines() if l.strip()]
    if len(lines) < 2 or lines[1] != HEADS:
        raise RuntimeError(f"headers.txt: the columns are not as read: {lines[1] if len(lines) > 1 else lines}")


def parse(text, station, base, counts):
    st, ba = STATIONS[station]
    out, seen, place = [], set(), None
    for k, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        f = line.split()
        if len(f) != len(HEADS):
            raise RuntimeError(f"{station} line {k + 1}: {len(f)} fields, not {len(HEADS)}: {line[:80]!r}")
        wban, yrmo, logger, lon, lat = f[0], f[1], f[2], f[3], f[4]
        if place is None:
            place = (wban, lon, lat)
        elif place != (wban, lon, lat):
            raise RuntimeError(f"{station} line {k + 1}: the WBAN number or place changed: {place} to {(wban, lon, lat)}")
        if len(yrmo) != 6 or not yrmo.isdigit() or not 1 <= int(yrmo[4:]) <= 12:
            raise RuntimeError(f"{station} line {k + 1}: not a year and month: {yrmo!r}")
        if yrmo in seen:
            raise RuntimeError(f"{station}: {yrmo} given twice")
        seen.add(yrmo)
        v = float(f[SOLRAD])
        if v == MISSING:
            counts[station] = counts.get(station, 0) + 1
            continue
        if v < 0:
            raise RuntimeError(f"{station} {yrmo}: a negative radiation that is not NOAA's missing mark: {v}")
        out.append(dict(base, entity=f"uscrn:{wban}", variable="solar_radiation", ts_utc=f"{yrmo[:4]}-{yrmo[4:]}-01T00:00:00Z", value=v,
                        unit="MJ/m2-day", freq="P1M", geo=f"US-{st}", market="", node=station.replace("_", " "), ba=ba,
                        x_station=station, x_lat=lat, x_lon=lon, x_logger=logger))
    if not out:
        raise RuntimeError(f"{station}: no month with a value")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA's USCRN: monthly average daily solar radiation at stations near CAISO's and ERCOT's solar")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        heads, _ = ip.fetch_raw(CONNECTOR, BASE + "headers.txt", log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        check_heads(heads.decode("utf-8"))
        rows, counts, latest, urls = [], {}, "", []
        for station in STATIONS:
            url = f"{BASE}CRNM0102-{station}.txt"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content.decode("utf-8"), station, base, counts)
            log(f"  {station}: {len(got)} months, {counts.get(station, 0)} missing")
            rows += got
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + ["ba"] + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        missing = ", ".join(f"{k} {n}" for k, n in counts.items())
        head = [
            "Energy Research Warehouse (ERW): NOAA, U.S. Climate Reference Network (USCRN) monthly01, the month's average daily total global "
            f"solar radiation at {len(STATIONS)} stations near CAISO's and ERCOT's solar fleets, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} "
            "(session 2107)",
            "Shape: series (docs/datastandard.md v0). entity uscrn:<WBAN>; variable solar_radiation (MJ/m2-day: MJ per square meter a day, "
            "NOAA's SOLRAD_MONTHLY_AVG); freq P1M; ts_utc the month's first day (NOAA's months are local standard time); geo US-<state>; "
            "ba ciso or erco; node the station; x_station, x_lat, x_lon (WGS-84), x_logger (the datalogger program's version).",
            "A month NOAA writes -9999.0 has no row (note H: valid only with fewer than 4 consecutive and no more than 5 total days missing); "
            f"the months without a row: {missing or 'none'}. A station's first months can be missing while it was installed. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_uscrn.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} National Oceanic and Atmospheric Administration, National Centers for Environmental Information, U.S. Climate "
            f"Reference Network, monthly01 product, {BASE}",
            f"  access: {BASE}headers.txt, {BASE}CRNM0102-<station>.txt for the stations above",
            "License: may be public (NOAA NCEI: a work of the U.S. government; its restriction concerns the non-U.S. data in ISD, not USCRN; "
            "see license_verdicts.csv). Cite NOAA NCEI, U.S. Climate Reference Network.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} stations; months missing: {missing or 'none'}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="NOAA NCEI",
                                    report="U.S. Climate Reference Network (USCRN), monthly01 product: SOLRAD_MONTHLY_AVG",
                                    report_url=BASE, document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
