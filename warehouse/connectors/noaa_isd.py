#!/usr/bin/env python3
"""Hourly station temperature and dew point from NOAA NCEI's Integrated Surface Database (session 49, approved pull c).

Energy Research Warehouse (ERW) connector. Writes one series table,

    warehouse/output/noaa_isd_hourly.csv    temperature_f, dew_point_f per station observation; partition column ba
                                            (the grid the station stands for)

from NCEI's Access Data Service, dataset global-hourly (ISD), for the days of every event window of event_window_daily
and its baseline days, at one airport per grid (and a second for ERCOT, CAISO and PJM where the ceiling allows):

    ERCOT DFW (and IAH), CAISO SAC (and LAX), PJM PHL (and ORD), MISO MSP, NYISO JFK, ISO-NE BOS, SPP OKC

    python warehouse/connectors/noaa_isd.py

Ceiling 100,000 rows, counted as the rows the service returns (about 40 a station-day: hourly METARs, specials and
synoptic reports alike; the service takes no report-type filter). Requests go one station and one contiguous date range
at a time, smallest events first; before each request the rows still allowed are checked against an estimate, and the
pull stops rather than pass the ceiling, recording what it left out. Each response is saved under warehouse/raw/.
Values: ISD's TMP and DEW, tenths of a degree Celsius with a quality code; 9999 (missing) and the codes ISD marks
suspect or erroneous (2, 3, 6, 7) are not written. License: public domain (U.S. Government data, NOAA NCEI).
"""

import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "noaa_isd_hourly"
API = "https://www.ncei.noaa.gov/access/services/data/v1"
PAGE = "https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database"
SOURCE = "noaa:isd_global_hourly"
CEILING = 100_000
PER_DAY = 45  # rows the service returns per station-day, a cautious estimate (2021-02-15 DFW: 53; two days: 86)
# station: (ISD id USAF+WBAN, grid ba, the grid's time zone, primary)
STATIONS = {
    "DFW": ("72259003927", "erco", "America/Chicago", True), "IAH": ("72243012960", "erco", "America/Chicago", False),
    "SAC": ("72483023232", "ciso", "America/Los_Angeles", True), "LAX": ("72295023174", "ciso", "America/Los_Angeles", False),
    "PHL": ("72408013739", "pjm", "America/New_York", True), "ORD": ("72530094846", "pjm", "America/New_York", False),
    "MSP": ("72658014922", "miso", "EST", True), "JFK": ("74486094789", "nyis", "America/New_York", True),
    "BOS": ("72509014739", "isne", "America/New_York", True), "OKC": ("72353013967", "swpp", "America/Chicago", True),
}
# event: (window start, end, baseline offsets in days or calendar years, the grids)
EVENTS = {
    "caiso_heat_2020": ("2020-08-10", "2020-08-24", [364, 728], ["ciso"]),
    "uri_2021": ("2021-02-07", "2021-02-24", ["2019", "2020"], ["erco"]),
    "elliott_2022": ("2022-12-19", "2022-12-29", [364, 728], ["erco", "isne", "miso", "nyis", "pjm", "swpp"]),
    "ercot_heat_2023": ("2023-08-01", "2023-09-10", [364, 728], ["erco"]),
    "covid_2020": ("2020-03-01", "2020-05-31", [364, 728], ["ciso", "erco", "isne", "miso", "nyis", "pjm", "swpp"]),
    # session 58 (approved pull: SAC and LAX, ceiling 10,000 rows): CAISO's September 2022 heat, weekday-aligned baselines
    "caiso_heat_2022": ("2022-08-31", "2022-09-09", [364, 728], ["ciso"]),
}
BAD_QUALITY = set("2367")


def ranges(event):
    """The event's contiguous local-date ranges: the window and each baseline."""
    s, e, base, _ = EVENTS[event]
    out = [(s, e)]
    for b in base:
        if isinstance(b, int):
            out.append(((pd.Timestamp(s) - pd.Timedelta(days=b)).strftime("%Y-%m-%d"),
                        (pd.Timestamp(e) - pd.Timedelta(days=b)).strftime("%Y-%m-%d")))
        else:
            out.append((f"{b}{s[4:]}", f"{b}{e[4:]}"))
    return out


def plan(only=None):
    """(station, local start, local end) requests: primary stations of every event first, smallest events first, then
    the second stations; a range already requested for a station is not requested again. only: one event's ranges."""
    jobs, seen = [], set()
    for primary in (True, False):
        for ev in ([only] if only else EVENTS):
            for code, (sid, ba, tz, prim) in STATIONS.items():
                if prim != primary or ba not in EVENTS[ev][3]:
                    continue
                for s, e in ranges(ev):
                    if (code, s, e) not in seen:
                        seen.add((code, s, e))
                        jobs.append((code, s, e, ev))
    return jobs


def parse(text, code):
    df = pd.read_csv(io.StringIO(text), dtype=str)
    out = []
    for col, var in (("TMP", "temperature_f"), ("DEW", "dew_point_f")):
        if col not in df.columns:
            continue
        v = df[col].str.split(",", expand=True)
        val, q = pd.to_numeric(v[0], errors="coerce"), v[1].str.strip()
        ok = val.notna() & (val.abs() < 9999) & ~q.isin(BAD_QUALITY)
        out.append(pd.DataFrame({"ts": pd.to_datetime(df.loc[ok, "DATE"], utc=True), "variable": var,
                                 "value": (val[ok] / 10.0 * 9 / 5 + 32).round(2), "report_type": df.loc[ok, "REPORT_TYPE"].str.strip()}))
    return pd.concat(out, ignore_index=True), len(df), (df["NAME"].iloc[0] if "NAME" in df.columns and len(df) else "")


def main():
    """python noaa_isd.py: every event, the table rewritten. Session 58: python noaa_isd.py --event caiso_heat_2022
    --ceiling 10000: one event's ranges, merged into the table (its other rows kept), under its own ceiling."""
    global CEILING
    only = sys.argv[sys.argv.index("--event") + 1] if "--event" in sys.argv else None
    if only and only not in EVENTS:
        raise SystemExit(f"no event {only}")
    if "--ceiling" in sys.argv:
        CEILING = int(sys.argv[sys.argv.index("--ceiling") + 1])
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"noaa_isd_{run_id}.log"))
    ip.RAW.open("noaa_isd", run_id)
    results, frames, pulled, skipped, names = [], [], 0, [], {}
    jobs = plan(only)
    log(f"ERW noaa_isd run {run_id}: {len(jobs)} station ranges planned; ceiling {CEILING} rows returned")
    try:
        for code, s, e, ev in jobs:
            sid, ba, tz, _ = STATIONS[code]
            days = (pd.Timestamp(e) - pd.Timestamp(s)).days + 1
            if pulled + days * PER_DAY > CEILING:
                skipped.append(f"{code} {s} to {e} ({ev})")
                log(f"  skipped {code} {s} to {e} ({ev}): {pulled:,} rows pulled, {days * PER_DAY:,} more would pass the ceiling")
                continue
            # the local days as UTC instants
            t0 = pd.Timestamp(s).tz_localize(tz).tz_convert("UTC")
            t1 = (pd.Timestamp(e) + pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC") - pd.Timedelta(seconds=1)
            params = {"dataset": "global-hourly", "stations": sid, "startDate": t0.strftime("%Y-%m-%dT%H:%M:%S"),
                      "endDate": t1.strftime("%Y-%m-%dT%H:%M:%S"), "dataTypes": "TMP,DEW", "format": "csv",
                      "includeStationName": "true"}

            def call():
                r = requests.get(API, params=params, timeout=600)
                if r.status_code != 200 or not r.text.startswith('"STATION"'):
                    raise RuntimeError(f"NCEI HTTP {r.status_code}: {r.text[:200]}")
                return r
            r = ip.with_retries(f"NCEI {code} {s}", call, log)
            obs, n, name = parse(r.text, code)
            pulled += n
            names[code] = name
            obs["code"], obs["url"] = code, r.url
            frames.append(obs)
            log(f"  {code} ({name}) {s} to {e} ({ev}): {n} rows returned, {len(obs)} values kept; {pulled:,} pulled")
        if not frames:
            raise RuntimeError("nothing pulled")
        x = pd.concat(frames, ignore_index=True).drop_duplicates(["code", "variable", "ts", "report_type"])
        # one value per station, variable and instant: the routine hourly report (FM-15) where two types share it
        x["rank"] = (x["report_type"] != "FM-15").astype(int)
        x = x.sort_values(["code", "variable", "ts", "rank"]).drop_duplicates(["code", "variable", "ts"])
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        s_ = pd.DataFrame({
            "entity": "noaa:" + x["code"], "variable": x["variable"], "ts_utc": x["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "value": x["value"], "unit": "degF", "freq": "", "geo": "", "market": "", "node": x["report_type"],
            "source": SOURCE, "source_url": x["url"].map(ip.redact), "retrieved_at": retrieved, "vintage": "",
            "ba": x["code"].map(lambda c: STATIONS[c][1]), "x_station_id": x["code"].map(lambda c: STATIONS[c][0])})
        cols = ip.SERIES_COLS + ["ba", "x_station_id"]
        header = [
            "Energy Research Warehouse (ERW): hourly station temperature and dew point, NOAA NCEI Integrated Surface "
            "Database, for the event windows of event_window_daily and their baseline days (session 49)",
            "Shape: series (docs/datastandard.md v0), partition column ba (the grid the station stands for). temperature_f and "
            "dew_point_f, degrees Fahrenheit (ISD's tenths of a degree Celsius times 9/5 plus 32, to 2 decimals), at each observation's time (UTC); node is ISD's report type (FM-15 the routine "
            "hourly METAR; where two reports share an instant, FM-15 is kept). Irregular observation times: freq left blank.",
            "Stations: " + "; ".join(f"{c} {STATIONS[c][0]} {names.get(c, '')} ({STATIONS[c][1]})" for c in sorted(names)),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_isd.py",
            f"Run log: warehouse/output/logs/noaa_isd_{run_id}.log",
            f"Raw files: warehouse/raw/noaa_isd/{run_id}/ (not in git; manifest.csv lists each response and URL)",
            f"Source: {SOURCE} NOAA NCEI Integrated Surface Database (global-hourly), {PAGE}",
            f"  access: {API} (dataset global-hourly, dataTypes TMP,DEW)",
            f"Rows returned: {pulled:,} of the {CEILING:,} ceiling. Left out to stay under it: " + ("; ".join(skipped) or "nothing") + ".",
            "Values: ISD's TMP and DEW (tenths of a degree C); missing (9999) and quality codes 2, 3, 6 and 7 are not written.",
            "License: public domain (U.S. Government data, NOAA NCEI).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if only and os.path.exists(path):
            # one event merged into the table: its header as it was (the stations and the earlier pull), and a line for this one
            with open(path, encoding="utf-8") as f:
                old = [ln[1:].strip() for ln in f if ln.startswith("#")]
            header = old + [f"Session 58, {only}: {', '.join(sorted(names))} over its window and weekday-aligned baselines "
                            f"({'; '.join(f'{a} to {b}' for a, b in ranges(only))}); {pulled:,} rows returned of this pull's {CEILING:,} "
                            f"ceiling; retrieved {run_id} (UTC), run log warehouse/output/logs/noaa_isd_{run_id}.log, raw files "
                            f"warehouse/raw/noaa_isd/{run_id}/. Left out: " + ("; ".join(skipped) or "nothing") + "."]
        elif os.path.exists(path):
            os.remove(path)
        ip.write_csv(s_[cols], NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        ip.update_sources([dict(source=SOURCE, publisher="NOAA National Centers for Environmental Information (NCEI)",
                                report="Integrated Surface Database (global-hourly)", report_url=PAGE, document_list=API,
                                license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok",
                            detail=f"{len(s_)} values; {pulled} rows returned; {len(skipped)} ranges left out for the ceiling"))
        print(f"noaa_isd: {len(s_):,} values, {pulled:,} rows returned, {len(skipped)} ranges left out")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"noaa_isd FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("noaa_isd", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
