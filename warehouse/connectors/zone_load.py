#!/usr/bin/env python3
"""Hourly load by zone or area: what the four connectors of session 138 share.

Energy Research Warehouse (ERW). Each operator that publishes its hourly load by region has a connector of its own
(ercot_zone_load.py, nyiso_zone_load.py, isone_zone_load.py, caiso_area_load.py): its report, its route, its terms
quoted, its parsing. Four connectors need the same frame, so it is here once (CLAUDE.md: no shared code until two
connectors need it). The count against a ceiling, the test for a kept raw file and the request header are session
136's (dam_cleared.py) and are used from there, not copied; what is added here is what a load table needs: a start
day for the history, the placing of local hours at a clock change, and the table's header.

Every table is a series, one row a zone (or area) and hour:

    entity    <iso>:<zone or area>, the operator's own name (ISO-NE: the name its price tables use, so the two join);
              the operator's own total, where its file gives one, is <iso>:system
    variable  load
    value     the operator's own figure for the hour, MW over the hour
    freq      PT1H; ts_utc is the hour's start, UTC
    node      the name of the operator's column, sheet or area the value is read from

An hour the operator does not give is not written. Nothing is filled, summed across zones or estimated: a total is
written only where the operator's own file holds it. An hour that cannot be placed in UTC (a clock hour that does not
exist in spring, or the repeated autumn hour held once only) is not written and is counted in the log and the header.
The table is merged into the one already held (iso_prices.write_csv), so a weekly run adds to the history.

MISO is paused (warehouse/metadata/paused_sources.csv) and PJM's data is licensed: neither has a connector here.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

VARIABLE = "load"
UA = dc.UA
Counter, Ceiling, reused = dc.Counter, dc.Ceiling, dc.reused       # session 136's, used as they are
PIECE = ["entity", "node", "ts", "value"]                          # what a parser returns: one row a zone and hour, ts in UTC


def to_utc(local, tz, second=None):
    """Local hour starts (naive: the operator's hour ending less one hour) as (UTC, NaT where an hour cannot be
    placed; how many hours were placed by their end).

    AUTUMN. The hour the clock repeats is placed when the file holds it twice: the first is daylight time, the second
    standard time. second: the rows the operator itself marks as the second (ISO-NE's "02X"); without it the order of
    the rows says which is which. Held once, that hour could be either and is not placed.

    SPRING. The day has 23 hours and operators label the one after the change in two ways. ERCOT's files from 2017
    name it by its number (hour ending 02:00, then 04:00): its start, 01:00 standard time, exists and places it.
    ERCOT's files of 2015 and 2016 and ISO-NE's workbooks name it by the clock at its end (hour ending 01:00, then
    03:00): that hour ended at 03:00 daylight time and so began at 01:00 standard time, but "03:00 less one hour" is
    02:00, a clock time that day never had. Such a line is placed by its end: the end's instant, less one hour. Both
    labels then give the same hour, and a file that held both (24 lines that day) would give one hour twice, which
    rows() refuses."""
    idx = pd.DatetimeIndex(pd.to_datetime(list(local)))
    key = pd.Series(idx)
    if second is None:
        second = key.duplicated(keep="first").values
        twice = key.duplicated(keep=False).values
    else:
        second = np.asarray(second, dtype=bool)
        twice = key.isin(key[second]).values
    placed = idx.tz_localize(tz, ambiguous=~second, nonexistent="NaT")
    gap = np.asarray(placed.isna())                                    # the start is a clock time the spring day never had
    repeated = np.asarray(idx.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").isna()) & ~gap
    utc = np.array(placed.tz_convert("UTC").tz_localize(None), dtype="datetime64[ns]")
    if gap.any():
        ends = (idx[gap] + pd.Timedelta(hours=1)).tz_localize(tz, ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
        utc[gap] = np.array((ends - pd.Timedelta(hours=1)).tz_localize(None), dtype="datetime64[ns]")
    utc[repeated & ~twice] = np.datetime64("NaT")
    return pd.Series(pd.DatetimeIndex(utc).tz_localize("UTC")), int(gap.sum())


def once(df, log, what):
    """A zone's hour given twice: one row is kept when the rows agree, none when they differ (nothing is chosen)."""
    dup = df.duplicated(["entity", "ts"], keep=False)
    if not dup.any():
        return df, 0
    agree = df[dup].groupby(["entity", "ts"])["value"].transform("nunique") == 1
    differ = dup.copy()
    differ[dup] = ~agree.values
    n = int(df[differ][["entity", "ts"]].drop_duplicates().shape[0])
    log(f"  {what}: {int(dup.sum())} rows give a zone's hour more than once; {n} such hours differ between their rows and are not written")
    return df[~differ].drop_duplicates(["entity", "ts"]), n


def rows(spec, piece, url, rec):
    """A parser's piece as rows of the table. A blank value is not a quantity: the row is not written."""
    p = piece[pd.notna(piece["value"]) & pd.notna(piece["ts"])]
    dup = p.duplicated(["entity", "ts"])
    if dup.any():
        raise RuntimeError(f"{int(dup.sum())} zone hours given twice in {url}, for example {p.loc[dup, 'entity'].iloc[0]} at {p.loc[dup, 'ts'].iloc[0]}")
    return pd.DataFrame({
        "entity": p["entity"].values, "variable": VARIABLE, "ts_utc": pd.DatetimeIndex(p["ts"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": p["value"].astype(float).values, "unit": "MW", "freq": "PT1H", "geo": spec["geo"], "market": f"{spec['iso']}_load",
        "node": p["node"].values, "source": spec["source"], "source_url": url, "retrieved_at": rec["retrieved_at"], "vintage": ip.vintage_of(rec)},
        columns=ip.SERIES_COLS)


def run(spec, pull, argv=None):
    """One connector's run. spec: iso, name, connector, source, entry (the registry's row), geo, days (the days asked
    for by default), ceiling (rows a run may read), stale_days, what (the header's first line), notes (header lines),
    license (the header's license line). pull(log, first, counter) returns (a list of rows() frames, notes for the
    header); first is the first local day asked for."""
    ap = argparse.ArgumentParser(description=spec["what"])
    ap.add_argument("--days", type=int, default=spec["days"], help=f"how many days back to ask for (default {spec['days']})")
    ap.add_argument("--from", dest="first", help="the history: the first day to ask for, YYYY-MM-DD (give --ceiling with it)")
    ap.add_argument("--ceiling", type=int, default=spec["ceiling"], help=f"the rows this run may read (default {spec['ceiling']:,})")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name, connector = spec["name"], spec["connector"]
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{connector}_{run_id}.log"))
    results = []
    held = ip.paused(spec["iso"])
    if held:
        log(f"{spec['iso']} is paused since {held.get('paused_on')}: no request is made")
        print(f"{connector}: {spec['iso']} is paused; no request made")
        results.append(dict(table=name, market="all", status="skipped", detail="the publisher's pulls are paused"))
        ip.write_status(connector, run_id, results)
        log.close()
        return 0
    ip.RAW.open(connector, run_id)
    counter = Counter(args.ceiling)
    first = pd.Timestamp(args.first) if args.first else pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=args.days)
    try:
        pieces, found = pull(log, first, counter)
        pieces = [p for p in pieces if len(p)]
        if not pieces:
            raise RuntimeError("the operator answered no hour")
        s = pd.concat(pieces, ignore_index=True)
        s = s.drop_duplicates(ip.SERIES_KEY, keep="first")       # two files may hold the same hour (a window's edge); the newer file is read first
        age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(s["ts_utc"].max())).days
        if age > spec["stale_days"]:
            raise RuntimeError(f"the newest hour the operator gave is {s['ts_utc'].max()}, {age} days old (limit {spec['stale_days']})")
        header = [
            f"Energy Research Warehouse (ERW): {spec['what']} (session 138)",
            "Shape: series (docs/datastandard.md v0). variable load: the operator's own figure for the zone (or area) and hour, MW over the hour; freq PT1H, ts_utc the hour's start in UTC. "
            "An hour the operator does not give is not written; nothing is filled, summed across zones or estimated. The table is merged into the one held.",
            *spec["notes"],
            *[f"This run: {n}" for n in found],
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{connector}.py",
            f"Run log: warehouse/output/logs/{connector}_{run_id}.log",
            f"Raw files: warehouse/raw/{connector}/ (not in git)",
            f"Source: {spec['source']} {spec['entry']['publisher']}, {spec['title']}, {spec['entry']['report_url']}",
            f"  access: {spec['entry']['document_list']}",
            f"Rows read from the operator in this run: {counter.read:,} (this run's ceiling {args.ceiling:,}). Rows written by this run: {len(s):,}, {s['ts_utc'].min()} to {s['ts_utc'].max()}.",
            spec["license"],
        ]
        ip.write_csv(s[ip.SERIES_COLS], name, header, log)
        if not args.out_dir:
            ip.update_sources([spec["entry"]])
        results.append(dict(table=name, market="all", status="ok", detail=f"{len(s):,} rows; {counter.read:,} rows read"))
        print(f"{name}: {len(s):,} rows, {s['entity'].nunique()} entities, {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}; rows read {counter.read:,}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{connector} FAILED, no output file written: {tb.strip().splitlines()[-1]}; rows read {counter.read:,}", file=sys.stderr)
        results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(connector, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1
