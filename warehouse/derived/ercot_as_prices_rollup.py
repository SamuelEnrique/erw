#!/usr/bin/env python3
"""ERCOT reserve prices by day and by month (session 148): the hourly history in two tables small enough to read fast.

Energy Research Warehouse (ERW). Method: docs/methods/ercot_as_prices_rollup.md. No request is made.

From ercot_as_prices (the day-ahead market clearing price for capacity of each reserve product, hourly, USD/MW-hour),
two tables, each in the series shape with one statistic a row (docs/datastandard.md, Decisions 39 and 44):

  ercot_as_prices_daily     for each product and local operating day (America/Chicago), five rows
  ercot_as_prices_monthly   for each product and local month, five rows

  mcpc_dam_mean              the mean of the hours held, USD/MW-hour, four decimals, half up
  mcpc_dam_min, mcpc_dam_max the lowest and the highest hourly price held, USD/MW-hour, as published
  mcpc_dam_hours             the count of hours held, unit count
  mcpc_dam_hours_in_day      the hours the local day has (24; 23 and 25 on the two clock-change days), unit count
  mcpc_dam_hours_in_month    the hours the local month has, unit count (the monthly table, in place of hours_in_day)

The clock is the hourly table's own: ERCOT publishes the hour ending in Central time and the hourly table writes a
(product, local day) only when every hour of it is there. ts_utc is the local day, written as its date at 00:00:00Z; a
month is its first local day at 00:00:00Z. The monthly mean is the mean of the month's hours, not of its daily means.

NEVER FILLED. A day or a month with fewer hours than it has is still written, from the hours held, and carries its
count: mcpc_dam_hours is then less than mcpc_dam_hours_in_day or mcpc_dam_hours_in_month. Nothing is scaled, spread
or interpolated. A product has no row for a day or a month it holds no hour of (ECRS begins on 2023-06-10): absence,
never a zero. The run log names each short day and each short month and the header counts them.

A (product, day) or (product, month) the input holds no hour of keeps the rows an earlier run wrote, as they were. A
row whose value did not change keeps its retrieved_at, so the loader rewrites only what is new (docs/datastandard.md).

    python warehouse/derived/ercot_as_prices_rollup.py
    python warehouse/derived/ercot_as_prices_rollup.py --in-dir <dir>    # read ercot_as_prices.csv there (read only)
    python warehouse/derived/ercot_as_prices_rollup.py --out-dir <dir>   # a trial: writes there, records nothing
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402  (four decimals half up, and a day as its date at 00:00:00Z)

NAME = "ercot_as_prices_rollup"
INPUT = "ercot_as_prices"
DAILY = "ercot_as_prices_daily"
MONTHLY = "ercot_as_prices_monthly"
SOURCE = "erw:ercot_as_prices_rollup"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md"
TZ = "America/Chicago"
VARIABLE = "mcpc_dam"
UNIT = "USD/MW-hour"
FREQ_IN = "PT1H"
# a table's name, its freq, the period a row is, the name of the row that says how many hours the period has
TABLES = {DAILY: ("P1D", "day", "hours_in_day"), MONTHLY: ("P1M", "month", "hours_in_month")}
# (the statistic's name, its column in the period's summary, its unit); the period's own hours come last
STATS = [("mean", "mean", UNIT), ("min", "vmin", UNIT), ("max", "vmax", UNIT), ("hours", "n", "count")]
COLS = ip.SERIES_COLS
KEY = ["entity", "variable", "ts_utc"]
PERIOD = ["entity", "ts_utc"]  # one product and one day or month: what a carried period is told by


def num(v):
    """A number as the table writes it: at most four decimals, half up."""
    return repr(pb.r4(v))


def read_input(in_dir, log):
    """The hourly table as a frame, one row per (product, hour), checked. Raises when it cannot be trusted."""
    path = os.path.join(in_dir, INPUT + ".csv")
    if not os.path.exists(path):
        raise RuntimeError(f"{INPUT} is not at {path}: nothing is written")
    df = ip.read_series(path, COLS)
    log(f"{INPUT}: {len(df)} rows, {df['ts_utc'].min()} to {df['ts_utc'].max()} ({path.replace(os.sep, '/')})")
    return check_input(df)


def check_input(df):
    """The checks every build makes of the hours it is given; the frame with ts (UTC) added."""
    if df.empty:
        raise RuntimeError(f"{INPUT} holds no row: nothing is written")
    for col, want in (("variable", VARIABLE), ("freq", FREQ_IN), ("unit", UNIT)):
        seen = set(df[col])
        if seen != {want}:
            raise RuntimeError(f"{INPUT}: {col} is {sorted(seen)} where only {want} is expected: nothing is written")
    if df["value"].isna().any():
        raise RuntimeError(f"{INPUT}: {int(df['value'].isna().sum())} hours have no price: nothing is written")
    if df.duplicated(KEY).any():
        raise RuntimeError(f"{INPUT}: {int(df.duplicated(KEY).sum())} duplicate (entity, variable, ts_utc) keys: nothing is written")
    df = df.assign(ts=pd.to_datetime(df["ts_utc"], utc=True))
    if (df["ts"].dt.minute != 0).any() or (df["ts"].dt.second != 0).any():
        raise RuntimeError(f"{INPUT}: an hour does not start on the hour: nothing is written")
    return df


def summarize(df, period):
    """One row per (product, local day) or (product, local month): its statistics, its hours held (n) and the hours
    the period has (expected). period: "day" or "month"."""
    local = df["ts"].dt.tz_convert(TZ).dt.tz_localize(None)
    start = local.dt.normalize() if period == "day" else local.dt.to_period("M").dt.to_timestamp()
    d = pd.DataFrame({"entity": df["entity"].values, "start": start.values, "value": df["value"].values})
    out = d.groupby(["entity", "start"], sort=True).agg(mean=("value", "mean"), vmin=("value", "min"), vmax=("value", "max"),
                                                       n=("value", "size")).reset_index()
    ident = df.drop_duplicates("entity")[["entity", "geo", "market", "node"]]
    if df.groupby("entity")[["geo", "market", "node"]].nunique().max().max() > 1:
        raise RuntimeError(f"{INPUT}: a product has more than one geo, market or node: nothing is written")
    out = out.merge(ident, on="entity", how="left")
    nxt = out["start"] + (pd.Timedelta(days=1) if period == "day" else pd.offsets.MonthBegin(1))
    # the hours between the period's first local instant and the next period's, on the clock that changes twice a year
    out["expected"] = ((nxt.dt.tz_localize(TZ) - out["start"].dt.tz_localize(TZ)) / pd.Timedelta(hours=1)).round().astype(int)
    if (out["n"] > out["expected"]).any():
        raise RuntimeError(f"{INPUT}: a {period} holds more hours than it has: nothing is written")
    return out


def rows_of(s, table, retrieved):
    """The table's rows for a summary: five rows per product and period."""
    freq, _, in_period = TABLES[table]
    ts = np.array([pb.day_ts(x.date()) for x in s["start"]], dtype=object)
    parts = []
    for name, col, unit in STATS + [(in_period, "expected", "count")]:
        value = [num(v) for v in s[col].values] if col == "mean" else [repr(float(v)) for v in s[col].values]
        parts.append(pd.DataFrame({
            "entity": s["entity"].values, "variable": f"{VARIABLE}_{name}", "ts_utc": ts, "value": value,
            "unit": unit, "freq": freq, "geo": s["geo"].values, "market": s["market"].values, "node": s["node"].values,
            "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": ""}, columns=COLS))
    return pd.concat(parts, ignore_index=True)


def merge_previous(new, old, seen, log):
    """Keep what an earlier run wrote for the periods the input holds no hour of, and an unchanged row's retrieved_at.
    seen: the (entity, ts_utc) of every period the input holds at least one hour of. (frame, rows carried)."""
    if old is None or old.empty:
        return new, 0
    old = old[COLS].assign(value=[repr(float(v)) for v in old["value"]])
    j = new.merge(old[KEY + ["value", "retrieved_at"]], on=KEY, how="left", suffixes=("", "_old"))
    same = (j["value"] == j["value_old"]).values
    new = new.assign(retrieved_at=np.where(same, j["retrieved_at_old"], j["retrieved_at"]))
    carried = old[~pd.MultiIndex.from_frame(old[PERIOD]).isin(seen)]
    log(f"  {int(same.sum())} rows unchanged (their retrieved_at kept), {len(new) - int(same.sum())} new or changed, "
        f"{len(carried)} carried from the last run's table (periods the input holds no hour of)")
    return pd.concat([new, carried], ignore_index=True), len(carried)


def header(table, run_id, notes, df, n_short, n_periods):
    freq, period, in_period = TABLES[table]
    first = df.groupby("entity")["ts_utc"].min()
    span = "; ".join(f"{e} from {t[:10]}" for e, t in first.items())
    what = "day" if period == "day" else "month"
    return [
        f"Energy Research Warehouse (ERW): ERCOT reserve (ancillary service) prices by {what}, day-ahead market clearing "
        "prices for capacity (derived)",
        "Shape: series (docs/datastandard.md v0). Derived by the ERW from the table named below; method "
        f"docs/methods/ercot_as_prices_rollup.md. Units: {UNIT} (US dollars per MW of capacity held for one hour); the "
        "counts of hours are unit count.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_as_prices_rollup.py",
        f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        f"Source: {SOURCE} ERW derived daily and monthly summary of ERCOT reserve prices "
        f"(docs/methods/ercot_as_prices_rollup.md), {METHOD_URL}",
        f"Derived from: {INPUT}",
        f"Five rows per reserve product and local {what} (America/Chicago, ERCOT's operating day: the clock the hourly "
        f"table writes its days by); ts_utc is the local {'day' if period == 'day' else 'month, its first day'}, written "
        f"as its date at 00:00:00Z. variable: {VARIABLE}_mean (the mean of the hours held, four decimals, half up), "
        f"{VARIABLE}_min and {VARIABLE}_max (the lowest and highest hourly price held, as published), {VARIABLE}_hours "
        f"(the count of hours held), {VARIABLE}_{in_period} (the hours the local {what} has"
        + (": 24, or 23 and 25 on the two clock-change days)." if period == "day" else ")."),
        f"Never filled: a {what} with fewer hours than it has is written from the hours held and carries its count "
        f"({VARIABLE}_hours less than {VARIABLE}_{in_period}); nothing is scaled or interpolated. {n_short} of the "
        f"{n_periods} product-{what}s built by this run are short (the run log names each). A product has no row for a "
        f"{what} it holds no hour of.",
        f"Products: {span}. Last {what}: {df['ts_utc'].max()[:10]}.",
        "License: public. Derived from public ERCOT reports (ercot:NP4-181-ER, ercot:NP4-188-CD).",
    ] + notes


def build_table(table, df, out_dir, log, run_id, retrieved):
    """Build one of the two tables as a frame and its header lines. Nothing is written here."""
    _, period, _ = TABLES[table]
    s = summarize(df, period)
    short = s[s["n"] != s["expected"]]
    for r in short.itertuples():
        log(f"  short {period}: {table} {r.entity} {str(r.start.date())[:10 if period == 'day' else 7]} holds {r.n} of {r.expected} hours")
    new = rows_of(s, table, retrieved)
    seen = pd.MultiIndex.from_arrays([s["entity"], [pb.day_ts(x.date()) for x in s["start"]]])
    path = os.path.join(out_dir, table + ".csv")
    old = ip.read_series(path, COLS) if os.path.exists(path) else None
    out, carried = merge_previous(new, old, seen, log)
    notes = []
    if carried:
        notes.append(f"{carried} rows are carried from the last run's table: periods the input on this machine holds no hour of.")
    out = out[COLS].sort_values(KEY).reset_index(drop=True)
    if out.duplicated(KEY).any():
        raise RuntimeError(f"{table}: duplicate (entity, variable, ts_utc) keys: nothing is written")
    if out.empty:
        raise RuntimeError(f"{table}: no row: nothing is written")
    return out, header(table, run_id, notes, out, len(short), len(s)), len(s), len(short), path


def build(in_dir, out_dir, log, run_id, retrieved):
    """Both tables, built whole in memory first and written only when both stand. [(table, rows, periods, short)]."""
    df = read_input(in_dir, log)
    built = [build_table(t, df, out_dir, log, run_id, retrieved) for t in TABLES]
    done = []
    for (out, head, n, n_short, path), table in zip(built, TABLES):
        ip._require_lock(path, f"writing {table}")  # session 59: a write into warehouse/output needs the data lock
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            for line in head + [f"File holds {len(out)} rows, rewritten whole by this run."]:
                f.write("# " + line + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(tmp, path)
        what = TABLES[table][1]
        log(f"  wrote {table}.csv: {len(out)} rows, {len(out.drop_duplicates(PERIOD))} product-{what}s of "
            f"{out['entity'].nunique()} products, {out['ts_utc'].min()[:10]} to {out['ts_utc'].max()[:10]}; {n_short} short")
        print(f"{table}.csv: rows={len(out)}")
        done.append((table, len(out), n, n_short))
    return done


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT reserve prices by day and by month (derived)")
    ap.add_argument("--in-dir", help="read ercot_as_prices.csv from this folder (another copy's warehouse/output); nothing is written there")
    ap.add_argument("--out-dir", help="a trial: write the two tables here and record nothing")
    a = ap.parse_args(argv)
    trial = bool(a.out_dir)
    in_dir = a.in_dir or ip.OUT_DIR
    out_dir = a.out_dir or ip.OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    if not trial:
        os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(out_dir if trial else ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        for table, rows, n, n_short in build(in_dir, out_dir, log, run_id, retrieved):
            what = TABLES[table][1]
            results.append(dict(table=table, market="derived", status="ok", detail=f"{rows} rows; {n_short} of {n} product-{what}s short"))
        if not trial:
            ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                                "report": "ERCOT reserve prices by day and by month (docs/methods/ercot_as_prices_rollup.md)",
                                "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": list(TABLES)}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results = [dict(table=t, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]) for t in TABLES]
    if not trial:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
