#!/usr/bin/env python3
"""Hourly interchange between balancing authorities, from EIA-930 (every BA pair EIA reports).

Energy Research Warehouse (ERW) connector, session 46 (Part A, session 42's prompt A1). Writes one series table,

    warehouse/output/eia930_all_interchange.csv    interchange_mw, partition column ba (the reporting BA)

from the EIA API v2 route electricity/rto/interchange-data, hourly. One entity per BA pair, eia930:<FROM>-<TO>, where
FROM is the reporting BA (EIA's fromba) and TO its neighbour (toba); x_to_ba repeats TO, lowercase, for filtering.
EIA's sign convention (docs/methods/grid_network.md): the value is the reporting BA's net flow with the neighbour,
positive when the reporting BA exports. Each pair is reported by both BAs, so the table holds both directions as EIA
publishes them; grid_network_links keeps one of each pair (its method records the rule).

    python warehouse/connectors/eia930_interchange.py --days 30      # the approved pull (last 30 days)
    python warehouse/connectors/eia930_interchange.py --days 3       # the daily run

Time: EIA's hourly period is the END of the hour in UTC (see eia930.py), so ts_utc = period minus one hour.
Completeness: per pair and UTC day, as the EIA-930 generation tables (session 16): a pair-day is written only when all
24 hours have a value; a pair-day with a missing hour is not written and is a gap row in run_status.csv. Nothing is
filled.
Ceiling (session 42 prompt): 150,000 rows. The connector counts the rows the API reports before it pages, and stops
without writing when the pull would pass the ceiling.
Paging and resume: one UTC day at a time, 5,000 rows a page, every page saved under warehouse/raw/eia930_interchange/
<run_id>/ with a manifest; each finished past day is kept as a checkpoint (warehouse/raw/eia930_interchange/
checkpoints/<YYYY-MM-DD>.csv) so an interrupted pull resumes from the days not yet checkpointed. The key comes from
EIA_API_KEY and is removed from every URL, log line and row.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eia930  # noqa: E402  (fetch_route, API, REPORT_PAGE: the EIA-930 connector's own code)
import iso_prices as ip  # noqa: E402

NAME = "eia930_all_interchange"
ROUTE = "electricity/rto/interchange-data"
SOURCE = f"eia:{ROUTE}"
VARIABLE = "interchange_mw"
CEILING = 150_000
COLS = ip.SERIES_COLS + ["ba", "x_to_ba"]
REPORT = ("Form EIA-930, Hourly Electric Grid Monitor: hourly interchange between balancing authorities",
          eia930.REPORT_PAGE, eia930.API + ROUTE + "/")


def checkpoint_dir():
    return os.path.join(ip.RAW_DIR, "eia930_interchange", "checkpoints")


def count_rows(key, start, end, log):
    """The rows the API holds for the window, from a length-0 request (its total)."""
    params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"), ("start", start), ("end", end),
              ("offset", "0"), ("length", "0")]

    def call():
        r = requests.get(eia930.API + ROUTE + "/data/", params=params, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"EIA {ROUTE} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
        return r
    r = ip.with_retries(f"EIA {ROUTE} count", call, log)
    total = int(r.json()["response"].get("total", 0))
    log(f"  {ROUTE} [{start}, {end}]: the API reports {total} rows")
    return total


def fetch(key, start, end, log):
    """Every row of the route for [start, end] hours, paged 5,000 at a time. eia930.fetch_route sorts by respondent,
    which this route has not (HTTP 400): here the sort is period, fromba, toba. Each row keeps its page's URL."""
    import time
    out, offset, total = [], 0, None
    while True:
        params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"), ("start", start), ("end", end),
                  ("sort[0][column]", "period"), ("sort[0][direction]", "asc"), ("sort[1][column]", "fromba"),
                  ("sort[1][direction]", "asc"), ("sort[2][column]", "toba"), ("sort[2][direction]", "asc"),
                  ("offset", str(offset)), ("length", str(eia930.PAGE))]

        def call():
            r = requests.get(eia930.API + ROUTE + "/data/", params=params, timeout=120)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {ROUTE} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {ROUTE} offset {offset}", call, log)
        body = r.json()["response"]
        rows = body.get("data", [])
        total = int(body.get("total", 0))
        url, retrieved = ip.redact(r.url), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for row in rows:
            row["_url"], row["_retrieved"] = url, retrieved
        out += rows
        log(f"  {ROUTE} offset {offset}: {len(rows)} rows (total {total})")
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.5)
    if total is not None and len(out) != total:
        raise RuntimeError(f"EIA {ROUTE}: got {len(out)} rows, API reported {total}")
    return pd.DataFrame(out)


def pull_day(d, key, log, current):
    cp = os.path.join(checkpoint_dir(), f"{d:%Y-%m-%d}.csv")
    if os.path.exists(cp) and not current:
        log(f"  {d:%Y-%m-%d}: from checkpoint {os.path.relpath(cp, ip.ROOT)}")
        return pd.read_csv(cp, dtype=str, keep_default_na=False)
    start = (d + pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    end = (d + pd.Timedelta(days=1)).strftime("%Y-%m-%dT%H")
    df = fetch(key, start, end, log)
    if not current and len(df):
        os.makedirs(checkpoint_dir(), exist_ok=True)
        df.astype(str).to_csv(cp, index=False)
    return df.astype(str) if len(df) else df


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 interchange connector (session 46)")
    ap.add_argument("--days", type=int, default=3, help="the last N complete UTC days")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_interchange_{run_id}.log"))
    ip.RAW.open("eia930_interchange", run_id)
    end = pd.Timestamp.now(tz="UTC").normalize()  # the end of yesterday, UTC
    start = end - pd.Timedelta(days=args.days)
    results, gaps = [], []
    log(f"ERW eia930_interchange run {run_id}; window [{ip.utc_iso(start)}, {ip.utc_iso(end)}); ceiling {CEILING} rows")
    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is empty")
        total = count_rows(key, (start + pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H"), end.strftime("%Y-%m-%dT%H"), log)
        if total > CEILING:
            raise RuntimeError(f"the window holds {total} rows, over the {CEILING} ceiling: nothing pulled")
        got = []
        for d in pd.date_range(start, end - pd.Timedelta(days=1), freq="D", tz="UTC"):
            current = d >= end - pd.Timedelta(days=4)  # EIA revises the latest days: pulled again, never checkpointed
            df = pull_day(d, key, log, current)
            if len(df):
                got.append(df)
        if not got:
            raise RuntimeError("no interchange rows in the window")
        raw = pd.concat(got, ignore_index=True)
        value = pd.to_numeric(raw["value"], errors="coerce")
        period_end = pd.to_datetime(raw["period"], format="%Y-%m-%dT%H", utc=True)
        rows = pd.DataFrame({"fromba": raw["fromba"].str.upper(), "toba": raw["toba"].str.upper(),
                             "interval_start": period_end - pd.Timedelta(hours=1), "value": value,
                             "source_url": raw["_url"], "retrieved_at": raw["_retrieved"]})
        rows = rows[(rows["interval_start"] >= start) & (rows["interval_start"] < end)].dropna(subset=["value"])
        rows = rows.drop_duplicates(["fromba", "toba", "interval_start"], keep="last")
        rows["day"] = rows["interval_start"].dt.floor("D")
        n = rows.groupby(["fromba", "toba", "day"])["value"].transform("size")
        keep = rows[n == 24]
        # one run_status row for the incomplete pair-days (there can be hundreds a day), naming the first 20
        short = rows[n != 24].groupby(["fromba", "toba", "day"]).size()
        if len(short):
            named = "; ".join(f"{f}-{t} {d:%Y-%m-%d} ({k} h)" for (f, t, d), k in list(short.items())[:20])
            gaps.append(dict(table=NAME, market="pairs", status="gap",
                             detail=f"{len(short)} pair-days with fewer than 24 hours not written: {named}"[:1000]))
            log(f"  {len(short)} incomplete pair-days not written")
        s = pd.DataFrame({
            "entity": "eia930:" + keep["fromba"] + "-" + keep["toba"], "variable": VARIABLE,
            "ts_utc": keep["interval_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "value": keep["value"].map(lambda v: f"{v:g}"), "unit": "MW", "freq": "PT1H", "geo": "", "market": "", "node": "",
            "source": SOURCE, "source_url": keep["source_url"], "retrieved_at": keep["retrieved_at"], "vintage": "",
            "ba": keep["fromba"].str.lower(), "x_to_ba": keep["toba"].str.lower()})[COLS]
        s["value"] = pd.to_numeric(s["value"])
        if len(s) > CEILING:
            raise RuntimeError(f"{len(s)} rows, over the {CEILING} ceiling: not written")
        pairs = s["entity"].nunique()
        header = [
            "Energy Research Warehouse (ERW): EIA-930 hourly interchange between balancing authorities, every pair EIA reports",
            "Shape: series (docs/datastandard.md v0), partition column ba (the reporting BA). One entity per pair, "
            "eia930:<FROM>-<TO>; x_to_ba is the neighbour. interchange_mw, MW, as EIA publishes it: positive when the "
            "reporting BA exports to the neighbour (docs/methods/grid_network.md). ts_utc is the hour's start.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_interchange.py via the EIA API v2",
            f"Run log: warehouse/output/logs/eia930_interchange_{run_id}.log (every API request, key removed)",
            f"Raw files: warehouse/raw/eia930_interchange/{run_id}/ (not in git; manifest.csv lists each file and URL); "
            "finished days kept in warehouse/raw/eia930_interchange/checkpoints/",
            f"Source: {SOURCE} {REPORT[0]}, {REPORT[1]}",
            f"  document list: {REPORT[2]}",
            f"Completeness per pair and UTC day: a pair-day with any hour missing is not written "
            f"({len(short)} in this run, counted in one gap row of warehouse/metadata/run_status.csv).",
            "Values: EIA states interchange in megawatthours per hour, which is the hour's mean MW; written as MW.",
        ]
        ip.write_csv(s, NAME, header, log, cols=COLS, key=["entity", "variable", "ts_utc"])
        ip.update_sources([{"source": SOURCE, "publisher": "U.S. Energy Information Administration (EIA)",
                            "report": REPORT[0], "report_url": REPORT[1], "document_list": REPORT[2],
                            "license": "public", "tables": [NAME]}])
        results.append(dict(table=NAME, market="all", status="ok",
                            detail=f"{len(s)} hours written for {pairs} pairs; {len(short)} incomplete pair-days left out"))
        print(f"eia930_interchange: {len(s)} rows, {pairs} pairs; {len(short)} incomplete pair-days left out")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"eia930_interchange {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("eia930_interchange", run_id, results + gaps)
    log.close()
    return 0 if all(r["status"] != "failed" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
