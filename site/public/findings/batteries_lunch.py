"""Finding: "Batteries ate their own lunch?" (session 170). ERCOT, 2019 to 2026.

How often and how far real-time prices spiked, measured like the thesis's peak premium (the 99.9th percentile against
the median, intervals in the top 1 percent, intervals at or above fixed thresholds), by month, set against ERCOT's
battery fleet in MW; then a regression of each monthly spike measure on battery GW, controlling for monthly mean load,
Henry Hub and month-of-year fixed effects, with HC1 standard errors. A before-and-after with controls: the words say
association, never cause.

Inputs: hub (HB_HUBAVG, the thesis's hub, or any ERCOT trading hub), first year (2019).
Tables: ercot_all_hub_prices_history (market ercot_rtm, 15-minute, 2015 to 2026-08), iso_rtm_hub_prices (the live
window after it), storage_buildout_monthly (iso:ercot battery_operating_mw), ercot_zone_load_hourly, eia_fuel_spot_prices.
"""

import os

import numpy as np
import pandas as pd

from findings_common import (METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, ols_hc1, pct,
                    read_table, to_utc)

NAME = "batteries_lunch"
TITLE = "BATTERIES ATE THEIR OWN LUNCH?"
KIND = "econometric"
HUBS = ["HB_HUBAVG", "HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON", "HB_BUSAVG"]
HUB_WORDS = {"HB_HUBAVG": "ERCOT hub average", "HB_NORTH": "ERCOT North Hub", "HB_SOUTH": "ERCOT South Hub",
             "HB_WEST": "ERCOT West Hub", "HB_HOUSTON": "ERCOT Houston Hub", "HB_BUSAVG": "ERCOT bus average"}
INPUTS = {
    "hub": {"label": "Hub", "default": "HB_HUBAVG", "choices": HUBS, "words": HUB_WORDS},
    "first_year": {"label": "First year", "default": 2019, "choices": [2019, 2020, 2021]},
}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "storage_buildout_monthly", "ercot_zone_load_hourly",
          "eia_fuel_spot_prices"]
TZ = "America/Chicago"
SCARCITY = 1000.0
HIGH = 250.0
CSV_NAME = "erw_2026_ercot_spikes_batteries.csv"


def prices(hub, first_year, in_dir):
    """Every real-time 15-minute interval of the hub from first_year (local), history then the live window, once each."""
    h = read_table("ercot_all_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node", "year"],
                   keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == hub) & (c["year"].astype(int) >= first_year - 1))
    live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                      keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == hub))
    d = pd.concat([h[["ts_utc", "value"]], live[["ts_utc", "value"]]], ignore_index=True)
    d = d.drop_duplicates("ts_utc")
    if d.empty:
        raise NoData(f"no real-time rows for {hub}")
    d["ts"] = to_utc(d["ts_utc"])
    d["value"] = d["value"].astype(float)
    loc = d["ts"].dt.tz_convert(TZ)
    d["year"] = loc.dt.year
    d["month"] = loc.dt.strftime("%Y-%m")
    d = d[d["year"] >= first_year].sort_values("ts")
    return d


def spike_measures(v, top1):
    """The thesis's spike measures for one period's intervals v (15 minutes each)."""
    med = pct(v, 50)
    p999 = pct(v, 99.9)
    return {
        "n_intervals": int(len(v)),
        "median_usd_mwh": med,
        "p999_usd_mwh": p999,
        "worst_interval_multiple": (p999 / med) if med > 0 else None,
        "hours_top1pct": float((v >= top1).sum()) / 4.0,
        "hours_ge_1000": float((v >= SCARCITY).sum()) / 4.0,
        "hours_ge_250": float((v >= HIGH).sum()) / 4.0,
    }


def fleet(in_dir):
    s = read_table("storage_buildout_monthly", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c["entity"] == "iso:ercot") & (c["variable"] == "battery_operating_mw"))
    if s.empty:
        raise NoData("storage_buildout_monthly has no iso:ercot battery_operating_mw rows")
    return {t[:7]: float(v) for t, v in zip(s["ts_utc"], s["value"])}


def load_monthly(in_dir):
    """ERCOT's monthly mean load in MW: the sum of the zones each hour (local month), then the mean of the hours."""
    L = read_table("ercot_zone_load_hourly", in_dir, usecols=["ts_utc", "value", "node"],
                   keep=lambda c: c["ts_utc"] >= "2018-12-31")
    if L.empty:
        raise NoData("ercot_zone_load_hourly has no rows from 2019")
    L["value"] = L["value"].astype(float)
    nodes = set(L["node"])
    if "ERCOT" in nodes:
        L = L[L["node"] == "ERCOT"]
        how = "the ERCOT total row"
    else:
        L = L.groupby("ts_utc", as_index=False)["value"].sum()
        how = f"the sum of {len(nodes)} zones each hour"
    ts = to_utc(L["ts_utc"]).dt.tz_convert(TZ)
    L = L.assign(month=ts.dt.strftime("%Y-%m"))
    return L.groupby("month")["value"].mean().to_dict(), how


def henry_hub_monthly(in_dir):
    g = read_table("eia_fuel_spot_prices", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c["entity"] == "eia:henry_hub") & (c["variable"] == "spot_price") & (c["ts_utc"] >= "2019-01-01"))
    if g.empty:
        raise NoData("eia_fuel_spot_prices has no Henry Hub rows from 2019")
    g["value"] = g["value"].astype(float)
    g["month"] = g["ts_utc"].str[:7]
    return g.groupby("month")["value"].mean().to_dict(), g.groupby("month")["value"].size().to_dict()


def compute(params, in_dir=None):
    hub = params.get("hub", "HB_HUBAVG")
    first_year = int(params.get("first_year", 2019))
    if hub not in HUBS:
        raise ValueError(f"hub {hub!r} is not an ERCOT trading hub")
    d = prices(hub, first_year, in_dir)
    top1 = pct(d["value"].to_numpy(), 99)
    mw = fleet(in_dir)
    load, load_how = load_monthly(in_dir)
    hh, hh_days = henry_hub_monthly(in_dir)
    rows = []
    for month, g in d.groupby("month"):
        m = spike_measures(g["value"].to_numpy(), top1)
        rows.append({"period": month, "kind": "month", "hub": hub, **m,
                     "battery_mw": mw.get(month), "load_mean_mw": load.get(month), "henry_hub_usd_mmbtu": hh.get(month)})
    for year, g in d.groupby("year"):
        m = spike_measures(g["value"].to_numpy(), top1)
        rows.append({"period": str(year), "kind": "year", "hub": hub, **m,
                     "battery_mw": mw.get(f"{year}-12") if f"{year}-12" in mw else None, "load_mean_mw": None, "henry_hub_usd_mmbtu": None})
    last = d["ts"].max()
    meta = {"hub": hub, "first_year": first_year, "top1_threshold_usd_mwh": top1, "last_interval_utc": last.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_intervals_all": int(len(d)), "load_how": load_how, "fleet_last_month": max(mw), "henry_hub_days": sum(hh_days.values())}
    return rows, meta


def regression_rows(rows):
    """The months with every regressor held: a month without a fleet figure (after the latest EIA-860M) is left out."""
    R = [r for r in rows if r["kind"] == "month" and r["battery_mw"] is not None and r["load_mean_mw"] is not None
         and r["henry_hub_usd_mmbtu"] is not None and r["worst_interval_multiple"] is not None]
    return R


def fit(rows):
    """Each spike measure on battery GW, mean load in GW, Henry Hub and month-of-year fixed effects (HC1)."""
    R = regression_rows(rows)
    X, names = [], ["const", "battery_gw", "load_gw", "henry_hub"] + [f"m{m:02d}" for m in range(2, 13)]
    for r in R:
        mo = int(r["period"][5:7])
        X.append([1.0, r["battery_mw"] / 1000.0, r["load_mean_mw"] / 1000.0, r["henry_hub_usd_mmbtu"]] + [1.0 if mo == m else 0.0 for m in range(2, 13)])
    out = {}
    for y_name, label in (("worst_interval_multiple", "worst-interval multiple (P99.9 over the median)"),
                          ("hours_ge_1000", "hours at or above USD 1,000/MWh"),
                          ("hours_top1pct", "hours in the sample's top 1 percent")):
        y = [r[y_name] for r in R]
        f = ols_hc1(y, X, names)
        out[y_name] = {"label": label, **f["coef"]["battery_gw"], "n": f["n"], "r2": f["r2"], "se_kind": f["se_kind"],
                       "load_gw": f["coef"]["load_gw"], "henry_hub": f["coef"]["henry_hub"]}
    out["sample"] = {"n": len(R), "first": R[0]["period"], "last": R[-1]["period"]}
    return out


def numbers_from_rows(rows, meta=None):
    """Every number on the card, from the data rows alone (the test's proof)."""
    years = {r["period"]: r for r in rows if r["kind"] == "year"}
    months = [r for r in rows if r["kind"] == "month"]
    ys = sorted(years)
    first, last_full = ys[0], max(y for y in ys if y < ys[-1]) if len(ys) > 1 else ys[0]
    fl = [r for r in months if r["battery_mw"] is not None]
    f = fit(rows)
    n = {
        "first_year": first, "last_full_year": last_full,
        "multiple_first": years[first]["worst_interval_multiple"], "multiple_last": years[last_full]["worst_interval_multiple"],
        "hours1000_first": years[first]["hours_ge_1000"], "hours1000_last": years[last_full]["hours_ge_1000"],
        "hours_top1_first": years[first]["hours_top1pct"], "hours_top1_last": years[last_full]["hours_top1pct"],
        "p999_first": years[first]["p999_usd_mwh"], "p999_last": years[last_full]["p999_usd_mwh"],
        "median_first": years[first]["median_usd_mwh"], "median_last": years[last_full]["median_usd_mwh"],
        "fleet_first_month": fl[0]["period"], "fleet_first_mw": fl[0]["battery_mw"],
        "fleet_last_month": fl[-1]["period"], "fleet_last_mw": fl[-1]["battery_mw"],
        "peak_multiple_month": max(months, key=lambda r: r["worst_interval_multiple"] or 0)["period"],
        "peak_multiple": max(r["worst_interval_multiple"] or 0 for r in months),
        "reg_n": f["sample"]["n"], "reg_first": f["sample"]["first"], "reg_last": f["sample"]["last"],
        "reg_multiple_coef": f["worst_interval_multiple"]["coef"], "reg_multiple_se": f["worst_interval_multiple"]["se"],
        "reg_multiple_p": f["worst_interval_multiple"]["p"], "reg_multiple_r2": f["worst_interval_multiple"]["r2"],
        "reg_hours1000_coef": f["hours_ge_1000"]["coef"], "reg_hours1000_se": f["hours_ge_1000"]["se"], "reg_hours1000_p": f["hours_ge_1000"]["p"],
        "reg_top1_coef": f["hours_top1pct"]["coef"], "reg_top1_se": f["hours_top1pct"]["se"], "reg_top1_p": f["hours_top1pct"]["p"],
        "n_months": len(months), "n_intervals": sum(r["n_intervals"] for r in months),
    }
    return n, f


def verdict(n):
    """The subtitle and the causal sentence, chosen by the fit: a flat result is reported flat."""
    c, p = n["reg_multiple_coef"], n["reg_multiple_p"]
    pw = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
    if p < 0.05 and c < 0:
        sub = "Spikes shrank as the fleet grew, and the regression agrees, with the usual caveat"
        caus = ("With load, Henry Hub and the month of the year held fixed, each added GW of batteries goes with a multiple "
                f"{fmt(abs(c), 2)} lower (standard error {fmt(n['reg_multiple_se'], 2)}, {pw}). That is an association in a before-and-after "
                "with controls, not a cause: the same years brought the 2021 winter storm, a new offer cap, more solar and a gas price "
                "that doubled and fell back.")
    elif p < 0.05 and c > 0:
        sub = "Spikes did not shrink with the fleet: the regression points the other way"
        caus = (f"With the controls in, each added GW of batteries goes with a multiple {fmt(c, 2)} higher (standard error "
                f"{fmt(n['reg_multiple_se'], 2)}, {pw}), which no one claims is a cause: a before-and-after with controls cannot separate "
                "the fleet from the years it arrived in.")
    else:
        sub = "The spikes shrank, but the regression cannot pin it on batteries"
        caus = (f"With load, Henry Hub and the month of the year held fixed, the battery coefficient on the multiple is {fmt(c, 2)} per GW "
                f"with a standard error of {fmt(n['reg_multiple_se'], 2)} ({pw}): flat. A before-and-after with controls, "
                "over months that also brought the 2021 winter storm and a gas price that doubled and fell back, cannot say more.")
    return sub, caus


def chart(rows, hub):
    months = [r for r in rows if r["kind"] == "month"]
    x = [r["period"] for r in months]
    return {
        "kind": "line_with_fleet", "x": x, "x_label": "Month (America/Chicago)",
        "series": [
            {"name": "Worst-interval multiple (P99.9 / median)", "axis": "left", "type": "line", "unit": "x",
             "values": [r["worst_interval_multiple"] for r in months]},
            {"name": "Hours at or above USD 1,000/MWh", "axis": "left_hours", "type": "bar", "unit": "hours",
             "values": [r["hours_ge_1000"] for r in months]},
            {"name": "ERCOT battery fleet (MW, operating)", "axis": "right", "type": "line", "unit": "MW",
             "values": [r["battery_mw"] for r in months]},
        ],
        "y_left_label": "multiple (x)", "y_right_label": "battery MW",
    }


def card(rows, params, meta):
    hub = meta["hub"]
    n, f = numbers_from_rows(rows, meta)
    sub, caus = verdict(n)
    y0, y1 = n["first_year"], n["last_full_year"]
    why = (f"ERCOT's operating battery fleet went from {fmt(n['fleet_first_mw'], 0)} MW in {n['fleet_first_month']} to "
           f"{fmt(n['fleet_last_mw'], 0)} MW in {n['fleet_last_month']} (EIA-860M). Over the same years the {HUB_WORDS[hub]}'s "
           f"worst-interval multiple fell from {fmt(n['multiple_first'], 1)}x in {y0} to {fmt(n['multiple_last'], 1)}x in {y1}: the "
           f"99.9th percentile went from {fmt(n['p999_first'], 0)} to {fmt(n['p999_last'], 0)} USD/MWh while the median went from "
           f"{fmt(n['median_first'], 2)} to {fmt(n['median_last'], 2)}. Hours at or above USD 1,000 went from {fmt(n['hours1000_first'], 0)} "
           f"in {y0} to {fmt(n['hours1000_last'], 0)} in {y1}; the worst month was {n['peak_multiple_month']} at {fmt(n['peak_multiple'], 0)}x. "
           + caus)
    foot = (f"Data: ERCOT real-time settlement point prices at {hub}, 15-minute intervals, {y0}-01 to {meta['last_interval_utc'][:10]} "
            f"({fmt(n['n_intervals'], 0)} intervals in {n['n_months']} local months, America/Chicago; ERW tables ercot_all_hub_prices_history and "
            f"iso_rtm_hub_prices from ERCOT NP6-785-ER and NP6-905-CD). Per month and per year: the median and the 99.9th percentile "
            f"(numpy linear percentiles, no cap or exclusion), their ratio (the worst-interval multiple), hours at or above USD 1,000 and "
            f"USD 250 (intervals over four), and hours at or above the 99th percentile of every interval in the sample "
            f"({fmt(meta['top1_threshold_usd_mwh'], 2)} USD/MWh, one fixed threshold). Fleet: storage_buildout_monthly, iso:ercot "
            f"battery_operating_mw (EIA-860M, operating units, month of the data). Load: ercot_zone_load_hourly, {meta['load_how']}, "
            f"monthly mean. Gas: eia_fuel_spot_prices Henry Hub daily spot, monthly mean. Regression: OLS of each monthly spike measure on "
            f"battery GW, mean load in GW, Henry Hub in USD/MMBtu and eleven month-of-year dummies, {n['reg_n']} months "
            f"{n['reg_first']} to {n['reg_last']} (months after the latest fleet figure are left out), HC1 standard errors, p from "
            f"Student's t. No instrument, no event window: an association.")
    table = [{"measure": f[k]["label"], "coef_per_gw": f[k]["coef"], "se": f[k]["se"], "p": f[k]["p"], "n": f[k]["n"], "r2": f[k]["r2"]}
             for k in ("worst_interval_multiple", "hours_ge_1000", "hours_top1pct")]
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub, "params": {"hub": hub, "first_year": meta["first_year"]},
        "inputs_words": {"hub": HUB_WORDS[hub], "first_year": str(meta["first_year"])},
        "chart": chart(rows, hub),
        "callouts": [
            callout("Worst-interval multiple", y0, f"{fmt(n['multiple_first'], 1)}x", y1, f"{fmt(n['multiple_last'], 1)}x"),
            callout("Hours at or above USD 1,000/MWh", y0, fmt(n["hours1000_first"], 0), y1, fmt(n["hours1000_last"], 0), "hours"),
            callout("Battery fleet", n["fleet_first_month"], f"{fmt(n['fleet_first_mw'], 0)} MW", n["fleet_last_month"], f"{fmt(n['fleet_last_mw'], 0)} MW"),
        ],
        "why": why, "footnote": foot, "numbers": n,
        "effect_table": {"columns": ["measure", "coef_per_gw", "se", "p", "n", "r2"], "rows": table,
                         "in_words": caus},
        "source_line": "Source: ERCOT (NP6-785-ER, NP6-905-CD), EIA-860M, EIA Henry Hub spot; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per local month and one per local year (kind), the thesis's spike measures, the fleet, the load and the gas price",
                       "Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    hub = params.get("hub", "HB_HUBAVG")
    V = ["n_intervals", "median_usd_mwh", "p999_usd_mwh", "worst_interval_multiple", "hours_top1pct", "hours_ge_1000", "hours_ge_250",
         "battery_mw", "load_mean_mw", "henry_hub_usd_mmbtu"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE} ({hub}). Reproduces the card's regression from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        'keep if kind == "month"',
        *do_destring(V),
        *do_sentinels(V),
        "gen battery_gw = battery_mw / 1000",
        "gen load_gw = load_mean_mw / 1000",
        "gen month_of_year = real(substr(period, 6, 2))",
        "drop if missing(battery_gw) | missing(load_gw) | missing(henry_hub_usd_mmbtu) | missing(worst_interval_multiple)",
        ["foreach y in worst_interval_multiple hours_ge_1000 hours_top1pct {",
         "    regress `y' battery_gw load_gw henry_hub_usd_mmbtu i.month_of_year, vce(robust)",
         "}"],
        "* vce(robust) is HC1, the card's standard errors",
    ])


SOURCE_PATH = os.path.abspath(__file__)
