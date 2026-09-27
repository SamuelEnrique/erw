#!/usr/bin/env python3
"""Trader view: daily day-ahead and real-time metrics per hub, per ISO (session 19, tool 24).

Energy Research Warehouse (ERW). Implements docs/methods/trader_view.md. Inputs: the ISO price
tables (day-ahead and real-time, hubs and zones) and eia_fuel_spot_prices (Henry Hub). Outputs,
through the merge writer, derived `series` tables:

    <iso>_trader_daily         one row per hub, local operating day and metric (ercot, caiso,
                               nyiso, miso, spp, isone)
    iso_rt_top_intervals       a snapshot: the 10 highest real-time intervals of each ISO's
                               latest 7 complete local days

    python warehouse/derived/trader_view.py

Metrics per hub and local operating day (all hours of the day present, or nothing is written):
    da_mean_usd              mean of the day-ahead hourly prices
    da_onpeak_mean_usd       mean over on-peak hours: the standard 5x16 block, hours starting
                             06:00 to 21:00 local (hours ending 7 to 22) on weekdays that are not
                             NERC holidays; not written on weekends and holidays
    da_offpeak_mean_usd      mean over every other hour of the day
    rt_mean_usd              mean of the hourly real-time prices (a 15-minute table's hour is the
                             mean of its four intervals, all four required)
    da_rt_spread_mean_usd    mean over the day's hours of real-time minus day-ahead
    da_rt_spread_max_usd     the largest hourly real-time minus day-ahead
    hours_rt_over_da_50      hours in which real-time exceeded day-ahead by more than 50 USD/MWh
    implied_heat_rate        da_mean_usd / Henry Hub spot (USD/MMBtu) of the day, or of the
                             latest trading day up to 4 days before it (weekends, holidays)
    da_volatility_30d_usd    sample standard deviation of the 30 day-over-day changes in
                             da_mean_usd over the 31 days ending that day (all 31 required)
The real-time metrics need every hour of both markets; SPP has no real-time table, so it has
the day-ahead metrics only. PJM is absent: the ERW has no PJM price table (its data needs a
licensed API key). Values are exact decimal arithmetic on the published prices, rounded to
4 decimals. A row whose value is unchanged keeps its earlier retrieved_at (the Supabase loader
compares every column; see generation_mix.py).
"""

import datetime as dt
import os
import statistics
import sys
import traceback
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

METHOD = "docs/methods/trader_view.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md"
SOURCE = "erw:trader_view"
TOP = "iso_rt_top_intervals"
FUEL = "eia_fuel_spot_prices"
# iso: (day-ahead table, real-time table or None, local time zone of the operating day)
ISOS = {
    "ercot": ("ercot_dam_hub_prices", "ercot_rtm_hub_prices", "America/Chicago"),
    "caiso": ("caiso_dam_hub_prices", "caiso_rtm_hub_prices", "America/Los_Angeles"),
    "nyiso": ("nyiso_dam_zone_prices", "nyiso_rtm_zone_prices", "America/New_York"),
    "miso": ("miso_dam_hub_prices", "miso_rtm_hub_prices", "EST"),
    "spp": ("spp_dam_hub_prices", None, "America/Chicago"),
    "isone": ("isone_dam_zone_prices", "isone_rtm_zone_prices_hourly", "America/New_York"),
}
UNITS = {"hours_rt_over_da_50": "count", "implied_heat_rate": "MMBtu/MWh"}
Q = Decimal("0.0001")


def nerc_holidays(year):
    """NERC off-peak holidays: New Year's Day, Memorial Day, Independence Day, Labor Day,
    Thanksgiving, Christmas; a Sunday holiday moves to Monday (none move from Saturday)."""
    def nth(month, weekday, n):
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    last_mon_may = max(dt.date(year, 5, d) for d in range(25, 32) if dt.date(year, 5, d).weekday() == 0)
    days = [dt.date(year, 1, 1), last_mon_may, dt.date(year, 7, 4), nth(9, 0, 1), nth(11, 3, 4),
            dt.date(year, 12, 25)]
    return {d + dt.timedelta(days=1) if d.weekday() == 6 else d for d in days}


def dec(v):
    return Decimal(str(v))


def mean(vals):
    return sum(vals, Decimal(0)) / len(vals)


def read(name):
    d = ip.read_series(os.path.join(ip.OUT_DIR, name + ".csv"), ip.SERIES_COLS)
    d["t"] = pd.to_datetime(d["ts_utc"], utc=True)
    d["v"] = d["value"].map(dec)
    return d


def hourly_rt(rt):
    """Real-time prices per (node, hour start UTC): the table's hourly value, or the mean of the
    four 15-minute intervals of the hour (all four present)."""
    if (rt["freq"] == "PT1H").all():
        return {(r.node, r.t): r.v for r in rt.itertuples()}
    rt = rt.assign(h=rt["t"].dt.floor("h"))
    out = {}
    for (node, h), g in rt.groupby(["node", "h"]):
        if len(g) == 4 and g["t"].nunique() == 4:
            out[(node, h)] = mean(list(g["v"]))
    return out


def henry_hub(log):
    f = read(FUEL)
    hh = f[f["entity"] == "eia:henry_hub"].sort_values("t")
    return {r.t.date(): r.v for r in hh.itertuples()}, sorted(set(hh["t"].dt.date))


def hh_for(day, hh, dates):
    """Henry Hub of the day or the latest trading day up to 4 days before it."""
    for k in range(0, 5):
        d = day - dt.timedelta(days=k)
        if d in hh:
            return hh[d], d
    return None, None


def build_iso(iso, log, hh, hh_dates):
    da_t, rt_t, tz = ISOS[iso]
    da = read(da_t)
    rt = read(rt_t) if rt_t and os.path.exists(os.path.join(ip.OUT_DIR, rt_t + ".csv")) else None
    rth = hourly_rt(rt) if rt is not None else {}
    da["day"] = da["t"].dt.tz_convert(tz).dt.date
    rows, days_written = [], {}
    daily_mean = {}
    for (node, day), g in da.groupby(["node", "day"]):
        d0 = pd.Timestamp(day).tz_localize(tz)
        n = int(((d0 + pd.DateOffset(days=1)) - d0) / pd.Timedelta(hours=1))
        if len(g) != n or g["t"].nunique() != n:
            continue  # an incomplete day-ahead day writes nothing for the hub
        entity = g["entity"].iloc[0]
        vals = list(g["v"])
        m = mean(vals)
        daily_mean[(node, day)] = m
        out = {"da_mean_usd": m}
        local_hour = g["t"].dt.tz_convert(tz).dt.hour
        workday = day.weekday() < 5 and day not in nerc_holidays(day.year)
        on = [v for v, h in zip(vals, local_hour) if workday and 6 <= h <= 21]
        off = [v for v, h in zip(vals, local_hour) if not (workday and 6 <= h <= 21)]
        if on:
            out["da_onpeak_mean_usd"] = mean(on)
        if off:
            out["da_offpeak_mean_usd"] = mean(off)
        if rth:
            pairs = [(rth.get((node, t)), v) for t, v in zip(g["t"], g["v"])]
            if all(r is not None for r, _ in pairs):
                spread = [r - v for r, v in pairs]
                out["rt_mean_usd"] = mean([r for r, _ in pairs])
                out["da_rt_spread_mean_usd"] = mean(spread)
                out["da_rt_spread_max_usd"] = max(spread)
                out["hours_rt_over_da_50"] = Decimal(sum(1 for s in spread if s > 50))
        price, hh_day = hh_for(day, hh, hh_dates)
        if price is not None and price > 0:
            out["implied_heat_rate"] = m / price
        for var, v in out.items():
            rows.append((entity, node, var, day, v))
        days_written.setdefault(node, []).append(day)
    # 30-day volatility: the 30 day-over-day changes over 31 consecutive days
    for node, days in days_written.items():
        ds = sorted(days)
        for day in ds:
            window = [day - dt.timedelta(days=k) for k in range(30, -1, -1)]
            if all((node, d) in daily_mean for d in window):
                ch = [daily_mean[(node, window[i])] - daily_mean[(node, window[i - 1])] for i in range(1, 31)]
                sd = Decimal(str(statistics.stdev([float(c) for c in ch])))
                entity = da.loc[da["node"] == node, "entity"].iloc[0]
                rows.append((entity, node, "da_volatility_30d_usd", day, sd))
    t = pd.DataFrame(rows, columns=["entity", "node", "variable", "day", "v"])
    log(f"  {iso}: {len(t)} rows, {t['node'].nunique() if len(t) else 0} hubs, "
        f"{t['day'].nunique() if len(t) else 0} days; real-time {'from ' + rt_t if rth else 'none'}")
    top = None
    if rt is not None and len(rt):
        rt["day"] = rt["t"].dt.tz_convert(tz).dt.date
        # the latest 7 local days with every interval of every hub
        per = rt.groupby("day")["t"].nunique()
        full = []
        for day, n in per.items():
            d0 = pd.Timestamp(day).tz_localize(tz)
            step = pd.Timedelta(rt["freq"].iloc[0].replace("PT", "").lower().replace("m", "min").replace("1h", "1h"))
            if n == int(((d0 + pd.DateOffset(days=1)) - d0) / step):
                full.append(day)
        week = sorted(full)[-7:]
        if len(week) == 7:
            w = rt[rt["day"].isin(week)].sort_values(["v", "t"], ascending=[False, True]).head(10)
            top = (w, week)
    return t, top, da_t, rt_t


def keep_retrieved(s, name):
    """An unchanged row keeps its earlier retrieved_at (see the module docstring)."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return s
    prev = ip.read_series(path, ip.SERIES_COLS)
    key = ["entity", "variable", "ts_utc", "value"]
    s = s.assign(value=s["value"].astype(str))
    m = s.merge(prev[key + ["retrieved_at"]].rename(columns={"retrieved_at": "_prev"}), on=key, how="left")
    m["retrieved_at"] = m["_prev"].fillna(m["retrieved_at"])
    return m.drop(columns="_prev")


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"trader_view_{run_id}.log"))
    now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    results, tops, sources_done = [], [], []
    try:
        hh, hh_dates = henry_hub(log)
        log(f"Henry Hub: {len(hh)} trading days, latest {max(hh_dates)}")
    except Exception as exc:
        hh, hh_dates = {}, []
        log(f"Henry Hub unavailable ({exc!r}); implied heat rates not written")
    reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
    lic = dict(zip(reg["source"], reg["license"]))
    for iso, (da_t, rt_t, tz) in ISOS.items():
        name = f"{iso}_trader_daily"
        try:
            if not os.path.exists(os.path.join(ip.OUT_DIR, da_t + ".csv")):
                raise ip.SourceGap(f"input table absent: {da_t}")
            t, top, da_t, rt_t = build_iso(iso, log, hh, hh_dates)
            if t.empty:
                raise ip.SourceGap(f"no complete day-ahead day in {da_t}")
            inputs = [da_t] + ([rt_t] if rt_t and os.path.exists(os.path.join(ip.OUT_DIR, rt_t + ".csv")) else [])
            if hh and (t["variable"] == "implied_heat_rate").any():
                inputs.append(FUEL)
            srcs = set()
            for n in inputs:
                srcs |= set(ip.read_series(os.path.join(ip.OUT_DIR, n + ".csv"), ip.SERIES_COLS)["source"])
            license_ = "internal" if any(lic.get(s) == "internal" for s in srcs) else "public"
            s = pd.DataFrame({
                "entity": t["entity"], "variable": t["variable"],
                "ts_utc": t["day"].map(lambda d: f"{d}T00:00:00Z"),
                "value": t["v"].map(lambda v: float(v.quantize(Q, rounding=ROUND_HALF_UP))),
                "unit": t["variable"].map(lambda v: UNITS.get(v, "USD/MWh")), "freq": "P1D", "geo": "",
                "market": iso, "node": t["node"], "source": SOURCE, "source_url": METHOD_URL,
                "retrieved_at": now, "vintage": "",
            }).sort_values(["entity", "variable", "ts_utc"])
            s = keep_retrieved(s, name)
            header = [
                f"Energy Research Warehouse (ERW): {iso.upper()} trader view, daily day-ahead and real-time metrics "
                "per hub (derived; platform tool 24)",
                "Shape: series (docs/datastandard.md v0). freq P1D: ts_utc is the ISO's local operating day at "
                f"00:00:00Z (Decision 11; time zone {tz}). Method: {METHOD}.",
                f"Retrieved: {run_id} (UTC) by warehouse/derived/trader_view.py",
                f"Run log: warehouse/output/logs/trader_view_{run_id}.log",
                f"Source: {SOURCE} ERW derived table, trader view method ({METHOD}), {METHOD_URL}",
                "Derived from: " + "; ".join(inputs),
                "  input sources: " + "; ".join(sorted(srcs)),
                "Variables: " + ", ".join(sorted(t["variable"].unique())) + ". A metric is written only for a day "
                "with every hour it needs; on-peak is 5x16 (hours starting 06:00 to 21:00 local, weekdays that are "
                "not NERC holidays).",
                f"License: {license_}. A derived table inherits the most restrictive license of its inputs (Decision 23).",
            ]
            ip.write_csv(s[ip.SERIES_COLS], name, header, log)
            sources_done.append((name, license_))
            results.append(dict(table=name, market=iso, status="ok", detail=f"{len(s)} rows"))
            if top is not None:
                tops.append((iso, top, rt_t))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            skipped = "SourceGap" in last and os.environ.get("GITHUB_ACTIONS") == "true"
            print(f"trader_view {name} {'SKIPPED' if skipped else 'FAILED'}: {last}", file=sys.stderr)
            results.append(dict(table=name, market=iso, status="skipped" if skipped else "failed", detail=last[:300]))
    try:
        rows = []
        for iso, (w, week), rt_t in tops:
            for r in w.itertuples():
                rows.append({"entity": r.entity, "variable": "rt_price_top10_week", "ts_utc": r.ts_utc,
                             "value": float(r.v), "unit": "USD/MWh", "freq": r.freq, "geo": "", "market": iso,
                             "node": r.node, "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": now,
                             "vintage": ""})
        if not rows:
            raise ip.SourceGap("no ISO has 7 complete real-time days")
        s = pd.DataFrame(rows, columns=ip.SERIES_COLS).sort_values(["entity", "variable", "ts_utc"])
        weeks = "; ".join(f"{iso} {week[0]} to {week[-1]} ({rt_t})" for iso, (w, week), rt_t in tops)
        header = [
            "Energy Research Warehouse (ERW): the 10 highest real-time intervals of each ISO's latest 7 complete "
            "local days, all hubs (derived; platform tool 24)",
            "Shape: series (docs/datastandard.md v0), a snapshot: each run replaces the table. ts_utc is the "
            "interval start; freq is the real-time table's interval.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/trader_view.py",
            f"Source: {SOURCE} ERW derived table, trader view method ({METHOD}), {METHOD_URL}",
            "Derived from: " + "; ".join(rt for _, _, rt in tops),
            f"Weeks: {weeks}. Ties are broken by the earlier interval.",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        ip.write_snapshot(s, TOP, header, log, ip.SERIES_COLS)
        sources_done.append((TOP, "public"))
        results.append(dict(table=TOP, market="", status="ok", detail=f"{len(s)} rows"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{TOP} FAILED:\n{tb}")
        results.append(dict(table=TOP, market="", status="failed", detail=last[:300]))
    if sources_done:
        lic_all = "internal" if any(l == "internal" for _, l in sources_done) else "public"
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Trader view (docs/methods/trader_view.md)", report_url=METHOD_URL,
                                document_list=METHOD, license=lic_all, tables=[n for n, _ in sources_done])])
    ip.write_status("trader_view", run_id, results)
    log.close()
    print(f"trader_view run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
