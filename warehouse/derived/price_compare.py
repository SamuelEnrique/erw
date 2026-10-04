#!/usr/bin/env python3
"""Where power is cheap: every public hub and zone price the warehouse holds, compared (session 96).

Energy Research Warehouse (ERW). One derived table, hub_price_comparison, from the public hub and zone price tables.
Method: docs/methods/hub_price_comparison.md. Page: /prices/compare (in review).

    python warehouse/derived/price_compare.py                 # the table, under the data lock
    python warehouse/derived/price_compare.py --out-dir DIR   # a trial run: the table under DIR, nothing in warehouse/output
    python warehouse/derived/price_compare.py --snapshot      # also the site's own copy (site/data/price_compare.json)
    python warehouse/derived/price_compare.py --end 2026-09   # the last month of the windows (default: the last whole month held)

No request is made. Two windows, in each grid's own local time: the twelve calendar months to the last whole month
held (freq P1Y, ts_utc the first day of the window), and that last month alone (freq P1M). The hub history reaches back
twelve months for eleven hubs; the zones and the other hubs are held only since late August 2026, so they have the
month and not the year.

For each hub or zone (entity <iso>:<node>), each market (dam: day-ahead; rtm: real-time) and each window:
    <m>_avg_price                     USD/MWh   the mean of the hourly prices held
    <m>_negative_hours_share_pct      pct       the share of those hours with a price below zero
    <m>_above_200_hours_share_pct     pct       the share with a price above USD 200 per MWh
    <m>_day_spread_top4_bottom4       USD/MWh   on the average day (the mean price of each local hour of the day over the
                                                window), the mean of its four dearest hours less the mean of its four cheapest
    <m>_hours_held, <m>_hours_in_window   count
and once per entity and window, the carbon intensity of its grid's generation:
    grid_carbon_intensity             kgCO2/MWh the mean of the daily intensities held (carbon_intensity_daily)
    grid_carbon_days_held             count

An hour of real-time price is the mean of its four 15-minute prices, and is held only when all four are. ISO-NE's
real-time price is also held as ISO-NE's own hourly report; the one of the two that holds more of the window is used,
whole, never mixed with the other (the site's copy says which: rtm_basis PT15M or PT1H). A market of a hub is written for a window only when at least
95 percent of the window's hours are held; the carbon intensity only when at least 90 percent of its days are. Nothing
is filled.

Not written: a table whose license does not allow republishing, and a publisher whose terms are under review
(warehouse/metadata/paused_sources.csv). Their hubs are listed in the site's copy by name, with the reason, and no
number: "held, not shown".
"""

import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "hub_price_comparison"
SOURCE = "erw:hub_price_comparison"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/hub_price_comparison.md"
SITE_FILE = os.path.join(ROOT, "site", "data", "price_compare.json")
META = os.path.join(ROOT, "warehouse", "metadata")

# the price tables read, in order of preference for a row held twice (the history first)
TABLES = ["iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices",
          "isone_dam_zone_prices", "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly", "nyiso_dam_zone_prices", "nyiso_rtm_zone_prices"]
GRIDS = {"caiso": dict(name="CAISO", tz="America/Los_Angeles", ba="CISO"), "ercot": dict(name="ERCOT", tz="America/Chicago", ba="ERCO"),
         "isone": dict(name="ISO-NE", tz="America/New_York", ba="ISNE"), "miso": dict(name="MISO", tz="America/Chicago", ba="MISO"),
         "nyiso": dict(name="NYISO", tz="America/New_York", ba="NYIS"), "spp": dict(name="SPP", tz="America/Chicago", ba="SWPP")}
DAM_VARS = {"lmp_dam", "spp_dam"}
RTM_VARS = {"lmp_rtm_15m_mean", "spp_rtm", "lmp_rtm"}
NEAR_HOURS = 0.95
NEAR_DAYS = 0.90
HIGH = 200.0


def licenses():
    """Each price table's license in coverage.csv, and the publishers paused (their terms under review)."""
    with open(os.path.join(META, "coverage.csv"), encoding="utf-8", newline="") as f:
        lic = {r["table"]: r["license"] for r in csv.DictReader(f)}
    paused = {}
    path = os.path.join(META, "paused_sources.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                paused[r["scope"]] = r
    return lic, paused


def read_prices(in_dir, since, log):
    """Every hub and zone price row from `since` (UTC), one row per (entity, market side, ts): the first table of TABLES
    that holds it. Columns: entity, side (dam or rtm), ts (UTC), value, freq, geo, table."""
    parts = []
    for i, t in enumerate(TABLES):
        path = os.path.join(in_dir, f"{t}.csv")
        if not os.path.exists(path):
            log(f"  {t}: not on this machine")
            continue
        got = []
        for chunk in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "freq", "geo"], chunksize=500_000):
            chunk = chunk[chunk["ts_utc"] >= since]
            if len(chunk):
                got.append(chunk)
        if not got:
            continue
        d = pd.concat(got)
        d["side"] = np.where(d["variable"].isin(DAM_VARS), "dam", np.where(d["variable"].isin(RTM_VARS), "rtm", ""))
        d = d[d["side"] != ""]
        d["table"], d["rank"] = t, i
        log(f"  {t}: {len(d):,} rows from {since}, {d['entity'].nunique()} hubs and zones")
        parts.append(d)
    x = pd.concat(parts)
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
    x = x.sort_values("rank").drop_duplicates(["entity", "side", "freq", "ts"], keep="first")
    return x[["entity", "side", "ts", "value", "freq", "geo", "table"]]


def hourly(s, freq):
    """A price series by hour (UTC): as it is when hourly; from 15-minute prices, the mean of an hour's four, and only
    when all four are held."""
    if freq == "PT1H":
        return s
    g = s.groupby(s.index.floor("h"))
    return g.mean()[g.size() == 4]


def window_hours(start, end, tz):
    """The hours (UTC) of the local window [start, end), start and end local midnights as YYYY-MM-DD."""
    a, b = pd.Timestamp(start, tz=tz).tz_convert("UTC"), pd.Timestamp(end, tz=tz).tz_convert("UTC")
    return a, b, int((b - a) / pd.Timedelta(hours=1))


def measures(h, tz):
    """The four measures of an hourly price series (UTC index) in a window, or None when an hour of the day is missing."""
    local = h.index.tz_convert(tz).hour
    day = h.groupby(local).mean()
    if len(day) < 24:
        return None
    top, bottom = day.nlargest(4).mean(), day.nsmallest(4).mean()
    return {"avg_price": round(float(h.mean()), 2), "negative_hours_share_pct": round(100 * float((h < 0).mean()), 2),
            "above_200_hours_share_pct": round(100 * float((h > HIGH).mean()), 2), "day_spread_top4_bottom4": round(float(top - bottom), 2)}


def carbon(in_dir, ba, start, end):
    """The mean of a grid's daily carbon intensity of generation over [start, end) (dates), with the days held and due."""
    path = os.path.join(in_dir, "carbon_intensity_daily.csv")
    c = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    c = c[(c["entity"] == f"eia930:{ba}") & (c["variable"] == "intensity_generation") & (c["ts_utc"] >= f"{start}T00:00:00Z") & (c["ts_utc"] < f"{end}T00:00:00Z")]
    due = (pd.Timestamp(end) - pd.Timestamp(start)).days
    if len(c) < NEAR_DAYS * due:
        return None, len(c), due
    return round(float(c["value"].mean()), 2), len(c), due


def last_whole_month(x):
    """The last calendar month every market side of the hub history holds to its end: the month before the month of the
    earliest of the sides' newest timestamps."""
    newest = x.groupby(["entity", "side"])["ts"].max().min()
    return (newest.tz_convert("UTC").to_period("M") - 1).strftime("%Y-%m")


def build(x, in_dir, end_month, hidden, log):
    """The rows and the site's view. hidden: {iso: reason} for the grids whose hubs are held and not shown."""
    end = (pd.Period(end_month) + 1).strftime("%Y-%m-01")
    windows = {"year": ((pd.Period(end_month) - 11).strftime("%Y-%m-01"), end, "P1Y"), "month": (f"{end_month}-01", end, "P1M")}
    rows, view, held_not_shown, skipped = [], {"year": [], "month": []}, [], []
    for entity, e in x.groupby("entity"):
        iso, node = entity.split(":", 1)
        if iso in hidden:
            held_not_shown.append({"entity": entity, "grid": GRIDS[iso]["name"], "node": node, "reason": hidden[iso]})
            continue
        g = GRIDS[iso]
        geo = e["geo"].iloc[0]
        for wname, (start, stop, freq) in windows.items():
            a, b, n = window_hours(start, stop, g["tz"])
            rec = {"entity": entity, "grid": g["name"], "node": node}
            wrote = False
            for side in ("dam", "rtm"):
                s = e[e["side"] == side]
                if s.empty:
                    continue
                # a real-time price may be held two ways (ISO-NE: 15-minute means, and its own hourly report): each is
                # made hourly on its own, never mixed, and the one that holds more of the window is used
                h, basis = None, ""
                for f, part in s.groupby("freq"):
                    c = hourly(pd.Series(part["value"].values, index=part["ts"]).sort_index(), f)
                    c = c[(c.index >= a) & (c.index < b)].dropna()
                    if h is None or len(c) > len(h):
                        h, basis = c, f
                m = measures(h, g["tz"]) if len(h) >= NEAR_HOURS * n else None
                if m is None:
                    skipped.append(f"{entity} {side} {wname}: {len(h):,} of {n:,} hours")
                    continue
                m.update(hours_held=int(len(h)), hours_in_window=n)
                rec[f"{side}_basis"] = basis
                for k, v in m.items():
                    unit = "pct" if k.endswith("pct") else "count" if k.startswith("hours") else "USD/MWh"
                    rows.append(dict(entity=entity, variable=f"{side}_{k}", ts_utc=f"{start}T00:00:00Z", value=v, unit=unit, freq=freq, geo=geo, market="", node=node))
                    rec[f"{side}_{k}"] = v
                wrote = True
            if not wrote:
                continue
            ci, days, due = carbon(in_dir, g["ba"], start, stop)
            rec["grid_carbon_days_held"], rec["grid_carbon_days_due"] = days, due
            rows.append(dict(entity=entity, variable="grid_carbon_days_held", ts_utc=f"{start}T00:00:00Z", value=days, unit="count", freq=freq, geo=geo, market="", node=node))
            if ci is not None:
                rec["grid_carbon_intensity"] = ci
                rows.append(dict(entity=entity, variable="grid_carbon_intensity", ts_utc=f"{start}T00:00:00Z", value=ci, unit="kgCO2/MWh", freq=freq, geo=geo, market="", node=node))
            view[wname].append(rec)
    for line in skipped:
        log(f"  not written (under {NEAR_HOURS:.0%} of the window's hours, or an hour of the day missing): {line}")
    return rows, view, held_not_shown, windows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Where power is cheap: every public hub and zone price held, compared")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the registry under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/price_compare.json)")
    ap.add_argument("--end", help="the last month of the windows, YYYY-MM (default: the last whole month held)")
    a = ap.parse_args(argv)
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"price_compare_{run_id}.log"))
    lic, paused = licenses()
    internal = [t for t in TABLES if lic.get(t) not in (None, "public")]
    hidden = {}
    for iso in GRIDS:
        if iso in paused:
            p = paused[iso]
            hidden[iso] = f"{p['publisher']}'s terms are under review (pulls paused {p['paused_on']}); its terms forbid derivative works, so no figure is derived from its prices"
    log(f"  licenses: {len(internal)} of the {len(TABLES)} price tables are internal {internal}; publishers under review: {sorted(hidden)}")
    x = read_prices(inputs, "2025-08-01", log)
    x = x[~x["table"].isin(internal)]
    end_month = a.end or last_whole_month(x[x["table"] == "iso_hub_prices_history"])
    rows, view, held_not_shown, windows = build(x, inputs, end_month, hidden, log)
    out = pd.DataFrame(rows)
    out["source"], out["source_url"], out["retrieved_at"], out["vintage"] = SOURCE, METHOD_URL, retrieved, ""
    out = out[ip.SERIES_COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole each run: the windows move with the last whole month
    year, month = windows["year"], windows["month"]
    ip.write_csv(out, NAME, [
        "Energy Research Warehouse (ERW): where power is cheap, every public hub and zone price held, compared over twelve months and over the last whole month (session 96)",
        "Shape: series (docs/datastandard.md v0). Entity <iso>:<node>. freq P1Y: the twelve months from ts_utc; freq P1M: the month of ts_utc; both in the grid's "
        "local time. Variables, for dam (day-ahead) and rtm (real-time): _avg_price, _negative_hours_share_pct, _above_200_hours_share_pct, "
        "_day_spread_top4_bottom4, _hours_held, _hours_in_window; and grid_carbon_intensity, grid_carbon_days_held. Definitions: docs/methods/hub_price_comparison.md.",
        f"Window: twelve months {year[0]} to {year[1]} (exclusive), and the month {month[0]} to {month[1]} (exclusive). A market of a hub is written when at least "
        f"{NEAR_HOURS:.0%} of the window's hours are held; the carbon intensity when at least {NEAR_DAYS:.0%} of its days are.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/price_compare.py", f"Run log: warehouse/output/logs/price_compare_{run_id}.log",
        f"Derived from: {'; '.join(t for t in TABLES if t not in internal)}; carbon_intensity_daily",
        f"Source: {SOURCE} from each grid operator's public price reports (CAISO OASIS; ERCOT NP4-180-ER, NP4-190-CD, NP6-785-ER, NP6-905-CD; ISO-NE hourly and "
        "five-minute LMPs; NYISO zonal LBMPs; SPP LMP by settlement location) and from EIA-930 emissions",
        "Not derived from: " + ("; ".join(f"{g} ({r})" for g, r in hidden.items()) or "nothing") + ". PJM: no hub or zone price is held.",
        "License: public",
    ], log, key=["entity", "variable", "ts_utc"])
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="Where power is cheap: hub and zone prices compared (docs/methods/hub_price_comparison.md)", report_url=METHOD_URL,
                            document_list="docs/methods/hub_price_comparison.md", license="public", tables=[NAME])])
    if a.snapshot:
        os.makedirs(os.path.dirname(SITE_FILE), exist_ok=True)
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(table=NAME, built=retrieved, end_month=end_month, windows={k: {"start": v[0], "end": v[1], "freq": v[2]} for k, v in windows.items()},
                           near_hours=NEAR_HOURS, near_days=NEAR_DAYS, high=HIGH, year=view["year"], month=view["month"], held_not_shown=held_not_shown,
                           internal_tables=internal, not_held=["PJM"]), f, separators=(",", ":"))
    log.close()
    print(f"{NAME}: {len(out):,} rows; twelve months to {end_month}: {len(view['year'])} hubs; the month {end_month}: {len(view['month'])} hubs and zones; "
          f"held, not shown: {len(held_not_shown)}" + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir}; inputs read from {inputs})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
