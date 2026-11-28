#!/usr/bin/env python3
"""SPP's own mid-term load forecast beside its actual load, hourly, as SPP publishes it on its marketplace portal
(session 10000, chain 701; predict data request 19 of docs/state/data_requests_predict.md).

Energy Research Warehouse (ERW). SPP's portal (file browser `mtlf-vs-actual`, the page
https://portal.spp.org/pages/mtlf-vs-actual) keeps one file an hour, OP-MTLF-<YYYYMMDDHH00>.csv (the hour in central
prevailing time), each holding SPP's mid-term load forecast (MTLF) for the next seven days and the averaged actual load
of the day before, for SPP's footprint (BAA SPP) and SPP's western area (SWPW); a finished year is one zip of its files.
This connector reads one file a day, the one published at 09:00 central time (before the day-ahead market closes), and
writes every row of it:

    spp_mtlf_hourly   series. entity spp:<BAA>; variable load_forecast_mtlf_mw (the forecast for the hour) or
                      load_actual_mw (the averaged actual SPP prints beside it); ts_utc the hour's start (GMTIntervalEnd
                      less one hour); vintage the hour the file was published (UTC), so a forecast once made is never
                      replaced and each publication's actuals are kept as printed; x_horizon_hours the hours from the
                      publication to the hour's start (negative for an actual); x_interval_end_cpt SPP's own hour ending
                      in central time; x_file the file read.

Nothing is filled or computed: an empty cell of the file is no row. Every file read is saved in warehouse/raw/spp_mtlf/
and a saved file answers a later run (a published file does not change), so a history run stopped at the ceiling
resumes where it stopped.

    python warehouse/connectors/spp_mtlf.py                 # the last 10 days' 09:00 files (the daily run)
    python warehouse/connectors/spp_mtlf.py --history       # every year the portal lists: the zips, then this year's days
    python warehouse/connectors/spp_mtlf.py --out-dir DIR   # a trial: the table under DIR

Ceiling: 120 requests a run (one a second; a 5xx or a timeout retried by iso_prices.fetch_raw). License: public with
citation, not within a commercial publication (SPP's terms, https://www.spp.org/terms-conditions/, license read 1671,
verdict row 7 of warehouse/metadata/license_verdicts.csv), as for SPP's other portal files the warehouse holds.
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "spp_mtlf_hourly"
CONNECTOR = "spp_mtlf"
SOURCE = "spp:MTLF-VS-ACTUAL"
FS = "mtlf-vs-actual"
PAGE = "https://portal.spp.org/pages/mtlf-vs-actual"
LIST = "https://portal.spp.org/file-browser-api/?fsName=" + FS + "&path={path}&type=folder"
DOWNLOAD = "https://portal.spp.org/file-browser-api/download/" + FS + "?path={path}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CEILING, PAUSE = 120, 1
HOUR = "0900"                  # the file read each day: published at 09:00 central time
DAYS = 10
TZ = "America/Chicago"
KEY = ["entity", "variable", "ts_utc", "vintage"]
X_COLS = ["x_horizon_hours", "x_interval_end_cpt", "x_file"]
FILE = re.compile(r"OP-MTLF-(\d{12})\.csv$")


class Ceiling(RuntimeError):
    pass


def published_utc(name):
    """The UTC hour a file was published, from its name (central prevailing time)."""
    m = FILE.search(name)
    if not m:
        raise ValueError(f"not an MTLF file name: {name!r}")
    local = pd.Timestamp(dt.datetime.strptime(m.group(1), "%Y%m%d%H%M"))
    return local.tz_localize(TZ, ambiguous=True, nonexistent="shift_forward").tz_convert("UTC")


def rows_of(content, name, url, retrieved):
    """The table's rows of one MTLF file."""
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    names = {c.strip().lower(): c for c in d.columns}
    d = d.rename(columns={names[k]: v for k, v in (("interval", "Interval"), ("gmtintervalend", "GMTIntervalEnd"), ("mtlf", "MTLF"),
                                                   ("averaged actual", "Averaged Actual"), ("baa", "BAA")) if k in names})
    need = ["Interval", "MTLF", "Averaged Actual"]
    if any(c not in d.columns for c in need):
        raise ValueError(f"{name}: columns {list(d.columns)}, not {need} (with GMTIntervalEnd and BAA in the later files)")
    pub = published_utc(name)
    if "GMTIntervalEnd" in d.columns:
        end = when(d["GMTIntervalEnd"]).dt.tz_localize("UTC")
    else:
        # the early files (2013 on) give only Interval, SPP's hour ending in central prevailing time, one row an hour,
        # newest first; at the autumn change a label repeats. The first row's hour is taken from its label (an hour of
        # the morning, never ambiguous at 09:00's publication) and each row after it is one hour earlier
        loc = when(d["Interval"])
        step = (loc.diff().dropna() / pd.Timedelta(hours=1)).round()
        if not step.isin([-1, -2, 0]).all():
            raise ValueError(f"{name}: the hours are not one apart, newest first")
        first = loc.iloc[0].tz_localize(TZ, ambiguous=False, nonexistent="shift_forward").tz_convert("UTC")
        end = pd.Series([first - pd.Timedelta(hours=i) for i in range(len(d))], index=d.index)
    if "BAA" not in d.columns:
        d["BAA"] = "SPP"   # the early files are SPP's footprint alone
    start = end - pd.Timedelta(hours=1)
    out = []
    for col, var in (("MTLF", "load_forecast_mtlf_mw"), ("Averaged Actual", "load_actual_mw")):
        v = pd.to_numeric(d[col].str.strip(), errors="coerce")
        bad = (d[col].str.strip() != "") & v.isna()
        if bad.any():
            raise ValueError(f"{name}: {int(bad.sum())} cells of {col} are not numbers")
        keep = v.notna()
        if not keep.any():
            continue
        out.append(pd.DataFrame({
            "entity": "spp:" + d.loc[keep, "BAA"].str.strip(), "variable": var,
            "ts_utc": start[keep].dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": v[keep].astype(float),
            "unit": "MW", "freq": "PT1H", "geo": "US", "market": "", "node": "", "source": SOURCE, "source_url": url,
            "retrieved_at": retrieved, "vintage": pub.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "x_horizon_hours": ((start[keep] - pub) / pd.Timedelta(hours=1)).round().astype(int).astype(str),
            "x_interval_end_cpt": d.loc[keep, "Interval"].str.strip(), "x_file": name}))
    t = pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=ip.SERIES_COLS + X_COLS)
    if t.duplicated(KEY).any():
        raise ValueError(f"{name}: an (entity, variable, hour) is given twice")
    return t


def when(col):
    """SPP's times, written with seconds ('11/26/2026 09:00:00') or, in some files of 2017, without ('10/5/2017 14:00')."""
    v = col.str.strip()
    t = pd.to_datetime(v, format="%m/%d/%Y %H:%M:%S", errors="coerce")
    short = t.isna()
    if short.any():
        t[short] = pd.to_datetime(v[short], format="%m/%d/%Y %H:%M", errors="coerce")
    if t.isna().any():
        raise ValueError(f"times not read: {v[t.isna()].head(3).tolist()}")
    return t


def daily_path(day):
    return f"/{day:%Y}/{day:%m}/{day:%d}/OP-MTLF-{day:%Y%m%d}{HOUR}.csv"


def main(argv=None):
    ap = argparse.ArgumentParser(description="SPP's mid-term load forecast beside its actual load (portal mtlf-vs-actual)")
    ap.add_argument("--history", action="store_true", help="every year the portal lists (zips, then this year's days)")
    ap.add_argument("--days", type=int, default=DAYS)
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused("spp"):
        print(f"{NAME}: {ip.pause_line('spp')}")
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    retrieved = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    asked = [0]

    def get(url, fresh=False):
        """(bytes, asked from the source): a saved file is reused unless fresh; each request counted."""
        prepared = requests.Request("GET", url).prepare().url
        if not fresh and ip.raw_cached(CONNECTOR, prepared):
            return ip.fetch_raw(CONNECTOR, url, log)[0], False
        if asked[0] >= CEILING:
            raise Ceiling(f"the ceiling of {CEILING} requests is reached")
        asked[0] += 1
        return ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, pause=PAUSE, headers=UA)[0], True

    frames, files, missing, stopped = [], 0, [], ""
    try:
        today = pd.Timestamp.now(tz=TZ)
        if args.history:
            years = [x["name"] for x in json.loads(get(LIST.format(path="/"), fresh=True)[0]) if x.get("type") == "folder"]
            days = []
            for y in sorted(years):
                items = json.loads(get(LIST.format(path=f"/{y}"), fresh=(int(y) >= today.year - 1))[0])
                zips = [x["name"] for x in items if x.get("type") == "file" and x["name"].lower().endswith(".zip")]
                if zips:
                    for zname in zips:
                        url = DOWNLOAD.format(path=f"/{y}/{zname}")
                        z = zipfile.ZipFile(io.BytesIO(get(url)[0]))
                        names = sorted(n for n in z.namelist() if FILE.search(n) and FILE.search(n).group(1).endswith(HOUR))
                        for n in names:
                            frames.append(rows_of(z.read(n), os.path.basename(n), url, retrieved))
                            files += 1
                        log(f"  {y}/{zname}: {len(names)} files of {HOUR}")
                else:
                    d0 = dt.date(int(y), 1, 1)
                    d1 = min(dt.date(int(y), 12, 31), today.date())
                    days += [d0 + dt.timedelta(n) for n in range((d1 - d0).days + 1)]
        else:
            days = [today.date() - dt.timedelta(n) for n in range(args.days, -1, -1)]
        for day in days:
            if day == today.date() and today.hour * 100 + today.minute < 915:
                continue   # today's 09:00 file is not yet published
            path = daily_path(day)
            url = DOWNLOAD.format(path=path)
            try:
                content = get(url)[0]
            except ip.SourceGap:
                missing.append(str(day))
                continue
            frames.append(rows_of(content, os.path.basename(path), url, retrieved))
            files += 1
    except Ceiling as e:
        stopped = str(e)
        log(f"  {stopped}: the files read are written; the next run goes on from the saved files")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        ip.write_status(CONNECTOR, run_id, [dict(table=NAME, market="spp", status="failed", detail=tb.strip().splitlines()[-1][:300])]) if not args.out_dir else None
        log.close()
        return 1
    if not frames:
        print(f"{NAME} FAILED, no output file written: no file read ({len(missing)} days not on the portal)", file=sys.stderr)
        log.close()
        return 1
    t = pd.concat(frames, ignore_index=True)
    t = t.drop_duplicates(KEY, keep="last")
    header = [
        "Energy Research Warehouse (ERW): SPP's mid-term load forecast (MTLF) beside its averaged actual load, hourly, one "
        "file a day as published at 09:00 central time (session 10000, chain 701; predict data request 19)",
        "Shape: series (docs/datastandard.md v0). entity spp:<BAA> (SPP the footprint, SWPW its western area); variable "
        "load_forecast_mtlf_mw or load_actual_mw (MW); ts_utc the hour's start; vintage the hour the file was published "
        "(UTC); x_horizon_hours the hours from publication to the hour's start; x_interval_end_cpt SPP's hour ending in "
        "central time; x_file the file read.",
        "Revisions: kept, one row per vintage (each publication's forecast and actuals as printed).",
        f"Rows this run: {len(t)} from {files} files; days not on the portal: {', '.join(missing) if missing else 'none'}"
        + (f"; stopped: {stopped}" if stopped else ""),
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/spp_mtlf.py; {asked[0]} requests of {CEILING}",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        f"Source: {SOURCE} Southwest Power Pool (SPP), Marketplace portal, Mid-Term Load Forecast vs Actual, {PAGE}",
        f"  access: {DOWNLOAD.format(path='/<YYYY>/<MM>/<DD>/OP-MTLF-<YYYYMMDD>' + HOUR + '.csv')}; a finished year: "
        f"{DOWNLOAD.format(path='/<YYYY>/<YYYY>.zip')}",
        "License: public, with citation, not within a commercial publication (SPP's terms, https://www.spp.org/terms-conditions/).",
    ]
    cols = ip.SERIES_COLS + X_COLS
    ip.write_csv(t[cols], NAME, header, log, cols=cols, key=KEY)
    if not args.out_dir:
        ip.update_sources([dict(source=SOURCE, publisher="Southwest Power Pool (SPP)", report="Mid-Term Load Forecast vs Actual (MTLF)",
                                report_url=PAGE, document_list=LIST.format(path="/"), license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, [dict(table=NAME, market="spp", status="ok",
                                                 detail=f"{len(t)} rows from {files} files" + (f"; {stopped}" if stopped else ""))])
    print(f"{NAME}: {len(t):,} rows from {files} files, {t['entity'].nunique()} areas, {t['ts_utc'].min()} to "
          f"{t['ts_utc'].max()}; {asked[0]} requests" + (f"; {stopped}" if stopped else ""))
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
