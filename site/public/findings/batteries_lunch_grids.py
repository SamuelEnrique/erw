"""Finding: "Batteries ate their own lunch?" across every grid with public prices (session 182).

The ERCOT card of session 170 (batteries_lunch.py), asked of five grids on one timeline: ERCOT, CAISO, NYISO, ISO-NE and
SPP. MISO is paused while its terms are reviewed and PJM needs a licensed source: both are placeholders, never data, and
neither is requested. For each grid, by local month: the spike measures of the thesis's peak premium (the 99.9th
percentile against the median, hours in the grid's own top 1 percent, hours at or above USD 1,000 and USD 250 per MWh),
set against that grid's own battery fleet in MW from EIA-860M; then the ERCOT card's regression run grid by grid
(each monthly spike measure on battery GW, mean load in GW, Henry Hub and month-of-year fixed effects, HC1 errors).

A grid's panel starts where its real-time prices start in the warehouse: ERCOT and NYISO in 2019-01, CAISO, ISO-NE and
SPP in 2024-09. Nothing earlier is filled. NYISO's history is hourly (its own integrated hourly price), the other four
are 15-minute, so NYISO's multiple is not comparable in level with the others: an hour's mean hides a spike that four
quarter hours would show. The ERCOT panel is computed by the old card's own functions and equals it number for number.

Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT HB_HUBAVG), iso_hub_prices_history and
iso_rtm_hub_prices (CAISO TH_SP15_GEN-APND, ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB), iso_zone_prices_history (NYISO
N.Y.C., hourly), storage_buildout_monthly (each grid's battery_operating_mw), ercot_zone_load_hourly (ERCOT's load),
eia930_daily_demand (the other grids' demand), eia_fuel_spot_prices (Henry Hub).
"""

import os

import numpy as np
import pandas as pd

import batteries_lunch as ercot_card
from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, pct, read_table, to_utc

NAME = "batteries_lunch_grids"
TITLE = "BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS"
KIND = "econometric"
INPUTS = {"first_year": {"label": "First year", "default": 2019, "choices": [2019]}}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_hub_prices_history", "iso_zone_prices_history",
          "storage_buildout_monthly", "ercot_zone_load_hourly", "eia930_daily_demand", "eia_fuel_spot_prices"]
CSV_NAME = "erw_2026_grids_spikes_batteries.csv"
SUPERSEDES = "batteries_lunch"
ERCOT_HUB = "HB_HUBAVG"
GRIDS = [
    # grid, words, timezone, EIA balancing authority, table, market, node, node in words, minutes per interval
    {"grid": "ercot", "words": "ERCOT", "tz": "America/Chicago", "ba": "ERCO", "table": "ercot_all_hub_prices_history", "market": "ercot_rtm",
     "node": ERCOT_HUB, "node_words": "hub average", "minutes": 15},
    {"grid": "caiso", "words": "CAISO", "tz": "America/Los_Angeles", "ba": "CISO", "table": "iso_hub_prices_history", "market": "caiso_rtm",
     "node": "TH_SP15_GEN-APND", "node_words": "SP15", "minutes": 15},
    {"grid": "nyiso", "words": "NYISO", "tz": "America/New_York", "ba": "NYIS", "table": "iso_zone_prices_history", "market": "nyiso_rtm",
     "node": "N.Y.C.", "node_words": "New York City zone", "minutes": 60},
    {"grid": "isone", "words": "ISO-NE", "tz": "America/New_York", "ba": "ISNE", "table": "iso_hub_prices_history", "market": "isone_rtm",
     "node": ".H.INTERNAL_HUB", "node_words": "internal hub", "minutes": 15},
    {"grid": "spp", "words": "SPP", "tz": "America/Chicago", "ba": "SWPP", "table": "iso_hub_prices_history", "market": "spp_rtm",
     "node": "SPPNORTH_HUB", "node_words": "North Hub", "minutes": 15},
]
GRID = {g["grid"]: g for g in GRIDS}
PLACEHOLDERS = [{"grid": "miso", "words": "MISO", "text": "paused while terms are reviewed"},
                {"grid": "pjm", "words": "PJM", "text": "licensed source needed"}]
MEASURES = [("worst_interval_multiple", "Worst-interval multiple (P99.9 / median)", "x", 1),
            ("hours_ge_1000", "Hours at or above USD 1,000/MWh", "hours", 2),
            ("hours_top1pct", "Hours in the grid's own top 1 percent", "hours", 2),
            ("hours_ge_250", "Hours at or above USD 250/MWh", "hours", 2)]
REG = (("worst_interval_multiple", "multiple"), ("hours_ge_1000", "hours1000"), ("hours_top1pct", "top1"))
FULL_YEAR_SHARE = 0.90   # a year is full when it holds at least 90 percent of its intervals (ISO-NE's 2025 holds 90.7)


def grid_prices(g, first_year, in_dir):
    """Every real-time interval of the grid's node from first_year (local time), the history then the live window."""
    if g["grid"] == "ercot":
        d = ercot_card.prices(g["node"], first_year, in_dir)
        return d[["ts", "value", "year", "month"]]
    h = read_table(g["table"], in_dir, usecols=["ts_utc", "value", "market", "node"],
                   keep=lambda c: (c["market"] == g["market"]) & (c["node"] == g["node"]))
    parts = [h[["ts_utc", "value"]]]
    if g["minutes"] == 15:
        live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == g["market"]) & (c["node"] == g["node"]))
        parts.append(live[["ts_utc", "value"]])
    d = pd.concat(parts, ignore_index=True).drop_duplicates("ts_utc")
    if d.empty:
        raise NoData(f"no real-time rows for {g['grid']} {g['node']}")
    d["ts"] = to_utc(d["ts_utc"])
    d["value"] = d["value"].astype(float)
    loc = d["ts"].dt.tz_convert(g["tz"])
    d["year"] = loc.dt.year
    d["month"] = loc.dt.strftime("%Y-%m")
    return d[d["year"] >= first_year].sort_values("ts")[["ts", "value", "year", "month"]]


def spike_measures(v, top1, minutes):
    """The thesis's spike measures for one period's intervals; an interval is `minutes` long."""
    if minutes == 15:
        return ercot_card.spike_measures(v, top1)
    med, p999, per_hour = pct(v, 50), pct(v, 99.9), 60.0 / minutes
    return {"n_intervals": int(len(v)), "median_usd_mwh": med, "p999_usd_mwh": p999,
            "worst_interval_multiple": (p999 / med) if med > 0 else None,
            "hours_top1pct": float((v >= top1).sum()) / per_hour,
            "hours_ge_1000": float((v >= ercot_card.SCARCITY).sum()) / per_hour,
            "hours_ge_250": float((v >= ercot_card.HIGH).sum()) / per_hour}


def fleets(in_dir):
    """Each grid's operating battery MW by month (EIA-860M through storage_buildout_monthly)."""
    want = {f"iso:{g['grid']}" for g in GRIDS}
    s = read_table("storage_buildout_monthly", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: c["entity"].isin(want) & (c["variable"] == "battery_operating_mw"))
    out = {g["grid"]: {} for g in GRIDS}
    for e, t, v in zip(s["entity"], s["ts_utc"], s["value"]):
        out[e[4:]][t[:7]] = float(v)
    for k, v in out.items():
        if not v:
            raise NoData(f"storage_buildout_monthly has no iso:{k} battery_operating_mw rows")
    return out


def demand_monthly(in_dir):
    """Mean load in MW by month for the grids other than ERCOT: EIA-930's daily demand (MWh over EIA's Eastern day) over 24,
    averaged over the month's held days."""
    want = {f"eia930:{g['ba']}": g["grid"] for g in GRIDS if g["grid"] != "ercot"}
    d = read_table("eia930_daily_demand", in_dir, usecols=["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: c["entity"].isin(set(want)) & (c["variable"] == "demand_mwh"))
    if d.empty:
        raise NoData("eia930_daily_demand has no rows for the grids' balancing authorities")
    d["mw"] = d["value"].astype(float) / 24.0
    d["month"] = d["ts_utc"].str[:7]
    d["grid"] = d["entity"].map(want)
    return {g: s.groupby("month")["mw"].mean().to_dict() for g, s in d.groupby("grid")}


def expected_intervals(year, tz, minutes):
    a = pd.Timestamp(year=year, month=1, day=1, tz=tz)
    b = pd.Timestamp(year=year + 1, month=1, day=1, tz=tz)
    return (b - a).total_seconds() / 60.0 / minutes


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    mw = fleets(in_dir)
    dem = demand_monthly(in_dir)
    hh, _ = ercot_card.henry_hub_monthly(in_dir)
    e_rows, e_meta = ercot_card.compute({"hub": ERCOT_HUB, "first_year": first_year}, in_dir)
    rows, meta = [], {"first_year": first_year, "grids": {}, "ercot_card": e_meta}
    for g in GRIDS:
        grid = g["grid"]
        if grid == "ercot":
            for r in e_rows:   # the old card's rows, as it computes them: the proof that the ERCOT panel is the old card
                r = dict(r)
                r.pop("hub")
                year = int(r["period"][:4])
                full = share = None
                if r["kind"] == "year":
                    share = 100.0 * r["n_intervals"] / expected_intervals(year, g["tz"], 15)
                    full = bool(share >= 100.0 * FULL_YEAR_SHARE)
                rows.append({"grid": grid, "period": r.pop("period"), "kind": r.pop("kind"), "node": g["node"], "interval_minutes": 15, **r,
                             "share_of_year_pct": share, "full_year": full})
            meta["grids"][grid] = {"top1_threshold_usd_mwh": e_meta["top1_threshold_usd_mwh"], "last_interval_utc": e_meta["last_interval_utc"],
                                   "first_interval_utc": None, "n_intervals": e_meta["n_intervals_all"], "load_how": "ercot_zone_load_hourly, " + e_meta["load_how"]}
            continue
        d = grid_prices(g, first_year, in_dir)
        top1 = pct(d["value"].to_numpy(), 99)
        for month, s in d.groupby("month"):
            m = spike_measures(s["value"].to_numpy(), top1, g["minutes"])
            rows.append({"grid": grid, "period": month, "kind": "month", "node": g["node"], "interval_minutes": g["minutes"], **m,
                         "battery_mw": mw[grid].get(month), "load_mean_mw": dem.get(grid, {}).get(month), "henry_hub_usd_mmbtu": hh.get(month), "share_of_year_pct": None, "full_year": None})
        for year, s in d.groupby("year"):
            m = spike_measures(s["value"].to_numpy(), top1, g["minutes"])
            share = 100.0 * len(s) / expected_intervals(int(year), g["tz"], g["minutes"])
            rows.append({"grid": grid, "period": str(year), "kind": "year", "node": g["node"], "interval_minutes": g["minutes"], **m,
                         "battery_mw": mw[grid].get(f"{year}-12"), "load_mean_mw": None, "henry_hub_usd_mmbtu": None,
                         "share_of_year_pct": share, "full_year": bool(share >= 100.0 * FULL_YEAR_SHARE)})
        meta["grids"][grid] = {"top1_threshold_usd_mwh": top1, "first_interval_utc": d["ts"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
                               "last_interval_utc": d["ts"].max().strftime("%Y-%m-%dT%H:%M:%SZ"), "n_intervals": int(len(d)),
                               "load_how": "eia930_daily_demand, EIA's daily MWh over 24, mean of the month's days"}
    meta["grids"]["ercot"]["first_interval_utc"] = f"{first_year}-01-01T06:00:00Z"
    meta["fleet_last_month"] = max(mw["ercot"])
    return rows, meta


def grid_rows(rows, grid):
    return [r for r in rows if r["grid"] == grid]


def fit_grid(rows, grid):
    """The ERCOT card's regression on one grid's months. None when the months do not outnumber the parameters."""
    R = ercot_card.regression_rows(grid_rows(rows, grid))
    if len(R) <= 15 + 2:
        return None, len(R)
    try:
        return ercot_card.fit(grid_rows(rows, grid)), len(R)
    except np.linalg.LinAlgError:
        return None, len(R)


def clean(x):
    if x is None:
        return None
    if isinstance(x, (float, np.floating)) and (np.isnan(x) or np.isinf(x)):
        return None
    return x


def numbers_from_rows(rows, meta=None):
    """Every number on the card, from the data rows alone (the test's proof). Keys are <grid>_<name>; the ERCOT keys
    are the old card's names, so that the old card's numbers can be compared one for one."""
    n, fits = {}, {}
    for g in GRIDS:
        grid = g["grid"]
        R = grid_rows(rows, grid)
        if grid == "ercot":
            old, f = ercot_card.numbers_from_rows(R)
            for k, v in old.items():
                n[f"ercot_{k}"] = v
            fits[grid] = f
            n["ercot_full_years"] = sum(1 for r in R if r["kind"] == "year" and r["full_year"])
            n["ercot_reg_df"] = old["reg_n"] - 15
            continue
        years = {r["period"]: r for r in R if r["kind"] == "year"}
        months = [r for r in R if r["kind"] == "month"]
        full = sorted(y for y, r in years.items() if r["full_year"])
        ys = sorted(years)
        first = full[0] if full else None
        last = full[-1] if full else None
        this = ys[-1]
        fl = [r for r in months if r["battery_mw"] is not None]
        top = max(months, key=lambda r: r["worst_interval_multiple"] or 0)
        n.update({f"{grid}_first_year": first, f"{grid}_last_full_year": last, f"{grid}_this_year": this, f"{grid}_full_years": len(full),
                  f"{grid}_first_month": months[0]["period"], f"{grid}_last_month": months[-1]["period"],
                  f"{grid}_n_months": len(months), f"{grid}_n_intervals": sum(r["n_intervals"] for r in months),
                  f"{grid}_fleet_first_month": fl[0]["period"], f"{grid}_fleet_first_mw": fl[0]["battery_mw"],
                  f"{grid}_fleet_last_month": fl[-1]["period"], f"{grid}_fleet_last_mw": fl[-1]["battery_mw"],
                  f"{grid}_peak_multiple_month": top["period"], f"{grid}_peak_multiple": top["worst_interval_multiple"]})
        for tag, y in (("first", first), ("last", last), ("this", this)):
            r = years.get(y) if y else None
            for key, short in (("worst_interval_multiple", "multiple"), ("hours_ge_1000", "hours1000"), ("hours_top1pct", "hours_top1"),
                               ("hours_ge_250", "hours250"), ("p999_usd_mwh", "p999"), ("median_usd_mwh", "median")):
                n[f"{grid}_{short}_{tag}"] = r[key] if r else None
            n[f"{grid}_share_{tag}_pct"] = r["share_of_year_pct"] if r else None
        f, n_reg = fit_grid(rows, grid)
        fits[grid] = f
        n[f"{grid}_reg_n"] = n_reg
        n[f"{grid}_reg_df"] = n_reg - 15
        if f:
            n[f"{grid}_reg_first"], n[f"{grid}_reg_last"] = f["sample"]["first"], f["sample"]["last"]
            for key, short in REG:
                for stat in ("coef", "se", "p", "r2"):
                    n[f"{grid}_reg_{short}_{stat}"] = clean(f[key][stat])
    n["grids_with_two_full_years"] = [g["grid"] for g in GRIDS if (n.get(f"{g['grid']}_full_years") or 0) >= 2]
    n["grids_multiple_fell"] = [g for g in n["grids_with_two_full_years"] if n[f"{g}_multiple_last"] < n[f"{g}_multiple_first"]]
    n["grids_reg_negative_sig"] = [g["grid"] for g in GRIDS if n.get(f"{g['grid']}_reg_multiple_p") is not None
                                   and n[f"{g['grid']}_reg_multiple_p"] < 0.05 and n[f"{g['grid']}_reg_multiple_coef"] < 0]
    n["grids_reg_positive_sig"] = [g["grid"] for g in GRIDS if n.get(f"{g['grid']}_reg_multiple_p") is not None
                                   and n[f"{g['grid']}_reg_multiple_p"] < 0.05 and n[f"{g['grid']}_reg_multiple_coef"] > 0]
    return n, fits


def words_list(grids):
    w = [GRID[g]["words"] for g in grids]
    if not w:
        return "no grid"
    return w[0] if len(w) == 1 else ", ".join(w[:-1]) + " and " + w[-1]


def p_words(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def grid_words(n, grid):
    """The regression of one grid in plain words, and its honest caveat."""
    g = GRID[grid]
    c, se, p = n.get(f"{grid}_reg_multiple_coef"), n.get(f"{grid}_reg_multiple_se"), n.get(f"{grid}_reg_multiple_p")
    gw = n[f"{grid}_fleet_last_mw"] / 1000.0
    if c is None:
        return (f"{g['words']}: not run, {n[f'{grid}_reg_n']} months do not outnumber the 15 parameters.", "No regression: too few months.")
    if p < 0.05:
        way = "lower" if c < 0 else "higher"
        said = f"each added GW of batteries goes with a worst-interval multiple {fmt(abs(c), 2)} {way} (standard error {fmt(se, 2)}, {p_words(p)})"
    else:
        said = f"the battery coefficient on the multiple is {fmt(c, 2)} per GW with a standard error of {fmt(se, 2)} ({p_words(p)}): flat"
    cav = []
    if n[f"{grid}_reg_df"] < 30:
        cav.append(f"{n[f'{grid}_reg_n']} months against 15 parameters leave {n[f'{grid}_reg_df']} degrees of freedom: read it as a description, not a test")
    if gw < 2.0:
        cav.append(f"the fleet never passed {fmt(gw, 2)} GW, so \"per GW\" is an extrapolation beyond anything this grid has seen")
    if g["minutes"] == 60:
        cav.append("hourly prices: an hour's mean hides a spike that quarter hours would show, so the level is not comparable with the 15-minute grids")
    if grid == "ercot":
        cav.append("the same months brought the 2021 winter storm, a new offer cap, more solar and a gas price that doubled and fell back")
    cav.append("an association in a before-and-after with controls, not a cause")
    return f"{g['words']}: with load, Henry Hub and the month of the year held fixed, {said}.", "Caveat: " + "; ".join(cav) + "."


def verdict(n):
    """The subtitle, chosen by the data: where the answer is flat or against the title, it says so."""
    two, fell, neg = n["grids_with_two_full_years"], n["grids_multiple_fell"], n["grids_reg_negative_sig"]
    short = [g["grid"] for g in GRIDS if g["grid"] not in two]
    big_flat = [g["grid"] for g in GRIDS if g["grid"] not in neg and n[f"{g['grid']}_fleet_last_mw"] >= 10000]
    if neg == ["ercot"] and big_flat:
        return f"In Texas the spikes shrank as the fleet grew. No other grid shows it, {words_list(big_flat)} with a fleet nearly as large included"
    if neg == ["ercot"]:
        return "In Texas the spikes shrank as the fleet grew. No other grid shows it, and no other grid has the fleet"
    if neg:
        return f"The fleet coefficient is negative and clear of zero in {words_list(neg)}; elsewhere the data is short or flat"
    if fell:
        return f"Spikes shrank in {words_list(fell)}, but no grid's regression can pin it on batteries"
    return "No grid shows spikes shrinking with its fleet"


def panel_table(n, fits, grid):
    f = fits[grid]
    if not f:
        return []
    return [{"measure": f[k]["label"], "coef_per_gw": clean(f[k]["coef"]), "se": clean(f[k]["se"]), "p": clean(f[k]["p"]), "n": f[k]["n"], "r2": clean(f[k]["r2"])}
            for k in ("worst_interval_multiple", "hours_ge_1000", "hours_top1pct")]


def panel_callouts(n, grid):
    w = GRID[grid]["words"]
    y0, y1, yt = n[f"{grid}_first_year"], n[f"{grid}_last_full_year"], n.get(f"{grid}_this_year")
    if grid != "ercot" and n[f"{grid}_full_years"] < 2:
        a, b, ta, tb = y1, f"{yt} to date", "last", "this"   # one full year held: it is set against the year to date, and labeled so
    else:
        a, b, ta, tb = y0, y1, "first", "last"
    return [
        callout(f"{w} worst-interval multiple", str(a), f"{fmt(n[f'{grid}_multiple_{ta}'], 1)}x", str(b), f"{fmt(n[f'{grid}_multiple_{tb}'], 1)}x"),
        callout(f"{w} hours at or above USD 1,000/MWh", str(a), fmt(n[f"{grid}_hours1000_{ta}"], 0), str(b), fmt(n[f"{grid}_hours1000_{tb}"], 0), "hours"),
        callout(f"{w} battery fleet", n[f"{grid}_fleet_first_month"], f"{fmt(n[f'{grid}_fleet_first_mw'], 0)} MW", n[f"{grid}_fleet_last_month"],
                f"{fmt(n[f'{grid}_fleet_last_mw'], 0)} MW"),
    ]


def chart(rows, n, fits):
    x = sorted({r["period"] for r in rows if r["kind"] == "month"})
    panels = []
    for g in GRIDS:
        grid = g["grid"]
        by = {r["period"]: r for r in grid_rows(rows, grid) if r["kind"] == "month"}
        vals = {key: [by[m][key] if m in by else None for m in x] for key, _, _, _ in MEASURES}
        fleet = [by[m]["battery_mw"] if m in by else None for m in x]
        gx = [m for m in x if m in by]
        said, cav = grid_words(n, grid)
        every = "hour" if g["minutes"] == 60 else "15 minutes"
        single = {"kind": "line_with_fleet", "x": gx, "x_label": f"Month ({g['tz']})",
                  "series": [{"name": "Worst-interval multiple (P99.9 / median)", "axis": "left", "type": "line", "unit": "x", "values": [by[m]["worst_interval_multiple"] for m in gx]},
                             {"name": "Hours at or above USD 1,000/MWh", "axis": "left_hours", "type": "bar", "unit": "hours", "values": [by[m]["hours_ge_1000"] for m in gx]},
                             {"name": f"{g['words']} battery fleet (MW, operating)", "axis": "right", "type": "line", "unit": "MW", "values": [by[m]["battery_mw"] for m in gx]}],
                  "y_left_label": "multiple (x)", "y_right_label": "battery MW"}
        panels.append({"grid": grid, "words": g["words"], "title": f"{g['words']}: {g['node_words']}, every {every}, from {gx[0]}",
                       "first": gx[0], "last": gx[-1], "values": vals, "fleet": fleet, "single": single,
                       "callouts": panel_callouts(n, grid), "table": panel_table(n, fits, grid), "in_words": said, "caveat": cav})
    return {"kind": "multiples", "param": "lunch_grid", "x": x, "x_label": "Month (each grid's local time)",
            "measures": [{"key": k, "label": lab, "unit": u, "decimals": d} for k, lab, u, d in MEASURES],
            "fleet_label": "battery fleet, MW operating (EIA-860M)", "fleet_unit": "MW",
            "axis_note": ("One timeline for every grid; a panel starts where the grid's prices start. Left axis (the measure): each grid's own scale. "
                          "Right axis (battery MW, shaded): one shared scale, so the fleets compare at a glance."),
            "fleet_axis": "shared", "measure_axis": "own", "table_columns": ["Measure (monthly)", "Per GW of batteries", "SE (HC1)", "p", "Months", "R2"],
            "panels": panels, "placeholders": PLACEHOLDERS, "series": [], "all_label": "All grids"}


def span_words(meta, n):
    out = []
    for g in GRIDS:
        grid = g["grid"]
        m = meta["grids"][grid]
        every = "hourly" if g["minutes"] == 60 else "15-minute"
        ni = n["ercot_n_intervals"] if grid == "ercot" else n[f"{grid}_n_intervals"]
        nm = n["ercot_n_months"] if grid == "ercot" else n[f"{grid}_n_months"]
        first = f"{n['ercot_first_year']}-01" if grid == "ercot" else n[f"{grid}_first_month"]
        tables = "ercot_all_hub_prices_history and iso_rtm_hub_prices" if grid == "ercot" else (g["table"] if g["minutes"] == 60 else g["table"] + " and iso_rtm_hub_prices")
        out.append(f"{g['words']} {g['node']} ({every}, {tables}, {first} to {m['last_interval_utc'][:10]}, {fmt(ni, 0)} intervals in {nm} local months, {g['tz']}, "
                   f"top 1 percent at {fmt(m['top1_threshold_usd_mwh'], 2)} USD/MWh)")
    return "; ".join(out)


def card(rows, params, meta):
    n, fits = numbers_from_rows(rows, meta)
    sub = verdict(n)
    y0, y1 = n["ercot_first_year"], n["ercot_last_full_year"]
    ny0, ny1 = n["nyiso_first_year"], n["nyiso_last_full_year"]
    said = {g["grid"]: grid_words(n, g["grid"]) for g in GRIDS}
    short = [g["grid"] for g in GRIDS if g["grid"] not in n["grids_with_two_full_years"]]
    flat_short = [g for g in short if n.get(f"{g}_reg_multiple_p") is not None and n[f"{g}_reg_multiple_p"] >= 0.05]
    flat_words = "is flat in each" if len(flat_short) == len(short) else f"is flat in {words_list(flat_short)}"
    ny_way = "fell" if n["nyiso_multiple_last"] < n["nyiso_multiple_first"] else "rose"
    ca_way = "fell" if n["caiso_multiple_this"] < n["caiso_multiple_last"] else "rose"
    rest = [g for g in ("isone", "spp") if n[f"{g}_multiple_last"] is not None]
    rest_bits = "; ".join(f"{GRID[g]['words']} {fmt(n[f'{g}_multiple_last'], 1)}x and {fmt(n[f'{g}_multiple_this'], 1)}x on {fmt(n[f'{g}_fleet_last_mw'], 0)} MW" for g in rest)
    why = (f"A battery that sells into a spike makes the spike smaller, so a big enough fleet should eat its own lunch. Texas has the fleet, "
           f"{fmt(n['ercot_fleet_first_mw'], 0)} MW in {n['ercot_fleet_first_month']} and {fmt(n['ercot_fleet_last_mw'], 0)} MW in {n['ercot_fleet_last_month']} (EIA-860M), "
           f"and its worst-interval multiple went from {fmt(n['ercot_multiple_first'], 1)}x in {y0} to {fmt(n['ercot_multiple_last'], 1)}x in {y1}, its hours at or above "
           f"USD 1,000 from {fmt(n['ercot_hours1000_first'], 0)} to {fmt(n['ercot_hours1000_last'], 0)}. New York is the comparison nobody planned: "
           f"{fmt(n['nyiso_fleet_last_mw'], 0)} MW of batteries in {n['nyiso_fleet_last_month']}, and a multiple that {ny_way} from {fmt(n['nyiso_multiple_first'], 1)}x in {ny0} to "
           f"{fmt(n['nyiso_multiple_last'], 1)}x in {ny1} (hourly prices), with {fmt(n['nyiso_hours1000_first'], 0)} and then {fmt(n['nyiso_hours1000_last'], 0)} hours at or above USD 1,000. "
           f"California spoils the story: its fleet grew from {fmt(n['caiso_fleet_first_mw'], 0)} MW in {n['caiso_fleet_first_month']} to {fmt(n['caiso_fleet_last_mw'], 0)} MW, "
           f"and its multiple {ca_way} from {fmt(n['caiso_multiple_last'], 1)}x in {n['caiso_last_full_year']} to {fmt(n['caiso_multiple_this'], 1)}x in {n['caiso_this_year']} to date; "
           f"the warehouse holds its prices from {n['caiso_first_month']} only, so the years in which that fleet was built are not on the chart. "
           f"The same holds for {words_list(rest)} ({n['isone_last_full_year']} against {n['isone_this_year']} to date: {rest_bits}). "
           f"{said['ercot'][0]} {said['nyiso'][0]} For {words_list(short)} the regression has {' and '.join(sorted({str(n[f'{g}_reg_n']) for g in short}))} months and {flat_words}; "
           "each grid's view prints it with its caveat. Nothing here separates a fleet from the years it arrived in, and a grid with one year of prices has no before to compare.")
    foot = ("Data: real-time prices, " + span_words(meta, n) + ". A grid's panel starts where its prices start in the warehouse; nothing earlier is filled. "
            "Per grid, local month and local year: the median and the 99.9th percentile (numpy linear percentiles, no cap or exclusion), their ratio (the worst-interval "
            "multiple), hours at or above USD 1,000 and USD 250 (intervals times their length), and hours at or above the 99th percentile of every interval of that grid's "
            "own sample (one fixed threshold per grid). A year is full when it holds at least 90 percent of its intervals (ISO-NE's " + str(n['isone_last_full_year']) + f" holds {fmt(n['isone_share_last_pct'], 1)} percent); a grid"
            " with one full year is compared with the year to date and labeled so. Fleet: storage_buildout_monthly, battery_operating_mw of iso:ercot, iso:caiso, iso:nyiso, iso:isone and iso:spp. A unit is a "
            "generator with prime mover BA in EIA-860M's inventory; it is assigned to a grid by its balancing authority code (ERCO, CISO, NYIS, ISNE, SWPP) and counted "
            f"at nameplate MW from its first operating month until the month it retired (inventory of {meta['fleet_last_month']}; months after it carry no fleet figure). "
            "Load: ERCOT from ercot_zone_load_hourly, monthly mean; the other grids from eia930_daily_demand (EIA-930 daily MWh of the balancing authority over 24, mean of "
            "the month's days, EIA's Eastern day). Gas: eia_fuel_spot_prices Henry Hub daily spot, monthly mean. Regression, per grid: OLS of each monthly spike measure on "
            "battery GW, mean load in GW, Henry Hub in USD/MMBtu and eleven month-of-year dummies (15 parameters), over the months with every regressor held, HC1 standard "
            "errors, p from Student's t: " + "; ".join(f"{g['words']} {n[g['grid'] + '_reg_n']} months" for g in GRIDS) + ". No instrument, no event window: associations. "
            "MISO is paused while its terms are reviewed and PJM needs a licensed source: neither is requested, neither is data here.")
    table = []
    for g in GRIDS:
        grid = g["grid"]
        if n.get(f"{grid}_reg_multiple_coef") is None:
            continue
        table.append({"measure": f"{g['words']} ({n[f'{grid}_reg_first']} to {n[f'{grid}_reg_last']})", "coef_per_gw": n[f"{grid}_reg_multiple_coef"],
                      "se": n[f"{grid}_reg_multiple_se"], "p": n[f"{grid}_reg_multiple_p"], "n": n[f"{grid}_reg_n"], "r2": n[f"{grid}_reg_multiple_r2"]})
    in_words = " ".join(said[g["grid"]][0] + " " + said[g["grid"]][1] for g in GRIDS)
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub, "params": {"first_year": meta["first_year"]},
        "inputs_words": {"grids": "ERCOT, CAISO, NYISO, ISO-NE, SPP", "first_year": str(meta["first_year"])},
        "chart": chart(rows, n, fits),
        "callouts": [
            callout("ERCOT worst-interval multiple", y0, f"{fmt(n['ercot_multiple_first'], 1)}x", y1, f"{fmt(n['ercot_multiple_last'], 1)}x"),
            callout("NYISO worst-interval multiple (hourly)", ny0, f"{fmt(n['nyiso_multiple_first'], 1)}x", ny1, f"{fmt(n['nyiso_multiple_last'], 1)}x"),
            callout(f"Battery fleet, {n['ercot_fleet_last_month']}", "ERCOT", f"{fmt(n['ercot_fleet_last_mw'], 0)} MW", "NYISO", f"{fmt(n['nyiso_fleet_last_mw'], 0)} MW"),
        ],
        "why": why, "footnote": foot, "numbers": n, "placeholders": PLACEHOLDERS, "supersedes": SUPERSEDES,
        "effect_table": {"columns": ["Grid: worst-interval multiple, monthly", "Per GW of batteries", "SE (HC1)", "p", "Months", "R2"], "rows": table, "in_words": in_words},
        "source_line": "Source: ERCOT (NP6-785-ER, NP6-905-CD), CAISO OASIS, NYISO (P-4A), ISO-NE, SPP, EIA-860M, EIA-930, EIA Henry Hub spot; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per grid and local month and one per grid and local year (kind): the spike measures, the grid's battery fleet, its mean load and Henry Hub; "
                       "share_of_year_pct is the share of the year's intervals held and full_year whether it is at least 90 percent. MISO and PJM are not in the file: paused, and licensed",
                       "Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["interval_minutes", "share_of_year_pct", "n_intervals", "median_usd_mwh", "p999_usd_mwh", "worst_interval_multiple", "hours_top1pct", "hours_ge_1000", "hours_ge_250",
         "battery_mw", "load_mean_mw", "henry_hub_usd_mmbtu"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces each grid's regression from {CSV_NAME}.",
        "* The CSV begins with four comment lines: the names are on line 5 and the data from line 6.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(5) rowrange(6) stringcols(_all) clear',
        'keep if kind == "month"',
        *do_destring(V),
        *do_sentinels(V),
        "gen battery_gw = battery_mw / 1000",
        "gen load_gw = load_mean_mw / 1000",
        "gen month_of_year = real(substr(period, 6, 2))",
        "drop if missing(battery_gw) | missing(load_gw) | missing(henry_hub_usd_mmbtu) | missing(worst_interval_multiple)",
        ["foreach g in ercot caiso nyiso isone spp {",
         "    foreach y in worst_interval_multiple hours_ge_1000 hours_top1pct {",
         "        regress `y' battery_gw load_gw henry_hub_usd_mmbtu i.month_of_year if grid == \"`g'\", vce(robust)",
         "    }",
         "}"],
        "* vce(robust) is HC1, the card's standard errors",
    ])


SOURCE_PATH = os.path.abspath(__file__)
