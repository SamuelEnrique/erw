#!/usr/bin/env python3
"""The two historical stories of /network (session 68): Texas during Uri, and the June 2025 heat.

Energy Research Warehouse (ERW). Writes, for each story, one compact snapshot in the shape the network already draws:

    site/public/network/story_<event>.json                 served by the site as a static file
    erw-public/network/story_<event>.json (Supabase Storage, the public bucket of the hourly network snapshot), with --upload

from eia930_event_hourly_interchange (EIA-930 hourly interchange of every pair and demand of every balancing authority
for the two windows), carbon_intensity_daily (the sphere color, the seven ISO balancing authorities) and
eia930_all_storage (battery storage, where EIA-930 reports it and the warehouse holds it), and the real-time price of each
ISO's main hub where a public price is held (not PJM's). Node positions and names are
those of the network's committed snapshot (site/data/grid_network.json), so a story draws the same network; a balancing
authority of the window that is not in it is left out and counted.

Each pair is counted once, by the network's own rule (warehouse/derived/grid_network.py, RULE): its flow is read from the
balancing authority whose code sorts first, as that one reported it; in an hour it did not report, from the other's
report with the sign flipped. An hour neither reported is null, never filled. Carbon intensity is that local day's
(intensity_generation, kg CO2/MWh); where it is not held the sphere is grey, as on the live network.

    python warehouse/derived/network_stories.py [--upload]
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import grid_network as gn  # noqa: E402  (RULE)
import iso_prices as ip  # noqa: E402

EVENTS = {
    "uri_2021": dict(title="Texas during Uri", start="2021-02-07", end="2021-02-24", tz="America/Chicago", focus="ERCO"),
    "east_heat_2025": dict(title="The June 2025 heat", start="2025-06-20", end="2025-06-28", tz="America/New_York", focus="PJM"),
}
TABLE = "eia930_event_hourly_interchange"
OUT_DIR = os.path.join(ROOT, "site", "public", "network")
COMMITTED = os.path.join(ROOT, "site", "data", "grid_network.json")


def read(name, cols):
    return pd.read_csv(os.path.join(ip.OUT_DIR, name + ".csv"), skiprows=ip.header_rows(os.path.join(ip.OUT_DIR, name + ".csv")), usecols=cols, dtype=str, keep_default_na=False)


HUB_BA = {"ercot": "ERCO", "caiso": "CISO", "nyiso": "NYIS", "miso": "MISO", "spp": "SWPP", "isone": "ISNE"}  # PJM: internal prices


def hub_prices(log=print):
    """{BA: hourly real-time price of its ISO's main hub, USD/MWh}, complete hours only, from the price tables the cost of
    power reads (cost_of_power.prices_of); PJM's prices are internal and not read."""
    import cost_of_power as cp
    out = {}
    for iso, ba in HUB_BA.items():
        df, _ = cp.prices_of(iso, "rtm", lambda m: None)
        out[ba] = cp.hourly(df)
    return out


def build(event, spec, x, base, ci, bat, prices):
    nodes = {n["id"]: n for n in base["nodes"]}
    a = pd.Timestamp(spec["start"]).tz_localize(spec["tz"]).tz_convert("UTC")
    b = (pd.Timestamp(spec["end"]) + pd.Timedelta(days=1)).tz_localize(spec["tz"]).tz_convert("UTC")
    hours = pd.date_range(a, b, freq="h", inclusive="left")
    hs = [h.strftime("%Y-%m-%dT%H:%M:%SZ") for h in hours]
    e = x[x["event"] == event]
    flows = e[e["variable"] == "interchange_mw"].assign(fr=lambda z: z["entity"].str[7:].str.split("-").str[0],
                                                        to=lambda z: z["entity"].str[7:].str.split("-").str[1])
    seen = set(flows["fr"]) | set(flows["to"])
    left_out = sorted(c for c in seen if c not in nodes)
    flows = flows[flows["fr"].isin(nodes) & flows["to"].isin(nodes)]
    by = {(r.fr, r.to): {} for r in flows[["fr", "to"]].drop_duplicates().itertuples()}
    for r in flows.itertuples():
        by[(r.fr, r.to)][r.ts_utc] = float(r.value)
    links, from_other, missing = [], 0, 0
    for p, q in sorted({tuple(sorted(k)) for k in by}):
        own, other = by.get((p, q), {}), by.get((q, p), {})
        mw = []
        for h in hs:
            if h in own:
                mw.append(round(own[h], 1))
            elif h in other:
                mw.append(round(-other[h], 1))
                from_other += 1
            else:
                mw.append(None)
                missing += 1
        links.append(dict(a=p, b=q, mw=mw))
    dem = e[e["variable"] == "demand_mw"].assign(ba=lambda z: z["entity"].str[7:])
    demand = {}
    for ba, g in dem[dem["ba"].isin(nodes)].groupby("ba"):
        m = dict(zip(g["ts_utc"], g["value"].astype(float)))
        demand[ba] = [round(m[h], 1) if h in m else None for h in hs]
    demand_missing = sum(v is None for arr in demand.values() for v in arr)
    # carbon intensity: the local day of each hour, where held
    days = sorted({h.tz_convert(spec["tz"]).strftime("%Y-%m-%d") for h in hours})
    intensity = {}
    for ba, g in ci.groupby("ba"):
        if ba in nodes:
            m = dict(zip(g["day"], g["value"].astype(float)))
            if any(d in m for d in days):
                intensity[ba] = {d: round(m[d], 2) for d in days if d in m}
    batteries = {}
    for ba, g in bat.groupby("ba"):
        m = dict(zip(g["ts_utc"], g["value"].astype(float)))
        arr = [round(m[h], 1) if h in m else None for h in hs]
        if any(v is not None for v in arr) and ba in nodes:
            batteries[ba] = arr
    hub = {}
    for ba, ser in prices.items():
        arr = [round(float(ser[h]), 2) if h in ser.index else None for h in hours]
        if any(v is not None for v in arr):
            hub[ba] = arr
    snap = dict(event=event, title=spec["title"], focus=spec["focus"], tz=spec["tz"], window=[spec["start"], spec["end"]], hours=hs,
                built=ip.utc_iso(pd.Timestamp.now(tz="UTC")), rule=gn.RULE, links=links, demand=demand, intensity=intensity,
                intensity_days=days, batteries=batteries, hub_prices=hub,
                missing=dict(link_hours=missing, link_hours_from_other_side=from_other, demand_hours=demand_missing, left_out_bas=left_out,
                             nodes_without_demand=sorted(set(nodes) - set(demand)), batteries_reported=sorted(batteries)),
                source=[TABLE, "carbon_intensity_daily", "eia930_all_storage", "ercot_all_hub_prices_history", "iso_hub_prices_history", "iso_rtm_hub_prices"])
    return snap


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the network's historical stories")
    ap.add_argument("--upload", action="store_true", help="also upload each story to the public Storage bucket erw-public (needs the data lock)")
    a = ap.parse_args(argv)
    base = json.load(open(COMMITTED, encoding="utf-8"))
    x = read(TABLE, ["entity", "variable", "ts_utc", "value", "event"])
    ci = read("carbon_intensity_daily", ["entity", "variable", "ts_utc", "value"])
    ci = ci[ci["variable"] == "intensity_generation"].assign(ba=lambda z: z["entity"].str[7:], day=lambda z: z["ts_utc"].str[:10])
    bat = read("eia930_all_storage", ["entity", "variable", "ts_utc", "value"])
    bat = bat[bat["variable"] == "net_generation_battery_mw"].assign(ba=lambda z: z["entity"].str[7:])
    prices = hub_prices()
    os.makedirs(OUT_DIR, exist_ok=True)
    for event, spec in EVENTS.items():
        snap = build(event, spec, x, base, ci, bat, prices)
        body = json.dumps(snap, separators=(",", ":"))
        path = os.path.join(OUT_DIR, f"story_{event}.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        m = snap["missing"]
        print(f"{event}: {len(snap['hours'])} hours, {len(snap['links'])} pairs, {len(snap['demand'])} BAs with demand, "
              f"{len(snap['intensity'])} with carbon, batteries {m['batteries_reported']}, hub prices {sorted(snap['hub_prices'])}; pair-hours missing {m['link_hours']}, "
              f"from the other side {m['link_hours_from_other_side']}; demand hours missing {m['demand_hours']}; left out {m['left_out_bas']}; "
              f"{len(body):,} bytes -> {os.path.relpath(path, ROOT)}")
        if a.upload:
            import network_hourly as nh
            ip._require_lock(os.path.join(ip.OUT_DIR, "network_stories"), "uploading a network story")
            base_url = nh.origin(nh.env("SUPABASE_URL"))
            obj = f"network/story_{event}.json"
            was = nh.OBJECT
            nh.OBJECT = obj
            try:
                nh.upload(base_url, nh.env("SUPABASE_SERVICE_KEY"), body.encode("utf-8"))
            finally:
                nh.OBJECT = was
            print(f"  uploaded to erw-public/{obj}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
