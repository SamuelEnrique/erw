"""Finding: "The peak hour moved" (session 174).

The hour of each day's highest real-time price, ERCOT and CAISO, by year 2019 to 2026, set against solar capacity.
For every local day the hourly mean real-time price is computed from the 15-minute settlement prices, the day's highest
hour is taken (the first hour on a tie; a day needs at least 20 held hours), and each year's days are counted by that
hour: the share of days peaking in each hour of the day, the median peak hour, the share of days peaking in the evening
(17:00 to 21:59) and at midday (10:00 to 15:59). Solar capacity is the nameplate MW of solar photovoltaic generators in
the grid's balancing authority that were operating at the end of each year, read from EIA-860M's inventory as it stands
(the August 2026 vintage: units operating now, by their operating year, plus units retired since, by their retirement
year).

Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT HB_HUBAVG, 15-minute, 2019 on), iso_hub_prices_history
and iso_rtm_hub_prices (CAISO TH_SP15_GEN-APND, 15-minute, from 2024-09-01 only: the warehouse holds no earlier CAISO
prices, so CAISO's earlier years are not held and not filled), eia860m_operating_generators and
eia860m_retired_generators_all (solar capacity by year).
"""

import os

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table, to_utc

NAME = "peak_hour_moved"
TITLE = "THE PEAK HOUR MOVED"
KIND = "visual"
INPUTS = {
    "first_year": {"label": "First year", "default": 2019, "choices": [2019, 2020, 2021]},
    "min_hours": {"label": "Hours a day must hold", "default": 20, "choices": [20, 24]},
}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_hub_prices_history", "eia860m_operating_generators",
          "eia860m_retired_generators_all"]
CSV_NAME = "erw_2026_peak_hour_solar.csv"
GRIDS = [
    # grid, words, timezone, EIA balancing authority code, how the hourly price is made
    ("ercot", "ERCOT", "America/Chicago", "ERCO", "HB_HUBAVG, the mean of the four 15-minute settlement point prices in the local hour"),
    ("caiso", "CAISO", "America/Los_Angeles", "CISO", "TH_SP15_GEN-APND, the mean of the four 15-minute interval means in the local hour"),
]
EVENING = (17, 21)   # 17:00 to 21:59 local
MIDDAY = (10, 15)    # 10:00 to 15:59 local


def grid_rows(grid, first_year, in_dir):
    if grid == "ercot":
        h = read_table("ercot_all_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node", "year"],
                       keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_HUBAVG") & (c["year"].astype(int) >= first_year - 1))
        live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == "HB_HUBAVG"))
    elif grid == "caiso":
        h = read_table("iso_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node"],
                       keep=lambda c: (c["market"] == "caiso_rtm") & (c["node"] == "TH_SP15_GEN-APND"))
        live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == "caiso_rtm") & (c["node"] == "TH_SP15_GEN-APND"))
    else:
        raise ValueError(grid)
    d = pd.concat([h[["ts_utc", "value"]], live[["ts_utc", "value"]]]).drop_duplicates("ts_utc")
    if d.empty:
        raise NoData(f"no real-time rows for {grid}")
    return d


def daily_peak_hours(d, tz, min_hours):
    """15-minute rows -> one row per local day: the hour (0 to 23) of the day's highest hourly mean price."""
    d = d.copy()
    d["value"] = d["value"].astype(float)
    d["hour_utc"] = to_utc(d["ts_utc"]).dt.floor("h")
    h = d.groupby("hour_utc", as_index=False)["value"].mean()
    h["local"] = h["hour_utc"].dt.tz_convert(tz)
    h["day"] = h["local"].dt.strftime("%Y-%m-%d")
    h["hour"] = h["local"].dt.hour
    out = []
    for day, g in h.groupby("day"):
        if len(g) < min_hours:
            continue
        g = g.sort_values("hour")
        top = g.loc[g["value"].idxmax()]   # the first hour on a tie: idxmax takes the first maximum
        out.append({"day": day, "year": int(day[:4]), "peak_hour": int(top["hour"]), "peak_price": float(top["value"]), "n_hours": int(len(g))})
    return pd.DataFrame(out)


def solar_mw_by_year(ba, years, in_dir):
    """Nameplate MW of solar photovoltaic units in the balancing authority operating at the end of each year, from the
    inventory as it stands: operating units by operating_year, plus units retired since by their retirement year."""
    op = read_table("eia860m_operating_generators", in_dir, usecols=["balancing_authority", "technology", "nameplate_mw", "operating_year"],
                    keep=lambda c: (c["balancing_authority"] == ba) & (c["technology"] == "Solar Photovoltaic"))
    ret = read_table("eia860m_retired_generators_all", in_dir, usecols=["balancing_authority", "technology", "nameplate_mw", "operating_year", "retirement_date"],
                     keep=lambda c: (c["balancing_authority"] == ba) & (c["technology"] == "Solar Photovoltaic"))
    for f in (op, ret):
        f["mw"] = pd.to_numeric(f["nameplate_mw"], errors="coerce").fillna(0.0)
        f["oy"] = pd.to_numeric(f["operating_year"], errors="coerce")
    ret["ry"] = pd.to_numeric(ret["retirement_date"].str[:4], errors="coerce")
    out = {}
    for y in years:
        a = float(op.loc[op["oy"] <= y, "mw"].sum())
        b = float(ret.loc[(ret["oy"] <= y) & (ret["ry"] > y), "mw"].sum())
        out[y] = a + b
    return out


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    min_hours = int(params.get("min_hours", 20))
    this_year = pd.Timestamp.now(tz="UTC").year
    years = list(range(first_year, this_year + 1))
    rows, meta = [], {"first_year": first_year, "min_hours": min_hours, "spans": {}, "missing": []}
    for grid, words, tz, ba, how in GRIDS:
        solar = solar_mw_by_year(ba, years, in_dir)
        try:
            d = grid_rows(grid, first_year, in_dir)
            days = daily_peak_hours(d, tz, min_hours)
            days = days[days["year"] >= first_year]
        except NoData as exc:
            meta["missing"].append({"grid": grid, "reason": str(exc)})
            days = pd.DataFrame(columns=["day", "year", "peak_hour", "peak_price", "n_hours"])
        if len(days):
            meta["spans"][grid] = {"first_day": days["day"].min(), "last_day": days["day"].max(), "n_days": int(len(days)), "how": how, "tz": tz}
        for y in years:
            g = days[days["year"] == y]
            n = int(len(g))
            counts = g["peak_hour"].value_counts() if n else pd.Series(dtype=int)
            med = float(np.median(g["peak_hour"])) if n else None
            evening = float(g["peak_hour"].between(*EVENING).mean() * 100) if n else None
            midday = float(g["peak_hour"].between(*MIDDAY).mean() * 100) if n else None
            for hr in range(24):
                rows.append({"grid": grid, "year": y, "hour": hr,
                             "share_days_pct": float(counts.get(hr, 0) / n * 100) if n else None,
                             "n_days": n if n else None, "median_peak_hour": med, "share_evening_pct": evening, "share_midday_pct": midday,
                             "solar_mw_yearend": solar[y]})
    return rows, meta


def numbers_from_rows(rows, params=None):
    years = sorted({r["year"] for r in rows})
    first, this_year = years[0], years[-1]
    last_full = max(y for y in years if y < this_year)
    def year_row(grid, y):
        return next((r for r in rows if r["grid"] == grid and r["year"] == y and r["hour"] == 0), None)
    def held_years(grid):
        return [y for y in years if (year_row(grid, y) or {}).get("n_days")]
    n = {"first_year": first, "last_full_year": last_full, "this_year": this_year}
    for grid, _, _, _, _ in GRIDS:
        hy = held_years(grid)
        n[f"{grid}_first_held_year"] = hy[0] if hy else None
        n[f"{grid}_last_full_held_year"] = max((y for y in hy if y < this_year), default=None)
        for tag, y in (("first", n[f"{grid}_first_held_year"]), ("last", n[f"{grid}_last_full_held_year"]), ("this", this_year if this_year in hy else None)):
            r = year_row(grid, y) if y is not None else None
            n[f"{grid}_{tag}_year"] = y
            n[f"{grid}_{tag}_median_hour"] = r["median_peak_hour"] if r else None
            n[f"{grid}_{tag}_evening_pct"] = r["share_evening_pct"] if r else None
            n[f"{grid}_{tag}_midday_pct"] = r["share_midday_pct"] if r else None
            n[f"{grid}_{tag}_days"] = r["n_days"] if r else None
            n[f"{grid}_{tag}_solar_mw"] = r["solar_mw_yearend"] if r else None
            if r:
                top = max((x for x in rows if x["grid"] == grid and x["year"] == y), key=lambda x: x["share_days_pct"] or 0)
                n[f"{grid}_{tag}_modal_hour"] = top["hour"]
                n[f"{grid}_{tag}_modal_pct"] = top["share_days_pct"]
            else:
                n[f"{grid}_{tag}_modal_hour"] = n[f"{grid}_{tag}_modal_pct"] = None
        n[f"{grid}_solar_mw_first_year"] = (year_row(grid, first) or {}).get("solar_mw_yearend")
        n[f"{grid}_solar_mw_last_full_year"] = (year_row(grid, last_full) or {}).get("solar_mw_yearend")
    return n


def chart(rows, n):
    x = [f"{h:02d}" for h in range(24)]
    series = []
    for grid, words, _, _, _ in GRIDS:
        for tag in ("first", "last", "this"):
            y = n.get(f"{grid}_{tag}_year")
            if y is None or (tag == "this" and grid == "ercot"):
                continue
            if tag == "first" and (n.get(f"{grid}_first_days") or 0) < 300:
                continue   # a partial first year (CAISO is held from September 2024) is not a line
            vals = [next((r["share_days_pct"] for r in rows if r["grid"] == grid and r["year"] == y and r["hour"] == h), None) for h in range(24)]
            label = f"{words} {y}" + (" (to date)" if y == n["this_year"] else "")
            if any(s["name"] == label for s in series):
                continue
            series.append({"name": label, "type": "line", "unit": "percent of days", "values": vals,
                           "days": n.get(f"{grid}_{tag}_days")})
    return {"kind": "lines", "x": x, "x_label": "Hour of the day (local) in which the day's highest real-time price fell",
            "series": series, "y_left_label": "percent of the year's days", "value_suffix": "%", "decimals": 1}


def card(rows, params, meta):
    n = numbers_from_rows(rows, params)
    e0, e1 = n["ercot_first_year"], n["ercot_last_year"]
    ev0, ev1 = n["ercot_first_evening_pct"], n["ercot_last_evening_pct"]
    m0, m1 = n["ercot_first_median_hour"], n["ercot_last_median_hour"]
    s0, s1 = n["ercot_first_solar_mw"], n["ercot_last_solar_mw"]
    if ev1 is not None and ev0 is not None and ev1 > ev0 + 10 and m1 is not None and m0 is not None and m1 > m0:
        sub = "In Texas the day's dearest hour walked into the evening as solar took the midday"
    elif ev1 is not None and ev0 is not None and ev1 < ev0 - 10:
        sub = "In Texas the day's dearest hour moved earlier, not later, as solar grew"
    else:
        sub = "In Texas the day's dearest hour barely moved while solar capacity multiplied"
    c_last = n["caiso_last_year"]
    spans = meta.get("spans", {})
    caiso_words = ""
    if c_last is not None:
        caiso_words = (f" CAISO's prices are held from {spans.get('caiso', {}).get('first_day', 'not held')} only, so its first full year is {c_last}: "
                       f"the median peak hour is {fmt(n['caiso_last_median_hour'], 0)} and {fmt(n['caiso_last_evening_pct'], 1)} percent of days peak in the evening, "
                       f"with {fmt(n['caiso_last_solar_mw'], 0)} MW of solar in the balancing authority.")
    why = (f"ERCOT's solar fleet went from {fmt(s0, 0)} MW at the end of {e0} to {fmt(s1, 0)} MW at the end of {e1} (EIA-860M, units operating today by their operating year). "
           f"The hour of the day's highest real-time price moved with it: the median peak hour went from {fmt(m0, 0)} to {fmt(m1, 0)}, the share of days whose dearest hour fell "
           f"between 17:00 and 21:59 from {fmt(ev0, 1)} to {fmt(ev1, 1)} percent, and the share peaking at midday (10:00 to 15:59) from {fmt(n['ercot_first_midday_pct'], 1)} to "
           f"{fmt(n['ercot_last_midday_pct'], 1)} percent ({fmt(n['ercot_first_days'], 0)} and {fmt(n['ercot_last_days'], 0)} days). The most common peak hour was "
           f"{fmt(n['ercot_first_modal_hour'], 0)} in {e0} ({fmt(n['ercot_first_modal_pct'], 1)} percent of days) and {fmt(n['ercot_last_modal_hour'], 0)} in {e1} "
           f"({fmt(n['ercot_last_modal_pct'], 1)} percent).{caiso_words} A later peak is what a solar-heavy grid does to prices: the midday is cheap, the ramp after "
           "sunset is dear. The chart compares the years; it does not separate solar from gas prices, load growth or the batteries that now arbitrage the evening.")
    foot = (f"Data: real-time prices, 15-minute, " + "; ".join(f"{w}: {spans[g]['how']}, {spans[g]['first_day']} to {spans[g]['last_day']} ({fmt(spans[g]['n_days'], 0)} local days, {spans[g]['tz']})"
                                                               for g, w, _, _, _ in GRIDS if g in spans) +
            f". A day's peak hour is the local clock hour with the highest mean of its intervals (the first hour on a tie); a day needs at least {meta['min_hours']} held hours. "
            "Per grid and year: the percent of days peaking in each hour, the median peak hour, the percent peaking 17:00 to 21:59 (evening) and 10:00 to 15:59 (midday). "
            "Solar: nameplate MW of Solar Photovoltaic generators with the grid's balancing authority code (ERCO, CISO) operating at the end of the year, from EIA-860M's "
            "inventory of August 2026 (eia860m_operating_generators by operating_year, plus eia860m_retired_generators_all by retirement year); units retired before the "
            "inventory's retired list begins are not counted. A year a grid's prices do not cover is not held and not filled.")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"first_year": meta["first_year"], "min_hours": meta["min_hours"]},
        "inputs_words": {"first_year": str(meta["first_year"]), "min_hours": f"{meta['min_hours']} held hours a day"},
        "chart": chart(rows, n),
        "callouts": [
            callout("ERCOT median peak hour (local)", str(e0), f"hour {fmt(m0, 0)}", str(e1), f"hour {fmt(m1, 0)}"),
            callout("ERCOT days peaking 17:00 to 21:59", str(e0), f"{fmt(ev0, 1)}%", str(e1), f"{fmt(ev1, 1)}%"),
            callout("ERCOT solar fleet, year end", str(e0), f"{fmt(s0, 0)} MW", str(e1), f"{fmt(s1, 0)} MW"),
        ],
        "why": why, "footnote": foot, "numbers": n,
        "source_line": "Source: ERCOT and CAISO OASIS real-time prices; EIA-860M; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per grid, local year and hour of the day: the percent of the year's days whose highest hourly real-time price fell in that hour; "
                       "the year's days, median peak hour, percent of days peaking 17:00 to 21:59 and 10:00 to 15:59 (repeated on each hour row); solar MW at year end",
                       "A blank is a year the warehouse does not hold for that grid. Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["year", "hour", "share_days_pct", "n_days", "median_peak_hour", "share_evening_pct", "share_midday_pct", "solar_mw_yearend"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's shares and hours from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "sort grid year hour",
        "bysort grid year: egen modal_share = max(share_days_pct)",
        "gen modal_hour = hour if share_days_pct == modal_share",
        ["foreach v in median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend {",
         "    tabstat `v' if hour == 0, by(grid) statistics(mean min max) format(%9.1f)",
         "}"],
        "list grid year median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend if hour == 0, sepby(grid) noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
