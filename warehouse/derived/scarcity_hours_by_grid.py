#!/usr/bin/env python3
"""Each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (session 254).

Energy Research Warehouse (ERW) derived table, public: warehouse/output/scarcity_hours_by_grid.csv. For each grid and
hour of the 36 whole months before the month of the run, in the grid's standard time (ERCOT: Central standard, UTC-6;
CAISO: Pacific standard, UTC-8), one row per variable:

    entity iso:ercot (hub HB_HUBAVG), iso:caiso (trading hub TH_SP15_GEN-APND)
        rt_intervals_ge_1000   the hour's real-time intervals (15-minute) priced at or above USD 1,000 per MWh, count;
                               x_detail "held=<n>": the intervals of the hour the warehouse holds
        rt_hour_ge_1000        1 when the mean of the hour's held real-time intervals is at or above USD 1,000, else 0
                               (the datacenter page's count: docs/methods/datacenter_pays_algorithm.md, 4.15)
        da_hour_ge_1000        1 when the hour's day-ahead price is at or above USD 1,000, else 0
        own_signal             the grid's own scarcity signal, 1 in force and 0 not, written only for an hour the
                               signal is held for:
                               ERCOT  its on-line reserve price adder (RTORPA, the ORDC adder) above zero: the hour's
                                      mean of ercot_rtm_price_adders `rtorpa_mean`; x_detail "rtorpa_mean=<USD per
                                      MWh>". ERCOT published the adder to 4 December 2025; no hour after it is written
                                      (the reliability deployment adder that follows is another thing, not joined).
                               CAISO  an Energy Emergency Alert (EEA Watch, EEA 1, 2 or 3) or an alert (Flex Alert; and
                                      the Alert, Warning and Stage notices of the years before May 2022) in force in
                                      any part of the hour, any region, from caiso_grid_emergencies; x_detail names
                                      every notice in force in the hour as <type>@<region>, the restricted maintenance
                                      and transmission notices too, which do not make the signal 1. Held for every
                                      hour of the window before the day CAISO's report was revised.

A price row is written only for an hour with at least one interval held: CAISO's real-time and day-ahead prices are
held from 1 September 2024, so its price rows begin there and its own signal runs the whole window. An hour without a
row is not held; it is not a zero. NYISO, ISO-NE, SPP and MISO are not in the table: their price tables need a license
from 21 October 2026 or are held (license_status.csv), and no table of their own signal (reserve shortage pricing) is
held. Rule: docs/methods/scarcity_hours_by_grid.md.

    python warehouse/derived/scarcity_hours_by_grid.py [--month YYYY-MM]   # the month of the run (default: this month)
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "scarcity_hours_by_grid"
SOURCE = "erw:scarcity_hours_by_grid"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md"
COLS = ip.SERIES_COLS + ["x_detail"]
LEVEL = 1000.0                                   # USD per MWh: the level of the page's count, one for every grid
MONTHS = 36
EEA = ("eea_watch", "eea1", "eea2", "eea3")
ALERTS = ("flex_alert", "alert", "warning", "stage1", "stage2", "stage3")
GRIDS = [
    # grid, geo, hours behind UTC in standard time, the local zone of its notices, node, the price tables (history, live)
    dict(grid="ercot", geo="US-TX", offset=6, node="HB_HUBAVG", rt_market="ercot_rtm", da_market="ercot_dam",
         rt_tables=["ercot_all_hub_prices_history", "iso_rtm_hub_prices"], da_tables=["ercot_all_hub_prices_history", "iso_dam_hub_prices"]),
    dict(grid="caiso", geo="US-CA", offset=8, node="TH_SP15_GEN-APND", rt_market="caiso_rtm", da_market="caiso_dam",
         rt_tables=["iso_hub_prices_history", "iso_rtm_hub_prices"], da_tables=["iso_hub_prices_history", "iso_dam_hub_prices"]),
]


def window(month, offset):
    """The first and the last hour (UTC, both included) of the 36 whole months before `month` (YYYY-MM), in a standard
    time `offset` hours behind UTC."""
    end = pd.Timestamp(f"{month}-01T00:00:00Z") + pd.Timedelta(hours=offset)
    start = (pd.Timestamp(f"{month}-01") - pd.DateOffset(months=MONTHS)).tz_localize("UTC") + pd.Timedelta(hours=offset)
    return start, end - pd.Timedelta(hours=1)


def read_prices(tables, market, node, start, end, in_dir=None):
    """The rows of one market and node in the window, from the history table and the live one, an interval once."""
    parts = []
    lo, hi = ip.utc_iso(start), ip.utc_iso(end + pd.Timedelta(hours=1))
    for t in tables:
        path = os.path.join(in_dir or ip.OUT_DIR, t + ".csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"{t} is not in {in_dir or ip.OUT_DIR}")
        for ch in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["ts_utc", "value", "market", "node"], dtype=str, keep_default_na=False, chunksize=400_000):
            ch = ch[(ch["market"] == market) & (ch["node"] == node) & (ch["ts_utc"] >= lo) & (ch["ts_utc"] < hi)]
            if len(ch):
                parts.append(ch[["ts_utc", "value"]])
    if not parts:
        return pd.DataFrame(columns=["ts_utc", "value"])
    d = pd.concat(parts).drop_duplicates("ts_utc", keep="first")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


def price_rows(rt, da):
    """[(variable, hour as ts_utc, value, x_detail)] from one grid's real-time intervals and day-ahead hours."""
    out = []
    if len(rt):
        rt = rt.assign(hour=rt["ts_utc"].str[:13] + ":00:00Z")
        for hour, g in rt.groupby("hour"):
            out.append(("rt_intervals_ge_1000", hour, int((g["value"] >= LEVEL).sum()), f"held={len(g)}"))
            out.append(("rt_hour_ge_1000", hour, int(g["value"].mean() >= LEVEL), ""))
    for ts, v in zip(da["ts_utc"], da["value"]):
        out.append(("da_hour_ge_1000", ts[:13] + ":00:00Z", int(v >= LEVEL), ""))
    return out


def ercot_signal(start, end, in_dir=None):
    """ERCOT's own signal by hour: RTORPA's hourly mean above zero, for the hours the adder is held."""
    path = os.path.join(in_dir or ip.OUT_DIR, "ercot_rtm_price_adders.csv")
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"], dtype=str, keep_default_na=False)
    lo, hi = ip.utc_iso(start), ip.utc_iso(end)
    d = d[(d["entity"] == "ercot:system") & (d["variable"] == "rtorpa_mean") & (d["ts_utc"] >= lo) & (d["ts_utc"] <= hi) & (d["value"] != "")]
    return [("own_signal", ts, int(float(v) > 0), f"rtorpa_mean={v}") for ts, v in zip(d["ts_utc"], d["value"])]


def notice_hours(notices, zone="America/Los_Angeles"):
    """{UTC hour: [type@region, ...]} for every hour a notice was in force in any part of. `notices` holds event_type,
    x_region, x_start and x_end (local clock, minute); a notice repeated on each day it covers is read once."""
    out = {}
    seen = set()
    for typ, region, a, b in zip(notices["event_type"], notices["x_region"], notices["x_start"], notices["x_end"]):
        if not a or not b or (typ, region, a, b) in seen:
            continue
        seen.add((typ, region, a, b))
        t0 = pd.Timestamp(a).tz_localize(zone, ambiguous=True, nonexistent="shift_forward").tz_convert("UTC")
        t1 = pd.Timestamp(b).tz_localize(zone, ambiguous=True, nonexistent="shift_forward").tz_convert("UTC")
        if t1 < t0:
            continue
        for h in pd.date_range(t0.floor("h"), t1.floor("h"), freq="h"):
            out.setdefault(ip.utc_iso(h), []).append(f"{typ}@{region}")
    return out


def caiso_signal(start, end, in_dir=None):
    """CAISO's own signal by hour, and the last hour it is held for: an EEA or an alert in force. The report is CAISO's
    whole history to its revision date, so every hour to the end of the window that lies before the report's newest
    day is held; an hour with no notice is 0."""
    path = os.path.join(in_dir or ip.OUT_DIR, "caiso_grid_emergencies.csv")
    n = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    with open(path, encoding="utf-8") as f:
        revised = next((ln.split("revision date ")[1].strip() for ln in f if ln.startswith("#") and "revision date " in ln), "")
    held_to = pd.Timestamp(dt.datetime.strptime(revised, "%m/%d/%Y")).tz_localize("UTC") if revised else pd.Timestamp(n["event_date"].max()).tz_localize("UTC")
    last = min(end, held_to - pd.Timedelta(hours=1))
    hours = notice_hours(n)
    out = []
    for h in pd.date_range(start, last, freq="h"):
        ts = ip.utc_iso(h)
        inforce = sorted(set(hours.get(ts, [])))
        on = any(x.split("@")[0] in EEA + ALERTS for x in inforce)
        out.append(("own_signal", ts, int(on), ";".join(inforce)))
    return out, revised


def build(month, in_dir=None, log=print):
    rows, notes = [], {}
    for g in GRIDS:
        start, end = window(month, g["offset"])
        rt = read_prices(g["rt_tables"], g["rt_market"], g["node"], start, end, in_dir)
        da = read_prices(g["da_tables"], g["da_market"], g["node"], start, end, in_dir)
        pr = price_rows(rt, da)
        if g["grid"] == "ercot":
            sig, revised = ercot_signal(start, end, in_dir), ""
        else:
            sig, revised = caiso_signal(start, end, in_dir)
        hours = int((end - start) / pd.Timedelta(hours=1)) + 1
        n_rt = sum(1 for r in pr if r[0] == "rt_hour_ge_1000")
        notes[g["grid"]] = dict(first=ip.utc_iso(start), last=ip.utc_iso(end), hours=hours, rt_hours=n_rt,
                                rt_first=min((r[1] for r in pr if r[0] == "rt_hour_ge_1000"), default=""),
                                rt_hours_ge=sum(r[2] for r in pr if r[0] == "rt_hour_ge_1000"), rt_intervals_ge=sum(r[2] for r in pr if r[0] == "rt_intervals_ge_1000"),
                                da_hours=sum(1 for r in pr if r[0] == "da_hour_ge_1000"), da_hours_ge=sum(r[2] for r in pr if r[0] == "da_hour_ge_1000"),
                                signal_hours=len(sig), signal_on=sum(r[2] for r in sig), signal_last=max((r[1] for r in sig), default=""), revised=revised)
        log(f"{g['grid']}: window {notes[g['grid']]['first']} to {notes[g['grid']]['last']} ({hours} hours); real-time hours held {n_rt}, at or above the level "
            f"{notes[g['grid']]['rt_hours_ge']} (intervals {notes[g['grid']]['rt_intervals_ge']}); day-ahead hours held {notes[g['grid']]['da_hours']}, at or above "
            f"{notes[g['grid']]['da_hours_ge']}; own signal held {len(sig)} hours, in force {notes[g['grid']]['signal_on']}")
        for variable, ts, value, detail in pr + sig:
            market = g["da_market"] if variable.startswith("da_") else g["rt_market"] if variable.startswith("rt_") else ""
            rows.append((f"iso:{g['grid']}", variable, ts, value, "count", "PT1H", g["geo"], market, g["node"] if market else "", detail))
    s = pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "x_detail"])
    return s, notes


def kept_retrieved(s, path, retrieved):
    """retrieved_at for each row of `s`: the old file's, where the row (entity, variable, hour) holds the same value and
    the same x_detail there; else this run's."""
    old = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "x_detail", "retrieved_at"], dtype=str, keep_default_na=False)
    was = {(e, v, t): (float(val), d, r) for e, v, t, val, d, r in zip(old["entity"], old["variable"], old["ts_utc"], old["value"], old["x_detail"], old["retrieved_at"])}
    out = []
    for e, v, t, val, d in zip(s["entity"], s["variable"], s["ts_utc"], s["value"], s["x_detail"]):
        o = was.get((e, v, t))
        out.append(o[2] if o is not None and o[0] == float(val) and o[1] == str(d) else retrieved)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: each grid's own scarcity signal beside the USD 1,000 price count, by hour (session 254)")
    ap.add_argument("--month", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m"), help="the month of the run, YYYY-MM: the table holds the 36 whole months before it")
    a = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        s, notes = build(a.month, log=log)
        if s.empty:
            raise RuntimeError("no hour could be written: the price and signal tables hold nothing in the window")
        s = s.assign(source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")[COLS]
        e, c = notes["ercot"], notes["caiso"]
        header = [
            "Energy Research Warehouse (ERW): each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (derived, session 254)",
            "Shape: series (docs/datastandard.md v0); freq PT1H, ts_utc the hour's start. entity iso:<grid>. rt_intervals_ge_1000: the hour's 15-minute real-time intervals at or above "
            "USD 1,000 per MWh (x_detail held=<intervals held>); rt_hour_ge_1000: 1 when the mean of the hour's held intervals is at or above it; da_hour_ge_1000: the same for the "
            "day-ahead hour; own_signal: 1 in force, 0 not, only for hours the signal is held (ERCOT: RTORPA's hourly mean above zero, x_detail the mean; CAISO: an EEA or an alert in "
            "force in any part of the hour, x_detail every notice in force as type@region).",
            f"Window: the {MONTHS} whole months before {a.month}, in each grid's standard time. ERCOT (HB_HUBAVG): {e['first']} to {e['last']}, {e['hours']} hours; real-time held "
            f"{e['rt_hours']}, own signal held {e['signal_hours']} (to {e['signal_last']}: the adder ended on 4 December 2025). CAISO (TH_SP15_GEN-APND): {c['first']} to {c['last']}, "
            f"{c['hours']} hours; real-time held {c['rt_hours']} (from {c['rt_first']}: its prices are held from 1 September 2024), own signal held {c['signal_hours']} "
            f"(CAISO's report revised {c['revised']}).",
            "An hour without a row is not held; it is not a zero. NYISO, ISO-NE, SPP and MISO are not in the table (their prices need a license or are held; no table of their own signal).",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/scarcity_hours_by_grid.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the scarcity signal rule (docs/methods/scarcity_hours_by_grid.md), {METHOD_URL}",
            "Derived from: caiso_grid_emergencies; ercot_all_hub_prices_history; ercot_rtm_price_adders; iso_dam_hub_prices; iso_hub_prices_history; iso_rtm_hub_prices",
            "  only ERCOT's and CAISO's rows of the three iso_ tables are read",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): ERCOT, CAISO (credit the California ISO).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            # A row that comes out as it was keeps its retrieved_at (the data standard, decision on derived tables
            # recomputed from a window): the loader and the archive then take only the rows that are new or changed.
            s["retrieved_at"] = kept_retrieved(s, path, retrieved)
            os.remove(path)  # rebuilt whole from its inputs each run: the window moves with the month
        ip.write_csv(s, NAME, header, log, cols=COLS)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived", report="Each grid's own scarcity signal beside the USD 1,000 price count (warehouse/derived/scarcity_hours_by_grid.py)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        msg = f"{len(s)} rows; ERCOT {e['rt_hours_ge']} real-time hours at or above USD 1,000 and {e['signal_on']} hours with its adder above zero; CAISO {c['rt_hours_ge']} and {c['signal_on']} hours with an EEA or alert"
        log(msg)
        print(f"{NAME}: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
