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


def metrics(prices, hours, weekdays=None, loads=None):   # weekdays, loads: wip/alt-ercot-peak-premium-1
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
    # ruling alternative 1 of /explore/ercot-peak-premium (session 7708, branch wip/alt-ercot-peak-premium-1; not a default
    # on main): beside the medians, the figures a published source can be held to: each block's plain mean and the whole
    # period's, the traded 06:00 to 22:00 weekday block (local hour of interval start, Monday to Friday), and the mean
    # weighted by ERCOT's system load of the interval's UTC hour (ercot_zone_load_hourly, entity ercot:system) over the
    # intervals whose hour has a load.
    for b, rule in BLOCKS.items():
        out[f"{b}_mean"] = (float(prices[rule(hours)].mean()), USD)
    out["all_mean"] = (float(prices.mean()), USD)
    if weekdays is not None:
        traded = prices[(weekdays < 5) & (hours >= 6) & (hours < 22)]
        if len(traded):
            out["traded_median"] = (pct(traded, 50), USD)
            out["traded_mean"] = (float(traded.mean()), USD)
    if loads is not None:
        ok = np.isfinite(loads) & (loads > 0)
        if ok.any():
            out["all_mean_load_weighted"] = (float((prices[ok] * loads[ok]).sum() / loads[ok].sum()), USD)
            out["n_load_weighted"] = (float(ok.sum()), "count")
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
    # session 452: the daily append step (dm_ercot_hub_append_stores) writes the live days into the year's history too,
    # so the rolling table's intervals are also in ercot_rtm_hub_prices_<year>: the same interval at the same price is
    # one row (the history's, read first); the same interval at two prices is still refused below
    same = d.duplicated(["node", "ts_utc", "value"], keep="first")
    if same.any():
        log(f"  {int(same.sum())} intervals in both the history and the rolling table at the same price: read once")
        d = d[~same].reset_index(drop=True)
    dup = d.duplicated(["node", "ts_utc"], keep=False)
    if dup.any():
        raise RuntimeError(f"{int(dup.sum())} rows repeat a (hub, interval) across the input tables")
    d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    d["local"] = d["ts"].dt.tz_convert(TZ)
    return d, names


def expected(start_local, end_local):
    """Quarter hours in [start, end) local, counted in real (UTC) time."""
    return int((end_local.tz_convert("UTC") - start_local.tz_convert("UTC")) / pd.Timedelta("15min"))


def ytd_cut(last_local, year):
    """The local moment in `year` at the month, day and time of the last input interval (29 February falls back to the
    28th's same time in a year without it): the end, inclusive, of that year's year to date."""
    day = last_local.day
    if last_local.month == 2 and day == 29 and not pd.Timestamp(f"{year}-03-01").is_leap_year:
        day = 28
    naive = pd.Timestamp(year=year, month=last_local.month, day=day, hour=last_local.hour, minute=last_local.minute)
    return naive.tz_localize(TZ, ambiguous=True, nonexistent="shift_forward")


def metrics_of(g):
    """metrics() of a frame of intervals: its prices, local hours and weekdays, and its system load where load() read it
    (ruling alternative 1, wip/alt-ercot-peak-premium-1)."""
    loads = g["load"].to_numpy(float) if "load" in g.columns else None
    return metrics(g["value"].to_numpy(float), g["local"].dt.hour.to_numpy(), g["local"].dt.weekday.to_numpy(), loads)


LOAD = "ercot_zone_load_hourly"   # ruling alternative 1 (wip/alt-ercot-peak-premium-1): ERCOT's system load, entity ercot:system


def with_load(d, log, path=None):
    """d with a column load: ERCOT's system load (MW) of each interval's UTC hour, NaN where the hour has none. When the
    load table is not on the machine, d is returned as it is and no load-weighted mean is written."""
    path = path or os.path.join(ip.OUT_DIR, LOAD + ".csv")
    if not os.path.exists(path):
        log(f"  {LOAD} is not on this machine: no load-weighted mean")
        return d
    ld = ip.read_series(path)
    ld = ld[ld["entity"] == "ercot:system"]
    by_hour = dict(zip(ld["ts_utc"].str.slice(0, 13), pd.to_numeric(ld["value"], errors="coerce")))
    d = d.copy()
    d["load"] = d["ts_utc"].str.slice(0, 13).map(by_hour).astype(float)
    log(f"  {LOAD}: system load for {int(d['load'].notna().sum()):,} of {len(d):,} intervals")
    return d


def build(d, log):
    now_local = pd.Timestamp.now(tz=TZ)
    last = d["ts"].max()
    last_local = last.tz_convert(TZ)
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
            for var, (v, unit) in metrics_of(gy).items():
                annual.append((hub, var, f"{y}-01-01T00:00:00Z", v, unit))
            # session 7019 (chain 301, done-line request 36): the same metrics over 1 January 00:00 local to the local day
            # and time of year of the last input interval, for every year, so the partial year has a like figure beside
            # each earlier year (ytd_<variable>; for the newest year it is the year's own figure)
            gt = gy[gy["local"] <= ytd_cut(last_local, y)]
            if not gt.empty:
                for var, (v, unit) in metrics_of(gt).items():
                    annual.append((hub, f"ytd_{var}", f"{y}-01-01T00:00:00Z", v, unit))
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
                for var, (v, unit) in metrics_of(gm).items():
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


FAMILIES = ("ercot_all_hub_prices_history", "iso_rtm_hub_prices")   # the consolidated tables that hold the inputs


def main_split():
    """Session 7020 (chain 301): the inputs are members of two consolidated tables; on the data machine they exist only
    between `consolidate.py split` and `build`. --split runs the split, the build of the metrics, and the build of the
    families back (the members leave warehouse/output again), so a daily step can call it alone. Exit 1 when any of the
    three fails; the families are built back whatever the metrics did."""
    import subprocess
    cons = [sys.executable, os.path.join(ip.ROOT, "warehouse", "consolidate.py")]
    fam = [x for f in FAMILIES for x in ("--family", f)]
    if subprocess.run(cons + ["split"] + fam, cwd=ip.ROOT).returncode != 0:
        print("ercot_peak_premium FAILED: consolidate.py split failed; nothing built", file=sys.stderr)
        return 1
    try:
        rc = main()
    finally:
        back = subprocess.run(cons + ["build"] + fam, cwd=ip.ROOT).returncode
    if back != 0:
        print("ercot_peak_premium FAILED: consolidate.py build failed; the members stay in warehouse/output", file=sys.stderr)
        return 1
    return rc


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
        d = with_load(d, log)   # wip/alt-ercot-peak-premium-1
        if "load" in d.columns:
            names = names + [LOAD]
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
                "Means (ruling alternative 1 of /explore/ercot-peak-premium, branch wip/alt-ercot-peak-premium-1): <block>_mean and "
                "all_mean, plain means; traded_median and traded_mean, the 06:00 to 22:00 local weekday block (Monday to Friday); "
                "all_mean_load_weighted, weighted by ERCOT's system load of the interval's UTC hour (ercot_zone_load_hourly, "
                "ercot:system) over the n_load_weighted intervals whose hour has a load.",
                f"Last input interval: {ip.utc_iso(last)}; the current year and month are partial "
                "(n_intervals says how many intervals each period holds).",
            ] + ([
                "Year to date (session 7019): each ytd_<variable> is the same metric over 1 January 00:00 local to the local "
                "month, day and time of the last input interval in that year (inclusive), so every year has a figure like "
                "the partial year's; for the newest year it equals the year's own.",
            ] if name == "ercot_peak_premium_annual" else []) + [
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
    sys.exit(main_split() if "--split" in sys.argv[1:] else main())
