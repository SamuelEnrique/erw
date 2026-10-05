#!/usr/bin/env python3
"""Daily interchange between every pair of balancing authorities, EIA-930, 2019 to today (session 62, approved pull,
ceiling 3 million rows).

Energy Research Warehouse (ERW) connector. Writes one series table, history (not in the Supabase live set):

    warehouse/output/eia930_daily_interchange.csv    interchange_mwh, partition column ba (the reporting BA)

from the EIA API v2 route electricity/rto/daily-interchange-data (Form EIA-930, Hourly Electric Grid Monitor), every
directed pair EIA reports (fromba, toba), one row per pair and day, from 2019-01-01 to EIA's newest day. Hourly data for
the same span would be about 23 million rows, over the ceiling; the daily route is about 1 million.

    python warehouse/connectors/eia930_daily_interchange.py
    python warehouse/connectors/eia930_daily_interchange.py --days 5     # the daily run (session 114): the newest days, merged

Session 114, --days N: the table as it is, with the days from N days before today (UTC) to EIA's newest day asked for
again and merged in on (entity, variable, ts_utc): a day already held is replaced by what EIA reports now, a new day is
added, nothing else is touched. It never starts a table: where the table is not on the machine it asks EIA for nothing
and says so (a skip under warehouse/health.py), so a short table is never written over the history. It is how the
network's replay holds every day to EIA's newest (warehouse/run_daily.sh).

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


COLS = ip.SERIES_COLS + ["ba", "x_to_ba", "x_timezone"]


def rows_of(x):
    """The table's rows from EIA's (strings, with _url and _retrieved), and the count of rows without a number."""
    x = x.copy()
    x["value_n"] = pd.to_numeric(x["value"], errors="coerce")
    bad = int(x["value_n"].isna().sum())
    x = x[x["value_n"].notna()]
    if x.duplicated(["period", "fromba", "toba"]).any():
        raise RuntimeError("a pair-day appears twice")
    s = pd.DataFrame({
        "entity": "eia930:" + x["fromba"] + "-" + x["toba"], "variable": "interchange_mwh",
        "ts_utc": x["period"] + "T00:00:00Z", "value": x["value_n"].astype(float), "unit": "MWh", "freq": "P1D",
        "geo": "", "market": "", "node": "", "source": SOURCE, "source_url": x["_url"], "retrieved_at": x["_retrieved"],
        "vintage": "", "ba": x["fromba"].str.lower(), "x_to_ba": x["toba"].str.lower(), "x_timezone": TZ})
    return s[COLS], bad


def header_of(rows_line, retrieved_line, run_id):
    return [
        "Energy Research Warehouse (ERW): daily interchange between every pair of balancing authorities, EIA-930, from 2019 (session 62)",
        "Shape: series (docs/datastandard.md v0), partition column ba (the reporting BA, EIA's fromba); entity eia930:<FROM>-<TO>; "
        "interchange_mwh, MWh over the day, positive when the reporting BA exports to the neighbour (x_to_ba); ts_utc the day at "
        f"00:00:00Z (Decision 11); EIA's {TZ} day for every pair (x_timezone). Nothing filled: a pair-day EIA does not report is absent.",
        rows_line, retrieved_line,
        f"Run log: warehouse/output/logs/eia930_daily_interchange_{run_id}.log",
        "Raw files: warehouse/raw/eia930_daily_interchange/ (pages per run, month checkpoints; not in git)",
        f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-930, daily interchange (API route {ROUTE}), {PAGE_URL}",
        "License: public domain (U.S. Government data, EIA).",
    ]


def skip(reason):
    """Not an error: nothing was asked for. Under warehouse/health.py the exit is ERW_SKIP_EXIT (75), a recorded skip."""
    print(f"{NAME} SKIPPED: {reason}")
    return int(os.environ.get("ERW_SKIP_EXIT") or 0)


def data_rows(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f) - ip.header_rows(path) - 1


def recent(days, run_id, log, today=None):
    """Session 114, the daily run: the days from `days` before today (UTC) to EIA's newest, merged into the table held.
    Returns the message of the run. Raises when EIA returns nothing or the merge would leave fewer rows than were held."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    held = data_rows(path)
    key = ip.load_key("EIA_API_KEY", log)
    ip.RAW.open(NAME, run_id)
    today = today or dt.datetime.now(dt.timezone.utc).date()
    d0 = (today - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    df = month(key, d0, "2099-12-31", log)
    if not len(df):
        raise RuntimeError(f"EIA returned no row from {d0}: nothing written")
    s, bad = rows_of(df.astype(str))
    if held + len(s) > CEILING:
        raise RuntimeError(f"{held:,} rows held and {len(s):,} pulled would pass the {CEILING:,} ceiling: nothing written")
    last = s["ts_utc"].max()[:10]
    ip.write_csv(s, NAME, header_of(
        f"Rows: of the {CEILING:,}-row ceiling, from {START}; this run asked for {d0} to EIA's newest day ({last}); {bad} rows without a number not written.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/{NAME}.py --days {days} ({len(df):,} rows pulled this run and merged; "
        "the earlier days as the earlier runs wrote them)", run_id), log, cols=COLS, key=["entity", "variable", "ts_utc"])
    now = data_rows(path)
    if now < held:
        raise RuntimeError(f"the table held {held:,} rows and holds {now:,}: a merge never shrinks it")
    return f"{now:,} rows held ({now - held:,} new), {d0} to {last} asked again; {len(df):,} rows pulled this run"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, help="the daily run: only the days from this many before today, merged into the table held")
    a = ap.parse_args(argv)
    if a.days is not None and not os.path.exists(os.path.join(ip.OUT_DIR, NAME + ".csv")):
        return skip("the table is not on this machine; --days merges into the history and never starts it, so EIA was not asked")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    if a.days is not None:
        try:
            msg = recent(a.days, run_id, log)
            log(msg)
            print(f"{NAME}: {msg}")
            results.append(dict(table=NAME, market="all", status="ok", detail=msg))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"FAILED:\n{tb}")
            print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
        ip.write_status(NAME, run_id, results)
        log.close()
        return 0 if all(r["status"] == "ok" for r in results) else 1
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
        s, bad = rows_of(x)
        cols = COLS
        header = header_of(
            f"Rows: {len(s):,} of the {CEILING:,}-row ceiling, {START} to {last}; {bad} rows without a number not written.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_daily_interchange.py ({pulled:,} rows pulled this run; earlier months "
            "from checkpoints)", run_id)
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
