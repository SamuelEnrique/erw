#!/usr/bin/env python3
"""What a datacenter pays: the site's own files for /cost-of-power (session 138).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads the public hub and
zone price tables held and writes the page's files under site/data/datacenter/. Method: docs/methods/datacenter_cost.md.

    python warehouse/derived/datacenter_page.py                 # every grid, every year held
    python warehouse/derived/datacenter_page.py --since 2026    # only the files of 2026 on (the weekly refresh)
    python warehouse/derived/datacenter_page.py --out-dir DIR   # a trial run: the files under DIR, nothing in site/data

Files:
    index.json            the grids, each grid's regions (every hub and zone held, with the hours held of each market
                          and its first and last hour), the years of files, the tables read and when
    <grid>_<year>.json    for each region, the hourly price of that year, real time ("rt") and day-ahead ("da"), in
                          USD/MWh, by the hour of the year in the grid's STANDARD time (no daylight saving
                          shift, so every day has 24 hours and a year 8,760 or 8,784): {"s": the first hour held,
                          "v": the values from there to the last hour held}; an hour not held is null, never filled. Where the grid's hourly demand is held: "demand" (the grid's demand by hour,
                          MW, the same index), "peak_mw", and "tight" (the hours at or above TIGHT of the year's
                          highest hour).

An hour of real-time price is the mean of its four 15-minute prices and is held only when all four are (ISO-NE's
real-time price is also held as its own hourly report; the one of the two that holds more hours is used whole, never
mixed), exactly as hub_price_comparison does (warehouse/derived/price_compare.py, whose reader this uses). Prices are
written to the cent. A past year's file is rewritten only when its content changes, so the weekly refresh touches the
current year's files alone.

Not written: a table whose license does not allow republishing, and a publisher whose terms are under review
(warehouse/metadata/paused_sources.csv): MISO's regions are listed in index.json by name with the words the page
shows, and no number. PJM: no hub or zone price is held.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402  (the reader of every hub and zone price table, and the 15-minute to hourly rule)

SITE_DIR = os.path.join(ROOT, "site", "data", "datacenter")
FIRST = "2015-01-01"
TIGHT = 0.95  # an hour is tight when the grid's demand is at or above this share of the year's highest hour
NEAR_DEMAND = 0.95  # a year's tight hours are written when at least this share of its hours of demand are held
# each grid's standard time, hours behind UTC, and its main hub (the default region), as the price board names it
GRIDS = {
    "ercot": dict(name="ERCOT", std=6, main="HB_HUBAVG", zone="US Central standard time"),
    "caiso": dict(name="CAISO", std=8, main="TH_SP15_GEN-APND", zone="US Pacific standard time"),
    "nyiso": dict(name="NYISO", std=5, main="N.Y.C.", zone="US Eastern standard time"),
    "isone": dict(name="ISO-NE", std=5, main=".H.INTERNAL_HUB", zone="US Eastern standard time"),
    "spp": dict(name="SPP", std=6, main="SPPNORTH_HUB", zone="US Central standard time"),
}
# the grids shown and blanked, with the words the page shows (the owner's rule, session 138)
BLANK = {
    "miso": dict(name="MISO", words="paused while terms are reviewed"),
    "pjm": dict(name="PJM", words="licensed source needed"),
}
# the grid's hourly demand: the operator's own table and its entity (session 138's pulls), where held
DEMAND = {
    "ercot": ("ercot_zone_load_hourly", ["ercot:ERCOT", "ercot:TOTAL", "ercot:ERCOT_TOTAL"]),
    "nyiso": ("nyiso_zone_load_hourly", ["nyiso:NYCA", "nyiso:TOTAL", "nyiso:NYISO"]),
    "caiso": ("caiso_area_load_hourly", ["caiso:CA ISO-TAC", "caiso:CAISO", "caiso:TOTAL"]),
    "isone": ("isone_zone_load_hourly", ["isone:ISO-NE", "isone:ISONE", "isone:TOTAL", "isone:.Z.NEWENGLAND"]),
}


def year_hours(y):
    return 8784 if pd.Timestamp(year=y, month=12, day=31).dayofyear == 366 else 8760


def to_std(index, std):
    """A UTC hourly index as (year, hour of the year) in a grid's standard time."""
    local = (index - pd.Timedelta(hours=std)).tz_localize(None)
    return local.year.values, ((local.dayofyear.values - 1) * 24 + local.hour.values)


def hourly_side(e, side):
    """One market of one region by hour (UTC): of the ways it is held (15-minute means, or the operator's own hourly
    report), the one that holds more hours, whole."""
    s = e[e["side"] == side]
    best, basis = None, ""
    for f, part in s.groupby("freq"):
        c = pc.hourly(pd.Series(part["value"].values, index=part["ts"]).sort_index(), f).dropna()
        if best is None or len(c) > len(best):
            best, basis = c, f
    return best, basis


def read_demand(in_dir, grid, std, log):
    """The grid's own hourly demand in MW by (year, hour of the year), or None when its table is not on this machine."""
    if grid not in DEMAND:
        return None, None
    table, entities = DEMAND[grid]
    path = os.path.join(in_dir, f"{table}.csv")
    if not os.path.exists(path):
        log(f"  {grid}: demand table {table} is not on this machine; no tight hours are written")
        return None, None
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    have = [x for x in entities if x in set(d["entity"].unique())]
    if not have:
        log(f"  {grid}: {table} holds no grid total among {entities} (it holds {sorted(d['entity'].unique())[:12]}); no tight hours are written")
        return None, None
    d = d[d["entity"] == have[0]]
    s = pd.Series(d["value"].values, index=pd.to_datetime(d["ts_utc"], utc=True)).sort_index()
    s = s[~s.index.duplicated(keep="last")].dropna()
    log(f"  {grid}: demand from {table}, entity {have[0]}, {len(s):,} hours, {s.index.min()} to {s.index.max()}")
    return s, f"{table} ({have[0]})"


def trimmed(arr):
    """A year's hourly list without its empty ends: {"s": the index of the first hour held, "v": the values from there to
    the last hour held, an hour not held between them null}."""
    held = np.nonzero(~np.isnan(arr))[0]
    a, b = int(held.min()), int(held.max()) + 1
    return {"s": a, "v": [None if np.isnan(v) else float(v) for v in arr[a:b]]}


def write_if_changed(path, obj):
    text = json.dumps(obj, separators=(",", ":"), allow_nan=False)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        a, b = dict(old), dict(obj)
        a.pop("built", None), b.pop("built", None)
        if a == b:
            return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="What a datacenter pays: the site's files for /cost-of-power")
    ap.add_argument("--out-dir", help="a trial run: the files under this directory; nothing in site/data")
    ap.add_argument("--since", type=int, help="write only the files of this year on (the index is always whole)")
    a = ap.parse_args(argv)
    out_dir = a.out_dir or SITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"datacenter_page_{run_id}.log"))
    lic, paused = pc.licenses()
    internal = [t for t in pc.TABLES if lic.get(t) not in (None, "public")]
    log(f"  internal price tables, not read: {internal}; publishers under review, not read: {sorted(paused)}")
    x = pc.read_prices(ip.OUT_DIR, FIRST, log)
    x = x[~x["table"].isin(internal)]
    x["iso"] = x["entity"].str.split(":", n=1).str[0]
    tables_read = sorted(x["table"].unique())

    index = {"built": built, "method": "docs/methods/datacenter_cost.md", "first": FIRST, "tight": TIGHT, "tables": tables_read,
             "grids": {}, "blank": {}}
    for iso, b in BLANK.items():
        nodes = sorted(x.loc[x["iso"] == iso, "entity"].str.split(":", n=1).str[1].unique()) if iso in paused else []
        index["blank"][iso] = dict(name=b["name"], words=b["words"], regions=nodes)
    written = kept = 0
    for iso, g in GRIDS.items():
        if iso in paused:
            index["blank"][iso] = dict(name=g["name"], words="paused while terms are reviewed", regions=[])
            continue
        sub = x[x["iso"] == iso]
        if sub.empty:
            log(f"  {iso}: no price row is held")
            continue
        years, regions = {}, []
        for entity, e in sub.groupby("entity"):
            node = entity.split(":", 1)[1]
            rec = {"id": node, "entity": entity}
            for side, key in (("rtm", "rt"), ("dam", "da")):
                h, basis = hourly_side(e, side)
                if h is None or h.empty:
                    continue
                ys, hs = to_std(h.index, g["std"])
                vals = np.round(h.values.astype(float), 2)
                for y in np.unique(ys):
                    m = ys == y
                    arr = np.full(year_hours(int(y)), np.nan)
                    arr[hs[m]] = vals[m]
                    years.setdefault(int(y), {}).setdefault(node, {})[key] = arr
                rec[key] = {"hours": int(len(h)), "first": ip.utc_iso(h.index.min()), "last": ip.utc_iso(h.index.max()), "basis": basis,
                            "tables": sorted(e.loc[e["side"] == side, "table"].unique())}
            if "rt" in rec or "da" in rec:
                regions.append(rec)
        regions.sort(key=lambda r: (r["id"] != g["main"], -max(r.get("rt", {}).get("hours", 0), r.get("da", {}).get("hours", 0)), r["id"]))
        demand, demand_source = read_demand(ip.OUT_DIR, iso, g["std"], log)
        dem_years = {}
        if demand is not None:
            ys, hs = to_std(demand.index, g["std"])
            for y in np.unique(ys):
                m = ys == y
                arr = np.full(year_hours(int(y)), np.nan)
                arr[hs[m]] = demand.values[m]
                dem_years[int(y)] = arr
        demand_summary = {}
        for y in sorted(set(years) | set(dem_years)):
            n = year_hours(y)
            obj = {"grid": iso, "year": y, "hours": n, "built": built, "regions": {}}
            for node, sides in sorted(years.get(y, {}).items()):
                obj["regions"][node] = {k: trimmed(arr) for k, arr in sides.items()}
            d = dem_years.get(y)
            if d is not None:
                held = int((~np.isnan(d)).sum())
                # the newest year is not whole: its hours due are those up to the last hour held
                due = n if y < max(dem_years) else int(np.nonzero(~np.isnan(d))[0].max()) + 1
                rec = {"hours_held": held, "hours_due": due}
                if held >= NEAR_DEMAND * due:
                    peak = float(np.nanmax(d))
                    tight = np.nonzero(d >= TIGHT * peak)[0]
                    obj["peak_mw"], obj["peak_hour"], obj["tight"] = round(peak, 1), int(np.nanargmax(d)), [int(i) for i in tight]
                    obj["demand_mean_mw"] = round(float(np.nanmean(d)), 1)
                    rec.update(peak_mw=obj["peak_mw"], peak_hour=obj["peak_hour"], tight_hours=len(tight), mean_mw=obj["demand_mean_mw"], whole=bool(y < max(dem_years)))
                demand_summary[str(y)] = rec
            if a.since and y < a.since:
                continue
            if write_if_changed(os.path.join(out_dir, f"{iso}_{y}.json"), obj):
                written += 1
            else:
                kept += 1
        index["grids"][iso] = dict(name=g["name"], std_hours_behind_utc=g["std"], std_name=g["zone"], main=g["main"], years=sorted(years), regions=regions,
                                   demand_source=demand_source, demand=demand_summary)
        log(f"  {iso}: {len(regions)} regions, years {min(years)} to {max(years)}" + (f", demand years {sorted(dem_years)}" if dem_years else ", no demand"))
    write_if_changed(os.path.join(out_dir, "index.json"), index)
    log(f"  files written {written}, unchanged {kept}; index.json; under {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
