#!/usr/bin/env python3
"""Demand growth since 2019: annual and peak demand of the seven ISO balancing authorities and the Lower 48 (session 97).

Energy Research Warehouse (ERW). One derived table, eia930_demand_growth, from EIA-930 hourly demand. Method:
docs/methods/demand_growth.md. Page: /demand (in review).

    python warehouse/derived/demand_growth.py                 # the table, under the data lock
    python warehouse/derived/demand_growth.py --out-dir DIR   # a trial run: the table under DIR, nothing in warehouse/output
    python warehouse/derived/demand_growth.py --snapshot      # also the site's own copy (site/data/demand_growth.json)

Input (no request is made): EIA-930 hourly demand from the workbooks the emissions connector saved
(warehouse/raw/eia930_emissions/<run>/*_<BA>.xlsx, sheet Published Hourly Data): EIA's Adjusted demand for a balancing
authority, its Demand for the Lower 48 region. An hour is dated by its start. California's hours of 2023-11 to
2025-12-02, which EIA dates one hour late, are set back (caiso_join.true_hours).

WEATHER IS NOT REMOVED. A year's demand is that year's: a hot summer or a cold snap is in it. Growth between two years
is the difference of what was metered, not of what a normal year would have been.

An hour is used when its demand is held, above zero, and within 25 percent of the median of the four hours around it
(the two before and the two after that are held). The last test leaves out EIA's faulty hours: PJM's file holds
224,345 MW at 18:00 on 13 July 2020 between hours of about 140,000, and 155,276 MW on a December afternoon of 2019
that would have been the year's peak; New York's holds hours of zero. A real hour does not stand a quarter away from
its neighbours. An hour that is not used is used for nothing; nothing is filled.

The Lower 48 has no peak here. Its demand is EIA's sum over every balancing authority, faulty hours included: PJM's
224,345 MW is in the Lower 48's 776,575 MW of the same hour, which stands 12 percent above the hours around it and
would pass the test. Its average, over 8,760 hours, does not move for such an hour; its peak would be that hour.

Entity eia930:<BA>; all rows freq P1Y, ts_utc the first day of the local year.
    avg_demand_mw, hours_used, hours_in_year          the mean of the used hours; a year is written when at least 95
                                                      percent of its hours are used (the newest year is not: it is partial)
    peak_demand_mw                                    the highest used hour; x_at is that hour (its start, UTC)
    avg_demand_growth_since_2019_pct, avg_demand_growth_yoy_pct, peak_demand_growth_since_2019_pct
    ytd_avg_demand_mw, ytd_peak_demand_mw, ytd_hours_used, ytd_hours_in_window
    ytd_avg_demand_growth_since_2019_pct, ytd_peak_demand_growth_since_2019_pct
                                                      the same over 1 January to the end of the newest year's last whole
                                                      month, for every year, so the partial year compares like with like
    avg_demand_mw_mMM                                 the mean of a calendar month's used hours (at least 95 percent used)
    avg_demand_mw_hHH                                 the mean of a local hour of the day over the year
    avg_demand_mw_mMM_hHH                             the mean of one local hour of the day in one month (at least 90
                                                      percent of its hours used)
and, on the row of the last whole year, the change from 2019 to that year:
    growth_mw_mMM, growth_pct_mMM, growth_mw_hHH, growth_pct_hHH, growth_mw_mMM_hHH, growth_pct_mMM_hHH
"""

import argparse
import glob
import json
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "eia930_demand_growth"
SOURCE = "erw:demand_growth"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/demand_growth.md"
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
SITE_FILE = os.path.join(ROOT, "site", "data", "demand_growth.json")
BASE = 2019
JUMP = 0.25         # an hour further than this share from the median of the four hours around it is not used
NEAR_YEAR = 0.95    # a year, or a month, is written when at least this share of its hours is used
NEAR_CELL = 0.90    # a month-and-hour cell, when at least this share of its hours is used
AREAS = {
    "ERCO": dict(name="ERCOT", tz="America/Chicago", geo="US-TX"), "CISO": dict(name="CAISO", tz="America/Los_Angeles", geo="US-CA"),
    "PJM": dict(name="PJM", tz="America/New_York", geo="US"), "MISO": dict(name="MISO", tz="America/Chicago", geo="US"),
    "SWPP": dict(name="SPP", tz="America/Chicago", geo="US"), "NYIS": dict(name="NYISO", tz="America/New_York", geo="US-NY"),
    "ISNE": dict(name="ISO-NE", tz="America/New_York", geo="US"), "US48": dict(name="Lower 48", tz="America/New_York", geo="US", peak=False),
}


def workbook(ba):
    files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def read_demand(ba):
    """EIA-930's hourly demand of one area, MW, indexed by the hour's start (UTC); a blank is NaN."""
    import openpyxl
    path = workbook(ba)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    t = head.index("UTC time")
    col = head.index("Adjusted demand") if "Adjusted demand" in head else head.index("Demand")
    out = [(r[t] - timedelta(hours=1), float(r[col]) if isinstance(r[col], (int, float)) else np.nan) for r in rows if r[t] is not None and r[t].year >= BASE - 1]
    d = pd.DataFrame(out, columns=["ts", "demand"])
    d["ts"] = pd.to_datetime(d["ts"]).dt.tz_localize("UTC")
    d = d.drop_duplicates("ts").set_index("ts").sort_index()
    if ba == "CISO":
        d = cj.true_hours(d)
    return d["demand"], path, head[col]


def screened(d):
    """The hours used: held, above zero, and within JUMP of the median of the four hours around them."""
    v = d.where(d > 0)
    around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
    ok = v.notna() & ~((v - around).abs() > JUMP * around)
    return v.where(ok)


def hours_between(a, b, tz):
    return int((pd.Timestamp(b, tz=tz) - pd.Timestamp(a, tz=tz)) / pd.Timedelta(hours=1))


def summarize(d, tz, last_month=None, peak=True):
    """One area's figures from its screened hourly demand (UTC index; NaN where not used). Returns
    {year: {variable: value}}, {year: {variable: x_at}} and the last whole month of the newest year (YYYY-MM)."""
    local = d.index.tz_convert(tz)
    x = pd.DataFrame({"v": d.values, "year": local.year, "month": local.month, "hour": local.hour}, index=d.index)
    x = x[x["year"] >= BASE]
    newest = int(x["year"].max())
    if last_month is None:
        end = x["v"].dropna().index.max().tz_convert(tz)
        last_month = (end.to_period("M") - 1).strftime("%Y-%m") if (end + pd.Timedelta(hours=1)).month == end.month else end.strftime("%Y-%m")
    ytd_m = int(last_month[5:])
    out, at = {}, {}
    for y, g in x.groupby("year"):
        y = int(y)
        r, a = {}, {}
        n = hours_between(f"{y}-01-01", f"{y + 1}-01-01", tz)
        used = g["v"].dropna()
        if y < newest and len(used) >= NEAR_YEAR * n:
            r.update(avg_demand_mw=round(float(used.mean()), 1), hours_used=int(len(used)), hours_in_year=n)
            if peak:
                r["peak_demand_mw"] = round(float(used.max()), 1)
                a["peak_demand_mw"] = ip.utc_iso(used.idxmax())
            for h, c in g.groupby("hour"):
                r[f"avg_demand_mw_h{int(h):02d}"] = round(float(c["v"].mean()), 1)
        w = g[g["month"] <= ytd_m]
        wn = hours_between(f"{y}-01-01", (pd.Period(f"{y}-{ytd_m:02d}") + 1).strftime("%Y-%m-01"), tz)
        wu = w["v"].dropna()
        if len(wu) >= NEAR_YEAR * wn:
            r.update(ytd_avg_demand_mw=round(float(wu.mean()), 1), ytd_hours_used=int(len(wu)), ytd_hours_in_window=wn)
            if peak:
                r["ytd_peak_demand_mw"] = round(float(wu.max()), 1)
                a["ytd_peak_demand_mw"] = ip.utc_iso(wu.idxmax())
        for m, c in g.groupby("month"):
            m = int(m)
            if y == newest and m > ytd_m:
                continue
            mn = hours_between(f"{y}-{m:02d}-01", (pd.Period(f"{y}-{m:02d}") + 1).strftime("%Y-%m-01"), tz)
            if c["v"].count() < NEAR_YEAR * mn:
                continue
            r[f"avg_demand_mw_m{m:02d}"] = round(float(c["v"].mean()), 1)
            if y < newest:
                for h, cell in c.groupby("hour"):
                    if cell["v"].count() >= NEAR_CELL * len(cell):
                        r[f"avg_demand_mw_m{m:02d}_h{int(h):02d}"] = round(float(cell["v"].mean()), 1)
        if r:
            out[y], at[y] = r, a
    base = out.get(BASE, {})
    pct = lambda new, old: round(100 * (new - old) / old, 2)
    for y, r in out.items():
        if y == BASE:
            continue
        for k, name in (("avg_demand_mw", "avg_demand_growth_since_2019_pct"), ("peak_demand_mw", "peak_demand_growth_since_2019_pct"),
                        ("ytd_avg_demand_mw", "ytd_avg_demand_growth_since_2019_pct"), ("ytd_peak_demand_mw", "ytd_peak_demand_growth_since_2019_pct")):
            if k in r and k in base:
                r[name] = pct(r[k], base[k])
        if "avg_demand_mw" in r and "avg_demand_mw" in out.get(y - 1, {}):
            r["avg_demand_growth_yoy_pct"] = pct(r["avg_demand_mw"], out[y - 1]["avg_demand_mw"])
    whole = [y for y, r in out.items() if "avg_demand_mw" in r]
    if whole and BASE in whole and max(whole) > BASE:
        r = out[max(whole)]
        for k in [k for k in list(r) if k.startswith("avg_demand_mw_")]:
            if k in base:
                r["growth_mw_" + k[len("avg_demand_mw_"):]] = round(r[k] - base[k], 1)
                r["growth_pct_" + k[len("avg_demand_mw_"):]] = pct(r[k], base[k])
    return out, at, last_month


def break_check(d, tz):
    """California across the join: the mean of the used hours of the 28 days before the join's date and of the 28 days
    from it, in the year of the join and on the same dates of each earlier year, and the second over the first."""
    j = pd.Timestamp(cj.JOIN).tz_convert(tz)
    rows = []
    for back in range(0, j.year - BASE + 1):
        day = pd.Timestamp(year=j.year - back, month=j.month, day=j.day, tz=tz)
        a = d[(d.index >= day - pd.Timedelta(days=28)) & (d.index < day)].dropna()
        b = d[(d.index >= day) & (d.index < day + pd.Timedelta(days=28))].dropna()
        if len(a) >= 0.95 * 672 and len(b) >= 0.95 * 672:
            rows.append({"year": day.year, "before_mw": round(float(a.mean()), 1), "after_mw": round(float(b.mean()), 1), "ratio": round(float(b.mean() / a.mean()), 4)})
    return rows


def unit_of(variable):
    return "pct" if variable.endswith("_pct") or variable.startswith("growth_pct_") else "count" if "hours_" in variable else "MW"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Demand growth since 2019, from EIA-930 hourly demand")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the registry under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/demand_growth.json)")
    a = ap.parse_args(argv)
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"demand_growth_{run_id}.log"))
    rows, areas, paths, check, last_month = [], {}, [], [], None
    for ba, g in AREAS.items():
        raw, path, column = read_demand(ba)
        paths.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        d = screened(raw)
        since = raw[raw.index >= pd.Timestamp(f"{BASE}-01-01", tz=g["tz"]).tz_convert("UTC")]
        used = d.reindex(since.index)
        left = since[used.isna() & since.notna()]
        log(f"  {ba}: column '{column}', {len(since):,} hours from {BASE}, {int(since.isna().sum()):,} blank, {len(left):,} held and not used "
            f"({int((left <= 0).sum()):,} at or below zero, {int((left > 0).sum()):,} further than {JUMP:.0%} from the hours around them): "
            + "; ".join(f"{ip.utc_iso(i)} {int(v):,}" for i, v in left.items() if v > 0)[:900])
        out, at, last_month = summarize(d, g["tz"], last_month, g.get("peak", True))
        for y, r in out.items():
            for k, v in r.items():
                rows.append(dict(entity=f"eia930:{ba}", variable=k, ts_utc=f"{y}-01-01T00:00:00Z", value=v, unit=unit_of(k), freq="P1Y", geo=g["geo"], market="", node="",
                                 source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="", x_at=at[y].get(k, "")))
        areas[ba] = {"name": g["name"], "tz": g["tz"], "years": {str(y): r for y, r in sorted(out.items())}, "at": {str(y): v for y, v in sorted(at.items())},
                     "screened": {"blank": int(since.isna().sum()), "not_positive": int((left <= 0).sum()), "jumps": int((left > 0).sum())}}
        if ba == "CISO":
            check = break_check(d, g["tz"])
            log(f"  CISO across the join ({cj.JOIN}): 28 days before and after, by year: {check}")
    out = pd.DataFrame(rows)[ip.SERIES_COLS + ["x_at"]]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole each run: the year-to-date window moves with the last whole month
    whole = sorted(int(y) for y, r in areas["ERCO"]["years"].items() if "avg_demand_mw" in r)
    ip.write_csv(out, NAME, [
        "Energy Research Warehouse (ERW): demand growth since 2019, annual and peak demand of the seven ISO balancing authorities and the Lower 48 (session 97)",
        "Shape: series (docs/datastandard.md v0). freq P1Y; ts_utc is the first day of the local year. avg_demand_mw, peak_demand_mw (x_at: the hour of the peak, "
        "its start, UTC), their growth since 2019, the same year to date (ytd_), the mean by month (_mMM), by local hour (_hHH) and by month and hour "
        "(_mMM_hHH), and on the last whole year the change from 2019 (growth_mw_, growth_pct_). Definitions: docs/methods/demand_growth.md.",
        f"Window: whole years {whole[0]} to {whole[-1]}; year to date: 1 January to the end of {last_month[5:]}/{last_month[:4]} of each year. Weather is not "
        f"removed. An hour is used when its demand is above zero and within {JUMP:.0%} of the median of the four hours around it; a year or a month is written "
        f"when at least {NEAR_YEAR:.0%} of its hours are used.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/demand_growth.py", f"Run log: warehouse/output/logs/demand_growth_{run_id}.log",
        "Source: " + SOURCE + " from EIA Form EIA-930 (Hourly Electric Grid Monitor), hourly demand by balancing authority and for the Lower 48, the per-area "
        "workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); read by this run from " + "; ".join(paths),
        "License: public (EIA publications are in the public domain)",
    ], log, cols=ip.SERIES_COLS + ["x_at"], key=["entity", "variable", "ts_utc"])
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="Demand growth since 2019: annual and peak demand from EIA-930 hourly demand (docs/methods/demand_growth.md)", report_url=METHOD_URL,
                            document_list="docs/methods/demand_growth.md", license="public", tables=[NAME])])
    if a.snapshot:
        os.makedirs(os.path.dirname(SITE_FILE), exist_ok=True)
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(table=NAME, built=retrieved, base=BASE, last_year=whole[-1], ytd_through=last_month, jump=JUMP, near_year=NEAR_YEAR, near_cell=NEAR_CELL,
                           order=list(AREAS), areas=areas, caiso_break={"join": cj.JOIN, "rows": check}), f, separators=(",", ":"))
    log.close()
    print(f"{NAME}: {len(out):,} rows, {out['entity'].nunique()} areas, whole years {whole[0]} to {whole[-1]}, year to date through {last_month}"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
