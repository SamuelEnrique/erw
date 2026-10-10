"""Finding: "Negative prices march west" (session 174).

Negative-price hours by hub and year: ERCOT's West hub against Houston (with North and South beside them), 2019 to
2026, plus SPP's North hub for the years the warehouse holds it (from September 2024). An hour is negative when the mean
of its 15-minute real-time settlement prices is below zero; the count of such hours, their share of the year's held
hours, and the count of negative 15-minute intervals are reported per hub and year. A year a hub's history does not
cover is not held and not filled.

Tables: ercot_all_hub_prices_history and iso_rtm_hub_prices (ERCOT hubs, 15-minute), iso_hub_prices_history and
iso_rtm_hub_prices (SPP North hub, 15-minute, from 2024-09-01).
"""

import os

import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table, to_utc

NAME = "negative_prices_west"
TITLE = "NEGATIVE PRICES MARCH WEST"
KIND = "visual"
INPUTS = {
    "first_year": {"label": "First year", "default": 2019, "choices": [2019, 2020, 2021]},
    "threshold": {"label": "Price counted as negative (USD/MWh, below)", "default": 0, "choices": [0, -10, -20]},
}
TABLES = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_hub_prices_history"]
CSV_NAME = "erw_2026_negative_hours_hubs.csv"
HUBS = [
    # key, grid, market, node, words, timezone
    ("ercot_west", "ercot", "ercot_rtm", "HB_WEST", "ERCOT West", "America/Chicago"),
    ("ercot_houston", "ercot", "ercot_rtm", "HB_HOUSTON", "ERCOT Houston", "America/Chicago"),
    ("ercot_north", "ercot", "ercot_rtm", "HB_NORTH", "ERCOT North", "America/Chicago"),
    ("ercot_south", "ercot", "ercot_rtm", "HB_SOUTH", "ERCOT South", "America/Chicago"),
    ("spp_north", "spp", "spp_rtm", "SPPNORTH_HUB", "SPP North", "America/Chicago"),
]


def hub_rows(grid, market, node, first_year, in_dir):
    if grid == "ercot":
        h = read_table("ercot_all_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node", "year"],
                       keep=lambda c: (c["market"] == market) & (c["node"] == node) & (c["year"].astype(int) >= first_year - 1))
    else:
        h = read_table("iso_hub_prices_history", in_dir, usecols=["ts_utc", "value", "market", "node"],
                       keep=lambda c: (c["market"] == market) & (c["node"] == node))
    live = read_table("iso_rtm_hub_prices", in_dir, usecols=["ts_utc", "value", "market", "node"],
                      keep=lambda c: (c["market"] == market) & (c["node"] == node))
    d = pd.concat([h[["ts_utc", "value"]], live[["ts_utc", "value"]]]).drop_duplicates("ts_utc")
    if d.empty:
        raise NoData(f"no real-time rows for {node}")
    return d


def compute(params, in_dir=None):
    first_year = int(params.get("first_year", 2019))
    thr = float(params.get("threshold", 0))
    this_year = pd.Timestamp.now(tz="UTC").year
    years = list(range(first_year, this_year + 1))
    rows, meta = [], {"first_year": first_year, "threshold": thr, "spans": {}, "missing": []}
    for key, grid, market, node, words, tz in HUBS:
        try:
            d = hub_rows(grid, market, node, first_year, in_dir)
        except NoData as exc:
            meta["missing"].append({"hub": key, "reason": str(exc)})
            for y in years:
                rows.append({"hub": key, "words": words, "year": y, "n_hours": None, "negative_hours": None, "share_pct": None,
                             "negative_intervals": None, "n_intervals": None, "first_day": None, "last_day": None})
            continue
        d = d.copy()
        d["value"] = d["value"].astype(float)
        t = to_utc(d["ts_utc"])
        d["hour_utc"] = t.dt.floor("h")
        d["year"] = t.dt.tz_convert(tz).dt.year
        d = d[d["year"] >= first_year]
        meta["spans"][key] = {"first": t.min().tz_convert(tz).strftime("%Y-%m-%d"), "last": t.max().tz_convert(tz).strftime("%Y-%m-%d"),
                              "n_intervals": int(len(d)), "node": node, "tz": tz}
        h = d.groupby("hour_utc", as_index=False)["value"].mean()
        h["year"] = h["hour_utc"].dt.tz_convert(tz).dt.year
        by_year_h = {y: g for y, g in h.groupby("year")}
        by_year_i = {y: g for y, g in d.groupby("year")}
        for y in years:
            g, gi = by_year_h.get(y), by_year_i.get(y)
            if g is None or not len(g):
                rows.append({"hub": key, "words": words, "year": y, "n_hours": None, "negative_hours": None, "share_pct": None,
                             "negative_intervals": None, "n_intervals": None, "first_day": None, "last_day": None})
                continue
            neg = int((g["value"] < thr).sum())
            rows.append({"hub": key, "words": words, "year": y, "n_hours": int(len(g)), "negative_hours": neg,
                         "share_pct": float(neg / len(g) * 100), "negative_intervals": int((gi["value"] < thr).sum()), "n_intervals": int(len(gi)),
                         "first_day": gi["hour_utc"].min().tz_convert(tz).strftime("%Y-%m-%d"), "last_day": gi["hour_utc"].max().tz_convert(tz).strftime("%Y-%m-%d")})
    return rows, meta


def numbers_from_rows(rows, params=None):
    years = sorted({r["year"] for r in rows})
    first, this_year = years[0], years[-1]
    last_full = max(y for y in years if y < this_year)
    def at(hub, y, k="negative_hours"):
        return next((r[k] for r in rows if r["hub"] == hub and r["year"] == y), None)
    n = {"first_year": first, "last_full_year": last_full, "this_year": this_year}
    for key, _, _, _, _, _ in HUBS:
        held = [r["year"] for r in rows if r["hub"] == key and r["negative_hours"] is not None]
        n[f"{key}_first_held_year"] = held[0] if held else None
        for tag, y in (("first", first), ("last", last_full), ("this", this_year)):
            n[f"{key}_{tag}"] = at(key, y)
            n[f"{key}_{tag}_share"] = at(key, y, "share_pct")
            n[f"{key}_{tag}_hours"] = at(key, y, "n_hours")
            n[f"{key}_{tag}_intervals"] = at(key, y, "negative_intervals")
        peak = max((r for r in rows if r["hub"] == key and r["negative_hours"] is not None and r["year"] < this_year), key=lambda r: r["negative_hours"], default=None)
        n[f"{key}_peak_year"] = peak["year"] if peak else None
        n[f"{key}_peak"] = peak["negative_hours"] if peak else None
    w1, h1 = n["ercot_west_last"], n["ercot_houston_last"]
    n["west_over_houston_last"] = (w1 / h1) if (w1 and h1) else None
    return n


def chart(rows):
    years = sorted({r["year"] for r in rows})
    return {"kind": "lines", "x": [str(y) for y in years], "x_label": "Year (local)",
            "series": [{"name": words, "type": "line", "unit": "hours", "values": [next((r["negative_hours"] for r in rows if r["hub"] == key and r["year"] == y), None) for y in years],
                        "hours": [next((r["n_hours"] for r in rows if r["hub"] == key and r["year"] == y), None) for y in years]}
                       for key, _, _, _, words, _ in HUBS],
            "y_left_label": "hours with a negative mean real-time price", "decimals": 0}


def card(rows, params, meta):
    n = numbers_from_rows(rows, params)
    y0, y1, yt = n["first_year"], n["last_full_year"], n["this_year"]
    w0, w1, h0, h1 = n["ercot_west_first"], n["ercot_west_last"], n["ercot_houston_first"], n["ercot_houston_last"]
    thr = meta["threshold"]
    if w1 is not None and h1 is not None and w1 > 2 * max(h1, 1) and w1 > (w0 or 0):
        sub = "West Texas clears below zero far more often than Houston, and the gap has grown"
    elif w1 is not None and w0 is not None and w1 < w0:
        sub = "West Texas's negative hours have fallen from their peak; Houston never had many"
    else:
        sub = "Negative hours stay a western affair; Houston barely sees them"
    spp_words = ""
    if n["spp_north_last"] is not None:
        spp_words = (f" SPP's North hub, held from {meta['spans'].get('spp_north', {}).get('first', 'not held')}, had {fmt(n['spp_north_last'], 0)} negative hours in {y1} "
                     f"({fmt(n['spp_north_last_share'], 1)} percent of {fmt(n['spp_north_last_hours'], 0)} held hours).")
    this_words = ""
    if n["ercot_west_this"] is not None:
        this_words = f" So far in {yt}: West {fmt(n['ercot_west_this'], 0)} hours, Houston {fmt(n['ercot_houston_this'], 0)}, of {fmt(n['ercot_west_this_hours'], 0)} held."
    why = (f"ERCOT's West hub had {fmt(w0, 0)} hours with a negative mean real-time price in {y0} and {fmt(w1, 0)} in {y1} "
           f"({fmt(n['ercot_west_first_share'], 1)} and {fmt(n['ercot_west_last_share'], 1)} percent of the year's held hours); Houston had {fmt(h0, 0)} and {fmt(h1, 0)}. "
           f"West's worst year was {n['ercot_west_peak_year']} with {fmt(n['ercot_west_peak'], 0)} hours; North had {fmt(n['ercot_north_last'], 0)} in {y1} and South "
           f"{fmt(n['ercot_south_last'], 0)}. Counted by 15-minute interval West's {y1} figure is {fmt(n['ercot_west_last_intervals'], 0)} intervals.{spp_words}{this_words} "
           "A negative hour is wind or solar paid to run (tax credits, contracts) behind a line that cannot carry it east; the hubs name where that happens. The count "
           "says how often, not what it cost anyone.")
    spans = meta.get("spans", {})
    foot = (f"Data: real-time settlement point prices, 15-minute: " + "; ".join(f"{w}: {spans[k]['node']}, {spans[k]['first']} to {spans[k]['last']} ({fmt(spans[k]['n_intervals'], 0)} intervals, {spans[k]['tz']})"
                                                                               for k, _, _, _, w, _ in HUBS if k in spans) +
            f". An hour is the local clock hour; its price is the mean of its held intervals; it counts as negative when that mean is below {fmt(thr, 0)} USD/MWh "
            "(the threshold input); the share is of the year's held hours; the interval count is of intervals below the same threshold. The ERCOT hubs' history runs "
            "from 2015 (ercot_all_hub_prices_history, ERCOT NP6-785-ER and NP6-905-CD) and the live table from 2026-08-26; SPP North from 2024-09-01 "
            "(iso_hub_prices_history, SPP's RTBM settlement prices). A year a hub does not cover is not held and not filled. No cap, no exclusion.")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"first_year": meta["first_year"], "threshold": thr},
        "inputs_words": {"first_year": str(meta["first_year"]), "threshold": f"below {fmt(thr, 0)} USD/MWh"},
        "chart": chart(rows),
        "callouts": [
            callout("ERCOT West negative hours", str(y0), f"{fmt(w0, 0)} hours", str(y1), f"{fmt(w1, 0)} hours"),
            callout("ERCOT Houston negative hours", str(y0), f"{fmt(h0, 0)} hours", str(y1), f"{fmt(h1, 0)} hours"),
            callout(f"West's share of held hours", str(y0), f"{fmt(n['ercot_west_first_share'], 1)}%", str(y1), f"{fmt(n['ercot_west_last_share'], 1)}%"),
        ],
        "why": why, "footnote": foot, "numbers": n,
        "source_line": "Source: ERCOT real-time settlement point prices (NP6-785-ER, NP6-905-CD); SPP RTBM; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per hub and local year: held hours, hours with a negative mean real-time price, their share, negative 15-minute intervals and held intervals, first and last day held",
                       "A blank is a year the warehouse does not hold for that hub. Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["year", "n_hours", "negative_hours", "share_pct", "negative_intervals", "n_intervals"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's counts from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "sort hub year",
        ["foreach v in negative_hours share_pct {",
         "    tabstat `v', by(hub) statistics(mean min max) format(%9.1f)",
         "}"],
        "list hub year n_hours negative_hours share_pct, sepby(hub) noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
