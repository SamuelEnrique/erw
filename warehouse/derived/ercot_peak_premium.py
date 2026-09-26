#!/usr/bin/env python3
"""ERCOT peak premium: derived annual and monthly metrics per hub.

Energy Research Warehouse (ERW), session 9. Implements
docs/methods/ercot_peak_premium.md exactly: time-of-day blocks by local
(America/Chicago) hour of interval start, per-block min, Q1, median, Q3 and
max, peak-block IQR, worst-interval multiple, peak-minus-midday median spread,
all-intervals IQR, and counts of intervals at or above 1,000 USD/MWh and at or
below 0. Percentiles are numpy's default (linear). No cap or exclusion.

Input: the ERCOT real-time hub price tables in warehouse/output,
ercot_rtm_hub_prices_<year> (history, session 8) and ercot_rtm_hub_prices
(live). Output, through the merge writer, two derived `series` tables:

    ercot_peak_premium_annual    freq P1Y, ts_utc YYYY-01-01T00:00:00Z labels ERCOT operating year YYYY
    ercot_peak_premium_monthly   freq P1M, ts_utc YYYY-MM-01T00:00:00Z labels the local calendar month

    python warehouse/derived/ercot_peak_premium.py

A past year or month must be complete (every 15-minute interval of the local
period), or nothing is written. The current year and month are partial;
n_intervals says how many intervals they hold. License: a derived table
inherits the most restrictive license of its inputs (docs/datastandard.md
Decision 23), read from warehouse/metadata/sources.csv.

In CI (GITHUB_ACTIONS=true) the yearly ERCOT history tables are not present,
because tables are not in git (session 9). Session 10 ruling (3): there the
script skips with a warning, writes nothing, records status "skipped" (which
does not count toward a failure streak) and exits 0. Anywhere else, missing
inputs still fail loudly.
"""

import datetime as dt
import glob
import os
import re
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

TZ = "America/Chicago"
METHOD = "docs/methods/ercot_peak_premium.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md"
SOURCE = "erw:ercot_peak_premium"
FIRST_YEAR = 2015
SCARCITY = 1000.0
BLOCKS = {  # local hour of interval start -> block (docs/methods/ercot_peak_premium.md)
    "overnight": lambda h: (h >= 21) | (h < 12),
    "midday": lambda h: (h >= 12) & (h < 16),
    "peak": lambda h: (h >= 16) & (h < 21),
}
STATS = ["min", "q1", "median", "q3", "max"]
USD = "USD/MWh"


def pct(v, p):
    return float(np.percentile(v, p))  # numpy default: linear interpolation


def five(v):
    return {"min": float(v.min()), "q1": pct(v, 25), "median": pct(v, 50), "q3": pct(v, 75),
            "max": float(v.max())}


def metrics(prices, hours):
    """{variable: (value, unit)} for one hub and one period."""
    out = {}
    for b, rule in BLOCKS.items():
        v = prices[rule(hours)]
        if len(v) == 0:
            raise RuntimeError(f"no intervals in the {b} block")
        for k, x in five(v).items():
            out[f"{b}_{k}"] = (x, USD)
    for k, x in five(prices).items():
        out[f"all_{k}"] = (x, USD)
    peak, mid = prices[BLOCKS["peak"](hours)], prices[BLOCKS["midday"](hours)]
    med, p999 = pct(prices, 50), pct(prices, 99.9)
    if med == 0:
        raise RuntimeError("median is 0: the worst-interval multiple is undefined")
    out["all_p999"] = (p999, USD)
    out["peak_iqr"] = (pct(peak, 75) - pct(peak, 25), USD)
    out["all_iqr"] = (pct(prices, 75) - pct(prices, 25), USD)
    out["worst_interval_multiple"] = (p999 / med, "ratio")
    out["peak_minus_midday_median"] = (pct(peak, 50) - pct(mid, 50), USD)
    out["n_scarcity"] = (float((prices >= SCARCITY).sum()), "count")
    out["n_negative"] = (float((prices <= 0).sum()), "count")
    out["n_intervals"] = (float(len(prices)), "count")
    return out


def load(log):
    """All real-time hub rows from the history and live tables, with the input table names."""
    names = sorted(os.path.splitext(os.path.basename(p))[0]
                   for p in glob.glob(os.path.join(ip.OUT_DIR, "ercot_rtm_hub_prices_*.csv"))
                   if re.fullmatch(r"ercot_rtm_hub_prices_\d{4}", os.path.splitext(os.path.basename(p))[0]))
    names.append("ercot_rtm_hub_prices")
    frames = []
    for n in names:
        path = os.path.join(ip.OUT_DIR, n + ".csv")
        if not os.path.exists(path):
            raise RuntimeError(f"input table {n} is missing; see warehouse/output/README.md to rebuild it")
        d = ip.read_series(path)
        if set(d["variable"]) != {"spp_rtm"} or set(d["unit"]) != {USD} or set(d["freq"]) != {"PT15M"}:
            raise RuntimeError(f"{n}: not 15-minute spp_rtm in USD/MWh")
        d["table"] = n
        frames.append(d[["node", "ts_utc", "value", "source", "table"]])
        log(f"  input {n}: {len(d)} rows, {d['ts_utc'].min()} to {d['ts_utc'].max()}")
    d = pd.concat(frames, ignore_index=True)
    dup = d.duplicated(["node", "ts_utc"], keep=False)
    if dup.any():
        raise RuntimeError(f"{int(dup.sum())} rows repeat a (hub, interval) across the input tables")
    d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    d["local"] = d["ts"].dt.tz_convert(TZ)
    return d, names


def expected(start_local, end_local):
    """Quarter hours in [start, end) local, counted in real (UTC) time."""
    return int((end_local.tz_convert("UTC") - start_local.tz_convert("UTC")) / pd.Timedelta("15min"))


def build(d, log):
    now_local = pd.Timestamp.now(tz=TZ)
    last = d["ts"].max()
    annual, monthly = [], []
    d = d[d["local"].dt.year >= FIRST_YEAR]
    for hub, g in d.groupby("node"):
        g = g.sort_values("ts")
        years = g["local"].dt.year
        months = g["local"].dt.month
        for y in range(FIRST_YEAR, now_local.year + 1):
            gy = g[years == y]
            if gy.empty:
                raise RuntimeError(f"{hub} {y}: no intervals")
            s = pd.Timestamp(f"{y}-01-01").tz_localize(TZ)
            e = pd.Timestamp(f"{y + 1}-01-01").tz_localize(TZ)
            full = expected(s, e)
            if y < now_local.year and len(gy) != full:
                raise RuntimeError(f"{hub} {y}: {len(gy)} intervals, expected {full}")
            for var, (v, unit) in metrics(gy["value"].to_numpy(float), gy["local"].dt.hour.to_numpy()).items():
                annual.append((hub, var, f"{y}-01-01T00:00:00Z", v, unit))
            for m in range(1, 13):
                gm = gy[months[years == y] == m]
                ms = pd.Timestamp(f"{y}-{m:02d}-01").tz_localize(TZ)
                me = (ms.tz_localize(None) + pd.offsets.MonthBegin(1)).tz_localize(TZ)
                if gm.empty:
                    if ms > now_local or ms.tz_convert("UTC") > last:
                        continue  # a month that has not happened or has no data yet
                    raise RuntimeError(f"{hub} {y}-{m:02d}: no intervals")
                if me.tz_convert("UTC") <= last and len(gm) != expected(ms, me):
                    raise RuntimeError(f"{hub} {y}-{m:02d}: {len(gm)} intervals, expected {expected(ms, me)}")
                for var, (v, unit) in metrics(gm["value"].to_numpy(float), gm["local"].dt.hour.to_numpy()).items():
                    monthly.append((hub, var, f"{y}-{m:02d}-01T00:00:00Z", v, unit))
        log(f"  {hub}: {FIRST_YEAR} to {now_local.year}, {len(g)} intervals")
    return annual, monthly, last


def derived_license(names, log):
    """The most restrictive license of the inputs' sources (Decision 23)."""
    reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
    lic = dict(zip(reg["source"], reg["license"]))
    srcs = set()
    for n in names:
        srcs |= set(ip.read_series(os.path.join(ip.OUT_DIR, n + ".csv"))["source"])
    missing = sorted(s for s in srcs if s not in lic)
    if missing:
        raise RuntimeError(f"input sources {missing} are not in the registry; cannot set the license")
    out = "internal" if any(lic[s] == "internal" for s in srcs) else "public"
    log(f"  input sources {sorted(srcs)}: licenses {sorted({lic[s] for s in srcs})} -> {out}")
    return out, sorted(srcs)


def frame(rows, freq, run_id):
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    df = pd.DataFrame(rows, columns=["node", "variable", "ts_utc", "value", "unit"])
    return pd.DataFrame({
        "entity": "ercot:" + df["node"], "variable": df["variable"], "ts_utc": df["ts_utc"],
        "value": df["value"].round(6), "unit": df["unit"], "freq": freq, "geo": "US-TX",
        "market": "ercot_rtm", "node": df["node"], "source": SOURCE, "source_url": METHOD_URL,
        "retrieved_at": got, "vintage": "",
    }).sort_values(["entity", "variable", "ts_utc"])[ip.SERIES_COLS]


TABLES = ("ercot_peak_premium_annual", "ercot_peak_premium_monthly")


def missing_inputs():
    """Years from FIRST_YEAR to last year whose history table is absent, plus the live table."""
    this_year = pd.Timestamp.now(tz=TZ).year
    want = [f"ercot_rtm_hub_prices_{y}" for y in range(FIRST_YEAR, this_year + 1)] + ["ercot_rtm_hub_prices"]
    return [n for n in want if not os.path.exists(os.path.join(ip.OUT_DIR, n + ".csv"))]


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_peak_premium_{run_id}.log"))
    results = []
    absent = missing_inputs()
    if absent and os.environ.get("GITHUB_ACTIONS") == "true":
        msg = (f"inputs absent in CI ({len(absent)} tables, e.g. {', '.join(absent[:3])}); "
               "derived tables not written (session 10 ruling 3)")
        log(f"SKIPPED: {msg}")
        print(f"::warning::ercot_peak_premium SKIPPED: {msg}")
        print(f"ercot_peak_premium SKIPPED: {msg}")
        ip.write_status("ercot_peak_premium", run_id,
                        [dict(table=t, market="", status="skipped", detail=msg) for t in TABLES])
        log.close()
        return 0
    try:
        log(f"ERW ercot_peak_premium {run_id}: method {METHOD}")
        d, names = load(log)
        license_, srcs = derived_license(names, log)
        annual, monthly, last = build(d, log)
        for name, rows, freq, what in (("ercot_peak_premium_annual", annual, "P1Y", "ERCOT operating year"),
                                       ("ercot_peak_premium_monthly", monthly, "P1M", "calendar month")):
            s = frame(rows, freq, run_id)
            header = [
                f"Energy Research Warehouse (ERW): ERCOT peak premium metrics per hub and {what} (derived)",
                f"Shape: series (docs/datastandard.md v0). freq {freq}: ts_utc labels the {what} in "
                "America/Chicago (YYYY-01-01 or YYYY-MM-01 at 00:00:00Z); the period itself is local time.",
                f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_peak_premium.py",
                f"Run log: warehouse/output/logs/ercot_peak_premium_{run_id}.log",
                f"Source: {SOURCE} ERW derived metrics, ERCOT peak premium method ({METHOD}), {METHOD_URL}",
                "Derived from: " + "; ".join(names),
                "  input sources: " + "; ".join(srcs),
                "Method: blocks by local hour of interval start: overnight h>=21 or h<12, midday 12<=h<16, "
                "peak 16<=h<21; percentiles numpy default (linear); no cap or exclusion.",
                f"Last input interval: {ip.utc_iso(last)}; the current year and month are partial "
                "(n_intervals says how many intervals each period holds).",
                f"License: {license_}. A derived table inherits the most restrictive license of its inputs "
                "(Decision 23).",
            ]
            ip.write_csv(s, name, header, log)
            results.append(dict(table=name, market=freq, status="ok", detail=""))
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="ERCOT peak premium metrics (docs/methods/ercot_peak_premium.md)",
                                report_url=METHOD_URL, document_list=METHOD, license=license_,
                                tables=["ercot_peak_premium_annual", "ercot_peak_premium_monthly"])])
    except Exception:
        tb = traceback.format_exc()
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"ercot_peak_premium all FAILED, no output file written: {last}", file=sys.stderr)
        results = [dict(table=t, market="", status="failed", detail=last[:300])
                   for t in ("ercot_peak_premium_annual", "ercot_peak_premium_monthly")]
    ip.write_status("ercot_peak_premium", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"ercot_peak_premium run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
