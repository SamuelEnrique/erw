#!/usr/bin/env python3
"""The early years: why the battery model earns so much in ERCOT before 2024 (session 101). Analysis only: it writes no
table of the live set and changes no strategy of the page.

Energy Research Warehouse (ERW). docs/methods/battery_early_years.md.

    python warehouse/analysis/battery_early_years.py

The page's model (warehouse/derived/battery_stack.py) is one price-taking battery. For ERCOT it shows USD 244 to 530 per
kW a year from 2018 to 2023 (and 3,431 in 2021) at four hours with perfect foresight, and far less from 2024. The
warehouse holds no measure of what real batteries earned in those years, so the gap to them cannot be measured here.
What can be measured is how much of the model's own figure rests on each thing a battery of those years did not have.
This script takes the page's figure down a ladder, one assumption at a time, each rung solved with the page's own
program (battery_stack.solve_day) on the page's own prices:

    1  page_foresight_4h     the page: perfect foresight of real-time prices, four hours
    2  page_dayahead_4h      the page's other strategy: energy at day-ahead prices, no knowledge of real time
    3  dayahead_fleet        the same with the duration the fleet of that year had: ERCOT's operating battery MWh over
                             its MW (EIA-860M via storage_buildout_monthly), the mean of the year's months
    4  dayahead_fleet_no_regulation   and no regulation sold: ERCOT buys a few hundred MW of regulation, and the
                             quantities of those years are not held, so the cap cannot be computed; selling none is the
                             far end of what a cap could do
    5  energy_only_fleet     and no reserve at all: day-ahead energy arbitrage alone, at the fleet's duration

and, beside the ladder, for each year: the share of the page's figure that is reserve capacity payments, by product;
the share earned on the year's ten best days; and February 2021's storm week (13 to 19 February) alone.

Output: warehouse/output/analysis_internal/battery_early_years_ercot_daily.csv and _yearly.csv (not in git), USD per MW
of rated power; and the yearly table on the terminal. Never filled: a day without every hour of a price is left out of
every rung, so the rungs of a year cover the same days.
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_early_years_ercot_{}.csv")
STORM = ("2021-02-13", "2021-02-19")
REGULATION = ("regup", "regdn")


def fleet_duration():
    """{year: (hours, MW at the year's end)}: ERCOT's operating battery MWh over MW, the mean of the year's months held."""
    f = bs.pb.read_table("storage_buildout_monthly")
    f = f[f["entity"] == "iso:ercot"]
    mw = f[f["variable"] == "battery_operating_mw"].set_index("ts")["value"]
    mwh = f[f["variable"] == "battery_operating_mwh"].set_index("ts")["value"]
    d = pd.DataFrame({"mw": mw, "mwh": mwh}).dropna()
    d = d[d["mw"] > 0]
    d["h"] = d["mwh"] / d["mw"]
    d["year"] = pd.DatetimeIndex(d.index).year
    return {int(y): (round(float(g["h"].mean()), 2), round(float(g["mw"].iloc[-1]), 1), len(g)) for y, g in d.groupby("year")}


def page_table(duration, strategy):
    """{year: USD per MW}: the page's own table (battery_stack_monthly), ERCOT, the year's months added."""
    t = bs.pb.read_table("battery_stack_monthly")
    t = t[(t["entity"] == "ercot:HB_HUBAVG") & (t["variable"] == f"{strategy}_{duration}h_revenue_total_usd_per_mw")]
    return t.groupby(pd.DatetimeIndex(t["ts"]).year)["value"].sum().to_dict()


def run(log=print):
    m = bs.MARKETS["ercot"]
    tz = bs.pb.TZ["ercot"]
    energy = {mk: bs.energy_prices("ercot", mk, log)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices(m["as_table"], m["products"])
    fd = fleet_duration()
    log(f"fleet duration by year (hours, MW at the year's end, months held): {fd}")
    first = pd.Timestamp(m["start"])
    last = min(min(s.index.max() for s in reserve.values()), energy["rtm"].index.max(), energy["dam"].index.max()).tz_convert(tz).tz_localize(None).normalize()
    rows, left = [], 0
    for ts in pd.date_range(first, last, freq="D"):
        day = ts.strftime("%Y-%m-%d")
        year = ts.year
        if year not in fd:
            continue
        hrs = bs.day_hours(day, tz)
        prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
        pr = [reserve[p["key"]].reindex(hrs) for p in prods]
        rt, da = energy["rtm"].reindex(hrs), energy["dam"].reindex(hrs)
        if any(s.isna().any() for s in pr) or rt.isna().any() or da.isna().any():
            left += 1
            continue
        prices = [s.values for s in pr]
        spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
        dur = fd[year][0]
        ones = [np.ones(len(hrs)) for _ in prods]
        no_reg = [np.zeros(len(hrs)) if p["key"] in REGULATION else np.ones(len(hrs)) for p in prods]
        none = [np.zeros(len(hrs)) for _ in prods]
        sols = {
            "page_foresight_4h": bs.solve_day(rt.values, prices, spec, 4),
            "page_dayahead_4h": bs.solve_day(da.values, prices, spec, 4),
            "dayahead_fleet": bs.solve_day(da.values, prices, spec, dur, caps=ones),
            "dayahead_fleet_no_regulation": bs.solve_day(da.values, prices, spec, dur, caps=no_reg),
            "energy_only_fleet": bs.solve_day(da.values, prices, spec, dur, caps=none),
        }
        r = dict(day=day, year=year, fleet_hours=dur)
        for name, sol in sols.items():
            bad = bs.check_day(sol, spec, 4 if name.startswith("page") else dur)
            if bad:
                raise RuntimeError(f"{day} {name}: {bad[0]}")
            r[f"{name}_total"] = round(sol["total"], 4)
            r[f"{name}_energy"] = round(sol["energy"], 4)
            if name == "page_foresight_4h":
                for p, v in zip(prods, sol["reserve"]):
                    r[f"page_{p['key']}"] = round(v, 4)
        rows.append(r)
    d = pd.DataFrame(rows).fillna(0.0)
    os.makedirs(os.path.dirname(OUT.format("daily")), exist_ok=True)
    head = ("# ERW analysis, internal, for review (session 101): the early years, ERCOT HB_HUBAVG, USD per MW of rated power (warehouse/analysis/battery_early_years.py). "
            "The page's figure taken down a ladder, one assumption at a time; fleet_hours is ERCOT's operating battery MWh over MW of that year (EIA-860M). "
            f"Days left out of every rung (a price not held): {left}\n")
    with open(OUT.format("daily"), "w", encoding="utf-8", newline="") as f:
        f.write(head)
        d.to_csv(f, index=False, lineterminator="\n")
    rungs = ["page_foresight_4h", "page_dayahead_4h", "dayahead_fleet", "dayahead_fleet_no_regulation", "energy_only_fleet"]
    out = []
    for year, g in d.groupby("year"):
        page = g["page_foresight_4h_total"]
        r = dict(year=int(year), days=len(g), fleet_hours=fd[year][0], fleet_mw_year_end=fd[year][1])
        for name in rungs:
            r[name] = round(float(g[f"{name}_total"].sum()), 1)
        for k in ("regup", "regdn", "rrs", "ecrs", "nspin"):
            r[f"page_{k}"] = round(float(g[f"page_{k}"].sum()), 1) if f"page_{k}" in g else 0.0
        r["page_energy"] = round(float(g["page_foresight_4h_energy"].sum()), 1)
        r["page_top10_days"] = round(float(page.nlargest(10).sum()), 1)
        storm = g[(g["day"] >= STORM[0]) & (g["day"] <= STORM[1])]
        r["page_storm_week"] = round(float(storm["page_foresight_4h_total"].sum()), 1)
        r["dayahead_fleet_storm_week"] = round(float(storm["dayahead_fleet_total"].sum()), 1)
        out.append(r)
    y = pd.DataFrame(out)
    # beside the ladder: the page's two-hour battery, its shortest, from the page's own table; and a check that the
    # first rung is the page's table to the cent of a kW
    for name, (dur, strat) in {"table_foresight_4h": (4, "foresight"), "table_foresight_2h": (2, "foresight"), "table_dayahead_2h": (2, "dayahead")}.items():
        tab = page_table(dur, strat)
        y[name] = [round(float(tab.get(int(v), float("nan"))), 1) for v in y["year"]]
    off = (y["table_foresight_4h"] - y["page_foresight_4h"]).abs().max()
    if off > 1.0:
        raise RuntimeError(f"the first rung is not the page's table: off by {off} USD per MW in a year")
    y["fleet_over_page_pct"] = (100 * y["dayahead_fleet"] / y["page_foresight_4h"]).round(1)
    y["reserve_share_of_page_pct"] = (100 * (y["page_foresight_4h"] - y["page_energy"]) / y["page_foresight_4h"]).round(1)
    with open(OUT.format("yearly"), "w", encoding="utf-8", newline="") as f:
        f.write(head)
        y.to_csv(f, index=False, lineterminator="\n")
    log(f"{len(d)} days, {d['day'].min()} to {d['day'].max()}; left out {left} -> {os.path.relpath(OUT.format('yearly'), ROOT)}")
    k = y.copy()
    for c in rungs + ["page_energy", "page_top10_days", "page_storm_week", "dayahead_fleet_storm_week", "page_regup", "page_regdn", "page_rrs", "page_ecrs", "page_nspin",
                      "table_foresight_4h", "table_foresight_2h", "table_dayahead_2h"]:
        k[c] = (k[c] / 1000).round(1)  # USD per kW
    pd.set_option("display.width", 260)
    log(k.to_string(index=False))
    return d, y


if __name__ == "__main__":
    run()
    sys.exit(0)
