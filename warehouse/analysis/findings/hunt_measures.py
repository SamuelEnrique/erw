#!/usr/bin/env python3
"""The weekly hunt's own measures (session 251): thirteen pattern families that are not a finding's card.

Energy Research Warehouse (ERW). A pattern of session 233 reads one measure by year from the rows of a finding written
for /analysis. The families here are measures by region and by year computed straight from warehouse tables, for the
hunt alone: each function returns

    {"rows":   [{"region", "words", "year", "value", "n", "context"}],   one row a region and local year held
     "tables": {region: [the ERW tables whose rows that region's numbers rest on]}}

and hunt.py tests each region's series as it tests a finding's (the claim, the three tests, new or changed). "context"
is a second number of the same region and year that the family's question names (solar's share beside the capture
rate, the battery fleet beside curtailment); it is printed beside the claim and never tested: the claim states a
change and not its cause. A blank context is a year the warehouse does not hold for it.

Session 252's lessons are built in: no measure here is one interval of a year (medians, shares of hours or days, and
counts over a year), and "tables" names only the tables a region's own rows come from.

Regions: the seven grids by their name (ercot, caiso, pjm, miso, spp, nyiso, isone) and a node of a grid as
<grid>_<node>. The families that read EIA-930 are run on the seven grids' balancing authorities: the daily
interchange of smaller respondents holds reporting faults (Arizona Public Service's 2019 has the other sign), and
EIA's region totals (CAL, MIDA, US48 and the like) are not balancing authorities. hunt.py never drafts a region of a
grid that needs a license or is held, whoever published the rows.

A table that is not on this machine raises NoData for its family; nothing is filled in.
"""

import math
import os

import numpy as np
import pandas as pd

from findings_common import NoData, read_table, to_utc

SOURCE_PATH = os.path.abspath(__file__)
GRID = {"ercot": "ERCOT", "caiso": "CAISO", "pjm": "PJM", "miso": "MISO", "spp": "SPP", "nyiso": "NYISO", "isone": "ISO-NE"}
TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "pjm": "America/New_York", "miso": "America/Chicago",
      "spp": "America/Chicago", "nyiso": "America/New_York", "isone": "America/New_York"}
BA_GRID = {"ERCO": "ercot", "CISO": "caiso", "PJM": "pjm", "MISO": "miso", "SWPP": "spp", "NYIS": "nyiso", "ISNE": "isone"}
# The datacenter markets a balancing authority holds, as places (no number): the words beside the demand-growth family.
DATACENTER_PLACES = {"pjm": "northern Virginia, Ohio and Chicago's suburbs", "ercot": "Dallas, Austin and San Antonio", "caiso": "Silicon Valley",
                     "miso": "the Midwest's new campuses", "spp": "the Plains", "nyiso": "New York", "isone": "New England"}
ERCOT_HUBS = {"HB_HUBAVG": "hub average", "HB_NORTH": "North hub", "HB_HOUSTON": "Houston hub", "HB_SOUTH": "South hub", "HB_WEST": "West hub"}
CAISO_HUBS = {"TH_NP15_GEN-APND": "NP15", "TH_SP15_GEN-APND": "SP15", "TH_ZP26_GEN-APND": "ZP26"}
EVENING = (17, 21)                # local clock hours 17 to 21: 5 PM to 10 PM, the evening of finding 10
NIGHT = (0, 5)                    # local clock hours 0 to 5: midnight to 6 AM
DAY_PARTS = [("night", "midnight to 6 AM", 0, 5), ("morning", "6 AM to 11 AM", 6, 10), ("midday", "11 AM to 4 PM", 11, 15),
             ("evening", "4 PM to 9 PM", 16, 20), ("late", "9 PM to midnight", 21, 23)]
STRESS_SHARE = 0.05               # a year's stress days: its 5 percent of days with the highest demand
_CACHE = {}


def _cached(key, build):
    if key not in _CACHE:
        _CACHE[key] = build()
    return _CACHE[key]


def clear_cache():
    _CACHE.clear()


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def series(name, in_dir, variables=None, entities=None, entity_prefix=None, extra=()):
    """A standard series table's rows as (entity, variable, ts, value), filtered while it is read."""
    def keep(c):
        m = pd.Series(True, index=c.index)
        if variables is not None:
            m &= c["variable"].isin(variables)
        if entities is not None:
            m &= c["entity"].isin(entities)
        if entity_prefix is not None:
            m &= c["entity"].str.startswith(entity_prefix)
        return m
    d = read_table(name, in_dir, usecols=["entity", "variable", "ts_utc", "value", *extra], keep=keep)
    d["value"] = _num(d["value"])
    d = d.dropna(subset=["value"]).copy()
    d["ts"] = to_utc(d["ts_utc"])
    return d


def _row(region, words, year, value, n, context=None):
    ok = value is not None and not (isinstance(value, float) and (math.isnan(value) or math.isinf(value)))
    c = None if context is None or (isinstance(context, float) and (math.isnan(context) or math.isinf(context))) else float(context)
    return {"region": region, "words": words, "year": int(year), "value": float(value) if ok else None, "n": float(n), "context": c}


def ba_region(code):
    return BA_GRID[code]


def ba_words(code):
    return GRID[BA_GRID[code]]


# ---------------------------------------------------------------------------------------------------------------------
# hourly prices, read once a hunt
# ---------------------------------------------------------------------------------------------------------------------
def _hourly(d, tz):
    """15-minute or hourly price rows (ts_utc, value, market, node) as one row a node and hour: rt and da, the local
    year and the local clock hour. An hour's real-time price is the mean of its held intervals."""
    d = d.copy()
    d["value"] = _num(d["value"])
    d = d.dropna(subset=["value"])
    d["hour"] = to_utc(d["ts_utc"]).dt.floor("h")
    d["kind"] = np.where(d["market"].str.endswith("_dam"), "da", "rt")
    h = d.groupby(["node", "kind", "hour"], as_index=False)["value"].mean()
    w = h.pivot_table(index=["node", "hour"], columns="kind", values="value").reset_index()
    for k in ("rt", "da"):
        if k not in w:
            w[k] = np.nan
    local = w["hour"].dt.tz_convert(tz)
    w["year"], w["lhour"], w["day"] = local.dt.year, local.dt.hour, local.dt.strftime("%Y-%m-%d")
    return w


def ercot_prices(in_dir):
    def build():
        cols = ["ts_utc", "value", "market", "node"]
        hubs = read_table("ercot_all_hub_prices_history", in_dir, usecols=cols,
                          keep=lambda c: c["market"].isin(["ercot_rtm", "ercot_dam"]) & c["node"].isin(list(ERCOT_HUBS)))
        zones = read_table("ercot_zone_prices_history", in_dir, usecols=cols,
                           keep=lambda c: c["market"].isin(["ercot_rtm", "ercot_dam"]) & c["node"].str.startswith("LZ_"))
        return _hourly(pd.concat([hubs, zones], ignore_index=True), TZ["ercot"])
    return _cached(("ercot_prices", in_dir), build)


def caiso_prices(in_dir):
    def build():
        cols = ["ts_utc", "value", "market", "node"]
        keep = lambda c: c["market"].isin(["caiso_rtm", "caiso_dam"]) & c["node"].isin(list(CAISO_HUBS))  # noqa: E731
        a = read_table("iso_hub_prices_history", in_dir, usecols=cols, keep=keep)
        b = read_table("iso_zone_prices_history", in_dir, usecols=cols, keep=keep)
        a["table"], b["table"] = "iso_hub_prices_history", "iso_zone_prices_history"
        both = pd.concat([a, b], ignore_index=True)
        w = _hourly(both, TZ["caiso"])
        w.attrs["tables"] = {n: sorted(set(g["table"])) for n, g in both.groupby("node")}
        return w
    return _cached(("caiso_prices", in_dir), build)


def price_nodes(in_dir, zones=False, hubs=True):
    """[(region, words, grid, node's hourly rows, the tables its rows come from)] for ERCOT and CAISO."""
    out = []
    e = ercot_prices(in_dir)
    for node, g in e.groupby("node"):
        if node in ERCOT_HUBS and hubs:
            out.append((f"ercot_{node}", f"ERCOT, {ERCOT_HUBS[node]} ({node})", "ercot", g, ["ercot_all_hub_prices_history"]))
        elif node.startswith("LZ_") and zones:
            out.append((f"ercot_{node}", f"ERCOT, load zone {node}", "ercot", g, ["ercot_zone_prices_history"]))
    c = caiso_prices(in_dir)
    for node, g in c.groupby("node"):
        if hubs or zones:
            out.append((f"caiso_{CAISO_HUBS[node]}", f"CAISO, {CAISO_HUBS[node]} trading hub", "caiso", g, list(c.attrs["tables"][node])))
    return out


# ---------------------------------------------------------------------------------------------------------------------
# the thirteen families
# ---------------------------------------------------------------------------------------------------------------------
def solar_capture_rate(in_dir=None):
    """Solar cannibalization: the year's solar capture rate (what a solar plant earned per MWh as a percent of the
    time-weighted average price), with solar's share of the grid's generation beside it."""
    V = ["solar_revenue_per_mw", "solar_energy_per_mw", "solar_flat_price", "solar_hours"]
    m = series("merchant_revenue_monthly", in_dir, variables=V)
    mix = series("generation_mix_hourly_profile", in_dir, variables=["solar_mwh", "net_generation_mwh"])
    rows, tables = [], {}
    for entity, g in m.groupby("entity"):
        grid, node = entity.split(":", 1)
        w = g.pivot_table(index="ts", columns="variable", values="value").dropna(subset=V)
        w["year"] = w.index.year
        x = mix[mix["entity"] == f"iso:{grid}"].pivot_table(index="ts", columns="variable", values="value")
        x["year"] = x.index.year
        share = {int(y): float(s["solar_mwh"].sum() / s["net_generation_mwh"].sum() * 100) for y, s in x.groupby("year") if s["net_generation_mwh"].sum() > 0} if len(x) else {}
        for y, s in w.groupby("year"):
            hours, energy = s["solar_hours"].sum(), s["solar_energy_per_mw"].sum()
            flat = (s["solar_flat_price"] * s["solar_hours"]).sum() / hours if hours else float("nan")
            rate = (s["solar_revenue_per_mw"].sum() / energy) / flat * 100 if energy and flat else float("nan")
            rows.append(_row(grid, f"{GRID.get(grid, grid)} ({node})", y, rate, hours, share.get(int(y))))
        tables[grid] = ["merchant_revenue_monthly", "generation_mix_hourly_profile"]
    return {"rows": rows, "tables": tables}


def evening_ramp(in_dir=None):
    """The evening ramp's growth: the median day's steepest hourly rise of net load in the evening, MW per hour."""
    d = series("grid_stress_yearly", in_dir, variables=["evening_ramp_median_mw_per_h", "hours_held"], entity_prefix="iso:")
    rows, tables = [], {}
    for entity, g in d.groupby("entity"):
        grid = entity.split(":", 1)[1]
        w = g.pivot_table(index="ts", columns="variable", values="value").dropna()
        for ts, r in w.iterrows():
            rows.append(_row(grid, GRID.get(grid, grid), ts.year, r["evening_ramp_median_mw_per_h"], r["hours_held"]))
        tables[grid] = ["grid_stress_yearly"]
    return {"rows": rows, "tables": tables}


def _evening_share(hours, tz):
    """{year: (percent of the year's discharge that fell in the evening, hours held)} from hourly net battery MW."""
    local = hours["ts"].dt.tz_convert(tz)
    d = pd.DataFrame({"year": local.dt.year.values, "lhour": local.dt.hour.values, "out": hours["value"].clip(lower=0).values})
    out = {}
    for y, s in d.groupby("year"):
        total = s["out"].sum()
        out[int(y)] = (float(s.loc[s["lhour"].between(*EVENING), "out"].sum() / total * 100) if total > 0 else float("nan"), len(s))
    return out


def battery_evening_discharge(in_dir=None):
    """Battery discharge against the evening price peak: the percent of the year's battery discharge delivered from
    5 PM to 10 PM local, the hours finding 10 calls the evening."""
    rows, tables = [], {}
    c = pd.concat([series("caiso_fuel_supply_history", in_dir, variables=["batteries_mw"], entities=["caiso:ISO"]),
                   series("caiso_fuel_supply", in_dir, variables=["batteries_mw"], entities=["caiso:ISO"])]).drop_duplicates("ts_utc")
    for y, (v, n) in _evening_share(c, TZ["caiso"]).items():
        rows.append(_row("caiso", "CAISO", y, v, n))
    tables["caiso"] = ["caiso_fuel_supply_history", "caiso_fuel_supply"]
    try:
        e = series("eia930_all_storage", in_dir, variables=["net_generation_battery_mw"], entities=["eia930:ERCO"])
        for y, (v, n) in _evening_share(e, TZ["ercot"]).items():
            rows.append(_row("ercot", "ERCOT", y, v, n))
        tables["ercot"] = ["eia930_all_storage"]
    except NoData:
        pass
    return {"rows": rows, "tables": tables}


def implied_heat_rate(in_dir=None):
    """Gas pass-through: the year's median daily implied heat rate, the day's mean real-time price over Henry Hub."""
    gas = series("eia_fuel_spot_prices", in_dir, variables=["spot_price"], entities=["eia:henry_hub"])
    hh = {t.strftime("%Y-%m-%d"): v for t, v in zip(gas["ts"], gas["value"]) if v > 0}
    rows, tables = [], {}
    for region, words, grid, g, tbl in price_nodes(in_dir):
        day = g.dropna(subset=["rt"]).groupby("day").agg(rt=("rt", "mean"), hours=("rt", "size"), year=("year", "first"))
        day = day[day["hours"] >= 20]
        day["hh"] = day.index.map(hh)
        day = day.dropna(subset=["hh"])
        for y, s in day.groupby("year"):
            rows.append(_row(region, words, y, float(np.median(s["rt"] / s["hh"])), len(s)))
        tables[region] = tbl + ["eia_fuel_spot_prices"]
    return {"rows": rows, "tables": tables}


def negative_hours_zones(in_dir=None):
    """Negative-price hours by zone and trading hub: the percent of the year's hours whose mean real-time price was
    below zero. ERCOT's hubs are finding 6's pattern; here its load zones and CAISO's trading hubs."""
    rows, tables = [], {}
    for region, words, grid, g, tbl in price_nodes(in_dir, zones=True, hubs=False):
        g = g.dropna(subset=["rt"])
        for y, s in g.groupby("year"):
            rows.append(_row(region, words, y, float((s["rt"] < 0).mean() * 100), len(s)))
        tables[region] = tbl
    return {"rows": rows, "tables": tables}


def da_rt_spread(in_dir=None):
    """The day-ahead against real-time spread by hour: the median hour's day-ahead price minus its real-time price,
    for each part of the local day."""
    rows, tables = [], {}
    for region, words, grid, g, tbl in price_nodes(in_dir):
        g = g.dropna(subset=["rt", "da"])
        for part, part_words, h0, h1 in DAY_PARTS:
            p = g[g["lhour"].between(h0, h1)]
            key = f"{region}_{part}"
            for y, s in p.groupby("year"):
                rows.append(_row(key, f"{words}, {part_words}", y, float(np.median(s["da"] - s["rt"])), len(s)))
            tables[key] = tbl
    return {"rows": rows, "tables": tables}


def scarcity_hours(in_dir=None):
    """Scarcity hours against demand: the percent of the year's hours with ERCOT's on-line reserve price adder
    (RTORPA, the ORDC adder) above zero, with the year's mean demand beside it. The adder ends on 4 December 2025;
    the reliability deployment adder that follows is another thing and is not joined to it."""
    a = series("ercot_rtm_price_adders", in_dir, variables=["rtorpa_mean"], entities=["ercot:system"])
    a["year"] = a["ts"].dt.tz_convert(TZ["ercot"]).dt.year
    load = series("ercot_zone_load_hourly", in_dir, variables=["load"], entities=["ercot:system"])
    load["year"] = load["ts"].dt.tz_convert(TZ["ercot"]).dt.year
    demand = {int(y): float(s["value"].mean()) for y, s in load.groupby("year") if len(s) >= 8000}
    rows = [_row("ercot", "ERCOT", y, float((s["value"] > 0).mean() * 100), len(s), demand.get(int(y))) for y, s in a.groupby("year")]
    return {"rows": rows, "tables": {"ercot": ["ercot_rtm_price_adders", "ercot_zone_load_hourly"]}}


def curtailment_share(in_dir=None):
    """Curtailment against storage build-out: the percent of the year's wind and solar output that was curtailed, with
    the grid's operating battery fleet at the year's end beside it."""
    c = series("iso_curtailment_monthly", in_dir, variables=["share_curtailed_mwh", "share_output_mwh", "share_hours_held"])
    b = series("storage_buildout_monthly", in_dir, variables=["battery_operating_mw"], entity_prefix="iso:")
    rows, tables = [], {}
    for entity, g in c.groupby("entity"):
        grid = entity.split(":", 1)[0]
        w = g.pivot_table(index="ts", columns="variable", values="value").dropna()
        w["year"] = w.index.year
        fleet = b[b["entity"] == f"iso:{grid}"].sort_values("ts")
        fleet = {int(y): float(s["value"].iloc[-1]) for y, s in fleet.groupby(fleet["ts"].dt.year) if s["ts"].iloc[-1].month == 12}
        for y, s in w.groupby("year"):
            cut, out = s["share_curtailed_mwh"].sum(), s["share_output_mwh"].sum()
            rows.append(_row(grid, GRID.get(grid, grid), y, float(cut / (cut + out) * 100) if cut + out > 0 else float("nan"), s["share_hours_held"].sum(), fleet.get(int(y))))
        tables[grid] = ["iso_curtailment_monthly", "storage_buildout_monthly"]
    return {"rows": rows, "tables": tables}


def _daily_demand(in_dir):
    def build():
        d = series("eia930_daily_demand", in_dir, variables=["demand_mwh"], entities=[f"eia930:{b}" for b in BA_GRID])
        d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"])
        d["ba"], d["year"] = d["entity"].str.split(":").str[1], d["ts"].dt.year
        # a day EIA's respondent reported at a third of, or three times, its year's median is a fault of the report
        med = d.groupby(["ba", "year"])["value"].transform("median")
        return d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
    return _cached(("daily_demand", in_dir), build)


def stress_day_imports(in_dir=None):
    """Interchange dependence on stress days: net imports as a percent of demand on the year's stress days, its
    5 percent of days with the highest demand. EIA's total interchange is positive for a net export."""
    d = _daily_demand(in_dir)
    t = series("eia930_daily_total_interchange", in_dir, variables=["total_interchange_mwh"], entity_prefix="eia930:").drop_duplicates(["entity", "ts_utc"])
    j = d.merge(t[["entity", "ts_utc", "value"]].rename(columns={"value": "ti"}), on=["entity", "ts_utc"])
    rows, tables = [], {}
    for (ba, y), s in j.groupby(["ba", "year"]):
        k = max(1, int(math.ceil(STRESS_SHARE * len(s))))
        top = s.nlargest(k, "value")
        rows.append(_row(ba_region(ba), ba_words(ba), y, float(-top["ti"].sum() / top["value"].sum() * 100), len(s)))
        tables[ba_region(ba)] = ["eia930_daily_demand", "eia930_daily_total_interchange"]
    return {"rows": rows, "tables": tables}


def demand_growth_weather_adjusted(in_dir=None):
    """Weather-adjusted demand growth by balancing authority: the year's energy above the 2019 to 2021 base that
    temperature does not explain, percent (eia930_demand_weather, the whole years)."""
    d = read_table("eia930_demand_weather", in_dir, usecols=["entity", "variable", "ts_utc", "value", "x_window", "x_used"],
                   keep=lambda c: (c["variable"] == "energy_unexplained_pct") & (c["x_window"] == "the year"))
    rows, tables = [], {}
    for _, r in d.iterrows():
        ba = r["entity"].split(":", 1)[1]
        if ba not in BA_GRID:
            continue
        region = ba_region(ba)
        place = DATACENTER_PLACES.get(region)
        rows.append(_row(region, ba_words(ba) + (f" (its datacenter markets: {place})" if place else ""), int(r["ts_utc"][:4]), float(r["value"]), float(r["x_used"])))
        tables[region] = ["eia930_demand_weather"]
    return {"rows": rows, "tables": tables}


def peak_hour_carbon(in_dir=None):
    """The carbon of peak hours: how far the carbon intensity of the electricity used from 5 PM to 10 PM local stands
    above the year's all-hours mean, percent."""
    d = series("carbon_intensity_hourly", in_dir, variables=["intensity_demand"], entities=[f"eia930:{b}" for b in BA_GRID])
    rows, tables = [], {}
    for entity, g in d.groupby("entity"):
        grid = BA_GRID[entity.split(":", 1)[1]]
        local = g["ts"].dt.tz_convert(TZ[grid])
        w = pd.DataFrame({"year": local.dt.year.values, "lhour": local.dt.hour.values, "v": g["value"].values})
        for y, s in w.groupby("year"):
            allm = s["v"].mean()
            rows.append(_row(grid, GRID[grid], y, float((s.loc[s["lhour"].between(*EVENING), "v"].mean() / allm - 1) * 100) if allm > 0 else float("nan"), len(s)))
        tables[grid] = ["carbon_intensity_hourly"]
    return {"rows": rows, "tables": tables}


def _night_discount(g):
    """{year: the median night hour's real-time price minus the median hour's, USD per MWh} for one node's hours."""
    g = g.dropna(subset=["rt"])
    return {int(y): float(np.median(s.loc[s["lhour"].between(*NIGHT), "rt"]) - np.median(s["rt"])) for y, s in g.groupby("year") if len(s) >= 8000}


def wind_night_share(in_dir=None):
    """Wind's night share and its price effect: wind's percent of the grid's generation from midnight to 6 AM local,
    with the night's price against the whole day's beside it where the grid's prices are held."""
    hours = [f"h{h:02d}" for h in range(NIGHT[0], NIGHT[1] + 1)]
    V = [f"avg_wind_mw_{h}" for h in hours] + [f"avg_net_generation_mw_{h}" for h in hours] + ["days_held"]
    d = series("generation_mix_hourly_profile", in_dir, variables=V, entity_prefix="iso:")
    rows, tables = [], {}
    price = {}
    try:
        e = ercot_prices(in_dir)
        price["ercot"] = (_night_discount(e[e["node"] == "HB_HUBAVG"]), ["ercot_all_hub_prices_history"])
    except NoData:
        pass
    for entity, g in d.groupby("entity"):
        grid = entity.split(":", 1)[1]
        w = g.pivot_table(index="ts", columns="variable", values="value").dropna()
        w["wind"] = w[[f"avg_wind_mw_{h}" for h in hours]].sum(axis=1) * w["days_held"]
        w["gen"] = w[[f"avg_net_generation_mw_{h}" for h in hours]].sum(axis=1) * w["days_held"]
        w["year"] = w.index.year
        ctx, ctx_tables = price.get(grid, ({}, []))
        for y, s in w.groupby("year"):
            rows.append(_row(grid, GRID.get(grid, grid), y, float(s["wind"].sum() / s["gen"].sum() * 100) if s["gen"].sum() > 0 else float("nan"),
                             s["days_held"].sum(), ctx.get(int(y))))
        tables[grid] = ["generation_mix_hourly_profile"] + ctx_tables
    return {"rows": rows, "tables": tables}


def record_days(in_dir=None):
    """Record-setting days: the days of the year whose demand stood above the highest daily demand of every earlier
    year held. The first year held has no earlier year and is not counted."""
    d = _daily_demand(in_dir)
    rows, tables = [], {}
    for ba, g in d.groupby("ba"):
        best = None
        for y, s in sorted(g.groupby("year"), key=lambda kv: kv[0]):
            if best is not None:
                rows.append(_row(ba_region(ba), ba_words(ba), y, float((s["value"] > best).sum()), len(s)))
            best = max(best or 0.0, float(s["value"].max()))
        tables[ba_region(ba)] = ["eia930_daily_demand"]
    return {"rows": rows, "tables": tables}


FAMILIES = {f.__name__: f for f in (solar_capture_rate, evening_ramp, battery_evening_discharge, implied_heat_rate, negative_hours_zones, da_rt_spread,
                                    scarcity_hours, curtailment_share, stress_day_imports, demand_growth_weather_adjusted, peak_hour_carbon,
                                    wind_night_share, record_days)}


def run(name, in_dir=None):
    if name not in FAMILIES:
        raise ValueError(f"no measure named {name!r}; the measures are {', '.join(FAMILIES)}")
    return FAMILIES[name](in_dir)


if __name__ == "__main__":
    import sys
    import time
    for name in (sys.argv[1:] or list(FAMILIES)):
        t0 = time.time()
        got = run(name)
        regions = sorted({r["region"] for r in got["rows"]})
        print(f"{name}: {len(got['rows'])} rows, {len(regions)} regions, {round(time.time() - t0, 1)} s")
        for region in regions[:40]:
            s = sorted((r for r in got["rows"] if r["region"] == region), key=lambda r: r["year"])
            print(f"  {region} [{s[0]['words']}] " + " ".join(f"{r['year']}:{'' if r['value'] is None else round(r['value'], 2)}({int(r['n'])})" for r in s))
