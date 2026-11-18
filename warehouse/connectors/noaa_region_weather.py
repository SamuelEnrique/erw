#!/usr/bin/env python3
"""Weather stations for EIA's thirteen regions of the lower 48, hourly temperature at each from July 2018 to the newest
hour, and each region's population-weighted temperature (session 7803, chain 401 part C, tables 6 and 7).

Energy Research Warehouse (ERW) connector. Writes:

    noaa_region_stations              one row per county chosen: its station, the station's distance, its weight
    noaa_region_station_hourly_<year> temperature_f at every chosen station and UTC hour, one table a UTC year
    region_weather_hourly             each region and UTC hour: temperature_f, the weighted mean of its stations

    python warehouse/connectors/noaa_region_weather.py --fetch-only     # the pulls, to warehouse/raw (no data lock)
    python warehouse/connectors/noaa_region_weather.py                  # the tables, from the raw files, under the lock
    python warehouse/connectors/noaa_region_weather.py --out-dir DIR    # a trial

THE RULE (chain 401 part C, item 6). For each region, its counties (eia_county_region's primary region) in order of
population (census_county_population, the estimate of 1 July 2025), until 80 percent of the region's population is
covered, at most 25 counties. For each county, the nearest station to the county's center of population (the Census
Bureau's CenPop2020_Mean_CO.txt) among NOAA's stations with a WBAN number in isd-history.csv that holds at least 95 percent
of the hours of each year: 2018 (from 1 July), 2019 to 2024, and 2025 to the end of ISD-Lite (31 July); the next nearest
is tried when one falls short, within 150 km. A county's weight is its population over the population of its region's
chosen counties; a station chosen by several counties carries their sum.

THE TWO PRODUCTS (as warehouse/connectors/noaa_grid_weather.py, whose readers this imports): ISD-Lite to 2025-07-31 (NOAA's
ISD ended on 27 August 2025), one file per station and year from NOAA's mirror; Local Climatological Data v2 from
2025-08-01, through NCEI's Access Data Service, every report dated in local standard time, put on ISD-Lite's hour rule.
A station's local standard time offset is read from the data: over July 2025, held by both, the offset of -5, -6, -7 or -8
hours under which the two agree to a tenth of a degree Celsius in the most hours (the share is logged; under 80 percent the
station's LCD hours are not used). Stations already held by noaa_station_weather_hourly are pulled again only for what that
table lacks (it begins in 2019).

THE REGION'S HOUR. Each station's runs of at most three missing hours between two measured hours are interpolated on a
straight line (noaa_grid_weather's rule); a region's hour is written only when every one of its stations has a value then,
and is the weighted mean (x_stations: how many). Nothing else is filled. Method: docs/methods/region_weather.md.
"""

import argparse
import datetime as dt
import io
import math
import os
import sys
import time
import traceback

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import noaa_grid_weather as ngw  # noqa: E402  ISD-Lite and LCD readers, the hour rule, the gap fill

NAME = "noaa_region_weather"
STATIONS_TABLE, HOURLY_PREFIX, REGION_TABLE = "noaa_region_stations", "noaa_region_station_hourly", "region_weather_hourly"
CENPOP = "https://www2.census.gov/geo/docs/reference/cenpop2020/county/CenPop2020_Mean_CO.txt"
CENPOP_PAGE = "https://www.census.gov/geographies/reference-files/time-series/geo/centers-population.html"
SOURCE_LITE, SOURCE_LCD, SOURCE_CENPOP = "noaa:isd_lite", "noaa:lcd_v2", "census:cenpop2020_county"
SOURCE_STATIONS, SOURCE_REGION = "erw:noaa_region_stations", "erw:region_weather_hourly"
METHOD = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/region_weather.md"
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
START = pd.Timestamp("2018-07-01T00:00:00Z")
SEAM = ngw.SEAM
SHARE, MAX_COUNTIES, MIN_HOURS, MAX_KM = 0.80, 25, 0.95, 150.0
UA = ngw.UA
RAW_READ = ip.RAW_DIR
END = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=2)).date()  # the last day of LCD asked for
OFFSETS = {}  # station: (its local standard time offset, its July 2025 agreement)


def get(url, timeout=120):
    # a file this connector or noaa_grid_weather.py already saved is read from the raw files, not asked again
    for owner in (NAME, ngw.NAME):
        cached = ip.raw_cached(owner, url)
        if cached is not None:
            return cached[0]
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            time.sleep(ngw.PAUSE)
            if r.status_code == 404:
                return b""
            if r.status_code == 200:
                return r.content
            raise RuntimeError(f"{url}: HTTP {r.status_code}")
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5)


def read_table(name):
    for d in (ip.OUT_DIR, os.path.join(ip.ROOT, "warehouse", "output")):
        path = os.path.join(d, name + ".csv")
        if os.path.exists(path):
            n = 0
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("#"):
                        break
                    n += 1
            return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)
    raise RuntimeError(f"no {name}.csv")


def km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return 12742 * math.asin(math.sqrt(a))


def lite_year(usaf, wban, year):
    blob = get(ngw.lite_url(usaf, wban, year))
    if not blob or not ngw.is_gzip(blob):
        return pd.DataFrame(columns=["temp_c", "dew_c"])
    return ngw.parse_lite(blob)[0]


def lite_series(usaf, wban):
    parts = [p for p in (lite_year(usaf, wban, y) for y in range(2018, 2026)) if len(p) and isinstance(p.index, pd.DatetimeIndex)]
    if not parts:
        return pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC"))
    s = pd.concat([p["temp_c"] for p in parts])
    s = s[(s.index >= START) & (s.index < SEAM)].dropna()
    return s[~s.index.duplicated()]


def complete(s):
    """True when the series holds at least MIN_HOURS of the hours of each year (2018 from July, 2025 to the seam)."""
    for y in range(2018, 2026):
        lo = max(pd.Timestamp(f"{y}-01-01T00:00:00Z"), START)
        hi = min(pd.Timestamp(f"{y + 1}-01-01T00:00:00Z"), SEAM)
        need = (hi - lo) / pd.Timedelta(hours=1)
        if ((s.index >= lo) & (s.index < hi)).sum() < MIN_HOURS * need:
            return False
    return True


def lcd_series(wban, lite, end, log):
    """LCD v2 from 2025-07-01 to `end` (a date), its offset read against ISD-Lite over July 2025; the hours from the seam."""
    frames = []
    start = pd.Timestamp("2025-07-01")
    while start.date() <= end:
        stop = min(start + pd.DateOffset(months=3) - pd.Timedelta(days=1), pd.Timestamp(end))
        text = get(ngw.lcd_url(wban, start.strftime("%Y-%m-%d"), stop.strftime("%Y-%m-%d")), timeout=300)
        frames.append(text.decode("utf-8", "replace") if isinstance(text, bytes) else text)
        start = stop + pd.Timedelta(days=1)
    best, share = None, 0.0
    jul = lite[(lite.index >= pd.Timestamp("2025-07-01T00:00:00Z")) & (lite.index < SEAM)]
    for off in (5, 6, 7, 8):
        h = pd.concat([ngw.parse_lcd(t, off)[0]["temp_c"] for t in frames if t.strip()]) if frames else pd.Series(dtype=float)
        h = h[~h.index.duplicated()]
        both = jul.index.intersection(h.index)
        sh = float((abs(jul[both] - h[both]) <= 0.05).mean()) if len(both) else 0.0
        if sh > share:
            best, share, hourly = off, sh, h
    if best is None or share < 0.80:
        log(f"  LCD of {wban}: no offset agrees with ISD-Lite in 80 percent of July 2025 (best {share:.2f}); its LCD hours are not used")
        return pd.Series(dtype=float), None, share
    return hourly[hourly.index >= SEAM].dropna(), -best, share


def select(log):
    reg = read_table("eia_county_region")
    pop = read_table("census_county_population")
    p25 = pop[(pop["variable"] == "population_estimate") & (pop["ts_utc"] == "2025-07-01T00:00:00Z")]
    pops = dict(zip(p25["entity"], pd.to_numeric(p25["value"])))
    cen = pd.read_csv(io.BytesIO(get(CENPOP)), dtype=str, encoding="utf-8-sig")
    cen["fips"] = cen["STATEFP"].str.zfill(2) + cen["COUNTYFP"].str.zfill(3)
    centers = {f: (float(a), float(b)) for f, a, b in zip(cen["fips"], cen["LATITUDE"], cen["LONGITUDE"])}
    hist = pd.read_csv(io.BytesIO(get(ngw.HISTORY)), dtype=str)
    hist = hist[(hist["CTRY"] == "US") & (hist["WBAN"] != "99999") & hist["LAT"].notna() & hist["LON"].notna()]
    hist = hist[(hist["BEGIN"] <= "20180101") & (hist["END"] >= "20250731")].copy()
    hist["lat"], hist["lon"] = pd.to_numeric(hist["LAT"]), pd.to_numeric(hist["LON"])
    hist = hist[(hist["lat"] != 0) | (hist["lon"] != 0)]
    stations = hist[["USAF", "WBAN", "STATION NAME", "lat", "lon"]].drop_duplicates(["USAF", "WBAN"]).values.tolist()
    tried, rows, series = {}, [], {}
    for region in REGIONS:
        r = reg[reg["x_region"] == region].copy()
        r["pop"] = r["entity_id"].map(pops).fillna(0)
        r = r.sort_values("pop", ascending=False)
        total = r["pop"].sum()
        chosen, cum = [], 0.0
        for _, c in r.iterrows():
            if cum >= SHARE * total or len(chosen) >= MAX_COUNTIES:
                break
            chosen.append(c)
            cum += c["pop"]
        log(f"{region}: {len(chosen)} counties, {cum / total:.3f} of {total:,.0f}")
        for c in chosen:
            fips = c["x_fips"]
            lat, lon = centers[fips]
            near = sorted((km(lat, lon, s[3], s[4]), s) for s in stations)
            pick = None
            for d, s in near:
                if d > MAX_KM:
                    break
                sid = f"{s[0]}-{s[1]}"
                if sid not in tried:
                    ser = lite_series(s[0], s[1])
                    ok = complete(ser)
                    if ok:
                        # session 7803: a station whose Local Climatological Data do not line up with its ISD-Lite (no
                        # offset agrees in 80 percent of July 2025) has no hours after the seam and would empty its
                        # region from August 2025, so it is not complete either: the next nearest is tried
                        lcd, off, share = lcd_series(s[1], ser, END, log)
                        ok = off is not None
                        if ok:
                            series[sid] = pd.concat([ser, lcd]).sort_index()
                            OFFSETS[sid] = (off, share)
                            log(f"  {sid}: ISD-Lite and LCD, offset {off}, July 2025 agreement {share:.3f}, {len(series[sid]):,} hours")
                    tried[sid] = ok
                if tried[sid]:
                    pick = (d, s)
                    break
            rows.append(dict(region=region, fips=fips, county=c["name"], pop=c["pop"], region_pop_chosen=cum,
                             station=f"{pick[1][0]}-{pick[1][1]}" if pick else "", station_name=pick[1][2] if pick else "",
                             km=round(pick[0], 1) if pick else None))
            log(f"  {fips} {c['name']}: {rows[-1]['station']} {rows[-1]['station_name']} {rows[-1]['km']} km")
    return pd.DataFrame(rows), series


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW region weather (session 7803)")
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        ip.RAW.open(NAME, run_id)
        sel, series = select(log)
        offsets = {sid: v[0] for sid, v in OFFSETS.items()}
        lcd_share = {sid: v[1] for sid, v in OFFSETS.items()}
        if args.fetch_only:
            log.close()
            return 0
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        # the stations table: one row per county chosen
        sel["weight"] = sel["pop"] / sel["region_pop_chosen"]
        st = pd.DataFrame({
            "entity": "census:county:" + sel["fips"], "variable": "station_weight", "ts_utc": "2025-07-01T00:00:00Z",
            "value": sel["weight"].round(8), "unit": "ratio", "freq": "", "geo": "", "market": "", "node": sel["station"],
            "source": SOURCE_STATIONS, "source_url": METHOD, "retrieved_at": retrieved, "vintage": "",
            "x_region": sel["region"], "x_county": sel["county"], "x_population_2025": sel["pop"].astype(int),
            "x_station_name": sel["station_name"], "x_km": sel["km"],
            "x_lst_offset": sel["station"].map(lambda s: offsets.get(s)), "x_lcd_agreement_jul2025": sel["station"].map(lambda s: round(lcd_share.get(s, 0), 3))})
        st = st[st["node"] != ""]
        cols_st = list(st.columns)
        ip.write_snapshot(st, STATIONS_TABLE, [
            "Energy Research Warehouse (ERW): the counties chosen for each EIA region's weather and their stations (session 7803)",
            "Shape: series (docs/datastandard.md v0). entity the county, variable station_weight (its population over its region's "
            "chosen counties', 1 July 2025 estimates), node the station (USAF-WBAN). Rule and method: docs/methods/region_weather.md.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_region_weather.py",
            f"Source: {SOURCE_STATIONS} the ERW's choice of counties and stations, {METHOD}",
            f"  read from: eia_county_region, census_county_population; {SOURCE_CENPOP} {CENPOP}; NOAA isd-history.csv {ngw.HISTORY}",
            "License: public (derived by the ERW from Census Bureau, EIA and NOAA data)."], log, cols_st)
        # station-hours by UTC year; then the regions
        filled = {}
        for sid, s in series.items():
            if sid in set(sel["station"]):
                f, _ = ngw.fill_short(s.asfreq("h"))
                filled[sid] = f
        frame = pd.DataFrame(filled)
        for y in range(2018, pd.Timestamp.now(tz="UTC").year + 1):
            part = frame[(frame.index.year == y)]
            long = part.stack().rename("temp_c").reset_index()
            long.columns = ["ts", "station", "temp_c"]
            if not len(long):
                continue
            t = f"{HOURLY_PREFIX}_{y}"
            out = pd.DataFrame({"entity": "noaa:" + long["station"], "variable": "temperature_f", "ts_utc": long["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "value": (long["temp_c"] * 9 / 5 + 32).round(2), "unit": "degF", "freq": "PT1H",
                                "source": np.where(long["ts"] < SEAM, SOURCE_LITE, SOURCE_LCD)})
            cols = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source"]
            ip.write_snapshot(out[cols], t, [
                f"Energy Research Warehouse (ERW): hourly temperature at the stations of EIA's regions, the hours of {y} (UTC) (session 7803)",
                "Shape: series (docs/datastandard.md v0). entity noaa:<USAF-WBAN>, temperature_f; ISD-Lite before 2025-08-01, "
                "Local Climatological Data v2 from it on ISD-Lite's hour rule (source); runs of at most three missing hours "
                "interpolated. One table a UTC year. Method: docs/methods/region_weather.md.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_region_weather.py",
                f"Source: {SOURCE_LITE} ISD-Lite (Integrated Surface Database, hourly), {ngw.PAGE_LITE}",
                f"Source: {SOURCE_LCD} Local Climatological Data v2 (NCEI Access Data Service), {ngw.PAGE_LCD}",
                "License: public (U.S. Government data, NOAA NCEI)."], log, cols)
        w = sel[sel["station"] != ""].groupby(["region", "station"])["weight"].sum().reset_index()
        rows = []
        for region, g in w.groupby("region"):
            sub = frame[g["station"].tolist()]
            ok = sub.notna().all(axis=1)
            val = (sub[ok] * g["weight"].values).sum(axis=1) / g["weight"].sum()
            rows.append(pd.DataFrame({"entity": "eia930:" + region, "variable": "temperature_f",
                                      "ts_utc": val.index.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": (val * 9 / 5 + 32).round(2),
                                      "unit": "degF", "freq": "PT1H", "source": SOURCE_REGION, "x_stations": len(g)}))
            log(f"  {region}: {int(ok.sum()):,} hours with every station, {int((~ok).sum()):,} without")
        rg = pd.concat(rows, ignore_index=True)
        ip.write_snapshot(rg, REGION_TABLE, [
            "Energy Research Warehouse (ERW): each EIA region's temperature by hour, its stations weighted by county population (session 7803)",
            "Shape: series (docs/datastandard.md v0). entity eia930:<region>, temperature_f, the weighted mean of the region's "
            "stations (noaa_region_stations), written only for an hour every station holds (x_stations). Method: docs/methods/region_weather.md.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_region_weather.py",
            f"Source: {SOURCE_REGION} the ERW's weighted means of noaa_region_station_hourly_<year>, {METHOD}",
            "License: public (derived by the ERW from NOAA, Census Bureau and EIA data)."], log, list(rg.columns))
        ip.update_sources([
            dict(source=SOURCE_LITE, publisher="NOAA National Centers for Environmental Information", report="ISD-Lite (Integrated Surface Database, hourly)",
                 report_url=ngw.PAGE_LITE, document_list=ngw.LITE, license="public", tables=[f"{HOURLY_PREFIX}_{y}" for y in range(2018, 2026)]),
            dict(source=SOURCE_LCD, publisher="NOAA National Centers for Environmental Information", report="Local Climatological Data v2",
                 report_url=ngw.PAGE_LCD, document_list=ngw.API, license="public", tables=[f"{HOURLY_PREFIX}_{y}" for y in (2025, 2026)]),
            dict(source=SOURCE_STATIONS, publisher="Energy Research Warehouse", report="Counties and stations of EIA's regions",
                 report_url=METHOD, document_list="", license="public", tables=[STATIONS_TABLE]),
            dict(source=SOURCE_REGION, publisher="Energy Research Warehouse", report="Region temperature, population weighted",
                 report_url=METHOD, document_list="", license="public", tables=[REGION_TABLE])])
        results.append(dict(table=REGION_TABLE, market="all", status="ok", detail=f"{len(rg)} rows, {len(filled)} stations"))
        print(f"{NAME}: {len(filled)} stations, {len(sel)} counties, {len(rg):,} region-hours")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=REGION_TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.fetch_only:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
