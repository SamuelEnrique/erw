#!/usr/bin/env python3
"""National Weather Service: hourly observed temperature and wind at one airport per ISO load center, and the 7-day
hourly forecast there.

Energy Research Warehouse (ERW) connector, session 24 (the weather overlay on /grid). Source: the NWS API,
api.weather.gov (free, no key; the NWS asks for a User-Agent that names the application and a contact, and for
attribution: "Weather data: National Weather Service"). Every response is stored raw under
warehouse/raw/weather_nws/<run_id>/.

    python warehouse/connectors/weather_nws.py              # observations asked for 30 days (NWS serves about 7), and the forecast
    python warehouse/connectors/weather_nws.py --days 3

Stations, one airport per ISO's load center (a choice, documented here and in the table header):
  ERCOT KDFW (Dallas/Fort Worth), CAISO KLAX (Los Angeles), NYISO KLGA (New York LaGuardia), ISO-NE KBOS (Boston),
  PJM KPHL (Philadelphia), MISO KIND (Indianapolis; the ERW's MISO hub is INDIANA.HUB), SPP KOKC (Oklahoma City).

Tables (series shape):
  weather_obs_hourly       entity nws:<station>, node the ISO; variables temperature_f (degF) and wind_speed_mph (mph,
                           both converted from the API's metric values, docs/datastandard.md decision 27): the mean of
                           the station's quality-controlled observations whose time falls in the UTC hour (ts_utc the
                           hour start); an hour with no observation is not written. freq PT1H.
  weather_forecast_hourly  the NWS hourly gridpoint forecast at the station's point (units=si): temperature_f and
                           wind_speed_mph (the lower number when NWS gives a range) for each hour it covers (about 156);
                           vintage is the forecast's updateTime, and each run merges a new vintage over the hours.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

API = "https://api.weather.gov"
UA = {"User-Agent": "(ERW energy research warehouse, https://github.com/SamuelEnrique/erw)", "Accept": "application/geo+json"}
STATIONS = {"ERCOT": ("KDFW", "US-TX"), "CAISO": ("KLAX", "US-CA"), "NYISO": ("KLGA", "US-NY"), "ISO-NE": ("KBOS", "US-MA"),
            "PJM": ("KPHL", "US-PA"), "MISO": ("KIND", "US-IN"), "SPP": ("KOKC", "US-OK")}
OBS, FC = "weather_obs_hourly", "weather_forecast_hourly"
SOURCE_OBS, SOURCE_FC = "nws:observations", "nws:forecast_hourly"


def get(url, log, **kw):
    def call():
        r = requests.get(url, headers=UA, timeout=90, **kw)
        if r.status_code != 200:
            raise RuntimeError(f"NWS HTTP {r.status_code} for {r.url}")
        return r
    return ip.with_retries(url, call, log)


def observations(station, days, log):
    end = pd.Timestamp.now(tz="UTC").floor("h")
    start = end - pd.Timedelta(days=days)
    url, params, rows = f"{API}/stations/{station}/observations", {"start": ip.utc_iso(start), "end": ip.utc_iso(end)}, []
    while url:
        r = get(url, log, params=params)
        d = r.json()
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for f in d.get("features", []):
            p = f["properties"]
            rows.append({"t": p["timestamp"], "temperature_c": (p.get("temperature") or {}).get("value"),
                         "wind_speed_kmh": (p.get("windSpeed") or {}).get("value"), "_url": r.url, "_got": got})
        nxt = (d.get("pagination") or {}).get("next")
        url, params = (nxt, None) if nxt and d.get("features") else (None, None)
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(f"{station}: no observations")
    df["t"] = pd.to_datetime(df["t"], utc=True)
    df = df[(df["t"] >= start) & (df["t"] < end)]
    df["hour"] = df["t"].dt.floor("h")
    log(f"  {station}: {len(df)} observations {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M} UTC")
    return df


def forecast(station, log):
    s = get(f"{API}/stations/{station}", log).json()
    lon, lat = s["geometry"]["coordinates"]
    pt = get(f"{API}/points/{lat:.4f},{lon:.4f}", log).json()["properties"]
    r = get(pt["forecastHourly"], log, params={"units": "si"})
    p = r.json()["properties"]
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    rows = []
    for x in p["periods"]:
        if x.get("temperatureUnit") != "C":
            raise RuntimeError(f"{station}: forecast temperature unit {x.get('temperatureUnit')}, expected C")
        w = re.findall(r"\d+(?:\.\d+)?", x.get("windSpeed") or "")
        rows.append({"hour": pd.Timestamp(x["startTime"]).tz_convert("UTC"), "temperature_c": x["temperature"],
                     "wind_speed_kmh": float(w[0]) if w else None, "_url": r.url, "_got": got,
                     "_vintage": p.get("updateTime") or p.get("generatedAt")})
    log(f"  {station} forecast: {len(rows)} hours, updated {rows[0]['_vintage'] if rows else '?'}")
    return pd.DataFrame(rows)


def to_series(df, station, iso, geo, source, vintage=False):
    """The station's hours as series rows, in the ERW's units (docs/datastandard.md decision 27): degF and mph."""
    out = []
    for var, name, unit, conv in (("temperature_c", "temperature_f", "degF", lambda c: c * 9 / 5 + 32),
                                  ("wind_speed_kmh", "wind_speed_mph", "mph", lambda k: k / 1.609344)):
        v = df.dropna(subset=[var])
        out.append(pd.DataFrame({
            "entity": f"nws:{station}", "variable": name, "ts_utc": v["hour"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "value": conv(v[var].astype(float)).round(1), "unit": unit, "freq": "PT1H",
            "geo": geo, "market": "", "node": iso, "source": source, "source_url": v["_url"],
            "retrieved_at": v["_got"],
            "vintage": pd.to_datetime(v["_vintage"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ") if vintage else ""}))
    return pd.concat(out, ignore_index=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW NWS weather")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"weather_nws_{run_id}.log"))
    ip.RAW.open("weather_nws", run_id)
    results, obs, fcs, absent = [], [], [], []
    for iso, (station, geo) in STATIONS.items():
        try:
            o = observations(station, args.days, log)
            g = o.groupby("hour")
            hourly = g[["temperature_c", "wind_speed_kmh"]].mean().reset_index()
            last = g[["_url", "_got"]].last().reset_index()
            obs.append(to_series(hourly.merge(last, on="hour"), station, iso, geo, SOURCE_OBS))
        except Exception as exc:
            last_ = ip.redact(repr(exc))[:300]
            log(f"{iso} {station} observations FAILED: {last_}")
            print(f"weather_nws {station} observations FAILED: {last_}", file=sys.stderr)
            absent.append(f"{station} observations")
            results.append(dict(table=OBS, market=station, status="failed", detail=last_))
        try:
            fcs.append(to_series(forecast(station, log), station, iso, geo, SOURCE_FC, vintage=True))
        except Exception as exc:
            last_ = ip.redact(repr(exc))[:300]
            log(f"{iso} {station} forecast FAILED: {last_}")
            print(f"weather_nws {station} forecast FAILED: {last_}", file=sys.stderr)
            absent.append(f"{station} forecast")
            results.append(dict(table=FC, market=station, status="failed", detail=last_))
    stations = "; ".join(f"{iso} {s}" for iso, (s, _) in STATIONS.items())
    common = [f"Stations (one airport per ISO load center, a choice in warehouse/connectors/weather_nws.py): {stations}",
              f"Retrieved: {run_id} (UTC) by warehouse/connectors/weather_nws.py",
              f"Run log: warehouse/output/logs/weather_nws_{run_id}.log",
              f"Raw files: warehouse/raw/weather_nws/{run_id}/ (not in git)"] + \
             ([f"Absent inputs: {', '.join(absent)} (failed this run)"] if absent else []) + \
             ["License: public (US government work; attribution: \"Weather data: National Weather Service\")."]
    try:
        if obs:
            s = pd.concat(obs, ignore_index=True)
            ip.write_csv(s[ip.SERIES_COLS], OBS, [
                "Energy Research Warehouse (ERW): NWS observed temperature and wind, hourly, at one airport per ISO",
                "Shape: series (docs/datastandard.md v0). freq PT1H: ts_utc is the UTC hour start; the value is the mean "
                "of the station's observations in the hour (NWS quality-controlled values; an hour with none is absent).",
                f"Window: the last {args.days} days asked each run; the NWS API serves about the last 7 days of "
                "observations, so the table reaches back further only as daily runs merge.",
                f"Source: {SOURCE_OBS} National Weather Service API, {API}/stations/<station>/observations"] + common, log)
            results.append(dict(table=OBS, market="all", status="ok", detail=f"{len(obs)} stations"))
        if fcs:
            f = pd.concat(fcs, ignore_index=True)
            ip.write_csv(f[ip.SERIES_COLS], FC, [
                "Energy Research Warehouse (ERW): NWS hourly forecast of temperature and wind at one airport per ISO",
                "Shape: series (docs/datastandard.md v0). freq PT1H: ts_utc is the forecast hour's start (UTC); vintage "
                "is the forecast's updateTime. A newer run replaces the value for the same hour (the latest forecast).",
                "Window: the hours the forecast covers (about 7 days ahead).",
                f"Source: {SOURCE_FC} National Weather Service API, {API}/points/<lat,lon> then its forecastHourly "
                "(units=si)"] + common, log)
            results.append(dict(table=FC, market="all", status="ok", detail=f"{len(fcs)} stations"))
        ip.update_sources([
            dict(source=SOURCE_OBS, publisher="National Weather Service (NWS, NOAA)", report="Station observations (api.weather.gov)",
                 report_url="https://www.weather.gov/documentation/services-web-api", document_list=f"{API}/stations/KDFW/observations",
                 license="public", tables=[OBS]),
            dict(source=SOURCE_FC, publisher="National Weather Service (NWS, NOAA)", report="Hourly gridpoint forecast (api.weather.gov)",
                 report_url="https://www.weather.gov/documentation/services-web-api", document_list=f"{API}/points/<lat,lon>",
                 license="public", tables=[FC])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"weather_nws FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=OBS, market="write", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("weather_nws", run_id, results)
    log.close()
    print(f"weather_nws run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
