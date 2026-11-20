#!/usr/bin/env python3
"""ERW: grid conditions, the page files site/data/conditions/<operator>.json and index.json (chain 601, part G,
session 9000).

Energy Research Warehouse (ERW). Reads warehouse tables only; makes no request. Contract:
docs/state/page_files_conditions.md, section 2. Method: docs/methods/grid_conditions.md. For each of the seven grids,
strips on one time axis:

  demand        demand and the day-ahead demand forecast, from EIA-930 (eia930_ba_demand_hourly): every grid
  out           megawatts out of service (generation_outages_hourly): SPP (its RTO balancing area) and CAISO
  constraints   constraints binding and the largest shadow price (constraints_binding_hourly): SPP and CAISO
  scarcity      ERCOT's online reserve price adder above zero (ercot_rtm_price_adders, to its end on 4 December 2025)
  alerts        the notices in grid_all_alerts: CAISO and ERCOT

A strip an operator's terms hold, or that no open source publishes, is a key with its status and reason, no number.
Daily figures over every day held; hourly figures for the newest 35 days and for the nine events of /events.

    python warehouse/derived/conditions_page.py                 # the site's files
    python warehouse/derived/conditions_page.py --out-dir DIR   # a trial
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

SITE_DIR = os.path.join(ROOT, "site", "data", "conditions")
EVENTS_DIR = os.path.join(ROOT, "site", "data", "regions", "events")
METHOD = "docs/methods/grid_conditions.md"
FIRST_DAY = "2018-07-01"
RECENT_DAYS = 35
OPS = {
    "caiso": dict(name="CAISO", ba="CISO", tz="America/Los_Angeles", out="caiso:ISO", cons="caiso_dam"),
    "ercot": dict(name="ERCOT", ba="ERCO", tz="America/Chicago"),
    "spp": dict(name="SPP", ba="SWPP", tz="America/Chicago", out="spp:SPP", cons="spp_dam"),
    "miso": dict(name="MISO", ba="MISO", tz="America/Chicago"),
    "pjm": dict(name="PJM", ba="PJM", tz="America/New_York"),
    "nyiso": dict(name="NYISO", ba="NYIS", tz="America/New_York"),
    "isone": dict(name="ISO-NE", ba="ISNE", tz="America/New_York"),
}
HELD = {
    "ercot": ("source needed", "ERCOT publishes this only on paths its robots file disallows, or through an API whose key has not been made (the owner's ruling of 6 November 2026)"),
    "pjm": ("license needed", "PJM's terms forbid non-members to republish its data"),
    "nyiso": ("license needed", "NYISO's terms reserve its data; written permission needed"),
    "isone": ("license needed", "ISO-NE's terms ask written permission"),
    "miso": ("paused", "MISO's terms forbid automated access; the ERW paused it on 4 October 2026"),
}
SOURCES = {
    "demand": "U.S. EIA, Hourly Electric Grid Monitor (EIA-930): demand and the day-ahead demand forecast, as the ERW's table eia930_ba_demand_hourly holds them",
    "out_spp": "SPP, Capacity of Generation on Outage (portal.spp.org), the RTO balancing area (SPP), as generation_outages_hourly holds it",
    "out_caiso": "California ISO, Curtailed and Non-Operational Generator Prior Trade Date Report, planned and forced, as generation_outages_hourly holds it",
    "cons_spp": "SPP, Day-Ahead Binding Constraints, as constraints_binding_hourly holds them",
    "cons_caiso": "California ISO, OASIS PRC_NOMOGRAM (day-ahead), as constraints_binding_hourly holds them",
    "scarcity_ercot": "ERCOT, Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves (NP6-792-ER), the online reserve adder (RTORPA), as ercot_rtm_price_adders holds it",
    "alerts_caiso": "California ISO, grid emergencies history, as grid_all_alerts holds it",
    "alerts_ercot": "ERCOT's notices as its news releases print them, as grid_all_alerts holds them",
}


def read(name, cols, keep=None, chunks=False):
    p = os.path.join(ip.OUT_DIR, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    if not chunks:
        d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False)
        fh.close()
        return d if keep is None else d[keep(d)]
    parts = []
    for c in pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False, chunksize=1_000_000):
        parts.append(c[keep(c)])
    fh.close()
    return pd.concat(parts, ignore_index=True)


def local(ts_utc, tz):
    return pd.to_datetime(ts_utc, utc=True).dt.tz_convert(tz).dt.tz_localize(None)


def r(v, n=1):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), n)


def events():
    out = []
    for f in sorted(glob.glob(os.path.join(EVENTS_DIR, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            e = json.load(fh)
        out.append({"id": e["event"], "title": e["title"], "start": e["start"], "end": e["end"]})
    return sorted(out, key=lambda e: e["start"])


def hourly_frame(op, o, dem, out, cons, scar):
    """One row an hour (local clock) with every strip held for the operator."""
    d = dem[dem["ba"] == o["ba"].lower()].copy()
    d["value"] = pd.to_numeric(d["value"])
    w = d.pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="first")
    w = w.rename(columns={"demand_mw": "demand", "demand_forecast_mw": "forecast"})
    if out is not None and "out" in o:
        x = out[out["entity"] == o["out"]].copy()
        x["value"] = pd.to_numeric(x["value"])
        p = x.pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="first")
        p = p.rename(columns={"outage_mw_total": "out_total", "outage_mw_planned": "out_planned", "outage_mw_forced": "out_forced"})
        w = w.join(p[[c for c in ["out_total", "out_planned", "out_forced"] if c in p.columns]], how="outer")
    if cons is not None and "cons" in o:
        c = cons[cons["market"] == o["cons"]].copy()
        c["abs"] = pd.to_numeric(c["value"]).abs()
        g = c.groupby("ts_utc")["abs"].agg(cons_n="count", cons_max="max")
        w = w.join(g, how="outer")
    if scar is not None and op == "ercot":
        s = scar.copy()
        s["value"] = pd.to_numeric(s["value"])
        w = w.join(s.set_index("ts_utc")["value"].rename("adder"), how="outer")
    w = w.reset_index()
    w["local"] = local(w["ts_utc"], o["tz"])
    w["day"] = w["local"].dt.strftime("%Y-%m-%d")
    return w[w["day"] >= FIRST_DAY]


def daily_rows(w, op, alerts_by_day):
    cols = ["day", "demand_peak", "demand_min", "forecast_peak", "out_mean", "out_max", "cons_hours", "cons_max", "adder_hours", "adder_max", "alerts"]
    rows = []
    for day, g in w.groupby("day", sort=True):
        def agg(c, f):
            return r(getattr(g[c], f)(), 1) if c in g and g[c].notna().any() else None
        rows.append([day, agg("demand", "max"), agg("demand", "min"), agg("forecast", "max"), agg("out_total", "mean"),
                     agg("out_total", "max"),
                     int(g["cons_n"].fillna(0).sum()) if "cons_n" in g and g["cons_n"].notna().any() else None,
                     agg("cons_max", "max"),
                     int((g["adder"] > 0).sum()) if "adder" in g and g["adder"].notna().any() else None,
                     agg("adder", "max"), alerts_by_day.get(day, 0) if alerts_by_day is not None else None])
    return cols, rows


def hourly_rows(w, start, end):
    cols = ["t", "demand", "forecast", "out_total", "out_planned", "out_forced", "cons_n", "cons_max", "adder"]
    x = w[(w["day"] >= start) & (w["day"] <= end)].sort_values("ts_utc")
    rows = []
    for _, v in x.iterrows():
        rows.append([v["ts_utc"]] + [r(v[c], 1) if c in v and pd.notna(v[c]) else None for c in cols[1:]])
    return cols, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: grid conditions page files")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    out_dir = a.out_dir or SITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bas = {o["ba"].lower() for o in OPS.values()}
    dem = read("eia930_ba_demand_hourly", ["variable", "ts_utc", "value", "ba"],
               keep=lambda d: d["ba"].isin(bas) & d["variable"].isin(["demand_mw", "demand_forecast_mw"]), chunks=True)
    out = read("generation_outages_hourly", ["entity", "variable", "ts_utc", "value"]) if os.path.exists(os.path.join(ip.OUT_DIR, "generation_outages_hourly.csv")) else None
    cons = read("constraints_binding_hourly", ["ts_utc", "value", "market"])
    scar = read("ercot_rtm_price_adders", ["variable", "ts_utc", "value"], keep=lambda d: d["variable"] == "rtorpa_mean")
    al = read("grid_all_alerts", ["event_id", "event_date", "x_grid", "x_kind", "x_start", "x_end", "source_url"])
    evs = events()
    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    recent = (str((today - pd.Timedelta(days=RECENT_DAYS)).date()), str(today.date()))
    index = {"built": built, "method": METHOD, "contract": "docs/state/page_files_conditions.md", "license": "public",
             "events": evs, "recent_days": RECENT_DAYS, "operators": []}
    for op, o in OPS.items():
        w = hourly_frame(op, o, dem, out, cons, scar)
        mine = al[al["x_grid"] == op] if op in ("caiso", "ercot") else None
        by_day = mine.groupby("event_date").size().to_dict() if mine is not None else None
        cols, rows = daily_rows(w, op, by_day)
        strips = {"demand": {"status": "shown", "source": SOURCES["demand"]}}
        for s in ("out", "constraints"):
            key = "out" if s == "out" else "cons"
            if op in ("spp", "caiso"):
                strips[s] = {"status": "shown", "source": SOURCES[f"{key}_{op}"]}
            else:
                st, why = HELD[op]
                strips[s] = {"status": st, "why": why}
        if op == "ercot":
            strips["scarcity"] = {"status": "shown", "source": SOURCES["scarcity_ercot"],
                                  "note": "ERCOT's online reserve adder ended on 4 December 2025 (the held table says so); no hour after it is held"}
        else:
            strips["scarcity"] = {"status": HELD[op][0] if op in HELD else "not published",
                                  "why": HELD[op][1] if op in HELD else f"{o['name']} publishes no scarcity adder of this kind in the files read"}
        if op in ("caiso", "ercot"):
            strips["alerts"] = {"status": "shown", "source": SOURCES[f"alerts_{op}"]}
        else:
            st, why = HELD.get(op, ("not read", "SPP's conservative operations and EEA notices are published as news on www.spp.org, not read yet"))
            strips["alerts"] = {"status": st, "why": why}
        strips["reserves"] = {"status": "source needed",
                              "why": "No operator whose terms allow it publishes its reserves against the requirement over time in the files read: SPP's real-time reserves are 288 files a day with no requirement; ERCOT's plan is on paths its robots file disallows"}
        windows = [{"id": "recent", "title": f"the newest {RECENT_DAYS} days", "start": recent[0], "end": recent[1]}] + \
                  [{"id": e["id"], "title": e["title"], "start": e["start"], "end": e["end"]} for e in evs]
        hourly = {}
        for win in windows:
            hc, hr = hourly_rows(w, win["start"], win["end"])
            if hr:
                hourly[win["id"]] = hr
        alerts = []
        if mine is not None:
            for _, v in mine.sort_values("event_date").iterrows():
                alerts.append([v["event_date"], v["x_kind"], v["x_start"] or None, v["x_end"] or None, v["source_url"]])
        f = {"built": built, "method": METHOD, "license": "public", "op": op, "name": o["name"], "ba": o["ba"],
             "time": f"{o['tz']} clock time for days and hours", "strips": strips,
             "first_day": rows[0][0] if rows else None, "last_day": rows[-1][0] if rows else None,
             "daily_columns": cols, "daily": rows, "hourly_columns": hc if windows else [], "windows": windows,
             "hourly": hourly, "alert_columns": ["date", "kind", "start", "end", "source_url"], "alerts": alerts}
        path = os.path.join(out_dir, f"{op}.json")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(f, fh, separators=(",", ":"), ensure_ascii=False)
        index["operators"].append({"op": op, "name": o["name"], "ba": o["ba"],
                                   "strips": {k: v["status"] for k, v in strips.items()},
                                   "first_day": f["first_day"], "last_day": f["last_day"]})
        print(f"{os.path.relpath(path, ROOT)}: {os.path.getsize(path):,} bytes, {len(rows)} days, {sum(len(v) for v in hourly.values())} hours")
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(index, fh, separators=(",", ":"), ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
