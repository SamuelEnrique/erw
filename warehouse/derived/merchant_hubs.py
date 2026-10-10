#!/usr/bin/env python3
"""What a generator earns at every public hub and zone (session 183): the seller's model, one hub at a time.

Energy Research Warehouse (ERW). No warehouse table is written and no request is made. Until this session the page
/cost-of-power/seller priced its revenue, its months and its debt coverage at the grid's main hub whatever hub was
chosen, while the capture price and the contract followed the hub: two footings on one page. This builder runs the
seller's own model (merchant_revenue.build_iso: the same fleet shape, the same battery optimum, the same peaker rule,
the same 90 percent rule for a month) with each hub's or zone's own hourly price in place of the main hub's, and
writes the site's files for the page:

    site/data/seller/hubs/index.json            the hubs held, each one's market, tables, first and last hour, and the
                                                check of this builder against the page's snapshot at the main hub
    site/data/seller/hubs/<grid>/_grid.json     the grid's hourly index (its first hour), Henry Hub by hour, and each
                                                local month's [first index, last index + 1, hours in the month]
    site/data/seller/hubs/<grid>/<hub>.json     one hub: the months of every asset (the snapshot's own fields) and its
                                                hourly price on the grid's index (the peaker at the reader's heat
                                                rate); ERCOT's hubs also hold the stress days

    python warehouse/derived/merchant_hubs.py                                   # the tables of this copy
    python warehouse/derived/merchant_hubs.py --in-dir C:/.../warehouse/output  # the tables of another copy (read only)
    python warehouse/derived/merchant_hubs.py --out-dir DIR                     # a trial run: the files under DIR
    python warehouse/derived/merchant_hubs.py --only ercot                      # one grid (a trial)

Which price. The hubs and zones are those of the capture file (site/data/seller/capture.json), and the prices are read
exactly as warehouse/derived/capture_price.py reads them (its tables, its licence test, its rule for an hour of real
time: the mean of the hour's four 15-minute prices, held only when all four are). One market is kept for each hub: the
market the page shows the hub's capture price in (real time where the hub holds twelve counted months of it, else
day-ahead where it holds twelve, else whichever it holds), so the revenue and the capture price beside it are on one
market. The file says which, and the page writes it beside every figure.

The main hub is not written: the page keeps its own snapshot there (site/data/merchant_snapshot.json), so no number of
the default page moves. It is solved here all the same, at real-time prices, and set beside the snapshot month by
month: index.json holds the largest difference of each asset (`check`), and tests/test_session183.py reads it.

Nothing is filled: a hub with no hour of price in a month has no row for it, and a month under 90 percent of its hours
is shown by the page and not counted, as at the main hub. Method: docs/methods/generator_earns_algorithm.md.
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402
import capture_price as cq  # noqa: E402  (the hubs' prices, read as the capture price reads them)
import event_window as ew  # noqa: E402
import iso_prices as ip  # noqa: E402
import merchant_revenue as mr  # noqa: E402  (the model itself)
import price_board as pb  # noqa: E402
import price_compare as pc  # noqa: E402

SITE_DIR = os.path.join(ROOT, "site", "data", "seller", "hubs")
CAPTURE = os.path.join(ROOT, "site", "data", "seller", "capture.json")
SNAPSHOT = mr.SNAPSHOT
METHOD = "docs/methods/generator_earns_algorithm.md"
SINCE = "2018-06-30"   # the model's fleet shape begins on 2018-07-01 (merchant_revenue.SHAPE_START)
ASSETS = ["solar", "wind"] + [f"battery_{d}h" for d in mr.DURATIONS] + ["peaker"]
SIDE = {"rt": "rtm", "da": "dam"}
r4 = pb.r4


def slug(node):
    return re.sub(r"[^a-z0-9]+", "_", node.lower()).strip("_")


def market_of(hub):
    """The market the page shows this hub's capture price in (site/app/cost-of-power/seller/page.tsx, `mk`), from the
    capture file's own months."""
    def whole12(m):
        for f in cq.FUELS:
            months = hub.get(m, {}).get(f)
            if not months:
                continue
            t = cq.last_twelve(months)
            if t and cq.figure([months[k] for k in t]):
                return True
        return False

    def has(m):
        return any(hub.get(m, {}).get(f) for f in cq.FUELS)
    if whole12("rt"):
        return "rt"
    if whole12("da"):
        return "da"
    return "rt" if has("rt") or not has("da") else "da"


def fleet_hours(iso, cache_dir, log):
    """The fleet's hours as the model reads them (merchant_revenue.fuel_hours), kept under the cache folder while the
    workbook is the same file: reading one workbook takes minutes."""
    path, _ = mr.workbook_of(mr.BA[iso])
    stamp = f"{os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}:{os.path.getsize(path)}"
    cached = os.path.join(cache_dir, f"fuel_hours_{iso}.pkl") if cache_dir else None
    if cached and os.path.exists(cached):
        kept = pd.read_pickle(cached)
        if kept.attrs.get("stamp") == stamp:
            log(f"  {iso}: the fleet's hours read back from {cached} (workbook {stamp})")
            return kept, path
    fuel = mr.fuel_hours(path)
    if iso == "caiso":
        fuel = cj.true_hours(fuel)
    if cached:
        os.makedirs(cache_dir, exist_ok=True)
        fuel.attrs["stamp"] = stamp
        fuel.to_pickle(cached)
    return fuel, path


def months_of(monthly):
    """The snapshot's own month records (merchant_revenue.main), without the hourly indices."""
    return {m: {"flat": r4(o["flat_price"]), **{a: {k: (r4(v) if v is not None else None) for k, v in o[a].items()} for a in o if isinstance(o[a], dict)}}
            for m, o in sorted(monthly.items())}


def stress_of(h, bat, ev, day_index):
    """ERCOT's stress days for one hub, as merchant_revenue.main writes them for the main hub: the days are those of
    event_window_daily (the hub average's), the revenue is this hub's."""
    out = {}
    for e in mr.STRESS:
        x = ev[(ev["event"] == e) & (ev["entity"] == "ercot:HB_HUBAVG") & (ev["variable"] == "rt_mean")]
        win = next(w for w in ew.MULTI + ew.EVENTS if w["event"] == e)
        days = []
        for day in sorted(x["ts"].dt.strftime("%Y-%m-%d")):
            g = h[h["day"] == day]
            ix = day_index.get(day)
            d = {"day": day, "window": win["start"] <= day <= win["end"], "hours": len(g), "i0": ix[0] if ix else None, "i1": ix[1] if ix else None}
            for asset in ("solar", "wind"):
                d[asset] = r4((g[asset] * g["p"]).sum()) if g[asset].notna().any() else None
            for du in mr.DURATIONS:
                d[f"battery_{du}h"] = r4(bat[du][day][0]) if day in bat[du] else None
            days.append(d)
        out[e] = {"start": win["start"], "end": win["end"], "days": days}
    return out


def check_main(monthly, snap_iso, near):
    """This builder at the main hub against the page's snapshot, over the months the snapshot counts. A month is
    compared when both hold the same hours of it (a battery: days); a month whose hours differ was read from another
    price table or a later copy of it, and is counted apart (`hours_differ`), never compared. For each asset: the
    months compared, the largest difference of revenue per MW in USD and as a share, and the month it falls in."""
    out = {}
    for a in ASSETS:
        n, other, worst, share, at = 0, 0, 0.0, 0.0, ""
        for m, o in monthly.items():
            s = snap_iso["months"].get(m, {}).get(a)
            if not s or a not in o:
                continue
            days = pd.Period(m).days_in_month
            held = (s["hours"] / days if a.startswith("battery") else s["hours"] / snap_iso["months"][m]["him"]) >= near - 1e-9
            if not held:
                continue
            if int(o[a]["hours"]) != int(s["hours"]):
                other += 1
                continue
            n += 1
            d = abs(r4(o[a]["revenue_per_mw"]) - s["revenue_per_mw"])
            if d > worst:
                worst, at = d, m
                share = d / abs(s["revenue_per_mw"]) if s["revenue_per_mw"] else 0.0
        out[a] = {"months": n, "hours_differ": other, "max_abs_usd_per_mw": round(worst, 4), "max_share": round(share, 8), "at": at}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The seller's model at every public hub and zone")
    ap.add_argument("--in-dir", help="read the tables from this folder (another copy's warehouse/output); nothing is written there")
    ap.add_argument("--out-dir", help="a trial run: the files under this directory; nothing in site/data")
    ap.add_argument("--cache-dir", help="keep the fleet's hours read from each workbook under this folder")
    ap.add_argument("--only", help="one grid (a trial run; the index then holds that grid alone)")
    ap.add_argument("--main-only", action="store_true", help="solve the main hubs alone and write their check into the index already under the output folder; no hub file is written")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir) if a.in_dir else ip.OUT_DIR
    out_dir = os.path.abspath(a.out_dir) if a.out_dir else SITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else os.path.join(ROOT, "warehouse", "output", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"merchant_hubs_{run_id}.log"))
    log(f"ERW merchant hubs run {run_id}: tables from {in_dir}")
    ip.OUT_DIR = in_dir
    cq.SINCE = SINCE

    with open(CAPTURE, encoding="utf-8") as f:
        capture = json.load(f)
    with open(SNAPSHOT, encoding="utf-8") as f:
        snap = json.load(f)
    near = snap["defaults"]["near"]
    lic, _ = pc.licenses()
    tables = cq.readable(in_dir, lic, log)
    grids = [g for g in cq.GRIDS if g in capture["grids"] and not ip.paused(g) and (not a.only or g == a.only)]
    log(f"  price tables read: {tables}; grids: {grids}")
    parts = []
    for i, t in enumerate(tables):
        x = cq.read_one(in_dir, t, log)
        if x is None:
            continue
        x["iso"] = x["entity"].astype(str).str.split(":", n=1).str[0]
        x = x[x["iso"].isin(grids)].drop(columns="iso")
        x["rank"] = np.int8(i)
        parts.append(x)
    x = pd.concat(parts, ignore_index=True)
    del parts
    x["entity"] = x["entity"].astype(str)

    gens, vint = mr.read_gens()
    hh, hhrows = mr.henry_hub()
    ev = ip.read_series(os.path.join(ip.OUT_DIR, "event_window_daily.csv"), cols=ip.SERIES_COLS + ["ba", "event"])
    ev["ts"] = pd.to_datetime(ev["ts_utc"], utc=True)

    index = {"built": built, "method": METHOD, "near": near, "since": SINCE, "snapshot_built": snap["built"], "capture_built": capture["built"],
             "henry_hub": f"eia_fuel_spot_prices, {hhrows['ts'].min():%Y-%m-%d} to {hhrows['ts'].max():%Y-%m-%d}", "eia860m": vint, "grids": {}}
    failed = False
    checks = {}
    for iso in grids:
        cg = capture["grids"][iso]
        tz = pb.TZ[iso]
        fuel, wb = fleet_hours(iso, a.cache_dir, log)
        sub = x[x["entity"].str.startswith(iso + ":")]
        solved, check = {}, None
        for hub in cg["hubs"]:
            node, entity = hub["id"], hub["entity"]
            e = sub[sub["entity"] == entity]
            main_hub = node == cg["main"]
            if a.main_only and not main_hub:
                continue
            mk = "rt" if main_hub else market_of(hub)
            price, basis, tabs = cq.hourly_side(e, SIDE[mk])
            if price is None or price.empty:
                log(f"  {iso} {node}: no {mk} price read; no model")
                continue
            price = price.sort_index()
            h, monthly, bat, _, _, _, over, neg = mr.build_iso(iso, gens, hh, log, [], price=price, table=", ".join(tabs), fuel=fuel)
            if main_hub:
                check = check_main(monthly, snap["isos"][iso], near)
                checks[iso] = {"check": check, "check_tables": tabs, "check_basis": basis}
                log(f"  {iso} {node}: the main hub ({', '.join(tabs)}, {basis}), against the snapshot of {snap['built']}: {check}")
                continue
            solved[node] = dict(entity=entity, market=mk, basis=basis, tables=tabs, h=h, monthly=monthly, bat=bat)
            log(f"  {iso} {node}: {mk}, {len(h):,} hours {h.index.min()} to {h.index.max()}, {len(monthly)} months")
        if not solved:
            continue
        # the grid's hourly index: every hub's price sits on it, so a month's hours are the same indices for every hub
        first = min(s["h"].index.min() for s in solved.values())
        last = max(s["h"].index.max() for s in solved.values())
        grid = pd.date_range(first, last, freq="h")
        gl = grid.tz_convert(tz)
        gm, gd = gl.strftime("%Y-%m"), gl.strftime("%Y-%m-%d")
        days = pd.to_datetime(sorted(set(gd)))
        hhd = hh.reindex(hh.index.union(days)).sort_index().ffill().reindex(days)
        by_day = dict(zip(days.strftime("%Y-%m-%d"), hhd.values))
        hh_hours = [None if pd.isna(by_day[d]) else round(float(by_day[d]), 3) for d in gd]
        month_index = {}
        for m in sorted(set(gm)):
            ix = np.flatnonzero(gm == m)
            month_index[m] = [int(ix.min()), int(ix.max()) + 1, mr.cp.hours_in_month(m, tz)]
        day_index = {}
        if iso == "ercot":
            pos = pd.Series(np.arange(len(grid)), index=gd)
            lo, hi = pos.groupby(level=0).min(), pos.groupby(level=0).max()
            day_index = {d: [int(lo[d]), int(hi[d]) + 1] for d in lo.index}
        os.makedirs(os.path.join(out_dir, iso), exist_ok=True)
        with open(os.path.join(out_dir, iso, "_grid.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"iso": iso, "tz": tz, "start": first.strftime("%Y-%m-%dT%H:%M:%SZ"), "hours": len(grid), "months": month_index, "hh": hh_hours}, f, separators=(",", ":"), allow_nan=False)
        hubs, names = {}, set()
        for node, s in solved.items():
            name = slug(node)
            if name in names or name == "_grid":
                raise RuntimeError(f"{iso}: two hubs share the file name {name}")
            names.add(name)
            hp = s["h"]["p"].reindex(grid)
            rec = {"id": node, "entity": s["entity"], "market": s["market"], "months": months_of(s["monthly"]),
                   "price": [None if pd.isna(v) else round(float(v), 2) for v in hp]}
            if iso == "ercot":
                rec["stress"] = stress_of(s["h"], s["bat"], ev, day_index)
            path = os.path.join(out_dir, iso, f"{name}.json")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(rec, f, separators=(",", ":"), allow_nan=False)
            hubs[node] = {"file": f"{iso}/{name}.json", "market": s["market"], "basis": s["basis"], "tables": s["tables"], "first": ip.utc_iso(s["h"].index.min()),
                          "last": ip.utc_iso(s["h"].index.max()), "months": len(s["monthly"]), "bytes": os.path.getsize(path)}
        index["grids"][iso] = {"name": cg["name"], "tz": tz, "main": cg["main"], "workbook": os.path.basename(wb), "file": f"{iso}/_grid.json", **checks.get(iso, {"check": None}), "hubs": hubs}
        if check is None:
            log(f"  {iso}: the main hub was not solved, so there is no check against the snapshot")
            failed = True
    if a.main_only:
        # the check alone: the hub files and the rest of the index stay as the last whole run wrote them
        with open(os.path.join(out_dir, "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        for iso, c in checks.items():
            index["grids"][iso].update(c)
        index["check_run"] = built
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, separators=(",", ":"), allow_nan=False)
    n = sum(len(g["hubs"]) for g in index["grids"].values())
    size = sum(h["bytes"] for g in index["grids"].values() for h in g["hubs"].values())
    log(f"  written: {n} hubs of {len(index['grids'])} grids under {out_dir} ({size:,} bytes of hub files)")
    log.close()
    print(f"merchant hubs: {n} hubs and zones of {len(index['grids'])} grids, {size:,} bytes; {os.path.join(out_dir, 'index.json')}")
    for iso, g in index["grids"].items():
        print(f"  {iso} main hub against the snapshot: {g['check']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
