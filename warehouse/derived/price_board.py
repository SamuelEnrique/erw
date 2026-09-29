#!/usr/bin/env python3
"""Price board v2: the four derived tables behind the site's /board (session 30, Part A; tool 2).

Energy Research Warehouse (ERW). Reads the ERW's own tables and writes, with their method in
docs/methods/price_board.md:

  price_board_latest       every hub and zone of the six public ISOs, day-ahead and real-time: the daily mean of each
                           complete operating day of the last 30, and on the latest one the previous day, the change in
                           USD/MWh and percent, the 7- and 30-day averages, the 30-day minimum and maximum, the newest
                           interval, and (day-ahead rows) day-ahead minus real-time. Also the count of intervals the ERW
                           holds for each hub and market in the last 30 days, so a missing series shows as 0.
  price_board_peak_offpeak the main hub of each ISO, day-ahead and real-time: peak and off-peak means per complete
                           operating day, last 90 days (as far as the tables reach), with each ISO's peak definition;
                           and ERCOT's HB_HUBAVG per operating year since 2015 (the history): all-hours, peak and
                           off-peak means and peak minus off-peak.
  price_board_spreads      daily, last 365 days: Henry Hub, and per ISO main hub the spark spread at a heat rate of
                           7.0 MMBtu/MWh (the one labelled assumption) and the implied heat rate, both on the day-ahead
                           daily mean; Brent minus WTI.
  price_board_carbon       the latest CARB and RGGI auction results the ERW holds, with the auction before them.
                           License internal, as its inputs (CARB and RGGI terms are unconfirmed).

    python warehouse/derived/price_board.py

Local operating days: ERCOT and SPP America/Chicago, CAISO America/Los_Angeles, NYISO and ISO-NE America/New_York, MISO
EST (fixed UTC-5, as MISO publishes). A day counts only when every interval of it is present (24 hours, 23 or 25 on
the daylight saving days; 96, 92 or 100 fifteen-minute intervals). Nothing is filled or interpolated. The large ERCOT
history (ercot_all_hub_prices_history, 3 million rows) is streamed once with pyarrow, keeping HB_HUBAVG only.
"""

import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md"
HEAT_RATE = 7.0  # MMBtu/MWh: the one labelled assumption (spark spread)
AI = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]
TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "nyiso": "America/New_York",
      "miso": "EST", "spp": "America/Chicago", "isone": "America/New_York"}
LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO", "spp": "SPP", "isone": "ISO-NE"}
MAIN = {"ercot": "HB_HUBAVG", "caiso": "TH_SP15_GEN-APND", "nyiso": "N.Y.C.", "miso": "INDIANA.HUB",
        "spp": "SPPNORTH_HUB", "isone": ".H.INTERNAL_HUB"}  # site/data/markets.json, "main"
# (table, market) of each ISO's day-ahead and real-time prices. ISO-NE real time: the hourly final LMPs.
TABLES = {
    ("ercot", "dam"): ("iso_dam_hub_prices", "ercot_dam"), ("ercot", "rtm"): ("iso_rtm_hub_prices", "ercot_rtm"),
    ("caiso", "dam"): ("iso_dam_hub_prices", "caiso_dam"), ("caiso", "rtm"): ("iso_rtm_hub_prices", "caiso_rtm"),
    ("miso", "dam"): ("iso_dam_hub_prices", "miso_dam"), ("miso", "rtm"): ("iso_rtm_hub_prices", "miso_rtm"),
    ("spp", "dam"): ("iso_dam_hub_prices", "spp_dam"), ("spp", "rtm"): ("iso_rtm_hub_prices", "spp_rtm"),
    ("nyiso", "dam"): ("nyiso_dam_zone_prices", "nyiso_dam"), ("nyiso", "rtm"): ("nyiso_rtm_zone_prices", "nyiso_rtm"),
    ("isone", "dam"): ("isone_dam_zone_prices", "isone_dam"),
    ("isone", "rtm"): ("isone_rtm_zone_prices_hourly", "isone_rtm"),
}
HISTORY = "ercot_all_hub_prices_history"
# Peak: hours ending 7 to 22 (hour beginning 06:00 to 21:59 local), on peak days, NERC holidays excluded.
# The Eastern and Texas convention (5x16) is Monday to Friday; CAISO's, the Western (WECC) one (6x16), Monday to Saturday.
PEAK_DAYS = {"caiso": {0, 1, 2, 3, 4, 5}}
PEAK_DAYS_DEFAULT = {0, 1, 2, 3, 4}
PEAK_HOURS = range(6, 22)  # hour beginning, local
SERIES_COLS = ip.SERIES_COLS
COLS = SERIES_COLS  # the derived tables use the series shape as it is
SPREAD_COLS = SERIES_COLS + ["x_gas_date"]


def nerc_holidays(years):
    """NERC off-peak holidays: New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving and Christmas;
    one on a Sunday moves to the Monday after (none moves off a Saturday)."""
    out = set()
    for y in years:
        days = [dt.date(y, 1, 1), dt.date(y, 7, 4), dt.date(y, 12, 25)]
        may31 = dt.date(y, 5, 31)
        days.append(may31 - dt.timedelta(days=may31.weekday()))  # last Monday of May
        sep1 = dt.date(y, 9, 1)
        days.append(sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7))  # first Monday of September
        nov1 = dt.date(y, 11, 1)
        days.append(nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21))  # fourth Thursday of November
        for d in days:
            out.add(d + dt.timedelta(days=1) if d.weekday() == 6 else d)
    return out


def read_table(name, market=None, node=None, since=None):
    """A series table of warehouse/output as a frame (strings, value float), streamed in batches and filtered as it is
    read (market, node, ts_utc >= since), so a large table is never held whole."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = 0
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    cols = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node"]
    types = {c: pa.string() for c in cols}
    types["value"] = pa.float64()
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=n, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts = []
    for batch in reader:
        mask = None
        for col, want in (("market", market), ("node", node)):
            if want is not None:
                m = pc.equal(batch.column(col), want)
                mask = m if mask is None else pc.and_(mask, m)
        if since is not None:
            m = pc.greater_equal(batch.column("ts_utc"), since)
            mask = m if mask is None else pc.and_(mask, m)
        t = pa.Table.from_batches([batch])
        parts.append(t if mask is None else t.filter(mask))
    tbl = pa.concat_tables(parts) if parts else None
    if tbl is None:
        df = pd.DataFrame(columns=cols)
    else:
        # repeated strings (entity, market, node, ...) become shared objects, not one copy per row: the ERCOT history
        # keeps about half a million rows of HB_HUBAVG
        df = tbl.to_pandas(strings_to_categorical=True)
        for c in df.columns:
            if isinstance(df[c].dtype, pd.CategoricalDtype):
                df[c] = df[c].astype(object)
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, format="%Y-%m-%dT%H:%M:%SZ")
    return df


def step_of(freq):
    return {"PT1H": pd.Timedelta(hours=1), "PT15M": pd.Timedelta(minutes=15), "PT5M": pd.Timedelta(minutes=5)}[freq]


def complete_days(df, tz):
    """Daily means of complete local operating days of one node and market: {date: (mean, n, local start)}; with
    the intervals of each complete day for the peak split."""
    if df.empty:
        return pd.DataFrame(columns=["day", "mean", "n"]), df.assign(day=[])
    freq = df["freq"].iloc[0]
    step = step_of(freq)
    local = df["ts"].dt.tz_convert(tz)
    d = df.assign(day=local.dt.date, local=local)
    g = d.groupby("day")["value"].agg(["mean", "size"]).reset_index().rename(columns={"size": "n"})
    starts = pd.to_datetime(g["day"]).dt.tz_localize(tz)
    ends = (pd.to_datetime(g["day"]) + pd.Timedelta(days=1)).dt.tz_localize(tz)
    g["expected"] = ((ends - starts) / step).astype(int)
    full = g[g["n"] == g["expected"]]
    return full[["day", "mean", "n"]].reset_index(drop=True), d[d["day"].isin(set(full["day"]))]


def row(entity, variable, ts, value, unit, freq, geo, market, node, retrieved):
    return {"entity": entity, "variable": variable, "ts_utc": ts, "value": value, "unit": unit, "freq": freq,
            "geo": geo, "market": market, "node": node, "source": "erw:price_board", "source_url": METHOD_URL,
            "retrieved_at": retrieved, "vintage": ""}


def day_ts(d):
    return f"{d.isoformat()}T00:00:00Z"


def r4(v):
    """Four decimals, half up on the value as written (Python's round() would round half to even)."""
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def build_latest(prices, retrieved, log):
    rows = []
    for (iso, mk), df in prices.items():
        tz = TZ[iso]
        for node, g in df.groupby("node"):
            g = g.sort_values("ts")
            entity, geo, market = g["entity"].iloc[0], g["geo"].iloc[0], g["market"].iloc[0]
            days, _ = complete_days(g, tz)
            last_ts = g["ts"].max()
            n30 = int((g["ts"] > last_ts - pd.Timedelta(days=30)).sum())
            base = dict(geo=geo, market=market, node=node, retrieved=retrieved)
            rows.append(row(entity, "intervals_30d", ip.utc_iso(last_ts), n30, "count", g["freq"].iloc[0], **base))
            newest = g.iloc[-1]
            rows.append(row(entity, "latest_interval", newest["ts_utc"], r4(newest["value"]), "USD/MWh",
                            newest["freq"], **base))
            if days.empty:
                continue
            latest_day = days["day"].max()
            win = days[days["day"] > latest_day - dt.timedelta(days=30)]
            for r in win.itertuples():
                rows.append(row(entity, "daily_mean", day_ts(r.day), r4(r.mean), "USD/MWh", "P1D", **base))
            t = day_ts(latest_day)
            cur = float(win.loc[win["day"] == latest_day, "mean"].iloc[0])
            rows.append(row(entity, "latest_day_mean", t, r4(cur), "USD/MWh", "P1D", **base))
            prev = win[win["day"] == latest_day - dt.timedelta(days=1)]
            if len(prev):  # the previous operating day, only when it is complete: no gap is bridged
                p = float(prev["mean"].iloc[0])
                rows.append(row(entity, "previous_day_mean", day_ts(latest_day - dt.timedelta(days=1)), r4(p), "USD/MWh",
                                "P1D", **base))
                rows.append(row(entity, "day_change", t, r4(cur - p), "USD/MWh", "P1D", **base))
                if p != 0:
                    rows.append(row(entity, "day_change_pct", t, r4(100 * (cur - p) / abs(p)), "pct", "P1D", **base))
            w7 = win[win["day"] > latest_day - dt.timedelta(days=7)]
            rows += [row(entity, "avg_7d", t, r4(w7["mean"].mean()), "USD/MWh", "P1D", **base),
                     row(entity, "days_7d", t, int(len(w7)), "count", "P1D", **base),
                     row(entity, "avg_30d", t, r4(win["mean"].mean()), "USD/MWh", "P1D", **base),
                     row(entity, "days_30d", t, int(len(win)), "count", "P1D", **base),
                     row(entity, "min_30d", t, r4(win["mean"].min()), "USD/MWh", "P1D", **base),
                     row(entity, "max_30d", t, r4(win["mean"].max()), "USD/MWh", "P1D", **base)]
    out = market_prefix(pd.DataFrame(rows))
    # day-ahead minus real-time: on the latest day both markets of a node have complete, on the day-ahead row
    dm = out[out["variable"].isin(["da_daily_mean", "rt_daily_mean"])]
    for iso in AI:
        da, rt = TABLES[(iso, "dam")][1], TABLES[(iso, "rtm")][1]
        a = dm[dm["market"] == da].set_index(["node", "ts_utc"])["value"]
        b = dm[dm["market"] == rt].set_index(["node", "ts_utc"])["value"]
        both = a.index.intersection(b.index)
        if not len(both):
            continue
        j = pd.DataFrame({"da": a[both], "rt": b[both]}).reset_index()
        last = j.sort_values("ts_utc").groupby("node").tail(1)
        ref = out[(out["market"] == da) & (out["variable"] == "da_latest_day_mean")].set_index("node")
        for r in last.itertuples():
            e = ref.loc[r.node]
            rows_add = row(e["entity"], "da_minus_rt", r.ts_utc, r4(r.da - r.rt), "USD/MWh", "P1D", e["geo"], da, r.node,
                           retrieved)
            out = pd.concat([out, pd.DataFrame([rows_add])], ignore_index=True)
    log(f"price_board_latest: {len(out)} rows, {out['entity'].nunique()} hubs and zones, "
        f"{out['market'].nunique()} markets")
    return out


def market_prefix(df):
    """A hub is one entity in both markets, so the series key (entity, variable, ts_utc) needs the market in the
    variable: da_<name> for a day-ahead market, rt_<name> for a real-time one."""
    df["variable"] = np.where(df["market"].str.endswith("_dam"), "da_", "rt_") + df["variable"]
    return df


def is_peak(local, iso, holidays):
    days = PEAK_DAYS.get(iso, PEAK_DAYS_DEFAULT)
    return local.dt.weekday.isin(days) & local.dt.hour.isin(PEAK_HOURS) & ~local.dt.date.isin(holidays)


def build_peak(prices, ercot_hist, retrieved, log):
    rows = []
    holidays = nerc_holidays(range(2014, 2028))
    for (iso, mk), df in prices.items():
        g = df[df["node"] == MAIN[iso]]
        if iso == "ercot":  # the history reaches back past the rolling table's 30 days
            h = ercot_hist[ercot_hist["market"] == TABLES[(iso, mk)][1]]
            g = pd.concat([h, g]).drop_duplicates("ts_utc", keep="last").sort_values("ts")
        if g.empty:
            continue
        tz = TZ[iso]
        days, d = complete_days(g, tz)
        cut = days["day"].max() - dt.timedelta(days=89) if len(days) else None
        d = d[d["day"] >= cut] if cut else d
        d = d.assign(peak=is_peak(d["local"], iso, holidays))
        entity, geo, market = g["entity"].iloc[0], g["geo"].iloc[0], g["market"].iloc[0]
        base = dict(geo=geo, market=market, node=MAIN[iso], retrieved=retrieved)
        for day, x in d.groupby("day"):
            pk, op = x[x["peak"]], x[~x["peak"]]
            t = day_ts(day)
            if len(pk):
                rows += [row(entity, "peak_mean", t, r4(pk["value"].mean()), "USD/MWh", "P1D", **base),
                         row(entity, "peak_intervals", t, int(len(pk)), "count", "P1D", **base),
                         row(entity, "peak_minus_offpeak", t, r4(pk["value"].mean() - op["value"].mean()), "USD/MWh",
                             "P1D", **base)]
            rows += [row(entity, "offpeak_mean", t, r4(op["value"].mean()), "USD/MWh", "P1D", **base),
                     row(entity, "offpeak_intervals", t, int(len(op)), "count", "P1D", **base),
                     row(entity, "all_mean", t, r4(x["value"].mean()), "USD/MWh", "P1D", **base)]
    # ERCOT HB_HUBAVG per operating year (Central time) since 2015, from the history and the rolling tables
    for mk in (("dam", "rtm") if len(ercot_hist) else ()):  # without the history, carry_history keeps last run's
        market = TABLES[("ercot", mk)][1]
        g = pd.concat([ercot_hist[ercot_hist["market"] == market],
                       prices[("ercot", mk)][prices[("ercot", mk)]["node"] == "HB_HUBAVG"]])
        g = g.drop_duplicates("ts_utc", keep="last")
        days, d = complete_days(g, TZ["ercot"])
        d = d.assign(peak=is_peak(d["local"], "ercot", holidays), year=d["local"].dt.year)
        entity, geo = g["entity"].iloc[0], g["geo"].iloc[0]
        base = dict(geo=geo, market=market, node="HB_HUBAVG", retrieved=retrieved)
        for y, x in d.groupby("year"):
            t = f"{y}-01-01T00:00:00Z"
            pk, op = x.loc[x["peak"], "value"].mean(), x.loc[~x["peak"], "value"].mean()
            rows += [row(entity, "all_mean", t, r4(x["value"].mean()), "USD/MWh", "P1Y", **base),
                     row(entity, "peak_mean", t, r4(pk), "USD/MWh", "P1Y", **base),
                     row(entity, "offpeak_mean", t, r4(op), "USD/MWh", "P1Y", **base),
                     row(entity, "peak_minus_offpeak", t, r4(pk - op), "USD/MWh", "P1Y", **base),
                     row(entity, "days", t, int(x["day"].nunique()), "count", "P1Y", **base)]
    out = market_prefix(pd.DataFrame(rows))
    log(f"price_board_peak_offpeak: {len(out)} rows")
    return out


def build_spreads(prices, ercot_hist, fuels, retrieved, log):
    rows = []
    since = pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=365)
    hh = fuels[fuels["entity"] == "eia:henry_hub"].sort_values("ts")
    hh = hh[hh["ts"] >= since - pd.Timedelta(days=5)]
    for r in hh[hh["ts"] >= since].itertuples():
        rows.append(dict(row("eia:henry_hub", "henry_hub", r.ts_utc, r4(r.value), "USD/MMBtu", "P1D", "US-LA", "", "",
                             retrieved), x_gas_date=r.ts_utc[:10]))
    gas = hh.set_index(hh["ts"].dt.date)["value"]
    gas_days = sorted(gas.index)
    for iso in AI:
        g = prices[(iso, "dam")]
        g = g[g["node"] == MAIN[iso]]
        if iso == "ercot":
            h = ercot_hist[ercot_hist["market"] == "ercot_dam"]
            g = pd.concat([h, g]).drop_duplicates("ts_utc", keep="last").sort_values("ts")
        days, _ = complete_days(g, TZ[iso])
        entity, geo, market = g["entity"].iloc[0], g["geo"].iloc[0], g["market"].iloc[0]
        for r in days[pd.to_datetime(days["day"]).dt.tz_localize("UTC") >= since].itertuples():
            # the gas price of the operating day, else of the latest trading day up to 4 days before it (the trader
            # view's rule, docs/methods/trader_view.md)
            cands = [x for x in gas_days if r.day - dt.timedelta(days=4) <= x <= r.day]
            if not cands:
                continue
            gd = max(cands)
            gp = float(gas[gd])
            t = day_ts(r.day)
            base = dict(geo=geo, market=market, node=MAIN[iso], retrieved=retrieved)
            rows += [dict(row(entity, "spark_spread_7", t, r4(r.mean - HEAT_RATE * gp), "USD/MWh", "P1D", **base),
                          x_gas_date=gd.isoformat()),
                     dict(row(entity, "implied_heat_rate", t, r4(r.mean / gp), "MMBtu/MWh", "P1D", **base),
                          x_gas_date=gd.isoformat()),
                     dict(row(entity, "da_daily_mean", t, r4(r.mean), "USD/MWh", "P1D", **base),
                          x_gas_date=gd.isoformat())]
    b = fuels[fuels["entity"] == "eia:brent"].set_index("ts_utc")["value"]
    w = fuels[fuels["entity"] == "eia:wti_cushing"].set_index("ts_utc")["value"]
    for t in sorted(set(b.index) & set(w.index)):
        if pd.Timestamp(t) >= since:
            rows.append(dict(row("erw:brent_minus_wti", "brent_minus_wti", t, r4(b[t] - w[t]), "USD/bbl", "P1D", "", "",
                                 "", retrieved), x_gas_date=""))
    out = pd.DataFrame(rows, columns=SPREAD_COLS)
    log(f"price_board_spreads: {len(out)} rows")
    return out


def previous(name, cols=COLS):
    """The table as the last run wrote it (the daily run restores it from the Redivis draft), or None."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return None
    return ip.read_series(path, cols)


def build_carbon(retrieved, log, carried):
    rows = []
    old = previous("price_board_carbon")
    for table, price_var, unit in (("carb_auction_allowance_prices", "settlement_price", "USD/tCO2"),
                                   ("rggi_auction_allowance_prices", "clearing_price", "USD/short_ton")):
        if not os.path.exists(os.path.join(ip.OUT_DIR, table + ".csv")):
            # on GitHub CARB's server answers HTTP 202 (a known gap): the rows the last run derived are kept as they
            # were, with their auction dates, and the header says so; nothing is recomputed or refreshed
            prefix = table.split("_")[0] + ":"
            keep = old[old["entity"].str.startswith(prefix)] if old is not None else None
            if keep is None or keep.empty:
                raise RuntimeError(f"{table} is not on this machine and no earlier price_board_carbon holds its rows")
            rows += keep.to_dict("records")
            carried.append(f"{table} absent on this machine: its {len(keep)} rows are carried from the last run "
                           f"(retrieved_at {keep['retrieved_at'].max()})")
            log("  " + carried[-1])
            continue
        d = read_table(table)
        newest = d["ts"].max()
        for entity, g in d.groupby("entity"):
            if g["ts"].max() < newest - pd.Timedelta(days=366):
                # a discontinued series (RGGI's future-vintage auctions ended in 2011): its last value is not current,
                # so it is left out rather than shown beside this year's auctions
                log(f"  {table} {entity}: last auction {g['ts_utc'].max()[:10]}, over a year before the newest "
                    f"({newest:%Y-%m-%d}); left out as discontinued")
                continue
            p = g[g["variable"] == price_var].sort_values("ts")
            if p.empty:
                continue
            last = p.iloc[-1]
            base = dict(geo=last["geo"], market=last["market"], node=last["node"], retrieved=retrieved)
            rows.append(row(entity, "latest_price", last["ts_utc"], r4(last["value"]), unit, last["freq"], **base))
            same = g[g["ts_utc"] == last["ts_utc"]]
            for v in ("allowances_offered", "allowances_sold"):
                x = same[same["variable"] == v]
                if len(x):
                    rows.append(row(entity, v, last["ts_utc"], float(x["value"].iloc[0]), "count", last["freq"], **base))
            if len(p) > 1:
                prev = p.iloc[-2]
                rows.append(row(entity, "previous_price", prev["ts_utc"], r4(prev["value"]), unit, prev["freq"],
                                geo=prev["geo"], market=prev["market"], node=prev["node"], retrieved=retrieved))
                rows.append(row(entity, "price_change", last["ts_utc"], r4(last["value"] - prev["value"]), unit,
                                last["freq"], **base))
    out = pd.DataFrame(rows)
    log(f"price_board_carbon: {len(out)} rows")
    return out


def carry_history(new, old, name, carried, log):
    """Without the ERCOT history, keep the last run's ERCOT rows the rolling tables cannot rebuild: the annual rows and
    the days before the rolling tables' first complete day. Nothing else is kept from the old table."""
    if old is None or old.empty:
        log(f"  {name}: no earlier table to carry the ERCOT history rows from; they are absent this run")
        return new
    e = new[new["entity"].str.startswith("ercot:")]
    first = e.loc[e["freq"] == "P1D", "ts_utc"].min() if len(e) else None
    o = old[old["entity"].str.startswith("ercot:")]
    keep = o[(o["freq"] == "P1Y") | ((o["freq"] == "P1D") & ((first is None) | (o["ts_utc"] < (first or ""))))]
    carried.append(f"{name}: {len(keep)} ERCOT rows built from {HISTORY} are carried from the last run (the history "
                   "is not on this machine)")
    log("  " + carried[-1])
    for c in new.columns:
        if c not in keep.columns:
            keep = keep.assign(**{c: ""})
    return pd.concat([new, keep[new.columns]], ignore_index=True)


def header(title, inputs, run_id, notes, license_=None):
    h = [f"Energy Research Warehouse (ERW): {title} (derived)",
         "Shape: series (docs/datastandard.md v0). Derived by the ERW from the tables named below; method "
         "docs/methods/price_board.md.",
         f"Retrieved: {run_id} (UTC) by warehouse/derived/price_board.py",
         f"Run log: warehouse/output/logs/price_board_{run_id}.log",
         f"Source: erw:price_board ERW derived price board metrics (docs/methods/price_board.md), {METHOD_URL}",
         "Derived from: " + "; ".join(inputs)]
    if license_:
        h.append(f"License: {license_}. Its inputs are licensed internal (CARB and RGGI terms unconfirmed).")
    return h + notes + CARRIED


CARRIED = []  # filled by main: what this run carried from the last run's tables


def write(df, name, head, log, cols=COLS):
    """A derived table is rewritten whole each run (no merge): it is a function of its inputs as they stand."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    df = df[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    if df.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{name}: duplicate (entity, variable, ts_utc) keys")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in head + [f"File holds {len(df)} rows, rewritten whole by this run."]:
            f.write("# " + line + "\n")
        df.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    log(f"  wrote {name}.csv: {len(df)} rows")
    print(f"{name}.csv: rows={len(df)}")


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(ip.LOG_DIR, f"price_board_{run_id}.log"))
    results = []
    try:
        prices = {k: read_table(t, market=m) for k, (t, m) in TABLES.items()}
        for k, v in prices.items():
            log(f"{k}: {len(v)} rows, {v['node'].nunique()} nodes, {v['ts_utc'].min()} to {v['ts_utc'].max()}")
        # the ERCOT history: every year for the annual strip, HB_HUBAVG only (streamed, filtered while read)
        carried = CARRIED  # session 30: what this run carried from the last run's tables, named in the headers
        if os.path.exists(os.path.join(ip.OUT_DIR, HISTORY + ".csv")):
            hist = read_table(HISTORY, node="HB_HUBAVG")
        else:  # the GitHub runner never holds the ERCOT history (0.7 GB): the rows built from it are carried (below)
            hist = prices[("ercot", "dam")].iloc[0:0]
            log(f"{HISTORY} is not on this machine: the rows built from it are carried from the last run")
        log(f"{HISTORY} HB_HUBAVG: {len(hist)} rows, {hist['ts_utc'].min()} to {hist['ts_utc'].max()}")
        fuels = read_table("eia_fuel_spot_prices")
        price_inputs = sorted({t for t, _ in TABLES.values()})
        latest = build_latest(prices, retrieved, log)
        write(latest, "price_board_latest", header(
            "price board, latest day per hub and zone, day-ahead and real-time", price_inputs, run_id,
            ["Daily means are of complete local operating days only; a day with a missing interval is left out, never "
             "filled. Variables: daily_mean (last 30 days), latest_day_mean, previous_day_mean, day_change, "
             "day_change_pct, avg_7d, avg_30d, min_30d, max_30d (of the daily means), days_7d, days_30d, latest_interval, "
             "intervals_30d, da_minus_rt."]), log)
        results.append(dict(table="price_board_latest", market="derived", status="ok", detail=f"{len(latest)} rows"))
        peak = build_peak(prices, hist, retrieved, log)
        if hist.empty:
            peak = carry_history(peak, previous("price_board_peak_offpeak"), "price_board_peak_offpeak", carried, log)
        write(peak, "price_board_peak_offpeak", header(
            "price board, peak and off-peak means per ISO main hub", price_inputs + [HISTORY], run_id,
            ["Peak: hours ending 7 to 22 local, Monday to Friday (CAISO: Monday to Saturday, the WECC convention), "
             "NERC holidays off-peak. P1D rows: the last 90 complete operating days each table reaches. P1Y rows: ERCOT "
             "HB_HUBAVG per operating year since 2015 (days: the complete operating days included; the current year is "
             "year to date)."]), log)
        results.append(dict(table="price_board_peak_offpeak", market="derived", status="ok", detail=f"{len(peak)} rows"))
        spreads = build_spreads(prices, hist, fuels, retrieved, log)
        if hist.empty:
            spreads = carry_history(spreads, previous("price_board_spreads", SPREAD_COLS), "price_board_spreads",
                                    carried, log)
        write(spreads, "price_board_spreads", header(
            "price board, spark spreads, implied heat rates, Henry Hub and Brent minus WTI, daily",
            price_inputs + [HISTORY, "eia_fuel_spot_prices"], run_id,
            [f"Spark spread: day-ahead daily mean at the ISO's main hub minus {HEAT_RATE} MMBtu/MWh (an assumed heat "
             "rate, the one assumption of the board) times Henry Hub. Implied heat rate: the same daily mean over Henry "
             "Hub. Henry Hub of the operating day, else of the latest trading day up to 4 days before it (x_gas_date)."]),
            log, cols=SPREAD_COLS)
        results.append(dict(table="price_board_spreads", market="derived", status="ok", detail=f"{len(spreads)} rows"))
        carbon = build_carbon(retrieved, log, carried)
        write(carbon, "price_board_carbon", header(
            "price board, the latest CARB and RGGI auction results held", ["carb_auction_allowance_prices",
                                                                           "rggi_auction_allowance_prices"], run_id,
            ["ts_utc is the auction's date as its table gives it (CARB: the first of the auction month). The ERW holds "
             "no secondary-market carbon prices."], license_="internal"), log)
        results.append(dict(table="price_board_carbon", market="derived", status="ok", detail=f"{len(carbon)} rows"))
        ip.update_sources([{"source": "erw:price_board", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Price board v2 metrics (docs/methods/price_board.md)", "report_url": METHOD_URL,
                            "document_list": "", "license": "public",
                            "tables": ["price_board_latest", "price_board_peak_offpeak", "price_board_spreads",
                                       "price_board_carbon"]}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"price_board FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="price_board", market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("price_board", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
