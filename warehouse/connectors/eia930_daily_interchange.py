#!/usr/bin/env python3
"""Daily interchange between every pair of balancing authorities, EIA-930, 2019 to today (session 62, approved pull,
ceiling 3 million rows).

Energy Research Warehouse (ERW) connector. Writes one series table, history (not in the Supabase live set):

    warehouse/output/eia930_daily_interchange.csv    interchange_mwh, partition column ba (the reporting BA)

from the EIA API v2 route electricity/rto/daily-interchange-data (Form EIA-930, Hourly Electric Grid Monitor), every
directed pair EIA reports (fromba, toba), one row per pair and day, from 2019-01-01 to EIA's newest day. Hourly data for
the same span would be about 23 million rows, over the ceiling; the daily route is about 1 million.

    python warehouse/connectors/eia930_daily_interchange.py

EIA publishes each day in five time zones (Eastern, Central, Mountain, Pacific, Arizona); this table takes the Eastern
day for every pair (x_timezone), so every pair shares one day boundary; monthly and annual sums barely depend on it.
Sign (as the hourly table, docs/methods/grid_network.md): the reporting BA's net flow with the neighbour, MWh over the
day, positive when the reporting BA exports. Entity eia930:<FROM>-<TO>; ts_utc the day at 00:00:00Z (Decision 11).
Nothing is filled: a pair-day EIA does not report is absent.

Resumable: the pull goes a calendar month at a time; each month's rows are kept as a checkpoint
(warehouse/raw/eia930_daily_interchange/checkpoints/<YYYY-MM>.csv) once the month is past, so a restarted pull asks
only for the months it lacks. Every page EIA returns is saved under warehouse/raw/eia930_daily_interchange/<run_id>/.
Before paging, the rows the API reports for the whole span are counted, and the pull stops if they pass the ceiling.
The key comes from EIA_API_KEY and is removed from every URL, log line and row.
"""

import datetime as dt
import glob
import os
import sys
import time
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "eia930_daily_interchange"
ROUTE = "electricity/rto/daily-interchange-data"
API = "https://api.eia.gov/v2/"
PAGE_URL = "https://www.eia.gov/electricity/gridmonitor/"
SOURCE = "eia930:daily_interchange"
START = "2019-01-01"
TZ = "Eastern"
CEILING = 3_000_000
PAGE = 5000


def get(key, params, log, what):
    def call():
        r = requests.get(API + ROUTE + "/data/", params=[("api_key", key)] + params, timeout=180)
        if r.status_code != 200:
            raise RuntimeError(f"EIA {ROUTE} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
        return r
    return ip.with_retries(what, call, log)


def base(start, end):
    return [("frequency", "daily"), ("data[0]", "value"), ("facets[timezone][]", TZ), ("start", start), ("end", end),
            ("sort[0][column]", "period"), ("sort[0][direction]", "asc"), ("sort[1][column]", "fromba"),
            ("sort[1][direction]", "asc"), ("sort[2][column]", "toba"), ("sort[2][direction]", "asc")]


def month(key, m0, m1, log):
    """Every row of [m0, m1] (inclusive days), paged."""
    out, offset, total = [], 0, None
    while True:
        r = get(key, base(m0, m1) + [("offset", str(offset)), ("length", str(PAGE))], log, f"EIA daily interchange {m0} offset {offset}")
        body = r.json()["response"]
        rows = body.get("data", [])
        total = int(body.get("total", 0))
        url, retrieved = ip.redact(r.url), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for row in rows:
            row["_url"], row["_retrieved"] = url, retrieved
        out += rows
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.3)
    if len(out) != total:
        raise RuntimeError(f"{m0}: got {len(out)} rows, the API reported {total}")
    return pd.DataFrame(out)


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_daily_interchange_{run_id}.log"))
    results = []
    try:
        key = ip.load_key("EIA_API_KEY", log)
        ip.RAW.open("eia930_daily_interchange", run_id)
        ck = os.path.join(ip.RAW_DIR, "eia930_daily_interchange", "checkpoints")
        os.makedirs(ck, exist_ok=True)
        head = get(key, base(START, "2099-12-31") + [("length", "1")], log, "EIA daily interchange count").json()["response"]
        total = int(head.get("total", 0))
        log(f"EIA reports {total:,} rows ({TZ} days) from {START}; ceiling {CEILING:,}")
        if total > CEILING:
            raise RuntimeError(f"{total:,} rows would pass the {CEILING:,} ceiling: nothing pulled")
        last = get(key, [("frequency", "daily"), ("data[0]", "value"), ("facets[timezone][]", TZ), ("start", START),
                         ("sort[0][column]", "period"), ("sort[0][direction]", "desc"), ("length", "1")], log,
                   "EIA newest day").json()["response"]["data"][0]["period"]
        months = pd.period_range(START[:7], last[:7], freq="M")
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m")
        frames, pulled = [], 0
        for m in months:
            path = os.path.join(ck, f"{m}.csv")
            if os.path.exists(path) and str(m) < today:
                frames.append(pd.read_csv(path, dtype=str, keep_default_na=False))
                continue
            m0, m1 = m.start_time.strftime("%Y-%m-%d"), min(m.end_time.strftime("%Y-%m-%d"), last)
            df = month(key, m0, m1, log)
            pulled += len(df)
            log(f"  {m}: {len(df):,} rows")
            if len(df):
                df = df.astype(str)
                if str(m) < today and m.end_time.strftime("%Y-%m-%d") <= last:  # a past, complete month: a checkpoint
                    df.to_csv(path, index=False)
                frames.append(df)
        x = pd.concat(frames, ignore_index=True)
        x["value_n"] = pd.to_numeric(x["value"], errors="coerce")
        bad = int(x["value_n"].isna().sum())
        x = x[x["value_n"].notna()]
        if x.duplicated(["period", "fromba", "toba"]).any():
            raise RuntimeError("a pair-day appears twice")
        s = pd.DataFrame({
            "entity": "eia930:" + x["fromba"] + "-" + x["toba"], "variable": "interchange_mwh",
            "ts_utc": x["period"] + "T00:00:00Z", "value": x["value_n"].map(lambda v: repr(float(v))), "unit": "MWh", "freq": "P1D",
            "geo": "", "market": "", "node": "", "source": SOURCE, "source_url": x["_url"], "retrieved_at": x["_retrieved"],
            "vintage": "", "ba": x["fromba"].str.lower(), "x_to_ba": x["toba"].str.lower(), "x_timezone": TZ})
        cols = ip.SERIES_COLS + ["ba", "x_to_ba", "x_timezone"]
        header = [
            "Energy Research Warehouse (ERW): daily interchange between every pair of balancing authorities, EIA-930, from 2019 (session 62)",
            "Shape: series (docs/datastandard.md v0), partition column ba (the reporting BA, EIA's fromba); entity eia930:<FROM>-<TO>; "
            "interchange_mwh, MWh over the day, positive when the reporting BA exports to the neighbour (x_to_ba); ts_utc the day at "
            f"00:00:00Z (Decision 11); EIA's {TZ} day for every pair (x_timezone). Nothing filled: a pair-day EIA does not report is absent.",
            f"Rows: {len(s):,} of the {CEILING:,}-row ceiling, {START} to {last}; {bad} rows without a number not written.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_daily_interchange.py ({pulled:,} rows pulled this run; earlier months "
            "from checkpoints)",
            f"Run log: warehouse/output/logs/eia930_daily_interchange_{run_id}.log",
            "Raw files: warehouse/raw/eia930_daily_interchange/ (pages per run, month checkpoints; not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-930, daily interchange (API route {ROUTE}), {PAGE_URL}",
            "License: public domain (U.S. Government data, EIA).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rebuilt whole from the checkpoints and this run's months
        ip.write_csv(s[cols], NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration",
                                report="Form EIA-930, daily interchange (electricity/rto/daily-interchange-data)", report_url=PAGE_URL,
                                document_list=API + ROUTE, license="public", tables=[NAME])])
        msg = f"{len(s):,} pair-days, {s['entity'].nunique()} directed pairs, {START} to {last}; {pulled:,} rows pulled this run"
        log(msg)
        print(f"eia930_daily_interchange: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia930_daily_interchange FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia930_daily_interchange", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
