#!/usr/bin/env python3
"""ERCOT peak premium metrics for every settlement point the node pull holds, by calendar month (session 7019, chain 301;
done-line request 35).

Energy Research Warehouse (ERW). Writes warehouse/output/ercot_peak_premium_node_monthly.csv: the metrics of
docs/methods/ercot_peak_premium.md ("Metrics": the three blocks by local hour of interval start, the five-number
summaries, the 99.9th percentile, the spreads, the counts) for each node of ercot_rtm_node_prices (ERCOT's 15-minute
real-time settlement point prices, NP6-905-CD, the data machine's daily pull, held from 28 September 2026), by
calendar month in America/Chicago from October 2026, the first whole month. The rules are the hub table's own:
ercot_peak_premium.metrics and ercot_peak_premium.expected. A month that has ended is written for a node only when it
holds every interval of the month; the month in progress is written as far as it is held, and n_intervals says how
far. So that a named node's 16:00 to 21:00 median and spread can be set beside a hub's.

    python warehouse/lock.py run --task "node peak premium" -- <python> warehouse/derived/ercot_node_peak_premium.py
    python warehouse/derived/ercot_node_peak_premium.py --out-dir DIR      # a trial: nothing in warehouse/output

No request is made and no model is called.
"""
import argparse
import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "connectors"))
import ercot_peak_premium as pp  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "ercot_peak_premium_node_monthly"
INPUT = "ercot_rtm_node_prices"
FIRST_MONTH = "2026-10"
SOURCE = "erw:ercot_node_peak_premium"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md"


def read_nodes(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for ln in f:
            if not ln.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value", "node"], dtype=str,
                    keep_default_na=False)   # header lines skipped by count, never comment=
    d = d[(d["variable"] == "spp_rtm") & (d["value"] != "")].copy()
    d["value"] = d["value"].astype(float)
    d = d.drop_duplicates(["entity", "ts_utc"])
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    d["local"] = d["ts"].dt.tz_convert(pp.TZ)
    return d


def build(d, log):
    last = d["ts"].max()
    rows, skipped = [], []
    first = pd.Timestamp(FIRST_MONTH + "-01").tz_localize(pp.TZ)
    d = d[d["local"] >= first]
    ym = d["local"].dt.strftime("%Y-%m")
    for (entity, month), g in d.groupby([d["entity"], ym]):
        ms = pd.Timestamp(month + "-01").tz_localize(pp.TZ)
        me = (ms.tz_localize(None) + pd.offsets.MonthBegin(1)).tz_localize(pp.TZ)
        ended = me.tz_convert("UTC") <= last
        if ended and len(g) != pp.expected(ms, me):
            skipped.append(f"{entity} {month}: {len(g)} of {pp.expected(ms, me)} intervals")
            continue
        for var, (v, unit) in pp.metrics(g["value"].to_numpy(float), g["local"].dt.hour.to_numpy()).items():
            rows.append((entity, g["node"].iloc[0], var, f"{month}-01T00:00:00Z", v, unit))
    log(f"  {len(rows):,} rows, {d['entity'].nunique()} nodes, months from {FIRST_MONTH}; {len(skipped)} node-months left out"
        + (f" (e.g. {skipped[0]})" if skipped else ""))
    return rows, last, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT peak premium metrics per node and month (session 7019)")
    ap.add_argument("--out-dir", help="a trial: the table and its log under this folder")
    ap.add_argument("--inputs", help="the folder holding ercot_rtm_node_prices.csv (default warehouse/output)")
    a = ap.parse_args(argv)
    inputs = a.inputs or ip.OUT_DIR   # read before a trial moves the output folder
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    src = os.path.join(inputs, INPUT + ".csv")
    try:
        d = read_nodes(src)
        rows, last, skipped = build(d, log)
        if not rows:
            raise RuntimeError("no node-month held")
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        df = pd.DataFrame(rows, columns=["entity", "node", "variable", "ts_utc", "value", "unit"])
        s = pd.DataFrame({"entity": df["entity"], "variable": df["variable"], "ts_utc": df["ts_utc"], "value": df["value"].round(6),
                          "unit": df["unit"], "freq": "P1M", "geo": "US-TX", "market": "ercot_rtm", "node": df["node"],
                          "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": got, "vintage": ""}
                         ).sort_values(["entity", "variable", "ts_utc"])[ip.SERIES_COLS]
        header = [
            "Energy Research Warehouse (ERW): ERCOT peak premium metrics per settlement point and calendar month (derived)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc labels the calendar month in America/Chicago "
            "(YYYY-MM-01 at 00:00:00Z); the month itself is local time.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_node_peak_premium.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {SOURCE} ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md), {METHOD_URL}",
            f"Derived from: {INPUT}",
            "Method: the hub table's own (ercot_peak_premium.metrics): blocks by local hour of interval start, overnight h>=21 "
            "or h<12, midday 12<=h<16, peak 16<=h<21; percentiles numpy default (linear); no cap or exclusion. Months from "
            f"{FIRST_MONTH}; an ended month only with every interval of it ({len(skipped)} node-months left out this run).",
            f"Last input interval: {ip.utc_iso(last)}; the month in progress is partial (n_intervals says how far).",
            "License: public (ERCOT's settlement point prices, as ercot_rtm_node_prices).",
        ]
        ip.write_csv(s, NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="ERCOT peak premium metrics per settlement point (docs/methods/ercot_peak_premium.md)",
                                report_url=METHOD_URL, document_list="docs/methods/ercot_peak_premium.md", license="public",
                                tables=[NAME])])
        print(f"{NAME}: {len(s):,} rows written")
        rc = 0
    except Exception as exc:
        log(f"FAILED: {exc!r}")
        print(f"{NAME} FAILED: {exc!r}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
