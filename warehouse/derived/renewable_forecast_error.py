"""ERW: the operators' own day-ahead wind and solar forecasts beside the output that came (session 8013, chain 505, D2).

Energy Research Warehouse (ERW). Two grids publish both a day-ahead forecast of wind and solar output and the output
itself under a license docs/licenses.md lets a page show, and the warehouse holds both:

    CAISO   caiso_wind_solar_forecast: OASIS SLD_REN_FCST, the day-ahead forecast (market run DAM) and the actual
            output (market run ACTUAL), hourly, by trading hub (NP15, SP15, ZP26), from June 2023
    ERCOT   ercot_wind_solar_forecast: the short-term forecast posted a day ahead (NP4-732-CD, NP4-745-CD) and the
            system-wide output, hourly, from late September 2026

This builder sets each forecast beside the output of the same hour and writes the miss (forecast less output) as
measures over hours, local hours of day, local months, whole local days and the nine events of /events. No forecast of
the ERW's own and no table of its own: the page file is computed from the two tables as they stand.

    python warehouse/derived/renewable_forecast_error.py [--site-dir PATH]

Page file: site/data/regions/forecast/renewables.json (contract: section 12 of docs/state/page_files_regions.md).
Method: docs/methods/renewable_forecast_error.md.
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import region_files as rp  # noqa: E402

OUT = os.environ.get("ERW_OUTPUT_DIR") or os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "regions")
METHOD = "docs/methods/renewable_forecast_error.md"

GRIDS = [
    {"grid": "CAISO", "region": "CAL", "code": "CISO", "tz": "America/Los_Angeles", "table": "caiso_wind_solar_forecast",
     "hubs": ["NP15", "SP15", "ZP26"], "fc": "{k}_forecast_dam_mw", "act": "{k}_actual_mw",
     "forecast": "CAISO's day-ahead forecast (OASIS SLD_REN_FCST, market run DAM), by trading hub",
     "actual": "CAISO's actual output (OASIS SLD_REN_FCST, market run ACTUAL), by trading hub"},
    {"grid": "ERCOT", "region": "TEX", "code": "ERCO", "tz": "America/Chicago", "table": "ercot_wind_solar_forecast",
     "hubs": ["SYSTEM"], "fc": "{k}_forecast_24h_mw", "act": "{k}_actual_mw",
     "forecast": "ERCOT's short-term forecast as posted a day ahead of the hour (NP4-732-CD wind, NP4-745-CD solar)",
     "actual": "ERCOT's system-wide output (SYSTEM_WIDE_GEN) from the newest posting that holds the hour"},
]
NOT_HELD = [
    {"grid": "SPP", "why": "SPP publishes wind and solar forecasts; the warehouse does not hold them"},
    {"grid": "NYISO", "why": "the warehouse holds no NYISO wind or solar forecast, and NYISO's data needs written permission (docs/licenses.md)"},
    {"grid": "ISO-NE", "why": "the warehouse holds no ISO-NE wind or solar forecast, and ISO-NE's data needs written permission (docs/licenses.md)"},
    {"grid": "PJM", "why": "license needed: PJM's data is held for a license (docs/licenses.md)"},
    {"grid": "MISO", "why": "MISO is paused since 4 October 2026 (docs/methods/miso_pause.md); nothing of it is requested"},
]


def read_table(name):
    """A table of warehouse/output, its header lines skipped by count (a '#' inside a row is kept)."""
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    df = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype={"entity": str, "variable": str, "ts_utc": str})
    if df.empty:
        raise SystemExit(f"{name}: no rows")
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True)
    return df


def pairs(df, g, kind):
    """{hub: frame of f (forecast) and a (actual), indexed by hour} and the grid's sum (CAISO: all hubs hold both)."""
    fc, act = g["fc"].format(k=kind), g["act"].format(k=kind)
    out = {}
    for hub in g["hubs"]:
        e = df[df["entity"].str.endswith(":" + hub)]
        f = e[e["variable"] == fc].set_index("ts")["value"]
        a = e[e["variable"] == act].set_index("ts")["value"]
        if f.index.duplicated().any() or a.index.duplicated().any():
            raise SystemExit(f"{g['table']}: {hub} {kind} holds an hour twice")
        x = pd.concat([f.rename("f"), a.rename("a")], axis=1, join="inner").dropna().sort_index()
        out[hub] = x
    if len(g["hubs"]) == 1:
        total = out[g["hubs"][0]]
    else:
        common = None
        for x in out.values():
            common = x.index if common is None else common.intersection(x.index)
        total = sum(out[h].loc[common] for h in g["hubs"]).sort_index()
    return out, total


def stats(x):
    if not len(x):
        return {"hours": 0, "mae_mw": None, "bias_mw": None, "wape_pct": None, "bias_pct": None, "forecast_mean_mw": None, "actual_mean_mw": None}
    miss = x["f"] - x["a"]
    asum = float(x["a"].sum())
    return {"hours": int(len(x)), "mae_mw": round(float(miss.abs().mean()), 1), "bias_mw": round(float(miss.mean()), 1),
            "wape_pct": round(float(100 * miss.abs().sum() / asum), 2) if asum > 0 else None,
            "bias_pct": round(float(100 * miss.sum() / asum), 2) if asum > 0 else None,
            "forecast_mean_mw": round(float(x["f"].mean()), 1), "actual_mean_mw": round(float(x["a"].mean()), 1)}


def series_doc(x, tz, events):
    loc = x.index.tz_convert(tz)
    hours = [stats(x[loc.hour == h]) for h in range(24)]
    months = {}
    for m in sorted(set(loc.strftime("%Y-%m"))):
        months[m] = stats(x[loc.strftime("%Y-%m") == m])
    days = {"days": [], "forecast_mwh": [], "actual_mwh": [], "miss_mwh": [], "wape_pct": []}
    y = x.assign(day=loc.strftime("%Y-%m-%d"))
    for day, g in y.groupby("day"):
        a = pd.Timestamp(day, tz=tz)
        need = int(((a + pd.DateOffset(days=1)) - a) / pd.Timedelta(hours=1))
        if len(g) != need:
            continue
        fs, as_ = float(g["f"].sum()), float(g["a"].sum())
        days["days"].append(day)
        days["forecast_mwh"].append(round(fs, 1))
        days["actual_mwh"].append(round(as_, 1))
        days["miss_mwh"].append(round(fs - as_, 1))
        days["wape_pct"].append(round(float(100 * (g["f"] - g["a"]).abs().sum() / as_), 2) if as_ > 0 else None)
    ev = []
    for e in events:
        a = pd.Timestamp(e["start"], tz=tz)
        b = pd.Timestamp(e["end"], tz=tz) + pd.DateOffset(days=1)
        s = stats(x[(x.index >= a) & (x.index < b)])
        ev.append({"event": e["event"], "title": e["title"], "start": e["start"], "end": e["end"],
                   **{k: s[k] for k in ("hours", "mae_mw", "bias_mw", "wape_pct")}})
    return {"first_hour": x.index.min().strftime("%Y-%m-%dT%H:%M:%SZ"), "last_hour": x.index.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "overall": stats(x), "by_hour": {k: [h[k] for h in hours] for k in ("wape_pct", "bias_mw", "mae_mw", "hours")},
            "by_month": months, "daily": days, "events": ev}


def build():
    events = rp.events_list()
    grids = []
    for g in GRIDS:
        df = read_table(g["table"])
        doc = {k: g[k] for k in ("grid", "region", "code", "tz", "table", "forecast", "actual")}
        doc["entities"] = sorted(df["entity"].unique().tolist())
        doc["series"], doc["hubs"] = {}, {}
        for kind in ("wind", "solar"):
            hubs, total = pairs(df, g, kind)
            if not len(total):
                raise SystemExit(f"{g['table']}: no hour holds both the {kind} forecast and the output")
            doc["series"][kind] = series_doc(total, g["tz"], events)
            if len(g["hubs"]) > 1:
                for hub, x in hubs.items():
                    doc["hubs"].setdefault(hub, {})[kind] = {"overall": stats(x),
                                                            "first_hour": x.index.min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(x) else None,
                                                            "last_hour": x.index.max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(x) else None}
        if not doc["hubs"]:
            del doc["hubs"]
        grids.append(doc)
    return rp.clean({"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tables": [g["table"] for g in GRIDS],
                     "method": METHOD, "license": "public",
                     "note": "The operators' own day-ahead forecasts of wind and solar output beside the output that came; a miss is the forecast less the output.",
                     "grids": grids, "not_held": NOT_HELD})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site-dir", default=SITE)
    a = ap.parse_args(argv)
    doc = build()
    path = os.path.join(a.site_dir, "forecast", "renewables.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, path)
    for g in doc["grids"]:
        for k, s in g["series"].items():
            o = s["overall"]
            print(f"{g['grid']} {k}: {o['hours']} hours {s['first_hour']} to {s['last_hour']}, wape {o['wape_pct']}%, bias {o['bias_mw']} MW, {len(s['daily']['days'])} whole days")
    print(f"wrote {path} ({os.path.getsize(path):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
