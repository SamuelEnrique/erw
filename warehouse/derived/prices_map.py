#!/usr/bin/env python3
"""What power costs across the map: every hub and load zone a page may show, with its authority and region (session 8013).

Energy Research Warehouse (ERW). Chain 505, part E2 (the master plan's eighth tool). One page file,
site/data/regions/prices_map.json (contract: section 13 of docs/state/page_files_regions.md), for the "Price" switch
of the Grid tool's map. No table of its own and no request: every figure is computed from the public hub and zone price
tables that warehouse/derived/price_compare.py reads (its reader, its hourly rule and its license and pause handling are
used as they are), in each grid's own local time.

For each hub or zone (entity <iso>:<node>), day-ahead prices only:
    day                      the newest whole local day held before the build's own local day (all its hours held)
    day_avg                  USD/MWh   that day's mean price
    day_on_peak, day_off_peak USD/MWh  its on-peak and off-peak hours' means (price_board.py's rule: hours beginning
                                       06:00 to 21:00 local, Monday to Friday, Saturday too for CAISO, NERC holidays off)
    day_spread_top4_bottom4  USD/MWh   its four dearest hours' mean less its four cheapest
    avg_30d, negative_share_30d_pct    over the 30 local days to that day
    avg_12m, negative_share_12m_pct    over the 365 local days to that day
A window's figures are written only when at least 95 percent of its hours are held (price_compare.py's rule); otherwise
null with the reason. Grids whose prices are held for a license (warehouse/metadata/license_status.py) or paused
(paused_sources.csv) carry their key with every figure null and the words "license needed" or the pause; PJM holds no
price in the warehouse and is listed.

    python warehouse/derived/prices_map.py [--site-dir PATH]
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import price_compare as pc  # noqa: E402
import price_board as pb  # noqa: E402
import license_status as ls  # noqa: E402

SITE = os.path.join(ROOT, "site", "data", "regions")
METHOD = "docs/methods/prices_map.md"
LICENSE_NEEDED = "license needed"
NEAR = pc.NEAR_HOURS


def region_of(index, ba):
    for b in index.get("bas", []):
        if b.get("code") == ba:
            return b.get("region")
    return None


def whole_days(h, tz):
    """{local date: the day's hourly prices} for every local day all of whose hours are held."""
    loc = h.index.tz_convert(tz)
    out = {}
    for d, g in h.groupby(loc.date):
        need = int((pd.Timestamp(d + dt.timedelta(days=1), tz=tz) - pd.Timestamp(d, tz=tz)) / pd.Timedelta(hours=1))
        if len(g) == need:
            out[d] = g
    return out


def window(h, tz, end_day, days):
    """Mean and negative share over the `days` local days ending on end_day, or (None, None, why)."""
    b = pd.Timestamp(end_day + dt.timedelta(days=1), tz=tz).tz_convert("UTC")
    a = pd.Timestamp(end_day - dt.timedelta(days=days - 1), tz=tz).tz_convert("UTC")
    want = int((b - a) / pd.Timedelta(hours=1))
    w = h[(h.index >= a) & (h.index < b)]
    if len(w) < NEAR * want:
        return None, None, f"{len(w):,} of the window's {want:,} hours held, under {NEAR:.0%}"
    return round(float(w.mean()), 2), round(100 * float((w < 0).mean()), 2), None


def hub_doc(entity, iso, h, tz, today_local, holidays):
    days = whole_days(h, tz)
    before = sorted(d for d in days if d < today_local)
    if not before:
        return {"entity": entity, "day": None, "why": "no whole local day of day-ahead prices held before today"}
    d = before[-1]
    g = days[d]
    loc = g.index.tz_convert(tz).to_series(index=g.index)
    peak = pb.is_peak(loc, iso, holidays).to_numpy()
    doc = {"entity": entity, "node": entity.split(":", 1)[1], "day": d.isoformat(), "day_avg": round(float(g.mean()), 2),
           "day_on_peak": round(float(g[peak].mean()), 2) if peak.any() else None,
           "day_off_peak": round(float(g[~peak].mean()), 2) if (~peak).any() else None,
           "day_spread_top4_bottom4": round(float(g.nlargest(4).mean() - g.nsmallest(4).mean()), 2)}
    if not peak.any():
        doc["day_on_peak_why"] = "the day has no on-peak hour (a weekend or a NERC holiday)"
    for key, n in (("30d", 30), ("12m", 365)):
        avg, neg, why = window(h, tz, d, n)
        doc[f"avg_{key}"], doc[f"negative_share_{key}_pct"] = avg, neg
        if why:
            doc[f"window_{key}_why"] = why
    return doc


def build(log=print):
    lic, paused = pc.licenses()
    internal = [t for t in pc.TABLES if lic.get(t) not in (None, "public")]
    held = ls.held_grids()
    x = pc.read_prices(pc.ip.OUT_DIR, (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=400)).strftime("%Y-%m-%d"), log)
    x = x[(~x["table"].isin(internal)) & (x["side"] == "dam")]
    with open(os.path.join(SITE, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    holidays = pb.nerc_holidays(range(2024, 2029))
    now = pd.Timestamp.now(tz="UTC")
    grids, hubs = [], []
    for iso, g in pc.GRIDS.items():
        name, tz, ba = g["name"], g["tz"], g["ba"]
        entry = {"grid": name, "iso": iso, "ba": ba, "region": region_of(index, ba), "tz": tz}
        if iso in paused:
            p = paused[iso]
            entry.update(state="paused", why=f"{p['publisher']}'s terms are under review (pulls paused {p['paused_on']}); no figure is derived from its prices")
            grids.append(entry)
            continue
        mine = x[x["entity"].str.startswith(iso + ":")]
        if name in held:
            entry.update(state="held", why=f"{LICENSE_NEEDED}: {ls.note(name)}", nodes=sorted(mine["entity"].unique().tolist()))
            grids.append(entry)
            continue
        today_local = now.tz_convert(tz).date()
        n = 0
        for ent, e in mine.groupby("entity"):
            parts = [pc.hourly(s.set_index("ts")["value"].sort_index(), f) for f, s in e.groupby("freq")]
            h = pd.concat(parts).sort_index()
            h = h[~h.index.duplicated(keep="first")]
            d = hub_doc(ent, iso, h, tz, today_local, holidays)
            d.update(grid=name, ba=ba, region=entry["region"], table=e["table"].iloc[0] if e["table"].nunique() == 1 else sorted(e["table"].unique().tolist()))
            hubs.append(d)
            n += 1
        entry.update(state="shown", hubs=n)
        grids.append(entry)
    grids.append({"grid": "PJM", "iso": "pjm", "ba": "PJM", "region": region_of(index, "PJM"), "state": "held",
                  "why": f"{LICENSE_NEEDED}: PJM's data is held for a license, and no PJM hub or zone price is in the warehouse"})
    for gname in sorted(held - {g["grid"] for g in grids}):
        grids.append({"grid": gname, "state": "held", "why": f"{LICENSE_NEEDED}: {ls.note(gname)}"})
    return pc.ip.utc_iso(now), grids, hubs, internal


def bas_of(grids, hubs):
    """{EIA-930 code: what the map colors that authority's area by}: the grid's main hub (price_board.MAIN, the board's
    and markets.json's choice), or the grid's state and reason where nothing is shown."""
    out = {}
    for g in grids:
        ba = g.get("ba")
        if not ba:
            continue
        if g["state"] != "shown":
            out[ba] = {"grid": g["grid"], "state": g["state"], "why": g["why"]}
            continue
        main = f"{g['iso']}:{pb.MAIN.get(g['iso'], '')}"
        h = next((x for x in hubs if x["entity"] == main), None)
        out[ba] = {"grid": g["grid"], "state": "shown", "hub": main, "hubs_in_grid": sum(1 for x in hubs if x["grid"] == g["grid"]),
                   **({k: h.get(k) for k in ("day", "day_avg", "day_on_peak", "day_off_peak", "day_spread_top4_bottom4", "avg_30d",
                                            "negative_share_30d_pct", "avg_12m", "negative_share_12m_pct", "window_30d_why", "window_12m_why", "day_on_peak_why")
                       if k in h} if h else {"why": f"the main hub {main} holds no day-ahead price"})}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site-dir", default=SITE)
    a = ap.parse_args(argv)
    built, grids, hubs, internal = build()
    doc = {"built": built, "tables": [t for t in pc.TABLES if t not in internal], "method": METHOD, "license": "public",
           "measures": {"day_avg": "USD/MWh", "day_on_peak": "USD/MWh", "day_off_peak": "USD/MWh", "day_spread_top4_bottom4": "USD/MWh",
                        "avg_30d": "USD/MWh", "negative_share_30d_pct": "percent of hours", "avg_12m": "USD/MWh", "negative_share_12m_pct": "percent of hours"},
           "rules": {"market": "day-ahead", "near_hours": NEAR, "on_peak": "hours beginning 06:00 to 21:00 local, Monday to Friday (CAISO: to Saturday), NERC holidays off"},
           "grids": grids, "hubs": hubs, "bas": bas_of(grids, hubs)}
    path = os.path.join(a.site_dir, "prices_map.json")
    os.makedirs(a.site_dir, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    os.replace(tmp, path)
    for g in grids:
        print(f"{g['grid']}: {g['state']}" + (f", {g.get('hubs')} hubs and zones" if g["state"] == "shown" else ""))
    print(f"wrote {path} ({os.path.getsize(path):,} bytes, {len(hubs)} hubs and zones)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
