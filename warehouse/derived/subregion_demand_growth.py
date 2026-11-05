#!/usr/bin/env python3
"""A zone's own demand growth: every EIA-930 sub-region's peak hour and average demand by year (session 2877, chain 147).

Energy Research Warehouse (ERW). One derived table, subregion_demand_growth, from the hourly demand by sub-region the
warehouse holds (eia930_subba_demand_hourly_<year>, 2019 to 2025, and the rolling eia930_subba_demand_hourly). It gives
the All grids tab the demand growth of a row's own zone where the zone is an EIA-930 sub-region (docs/reviews/
siting-gaps.md, "demand growth of the row's own zone"), not only its grid's. Method: docs/methods/subregion_demand_growth.md.

    python warehouse/derived/subregion_demand_growth.py               # the table (data lock)
    python warehouse/derived/subregion_demand_growth.py --out-dir DIR # a trial: the table under DIR

No request is made. An hour is used as the grid-level builder uses one (warehouse/derived/demand_growth.py, through
impossible_hours.screen): held, above zero, within 25 percent of the median of the two hours on each side, and within a
third to three times the sub-region's median hour. An hour that is not used is used for nothing; nothing is filled.
Years are UTC calendar years (EIA-930's hours are dated in UTC; a sub-region spans no one time zone the table names).

    entity     eia930_subba:<parent>:<subba>, as the source table; node its names; ts_utc the year's first hour, freq P1Y
    variables  peak_mw (MW; x_at the peak hour's start, UTC), avg_mw (MW, the mean of the hours used), energy_mwh (MWh,
               the sum of the hours used), hours_used and hours_in_year (count), avg_growth_pct and peak_growth_pct (pct,
               against the year before)
    A year's figures are written only when at least 95 percent of its hours are used; growth only when both years are.
    A year with fewer hours used gets its hours_used and hours_in_year rows and no figure (2026: the rolling table holds
    90 days, so the year to date is not written).
"""

import argparse
import calendar
import datetime as dt
import glob
import os
import re
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import impossible_hours  # noqa: E402

NAME = "subregion_demand_growth"
SOURCE = "erw:subregion_demand_growth"
INPUT = "eia930_subba_demand_hourly"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/subregion_demand_growth.md"
NEAR_YEAR = 0.95
UNITS = {"peak_mw": "MW", "avg_mw": "MW", "energy_mwh": "MWh", "hours_used": "count", "hours_in_year": "count",
         "avg_growth_pct": "pct", "peak_growth_pct": "pct"}
COLS = ip.SERIES_COLS + ["x_at", "x_parent", "x_subba"]


def inputs(folder=None):
    """{path: year or None for the rolling table}, the yearly tables first."""
    folder = folder or ip.OUT_DIR
    out = {}
    for p in sorted(glob.glob(os.path.join(folder, f"{INPUT}_*.csv"))):
        m = re.search(r"_(\d{4})\.csv$", p)
        if m:
            out[p] = int(m.group(1))
    rolling = os.path.join(folder, f"{INPUT}.csv")
    if os.path.exists(rolling):
        out[rolling] = None
    return out


def read_hours(path):
    """The demand rows of one input: entity, node, ts (UTC), value."""
    d = pd.read_csv(path, comment="#", usecols=["entity", "variable", "ts_utc", "value", "node"], dtype=str, keep_default_na=False)
    d = d[d["variable"] == "demand_mw"]
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    return d[["entity", "node", "ts", "v"]]


def year_figures(s, year):
    """One sub-region's figures for one year from its hourly series (UTC index): {variable: (value, x_at)}."""
    start, end = pd.Timestamp(f"{year}-01-01", tz="UTC"), pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
    grid = pd.date_range(start, end, freq="h", inclusive="left")
    full = s[~s.index.duplicated(keep="last")].reindex(grid)
    used = impossible_hours.screen(full)
    n_used, n_all = int(used.notna().sum()), len(grid)
    out = {"hours_used": (n_used, ""), "hours_in_year": (n_all, "")}
    if n_used >= NEAR_YEAR * n_all:
        at = used.idxmax()
        out["peak_mw"] = (float(used.max()), at.strftime("%Y-%m-%dT%H:%M:%SZ"))
        out["avg_mw"] = (float(used.mean()), "")
        out["energy_mwh"] = (float(used.sum()), "")
    return out


def build(paths):
    """The table's rows from the inputs {path: year or None}."""
    figs, names = {}, {}
    for path, year in paths.items():
        d = read_hours(path)
        years = [year] if year is not None else sorted(d["ts"].dt.year.unique())
        for ent, g in d.groupby("entity"):
            names[ent] = g["node"].iloc[0]
            s = g.set_index("ts")["v"].sort_index()
            for y in years:
                if (ent, y) in figs:           # a year a yearly table holds is not taken from the rolling one
                    continue
                part = s[(s.index.year == y)]
                if part.empty:
                    continue
                figs[(ent, y)] = year_figures(part, y)
    rows = []
    for (ent, y), f in sorted(figs.items()):
        prev = figs.get((ent, y - 1), {})
        for a, b in (("avg_mw", "avg_growth_pct"), ("peak_mw", "peak_growth_pct")):
            if a in f and a in prev and prev[a][0] > 0:
                f[b] = (100.0 * (f[a][0] / prev[a][0] - 1.0), "")
        parent, subba = ent.split(":", 1)[1].split(":", 1)
        for var, (val, at) in f.items():
            rows.append({"entity": ent, "variable": var, "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(val, 4) if isinstance(val, float) else val,
                         "unit": UNITS[var], "freq": "P1Y", "geo": "US", "market": "", "node": names[ent], "source": SOURCE,
                         "source_url": METHOD_URL, "retrieved_at": "", "vintage": "", "x_at": at, "x_parent": parent, "x_subba": subba})
    t = pd.DataFrame(rows, columns=COLS)
    order = {v: i for i, v in enumerate(UNITS)}
    return t.sort_values(["entity", "ts_utc", "variable"], key=lambda c: c.map(order) if c.name == "variable" else c).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: every EIA-930 sub-region's peak and average demand by year (session 2877)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    a = ap.parse_args(argv)
    paths = inputs()
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        if not paths:
            raise RuntimeError(f"no {INPUT} table on this machine")
        t = build(paths)
        t["retrieved_at"] = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        written = t[t["variable"] == "peak_mw"]
        years = sorted(t["ts_utc"].str[:4].unique())
        header = [
            "Energy Research Warehouse (ERW): every EIA-930 sub-region's peak hour and average demand by year, and the growth of each (derived, session 2877)",
            "Shape: series (docs/datastandard.md v0). entity eia930_subba:<parent>:<subba>; ts_utc the year's first hour (UTC), freq P1Y; variables "
            + ", ".join(f"{k} ({u})" for k, u in UNITS.items()) + "; x_at the peak hour's start (UTC).",
            f"Years {years[0]} to {years[-1]}; {t['entity'].nunique()} sub-regions; {len(written)} sub-region years with figures (at least 95 percent of the hours used). "
            "An hour is used as warehouse/derived/demand_growth.py uses one (impossible_hours.screen); nothing is filled. Weather is not removed.",
            f"Derived from: {'; '.join(sorted(os.path.splitext(os.path.basename(p))[0] for p in paths))}",
            f"Built by warehouse/derived/subregion_demand_growth.py; method docs/methods/subregion_demand_growth.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: eia:electricity/rto/region-sub-ba-data U.S. Energy Information Administration, Hourly Electric Grid Monitor, demand by subregion",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Hourly Electric Grid Monitor").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="Every EIA-930 sub-region's peak and average demand by year (docs/methods/subregion_demand_growth.md)",
                                    report_url=METHOD_URL, document_list="docs/methods/subregion_demand_growth.md", license="public", tables=[NAME])])
        print(f"{NAME}: {len(t)} rows, {t['entity'].nunique()} sub-regions, years {years[0]} to {years[-1]}, {len(written)} sub-region years with figures")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
