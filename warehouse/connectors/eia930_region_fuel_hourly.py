#!/usr/bin/env python3
"""EIA-930 hourly net generation by energy source for each of EIA's thirteen regions of the lower 48, July 2018 to the
newest hour, from EIA's six-month files (session 8001, chain 501 step B5).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia930_region_fuel_hourly.csv. Method:
docs/methods/eia930_region_fuel_hourly.md.

    python warehouse/connectors/eia930_region_fuel_hourly.py                      # every saved six-month file (data lock)
    python warehouse/connectors/eia930_region_fuel_hourly.py --files EIA930_BALANCE_2026_Jul_Dec.csv   # merged into the table
    python warehouse/connectors/eia930_region_fuel_hourly.py --out-dir DIR        # a trial

No request is made. The files are the copies eia930_region_hourly.py saved (warehouse/raw/eia930_region_hourly/), the
newest copy of each; that connector's --download-only fetches a newer one. Chain 401 kept each balancing authority's
demand, net generation and interchange from these files and left their energy source columns; this table reads them.

THE SOURCES. The eight of the site's energy mix (site/data/mix/*.json, generation_mix_hourly_profile), from EIA's columns
"Net Generation (MW) from <source>", each balancing authority's value EIA's adjusted column where it prints one, else
the column as reported:

    natural_gas  Natural Gas
    coal         Coal
    nuclear      Nuclear
    wind         Wind; from July 2024 Wind without and with Integrated Battery Storage
    solar        Solar; from July 2024 Solar without and with Integrated Battery Storage
    hydro        Hydropower and Pumped Storage; from July 2024 Hydropower Excluding Pumped Storage and Pumped Storage
    storage      from July 2024 Battery Storage, Other Energy Storage and Unknown Energy Storage (negative while charging;
                 before July 2024 EIA counts batteries under Other Fuel Sources, so storage is blank, not zero)
    other        All Petroleum Products, Other Fuel Sources and Unknown Fuel Sources; from July 2024 Geothermal too

A balancing authority's hour is HELD when its net generation (adjusted, else reported) is held, at least one source is
held, and its sources add up to its net generation within 5 percent of it, or within 1 MW for a small one (the rule of
mix_profile.hours_of at the level of one authority). A source the authority does not print that hour counts as zero in
the sum. A region's hour is written when every balancing authority the file lists in that region for that hour is held
(x_bas: how many); otherwise nothing is written for the region and hour, and the log counts it. Nothing is filled or
scaled. ts_utc is the hour's start (the file's UTC Time at End of Hour minus one hour); the last day and a half of each
file is carried into the next, as eia930_region_hourly.py does, so an hour split between two files is summed whole.
"""

import argparse
import csv
import datetime as dt
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "eia930_region_fuel_hourly"
CONNECTOR = "eia930_region_fuel_hourly"
RAW_FROM = "eia930_region_hourly"
SOURCE = "eia:gridmonitor/sixMonthFiles"
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"
BASE = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]
# EIA's source name (after "from ", without "(Adjusted)") to the site's source
MAP = {"coal": "coal", "natural gas": "natural_gas", "nuclear": "nuclear", "all petroleum products": "other",
       "hydropower and pumped storage": "hydro", "hydropower excluding pumped storage": "hydro", "pumped storage": "hydro",
       "solar": "solar", "solar without integrated battery storage": "solar", "solar with integrated battery storage": "solar",
       "wind": "wind", "wind without integrated battery storage": "wind", "wind with integrated battery storage": "wind",
       "battery storage": "storage", "other energy storage": "storage", "unknown energy storage": "storage",
       "geothermal": "other", "other fuel sources": "other", "unknown fuel sources": "other"}
NG_REP, NG_ADJ = "Net Generation (MW)", "Net Generation (MW) (Adjusted)"
TOL_SHARE, TOL_MW = 0.05, 1.0
CARRY = pd.Timedelta(hours=30)
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "ba", "x_bas", "x_file"]
RAW_READ = ip.RAW_DIR


def files_between(first=(2018, 2), today=None):
    today = today or dt.date.today()
    out, (y, h) = [], first
    while (y, h) <= (today.year, 1 if today.month <= 6 else 2):
        out.append(f"EIA930_BALANCE_{y}_{'Jan_Jun' if h == 1 else 'Jul_Dec'}.csv")
        y, h = (y, 2) if h == 1 else (y + 1, 1)
    return out


def tag(name):
    return name.replace("EIA930_BALANCE_", "").replace(".csv", "")


def saved_copy(name):
    found = sorted(glob.glob(os.path.join(RAW_READ, RAW_FROM, "*", f"*{name}")))
    if not found:
        return None
    path = found[-1]
    man = pd.read_csv(os.path.join(os.path.dirname(path), "manifest.csv"), dtype=str)
    m = man[man["file"] == os.path.basename(path)].iloc[-1]
    return path, ip.utc_iso(pd.Timestamp(m["retrieved_at"])), m.get("last_modified"), m.get("url", BASE + name)


def source_of(col):
    """(site source, adjusted?) of an EIA column name, or None. EIA's file of July to December 2024 prints one adjusted
    column as 'Solar witho Integrated Battery Storage'; a doubled space is read as one."""
    m = re.match(r"^Net Generation \(MW\) from (.+?)\s*(\((Adjusted|Imputed)\))?$", col.strip())
    if not m or m.group(3) == "Imputed":
        return None
    name = re.sub(r"\s+", " ", m.group(1)).strip().lower().replace("witho integrated", "with integrated")
    s = MAP.get(name)
    return (s, m.group(3) == "Adjusted", name) if s else None


def read_file(path):
    head = list(pd.read_csv(path, nrows=0).columns)
    cols = {c: source_of(c) for c in head}
    fuel = {c: v for c, v in cols.items() if v}
    unknown = [c for c in head if c.startswith("Net Generation (MW) from") and "(Imputed)" not in c and not cols[c]]
    if unknown:
        raise RuntimeError(f"{os.path.basename(path)}: source column(s) not mapped: {unknown}")
    want = ["Balancing Authority", "Region", "UTC Time at End of Hour", NG_REP, NG_ADJ] + list(fuel)
    d = pd.read_csv(path, usecols=want, dtype=str, low_memory=False)
    d["ts"] = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    num = {c: pd.to_numeric(d[c].str.replace(",", ""), errors="coerce") for c in [NG_REP, NG_ADJ] + list(fuel)}
    out = pd.DataFrame({"ba": d["Balancing Authority"], "region": d["Region"], "ts": d["ts"]})
    out["ng"] = num[NG_ADJ].where(num[NG_ADJ].notna(), num[NG_REP])
    # each EIA source: adjusted where printed, else reported; then summed into the site's source
    by_name = {}
    for c, (s, adj, name) in fuel.items():
        by_name.setdefault(name, {})["adj" if adj else "rep"] = num[c]
    for s in SOURCES:
        parts = []
        for name, pair in by_name.items():
            if MAP[name] != s:
                continue
            rep, adj = pair.get("rep"), pair.get("adj")
            v = adj.where(adj.notna(), rep) if adj is not None and rep is not None else (adj if adj is not None else rep)
            parts.append(v)
        if parts:
            stack = pd.concat(parts, axis=1)
            out[s] = stack.sum(axis=1, min_count=1)
        else:
            out[s] = np.nan
    out["has_storage_cols"] = any(MAP[n] == "storage" for n in by_name)
    return out


def region_rows(d, file_tag, after, log):
    d = d[d["region"].isin(REGIONS)].copy()
    if after is not None:
        d = d[d["ts"] > after]
    src = d[SOURCES]
    total = src.sum(axis=1, min_count=1)
    held = d["ng"].notna() & total.notna() & ((total - d["ng"]).abs() <= np.maximum(TOL_SHARE * d["ng"].abs(), TOL_MW))
    d["held"] = held
    g = d.groupby(["region", "ts"])
    agg = g[SOURCES].sum(min_count=1)
    agg["n"], agg["n_held"] = g.size(), g["held"].sum()
    full = agg[agg["n_held"] == agg["n"]].reset_index()
    short = int((agg["n_held"] < agg["n"]).sum())
    storage_cols = bool(d["has_storage_cols"].any()) if len(d) else False
    parts = []
    for s in SOURCES:
        if s == "storage" and not storage_cols:
            continue          # before July 2024 batteries are in Other Fuel Sources: storage is blank, not zero
        v = full[s].fillna(0.0)   # a source no authority of the region prints that hour is zero in a held hour
        parts.append(pd.DataFrame({"entity": "eia930:" + full["region"], "variable": f"net_generation_{s}_mw", "ts": full["ts"],
                                   "value": v, "ba": full["region"].str.lower(), "x_bas": full["n"].astype(int)}))
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["entity", "variable", "ts", "value", "ba", "x_bas"])
    out["x_file"] = file_tag
    return out, short


def fmt(v):
    return "" if pd.isna(v) else f"{v:.10g}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 net generation by source, the thirteen regions, hourly (session 8001)")
    ap.add_argument("--files", nargs="*", help="file names (default: every file from 2018 Jul_Dec to the current half-year); "
                                               "with names, the rows are merged into the table")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    names = a.files or files_between()
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    ip._require_lock(path, f"writing {NAME}")
    parts, src_lines, short_total, carry, after = [], [], 0, None, None
    whole = not a.files
    for i, name in enumerate(names):
        got = saved_copy(name)
        if not got:
            raise RuntimeError(f"no saved copy of {name}: run eia930_region_hourly.py --download-only first")
        fpath, retrieved, lm, url = got
        d = read_file(fpath)
        if not whole and i == 0 and after is None:
            # merged into the table: the first hours of a file may lack the authorities whose local day began in the
            # file before it, so they are left as the whole build wrote them
            after = d["ts"].min() + CARRY
        both = d if carry is None else pd.concat([carry, d], ignore_index=True)
        cut = None if i == len(names) - 1 else d["ts"].max() - CARRY
        sel = both if cut is None else both[both["ts"] <= cut]
        rows, short = region_rows(sel, tag(name), after, log)
        after = sel["ts"].max() if len(sel) else after
        carry = None if cut is None else both[both["ts"] > cut]
        parts.append(rows)
        short_total += short
        src_lines.append(f"{name}: {url}, Last-Modified {lm}, saved {retrieved} ({os.path.relpath(fpath, ip.ROOT).replace(os.sep, '/')})")
        log(f"  {name}: {len(rows):,} rows, {short:,} region-hours left out (an authority not held)")
        print(f"  {name}: {len(rows):,} rows", flush=True)
    out = pd.concat(parts, ignore_index=True).drop_duplicates(["entity", "variable", "ts"], keep="last")
    out = out.sort_values(["entity", "variable", "ts"])
    out["ts_utc"] = out["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out["value"] = out["value"].map(fmt)
    out["unit"], out["freq"], out["source"] = "MW", "PT1H", SOURCE
    out = out[COLS]
    header = [
        "Energy Research Warehouse (ERW): EIA-930 hourly net generation by energy source, EIA's thirteen regions of the lower 48 (sums of their balancing authorities), July 2018 to the newest hour, from EIA's six-month files (session 8001, chain 501)",
        "Shape: series (docs/datastandard.md v0), partition column ba (the region, lowercase). Variables: net_generation_<source>_mw for natural_gas, coal, nuclear, wind, solar, hydro, storage (from July 2024 only) and other; MW. "
        "ts_utc is the hour's start. A region-hour is written when every balancing authority listed in the region that hour is held: its sources add up to its net generation within 5 percent (or 1 MW). x_bas: how many were summed. Method: docs/methods/eia930_region_fuel_hourly.md.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_region_fuel_hourly.py, from the copies warehouse/connectors/eia930_region_hourly.py saved (no request)",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {PAGE}",
        *src_lines,
        f"Left out: {short_total:,} region-hours where an authority of the region was not held.",
        "License: public (U.S. Energy Information Administration).",
    ]
    note = "Rebuilt whole by this run from the files above."
    if not whole and os.path.exists(path):
        # merged: the held rows of the same (entity, variable, ts_utc) are replaced, every other row kept
        fh = open(path, "rb")
        for _ in range(ip.header_rows(path)):
            fh.readline()
        old = pd.read_csv(fh, dtype=str, keep_default_na=False, engine="pyarrow")
        fh.close()
        key = old["entity"] + "|" + old["variable"] + "|" + old["ts_utc"]
        new_key = set(out["entity"] + "|" + out["variable"] + "|" + out["ts_utc"])
        kept = old[~key.isin(new_key)]
        note = (f"Merged by this run: {len(out)} rows written ({len(out) - (len(old) - len(kept))} new), {len(kept)} kept from earlier runs; "
                "the header's file lines name only this run's files, earlier runs' logs the rest.")
        out = pd.concat([kept[COLS], out.astype(str)], ignore_index=True).sort_values(["entity", "variable", "ts_utc"])
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for h in header + [f"File holds {len(out)} rows, {out['ts_utc'].min()} to {out['ts_utc'].max()}. {note}"]:
            f.write("# " + h + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    print(f"{NAME}.csv: rows={len(out)} range={out['ts_utc'].min()}..{out['ts_utc'].max()}")
    log(f"  {NAME}.csv: rows={len(out)}; {note}")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
