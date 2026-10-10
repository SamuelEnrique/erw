"""Finding: "The peak hour moved" across every grid with public prices (session 182).

The card of session 174 (peak_hour_moved.py: ERCOT and CAISO), asked of five grids on one timeline: ERCOT, CAISO, NYISO,
ISO-NE and SPP. MISO is paused while its terms are reviewed and PJM needs a licensed source: placeholders, never data,
never requested. For every local day of each grid the hourly mean real-time price is computed, the day's highest hour
is taken (the first hour on a tie; a day needs at least 20 held hours), and each year's days are counted by that hour:
the share of days peaking in each hour, the median peak hour, the share peaking in the evening (17:00 to 21:59) and at
midday (10:00 to 15:59). Each grid is set against its own solar fleet: nameplate MW of solar photovoltaic generators in
its balancing authority operating at the end of the year (EIA-860M, plants of 1 MW and more: rooftop solar is not in it).

A grid's panel starts where its real-time prices start in the warehouse: ERCOT and NYISO in 2019, CAISO, ISO-NE and SPP
in September 2024. Local time is each grid's own, daylight saving handled by the time zone conversion, as in the old
card. The ERCOT and CAISO rows are the old card's own rows (its compute is called), so they equal it number for number.

Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT HB_HUBAVG), iso_hub_prices_history and
iso_rtm_hub_prices (CAISO TH_SP15_GEN-APND, ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB), iso_zone_prices_history (NYISO
N.Y.C., hourly), eia860m_operating_generators and eia860m_retired_generators_all (solar capacity by year).
"""

import os

import numpy as np
import pandas as pd

import peak_hour_moved as old_card
from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table

NAME = "peak_hour_grids"
TITLE = "THE PEAK HOUR MOVED: FIVE GRIDS"
KIND = "visual"
INPUTS = {
    "first_year": {"label": "First year", "default": 2019, "choices": [2019]},
    "min_hours": {"label": "Hours a day must hold", "default": 20, "choices": [20, 24]},
}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_hub_prices_history", "iso_zone_prices_history",
          "eia860m_operating_generators", "eia860m_retired_generators_all"]
CSV_NAME = "erw_2026_grids_peak_hour_solar.csv"
SUPERSEDES = "peak_hour_moved"
GRIDS = [
    {"grid": "ercot", "words": "ERCOT", "tz": "America/Chicago", "ba": "ERCO", "node": "HB_HUBAVG", "node_words": "hub average", "every": "15 minutes"},
    {"grid": "caiso", "words": "CAISO", "tz": "America/Los_Angeles", "ba": "CISO", "node": "TH_SP15_GEN-APND", "node_words": "SP15", "every": "15 minutes"},
    {"grid": "nyiso", "words": "NYISO", "tz": "America/New_York", "ba": "NYIS", "node": "N.Y.C.", "node_words": "New York City zone", "every": "hour",
     "table": "iso_zone_prices_history", "market": "nyiso_rtm", "live": False,
     "how": "N.Y.C., NYISO's own integrated hourly real-time price"},
    {"grid": "isone", "words": "ISO-NE", "tz": "America/New_York", "ba": "ISNE", "node": ".H.INTERNAL_HUB", "node_words": "internal hub", "every": "15 minutes",
     "table": "iso_hub_prices_history", "market": "isone_rtm", "live": True,
     "how": ".H.INTERNAL_HUB, the mean of the 15-minute interval means in the local hour"},
    {"grid": "spp", "words": "SPP", "tz": "America/Chicago", "ba": "SWPP", "node": "SPPNORTH_HUB", "node_words": "North Hub", "every": "15 minutes",
     "table": "iso_hub_prices_history", "market": "spp_rtm", "live": True,
     "how": "SPPNORTH_HUB, the mean of the 15-minute interval means in the local hour"},
]
GRID = {g["grid"]: g for g in GRIDS}
OLD_GRIDS = [g[0] for g in old_card.GRIDS]   # ercot, caiso: computed by the old card's own compute
PLACEHOLDERS = [{"grid": "miso", "words": "MISO", "text": "paused while terms are reviewed"},
                {"grid": "pjm", "words": "PJM", "text": "licensed source needed"}]
EVENING, MIDDAY = old_card.EVENING, old_card.MIDDAY
FULL_DAYS = 300   # a year is full when at least 300 of its days are held (the old card's own rule for drawing a year)
MEASURES = [("share_evening_pct", "Days peaking 17:00 to 21:59", "% of days", 1),
            ("share_midday_pct", "Days peaking 10:00 to 15:59", "% of days", 1),
            ("median_peak_hour", "Median peak hour (local)", "hour", 1)]


def new_grid_prices(g, in_dir):
    h = read_table(g["table"], in_dir, usecols=["ts_utc", "value", "market", "node"],
                   keep=lambda c: (c["market"] == g["market"]) & (c["node"] == g["node"]))
    parts = [h[["ts_utc", "value"]]]
    if g["live"]:
        live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == g["market"]) & (c["node"] == g["node"]))
        parts.append(live[["ts_utc", "value"]])
    d = pd.concat(parts).drop_duplicates("ts_utc")
    if d.empty:
        raise NoData(f"no real-time rows for {g['grid']}")
    return d


def year_rows(grid, days, years, solar):
    """One grid's rows, one per year and hour: the old card's own arithmetic."""
    rows = []
    for y in years:
        s = days[days["year"] == y]
        n = int(len(s))
        counts = s["peak_hour"].value_counts() if n else pd.Series(dtype=int)
        med = float(np.median(s["peak_hour"])) if n else None
        evening = float(s["peak_hour"].between(*EVENING).mean() * 100) if n else None
        midday = float(s["peak_hour"].between(*MIDDAY).mean() * 100) if n else None
        for hr in range(24):
            rows.append({"grid": grid, "year": y, "hour": hr, "share_days_pct": float(counts.get(hr, 0) / n * 100) if n else None,
                         "n_days": n if n else None, "median_peak_hour": med, "share_evening_pct": evening, "share_midday_pct": midday,
                         "solar_mw_yearend": solar[y]})
    return rows


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    min_hours = int(params.get("min_hours", 20))
    rows, old_meta = old_card.compute({"first_year": first_year, "min_hours": min_hours}, in_dir)
    years = sorted({r["year"] for r in rows})
    meta = {"first_year": first_year, "min_hours": min_hours, "spans": dict(old_meta["spans"]), "missing": list(old_meta["missing"])}
    for g in GRIDS:
        if g["grid"] in OLD_GRIDS:
            continue
        solar = old_card.solar_mw_by_year(g["ba"], years, in_dir)
        d = new_grid_prices(g, in_dir)
        days = old_card.daily_peak_hours(d, g["tz"], min_hours)
        days = days[days["year"] >= first_year]
        meta["spans"][g["grid"]] = {"first_day": days["day"].min(), "last_day": days["day"].max(), "n_days": int(len(days)), "how": g["how"], "tz": g["tz"]}
        rows += year_rows(g["grid"], days, years, solar)
    return rows, meta


def numbers_from_rows(rows, params=None):
    """Every number on the card from the rows alone. For ERCOT and CAISO the keys are the old card's keys, computed here
    by this module's own code, so that the test can compare them with the old card's numbers one for one."""
    years = sorted({r["year"] for r in rows})
    first, this_year = years[0], years[-1]
    last_full = max(y for y in years if y < this_year)
    at = {(r["grid"], r["year"], r["hour"]): r for r in rows}
    n = {"first_year": first, "last_full_year": last_full, "this_year": this_year}
    for g in GRIDS:
        grid = g["grid"]
        held = [y for y in years if (at.get((grid, y, 0)) or {}).get("n_days")]
        full = [y for y in held if at[(grid, y, 0)]["n_days"] >= FULL_DAYS and y < this_year]
        picks = {"first": held[0] if held else None, "last": max((y for y in held if y < this_year), default=None),
                 "this": this_year if this_year in held else None, "full0": full[0] if full else None, "full1": full[-1] if full else None}
        n[f"{grid}_first_held_year"], n[f"{grid}_last_full_held_year"] = picks["first"], picks["last"]
        n[f"{grid}_full_years"] = len(full)
        for tag, y in picks.items():
            r = at.get((grid, y, 0)) if y is not None else None
            n[f"{grid}_{tag}_year"] = y
            for key, short in (("median_peak_hour", "median_hour"), ("share_evening_pct", "evening_pct"), ("share_midday_pct", "midday_pct"),
                               ("n_days", "days"), ("solar_mw_yearend", "solar_mw")):
                n[f"{grid}_{tag}_{short}"] = r[key] if r else None
            if r:
                top = max((at[(grid, y, h)] for h in range(24)), key=lambda x: x["share_days_pct"] or 0)
                n[f"{grid}_{tag}_modal_hour"], n[f"{grid}_{tag}_modal_pct"] = top["hour"], top["share_days_pct"]
            else:
                n[f"{grid}_{tag}_modal_hour"] = n[f"{grid}_{tag}_modal_pct"] = None
        n[f"{grid}_solar_mw_first_year"] = (at.get((grid, first, 0)) or {}).get("solar_mw_yearend")
        n[f"{grid}_solar_mw_last_full_year"] = (at.get((grid, last_full, 0)) or {}).get("solar_mw_yearend")
    two = [g["grid"] for g in GRIDS if n[f"{g['grid']}_full_years"] >= 2]
    n["grids_with_two_full_years"] = two
    n["grids_evening_up_10"] = [g for g in two if n[f"{g}_full1_evening_pct"] - n[f"{g}_full0_evening_pct"] > 10]
    n["grids_evening_down_10"] = [g for g in two if n[f"{g}_full1_evening_pct"] - n[f"{g}_full0_evening_pct"] < -10]
    return n


def words_list(grids):
    w = [GRID[g]["words"] for g in grids]
    if not w:
        return "no grid"
    return w[0] if len(w) == 1 else ", ".join(w[:-1]) + " and " + w[-1]


def compare_tags(n, grid):
    """The two periods a grid's callouts compare: its first and last full years, or, with one full year, that year
    against the year to date (labeled so)."""
    if n[f"{grid}_full_years"] >= 2:
        return ("full0", str(n[f"{grid}_full0_year"])), ("full1", str(n[f"{grid}_full1_year"]))
    if n[f"{grid}_full_years"] == 1 and n[f"{grid}_this_year"] is not None:
        return ("full1", str(n[f"{grid}_full1_year"])), ("this", f"{n[f'{grid}_this_year']} to date")
    return ("first", str(n[f"{grid}_first_year"])), ("this", f"{n[f'{grid}_this_year']} to date")


def panel_callouts(n, grid):
    w = GRID[grid]["words"]
    (ta, la), (tb, lb) = compare_tags(n, grid)
    return [
        callout(f"{w} median peak hour (local)", la, f"hour {fmt(n[f'{grid}_{ta}_median_hour'], 0)}", lb, f"hour {fmt(n[f'{grid}_{tb}_median_hour'], 0)}"),
        callout(f"{w} days peaking 17:00 to 21:59", la, f"{fmt(n[f'{grid}_{ta}_evening_pct'], 1)}%", lb, f"{fmt(n[f'{grid}_{tb}_evening_pct'], 1)}%"),
        callout(f"{w} solar fleet, year end", la, f"{fmt(n[f'{grid}_{ta}_solar_mw'], 0)} MW", lb, f"{fmt(n[f'{grid}_{tb}_solar_mw'], 0)} MW"),
    ]


def grid_words(n, grid):
    """One grid in plain words, from its numbers; and its caveat."""
    g = GRID[grid]
    (ta, la), (tb, lb) = compare_tags(n, grid)
    ev0, ev1 = n[f"{grid}_{ta}_evening_pct"], n[f"{grid}_{tb}_evening_pct"]
    way = "rose" if ev1 > ev0 + 1 else "fell" if ev1 < ev0 - 1 else "held"
    said = (f"{g['words']}: the share of days whose dearest hour fell between 17:00 and 21:59 {way} from {fmt(ev0, 1)} percent in {la} to {fmt(ev1, 1)} percent in {lb}; "
            f"the median peak hour went from {fmt(n[f'{grid}_{ta}_median_hour'], 0)} to {fmt(n[f'{grid}_{tb}_median_hour'], 0)}, the most common peak hour from "
            f"{fmt(n[f'{grid}_{ta}_modal_hour'], 0)} to {fmt(n[f'{grid}_{tb}_modal_hour'], 0)}, with solar at {fmt(n[f'{grid}_{ta}_solar_mw'], 0)} and then "
            f"{fmt(n[f'{grid}_{tb}_solar_mw'], 0)} MW ({fmt(n[f'{grid}_{ta}_days'], 0)} and {fmt(n[f'{grid}_{tb}_days'], 0)} days).")
    cav = []
    if n[f"{grid}_full_years"] < 2:
        cav.append(f"prices are held from {n[f'{grid}_first_year']} only, so one full year is set against the year to date: seasons differ between the two")
    if grid in ("nyiso", "isone"):
        cav.append("EIA-860M counts plants of 1 MW and more, and most of this grid's solar sits on rooftops, outside the count")
    if g["every"] == "hour":
        cav.append("hourly prices, where the other grids' hours are means of 15-minute prices")
    cav.append("a comparison of years: it does not separate solar from gas prices, load growth, weather or batteries")
    return said, "Caveat: " + "; ".join(cav) + "."


def verdict(n):
    up, down, two = n["grids_evening_up_10"], n["grids_evening_down_10"], n["grids_with_two_full_years"]
    flat = [g for g in two if g not in up and g not in down]
    small = [g for g in up if n[f"{g}_full1_solar_mw"] < 5000]
    if up and small and not flat and not down:
        return (f"The dearest hour walked into the evening in {words_list(up)}; {words_list(small)} did it on "
                f"{fmt(max(n[f'{g}_full1_solar_mw'] for g in small), 0)} MW of counted solar, so panels are not the whole story")
    if up and flat:
        return f"In {words_list(up)} the dearest hour walked into the evening as solar grew; in {words_list(flat)} it did not move"
    if up and down:
        return f"The dearest hour moved later in {words_list(up)} and earlier in {words_list(down)}"
    if up:
        return f"In {words_list(up)} the dearest hour walked into the evening as solar grew"
    if down:
        return f"The dearest hour moved earlier, not later, in {words_list(down)}"
    return "The dearest hour barely moved on any grid with two full years of prices"


def chart(rows, n, meta):
    years = sorted({r["year"] for r in rows})
    at = {(r["grid"], r["year"], r["hour"]): r for r in rows}
    x = [str(y) for y in years]
    hours = [f"{h:02d}" for h in range(24)]
    panels = []
    for g in GRIDS:
        grid = g["grid"]
        vals = {key: [(at[(grid, y, 0)][key] if at[(grid, y, 0)]["n_days"] else None) for y in years] for key, _, _, _ in MEASURES}
        days = [at[(grid, y, 0)]["n_days"] for y in years]
        fleet = [at[(grid, y, 0)]["solar_mw_yearend"] if at[(grid, y, 0)]["n_days"] else None for y in years]
        series, seen = [], set()
        for tag in ("full0", "full1", "this"):
            y = n.get(f"{grid}_{tag}_year")
            if y is None or y in seen:
                continue
            seen.add(y)
            series.append({"name": f"{g['words']} {y}" + (" (to date)" if y == n["this_year"] else ""), "type": "line", "unit": "percent of days",
                           "values": [at[(grid, y, h)]["share_days_pct"] for h in range(24)], "days": n.get(f"{grid}_{tag}_days")})
        single = {"kind": "lines", "x": hours, "x_label": f"Hour of the day ({g['tz']}) in which the day's highest real-time price fell",
                  "series": series, "y_left_label": "percent of the year's days", "value_suffix": "%", "decimals": 1}
        said, cav = grid_words(n, grid)
        panels.append({"grid": grid, "words": g["words"], "title": f"{g['words']}: {g['node_words']}, every {g['every']}, from {meta['spans'][grid]['first_day'][:7]}",
                       "first": str(n[f"{grid}_first_year"]), "last": str(n[f"{grid}_this_year"] or n[f"{grid}_last_year"]), "values": vals, "fleet": fleet, "days": days,
                       "single": single, "callouts": panel_callouts(n, grid), "table": [], "in_words": said, "caveat": cav})
    return {"kind": "multiples", "param": "peak_grid", "x": x, "x_label": "Year (each grid's local days)",
            "measures": [{"key": k, "label": lab, "unit": u, "decimals": d} for k, lab, u, d in MEASURES],
            "fleet_label": "solar fleet at year end, MW (EIA-860M)", "fleet_unit": "MW",
            "axis_note": ("One timeline for every grid; a panel starts where the grid's prices start, and a year with fewer than 300 days is drawn as held (hover gives its days). "
                          "Left axis (the measure): one shared scale. Right axis (solar MW, shaded): one shared scale, so the fleets compare at a glance."),
            "fleet_axis": "shared", "measure_axis": "shared", "panels": panels, "placeholders": PLACEHOLDERS, "series": [], "all_label": "All grids"}


def card(rows, params, meta):
    n = numbers_from_rows(rows, params)
    sub = verdict(n)
    spans = meta["spans"]
    said = {g["grid"]: grid_words(n, g["grid"]) for g in GRIDS}
    short = [g["grid"] for g in GRIDS if g["grid"] not in n["grids_with_two_full_years"]]
    e0, e1 = n["ercot_full0_year"], n["ercot_full1_year"]
    y0, y1 = n["nyiso_full0_year"], n["nyiso_full1_year"]
    ny_d = n["nyiso_full1_evening_pct"] - n["nyiso_full0_evening_pct"]
    ny_way = "rose" if ny_d > 1 else "fell" if ny_d < -1 else "held"
    ny_share = 100.0 * n["nyiso_full1_solar_mw"] / n["ercot_full1_solar_mw"]
    ny_read = (f" A grid with {fmt(ny_share, 0)} percent of Texas's counted solar moved the same way, which solar alone would not predict." if ny_d > 10 and ny_share < 25 else "")
    short_bits = "; ".join(f"{GRID[g]['words']} {fmt(n[f'{g}_full1_evening_pct'], 1)} percent in {n[f'{g}_full1_year']} and {fmt(n[f'{g}_this_evening_pct'], 1)} in {n[f'{g}_this_year']} to date, "
                           f"median hour {fmt(n[f'{g}_full1_median_hour'], 0)} and {fmt(n[f'{g}_this_median_hour'], 0)}" for g in short if n[f"{g}_full1_year"] is not None)
    why = (f"A solar-heavy grid is cheap at midday and dear after sunset, so the day's highest price should walk into the evening as panels go up. In Texas it did: "
           f"solar went from {fmt(n['ercot_full0_solar_mw'], 0)} MW at the end of {e0} to {fmt(n['ercot_full1_solar_mw'], 0)} MW at the end of {e1} (EIA-860M), the share of days "
           f"peaking between 17:00 and 21:59 from {fmt(n['ercot_full0_evening_pct'], 1)} to {fmt(n['ercot_full1_evening_pct'], 1)} percent, and the median peak hour from "
           f"{fmt(n['ercot_full0_median_hour'], 0)} to {fmt(n['ercot_full1_median_hour'], 0)}. New York City's zone is the comparison with little utility solar behind it "
           f"({fmt(n['nyiso_full0_solar_mw'], 0)} MW in {y0}, {fmt(n['nyiso_full1_solar_mw'], 0)} MW in {y1}, rooftops not counted): its evening share {ny_way} from "
           f"{fmt(n['nyiso_full0_evening_pct'], 1)} to {fmt(n['nyiso_full1_evening_pct'], 1)} percent and its median peak hour went from {fmt(n['nyiso_full0_median_hour'], 0)} to "
           f"{fmt(n['nyiso_full1_median_hour'], 0)}.{ny_read} {words_list(short)} have prices in the warehouse from September 2024 only, one full year each, so their panels are short and "
           f"compare {n[f'{short[0]}_full1_year'] if short else ''} with the year to date: evening share {short_bits}. California, with {fmt(n['caiso_full1_solar_mw'], 0)} MW of solar, "
           f"peaks most often at hour {fmt(n['caiso_full1_modal_hour'], 0)}: the hour's place depends on the hub and the season as well as on the panels. "
           "The card compares years; it does not separate solar from gas prices, load growth, weather or the batteries that now work the evening.")
    foot = ("Data: real-time prices, " + "; ".join(f"{g['words']}: {spans[g['grid']]['how']}, {spans[g['grid']]['first_day']} to {spans[g['grid']]['last_day']} "
                                                  f"({fmt(spans[g['grid']]['n_days'], 0)} local days, {spans[g['grid']]['tz']})" for g in GRIDS if g["grid"] in spans) +
            ". Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT); iso_hub_prices_history and iso_rtm_hub_prices (CAISO, ISO-NE, SPP); iso_zone_prices_history "
            f"(NYISO). A day's peak hour is the local clock hour with the highest mean of its intervals (the first hour on a tie); a day needs at least {meta['min_hours']} held "
            "hours; local time is the grid's own and daylight saving is handled by the time zone conversion (a 23-hour spring day and a 25-hour autumn day are days like any "
            "other). Per grid and year: the percent of days peaking in each hour, the median peak hour, the percent peaking 17:00 to 21:59 (evening) and 10:00 to 15:59 "
            f"(midday). A year is full with at least {FULL_DAYS} held days; a grid with one full year is compared with the year to date and labeled so. Solar: nameplate MW of "
            "Solar Photovoltaic generators with the grid's balancing authority code (ERCO, CISO, NYIS, ISNE, SWPP) operating at the end of the year, from EIA-860M's inventory of "
            "August 2026 (eia860m_operating_generators by operating_year, plus eia860m_retired_generators_all by retirement year); plants under 1 MW (rooftops) are not in "
            "EIA-860M, and units retired before the retired list begins are not counted. A year a grid's prices do not cover is not held and not filled. MISO is paused while "
            "its terms are reviewed and PJM needs a licensed source: neither is requested, neither is data here.")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"first_year": meta["first_year"], "min_hours": meta["min_hours"]},
        "inputs_words": {"grids": "ERCOT, CAISO, NYISO, ISO-NE, SPP", "first_year": str(meta["first_year"]), "min_hours": f"{meta['min_hours']} held hours a day"},
        "chart": chart(rows, n, meta),
        "callouts": [
            callout("ERCOT days peaking 17:00 to 21:59", str(e0), f"{fmt(n['ercot_full0_evening_pct'], 1)}%", str(e1), f"{fmt(n['ercot_full1_evening_pct'], 1)}%"),
            callout("NYISO days peaking 17:00 to 21:59", str(y0), f"{fmt(n['nyiso_full0_evening_pct'], 1)}%", str(y1), f"{fmt(n['nyiso_full1_evening_pct'], 1)}%"),
            callout(f"Solar fleet, end of {e1}", "ERCOT", f"{fmt(n['ercot_full1_solar_mw'], 0)} MW", "NYISO", f"{fmt(n['nyiso_full1_solar_mw'], 0)} MW"),
        ],
        "why": why, "footnote": foot, "numbers": n, "placeholders": PLACEHOLDERS, "supersedes": SUPERSEDES,
        "grid_words": {g: {"in_words": v[0], "caveat": v[1]} for g, v in said.items()},
        "source_line": "Source: ERCOT, CAISO OASIS, NYISO (P-4A), ISO-NE and SPP real-time prices; EIA-860M; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per grid, local year and hour of the day: the percent of the year's days whose highest hourly real-time price fell in that hour; "
                       "the year's days, median peak hour, percent of days peaking 17:00 to 21:59 and 10:00 to 15:59 (repeated on each hour row); solar MW at year end",
                       "A blank is a year the warehouse does not hold for that grid; MISO and PJM are not in the file (paused, and licensed). Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["year", "hour", "share_days_pct", "n_days", "median_peak_hour", "share_evening_pct", "share_midday_pct", "solar_mw_yearend"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's shares and hours from {CSV_NAME}.",
        "* The CSV begins with four comment lines: the names are on line 5 and the data from line 6.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(5) rowrange(6) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "sort grid year hour",
        "bysort grid year: egen modal_share = max(share_days_pct)",
        "gen modal_hour = hour if share_days_pct == modal_share",
        ["foreach v in median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend {",
         "    tabstat `v' if hour == 0, by(grid) statistics(mean min max) format(%9.1f)",
         "}"],
        "list grid year n_days median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend if hour == 0, sepby(grid) noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
