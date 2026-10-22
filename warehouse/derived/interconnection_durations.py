#!/usr/bin/env python3
"""How long a completed project took from its interconnection request to operation, from Berkeley Lab's Queued Up file
(session 671, chain 043): the All grids tab's time-to-connect column.

Energy Research Warehouse (ERW). Two derived tables from lbnl_interconnection_queue (held; no request is made). Method:
docs/methods/interconnection_durations.md.

    python warehouse/derived/interconnection_durations.py                 # both tables, under the data lock
    python warehouse/derived/interconnection_durations.py --out-dir DIR   # a trial: the tables under DIR

interconnection_durations (entities, one row a completed project): every request whose queue status is operational and
that gives both its request date (q_date) and its operation date (on_date). months_to_operation is the days between the two
divided by 30.4375 (the mean month), to one decimal. A project whose operation date is before its request date is left
out and counted in the header; nothing is filled or estimated. grid is Berkeley Lab's region (the seven ISOs, West and
Southeast); utility is the file's own utility field where it names one (blank where it does not).

interconnection_durations_summary (series): by grid and by the year a project began operating, and for the U.S. (all
grids), the median, 25th and 75th percentile months, the projects and their MW; and the median over the five years
ending that year (median_months_5y), so a grid with few projects in one year still has a steady figure. A year with no
completed project has no row.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

INPUT = "lbnl_interconnection_queue"
NAME, SUMMARY = "interconnection_durations", "interconnection_durations_summary"
SOURCE = "erw:interconnection_durations"
MONTH_DAYS = 30.4375
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["queue_id", "grid", "state", "county", "utility", "transmission_provider", "fuel", "request_date",
         "operation_date", "months_to_operation", "request_year", "operation_year"]


def read_table(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def grid_key(g):
    return "us" if g == "US" else g.lower().replace("-", "")


def durations(q):
    """The completed projects with both dates, and the counts left out: (table, {reason: count})."""
    op = q[q["q_status"] == "operational"].copy()
    left = {"operational": len(op)}
    req = pd.to_datetime(op["q_date"].replace("", None), errors="coerce")
    on = pd.to_datetime(op["on_date"].replace("", None), errors="coerce")
    has = req.notna() & on.notna()
    left["without a request or an operation date"] = int((~has).sum())
    days = (on - req).dt.days
    back = has & (days < 0)
    left["operation date before the request date"] = int(back.sum())
    keep = has & ~back
    d, req, on, days = op[keep], req[keep], on[keep], days[keep]
    t = pd.DataFrame({
        "entity_id": d["entity_id"], "entity_type": "project", "name": d["name"], "geo": d["geo"], "lat": d["lat"],
        "lon": d["lon"], "capacity_mw": d["capacity_mw"], "status": "operating", "status_date": on.dt.strftime("%Y-%m-%d"),
        "operator": d["operator"], "source": SOURCE, "source_url": d["source_url"], "retrieved_at": d["retrieved_at"],
        "vintage": d["vintage"], "queue_id": d["q_id"], "grid": d["region"], "state": d["state"], "county": d["county"],
        "utility": d["utility"], "transmission_provider": d["lbnl_entity"], "fuel": d["type_clean"],
        "request_date": req.dt.strftime("%Y-%m-%d"), "operation_date": on.dt.strftime("%Y-%m-%d"),
        "months_to_operation": (days / MONTH_DAYS).round(1), "request_year": req.dt.year.astype(str),
        "operation_year": on.dt.year.astype(str)})
    return t.sort_values("entity_id").reset_index(drop=True), left


def summary(t):
    """Series rows by grid (and the U.S.) and operation year."""
    t = t.assign(m=t["months_to_operation"].astype(float), mw=pd.to_numeric(t["capacity_mw"], errors="coerce"),
                 y=t["operation_year"].astype(int))
    src_url, ret = t["source_url"].iloc[0], t["retrieved_at"].iloc[0]
    rows = []
    for grid, g in list(t.groupby("grid")) + [("US", t)]:
        years = sorted(g["y"].unique())
        for y in years:
            one, five = g[g["y"] == y], g[(g["y"] > y - 5) & (g["y"] <= y)]
            vals = [("median_months", one["m"].median(), "month"), ("p25_months", one["m"].quantile(0.25), "month"),
                    ("p75_months", one["m"].quantile(0.75), "month"), ("projects", float(len(one)), "count"),
                    ("mw", float(one["mw"].sum()), "MW"), ("median_months_5y", five["m"].median(), "month"),
                    ("projects_5y", float(len(five)), "count")]
            for var, v, unit in vals:
                rows.append(dict(entity=f"lbnl_durations:{grid_key(grid)}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z",
                                 value=round(float(v), 2), unit=unit, freq="P1Y", geo="US", market="", node=grid,
                                 source=SOURCE, source_url=src_url, retrieved_at=ret, vintage=""))
    return pd.DataFrame(rows, columns=ip.SERIES_COLS).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Interconnection request to operation, completed projects (Queued Up)")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    inp = os.path.join(ip.OUT_DIR, INPUT + ".csv")
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"interconnection_durations_{run_id}.log"))
    try:
        q = read_table(inp)
        t, left = durations(q)
        s = summary(t)
        vin = t["vintage"].iloc[0]
        common = [
            f"Derived from: {INPUT}",
            f"Built by warehouse/derived/interconnection_durations.py from Berkeley Lab and GridTracker's Queued Up ({vin}); method docs/methods/interconnection_durations.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/interconnection_durations_{run_id}.log",
            "Source: lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file, https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics",
            'License: CC BY 4.0 (Berkeley Lab: "The Queued Up data file is licensed CC BY 4.0"; attribute it to Lawrence Berkeley National Laboratory and GridTracker). The durations are the ERW\'s arithmetic on it.',
        ]
        h1 = [f"Energy Research Warehouse (ERW): interconnection request to operation, every completed project with both dates, {vin} (session 671)",
              "Shape: entities (docs/datastandard.md v0). entity_id the queue table's own; entity_type project; status operating; status_date the operation date; months_to_operation = days from request_date to operation_date / 30.4375, one decimal; grid Berkeley Lab's region; utility as the file names it.",
              f"Rows: {len(t):,} of {left['operational']:,} operational requests; left out: {left['without a request or an operation date']:,} without a request or an operation date, {left['operation date before the request date']:,} whose operation date is before the request date. Nothing is filled."] + common
        h2 = [f"Energy Research Warehouse (ERW): interconnection request to operation by grid and year of operation, {vin} (session 671)",
              "Shape: series (docs/datastandard.md v0). entity lbnl_durations:<grid> (the seven ISOs, west, southeast, us); variables median_months, p25_months, p75_months (unit month: 30.4375 days), projects (count), mw (MW), median_months_5y and projects_5y (the five years ending ts_utc's year); ts_utc 1 January of the year the projects began operating; freq P1Y.",
              f"Rows: {len(s):,}, from {NAME}'s {len(t):,} projects. A year with no completed project in a grid has no row."] + common
        ip.write_snapshot(t, NAME, h1, log, cols=ENTITY_COLS + EXTRA)
        ip.write_snapshot(s, SUMMARY, h2, log, cols=ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="Interconnection request to operation, completed projects, from Berkeley Lab's Queued Up file (docs/methods/interconnection_durations.md)",
                                    report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interconnection_durations.md",
                                    document_list="docs/methods/interconnection_durations.md", license="public", tables=[NAME, SUMMARY])])
        print(f"{NAME}: {len(t):,} projects; {SUMMARY}: {len(s):,} rows; left out {left}")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"interconnection_durations FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc



if __name__ == "__main__":
    sys.exit(main())
