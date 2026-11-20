#!/usr/bin/env python3
"""EIA-930 hourly demand, demand forecast, net generation and total interchange for each of EIA's thirteen regions of
the lower 48 and for every balancing authority, July 2018 to the newest hour, from EIA's six-month files (session 7801,
chain 401 part C, table 1).

Energy Research Warehouse (ERW) connector. Writes three series tables from one read of the files:

    warehouse/output/eia930_region_hourly.csv       the thirteen regions, the four variables; partition column ba
    warehouse/output/eia930_ba_demand_hourly.csv    every balancing authority: demand_mw, demand_forecast_mw
    warehouse/output/eia930_ba_supply_hourly.csv    every balancing authority: net_generation_mw, total_interchange_mw

Three tables, split by measurement as eia930_all_demand, _generation and _interchange are, because one table of every
balancing authority and region, hourly since July 2018, is about twenty million rows and more than this machine's
validator reads in memory (Decisions made without Samuel, session 7801). From EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv
(https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/), every file from 2018 Jul_Dec to the current half-year.
Public (U.S. Government data).

    python warehouse/connectors/eia930_region_hourly.py --download-only [--skip-saved]   # files to warehouse/raw (no lock)
    python warehouse/connectors/eia930_region_hourly.py --from-raw                       # the tables from the saved copies
    python warehouse/connectors/eia930_region_hourly.py --from-raw --files EIA930_BALANCE_2025_Jul_Dec.csv --out-dir DIR

Variables (MW, EIA's MWh per hour). For demand, net generation and total interchange the file prints the value as the
balancing authority submitted it ("Demand (MW)") and EIA's adjusted value ("Demand (MW) (Adjusted)"); both are kept, in
x_value_reported and x_value_adjusted, and `value` is the adjusted value where EIA prints one, else the reported value
(x_basis says which). The forecast has one column (x_basis "reported"). ts_utc is the hour's start: the file's "UTC Time
at End of Hour" minus one hour. An hour without a value is not written. x_file names the six-month file a row was read
from (2018_Jul_Dec); the header gives each file's URL, Last-Modified and download time (rows carry no URL: twenty
million copies of it would be most of the tables' bytes).

Regions: the file names each balancing authority's region ("Region": CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE,
SW, TEN, TEX). A region's row is the sum of its balancing authorities' rows of that hour, written only when every
balancing authority the files list in that region for that hour has a value (x_bas: how many were summed); otherwise
nothing is written for that region and hour, and the run log counts it. Nothing is filled or scaled. The last day and a
half of each file is carried into the next, so a UTC hour split between two files by the balancing authorities' local
days is summed whole. Method: docs/methods/eia930_region_hourly.md.

The tables are rebuilt whole each run, one file at a time (never one frame of all files), written straight to CSV.
"""

import argparse
import csv
import datetime as dt
import glob
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia930_region_hourly"
BASE = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"
SOURCE = "eia:gridmonitor/sixMonthFiles"
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
# variable: (reported column, adjusted column or None)
VARS = {"demand_mw": ("Demand (MW)", "Demand (MW) (Adjusted)"),
        "net_generation_mw": ("Net Generation (MW)", "Net Generation (MW) (Adjusted)"),
        "total_interchange_mw": ("Total Interchange (MW)", "Total Interchange (MW) (Adjusted)"),
        "demand_forecast_mw": ("Demand Forecast (MW)", None)}
BA_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "ba", "x_region", "x_basis",
           "x_value_reported", "x_value_adjusted", "x_file"]
REGION_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "ba", "x_basis",
               "x_value_reported", "x_value_adjusted", "x_bas", "x_file"]
TABLES = {  # name: (columns, level, variables, title)
    "eia930_region_hourly": (REGION_COLS, "region", list(VARS), "the thirteen regions of the lower 48 (sums of their balancing authorities)"),
    "eia930_ba_demand_hourly": (BA_COLS, "ba", ["demand_mw", "demand_forecast_mw"], "every balancing authority, demand and demand forecast"),
    "eia930_ba_supply_hourly": (BA_COLS, "ba", ["net_generation_mw", "total_interchange_mw"], "every balancing authority, net generation and total interchange"),
}
CARRY = pd.Timedelta(hours=30)
RAW_READ = ip.RAW_DIR  # before any --out-dir: a trial reads this checkout's saved copies, read only


def files_between(first=(2018, 2), today=None):
    """Every six-month file name from `first` (year, half) to the half-year of today, oldest first."""
    today = today or dt.date.today()
    out, (y, h) = [], first
    while (y, h) <= (today.year, 1 if today.month <= 6 else 2):
        out.append(f"EIA930_BALANCE_{y}_{'Jan_Jun' if h == 1 else 'Jul_Dec'}.csv")
        y, h = (y, 2) if h == 1 else (y + 1, 1)
    return out


def tag(name):
    return name.replace("EIA930_BALANCE_", "").replace(".csv", "")


def saved_copy(name):
    """(path, retrieved_at, last_modified) of the newest saved copy of a file under warehouse/raw/<connector>/."""
    found = sorted(glob.glob(os.path.join(RAW_READ, CONNECTOR, "*", f"*{name}")))
    if not found:
        return None
    path = found[-1]
    man = pd.read_csv(os.path.join(os.path.dirname(path), "manifest.csv"), dtype=str)
    m = man[man["file"] == os.path.basename(path)].iloc[-1]
    return path, ip.utc_iso(pd.Timestamp(m["retrieved_at"])), m.get("last_modified")


def download(names, run_id, log, skip_saved=False):
    ip.RAW.open(CONNECTOR, run_id)
    for name in names:
        url = BASE + name
        if skip_saved and saved_copy(name):
            log(f"  {name}: a saved copy is held, not fetched again")
            continue
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=900)
                break
            except requests.RequestException as e:
                log(f"  {name}: {type(e).__name__} on try {attempt + 1}")
                if attempt == 2:
                    raise
        if r.status_code != 200 or not r.content.lstrip(b'\xef\xbb\xbf"').startswith(b"Balancing"):
            raise RuntimeError(f"{url}: HTTP {r.status_code}, {len(r.content)} bytes, not the CSV")
        log(f"downloaded {url}: {len(r.content):,} bytes, Last-Modified {r.headers.get('Last-Modified')}")
        print(f"  {name}: {len(r.content):,} bytes", flush=True)


def fmt(v):
    return "" if pd.isna(v) else f"{v:.10g}"


def read_file(path):
    want = ["Balancing Authority", "Region", "UTC Time at End of Hour"] + [c for r, a in VARS.values() for c in (r, a) if c]
    head = pd.read_csv(path, nrows=0).columns
    missing = [c for c in want if c not in head]
    if missing:
        raise RuntimeError(f"{os.path.basename(path)} has no column(s) {missing}")
    d = pd.read_csv(path, usecols=want, dtype=str, low_memory=False)
    d["ts"] = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    for r, a in VARS.values():
        for c in (r, a):
            if c:
                d[c] = pd.to_numeric(d[c].str.replace(",", ""), errors="coerce")
    return d.drop(columns=["UTC Time at End of Hour"])


def ba_rows(d, file_tag):
    parts = []
    for var, (r, a) in VARS.items():
        rep = d[r]
        adj = d[a] if a else pd.Series(float("nan"), index=d.index)
        val = adj.where(adj.notna(), rep)
        keep = val.notna()
        x = d[keep]
        parts.append(pd.DataFrame({
            "entity": "eia930:" + x["Balancing Authority"], "variable": var, "ts": x["ts"], "value": val[keep],
            "ba": x["Balancing Authority"].str.lower(), "x_region": x["Region"].fillna(""),
            "x_basis": (adj[keep].notna()).map({True: "adjusted", False: "reported"}),
            "x_value_reported": rep[keep], "x_value_adjusted": adj[keep], "x_bas": 1}))
    out = pd.concat(parts, ignore_index=True)
    out["x_file"] = file_tag
    return out


def region_rows(d, file_tag, after):
    """Sums by region and hour where every balancing authority listed has the variable; hours after `after` only.
    Returns the rows and, per variable, the region-hours left out for want of a value."""
    d = d[d["Region"].isin(REGIONS)]
    if after is not None:
        d = d[d["ts"] > after]
    parts, short = [], {}
    for var, (r, a) in VARS.items():
        rep = d[r]
        adj = d[a] if a else pd.Series(float("nan"), index=d.index)
        x = pd.DataFrame({"region": d["Region"], "ts": d["ts"], "val": adj.where(adj.notna(), rep), "rep": rep, "adj": adj})
        g = x.groupby(["region", "ts"])
        agg = pd.DataFrame({"n": g.size(), "n_val": g["val"].count(), "n_rep": g["rep"].count(), "n_adj": g["adj"].count(),
                            "val": g["val"].sum(), "rep": g["rep"].sum(), "adj": g["adj"].sum()}).reset_index()
        full = agg[agg["n_val"] == agg["n"]]
        short[var] = int((agg["n_val"] < agg["n"]).sum())
        basis = (full["n_adj"] == full["n"]).map({True: "adjusted", False: "mixed"}) if a else "reported"
        parts.append(pd.DataFrame({
            "entity": "eia930:" + full["region"], "variable": var, "ts": full["ts"], "value": full["val"],
            "ba": full["region"].str.lower(), "x_basis": basis,
            "x_value_reported": full["rep"].where(full["n_rep"] == full["n"]),
            "x_value_adjusted": full["adj"].where(full["n_adj"] == full["n"]) if a else float("nan"),
            "x_bas": full["n"]}))
    out = pd.concat(parts, ignore_index=True)
    out["x_file"] = file_tag
    return out, short


def to_csv_rows(df, cols):
    df = df.sort_values(["entity", "variable", "ts"])
    df["ts_utc"] = df["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    for c in ("value", "x_value_reported", "x_value_adjusted"):
        df[c] = df[c].map(fmt)
    df["unit"], df["freq"], df["source"] = "MW", "PT1H", SOURCE
    df["x_bas"] = df["x_bas"].astype(int)
    return df[cols]


def header_for(name, run_id, title, variables, src_lines, extra, rows, tmin, tmax):
    return [
        f"Energy Research Warehouse (ERW): EIA-930 hourly, {title}, July 2018 to the newest hour, from EIA's six-month "
        "files (session 7801)",
        f"Shape: series (docs/datastandard.md v0), partition column ba (the code, lowercase). Variables: {', '.join(variables)}; "
        "MW (EIA's MWh per hour). ts_utc is the hour's start (the file's UTC Time at End of Hour minus one hour). value is "
        "EIA's adjusted value where the file prints one, else the value as reported (x_basis); x_value_reported and "
        "x_value_adjusted keep both. x_file names the six-month file each row was read from; the files are listed below. "
        "Method: docs/methods/eia930_region_hourly.md.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_region_hourly.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/<run>/ (not in git; manifest.csv lists each file and URL)",
        f"Source: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {PAGE}",
        *src_lines,
        *extra,
        "License: public (U.S. Energy Information Administration).",
        f"File holds {rows} rows, {tmin} to {tmax}. Rebuilt whole by this run from the files above. Per row, source and "
        "x_file say where it came from; earlier run logs are in warehouse/output/logs/.",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 regions and balancing authorities, hourly (session 7801)")
    ap.add_argument("--files", nargs="*", help="file names (default: 2018 Jul_Dec to the current half-year)")
    ap.add_argument("--download-only", action="store_true")
    ap.add_argument("--skip-saved", action="store_true", help="with a download: leave a file whose copy is saved")
    ap.add_argument("--from-raw", action="store_true", help="read the newest saved copies, download none")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    names = args.files or files_between()
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        if not args.from_raw:
            download(names, run_id, log, args.skip_saved)
        if args.download_only:
            log.close()
            return 0
        paths = {t: os.path.join(ip.OUT_DIR, t + ".csv") for t in TABLES}
        for t, p in paths.items():
            ip._require_lock(p, f"writing {t}")
        handles = {t: open(p + ".body", "w", encoding="utf-8", newline="") for t, p in paths.items()}
        stats = {t: dict(rows=0, tmin=None, tmax=None) for t in TABLES}
        src_lines, short_total = [], {v: 0 for v in VARS}
        carry, last_region = None, None
        try:
            for t, h in handles.items():
                csv.writer(h, lineterminator="\n").writerow(TABLES[t][0])
            for name in names:
                got = saved_copy(name)
                if not got:
                    raise RuntimeError(f"no saved copy of {name}: run with --download-only first")
                fpath, retrieved, lm = got
                d = read_file(fpath)
                b = ba_rows(d, tag(name))
                both = d if carry is None else pd.concat([carry, d], ignore_index=True)
                last = name == names[-1]
                cut = None if last else d["ts"].max() - CARRY
                rg, short = region_rows(both if cut is None else both[both["ts"] <= cut], tag(name), last_region)
                for v, n in short.items():
                    short_total[v] += n
                if len(rg):
                    last_region = rg["ts"].max()
                carry = None if last else d[d["ts"] > d["ts"].max() - pd.Timedelta(hours=60)]
                counts = []
                for t, (cols, level, variables, _) in TABLES.items():
                    src = rg if level == "region" else b
                    part = to_csv_rows(src[src["variable"].isin(variables)].copy(), cols)
                    part.to_csv(handles[t], header=False, index=False, lineterminator="\n")
                    s = stats[t]
                    s["rows"] += len(part)
                    if len(part):
                        lo, hi = part["ts_utc"].min(), part["ts_utc"].max()
                        s["tmin"], s["tmax"] = min(s["tmin"] or lo, lo), max(s["tmax"] or hi, hi)
                    counts.append(f"{t} {len(part):,}")
                src_lines.append(f"  file: {BASE + name} (x_file {tag(name)}; Last-Modified {lm}; downloaded {retrieved})")
                log(f"{name}: {'; '.join(counts)}; region-hours short of a value {short}")
                print(f"  {name}: {'; '.join(counts)}", flush=True)
        finally:
            for h in handles.values():
                h.close()
        short_line = ("Region-hours not written because a balancing authority of the region had no value: "
                      + ", ".join(f"{v} {n:,}" for v, n in short_total.items()) + ".")
        for t, (cols, level, variables, title) in TABLES.items():
            s, p = stats[t], paths[t]
            extra = [short_line, "A region's row is the sum of its balancing authorities' rows of the hour, written only when "
                     "every one the files list in the region for that hour has a value; x_bas: how many."] if level == "region" else []
            header = header_for(t, run_id, title, variables, src_lines, extra, s["rows"], s["tmin"], s["tmax"])
            with open(p + ".tmp", "w", encoding="utf-8", newline="") as f:
                for line in header:
                    f.write("# " + line + "\n")
                with open(p + ".body", "r", encoding="utf-8") as src:
                    for block in iter(lambda: src.read(1 << 22), ""):
                        f.write(block)
            os.replace(p + ".tmp", p)
            os.remove(p + ".body")
            summary = f"{t}.csv: rows={s['rows']} range={s['tmin']}..{s['tmax']} files={len(names)}"
            log("  " + summary)
            print(summary)
            results.append(dict(table=t, market="all", status="ok", detail=f"{s['rows']} rows from {len(names)} files"))
        ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                report="EIA-930 six-month files (Hourly Electric Grid Monitor)", report_url=PAGE,
                                document_list=BASE, license="public", tables=list(TABLES))])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=",".join(TABLES), market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.download_only:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
