#!/usr/bin/env python3
"""Hourly temperature and dew point at 35 NOAA airport stations, 2019 to now, and each grid's weighted weather
(session 126, approved pull: NOAA's public station data, USD 0, ceiling 3,000,000 rows).

Energy Research Warehouse (ERW) connector. Method: docs/methods/demand_weather.md. Three series tables:

    noaa_grid_weather_stations   one row per station and figure: its weight in its grid, and its hours measured,
                                 interpolated and missing. The list of stations, with what each one lacks.
    noaa_grid_weather_hourly     per grid and UTC hour: temperature_f, dew_point_f, heating_degrees_f and
                                 cooling_degrees_f, each the weighted mean over the grid's five stations
    noaa_grid_weather_daily      per grid and local day: the day's mean, highest and lowest weighted temperature, mean
                                 dew point, heating_degree_days and cooling_degree_days

    python warehouse/connectors/noaa_grid_weather.py --fetch-only   # the pull, to warehouse/raw (no data lock)
    python warehouse/connectors/noaa_grid_weather.py                # the tables, from the raw files, under the lock
    python warehouse/connectors/noaa_grid_weather.py --out-dir DIR  # a trial: the tables under DIR, no lock

TWO NOAA PRODUCTS, AND WHY. NOAA's Integrated Surface Database stopped on 27 August 2025 (its station list gives that
day as every station's last, and it has no file for 2026). So:
  to 2025-07-31   ISD-Lite, NOAA NCEI's hourly cut of that database: one file per station and year, one row per hour,
                  air temperature and dew point in tenths of a degree Celsius, -9999 for missing
                  (https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/). ISD-Lite's own rule gives an hour the
                  observation taken from ten minutes before the hour up to the hour, the closest to the hour.
  from 2025-08-01 Local Climatological Data, version 2, through NCEI's Access Data Service (dataset
                  local-climatological-data-v2, dataTypes HourlyDryBulbTemperature and HourlyDewPointTemperature):
                  every report of the station, in degrees Celsius, dated in local standard time. This connector
                  moves the times to UTC and applies ISD-Lite's rule to them, so an hour means the same thing on
                  both sides of the seam.
The two are pulled together over 1 July 2025 to the end of ISD-Lite, and compared hour by hour at every station
before anything is written: the share of hours that agree to a tenth of a degree is in the log, the header and the
method. A station whose hours do not agree stops the run. The eight synoptic hours of the day (00, 03, ... 21 UTC) are
judged apart: there ISD-Lite takes the synoptic report filed on the hour where a station files one, and the Local
Climatological Data does not carry that report for every station (Austin's differ in two hours of three there, by
0.1 C on average over all hours), so the check that stops a run is on the other sixteen.

THE STATIONS AND THEIR WEIGHTS (the rule). For each grid, the five most populous metropolitan areas whose principal
city the grid operator serves; for each, the principal airport's station; the weight is the area's share of the five
areas' population, to the nearest twentieth (largest remainders first, so the five add to one).
  THE POPULATIONS WERE NOT RETRIEVED. The warehouse holds no population table and the session's one approved pull was
  NOAA's. The shares are stated here as a parameter of the method, as session 60 stated California's three, from the
  2020 Census counts of metropolitan areas as generally known, and rounded to twentieths so that a count wrong by a few
  percent gives the same weight. No population figure is written to any table. A person should check the twentieths
  against Census's table of metropolitan areas before the page built on them opens; demand_weather.py reports what
  changes with five equal weights in their place.
Left out by the rule and worth knowing: the New York area's New Jersey half (PJM's, but the area's principal city is
NYISO's); Sacramento (its city utility is its own balancing area); MISO's southern states (New Orleans is sixth).

ONE STATION'S EXCEPTION. Minneapolis-St. Paul's ISD-Lite files hold, from April 2020 to November 2022, little more than
the synoptic hours of the warm months (one hour in six on 14 July 2020; 8,276 hours missing in all), while the Local
Climatological Data holds that station's hourly report for every one of those hours. That stretch is read from the
second product for that station (PATCH), under the same rule for an hour; the two are compared over the hours both
hold, and the share that agree is in the table's header.

MISSING HOURS. A station's hour with no temperature is counted. A run of one, two or three missing hours between two
measured hours is interpolated on a straight line and counted as interpolated; a longer run stays missing. Nothing
else is filled. A grid's hour is written only when all five of its stations hold a temperature, measured or
interpolated across at most three hours; x_interpolated says how many of the five were interpolated. A grid's day is
written only when every hour of the local day is.

Degrees. heating_degrees_f is the weighted mean over the stations of max(65 - T, 0), cooling_degrees_f of
max(T - 65, 0), T in degrees Fahrenheit: taken at each station and then weighted, so a grid whose cities sit either
side of 65 has both. A day's degree days are the sum of its hours' degrees over 24.

Ceiling: 3,000,000 rows, counted as the data rows of every file and response read from NOAA, the session's trial reads
included (EXPLORED). Before each request the rows still allowed are checked against an estimate, and the pull stops
rather than pass the ceiling.
"""

import argparse
import datetime as dt
import gzip
import io
import json
import os
import sys
import time
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "noaa_grid_weather"
STATIONS_T, HOURLY, DAILY = "noaa_grid_weather_stations", "noaa_grid_weather_hourly", "noaa_grid_weather_daily"
LITE = "https://www.ncei.noaa.gov/pub/data/noaa/isd-lite"
HISTORY = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
API = "https://www.ncei.noaa.gov/access/services/data/v1"
SRC_LITE, SRC_LCD = "noaa:isd_lite", "noaa:lcd_v2"
PAGE_LITE = "https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database"
PAGE_LCD = "https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/demand_weather.md"
UA = {"User-Agent": "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)"}
CEILING = 3_000_000
# rows read from NOAA by session 126 before this connector existed, to choose the product (runs/session126/noaa_docs):
# ISD-Lite DFW 2025 (5,715), GHCN-hourly DFW 2025 (12,675) and part of 2026 (1,611), LCD v2 DFW 2026 (9,491), and a
# two-day trial of the data service (66). They count toward the ceiling.
EXPLORED = 5_715 + 12_675 + 1_611 + 9_491 + 66
# and rows of answers that were read and not used: the data service's first answer for Ontario, California stopped at
# 1 January 2026 (4,896 rows; asked again, it held the year), and three two-day trials made to find that out (199).
EXPLORED += 4_896 + 199
EXPLORED += 298   # two days of Minneapolis in July 2020, read to see why ISD-Lite is short there
# A station whose ISD-Lite file holds a small part of a stretch's hours has that stretch read from the Local
# Climatological Data instead: the same station's reports, under the same rule for an hour. Minneapolis-St. Paul:
# from April 2020 to November 2022 ISD-Lite keeps, in the warm months, little more than the synoptic hours (one hour in
# six on 14 July 2020), while the other product holds the hourly report of every one of those hours.
PATCH = {"MSP": ("2020-04-01", "2022-11-30")}
PATCH_PER_DAY = 170                                # rows a day the service returns for such a stretch (Minneapolis 2020: 149)
SHORT_DAYS = 21                                    # an answer whose newest report is this far before the day asked for is cut off
FIRST_YEAR = 2019
START = pd.Timestamp("2019-01-01T00:00:00Z")
SEAM = pd.Timestamp("2025-08-01T00:00:00Z")       # ISD-Lite before this hour, Local Climatological Data from it
LCD_FROM = "2025-07-01"                            # so the two overlap for the comparison
BASE_F = 65.0
MAX_GAP = 3                                        # a run of missing hours longer than this is never interpolated
AGREE = 0.90                                       # a station whose two products agree in fewer hours stops the run
PAUSE = 0.4
# grid: (EIA balancing authority code, name, time zone of its local day, geo)
GRIDS = {
    "erco": ("ERCOT", "America/Chicago", "US-TX"), "ciso": ("CAISO", "America/Los_Angeles", "US-CA"),
    "nyis": ("NYISO", "America/New_York", "US-NY"), "isne": ("ISO-NE", "America/New_York", "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"),
    "pjm": ("PJM", "America/New_York", "US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV"),
    "miso": ("MISO", "America/Chicago", "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI"),
    "swpp": ("SPP", "America/Chicago", "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY"),
}
# (grid, airport, USAF, WBAN, weight, hours local standard time is behind UTC, the metropolitan area it stands for).
# USAF and WBAN are NOAA's, read from its station list (isd-history.csv) on 2026-10-05; the list is read again each run
# for the name and position, and a station it does not hold stops the run.
STATIONS = [
    ("erco", "DFW", "722590", "03927", 0.35, 6, "Dallas-Fort Worth-Arlington"),
    ("erco", "IAH", "722430", "12960", 0.35, 6, "Houston-The Woodlands-Sugar Land"),
    ("erco", "SAT", "722530", "12921", 0.15, 6, "San Antonio-New Braunfels"),
    ("erco", "AUS", "722540", "13904", 0.10, 6, "Austin-Round Rock-Georgetown"),
    ("erco", "MFE", "722506", "12959", 0.05, 6, "McAllen-Edinburg-Mission"),
    ("ciso", "LAX", "722950", "23174", 0.50, 8, "Los Angeles-Long Beach-Anaheim"),
    ("ciso", "SFO", "724940", "23234", 0.15, 8, "San Francisco-Oakland-Berkeley"),
    ("ciso", "ONT", "747040", "03102", 0.15, 8, "Riverside-San Bernardino-Ontario"),
    ("ciso", "SAN", "722900", "23188", 0.10, 8, "San Diego-Chula Vista-Carlsbad"),
    ("ciso", "SJC", "724945", "23293", 0.10, 8, "San Jose-Sunnyvale-Santa Clara"),
    ("nyis", "LGA", "725030", "14732", 0.80, 5, "New York-Newark-Jersey City (the part in New York State)"),
    ("nyis", "BUF", "725280", "14733", 0.05, 5, "Buffalo-Cheektowaga"),
    ("nyis", "ROC", "725290", "14768", 0.05, 5, "Rochester"),
    ("nyis", "ALB", "725180", "14735", 0.05, 5, "Albany-Schenectady-Troy"),
    ("nyis", "SYR", "725190", "14771", 0.05, 5, "Syracuse"),
    ("isne", "BOS", "725090", "14739", 0.50, 5, "Boston-Cambridge-Newton"),
    ("isne", "PVD", "725070", "14765", 0.15, 5, "Providence-Warwick"),
    ("isne", "BDL", "725080", "14740", 0.15, 5, "Hartford-East Hartford-Middletown"),
    ("isne", "ORH", "725100", "94746", 0.10, 5, "Worcester"),
    ("isne", "BDR", "725040", "94702", 0.10, 5, "Bridgeport-Stamford-Norwalk"),
    ("pjm", "ORD", "725300", "94846", 0.35, 6, "Chicago-Naperville-Elgin"),
    ("pjm", "DCA", "724050", "13743", 0.25, 5, "Washington-Arlington-Alexandria"),
    ("pjm", "PHL", "724080", "13739", 0.20, 5, "Philadelphia-Camden-Wilmington"),
    ("pjm", "BWI", "724060", "93721", 0.10, 5, "Baltimore-Columbia-Towson"),
    ("pjm", "PIT", "725200", "94823", 0.10, 5, "Pittsburgh"),
    ("miso", "DTW", "725370", "94847", 0.30, 5, "Detroit-Warren-Dearborn"),
    ("miso", "MSP", "726580", "14922", 0.25, 6, "Minneapolis-St. Paul-Bloomington"),
    ("miso", "STL", "724340", "13994", 0.20, 6, "St. Louis"),
    ("miso", "IND", "724380", "93819", 0.15, 5, "Indianapolis-Carmel-Anderson"),
    ("miso", "MKE", "726400", "14839", 0.10, 6, "Milwaukee-Waukesha"),
    ("swpp", "MCI", "724460", "03947", 0.35, 6, "Kansas City"),
    ("swpp", "OKC", "723530", "13967", 0.25, 6, "Oklahoma City"),
    ("swpp", "TUL", "723560", "13968", 0.15, 6, "Tulsa"),
    ("swpp", "OMA", "725500", "14942", 0.15, 6, "Omaha-Council Bluffs"),
    ("swpp", "ICT", "724500", "03928", 0.10, 6, "Wichita"),
]


def ghcn_id(wban):
    return "USW000" + wban


def lite_url(usaf, wban, year):
    return f"{LITE}/{year}/{usaf}-{wban}-{year}.gz"


def lcd_url(wban, start, end):
    return (f"{API}?dataset=local-climatological-data-v2&stations={ghcn_id(wban)}&startDate={start}T00:00:00"
            f"&endDate={end}T23:59:59&dataTypes=HourlyDryBulbTemperature,HourlyDewPointTemperature&format=csv")


def parse_lite(blob):
    """One ISD-Lite file: a frame indexed by the UTC hour with temp_c and dew_c (NaN where NOAA wrote -9999), and the
    number of rows the file holds."""
    text = (gzip.decompress(blob) if blob[:2] == bytes([0x1F, 0x8B]) else blob).decode("ascii")
    rows = [ln.split() for ln in text.splitlines() if ln.strip()]
    if not rows:
        return pd.DataFrame(columns=["temp_c", "dew_c"]), 0
    a = np.array([r[:6] for r in rows], dtype=float)
    ts = pd.to_datetime(pd.DataFrame({"year": a[:, 0], "month": a[:, 1], "day": a[:, 2], "hour": a[:, 3]}), utc=True)
    out = pd.DataFrame({"temp_c": a[:, 4], "dew_c": a[:, 5]}, index=pd.DatetimeIndex(ts))
    out = out.where(out > -9999) / 10.0
    return out[~out.index.duplicated()], len(rows)


def number(s):
    """A value of the Local Climatological Data as a number: digits, a sign and a point, and nothing else. A value NOAA
    marks (a trailing letter or star) or leaves blank is not a number."""
    s = pd.Series(s, dtype=str).str.strip()
    return pd.to_numeric(s.where(s.str.fullmatch(r"-?\d+(\.\d+)?")), errors="coerce")


def parse_lcd(text, lst_hours):
    """One response of the data service: every report with its time moved from local standard time to UTC, then
    ISD-Lite's rule: an hour takes the report from ten minutes before the hour up to the hour, the closest to it, element
    by element. Returns the hourly frame (temp_c, dew_c), the rows returned, and the values that were not numbers."""
    d = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    n = len(d)
    if not n:
        return pd.DataFrame(columns=["temp_c", "dew_c"]), 0, 0
    d = d[d["REPORT_TYPE"].str.strip().str.startswith("FM")]
    t = pd.to_datetime(d["DATE"], utc=True) + pd.Timedelta(hours=lst_hours)
    marked = 0
    cols = {}
    for src, col in (("HourlyDryBulbTemperature", "temp_c"), ("HourlyDewPointTemperature", "dew_c")):
        v = number(d[src])
        marked += int(((d[src].str.strip() != "") & v.isna().to_numpy()).sum())
        x = pd.DataFrame({"t": t.to_numpy(), "v": v.to_numpy()}).dropna()
        x["t"] = pd.to_datetime(x["t"], utc=True)
        hour = x["t"].dt.ceil("h")
        x = x[(hour - x["t"]) <= pd.Timedelta(minutes=10)].assign(hour=hour)
        cols[col] = x.sort_values("t").groupby("hour")["v"].last()
    return pd.DataFrame(cols), n, marked


def fill_short(s, max_gap=MAX_GAP):
    """A station's hourly series with runs of at most max_gap missing hours, between two measured hours, interpolated
    on a straight line. Returns (the series, a boolean series: this hour is interpolated). A longer run, and a run at
    either end, stays missing."""
    miss = s.isna()
    run = (miss != miss.shift()).cumsum()
    length = miss.groupby(run).transform("sum")
    first, last = s.first_valid_index(), s.last_valid_index()
    inside = (s.index > first) & (s.index < last) if first is not None else np.zeros(len(s), bool)
    ok = miss & (length <= max_gap) & inside
    filled = s.interpolate(method="time", limit_area="inside")
    return s.where(~ok, filled), ok


def gaps(s):
    """(hours missing, runs of missing hours, the longest run) inside a station's first and last measured hour."""
    first, last = s.first_valid_index(), s.last_valid_index()
    if first is None:
        return 0, 0, 0
    m = s[first:last].isna()
    run = (m != m.shift()).cumsum()[m]
    sizes = run.value_counts()
    return int(m.sum()), int(len(sizes)), int(sizes.max()) if len(sizes) else 0


def grid_hours(st, weights):
    """A grid's hourly weather from its stations' hourly temperature and dew point (degrees F; frames by station with the
    same hourly index, the short runs already interpolated). An hour is held only when every station holds a
    temperature; its dew point only when every station holds one."""
    codes = list(weights)
    w = np.array([weights[c] for c in codes])
    if abs(w.sum() - 1) > 1e-9:
        raise ValueError(f"the weights of {codes} add to {w.sum()}, not 1")
    T = pd.concat([st[c]["temp_f"] for c in codes], axis=1).to_numpy()
    D = pd.concat([st[c]["dew_f"] for c in codes], axis=1).to_numpy()
    I = pd.concat([st[c]["interp"] for c in codes], axis=1).to_numpy()
    okT, okD = ~np.isnan(T).any(axis=1), ~np.isnan(D).any(axis=1)
    out = pd.DataFrame(index=st[codes[0]].index)
    out["temperature_f"] = np.where(okT, np.nansum(T * w, axis=1), np.nan)
    out["heating_degrees_f"] = np.where(okT, np.nansum(np.clip(BASE_F - T, 0, None) * w, axis=1), np.nan)
    out["cooling_degrees_f"] = np.where(okT, np.nansum(np.clip(T - BASE_F, 0, None) * w, axis=1), np.nan)
    out["dew_point_f"] = np.where(okT & okD, np.nansum(D * w, axis=1), np.nan)
    out["interpolated"] = np.where(okT, I.sum(axis=1), 0)
    return out


def grid_days(h, tz):
    """A grid's days from its hours: only local days whose every hour is held."""
    local = h.index.tz_convert(tz)
    day = pd.Series(local.strftime("%Y-%m-%d"), index=h.index)
    g = h.groupby(day)
    n = g["temperature_f"].size()
    held = g["temperature_f"].count()
    # the hours the local day has (23 or 25 on the days the clocks change)
    naive = pd.to_datetime(n.index)
    first, nxt = naive.tz_localize(tz), (naive + pd.Timedelta(days=1)).tz_localize(tz)   # the next local midnight, by the calendar
    want = (nxt.tz_convert("UTC") - first.tz_convert("UTC")) / pd.Timedelta(hours=1)
    whole = (held.to_numpy() == want.to_numpy()) & (n.to_numpy() == want.to_numpy())
    out = pd.DataFrame({
        "temperature_f": g["temperature_f"].mean(), "temperature_max_f": g["temperature_f"].max(),
        "temperature_min_f": g["temperature_f"].min(),
        "dew_point_f": g["dew_point_f"].mean().where(g["dew_point_f"].count() == n),
        "heating_degree_days": g["heating_degrees_f"].sum() / 24.0, "cooling_degree_days": g["cooling_degrees_f"].sum() / 24.0,
        "hours": n})
    return out[whole]


class Ledger:
    """The rows read from NOAA, against the ceiling."""

    def __init__(self, ceiling, log):
        self.rows, self.ceiling, self.log, self.requests, self.reused, self.bytes = EXPLORED, ceiling, log, 0, 0, 0

    def allow(self, estimate, what):
        if self.rows + estimate > self.ceiling:
            raise RuntimeError(f"{what}: {self.rows:,} rows read, about {estimate:,} more would pass the ceiling of {self.ceiling:,}; stopped")

    def add(self, n, rec, size):
        self.rows += n
        self.bytes += size
        if rec.get("cached"):
            self.reused += 1
        else:
            self.requests += 1
        if self.rows > self.ceiling:
            raise RuntimeError(f"{self.rows:,} rows read, over the ceiling of {self.ceiling:,}: stopped before writing")


def pull(log, offline=False, end=None, refresh=False):
    """Every station's hours, from the raw files where an earlier run saved them. Returns {airport: frame}, per-station
    facts, and the ledger."""
    led = Ledger(CEILING, log)
    today = pd.Timestamp.now(tz="UTC")
    end = end or today.strftime("%Y-%m-%d")
    blob, rec = ip.fetch_raw(NAME, HISTORY, log, offline=offline, headers=UA)
    hist = pd.read_csv(io.BytesIO(blob), dtype=str, keep_default_na=False)
    out, facts = {}, {}
    for ba, code, usaf, wban, weight, lst, metro in STATIONS:
        h = hist[(hist["USAF"] == usaf) & (hist["WBAN"] == wban)]
        if len(h) != 1:
            raise RuntimeError(f"{code}: NOAA's station list holds {len(h)} rows for {usaf}-{wban}")
        h = h.iloc[0]
        lite, n_lite, urls = [], 0, []
        for y in range(FIRST_YEAR, SEAM.year + 1):
            url = lite_url(usaf, wban, y)
            led.allow(8_784, f"{code} {y}")
            b, r = ip.fetch_raw(NAME, url, log, offline=offline, pause=0, headers=UA)
            if not r.get("cached"):
                time.sleep(PAUSE)
            f, n = parse_lite(b)
            led.add(n, r, len(b))
            n_lite += n
            lite.append(f)
            urls.append((url, r["retrieved_at"]))
        lite = pd.concat(lite).sort_index()
        url = lcd_url(wban, LCD_FROM, end)
        days = (pd.Timestamp(end) - pd.Timestamp(LCD_FROM)).days + 1
        led.allow(days * 45, f"{code} Local Climatological Data")
        hit = None if refresh and not offline else lcd_cached(wban)
        if hit is None and offline:
            raise RuntimeError(f"offline: no whole Local Climatological Data response for {code} in warehouse/raw/{NAME}/")
        if hit is None:
            # the service now and then answers 200 with nothing, or with a file that stops months early: such an answer is
            # counted, never used, and asked for again
            for attempt in (1, 2, 3, 4):
                b, r = ip.fetch_raw(NAME, url, log, fresh=True, pause=PAUSE, timeout=600, headers=UA)
                if whole_answer(b, url):
                    break
                short = max(b.count(b"\n") - 1, 0)
                led.rows += short
                log(f"  {code}: the data service's answer is empty or cut off ({short:,} rows, counted and not used); attempt {attempt} of 4")
                if attempt == 4:
                    raise RuntimeError(f"{code}: the data service gave no whole answer in 4 attempts")
                time.sleep(20 * attempt)
        else:
            b, r = hit
            url = r["url"]
            log(f"  raw file reused: {url}")
        text = b.decode("utf-8")
        lcd, n_lcd, marked = parse_lcd(text, lst)
        led.add(n_lcd, r, len(b))
        # the seam's check: the hours both products hold, 1 July 2025 to ISD-Lite's last hour
        both = lite.join(lcd, how="inner", lsuffix="_lite", rsuffix="_lcd").dropna(subset=["temp_c_lite", "temp_c_lcd"])
        both = both[both.index >= pd.Timestamp(LCD_FROM, tz="UTC")]
        diff = both["temp_c_lite"] - both["temp_c_lcd"]
        syn = both.index.hour % 3 == 0     # the synoptic hours: ISD-Lite takes the on-the-hour synoptic report where a station files one
        agree = float(diff[~syn].abs().le(0.051).mean()) if (~syn).sum() else float("nan")
        agree_syn = float(diff[syn].abs().le(0.051).mean()) if syn.sum() else float("nan")
        mad = float(diff.abs().mean()) if len(both) else float("nan")
        bias = float(diff.mean()) if len(both) else float("nan")
        if not len(both) or not agree >= AGREE:
            raise RuntimeError(f"{code}: ISD-Lite and the Local Climatological Data agree in {agree:.1%} of {int((~syn).sum()):,} shared hours "
                               f"outside the synoptic hours (local standard time taken as UTC minus {lst}); under {AGREE:.0%}, nothing is written")
        x = pd.concat([lite[lite.index < SEAM], lcd[lcd.index >= SEAM]]).sort_index()
        patch_note = ""
        if code in PATCH:
            a, z = PATCH[code]
            parts, n_patch = [], 0
            for y in range(int(a[:4]), int(z[:4]) + 1):
                s0, s1 = max(a, f"{y}-01-01"), min(z, f"{y}-12-31")
                u = lcd_url(wban, s0, s1)
                led.allow(((pd.Timestamp(s1) - pd.Timestamp(s0)).days + 1) * PATCH_PER_DAY, f"{code} {y}, the stretch ISD-Lite is short of")
                for attempt in (1, 2, 3, 4):
                    pb, pr = ip.fetch_raw(NAME, u, log, offline=offline, pause=PAUSE, timeout=900, headers=UA)
                    if whole_answer(pb, u):
                        break
                    if pr.get("cached") or attempt == 4:
                        raise RuntimeError(f"{code} {y}: no whole answer of the data service for {s0} to {s1}")
                    led.rows += max(pb.count(b"\n") - 1, 0)
                    time.sleep(20 * attempt)
                f, n, _ = parse_lcd(pb.decode("utf-8"), lst)
                led.add(n, pr, len(pb))
                n_patch += n
                parts.append(f)
            pf = pd.concat(parts).sort_index()
            pf = pf[~pf.index.duplicated()]
            lo, hi = pd.Timestamp(a, tz="UTC"), pd.Timestamp(z, tz="UTC") + pd.Timedelta(days=1)
            inside = (lite.index >= lo) & (lite.index < hi)
            sh = lite[inside].join(pf, how="inner", lsuffix="_lite", rsuffix="_lcd").dropna(subset=["temp_c_lite", "temp_c_lcd"])
            pa = float((sh["temp_c_lite"] - sh["temp_c_lcd"]).abs().le(0.051).mean()) if len(sh) else float("nan")
            had = int(lite.loc[inside, "temp_c"].notna().sum())
            x = pd.concat([x[(x.index < lo) | (x.index >= hi)], pf[(pf.index >= lo) & (pf.index < hi)]]).sort_index()
            now = int(x.loc[(x.index >= lo) & (x.index < hi), "temp_c"].notna().sum())
            patch_note = (f"{a} to {z} read from the Local Climatological Data ({n_patch:,} rows): {now:,} hours held there against "
                          f"{had:,} in ISD-Lite; over the {len(sh):,} hours both hold they agree to a tenth of a degree C in {pa:.2%}")
            log(f"  {code}: {patch_note}")
            n_lcd += n_patch
        x = x[x.index >= START]
        out[code] = x
        facts[code] = dict(ba=ba, usaf=usaf, wban=wban, weight=weight, metro=metro, name=h["STATION NAME"].strip(), state=h["STATE"],
                           lat=float(h["LAT"]), lon=float(h["LON"]), lite_rows=n_lite, lcd_rows=n_lcd, lcd_marked=marked,
                           shared_hours=int(len(both)), agree=agree, agree_synoptic=agree_syn, mean_abs_diff_c=mad, mean_diff_c=bias, lite_end=ip.utc_iso(lite.index.max()),
                           lcd_end=ip.utc_iso(lcd.index.max()), lcd_url=url, lcd_retrieved=str(r["retrieved_at"]), patch=patch_note,
                           lite_retrieved=str(max(u[1] for u in urls)))
        log(f"  {code} ({h['STATION NAME'].strip()}, {usaf}-{wban}): ISD-Lite {n_lite:,} rows to {facts[code]['lite_end']}; Local "
            f"Climatological Data {n_lcd:,} rows to {facts[code]['lcd_end']} ({marked} marked values not read); over {len(both):,} shared hours the "
            f"two agree to a tenth of a degree C in {agree:.2%} of the hours outside the synoptic ones and {agree_syn:.2%} of the synoptic ones "
            f"(ISD-Lite minus the other: mean {bias:+.3f} C, mean absolute {mad:.3f} C); {led.rows:,} rows in all")
    return out, facts, led


def whole_answer(content, url):
    """Is this answer of the data service whole? It begins with the header and its newest report is within SHORT_DAYS
    of the last day the address asked for (the service runs about a week behind)."""
    import re
    if not content.startswith(b'"STATION"'):
        return False
    m = re.search(r"endDate=(\d{4}-\d{2}-\d{2})", url)
    lines = content.rstrip().rsplit(b"\n", 1)
    last = re.search(rb'"(\d{4}-\d{2}-\d{2})T', lines[-1]) if len(lines) == 2 else None
    if not m or not last:
        return False
    return pd.Timestamp(last.group(1).decode()) >= pd.Timestamp(m.group(1)) - pd.Timedelta(days=SHORT_DAYS)


def lcd_cached(wban):
    """The newest saved response of the data service for a station, whatever its end date: a later run on the same day
    reads the file it already has. Returns (bytes, record) or None."""
    import csv
    import glob
    import hashlib
    want = f"stations={ghcn_id(wban)}&startDate={LCD_FROM}T"
    for manifest in sorted(glob.glob(os.path.join(ip.RAW_DIR, NAME, "*", "manifest.csv")), reverse=True):
        with open(manifest, encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if want in r["url"] and r["status"] == "200"]
        for r in reversed(rows):
            path = os.path.join(os.path.dirname(manifest), r["file"])
            if os.path.exists(path):
                with open(path, "rb") as f:
                    content = f.read()
                if hashlib.sha256(content).hexdigest() == r["sha256"] and whole_answer(content, r["url"]):
                    return content, {"url": r["url"], "retrieved_at": r["retrieved_at"], "last_modified": r["last_modified"],
                                     "file": path, "cached": True}
    return None


def build(raw, facts, weights=None):
    """The stations' filled hours, each grid's hours and days, and each station's counts. weights: {airport: weight}
    in place of the stated ones (demand_weather.py's trial with equal weights)."""
    end = min(f.index[f["temp_c"].notna()].max() for f in raw.values())   # the last hour every station reaches
    idx = pd.date_range(START, end, freq="h")
    st, counts = {}, {}
    for code, x in raw.items():
        x = x.reindex(idx)
        t, it = fill_short(x["temp_c"])
        d, _ = fill_short(x["dew_c"])
        missing, runs, longest = gaps(x["temp_c"])
        st[code] = pd.DataFrame({"temp_f": t * 9 / 5 + 32, "dew_f": d * 9 / 5 + 32, "interp": it.astype(int)}, index=idx)
        counts[code] = dict(hours=len(idx), measured=int(x["temp_c"].notna().sum()), interpolated=int(it.sum()),
                            missing=int(t.isna().sum()), gap_hours=missing, gap_runs=runs, longest_gap=longest,
                            dew_missing=int(d.isna().sum()))
    hours, days = {}, {}
    for ba, (name, tz, geo) in GRIDS.items():
        w = {c: (weights[c] if weights else f["weight"]) for c, f in facts.items() if f["ba"] == ba}
        hours[ba] = grid_hours(st, w)
        days[ba] = grid_days(hours[ba], tz)
    return st, hours, days, counts, idx


def series(ent, var, ts, val, unit, freq, geo, node, source, url, retrieved, ba, **x):
    d = pd.DataFrame({"entity": ent, "variable": var, "ts_utc": ts, "value": val, "unit": unit, "freq": freq, "geo": geo,
                      "market": "", "node": node, "source": source, "source_url": url, "retrieved_at": retrieved, "vintage": "", "ba": ba})
    for k, v in x.items():
        d[k] = v
    return d


def tables(facts, hours, days, counts, idx):
    """The three tables' rows."""
    retrieved = max(max(f["lite_retrieved"], f["lcd_retrieved"]) for f in facts.values())
    retrieved = ip.utc_iso(pd.Timestamp(retrieved))
    start = ip.utc_iso(idx[0])
    s_rows = []
    for code, f in facts.items():
        c = counts[code]
        for var, val, unit in (("weight", f["weight"], "ratio"), ("hours_measured", c["measured"], "count"),
                               ("hours_interpolated", c["interpolated"], "count"), ("hours_missing", c["missing"], "count"),
                               ("longest_gap_hours", c["longest_gap"], "count"), ("dew_point_hours_missing", c["dew_missing"], "count")):
            s_rows.append(dict(entity=f"noaa:{ghcn_id(f['wban'])}", variable=var, ts_utc=start, value=val, unit=unit, freq="",
                               geo=f"US-{f['state']}", market="", node=GRIDS[f["ba"]][0], source=SRC_LITE,
                               source_url=f"{LITE}/", retrieved_at=retrieved, vintage="", ba=f["ba"], x_airport=code,
                               x_station=f"{f['usaf']}-{f['wban']}", x_name=f["name"], x_lat=f["lat"], x_lon=f["lon"],
                               x_metro=f["metro"], x_hours=c["hours"], x_through=ip.utc_iso(idx[-1])))
    stations = pd.DataFrame(s_rows)
    h_frames, d_frames = [], []
    for ba, (name, tz, geo) in GRIDS.items():
        h = hours[ba].dropna(subset=["temperature_f"])
        ts = h.index.strftime("%Y-%m-%dT%H:%M:%SZ")
        src = np.where(h.index < SEAM, SRC_LITE, SRC_LCD)
        url = np.where(h.index < SEAM, LITE + "/" + h.index.strftime("%Y") + "/", API + "?dataset=local-climatological-data-v2")
        for var in ("temperature_f", "dew_point_f", "heating_degrees_f", "cooling_degrees_f"):
            keep = h[var].notna().to_numpy()
            h_frames.append(series(f"iso:{name.lower().replace('-', '')}", var, ts[keep], h[var].round(2).to_numpy()[keep], "degF", "PT1H",
                                   geo, name, src[keep], url[keep], retrieved, ba, x_interpolated=h["interpolated"].astype(int).to_numpy()[keep]))
        d = days[ba]
        dts = pd.Index(d.index) + "T00:00:00Z"
        last = pd.to_datetime(d.index).tz_localize(tz).tz_convert("UTC") + pd.Timedelta(hours=23)
        dsrc = np.where(last < SEAM, SRC_LITE, SRC_LCD)
        durl = np.where(last < SEAM, LITE + "/" + pd.Index(d.index).str[:4] + "/", API + "?dataset=local-climatological-data-v2")
        for var, unit in (("temperature_f", "degF"), ("temperature_max_f", "degF"), ("temperature_min_f", "degF"), ("dew_point_f", "degF"),
                          ("heating_degree_days", "degF-day"), ("cooling_degree_days", "degF-day")):
            keep = d[var].notna().to_numpy()
            d_frames.append(series(f"iso:{name.lower().replace('-', '')}", var, dts[keep], d[var].round(3).to_numpy()[keep], unit, "P1D",
                                   geo, name, dsrc[keep], durl[keep], retrieved, ba, x_hours=d["hours"].astype(int).to_numpy()[keep]))
    return stations, pd.concat(h_frames, ignore_index=True), pd.concat(d_frames, ignore_index=True)


def station_lines(facts, counts):
    out = []
    for code, f in facts.items():
        c = counts[code]
        out.append(f"  {GRIDS[f['ba']][0]} {code} {f['usaf']}-{f['wban']} {f['name']} ({f['metro']}), weight {f['weight']:.2f}: "
                   f"{c['measured']:,} of {c['hours']:,} hours measured, {c['interpolated']:,} interpolated across at most {MAX_GAP} hours, "
                   f"{c['missing']:,} missing (longest run {c['longest_gap']} hours); over {f['shared_hours']:,} shared hours the two products agree in "
                   f"{f['agree']:.2%} of the hours outside the synoptic ones and {f['agree_synoptic']:.2%} of the synoptic ones (mean difference {f['mean_diff_c']:+.3f} C)"
                   + (f". {f['patch']}" if f.get("patch") else ""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA hourly station temperature and each grid's weighted weather")
    ap.add_argument("--fetch-only", action="store_true", help="the pull, to warehouse/raw; no table is written (no data lock)")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; no request is made")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--refresh", action="store_true", help="ask the data service again for the months since July 2025 (a later day's run)")
    ap.add_argument("--end", help="the last day asked of the data service, YYYY-MM-DD (default today, UTC)")
    args = ap.parse_args(argv)
    if ip.paused("noaa"):
        print("noaa is a paused publisher (warehouse/metadata/paused_sources.csv): no request is made", file=sys.stderr)
        return 1
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir   # a trial reads the raw files the pull saved; it asks NOAA for nothing new unless told
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    if not args.offline:
        ip.RAW.open(NAME, run_id)
    results = []
    try:
        log(f"ERW {NAME} run {run_id}: {len(STATIONS)} stations, ISD-Lite {FIRST_YEAR} to {SEAM.year} and Local Climatological Data from "
            f"{LCD_FROM}; ceiling {CEILING:,} rows ({EXPLORED:,} read by the session's trials are counted)")
        raw, facts, led = pull(log, offline=args.offline, end=args.end, refresh=args.refresh)
        st, hours, days, counts, idx = build(raw, facts)
        log(f"  rows read from NOAA: {led.rows:,} of the {CEILING:,} ceiling ({led.requests} requests sent by this run, {led.reused} files "
            f"reused, {led.bytes / 1e6:.1f} MB)")
        for ln in station_lines(facts, counts):
            log(ln)
        held = {}
        for ba, (name, tz, geo) in GRIDS.items():
            h = hours[ba]
            held[ba] = (int(h["temperature_f"].notna().sum()), len(h), int((h["interpolated"] > 0).sum()), len(days[ba]))
            log(f"  {name}: {held[ba][0]:,} of {held[ba][1]:,} hours held ({held[ba][0] / held[ba][1]:.2%}), {held[ba][2]:,} of them with a "
                f"station interpolated; {held[ba][3]:,} whole local days")
        summary = dict(run_id=run_id, rows_read=led.rows, ceiling=CEILING, requests=led.requests, reused=led.reused, through=ip.utc_iso(idx[-1]),
                       stations={c: {**f, **counts[c]} for c, f in facts.items()}, grids={b: dict(zip(("hours_held", "hours", "hours_with_interpolation", "days"), v)) for b, v in held.items()})
        os.makedirs(os.path.join(ip.RAW_DIR, NAME), exist_ok=True)
        with open(os.path.join(ip.RAW_DIR, NAME, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)
        print(f"{NAME}: {led.rows:,} rows read of {CEILING:,} ({led.requests} requests, {led.reused} reused); stations through {summary['through']}")
        if args.fetch_only:
            results.append(dict(table=HOURLY, market="all", status="ok", detail=f"fetch only: {led.rows} rows read"))
        else:
            stations, hourly, daily = tables(facts, hours, days, counts, idx)
            worst = min(facts.values(), key=lambda f: f["agree"])
            common = [
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_grid_weather.py",
                f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
                f"Raw files: warehouse/raw/{NAME}/ (not in git; each run's manifest.csv lists each file and URL)",
                f"Source: {SRC_LITE} NOAA National Centers for Environmental Information, Integrated Surface Database, ISD-Lite, {PAGE_LITE}",
                f"  files: {LITE}/<year>/<USAF>-<WBAN>-<year>.gz, {FIRST_YEAR} to {SEAM.year}; used for hours before {ip.utc_iso(SEAM)}. NOAA's database ends on 27 August 2025.",
                f"Source: {SRC_LCD} NOAA National Centers for Environmental Information, Local Climatological Data version 2, {PAGE_LCD}",
                f"  access: {API}?dataset=local-climatological-data-v2 (stations USW000<WBAN>, dataTypes HourlyDryBulbTemperature,HourlyDewPointTemperature), from {LCD_FROM}; used for hours from {ip.utc_iso(SEAM)}. Its times are local standard time, moved to UTC; an hour takes the report from ten minutes before the hour up to the hour, the closest to it (ISD-Lite's rule).",
                f"The seam, checked: over the hours both products hold from {LCD_FROM} to ISD-Lite's end, every station agrees to a tenth of a degree C in at least {worst['agree']:.2%} of the hours outside the eight synoptic hours of the day (the least: {[c for c, f in facts.items() if f is worst][0]}). At the synoptic hours (00, 03, ... 21 UTC) ISD-Lite takes the on-the-hour synoptic report where a station files one, and the Local Climatological Data does not carry it for every station: there the agreement runs from {min(f['agree_synoptic'] for f in facts.values()):.2%} to {max(f['agree_synoptic'] for f in facts.values()):.2%} by station, and the mean difference over all shared hours from {min(f['mean_diff_c'] for f in facts.values()):+.3f} to {max(f['mean_diff_c'] for f in facts.values()):+.3f} C (the Stations lines give each).",
                f"Rows read from NOAA: {led.rows:,} of the {CEILING:,} ceiling, the session's trial reads included.",
                "Weights: each metropolitan area's share of its grid's five, to the nearest twentieth. The populations behind the shares were not retrieved (no population table is held and the one approved pull was NOAA's): they are a stated parameter of the method, to be checked against Census's table before the page opens. Method: docs/methods/demand_weather.md",
                f"Missing hours are counted and never interpolated across more than {MAX_GAP} hours. A grid's hour is written only when all five stations hold a temperature (measured, or interpolated across at most {MAX_GAP} hours: x_interpolated counts them).",
                "License: public. U.S. stations only. NOAA NCEI's record for the database gives a citation and two statements of liability and names no license; its readme restricts only non-U.S. data (WMO Resolution 40). Cite as: NOAA National Centers for Environmental Information (2001): Global Surface Hourly [ISD-Lite]. NOAA National Centers for Environmental Information; and Kantor, Diana; Casey, Nancy W.; Menne, Matthew J.; Buddenberg, Andrew. 2023. Local Climatological Data (LCD), Version 2. NOAA National Centers for Environmental Information. https://doi.org/10.25921/96dw-mb77. NOAA's terms are quoted in docs/methods/demand_weather.md.",
            ]
            cols_s = ip.SERIES_COLS + ["ba", "x_airport", "x_station", "x_name", "x_lat", "x_lon", "x_metro", "x_hours", "x_through"]
            ip.write_csv(stations[cols_s], STATIONS_T, [
                "Energy Research Warehouse (ERW): the 35 NOAA stations behind each grid's weighted weather, five a grid, with each one's weight and its hours measured, interpolated and missing (session 126)",
                "Shape: series (docs/datastandard.md v0), partition column ba. entity noaa:<GHCN identifier>; variables weight (ratio: the station's share of its grid), hours_measured, hours_interpolated, hours_missing, longest_gap_hours, dew_point_hours_missing (count), over x_hours hours from ts_utc to x_through. x_name, x_lat and x_lon are NOAA's (isd-history.csv); x_metro is the metropolitan area the station stands for.",
            ] + common + ["Stations:"] + station_lines(facts, counts), log, cols=cols_s)
            cols_h = ip.SERIES_COLS + ["ba", "x_interpolated"]
            for f in (HOURLY, DAILY):
                p = os.path.join(ip.OUT_DIR, f + ".csv")
                if os.path.exists(p):
                    os.remove(p)   # rebuilt whole from the raw files: an hour a station no longer holds must leave the table
            ip.write_csv(hourly[cols_h], HOURLY, [
                "Energy Research Warehouse (ERW): each grid's weighted hourly temperature, dew point, heating and cooling degrees, from five NOAA airport stations a grid, 2019 to now (session 126)",
                "Shape: series (docs/datastandard.md v0), partition column ba (the grid's EIA-930 code, to join eia930 tables). entity iso:<grid>; freq PT1H, ts_utc the hour (the reading taken in the ten minutes up to it). temperature_f and dew_point_f: the weighted mean of the stations' readings, degrees F (NOAA's tenths of a degree C times 9/5 plus 32). heating_degrees_f: the weighted mean of max(65 - T, 0) over the stations; cooling_degrees_f: of max(T - 65, 0). x_interpolated: how many of the five stations' temperatures in the hour are interpolated.",
            ] + common, log, cols=cols_h)
            cols_d = ip.SERIES_COLS + ["ba", "x_hours"]
            ip.write_csv(daily[cols_d], DAILY, [
                "Energy Research Warehouse (ERW): each grid's weighted daily temperature, dew point, heating and cooling degree days, from five NOAA airport stations a grid, 2019 to now (session 126)",
                "Shape: series (docs/datastandard.md v0), partition column ba. entity iso:<grid>; freq P1D, ts_utc the grid's local day (" + "; ".join(f"{v[0]} {v[1]}" for v in GRIDS.values()) + "). temperature_f the mean of the day's hours, temperature_max_f and temperature_min_f its highest and lowest hour, dew_point_f the mean (degF); heating_degree_days and cooling_degree_days the sum of the hours' heating and cooling degrees over 24 (degF-day, base 65 F). A day is written only when every one of its x_hours hours is held.",
            ] + common, log, cols=cols_d)
            if not args.out_dir:
                pub = "NOAA National Centers for Environmental Information (NCEI)"
                ip.update_sources([
                    dict(source=SRC_LITE, publisher=pub, report="Integrated Surface Database, ISD-Lite (hourly)", report_url=PAGE_LITE,
                         document_list=LITE + "/", license="public", tables=[STATIONS_T, HOURLY, DAILY]),
                    dict(source=SRC_LCD, publisher=pub, report="Local Climatological Data, version 2 (hourly)", report_url=PAGE_LCD,
                         document_list=API + "?dataset=local-climatological-data-v2", license="public", tables=[HOURLY, DAILY])])
            for t, n in ((STATIONS_T, len(stations)), (HOURLY, len(hourly)), (DAILY, len(daily))):
                results.append(dict(table=t, market="all", status="ok", detail=f"{n} rows; {led.rows} rows read from NOAA"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=HOURLY, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
