#!/usr/bin/env python3
"""Stress days of the seven grids, by one rule (session 306): the table grid_stress_days.

The chain prompt names the table stress_days; a series table's name has three parts (docs/datastandard.md), so it is
grid_stress_days. The rule is session 297's, docs/methods/battery_stress_days.md.

Energy Research Warehouse (ERW). docs/methods/stress_days.md. No stress-day rule for every grid was recorded in the
repository (ERCOT's are three named events, warehouse/derived/event_window.py; CAISO's the days of its own system-wide
notices, docs/methods/battery_stack.md, session 246), so this is the rule the chain prompt of 19 October 2026 gives
(the code machine's session 297):

    A local day is a stress day on a grid when the day's mean real-time price at the grid's main hub is above the 98th
    percentile of the daily means of the 365 days before it, or when the operator issued an emergency notice that day.

- The main hub is the price board's (warehouse/derived/price_board.py MAIN): ERCOT HB_HUBAVG, CAISO SP15, NYISO N.Y.C.,
  MISO Indiana Hub, SPP North Hub, ISO-NE Internal Hub. PJM: the ERW holds no PJM hub price (PJM's data is licensed)
  and no PJM notice, so PJM has no row, and the run says so.
- The day's mean: the local day of the grid's own clock; a day with any hour missing is not tested (session 297's
  rule: every local hour of the day holds at least one interval). ERCOT's daily means are ercot_hub_prices_daily's rt_mean (from 2015); the others are computed here from
  iso_hub_prices_history (CAISO from 14 July 2023, the others from 1 September 2024).
- The trailing 98th percentile is over the days held among the 365 before the day (the day itself left out), and only
  when at least 329 of them (nine tenths) are held; before that, a day is judged by the notice test alone.
- The operator's notices held: CAISO's (caiso_grid_emergencies), the system-wide kinds of session 246 (a Flex Alert,
  Restricted Maintenance Operations, an Energy Emergency Alert watch or level, a Stage emergency, a Warning, an Alert,
  a load interruption). No other operator's notices are held, so on the other grids only the price test can make one.
- Only days on which the grid's prices are held are written.

Shape: series, one row per grid and stress day: entity <iso>:<hub>, variable stress_day, value the day's mean real-time
price (USD/MWh), ts_utc the local day at 00:00Z, freq P1D; x_reason price, notice, or price and notice; x_trailing_p98
and x_trailing_days; x_notices the notice kinds that day.

    python warehouse/derived/stress_days.py
    python warehouse/derived/stress_days.py --dry-run    # say what it finds; write nothing
"""

import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "grid_stress_days"
OUT = os.path.join(ROOT, "warehouse", "output")
HISTORY = "iso_hub_prices_history"
ERCOT_DAILY = "ercot_hub_prices_daily"
NOTICES = "caiso_grid_emergencies"
MAIN = {"ercot": "HB_HUBAVG", "caiso": "TH_SP15_GEN-APND", "nyiso": "N.Y.C.", "miso": "INDIANA.HUB",
        "spp": "SPPNORTH_HUB", "isone": ".H.INTERNAL_HUB"}  # warehouse/derived/price_board.py MAIN
TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "nyiso": "America/New_York", "miso": "EST",
      "spp": "America/Chicago", "isone": "America/New_York"}  # price_board.py TZ
CAISO_NOTICES = ("flex_alert", "rmo", "eea_watch", "eea1", "eea2", "eea3", "stage1", "stage2", "stage3", "warning", "alert",
                 "load_interruption")  # battery_stack.py, session 246
PCT, WINDOW, MIN_DAYS, GAP = 0.98, 365, 329, 3
COLS = ip.SERIES_COLS + ["x_reason", "x_event", "x_trailing_p98", "x_trailing_days", "x_notices"]
# session 297: the named events keep their names (warehouse/derived/event_window.py)
NAMED = {"ercot": [("uri_2021", "2021-02-07", "2021-02-24"), ("elliott_2022", "2022-12-19", "2022-12-29"),
                   ("ercot_heat_2023", "2023-08-01", "2023-09-10")]}


def read(name, usecols=None):
    path = os.path.join(OUT, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, usecols=usecols)


def daily_means(hist, iso):
    """{local day: mean} of the main hub's real-time prices, days with every local hour held (session 297)."""
    h = hist[(hist["market"] == f"{iso}_rtm") & (hist["node"] == MAIN[iso])]
    if h.empty:
        return pd.Series(dtype=float), "", ""
    ts = pd.to_datetime(h["ts_utc"], utc=True)
    local = ts.dt.tz_convert(TZ[iso])
    day = local.dt.strftime("%Y-%m-%d")
    v = pd.to_numeric(h["value"])
    hour = ts.dt.floor("h").dt.strftime("%Y-%m-%dT%H")  # a UTC hour is one local hour (every offset is whole hours)
    g = pd.DataFrame({"day": day.values, "v": v.values, "h": hour.values}).groupby("day").agg(
        mean=("v", "mean"), hours=("h", "nunique"))
    # the hours a local day has (23, 24 or 25 at a clock change)
    days = pd.to_datetime(g.index)
    start = days.tz_localize(TZ[iso], nonexistent="shift_forward", ambiguous=True)
    end = (days + pd.Timedelta(days=1)).tz_localize(TZ[iso], nonexistent="shift_forward", ambiguous=True)
    want = ((end - start) / pd.Timedelta(hours=1)).astype(float)
    ok = g["hours"].values >= want.values
    src = h["source"].iloc[0]
    url = h["source_url"].iloc[0]
    return g.loc[ok, "mean"], src, url


def ercot_means():
    d = read(ERCOT_DAILY, ["entity", "variable", "ts_utc", "value", "source", "source_url"])
    d = d[(d["entity"] == "ercot:" + MAIN["ercot"]) & (d["variable"] == "rt_mean")]
    s = pd.Series(pd.to_numeric(d["value"]).values, index=d["ts_utc"].str[:10].values)
    return s[~s.index.duplicated()], d["source"].iloc[0], d["source_url"].iloc[0]


def judge(means):
    """(the trailing 98th percentile, the trailing days held) for each day of `means` (a Series by YYYY-MM-DD)."""
    s = means.sort_index()
    s.index = pd.to_datetime(s.index)
    p = s.rolling(f"{WINDOW}D", closed="left").quantile(PCT)
    n = s.rolling(f"{WINDOW}D", closed="left").count()
    p[n < MIN_DAYS] = np.nan
    return s, p, n


def events(iso, days):
    """{YYYY-MM-DD: event id}: stress days at most GAP days apart are one event, named for its first day, or the named
    event's id when it holds a day of that event's window (session 297)."""
    out, run = {}, []
    for d in sorted(days) + [None]:
        if run and (d is None or (pd.Timestamp(d) - pd.Timestamp(run[-1])).days > GAP):
            name = next((n for n, a, b in NAMED.get(iso, []) if any(a <= x <= b for x in run)),
                        f"{iso}_stress_{run[0].replace('-', '')}")
            out.update({x: name for x in run})
            run = []
        if d is not None:
            run.append(d)
    return out


def main():
    now = dt.datetime.now(dt.timezone.utc)
    run_id, stamp = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    hist = read(HISTORY, ["ts_utc", "value", "freq", "market", "node", "source", "source_url"])
    notices = read(NOTICES, ["event_date", "event_type"])
    notices = notices[notices["event_type"].isin(CAISO_NOTICES)]
    kinds = notices.groupby("event_date")["event_type"].agg(lambda x: ";".join(sorted(set(x))))
    rows, said = [], []
    for iso in ("ercot", "caiso", "nyiso", "miso", "spp", "isone"):
        means, src, url = ercot_means() if iso == "ercot" else daily_means(hist, iso)
        if means.empty:
            said.append(f"{iso}: no real-time prices held at {MAIN[iso]}; no row")
            continue
        s, p, n = judge(means)
        by_price = s > p
        note = pd.Series(False, index=s.index)
        if iso == "caiso":
            note = pd.Series(s.index.strftime("%Y-%m-%d").isin(kinds.index), index=s.index)
        stress = by_price | note
        ev = events(iso, [d.strftime("%Y-%m-%d") for d in s.index[stress.values]])
        for day in s.index[stress.values]:
            d = day.strftime("%Y-%m-%d")
            reason = " and ".join(x for x, f in (("price", by_price[day]), ("notice", note[day])) if f)
            rows.append(dict(entity=f"{iso}:{MAIN[iso]}", variable="stress_day", ts_utc=f"{d}T00:00:00Z",
                             value=round(float(s[day]), 4), unit="USD/MWh", freq="P1D", geo="", market=f"{iso}_rtm",
                             node=MAIN[iso], source=src, source_url=url, retrieved_at=stamp, vintage="",
                             x_reason=reason, x_event=ev[d], x_trailing_p98="" if pd.isna(p[day]) else round(float(p[day]), 4),
                             x_trailing_days=int(n[day]) if not pd.isna(n[day]) else 0,
                             x_notices=kinds.get(d, "") if iso == "caiso" else ""))
        k = int(stress.sum())
        n_ev = len(set(ev.values()))
        said.append(f"{iso}: {len(s):,} days held {s.index.min():%Y-%m-%d} to {s.index.max():%Y-%m-%d}, judged by price from "
                    f"{p.first_valid_index():%Y-%m-%d}; {k} stress days ({int(by_price.sum())} by price"
                    + (f", {int(note.sum())} by notice" if iso == "caiso" else "") + f"), {n_ev} events"
                    if p.first_valid_index() is not None else
                    f"{iso}: {len(s):,} days held from {s.index.min():%Y-%m-%d}, fewer than {MIN_DAYS} trailing days so far; {k} stress days by notice")
    said.append("pjm: no PJM hub price and no PJM notice is held (PJM's data is licensed); no row")
    for x in said:
        log(x)
        print(x)
    df = pd.DataFrame(rows, columns=COLS)
    df["geo"] = df["entity"].str.split(":").str[0].map({"ercot": "US-TX", "caiso": "US-CA", "nyiso": "US-NY",
                                                       "miso": "US", "spp": "US", "isone": "US"})
    header = [
        "Energy Research Warehouse (ERW): stress days of the grids by one rule (session 306); docs/methods/stress_days.md; the rule docs/methods/battery_stress_days.md",
        f"Rule: a local day is a stress day when the day's mean real-time price at the grid's main hub is above the {int(PCT * 100)}th percentile of "
        f"the daily means of the {WINDOW} days before it (at least {MIN_DAYS} of them held; a day with any hour missing is not tested), or the operator issued an emergency notice that day",
        "Shape: series (docs/datastandard.md v0). One row per grid and stress day: value the day's mean real-time price (USD/MWh); ts_utc the local day at 00:00Z; "
        "x_reason price, notice, or price and notice; x_event the event (days at most three apart; ERCOT's named events keep their names); x_trailing_p98 and x_trailing_days the threshold and the days it is taken over; x_notices CAISO's notice kinds",
        f"Inputs: {ERCOT_DAILY} (ERCOT's rt_mean at HB_HUBAVG), {HISTORY} (the other grids' main hubs), {NOTICES} (CAISO's system-wide notices); "
        "no other operator's notices are held, and PJM has neither prices nor notices here",
        *[f"This run: {x}" for x in said],
        f"Retrieved: {run_id} (UTC) by warehouse/derived/{NAME}.py from the ERW tables named above; per row, source and source_url are the prices' own",
        f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        "License: public (derived from public ERW tables)",
    ]
    if "--dry-run" in sys.argv:
        print(f"--dry-run: {len(df)} rows, nothing written")
        df.to_csv(os.path.join(ROOT, "runs", f"{NAME}_dry_run.csv"), index=False)
    else:
        ip.write_snapshot(df, NAME, header, log, COLS)
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
