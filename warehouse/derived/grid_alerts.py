#!/usr/bin/env python3
"""ERW: every grid alert, watch and emergency notice the warehouse holds, in one events table, grid_all_alerts
(chain 601, part E, session 9000).

Energy Research Warehouse (ERW). Reads three held events tables and writes their rows in one shape; makes no request.
The chain named the table grid_alerts; the data standard asks a name of three parts (source_market_product), so it is
grid_all_alerts. Method: docs/methods/grid_alerts.md.

    caiso_grid_emergencies   CAISO's grid emergencies history (1998 on): alerts, warnings, Flex Alerts and Power
                             Watches, Restricted Maintenance Operations, stages 1 to 3, transmission emergencies
    ercot_grid_notices       ERCOT's notices (2011 on): weather watches, conservation appeals, EEA levels, rotating
                             outages, as its news releases print them
    doe_oe417_events         the federal Electric Emergency Incident and Disturbance Reports (2016 on), every
                             authority, with the area affected as filed

Each row keeps its source table's event_id, date, type and source document. x_kind is the source's own words for the
kind (CAISO's label, ERCOT's headline label, OE-417's event type as published); x_grid is the grid (caiso, ercot) or
the NERC region of an OE-417 report; x_start and x_end are the source's own start and end where it prints them.
/grid/caiso/alerts keeps reading caiso_grid_emergencies; nothing of that table changes.

    python warehouse/derived/grid_alerts.py                 # the table
    python warehouse/derived/grid_alerts.py --out-dir DIR   # a trial
"""
import argparse
import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

TABLE = "grid_all_alerts"
INPUTS = ["caiso_grid_emergencies", "ercot_grid_notices", "doe_oe417_events"]
COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
        "source_url", "x_input_table", "x_grid", "x_kind", "x_start", "x_end", "x_area"]
METHOD = "docs/methods/grid_alerts.md"


def read(name):
    p = os.path.join(ip.OUT_DIR, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, dtype=str, keep_default_na=False)
    fh.close()
    return d


def col(d, c):
    return d[c] if c in d.columns else ""


def caiso(d):
    return pd.DataFrame({
        "event_id": d["event_id"], "event_date": d["event_date"], "event_type": d["event_type"],
        "parties": d["parties"], "entity_ids": d["entity_ids"], "mw": d["mw"], "price": d["price"],
        "currency": d["currency"], "status": d["status"], "source": d["source"], "source_url": d["source_url"],
        "x_input_table": "caiso_grid_emergencies", "x_grid": "caiso", "x_kind": col(d, "x_label"),
        "x_start": col(d, "x_start"), "x_end": col(d, "x_end"), "x_area": col(d, "x_region")})


def ercot(d):
    return pd.DataFrame({
        "event_id": d["event_id"], "event_date": d["event_date"], "event_type": d["event_type"],
        "parties": d["parties"], "entity_ids": d["entity_ids"], "mw": d["mw"], "price": d["price"],
        "currency": d["currency"], "status": d["status"], "source": d["source"], "source_url": d["source_url"],
        "x_input_table": "ercot_grid_notices", "x_grid": "ercot", "x_kind": col(d, "x_label"),
        "x_start": col(d, "x_issued_at"), "x_end": "", "x_area": col(d, "x_region")})


def oe417(d):
    start = (col(d, "x_begin_date") + " " + col(d, "x_begin_time")).str.strip()
    end = (col(d, "x_restoration_date") + " " + col(d, "x_restoration_time")).str.strip()
    return pd.DataFrame({
        "event_id": d["event_id"], "event_date": d["event_date"], "event_type": d["event_type"],
        "parties": d["parties"], "entity_ids": d["entity_ids"], "mw": d["mw"], "price": d["price"],
        "currency": d["currency"], "status": d["status"], "source": d["source"], "source_url": d["source_url"],
        "x_input_table": "doe_oe417_events", "x_grid": col(d, "x_nerc_region"),
        "x_kind": col(d, "x_event_type_as_published"), "x_start": start, "x_end": end,
        "x_area": col(d, "x_area_affected")})


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: grid alerts in one table")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    src = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    out = ip.OUT_DIR
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(out, "logs", f"grid_alerts_{run_id}.log"))
    ip.OUT_DIR = src
    parts = [caiso(read("caiso_grid_emergencies")), ercot(read("ercot_grid_notices")), oe417(read("doe_oe417_events"))]
    ip.OUT_DIR = out
    rows = pd.concat(parts, ignore_index=True).sort_values(["event_date", "event_id"]).reset_index(drop=True)
    if rows["event_id"].duplicated().any():
        raise RuntimeError(f"an event_id repeats: {rows[rows['event_id'].duplicated()]['event_id'].head(3).tolist()}")
    counts = rows.groupby("x_input_table").size().to_dict()
    header = [
        "Energy Research Warehouse (ERW): every grid alert, watch and emergency notice the warehouse holds, one table "
        "(derived, chain 601 session 9000)",
        "Shape: events (docs/datastandard.md v0). event_date is the date the source gives the event; x_kind is the "
        "source's own words for its kind; x_start and x_end are the source's own start and end where printed.",
        f"Rows by input: {', '.join(f'{k} {v}' for k, v in sorted(counts.items()))}.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/grid_alerts.py",
        "Source: erw:grid_all_alerts ERW derived table, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_alerts.md",
        "Derived from: " + "; ".join(INPUTS),
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): CAISO "
        "(credit the California ISO), ERCOT (unmodified, notices kept), DOE OE-417 (public domain).",
        f"Method: {METHOD}",
    ]
    ip.write_csv(rows[COLS], TABLE, header, log, cols=COLS, key=["event_id"], time_col="event_date")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
