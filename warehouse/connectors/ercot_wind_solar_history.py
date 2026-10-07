#!/usr/bin/env python3
"""ERCOT wind and solar by the hour: output, the High Sustained Limit where ERCOT prints it, and the yearly record
(session 144, the owner's approved pull (c): USD 0, ceiling 2,000,000 rows).

Energy Research Warehouse (ERW) connector. WHAT ERCOT PUBLISHES OPENLY (no account, no key), as read on 7 October 2026:

  1. The hourly reports by geographical region, each posted once an hour, each holding the 48 hours behind it
     (and a week of forecast ahead, which this connector does not read). ERCOT's public list keeps 7 DAYS of postings
     (the product page says so: display duration 7), so the open history of these reports is about nine days:
       NP4-742-CD  Wind Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region
                   (report type 14787). Regions as ERCOT prints them: PANHANDLE, COASTAL, SOUTH, WEST, NORTH.
       NP4-745-CD  Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region
                   (report type 21809). Regions: CenterWest, NorthWest, FarWest, FarEast, SouthEast, CenterEast.
     Columns read: SYSTEM_WIDE_GEN (actual output, hourly average, MW), SYSTEM_WIDE_HSL (the High Sustained Limit,
     the output the resources report they could sustain, hourly average, MW) and GEN_<region> (actual output of the
     region). ERCOT prints the actual HSL SYSTEM-WIDE ONLY: a region has GEN and COP_HSL_<region>, and COP HSL is the
     limit resources PLANNED in their Current Operating Plan, a plan, not the limit they reported in the hour. It is
     never read here and never stands in for the HSL. So a region has output and no "output below HSL".
     These are ERCOT's own wind and solar regions, not the eight weather zones of its load reports.
  2. PG7-126-M "Hourly Aggregated Wind and Solar Output" (report type 13424): one workbook a year; the public list
     keeps three (2023, 2024 and 2025 on 7 October 2026; display duration 1,095 days). Sheets Wind Data and Solar
     Data: Time (Hour-Ending) in Central clock time, ERCOT.LOAD, ERCOT.WIND.GEN or ERCOT.PVGR.GEN (system-wide hourly
     output, MW), total installed capacity, and ratios. NO HSL and NO region. Only the output column is read.

  SEEN IN THE FIRST NINE DAYS (28 September to 6 October 2026), reported and not corrected: system-wide solar GEN is
  ABOVE SYSTEM_WIDE_HSL in the morning hours of every day (44 of 219 hours, by up to 2,921 MW in the hour from 08:00
  Central) and below it by about as much in the evening, as if the two hourly averages were not of the same minutes.
  Output below HSL counts the evening and not the morning, so part of the solar estimate is this timing and not
  curtailment (29,190 MWh above against 59,580 MWh below over those hours). Wind shows it far less (562 against 126,031).

  WHAT IS NOT OPEN: the history of the hourly reports before the 7-day list. ERCOT's product pages send it to the
  Data Access Portal (data.ercot.com), whose own script asks https://api.ercot.com/api/public-reports/archive/<id>
  with a signed-in account's token and a subscription key. The ERW holds neither and this connector never asks that
  address. So the HSL is not openly published back to 2016, and no estimate is made for the hours without one:
  installed capacity, COP HSL and forecasts are never substituted for it.

Tables (series shape, MW, freq PT1H, ts_utc the hour's START in UTC; ERCOT labels an hour by its end in Central time):

    ercot_wind_solar_hsl_hourly     from the regional reports. entity ercot:system with wind_generation_mw,
                                    wind_hsl_mw, solar_generation_mw, solar_hsl_mw; entity ercot:wind:<REGION> with
                                    wind_generation_mw; entity ercot:solar:<Region> with solar_generation_mw. The
                                    newest posting that holds an hour wins. A blank stays blank: no row.
    ercot_wind_solar_hsl_monthly    derived by --write from the hourly table and nothing else, per Central month,
                                    fuel and area: <fuel>_generation_mwh, <fuel>_hsl_mwh, <fuel>_below_hsl_mwh
                                    (the sum over hours of max(0, HSL - GEN): the ERW's ESTIMATE of curtailment, the
                                    same as ercot_wind_solar_hsl_daily, not a figure ERCOT publishes),
                                    <fuel>_hours_held, <fuel>_hours_in_month and <fuel>_below_hsl_share_pct
                                    (below HSL / HSL x 100). Where an area has an HSL an hour is held with both its
                                    GEN and its HSL, and the three sums run over those hours; a region (no HSL) is
                                    held with its GEN and has generation only. A month is written only with at
                                    least 95 percent of its hours held; a share above 100 is never written.
    ercot_wind_solar_output_hourly  from the yearly workbooks: entity ercot:system, wind_generation_mw and
                                    solar_generation_mw (output only: no HSL, so no estimate for those years).

Stages:

    python warehouse/connectors/ercot_wind_solar_history.py --pull                 # save ERCOT's files (no data lock)
    python warehouse/connectors/ercot_wind_solar_history.py --write                # the tables, from saved files only
    python warehouse/connectors/ercot_wind_solar_history.py --write --out-dir DIR  # a trial, no data lock
    python warehouse/connectors/ercot_wind_solar_history.py --check [--out-dir DIR]  # against ercot_wind_solar_hsl_daily

--pull asks each report's list afresh, then the last posting of each publish day and the newest one (each holds 48
hours, so together they hold every hour the list still covers) and any yearly workbook not yet saved. A file is
saved once under warehouse/raw/ercot_wind_solar_history/ (manifest.csv: address, bytes, sha256, when, rows) and never
asked for again. One request at a time with a pause. Run daily, the hourly table grows by a day a day; a gap of more
than seven days between pulls loses hours for good.

THE CEILING. 2,000,000 rows of these series read to keep, over every run, repeats and probes included (the manifest's
series_rows; the rows of the files are counted apart as file_rows). The pull stops before a file that would pass it.
A publisher in warehouse/metadata/paused_sources.csv is never asked (ip.paused). HTTP 401 or 403, or a page where a
file should be, stops the pull: an access control is reported, never worked around.

Terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read
6 October 2026). License: public; cite "ERCOT".
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import os
import re
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "ercot_wind_solar_history"
NAME_H = "ercot_wind_solar_hsl_hourly"
NAME_M = "ercot_wind_solar_hsl_monthly"
NAME_O = "ercot_wind_solar_output_hourly"
DAILY = "ercot_wind_solar_hsl_daily"
TZ = "America/Chicago"
CEILING = 2_000_000
MIN_SHARE_OF_HOURS = 0.95
CHECK_MWH = 0.5  # --check: 0.02 MW an hour, 25 hours at most, between ERCOT's system-wide and by-region reports
PAUSE = 2.0
RAW = os.path.join(ip.RAW_DIR, CONNECTOR)
LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={}"
DOC = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={}"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id={}"
TERMS = ("ERCOT's terms: \"raw data provided in public portions of this website may be used, reproduced, and "
         "redistributed in compilations, charts, and analyses without maintaining such notices.\" "
         "(https://www.ercot.com/help/terms, read 6 October 2026)")
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
# fuel: (report type, ERCOT's id, report title)
REPORTS = {
    "wind": (14787, "NP4-742-CD", "Wind Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region"),
    "solar": (21809, "NP4-745-CD", "Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region"),
}
WORKBOOK = (13424, "PG7-126-M", "Hourly Aggregated Wind and Solar Output")
SRC_REGION = "ercot:np4_742_745_region"
SRC_WORKBOOK = "ercot:PG7-126-M"
# the workbook's sheets, and the names its output column has carried
SHEETS = {"wind": ("Wind Data", ("ERCOT.WIND.GEN", "Total Wind Output, MW")),
          "solar": ("Solar Data", ("ERCOT.PVGR.GEN", "Total Solar Output, MW"))}
POSTING_EST = 500      # rows of these series one posting can hold (48 hours x 8 series = 384)
WORKBOOK_EST = 17_600  # one year, two series (8,784 hours in a leap year)
MANIFEST_COLS = ["retrieved_at", "status", "bytes", "sha256", "kind", "file", "url", "published", "series_rows",
                 "file_rows", "note"]
KEPT_KINDS = ("posting", "workbook")


class CeilingStop(RuntimeError):
    """The next file would pass the ceiling: nothing more is asked."""


class AccessStop(RuntimeError):
    """ERCOT answered with an access control (401, 403, or a page where a file should be): not worked around."""


# ---------------------------------------------------------------- the saved files

def manifest_path():
    return os.path.join(RAW, "manifest.csv")


def manifest():
    if not os.path.exists(manifest_path()):
        return []
    with open(manifest_path(), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def record(**row):
    os.makedirs(RAW, exist_ok=True)
    new = not os.path.exists(manifest_path())
    with open(manifest_path(), "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(MANIFEST_COLS)
        w.writerow([row.get(c, "") for c in MANIFEST_COLS])


def held():
    """The files saved and still on disk, by address: {url: manifest row}."""
    out = {}
    for r in manifest():
        if r["kind"] in KEPT_KINDS and r["status"] == "200" and os.path.exists(os.path.join(RAW, r["file"])):
            out[r["url"]] = r
    return out


def counted():
    """(rows of these series read to keep, rows of the files read, requests, bytes), every run and every probe."""
    rows = manifest()
    return (sum(int(r["series_rows"] or 0) for r in rows), sum(int(r["file_rows"] or 0) for r in rows), len(rows),
            sum(int(r["bytes"] or 0) for r in rows))


def ask(est, what):
    have = counted()[0]
    if have + int(est) > CEILING:
        raise CeilingStop(f"stopped before {what}: {have:,} rows read and {int(est):,} more would pass the ceiling of {CEILING:,}")


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http_get(url):
    return requests.get(url, headers=UA, timeout=180)


def fetch(url, kind, name, log, published="", count=None, note=""):
    """One request, saved under RAW/<kind>s/<name> with its manifest line. count(body) gives (series rows, file rows)
    and fails on a file that is not what was asked for. Returns the body."""
    r = None
    for attempt in range(3):
        try:
            r = http_get(url)
        except requests.RequestException as exc:
            log(f"    retry {attempt + 1}/3 for {url}: {exc!r}")
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code in (401, 403):
            record(retrieved_at=now_utc(), status=r.status_code, bytes=len(r.content), sha256="", kind=kind, file="", url=url,
                   published=published, series_rows=0, file_rows=0, note="an access control: not worked around")
            raise AccessStop(f"HTTP {r.status_code} for {url}: an access control, nothing more asked")
        if r.status_code == 200:
            break
        log(f"    retry {attempt + 1}/3 for {url}: HTTP {r.status_code}")
        time.sleep(10 * (attempt + 1))
    if r is None or r.status_code != 200:
        raise RuntimeError(f"{url}: no answer after 3 attempts ({'no response' if r is None else 'HTTP ' + str(r.status_code)})")
    body = r.content
    rel = f"{kind}s/{re.sub(r'[^A-Za-z0-9._-]+', '_', name)}"
    path = os.path.join(RAW, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(body)
    if kind in KEPT_KINDS and body[:2] != b"PK":
        record(retrieved_at=now_utc(), status=r.status_code, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), kind="refused",
               file=rel, url=url, published=published, series_rows=0, file_rows=0, note="not a zip or workbook: a page where a file should be")
        raise AccessStop(f"{url}: a page where a file should be ({body[:60]!r}); nothing more asked")
    try:
        s_rows, f_rows = count(body) if count else (0, 0)
    except Exception as exc:
        record(retrieved_at=now_utc(), status=r.status_code, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), kind="unread",
               file=rel, url=url, published=published, series_rows=0, file_rows=0, note=f"could not be read: {str(exc)[:200]}")
        raise
    record(retrieved_at=now_utc(), status=r.status_code, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), kind=kind, file=rel,
           url=url, published=published, series_rows=s_rows, file_rows=f_rows, note=note)
    log(f"  GET {url}: {len(body):,} bytes, {s_rows:,} rows of these series ({rel})")
    time.sleep(PAUSE)
    return body


# ---------------------------------------------------------------- parsers

def hour_starts(d):
    """The UTC start of each row's hour, from ERCOT's DELIVERY_DATE (Central) and HOUR_ENDING (1 to 24). The repeated
    hour of the autumn clock change is told apart by DSTFlag (Y on the second); an hour the spring change skips is NaT."""
    day = pd.to_datetime(d["DELIVERY_DATE"], format="%m/%d/%Y")
    local = day + pd.to_timedelta(pd.to_numeric(d["HOUR_ENDING"]) - 1, unit="h")
    second = d["DSTFlag"].astype(str).str.upper().eq("Y") if "DSTFlag" in d else pd.Series(False, index=d.index)
    return local.dt.tz_localize(TZ, ambiguous=(~second).to_numpy(), nonexistent="NaT").dt.tz_convert("UTC")


def posting_columns(columns, fuel):
    """{column: (entity, variable)} for the actual columns of a regional posting. COP_HSL_*, the forecasts and every
    other column are left out: only GEN and the actual HSL are read."""
    out = {}
    for c in columns:
        if c == "SYSTEM_WIDE_GEN":
            out[c] = ("ercot:system", f"{fuel}_generation_mw")
        elif c == "SYSTEM_WIDE_HSL":
            out[c] = ("ercot:system", f"{fuel}_hsl_mw")
        elif c.startswith("GEN_"):
            out[c] = (f"ercot:{fuel}:{c[4:]}", f"{fuel}_generation_mw")
        elif c.startswith("HSL_"):  # ERCOT prints no regional actual HSL today; read as published if it ever does
            out[c] = (f"ercot:{fuel}:{c[4:]}", f"{fuel}_hsl_mw")
    return out


def parse_posting(body, fuel):
    """One posting (a zip holding one CSV) as long rows: ts (UTC hour start), entity, variable, value. A blank is no row."""
    z = zipfile.ZipFile(io.BytesIO(body))
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if len(names) != 1:
        raise RuntimeError(f"a posting with {len(names)} CSV files: {z.namelist()}")
    d = pd.read_csv(z.open(names[0]), dtype=str, keep_default_na=False)
    cols = posting_columns(d.columns, fuel)
    need = {"DELIVERY_DATE", "HOUR_ENDING", "SYSTEM_WIDE_GEN", "SYSTEM_WIDE_HSL"}
    if not need <= set(d.columns) or not any(e != "ercot:system" for e, _ in cols.values()):
        raise RuntimeError(f"{names[0]}: columns {list(d.columns)} are not a regional hourly report's")
    ts = hour_starts(d)
    parts = []
    for c, (entity, variable) in cols.items():
        text = d[c].str.strip()
        v = pd.to_numeric(text.mask(text == ""), errors="raise")  # a blank is missing; anything else must be a number
        keep = v.notna()
        if (keep & ts.isna()).any():
            raise RuntimeError(f"{names[0]}: a value in an hour the clock change skips ({c})")
        parts.append(pd.DataFrame({"ts": ts[keep], "entity": entity, "variable": variable, "value": v[keep].astype(float)}))
    out = pd.concat(parts, ignore_index=True)
    if out.duplicated(["ts", "entity", "variable"]).any():
        raise RuntimeError(f"{names[0]}: an hour twice in one posting")
    return out, len(d)


def workbook_rows(body):
    """The yearly workbook as long rows: ts (UTC hour start), entity ercot:system, variable, value, from the sheets
    Wind Data and Solar Data. Time (Hour-Ending) is Central clock time: on the autumn change the hour ending 01:00
    is listed twice (the first is daylight time), on the spring change the hour ending 02:00 is not listed."""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(body), read_only=True, data_only=True)
    parts, n_file = [], 0
    try:
        for fuel, (sheet, gen_names) in SHEETS.items():
            if sheet not in wb.sheetnames:
                raise RuntimeError(f"the workbook has no sheet {sheet!r}: {wb.sheetnames}")
            it = wb[sheet].iter_rows(values_only=True)
            head = [str(h).strip() if h is not None else "" for h in next(it)]
            if "Time (Hour-Ending)" not in head or not any(g in head for g in gen_names):
                raise RuntimeError(f"sheet {sheet!r}: columns {head[:9]} hold no Time (Hour-Ending) or none of {gen_names}")
            ti, gi = head.index("Time (Hour-Ending)"), head.index(next(g for g in gen_names if g in head))
            ends, vals = [], []
            for row in it:
                t, g = row[ti], row[gi]
                if t is None and g is None:
                    continue
                n_file += 1
                if not isinstance(t, dt.datetime):
                    raise RuntimeError(f"sheet {sheet!r}: a time that is not a date and hour: {t!r}")
                t = pd.Timestamp(t).round("s")
                if t.minute or t.second:
                    raise RuntimeError(f"sheet {sheet!r}: an hour ending that is not on the hour: {t}")
                if g is None or (isinstance(g, str) and not g.strip()):
                    continue  # a blank stays blank
                if isinstance(g, bool) or not isinstance(g, (int, float)):
                    raise RuntimeError(f"sheet {sheet!r} {t}: output {g!r} is not a number")
                ends.append(t)
                vals.append(float(g))
            idx = pd.DatetimeIndex(ends)
            first = ~idx.duplicated(keep="first")  # of an hour ending listed twice, the first is daylight time
            end_utc = idx.tz_localize(TZ, ambiguous=first, nonexistent="raise").tz_convert("UTC")
            parts.append(pd.DataFrame({"ts": end_utc - pd.Timedelta(hours=1), "entity": "ercot:system",
                                       "variable": f"{fuel}_generation_mw", "value": vals}))
    finally:
        wb.close()
    out = pd.concat(parts, ignore_index=True)
    if out.duplicated(["ts", "entity", "variable"]).any():
        raise RuntimeError("the workbook lists an hour twice")
    return out, n_file


def check_year(rows, what):
    """A yearly workbook must hold whole Central years hour by hour: every step one hour, first hour 1 January 00:00."""
    for variable, g in rows.groupby("variable"):
        ts = g["ts"].sort_values()
        steps = ts.diff().dropna()
        if not (steps == pd.Timedelta(hours=1)).all():
            bad = ts[1:][(steps != pd.Timedelta(hours=1)).to_numpy()]
            raise RuntimeError(f"{what} {variable}: {len(bad)} steps are not one hour (first at {bad.iloc[0]})")
        lo, hi = ts.iloc[0].tz_convert(TZ), (ts.iloc[-1] + pd.Timedelta(hours=1)).tz_convert(TZ)
        if (lo.month, lo.day, lo.hour) != (1, 1, 0) or (hi.month, hi.day, hi.hour) != (1, 1, 0):
            raise RuntimeError(f"{what} {variable}: {lo} to {hi} is not whole Central years")


# ---------------------------------------------------------------- pull

def pick_postings(docs, held_published=()):
    """Of a list's CSV postings: the last of each publish day (Central) and so the newest. Each holds 48 hours, so
    together they hold every hour from 48 hours before the first of them. The oldest posting on the list reaches about
    a day further back: it is wanted too unless a posting published at or before it is already saved (held_published,
    the publish times of the saved postings of this report), which is every run but the first and one after a lapse."""
    docs = sorted((x for x in docs if x["FriendlyName"].lower().endswith("_csv")), key=lambda x: x["PublishDate"])
    by_day = {}
    for x in docs:
        by_day[x["PublishDate"][:10]] = x
    pick = list(by_day.values())
    if docs and docs[0] not in pick:
        oldest = pd.Timestamp(docs[0]["PublishDate"])
        if not any(pd.Timestamp(p) <= oldest for p in held_published if p):
            pick.insert(0, docs[0])
    return pick


def listing(rtid, log):
    import json
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    body = fetch(LIST.format(rtid), "list", f"{rtid}_{stamp}.json", log, note="the public document list, asked afresh each pull")
    got = json.loads(body.decode("utf-8"))["ListDocsByRptTypeRes"].get("DocumentList") or []
    return [x["Document"] for x in got]


def pull(log, limit=10 ** 9):
    """Save what ERCOT's public lists hold and the ERW does not. Returns a line saying what happened."""
    if ip.paused("ercot"):
        log(ip.pause_line("ercot"))
        return "paused: no request made"
    asked = 0
    have = held()
    for fuel, (rtid, emil, _) in REPORTS.items():
        mine = [r["published"] for r in have.values() if r["kind"] == "posting" and r["note"].split()[-1] == fuel]
        docs = pick_postings(listing(rtid, log), mine)
        log(f"  {emil}: {len(docs)} postings wanted (the last of each publish day, and the oldest when none as old is saved), "
            f"{sum(DOC.format(x['DocID']) in have for x in docs)} already saved")
        for x in docs:
            url = DOC.format(x["DocID"])
            if url in have:
                continue
            if asked >= limit:
                return f"ok: stopped at the limit of {limit} files"
            ask(POSTING_EST, f"{emil} {x['PublishDate']}")
            fetch(url, "posting", f"{rtid}/{x['ConstructedName']}", log, published=x["PublishDate"],
                  count=lambda b, fuel=fuel: (lambda p: (len(p[0]), p[1]))(parse_posting(b, fuel)), note=f"{emil} {fuel}")
            asked += 1
    rtid, emil, _ = WORKBOOK
    for x in sorted(listing(rtid, log), key=lambda x: x["PublishDate"]):
        url = DOC.format(x["DocID"])
        if x["Extension"].lower() != "xlsx" or url in have:
            continue
        if asked >= limit:
            return f"ok: stopped at the limit of {limit} files"
        ask(WORKBOOK_EST, f"{emil} {x['FriendlyName']}")
        fetch(url, "workbook", x["ConstructedName"], log, published=x["PublishDate"],
              count=lambda b: (lambda p: (len(p[0]), p[1]))(workbook_rows(b)), note=f"{emil} {x['FriendlyName']}")
        asked += 1
    return f"ok: {asked} files saved"


# ---------------------------------------------------------------- the tables

def series(rows, source, node_of=lambda e: ""):
    """Long rows (ts, entity, variable, value, url, retrieved) as the series shape."""
    s = pd.DataFrame({
        "entity": rows["entity"], "variable": rows["variable"], "ts_utc": rows["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": rows["value"], "unit": "MW", "freq": "PT1H", "geo": "US-TX", "market": "",
        "node": rows["entity"].map(node_of), "source": source, "source_url": rows["url"], "retrieved_at": rows["retrieved"],
        "vintage": ""})
    return s.sort_values(ip.SERIES_KEY).reset_index(drop=True)[ip.SERIES_COLS]


def region_of(entity):
    return entity.split(":", 2)[2] if entity.count(":") == 2 else ""


def build_hourly(log):
    """Every saved posting, oldest first, the newest posting that holds an hour winning. One file in memory at a time."""
    best, n_files = {}, {}
    rows = sorted((r for r in held().values() if r["kind"] == "posting"), key=lambda r: (r["published"], r["url"]))
    for r in rows:
        fuel = r["note"].split()[-1]
        if fuel not in REPORTS:
            raise RuntimeError(f"manifest line of {r['file']} names no fuel: {r['note']!r}")
        with open(os.path.join(RAW, r["file"]), "rb") as f:
            body = f.read()
        if hashlib.sha256(body).hexdigest() != r["sha256"]:
            raise RuntimeError(f"{r['file']} is not the file the manifest recorded (sha256)")
        d, _ = parse_posting(body, fuel)
        for ts, entity, variable, value in d.itertuples(index=False):
            best[(entity, variable, ts)] = (value, r["url"], r["retrieved_at"])
        n_files[fuel] = n_files.get(fuel, 0) + 1
    if not best:
        raise RuntimeError("no posting saved: run --pull first")
    out = pd.DataFrame([(ts, e, v, x[0], x[1], x[2]) for (e, v, ts), x in best.items()],
                       columns=["ts", "entity", "variable", "value", "url", "retrieved"])
    log(f"  hourly: {len(out):,} values from {n_files} postings")
    return out, n_files


def build_output(log):
    parts, used = [], []
    for r in sorted((r for r in held().values() if r["kind"] == "workbook"), key=lambda r: r["published"]):
        with open(os.path.join(RAW, r["file"]), "rb") as f:
            body = f.read()
        if hashlib.sha256(body).hexdigest() != r["sha256"]:
            raise RuntimeError(f"{r['file']} is not the file the manifest recorded (sha256)")
        d, _ = workbook_rows(body)
        del body
        check_year(d, r["file"])
        d["url"], d["retrieved"] = r["url"], r["retrieved_at"]
        parts.append(d)
        used.append((r["note"].split()[-1], r["url"], d["ts"].min(), d["ts"].max(), len(d)))
        log(f"  {r['file']}: {len(d):,} hours of output, {d['ts'].min()} to {d['ts'].max()}")
    if not parts:
        raise RuntimeError("no yearly workbook saved: run --pull first")
    out = pd.concat(parts, ignore_index=True)
    dup = out.duplicated(["ts", "entity", "variable"], keep="last")
    if dup.any():  # two workbooks holding the same hour: the later published wins
        log(f"  {int(dup.sum())} hours are in two workbooks; the later published is kept")
        out = out[~out.duplicated(["ts", "entity", "variable"], keep="last")]
    return out, used


def wide(hourly):
    """The hourly table (series rows) as one row per (entity, fuel, hour): ts (UTC), gen, hsl (NaN where none)."""
    d = hourly[["entity", "variable", "ts_utc", "value"]].copy()
    m = d["variable"].str.extract(r"^(wind|solar)_(generation|hsl)_mw$")
    if m[0].isna().any():
        raise RuntimeError(f"variables that are not <fuel>_generation_mw or <fuel>_hsl_mw: {sorted(d['variable'][m[0].isna()].unique())[:5]}")
    d["fuel"], d["kind"] = m[0], m[1]
    d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    w = d.pivot(index=["entity", "fuel", "ts"], columns="kind", values="value").reset_index()
    for c in ("generation", "hsl"):
        if c not in w:
            w[c] = float("nan")
    return w.rename(columns={"generation": "gen"})[["entity", "fuel", "ts", "gen", "hsl"]]


def sums(w, period):
    """Sums of the held hours per (entity, fuel, Central period): period "D" a day, "M" a month. Where the group has
    an HSL in the period an hour is held with both GEN and HSL; where it has none, with its GEN."""
    local = w["ts"].dt.tz_convert(TZ)
    w = w.assign(period=local.dt.strftime("%Y-%m-%d" if period == "D" else "%Y-%m"))
    out = []
    for (entity, fuel, p), g in w.groupby(["entity", "fuel", "period"], sort=True):
        has_hsl = bool(g["hsl"].notna().any())
        h = g[g["gen"].notna() & g["hsl"].notna()] if has_hsl else g[g["gen"].notna()]
        first = pd.Timestamp(p + ("-01" if period == "M" else ""))  # clock dates first, then the zone: a day is 23 to 25 hours
        start = first.tz_localize(TZ)
        end = (first + (pd.offsets.MonthBegin(1) if period == "M" else pd.Timedelta(days=1))).tz_localize(TZ)
        row = dict(entity=entity, fuel=fuel, period=p, has_hsl=has_hsl, hours_held=len(h),
                   hours_in_period=int((end - start) / pd.Timedelta(hours=1)), generation_mwh=float(h["gen"].sum()),
                   hsl_mwh=float(h["hsl"].sum()) if has_hsl else float("nan"),
                   below_hsl_mwh=float((h["hsl"] - h["gen"]).clip(lower=0).sum()) if has_hsl else float("nan"))
        out.append(row)
    return pd.DataFrame(out, columns=["entity", "fuel", "period", "has_hsl", "hours_held", "hours_in_period", "generation_mwh",
                                      "hsl_mwh", "below_hsl_mwh"])


def monthly(hourly, log=lambda m: None):
    """The monthly table's rows from the hourly table's, and the months left out (under 95 percent of their hours)."""
    s = sums(wide(hourly), "M")
    retrieved = hourly["retrieved_at"].max() if "retrieved_at" in hourly and len(hourly) else ""
    rows, left = [], []
    for r in s.itertuples(index=False):
        if r.hours_held < MIN_SHARE_OF_HOURS * r.hours_in_period:
            left.append((r.entity, r.fuel, r.period, r.hours_held, r.hours_in_period))
            continue
        vals = [(f"{r.fuel}_generation_mwh", round(r.generation_mwh, 3), "MWh"),
                (f"{r.fuel}_hours_held", r.hours_held, "count"), (f"{r.fuel}_hours_in_month", r.hours_in_period, "count")]
        if r.has_hsl:
            vals += [(f"{r.fuel}_hsl_mwh", round(r.hsl_mwh, 3), "MWh"), (f"{r.fuel}_below_hsl_mwh", round(r.below_hsl_mwh, 3), "MWh")]
            if r.hsl_mwh > 0:
                share = r.below_hsl_mwh / r.hsl_mwh * 100
                if share > 100:
                    log(f"  {r.entity} {r.fuel} {r.period}: below HSL / HSL = {share:.3f} percent, above 100; the share is not written")
                else:
                    vals.append((f"{r.fuel}_below_hsl_share_pct", round(share, 4), "pct"))
        for variable, value, unit in vals:
            rows.append(dict(entity=r.entity, variable=variable, ts_utc=f"{r.period}-01T00:00:00Z", value=value, unit=unit, freq="P1M",
                             geo="US-TX", market="", node=region_of(r.entity), source="erw:" + NAME_M,
                             source_url="https://github.com/SamuelEnrique/erw/blob/main/warehouse/connectors/ercot_wind_solar_history.py",
                             retrieved_at=retrieved, vintage=""))
    return pd.DataFrame(rows, columns=ip.SERIES_COLS), left


def source_lines():
    out = []
    for fuel, (rtid, emil, title) in REPORTS.items():
        out.append(f"Source: {SRC_REGION} ERCOT {emil}, {title}, {PAGE.format(emil)}")
        out.append(f"  access: {LIST.format(rtid)} and {DOC.format('<DocID>')}")
    return out


def write(out_dir=None):
    if out_dir:
        ip.set_out_dir(out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    s_rows, f_rows, reqs, nbytes = counted()
    log(f"ERW {CONNECTOR} --write {run_id}: from the saved files under {os.path.relpath(RAW, ip.ROOT)}; "
        f"{s_rows:,} rows of these series read against the ceiling of {CEILING:,}")
    common = [f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_wind_solar_history.py --write, from the files --pull saved",
              f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
              f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; manifest.csv lists each file, its address, bytes and sha256)"]
    tail = [f"Rows of these series read by the pull, every run and probe: {s_rows:,} (ceiling {CEILING:,}); rows in the files read: {f_rows:,}; "
            f"{reqs:,} requests, {nbytes:,} bytes.", f"License: public. {TERMS}. Cite \"ERCOT\"."]
    results, registered = [], []

    def stage(table, fn):
        try:
            detail = fn()
            results.append(dict(table=table, market="all", status="ok" if not detail.startswith("skipped") else "skipped", detail=detail))
            print(f"{table}: {detail}")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{table} FAILED, no output file written:\n{tb}")
            print(f"{CONNECTOR} {table} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=table, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))

    def hourly_stage():
        rows, n_files = build_hourly(log)
        s = series(rows, SRC_REGION, region_of)
        header = [
            "Energy Research Warehouse (ERW): ERCOT wind and solar output and the High Sustained Limit (HSL), hourly, system-wide and by ERCOT's wind and solar regions (session 144)",
            "Shape: series (docs/datastandard.md v0). MW, freq PT1H; ts_utc is the hour's start (ERCOT's DELIVERY_DATE and HOUR_ENDING are Central time, the hour named by its end; "
            "DSTFlag tells the repeated hour of the autumn clock change apart).",
            "Entities: ercot:system (ERCOT's SYSTEM_WIDE columns), ercot:wind:<REGION> (PANHANDLE, COASTAL, SOUTH, WEST, NORTH) and ercot:solar:<Region> (CenterWest, NorthWest, FarWest, "
            "FarEast, SouthEast, CenterEast), the regions as ERCOT prints them. They are ERCOT's wind and solar regions, not the eight weather zones of its load reports.",
            "Variables: <fuel>_generation_mw = ERCOT's GEN, the hourly average of actual output. <fuel>_hsl_mw = ERCOT's SYSTEM_WIDE_HSL, the hourly average of the High Sustained Limit, "
            "the output the resources report they could sustain. ERCOT prints the actual HSL system-wide only: a region has generation and no HSL. ERCOT's COP_HSL columns (the limit planned "
            "in the Current Operating Plan) and its forecasts are not read and never stand in for the HSL.",
            "An hour's value is the newest posting's that holds it; a blank in ERCOT's file is no row. ERCOT's public list keeps 7 days of postings and each holds 48 hours, so the table "
            "starts about nine days before the first pull (28 September 2026) and grows only while the pull runs at least weekly. The history before it is not openly published "
            "(ERCOT's Data Access Portal needs a signed-in account and a key: not used).",
            f"This run: {', '.join(f'{n} {fuel} postings' for fuel, n in n_files.items())} read from the saved files.",
        ] + common + source_lines() + tail
        ip.write_csv(s, NAME_H, header, log)
        registered.append(dict(source=SRC_REGION, publisher=ip.ISO_PUBLISHERS["ercot"],
                               report="Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (NP4-742-CD, NP4-745-CD) "
                                      f"[terms: {TERMS.split(': ', 1)[1]}]",
                               report_url=PAGE.format("NP4-742-CD"), document_list=LIST.format(REPORTS["wind"][0]), license="public", tables=[NAME_H]))
        return f"{len(s):,} rows this run, {s['ts_utc'].min()} to {s['ts_utc'].max()}, {s['entity'].nunique()} areas"

    def monthly_stage():
        path = os.path.join(ip.OUT_DIR, NAME_H + ".csv")
        if not os.path.exists(path):
            raise RuntimeError(f"{NAME_H}.csv is not there: the monthly table is built from it and nothing else")
        hourly = ip.read_series(path)
        m, left = monthly(hourly, log)
        for e, fuel, p, n, want in left:
            log(f"  {e} {fuel} {p}: {n} of {want} hours held, under {MIN_SHARE_OF_HOURS:.0%}; month not written")
        if m.empty:
            log(f"  no month has {MIN_SHARE_OF_HOURS:.0%} of its hours: {NAME_M} is not written")
            return f"skipped: no month has 95 percent of its hours held yet ({len(left)} area-months under it); no file written"
        header = [
            "Energy Research Warehouse (ERW): ERCOT wind and solar output, High Sustained Limit (HSL) and output below HSL, monthly, system-wide and by ERCOT's wind and solar regions (session 144)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc is the first of the Central (America/Chicago) month at 00:00:00Z (Decision 11). Built from ercot_wind_solar_hsl_hourly and nothing else.",
            "Variables: <fuel>_generation_mwh (sum of hourly GEN), <fuel>_hsl_mwh (sum of hourly HSL), <fuel>_below_hsl_mwh (sum over hours of max(0, HSL - GEN)), <fuel>_hours_held, "
            "<fuel>_hours_in_month, <fuel>_below_hsl_share_pct (below HSL / HSL x 100).",
            "ERCOT publishes no curtailment figure. Output below HSL is the ERW's ESTIMATE of it, the same as ercot_wind_solar_hsl_daily, not ERCOT's: output also falls below the limit through "
            "ramping, telemetry and the hourly averaging of both figures (docs/methods/curtailment.md).",
            "Where an area has an HSL (ercot:system) an hour is held with both its GEN and its HSL and the three sums run over those hours. ERCOT prints no HSL for a region: a region is held "
            "with its GEN and has generation only, no estimate.",
            f"A month is written only with at least {MIN_SHARE_OF_HOURS:.0%} of its hours held; a share above 100 is never written. {len(left)} area-months were under it in this run.",
            f"Source: erw:{NAME_M} ERW derived table (warehouse/connectors/ercot_wind_solar_history.py), https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md",
            f"Derived from: {NAME_H}", f"input sources: {SRC_REGION}",
        ] + common[:2] + ["License: public. A derived table inherits the most restrictive license of its inputs (Decision 23)."]
        ip.write_csv(m, NAME_M, header, log)
        registered.append(dict(source="erw:" + NAME_M, publisher="Energy Research Warehouse (ERW)",
                               report="ERW derived table: ERCOT output below HSL by month, the ERW's estimate (docs/methods/curtailment.md)",
                               report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md", document_list="",
                               license="public", tables=[NAME_M]))
        return f"{len(m):,} rows this run, {m['ts_utc'].min()[:7]} to {m['ts_utc'].max()[:7]}; {len(left)} area-months under 95 percent of their hours, not written"

    def output_stage():
        rows, used = build_output(log)
        s = series(rows, SRC_WORKBOOK)
        rtid, emil, title = WORKBOOK
        header = [
            "Energy Research Warehouse (ERW): ERCOT wind and solar output, hourly, system-wide, from ERCOT's yearly workbooks (session 144)",
            "Shape: series (docs/datastandard.md v0). MW, freq PT1H; ts_utc is the hour's start. The workbook's Time (Hour-Ending) is Central clock time: on the autumn clock change the hour "
            "ending 01:00 is listed twice (the first is daylight time), on the spring change the hour ending 02:00 is not listed; every year read steps hour by hour in UTC with no gap.",
            "Entity ercot:system. wind_generation_mw = the workbook's ERCOT.WIND.GEN (sheet Wind Data); solar_generation_mw = ERCOT.PVGR.GEN (sheet Solar Data): hourly aggregated output, MW.",
            "OUTPUT ONLY. The workbook holds no High Sustained Limit and no region, so there is no output below HSL for these years; its other columns (ERCOT.LOAD, total installed capacity "
            "and ratios) are not read, and installed capacity never stands in for the HSL.",
            "ERCOT's public list keeps three yearly workbooks (2023, 2024 and 2025 on 7 October 2026); earlier years are not on it.",
            "This run: " + "; ".join(f"{name} {lo:%Y-%m-%dT%HZ} to {hi:%Y-%m-%dT%HZ}, {n:,} values" for name, _, lo, hi, n in used) + ".",
        ] + common + [f"Source: {SRC_WORKBOOK} ERCOT {emil}, {title}, {PAGE.format(emil)}",
                      f"  access: {LIST.format(rtid)} and {DOC.format('<DocID>')}"] + tail
        ip.write_csv(s, NAME_O, header, log)
        registered.append(dict(source=SRC_WORKBOOK, publisher=ip.ISO_PUBLISHERS["ercot"],
                               report=f"{title} (yearly workbook: system-wide hourly wind and solar output) [terms: {TERMS.split(': ', 1)[1]}]",
                               report_url=PAGE.format(emil), document_list=LIST.format(rtid), license="public", tables=[NAME_O]))
        return f"{len(s):,} rows this run, {s['ts_utc'].min()} to {s['ts_utc'].max()}"

    stage(NAME_H, hourly_stage)
    stage(NAME_M, monthly_stage)
    stage(NAME_O, output_stage)
    if not out_dir:  # a trial leaves the registry and the run status alone
        if registered:
            ip.update_sources(registered)
        ip.write_status(CONNECTOR, run_id, results)
    log(f"done: {[(r['table'], r['status']) for r in results]}")
    log.close()
    print(f"{CONNECTOR} run log: {log.path}")
    return 0 if all(r["status"] != "failed" for r in results) else 1


# ---------------------------------------------------------------- the check against the daily table

def check(out_dir=None, live_dir=None):
    """For each Central day ercot_wind_solar_hsl_daily holds and the hourly table holds whole (every hour with GEN and
    HSL), the hourly rows summed by day against the daily table's three figures. The daily table reads ERCOT's
    system-wide reports (NP4-732-CD and NP4-737-CD), this one the by-region reports, and ERCOT prints the same hour's
    system-wide figure up to 0.02 MW apart in the two (the by-region report's is the sum of its rounded regions; seen
    in session 144 in about half the hours). So a day may differ by 0.02 MW x its hours, CHECK_MWH, and by no more:
    an hour placed on the wrong day would differ by thousands. Returns 0 when every difference is within it."""
    mine = ip.read_series(os.path.join(out_dir or ip.OUT_DIR, NAME_H + ".csv"))
    live = ip.read_series(os.path.join(live_dir or os.path.join(ip.ROOT, "warehouse", "output"), DAILY + ".csv"))
    d = sums(wide(mine[mine["entity"] == "ercot:system"]), "D")
    d = d[d["has_hsl"] & (d["hours_held"] == d["hours_in_period"])]
    long = d.melt(id_vars=["fuel", "period"], value_vars=["generation_mwh", "hsl_mwh", "below_hsl_mwh"], var_name="kind", value_name="hourly_sum")
    long["variable"] = long["fuel"] + "_" + long["kind"]
    long["ts_utc"] = long["period"] + "T00:00:00Z"
    live = live[live["entity"] == "ercot:system"][["variable", "ts_utc", "value"]]
    want = set(zip(long["variable"], long["ts_utc"])) & set(zip(live["variable"], live["ts_utc"]))
    j = long.merge(live, on=["variable", "ts_utc"], how="inner", validate="one_to_one")
    assert len(j) == len(want), f"the join holds {len(j)} rows, {len(want)} expected"
    if j.empty:
        print(f"check: no day is whole in {NAME_H} and held by {DAILY}")
        return 1
    j["diff"] = (j["hourly_sum"] - j["value"]).abs()
    days_live, days_mine = sorted(set(live["ts_utc"].str[:10])), sorted(set(long["period"]))
    print(f"check: {DAILY} holds {len(days_live)} days ({days_live[0]} to {days_live[-1]}); {NAME_H} holds {len(days_mine)} whole days "
          f"({days_mine[0]} to {days_mine[-1]}); {len(j)} day-figures joined ({j['ts_utc'].nunique()} days x fuels x 3 figures)")
    for kind, g in j.groupby("kind"):
        w = g.loc[g["diff"].idxmax()]
        print(f"  {kind}: {len(g)} joined, largest difference {w['diff']:.4f} MWh ({w['variable']} {w['ts_utc'][:10]}: hourly sum {w['hourly_sum']:.3f}, daily table {w['value']:.3f})")
    worst = float(j["diff"].max())
    print(f"  largest difference of all: {worst:.4f} MWh (allowed: {CHECK_MWH} MWh a day, 0.02 MW an hour between ERCOT's two reports)")
    return 0 if worst <= CHECK_MWH else 1


def main(argv=None):
    global RAW
    ap = argparse.ArgumentParser(description="ERCOT wind and solar by the hour: output, HSL where printed, and the yearly workbooks")
    ap.add_argument("--pull", action="store_true", help="save ERCOT's files (no table is written, no data lock)")
    ap.add_argument("--write", action="store_true", help="build the tables from the saved files (the data lock into warehouse/output)")
    ap.add_argument("--check", action="store_true", help="the hourly table summed by day against ercot_wind_solar_hsl_daily")
    ap.add_argument("--limit", type=int, default=10 ** 9, help="pull: at most N files in this run")
    ap.add_argument("--out-dir", help="write, check: the tables under this folder, not warehouse/output (a trial; no data lock)")
    ap.add_argument("--raw-dir", help="another folder for the saved files (a trial or a test)")
    args = ap.parse_args(argv)
    if args.raw_dir:
        RAW = os.path.abspath(args.raw_dir)
    if not (args.pull or args.write or args.check):
        ap.error("one of --pull, --write, --check")
    code = 0
    if args.pull:
        os.makedirs(RAW, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        with open(os.path.join(RAW, f"pull_{stamp}.log"), "w", encoding="utf-8", newline="\n") as f:
            def say(msg):
                f.write(msg + "\n")
                f.flush()
                print(msg)
            try:
                say(f"ERW {CONNECTOR} --pull {stamp}")
                out = pull(say, args.limit)
            except (CeilingStop, AccessStop) as exc:
                out = f"stopped: {exc}"
                code = 1
            except Exception:
                out = "failed: " + traceback.format_exc().strip().splitlines()[-1]
                say(traceback.format_exc())
                code = 1
            s, fr, n, b = counted()
            say(f"pull: {out}. In all: {s:,} rows of these series read against the ceiling of {CEILING:,}; {fr:,} rows in the files read; {n:,} requests, {b:,} bytes")
    if args.write and code == 0:
        code = write(args.out_dir)
    if args.check and code == 0:
        code = check(args.out_dir)
    return code


if __name__ == "__main__":
    sys.exit(main())
