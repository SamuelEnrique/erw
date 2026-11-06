#!/usr/bin/env python3
"""The ISO interconnection queues summarized from their own snapshots: MW and requests by grid, status and fuel group at
each snapshot; MW entered, withdrawn and completed by year from the queues' own dates; and the median months from request
to in-service by grid and request year (session 2953, chain 157).

Energy Research Warehouse (ERW). One derived table, iso_queue_snapshot_summary, from the six ISO queue snapshots the
warehouse holds (caiso_, ercot_, isone_, miso_, nyiso_ and spp_interconnection_queue, warehouse/connectors/iso_queues.py
via gridstatus; MISO's table is held as it was before the pause and no request is made to MISO). It is not session 95's
interconnection_queue_summary, which summarizes Berkeley Lab's queue file. Method: docs/methods/iso_queue_snapshot_summary.md.

    python warehouse/derived/iso_queue_snapshot_summary.py               # the table (data lock)
    python warehouse/derived/iso_queue_snapshot_summary.py --out-dir DIR # a trial

    entity    iso_queue:<grid>:<fuel group> (the snapshot, ts_utc its retrieval day) and iso_queue:<grid> (by year,
              ts_utc the year's first day, freq P1Y)
    variables the snapshot: <status>_mw and <status>_count for active, completed, withdrawn and unknown (status blank)
              by year: entered_mw (queue date), completed_mw (in-service date of a completed request, on or before the snapshot:
              SPP's column holds requested dates too), withdrawn_mw (withdrawn date), each
              with _count; median_months_to_in_service and in_service_dated (the requests of that request year with both
              a queue date and an in-service date; the median only at 5 or more, as session 95's table writes one)
Each table holds one snapshot (its next pull replaces it), so withdrawals between two snapshots are not counted: the
queues' own withdrawn dates stand for them. Nothing is filled.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "iso_queue_snapshot_summary"
SOURCE = "erw:iso_queue_snapshot_summary"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/iso_queue_snapshot_summary.md"
GRIDS = ("caiso", "ercot", "isone", "miso", "nyiso", "spp")
MIN_DATED = 5
# the queues' fuel labels to one group, the first rule that matches (case ignored); the method note lists the labels
FUEL_RULES = [("solar_storage", r"(solar|photovoltaic|\bsun\b|pv).*(stor|batt|\bbat\b)|(stor|batt|\bbat\b).*(solar|photovoltaic|\bsun\b|pv)"),
              ("wind_storage", r"wind.*(stor|batt)|(stor|batt).*wind"),
              ("storage", r"stor|batt|\bbat\b|\bbes\b|\bes\b"),
              ("solar", r"solar|photovoltaic|\bsun\b|\bpv\b"),
              ("wind", r"wind|\bwnd\b|\bwt\b"),
              ("gas", r"gas|\bng\b|combustion|combined.?cycle|\bcc\b|\bct\b"),
              ("nuclear", r"nuclear|\bnuc\b|\buran"),
              ("hydro", r"hydro|\bwat\b|pumped"),
              ("hybrid", r"hybrid")]
COLS = ip.SERIES_COLS + ["x_grid", "x_fuel_group", "x_snapshot"]


def fuel_group(label):
    t = str(label or "").strip()
    if not t:
        return "unknown"
    for g, rx in FUEL_RULES:
        if re.search(rx, t, re.I):
            return g
    return "other"


def read(folder, grid):
    p = os.path.join(folder, f"{grid}_interconnection_queue.csv")
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    d["mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
    d["fuel"] = d["fuel_technology"].map(fuel_group)
    d["st"] = d["status"].replace("", "unknown")
    for c in ("queue_date", "actual_in_service_date", "withdrawn_date"):
        d[c[:3]] = pd.to_datetime(d[c].str[:10], errors="coerce", format="%Y-%m-%d")
    return d


def row(ent, var, ts, val, unit, freq, grid, fuel, snap):
    return {"entity": ent, "variable": var, "ts_utc": ts, "value": val, "unit": unit, "freq": freq, "geo": "US", "market": "", "node": "",
            "source": SOURCE, "source_url": METHOD_URL, "vintage": snap, "x_grid": grid, "x_fuel_group": fuel, "x_snapshot": snap}


def build_grid(d, grid):
    snap = d["retrieved_at"].str[:10].max()
    ts = f"{snap}T00:00:00Z"
    out = []
    # an in-service date counts only on a completed request and on or before the snapshot's day: SPP's column holds the
    # requested dates of active and withdrawn requests too, most of them in the future (session 2953)
    done = d["act"].notna() & (d["st"] == "completed") & (d["act"] <= pd.Timestamp(snap))
    d = d.assign(act=d["act"].where(done))
    for (fuel, st), g in d.groupby(["fuel", "st"]):
        out.append(row(f"iso_queue:{grid}:{fuel}", f"{st}_mw", ts, round(float(g["mw"].sum()), 3), "MW", "", grid, fuel, snap))
        out.append(row(f"iso_queue:{grid}:{fuel}", f"{st}_count", ts, int(len(g)), "count", "", grid, fuel, snap))
    for var, col in (("entered", "que"), ("completed", "act"), ("withdrawn", "wit")):
        x = d[d[col].notna()]
        for y, g in x.groupby(x[col].dt.year):
            yt = f"{int(y)}-01-01T00:00:00Z"
            out.append(row(f"iso_queue:{grid}", f"{var}_mw", yt, round(float(g["mw"].sum()), 3), "MW", "P1Y", grid, "", snap))
            out.append(row(f"iso_queue:{grid}", f"{var}_count", yt, int(len(g)), "count", "P1Y", grid, "", snap))
    x = d[d["que"].notna() & d["act"].notna() & (d["act"] >= d["que"])].copy()
    x["months"] = (x["act"] - x["que"]).dt.days / 30.4375
    for y, g in x.groupby(x["que"].dt.year):
        yt = f"{int(y)}-01-01T00:00:00Z"
        out.append(row(f"iso_queue:{grid}", "in_service_dated", yt, int(len(g)), "count", "P1Y", grid, "", snap))
        if len(g) >= MIN_DATED:
            out.append(row(f"iso_queue:{grid}", "median_months_to_in_service", yt, round(float(g["months"].median()), 1), "month", "P1Y", grid, "", snap))
    return out, snap


def build(folder=None):
    folder = folder or ip.OUT_DIR
    rows, snaps = [], {}
    for grid in GRIDS:
        r, snaps[grid] = build_grid(read(folder, grid), grid)
        rows += r
    t = pd.DataFrame(rows, columns=COLS)
    return t.sort_values(["entity", "ts_utc", "variable"]).reset_index(drop=True), snaps


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the ISO queues summarized from their own snapshots (session 2953)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder")
    a = ap.parse_args(argv)
    folder = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        t, snaps = build(folder)
        t["retrieved_at"] = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        header = [
            "Energy Research Warehouse (ERW): the ISO interconnection queues summarized from their own snapshots: MW and requests by grid, status and fuel group; entered, completed and withdrawn by year; months from request to in-service (derived, session 2953)",
            "Shape: series (docs/datastandard.md v0). entity iso_queue:<grid>:<fuel group> (the snapshot, ts_utc its day) or iso_queue:<grid> (by year, freq P1Y); "
            "variables <status>_mw and _count; entered_, completed_, withdrawn_ (mw and count); in_service_dated; median_months_to_in_service (at 5 or more dated requests).",
            "Snapshots: " + "; ".join(f"{g} {s}" for g, s in snaps.items()) + ". One snapshot a grid: withdrawals between snapshots are not counted; the queues' own withdrawn dates stand for them.",
            "Fuel groups: the queues' labels by the first matching rule of FUEL_RULES (docs/methods/iso_queue_snapshot_summary.md lists them). MISO's table is held as it was before the MISO pause; no request was made.",
            "Derived from: " + "; ".join(f"{g}_interconnection_queue" for g in GRIDS),
            "Built by warehouse/derived/iso_queue_snapshot_summary.py; method docs/methods/iso_queue_snapshot_summary.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: the ISOs' interconnection queues as gridstatus reads them (CAISO, ERCOT, ISO-NE, MISO, NYISO, SPP)",
            "License: public, as its six inputs are in the ERW's record.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The ISO interconnection queues summarized from their own snapshots (docs/methods/iso_queue_snapshot_summary.md)",
                                    report_url=METHOD_URL, document_list="docs/methods/iso_queue_snapshot_summary.md", license="public", tables=[NAME])])
        print(f"{NAME}: {len(t)} rows; snapshots {snaps}")
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
