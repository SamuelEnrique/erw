#!/usr/bin/env python3
"""ERCOT hub prices by day (session 114): the price history in a form small enough for the site's database.

Energy Research Warehouse (ERW). Method: docs/methods/ercot_hub_prices_daily.md. No request is made.

For each trading hub, market and complete local operating day (America/Chicago) since 2015-01-01, seven rows. The
variable is <market>_<statistic>, with market da (day-ahead, hourly prices) or rt (real-time, 15-minute prices):

  da_mean, rt_mean                    the mean of the day's intervals, USD/MWh
  da_peak_mean, da_offpeak_mean, ...  the mean of the day's peak and off-peak intervals, USD/MWh. Peak is the price
                                      board's definition: hours ending 7 to 22 local, Monday to Friday, NERC holidays
                                      off-peak. A Saturday, a Sunday or a holiday has no peak hour and no peak row:
                                      absence, never a zero
  da_min, da_max, ...                 the day's lowest and highest interval price, USD/MWh, as published
  da_hours_below_zero, ...            hours priced below zero, unit count (a 15-minute interval counts 0.25)
  da_hours_above_200, ...             hours priced above 200 USD/MWh, counted the same way

The series shape, one statistic a row, and not one row a day with seven columns: the site's database keeps only the
standard columns of a series table (warehouse/supabase/load.py), so a statistic in a column of its own would not reach
the page the table is for (docs/datastandard.md, Decision 39).

Inputs: ercot_all_hub_prices_history (the yearly files, from 2015), then iso_dam_hub_prices and iso_rtm_hub_prices
(the daily run's tables, ERCOT's rows). An interval held by both is read once, from the daily run's table.

A day is written only when it holds every interval of its local day (24 hours day-ahead and 96 intervals real-time; 23
and 92 on the day clocks go forward, 25 and 100 on the day they go back). A day with a missing interval is left out,
never filled; the run log names each one. A day the inputs hold no interval of (the GitHub runner never holds the
yearly history, and a rolling table's oldest days leave it) keeps the rows an earlier run wrote, as they were. A row
whose value did not change keeps its retrieved_at, so the loader rewrites only new days (docs/datastandard.md).

    python warehouse/derived/ercot_hub_prices_daily.py
    python warehouse/derived/ercot_hub_prices_daily.py --out-dir <dir>   # a trial: writes there, records nothing
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
import price_board as pb  # noqa: E402  (the peak definition, the NERC holidays and the streamed reader)

NAME = "ercot_hub_prices_daily"
SOURCE = "erw:ercot_hub_prices_daily"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md"
TZ = "America/Chicago"
HISTORY = pb.HISTORY
ROLLING = {"ercot_dam": "iso_dam_hub_prices", "ercot_rtm": "iso_rtm_hub_prices"}
PREFIX = {"ercot_dam": "da", "ercot_rtm": "rt"}
FREQ = {"ercot_dam": "PT1H", "ercot_rtm": "PT15M"}
HOURS = {"PT1H": 1.0, "PT15M": 0.25}  # what one interval counts in x_hours_below_zero and x_hours_above_200
HIGH = 200.0  # USD/MWh
# (the statistic's name, its column in the day's summary, its unit)
STATS = [("mean", "mean", "USD/MWh"), ("peak_mean", "peak", "USD/MWh"), ("offpeak_mean", "offpeak", "USD/MWh"),
         ("min", "vmin", "USD/MWh"), ("max", "vmax", "USD/MWh"),
         ("hours_below_zero", "below", "count"), (f"hours_above_{int(HIGH)}", "above", "count")]
COLS = ip.SERIES_COLS
KEY = ["entity", "variable", "ts_utc"]
DAY = ["entity", "market", "ts_utc"]  # one hub, market and day: what a carried day is told by


def num(v):
    """A number as the table writes it: at most four decimals, half up."""
    return repr(pb.r4(v))


def read_inputs(log):
    """Every ERCOT hub interval the machine holds, one row per (market, node, ts_utc). (frame, inputs read, notes)."""
    parts, inputs, notes = [], [], []
    if os.path.exists(os.path.join(ip.OUT_DIR, HISTORY + ".csv")):
        h = pb.read_table(HISTORY)
        h = h[h["market"].isin(ROLLING)]
        log(f"{HISTORY}: {len(h)} rows, {h['ts_utc'].min()} to {h['ts_utc'].max()}")
        parts.append(h.assign(_order=0))
        inputs.append(HISTORY)
    else:
        notes.append(f"{HISTORY} is not on this machine: the days built from it are carried from the last run's table")
        log(notes[-1])
    for market, table in ROLLING.items():
        if not os.path.exists(os.path.join(ip.OUT_DIR, table + ".csv")):
            raise RuntimeError(f"{table} is not on this machine: nothing is written")
        r = pb.read_table(table, market=market)
        log(f"{table} ({market}): {len(r)} rows, {r['ts_utc'].min()} to {r['ts_utc'].max()}")
        parts.append(r.assign(_order=1))
        inputs.append(table)
    df = pd.concat(parts, ignore_index=True)
    for market, freq in FREQ.items():
        seen = set(df.loc[df["market"] == market, "freq"])
        if seen - {freq}:
            raise RuntimeError(f"{market}: intervals of {sorted(seen)} where {freq} is expected: nothing is written")
    if df["value"].isna().any():
        raise RuntimeError(f"{int(df['value'].isna().sum())} intervals have no price: nothing is written")
    both = df.duplicated(["market", "node", "ts_utc"], keep=False)
    if both.any():
        d = df[both].sort_values(["market", "node", "ts_utc", "_order"])
        spread = d.groupby(["market", "node", "ts_utc"])["value"].agg(lambda x: x.max() - x.min())
        notes.append(f"{len(spread)} intervals are held by the history and by the daily run's table; "
                     f"{int((spread > ip.TOLERANCE).sum())} of them differ by more than {ip.TOLERANCE} USD/MWh; "
                     "each is read from the daily run's table")
        log(notes[-1])
        df = df.sort_values("_order").drop_duplicates(["market", "node", "ts_utc"], keep="last")
    return df.drop(columns="_order"), inputs, notes


def summarize(df, holidays):
    """One row per (market, node, local day): the day's statistics, its intervals and how many the day should hold."""
    local = df["ts"].dt.tz_convert(TZ)
    day = local.dt.tz_localize(None).dt.normalize()
    peak = (local.dt.weekday < 5) & local.dt.hour.isin(list(pb.PEAK_HOURS)) & ~day.isin(pd.to_datetime(sorted(holidays)))
    hours = df["freq"].map(HOURS)
    d = pd.DataFrame({"market": df["market"].values, "node": df["node"].values, "day": day.values,
                      "value": df["value"].values,
                      "pk": np.where(peak, df["value"], np.nan), "op": np.where(peak, np.nan, df["value"]),
                      "below": np.where(df["value"] < 0, hours, 0.0), "above": np.where(df["value"] > HIGH, hours, 0.0)})
    g = d.groupby(["market", "node", "day"], sort=True)
    out = g.agg(mean=("value", "mean"), vmin=("value", "min"), vmax=("value", "max"), n=("value", "size"),
                peak=("pk", "mean"), offpeak=("op", "mean"), below=("below", "sum"), above=("above", "sum")).reset_index()
    ident = df.drop_duplicates(["market", "node"])[["market", "node", "entity", "geo", "freq"]]
    out = out.merge(ident, on=["market", "node"], how="left")
    start = out["day"].dt.tz_localize(TZ)
    end = (out["day"] + pd.Timedelta(days=1)).dt.tz_localize(TZ)
    out["expected"] = ((end - start) / pd.Timedelta(hours=1) / out["freq"].map(HOURS)).round().astype(int)
    return out


def rows_of(s, retrieved):
    """The table's rows for the complete days of a summary: one row per statistic the day has."""
    full = s[s["n"] == s["expected"]]
    ts = np.array([pb.day_ts(x.date()) for x in full["day"]], dtype=object)
    prefix = full["market"].map(PREFIX)
    parts = []
    for name, col, unit in STATS:
        has = full[col].notna().values  # a day without a peak hour has no peak mean: no row
        parts.append(pd.DataFrame({
            "entity": full["entity"].values[has], "variable": (prefix + "_" + name).values[has],
            "ts_utc": ts[has], "value": [num(v) for v in full[col].values[has]],
            "unit": unit, "freq": "P1D", "geo": full["geo"].values[has], "market": full["market"].values[has],
            "node": full["node"].values[has], "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": retrieved,
            "vintage": ""}, columns=COLS))
    return pd.concat(parts, ignore_index=True)


def merge_previous(new, old, seen, log):
    """Keep what an earlier run wrote for the days the inputs hold nothing of, and an unchanged row's retrieved_at.
    seen: the (entity, market, ts_utc) of every day the inputs hold at least one interval of. (frame, rows carried)."""
    if old is None or old.empty:
        return new, 0
    old = old[COLS]
    j = new.merge(old[KEY + ["value", "retrieved_at"]], on=KEY, how="left", suffixes=("", "_old"))
    same = (j["value"] == j["value_old"]).values
    new = new.assign(retrieved_at=np.where(same, j["retrieved_at_old"], j["retrieved_at"]))
    carried = old[~pd.MultiIndex.from_frame(old[DAY]).isin(seen)]
    log(f"  {int(same.sum())} rows unchanged (their retrieved_at kept), {len(new) - int(same.sum())} new or changed, "
        f"{len(carried)} carried from the last run's table (days the inputs hold no interval of)")
    return pd.concat([new, carried], ignore_index=True), len(carried)


def header(run_id, inputs, notes, df, left_out):
    days = df.drop_duplicates(DAY).groupby("market")["ts_utc"].agg(["size", "min", "max"])
    span = "; ".join(f"{m} {int(r['size'])} hub-days, {r['min'][:10]} to {r['max'][:10]}" for m, r in days.iterrows())
    return [
        "Energy Research Warehouse (ERW): ERCOT trading hub prices by day, day-ahead and real-time, from 2015 (derived)",
        "Shape: series (docs/datastandard.md v0). Derived by the ERW from the tables named below; method "
        "docs/methods/ercot_hub_prices_daily.md. Units: USD/MWh; the hours below zero and above 200 are unit count.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_hub_prices_daily.py",
        f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        f"Source: {SOURCE} ERW derived daily summary of ERCOT hub prices (docs/methods/ercot_hub_prices_daily.md), {METHOD_URL}",
        "Derived from: " + "; ".join(inputs),
        "Seven rows per hub, market and complete local operating day (America/Chicago); ts_utc is the local day, written "
        "as its date at 00:00:00Z. variable is <market>_<statistic>: market da (day-ahead, hourly prices) or rt "
        "(real-time, 15-minute prices); statistic mean, peak_mean, offpeak_mean, min, max, hours_below_zero, "
        f"hours_above_{int(HIGH)}. Peak: hours ending 7 to 22 local, Monday to Friday, NERC holidays off-peak (the price "
        "board's definition); a day without a peak hour has no peak_mean row. hours_below_zero: hours priced below 0; "
        f"hours_above_{int(HIGH)}: hours priced above {HIGH:g} USD/MWh; a 15-minute interval counts 0.25.",
        f"Days: {span}. A day with a missing interval is left out, never filled: {left_out} hub-days of the inputs "
        "are left out (the run log names each).",
    ] + notes


def build(out_dir, log, run_id, retrieved):
    df, inputs, notes = read_inputs(log)
    years = range(int(df["ts_utc"].min()[:4]) - 1, int(df["ts_utc"].max()[:4]) + 2)
    s = summarize(df, pb.nerc_holidays(years))
    short = s[s["n"] != s["expected"]]
    for r in short.itertuples():
        log(f"  left out: {r.market} {r.node} {r.day.date()} holds {r.n} of {r.expected} intervals")
    new = rows_of(s, retrieved)
    seen = pd.MultiIndex.from_arrays([s["entity"], s["market"], [pb.day_ts(x.date()) for x in s["day"]]])
    path = os.path.join(out_dir, NAME + ".csv")
    old = ip.read_series(path, COLS) if os.path.exists(path) else None
    out, carried = merge_previous(new, old, seen, log)
    if carried:
        notes = notes + [f"{carried} rows are carried from the last run's table: days the inputs on this machine hold "
                         "no interval of."]
    out = out[COLS].sort_values(KEY).reset_index(drop=True)
    if out.duplicated(KEY).any():
        raise RuntimeError(f"{NAME}: duplicate (entity, variable, ts_utc) keys")
    if out.empty:
        raise RuntimeError(f"{NAME}: no complete day: nothing is written")
    head = header(run_id, inputs + ([NAME] if carried else []), notes, out, len(short))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in head + [f"File holds {len(out)} rows, rewritten whole by this run."]:
            f.write("# " + line + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    log(f"  wrote {NAME}.csv: {len(out)} rows, {len(out.drop_duplicates(DAY))} hub-days of {out['entity'].nunique()} hubs, "
        f"{out['ts_utc'].min()[:10]} to {out['ts_utc'].max()[:10]}; {len(short)} hub-days left out")
    print(f"{NAME}.csv: rows={len(out)}")
    return out, len(short)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT hub prices by day (derived)")
    ap.add_argument("--out-dir", help="a trial: write the table here and record nothing")
    a = ap.parse_args(argv)
    trial = bool(a.out_dir)
    out_dir = a.out_dir or ip.OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(out_dir if trial else ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        out, left = build(out_dir, log, run_id, retrieved)
        results.append(dict(table=NAME, market="derived", status="ok", detail=f"{len(out)} rows; {left} hub-days left out"))
        if not trial:
            ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                                "report": "ERCOT hub prices by day (docs/methods/ercot_hub_prices_daily.md)",
                                "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not trial:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
