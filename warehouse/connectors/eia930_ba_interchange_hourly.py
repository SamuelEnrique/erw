#!/usr/bin/env python3
"""EIA-930 hourly interchange between each pair of directly connected balancing authorities, each side's report its
own row, July 2018 to the newest hour, and the region pairs summed from it (session 7801, chain 401 part C, tables 2
and 3).

Energy Research Warehouse (ERW) connector. Writes two series tables from one read of the files:

    warehouse/output/eia930_ba_interchange_hourly.csv   one row per reporting BA, counterpart and hour (table 2)
    warehouse/output/eia930_region_pair_hourly.csv      one row per pair of EIA regions and hour (table 3, derived)

from EIA930_INTERCHANGE_<year>_<Jan_Jun|Jul_Dec>.csv (https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/), every
file from 2018 Jul_Dec to the current half-year. Public (U.S. Government data).

    python warehouse/connectors/eia930_ba_interchange_hourly.py --download-only [--skip-saved]
    python warehouse/connectors/eia930_ba_interchange_hourly.py --from-raw [--files ...] [--out-dir DIR]

Table 2. The file's rows are "Balancing Authority", "Directly Interconnected Balancing Authority" (DIBA), "Interchange
(MW)", the hour and both regions. A row of the table is one balancing authority's report about one neighbour: entity
eia930:<BA>-<DIBA>, variable interchange_mw, value as the reporting BA filed it (positive: the reporting BA sends power
to the neighbour, EIA's sign). The neighbour's own report about the same tie is its own row (eia930:<DIBA>-<BA>). Nothing
is netted, averaged or made to agree: the two sides often differ. ts_utc is the hour's start (UTC Time at End of Hour
minus one hour). An hour without a value is not written. Columns ba (the reporting BA, lowercase), x_diba, x_region,
x_diba_region, x_file (the six-month file).

Table 3 (derived from table 2's rows). For each pair of different regions with at least one tie, first region before
second by EIA's code, and each hour: the first region's report, the sum of every report a BA of the first region filed
about a BA of the second; and the second region's report, the sum of every report a BA of the second filed about a BA
of the first, its sign turned so that both read as power sent from the first region to the second. A side is summed
only when every tie between the two regions that appears in the files in that hour has that side's value; otherwise
the side is empty. x_first_report and x_second_report keep the two sides; x_gap is first less second where both are
held; value is the first region's side where held, else the second's (x_basis). A pair-hour with neither side whole is
not written. Method: docs/methods/eia930_region_hourly.md.

The tables are rebuilt whole each run, one file at a time, written straight to CSV.
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

CONNECTOR = "eia930_ba_interchange_hourly"
BASE = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"
SOURCE = "eia:gridmonitor/sixMonthFiles"
PAIR_SOURCE = "erw:eia930_ba_interchange_hourly"
BA_TABLE, PAIR_TABLE = "eia930_ba_interchange_hourly", "eia930_region_pair_hourly"
BA_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "ba", "x_diba", "x_region", "x_diba_region", "x_file"]
PAIR_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_first", "x_second", "x_basis",
             "x_first_report", "x_second_report", "x_gap", "x_ties", "x_file"]
CARRY = pd.Timedelta(hours=30)
RAW_READ = ip.RAW_DIR  # before any --out-dir: a trial reads this checkout's saved copies, read only


def files_between(first=(2018, 2), today=None):
    today = today or dt.date.today()
    out, (y, h) = [], first
    while (y, h) <= (today.year, 1 if today.month <= 6 else 2):
        out.append(f"EIA930_INTERCHANGE_{y}_{'Jan_Jun' if h == 1 else 'Jul_Dec'}.csv")
        y, h = (y, 2) if h == 1 else (y + 1, 1)
    return out


def tag(name):
    return name.replace("EIA930_INTERCHANGE_", "").replace(".csv", "")


def saved_copy(name):
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
    want = ["Balancing Authority", "Directly Interconnected Balancing Authority", "Interchange (MW)",
            "UTC Time at End of Hour", "Region", "DIBA_Region"]
    head = pd.read_csv(path, nrows=0).columns
    missing = [c for c in want if c not in head]
    if missing:
        raise RuntimeError(f"{os.path.basename(path)} has no column(s) {missing}")
    d = pd.read_csv(path, usecols=want, dtype=str, low_memory=False)
    d = d.rename(columns={"Balancing Authority": "ba", "Directly Interconnected Balancing Authority": "diba",
                          "Interchange (MW)": "v", "Region": "region", "DIBA_Region": "diba_region"})
    d["ts"] = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    d["v"] = pd.to_numeric(d["v"].str.replace(",", ""), errors="coerce")
    for c in ("region", "diba_region"):
        d[c] = d[c].fillna("")
    return d.drop(columns=["UTC Time at End of Hour"])


def ba_rows(d, file_tag):
    x = d[d["v"].notna()].sort_values(["ba", "diba", "ts"])
    return pd.DataFrame({
        "entity": "eia930:" + x["ba"] + "-" + x["diba"], "variable": "interchange_mw",
        "ts_utc": x["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": x["v"].map(fmt), "unit": "MW", "freq": "PT1H",
        "source": SOURCE, "ba": x["ba"].str.lower(), "x_diba": x["diba"], "x_region": x["region"],
        "x_diba_region": x["diba_region"], "x_file": file_tag})[BA_COLS]


def pair_rows(d, file_tag, after):
    """Region pairs by hour (see the module docstring); hours after `after` only."""
    d = d[(d["region"] != "") & (d["diba_region"] != "") & (d["region"] != d["diba_region"])]
    if after is not None:
        d = d[d["ts"] > after]
    first = d["region"] < d["diba_region"]
    d = d.assign(r1=d["region"].where(first, d["diba_region"]), r2=d["diba_region"].where(first, d["region"]),
                 side=first.map({True: "first", False: "second"}),
                 sv=d["v"].where(first, -d["v"]))  # both sides as power from the first region to the second
    g = d.groupby(["r1", "r2", "ts", "side"])
    agg = pd.DataFrame({"n": g.size(), "n_val": g["sv"].count(), "s": g["sv"].sum()}).reset_index()
    agg["whole"] = agg["n"] == agg["n_val"]
    w = agg.pivot_table(index=["r1", "r2", "ts"], columns="side", values=["s", "whole", "n"], aggfunc="first")
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w.reset_index()
    for c in ("s_first", "s_second", "whole_first", "whole_second", "n_first", "n_second"):
        if c not in w:
            w[c] = float("nan") if c.startswith(("s_", "n_")) else False
    f_ok = w["whole_first"].eq(True)
    s_ok = w["whole_second"].eq(True)
    fr = w["s_first"].where(f_ok)
    sr = w["s_second"].where(s_ok)
    keep = f_ok | s_ok
    w, fr, sr, f_ok = w[keep], fr[keep], sr[keep], f_ok[keep]
    w = w.assign(value=fr.where(f_ok, sr), basis=f_ok.map({True: "first", False: "second"}), fr=fr, sr=sr, gap=fr - sr,
                 ties=w[["n_first", "n_second"]].max(axis=1).fillna(0).astype(int))
    w = w.sort_values(["r1", "r2", "ts"])
    out = pd.DataFrame({
        "entity": "eia930:" + w["r1"] + "-" + w["r2"], "variable": "interchange_mw", "ts": w["ts"],
        "ts_utc": w["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": w["value"].map(fmt), "unit": "MW", "freq": "PT1H",
        "source": PAIR_SOURCE, "x_first": w["r1"], "x_second": w["r2"], "x_basis": w["basis"],
        "x_first_report": w["fr"].map(fmt), "x_second_report": w["sr"].map(fmt), "x_gap": w["gap"].map(fmt),
        "x_ties": w["ties"], "x_file": file_tag})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 interchange by BA pair and by region pair, hourly (session 7801)")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--download-only", action="store_true")
    ap.add_argument("--skip-saved", action="store_true")
    ap.add_argument("--from-raw", action="store_true")
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
        # table 2 is one table per UTC year of the hour (eia930_ba_interchange_hourly_<year>, as eia930_subba_demand_hourly
        # is, session 612): about 2.6 million rows a year; one table of every year would be more than the validator reads
        paths = {PAIR_TABLE: os.path.join(ip.OUT_DIR, PAIR_TABLE + ".csv")}
        ip._require_lock(paths[PAIR_TABLE], f"writing {PAIR_TABLE}")
        h = {PAIR_TABLE: open(paths[PAIR_TABLE] + ".body", "w", encoding="utf-8", newline="")}
        stats = {PAIR_TABLE: dict(rows=0, tmin=None, tmax=None)}
        files_of = {PAIR_TABLE: []}
        src_lines, carry, last_pair = [], None, None

        def year_table(year):
            t = f"{BA_TABLE}_{year}"
            if t not in h:
                paths[t] = os.path.join(ip.OUT_DIR, t + ".csv")
                ip._require_lock(paths[t], f"writing {t}")
                h[t] = open(paths[t] + ".body", "w", encoding="utf-8", newline="")
                csv.writer(h[t], lineterminator="\n").writerow(BA_COLS)
                stats[t], files_of[t] = dict(rows=0, tmin=None, tmax=None), []
            return t

        try:
            csv.writer(h[PAIR_TABLE], lineterminator="\n").writerow(PAIR_COLS)
            for name in names:
                got = saved_copy(name)
                if not got:
                    raise RuntimeError(f"no saved copy of {name}: run with --download-only first")
                fpath, retrieved, lm = got
                d = read_file(fpath)
                b = ba_rows(d, tag(name))
                last = name == names[-1]
                both = d if carry is None else pd.concat([carry, d], ignore_index=True)
                cut = None if last else d["ts"].max() - CARRY
                pr = pair_rows(both if cut is None else both[both["ts"] <= cut], tag(name), last_pair)
                if len(pr):
                    last_pair = pr["ts"].max()
                carry = None if last else d[d["ts"] > d["ts"].max() - pd.Timedelta(hours=60)]
                pr = pr[PAIR_COLS]
                pieces = [(year_table(y), part) for y, part in b.groupby(b["ts_utc"].str[:4], sort=True)] + [(PAIR_TABLE, pr)]
                for t, part in pieces:
                    if name not in files_of[t]:
                        files_of[t].append(name)
                    part.to_csv(h[t], header=False, index=False, lineterminator="\n")
                    s = stats[t]
                    s["rows"] += len(part)
                    if len(part):
                        lo, hi = part["ts_utc"].min(), part["ts_utc"].max()
                        s["tmin"], s["tmax"] = min(s["tmin"] or lo, lo), max(s["tmax"] or hi, hi)
                src_lines.append((name, f"  file: {BASE + name} (x_file {tag(name)}; Last-Modified {lm}; downloaded {retrieved})"))
                log(f"{name}: {len(b):,} BA rows, {len(pr):,} region pair rows")
                print(f"  {name}: {len(b):,} BA rows, {len(pr):,} region pair rows", flush=True)
        finally:
            for f in h.values():
                f.close()
        heads = {
            BA_TABLE: [
                "Energy Research Warehouse (ERW): EIA-930 hourly interchange between each pair of directly connected balancing "
                "authorities, each side's report its own row, July 2018 to the newest hour, from EIA's six-month files (session 7801)",
                "Shape: series (docs/datastandard.md v0), partition column ba (the reporting balancing authority, lowercase). "
                "entity eia930:<reporting BA>-<neighbour>, variable interchange_mw, MW as the reporting BA filed it (positive: "
                "it sends power to the neighbour). The neighbour's report is its own row; nothing is netted, averaged or made to "
                "agree. ts_utc is the hour's start. x_file names the six-month file each row was read from. Method: "
                "docs/methods/eia930_region_hourly.md.",
                f"Source: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {PAGE}"],
            PAIR_TABLE: [
                "Energy Research Warehouse (ERW): EIA-930 hourly interchange between each pair of EIA's regions of the lower 48, "
                "each region's report summed from its balancing authorities' reports, July 2018 to the newest hour (session 7801)",
                "Shape: series (docs/datastandard.md v0). entity eia930:<first region>-<second region> (first before second by "
                "EIA's code), variable interchange_mw, MW sent from the first region to the second. x_first_report: the sum of "
                "every report a BA of the first region filed about a BA of the second; x_second_report: the same for the second "
                "region, its sign turned; each written only when every tie that appears in the hour has that side's value. x_gap: "
                "first less second. value: the first side where held, else the second (x_basis). Derived from "
                "eia930_ba_interchange_hourly; method docs/methods/eia930_region_hourly.md.",
                f"Source: {PAIR_SOURCE} the ERW's eia930_ba_interchange_hourly, summed by region pair, "
                "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_region_hourly.md",
                f"  read from: {SOURCE} EIA-930 six-month files (Hourly Electric Grid Monitor), {PAGE}"],
        }
        for t, p in paths.items():
            s = stats[t]
            kind = BA_TABLE if t.startswith(BA_TABLE + "_") else t
            lines = [line for n, line in src_lines if n in files_of[t]]
            year_note = ([f"This table holds the hours of {t[-4:]} (UTC); the other years are {BA_TABLE}_<year>, one table a year "
                          "because all of them in one would be more than the validator reads in memory."] if kind == BA_TABLE else [])
            header = heads[kind] + year_note + [
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_ba_interchange_hourly.py",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/<run>/ (not in git; manifest.csv lists each file and URL)",
                *lines,
                "License: public (U.S. Energy Information Administration)." if kind == BA_TABLE else
                "License: public (derived by the ERW from U.S. Energy Information Administration data).",
                f"File holds {s['rows']} rows, {s['tmin']} to {s['tmax']}. Rebuilt whole by this run from the files above. Per row, "
                "source and x_file say where it came from; earlier run logs are in warehouse/output/logs/."]
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
        ip.update_sources([
            dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                 report="EIA-930 six-month files (Hourly Electric Grid Monitor)", report_url=PAGE, document_list=BASE,
                 license="public", tables=sorted(t for t in paths if t.startswith(BA_TABLE + "_"))),
            dict(source=PAIR_SOURCE, publisher="Energy Research Warehouse (from U.S. Energy Information Administration data)",
                 report="EIA-930 interchange summed by region pair",
                 report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_region_hourly.md",
                 document_list="", license="public", tables=[PAIR_TABLE])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=f"{BA_TABLE},{PAIR_TABLE}", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.download_only:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
