#!/usr/bin/env python3
"""What curtailed energy is worth: its value at the hub price of its hours, what a flat load would have paid in those
hours, and what a battery could have absorbed, grid by grid (session 144).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made. Writes the page's file,
site/data/curtailment/worth.json, from the curtailment series the warehouse holds by the hour or finer, the public hub
prices, and (California) CAISO's own battery output, the data of the battery-charging overlay.

    python warehouse/derived/curtailment_worth.py                  # the site's file
    python warehouse/derived/curtailment_worth.py --out-dir DIR    # a trial: the file under DIR, nothing in site/data
    python warehouse/derived/curtailment_worth.py --ercot-dir DIR  # read ercot_wind_solar_hsl_hourly from DIR (a trial copy)

Which hours each grid rests on:
    CAISO   caiso_curtailment_intervals: CAISO's own curtailment, five-minute to 2025 and hourly from 2026, on the days
            the table covers. Valued from September 2024, the first month its hub prices are held.
    ERCOT   ercot_wind_solar_hsl_hourly: output below the High Sustained Limit, max(0, HSL less output) by hour, wind
            and solar. The ERW's estimate, not a curtailment figure of ERCOT's. ERCOT's public list keeps about nine
            days, so there is no whole month: the figures are for the hours held and say which.
    SPP     held by day only (spp_curtailment_daily): an hour's price cannot be matched to it, so nothing is valued.
    MISO    paused while terms are reviewed. PJM: licensed source needed. NYISO, ISO-NE: no hourly series is held.

The rules:
    Value.      Each hour's curtailed MWh times the hub's price of that hour, summed; and that over the MWh, USD per MWh
                curtailed (the curtailment-weighted price). Real time ("rt": the mean of the hour's four 15-minute
                prices, all four held) and day-ahead ("da"), each on its own. A month is written when the curtailment
                covers at least 90 percent of its days and the price at least 95 percent of its hours; an hour with no
                price is left out of both the MWh and the dollars, never priced at a guess.
    Cheap hours. Of the curtailed MWh that have a price: the share in hours priced below zero, and the share in hours
                priced under USD 5 per MWh (which includes those below zero).
    A flat load. 1 MW running only in the hours with any curtailment pays the simple mean of those hours' prices; beside
                it, the mean of every hour of the month held, and the curtailment-weighted price.
    A battery.  Per MW of battery with D hours of storage (D = 2, 4, 8): in every interval with curtailment it charges
                at full power, 1 MW, or at the curtailed MW when that is less, until it has taken in D MWh that local
                day; then it stops. One cycle a day: what it takes in one day is assumed gone by the next. The figure is
                energy taken in at the meter; round-trip losses are not credited and nothing is said of where it stands
                (the data does not locate a curtailment).
    The fleet.  CAISO's batteries (caiso_battery_storage, five-minute, from late August 2025), for a month in which
                both tables hold at least 90 percent of the days, over the days both hold. The installed power of the
                fleet is NOT in that data: the scale used is the fleet's highest five-minute charging rate of the month
                ("fleet_peak_charging_mw"), a measured figure, said as such. "absorb_fleet_mwh": the battery rule at
                that power. "fleet_charged_in_curtailed_hours_mwh": what the fleet actually took in during the hours
                with curtailment. Their ratio is given both ways and is not bounded by 100: the fleet may charge more
                in those hours than was curtailed.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402
import datacenter_page as dp  # noqa: E402
import curtailment_profile as cp  # noqa: E402
import free_energy as fe  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment", "worth.json")
DURATIONS = (2, 4, 8)
NEAR_DAYS = 0.90    # the profile's rule for a month of curtailment, and of batteries
NEAR_HOURS = 0.95   # the house rule for a month of prices
HUBS = {"caiso": ["TH_SP15_GEN-APND", "TH_NP15_GEN-APND"], "ercot": ["HB_HUBAVG", "HB_WEST"]}
TZ = {"caiso": "America/Los_Angeles", "ercot": "America/Chicago"}
ERCOT_TABLE = "ercot_wind_solar_hsl_hourly"


def read_hubs(in_dir, entities, since, log):
    """The price rows of a few hubs from `since`, as price_compare.read_prices keeps them (the first table of
    datacenter_page.TABLES that holds a row wins), read in chunks so that a history of years is never whole in memory."""
    lic, _ = pc.licenses()
    parts = []
    for i, t in enumerate(dp.TABLES):
        path = os.path.join(in_dir, f"{t}.csv")
        if lic.get(t) not in (None, "public") or not os.path.exists(path):
            continue
        got = []
        for chunk in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "freq", "geo"], chunksize=500_000):
            chunk = chunk[chunk["entity"].isin(entities) & (chunk["ts_utc"] >= since)]
            if len(chunk):
                got.append(chunk)
        if not got:
            continue
        d = pd.concat(got)
        d["side"] = np.where(d["variable"].isin(pc.DAM_VARS), "dam", np.where(d["variable"].isin(pc.RTM_VARS), "rtm", ""))
        d = d[d["side"] != ""]
        d["table"], d["rank"] = t, i
        log(f"  {t}: {len(d):,} rows of {sorted(d['entity'].unique())} from {since}")
        parts.append(d)
    if not parts:
        return {}
    x = pd.concat(parts)
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
    x = x.sort_values("rank").drop_duplicates(["entity", "side", "freq", "ts"], keep="first")
    return fe.location_series(x[["entity", "side", "ts", "value", "freq", "geo", "table"]])


def value_of(c, p):
    """The worth of a set of hours. c: curtailed MWh by hour (UTC), every hour of the set present (0 where none);
    p: the hub's hourly price. Hours with no price are left out of the MWh and of the dollars."""
    p = p.reindex(c.index)
    ok = p.notna()
    cp_, pp = c[ok], p[ok]
    mwh = float(cp_.sum())
    rec = {"hours": int(len(c)), "hours_priced": int(ok.sum()), "hours_curtailed": int((c > 0).sum()), "hours_curtailed_priced": int((cp_ > 0).sum()),
           "curtailed_mwh": round(float(c.sum()), 1), "curtailed_mwh_priced": round(mwh, 1)}
    if ok.sum() == 0:
        return rec
    rec["price_all_hours_mean"] = round(float(pp.mean()), 2)
    if mwh > 0:
        usd = float((cp_ * pp).sum())
        rec.update(value_usd=round(usd, 0), usd_per_mwh_curtailed=round(usd / mwh, 2),
                   share_mwh_negative_pct=round(100 * float(cp_[pp < 0].sum()) / mwh, 2), share_mwh_under5_pct=round(100 * float(cp_[pp < fe.THRESHOLD].sum()) / mwh, 2),
                   price_curtailed_hours_mean=round(float(pp[cp_ > 0].mean()), 2))
    return rec


def absorbed(iv, power, hours, tz):
    """What a battery of `power` MW and `hours` hours takes in, MWh by local day. iv: the intervals with curtailment,
    columns ts (UTC start), mwh (curtailed in the interval), dur (the interval's length, hours). In each interval it
    takes min(power x dur, the curtailed MWh); the day's total stops at power x hours (one cycle a day)."""
    if iv.empty:
        return pd.Series(dtype=float)
    take = np.minimum(power * iv["dur"].values, iv["mwh"].values)
    day = iv["ts"].dt.tz_convert(tz).dt.strftime("%Y-%m-%d").values
    return pd.Series(take).groupby(day).sum().clip(upper=power * hours)


def month_hours(month, tz):
    a = pd.Timestamp(f"{month}-01", tz=tz)
    b = (pd.Period(month) + 1).to_timestamp().tz_localize(tz)
    return pd.date_range(a.tz_convert("UTC"), b.tz_convert("UTC"), freq="h", inclusive="left")


def year_of(months, year, last, sum_keys):
    """A year from its months, when every month of it to `last` is written: the sums, and the ratios made again."""
    due = [f"{year}-{i:02d}" for i in range(1, 13) if f"{year}-{i:02d}" <= last]
    have = [m for m in due if m in months]
    if have != due:
        return {"missing": f"{len(have)} of the year's {len(due)} months to {last} are written; not written: " + (", ".join(m for m in due if m not in months))}
    return {"months": len(have), **{k: round(sum(months[m].get(k, 0) for m in have), 1) for k in sum_keys}}


def caiso(in_dir, log):
    """California: the value by hub and market, the battery rule per MW, and the fleet."""
    path = os.path.join(in_dir, f"{cp.INPUT}.csv")
    t = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["variable", "ts_utc", "value", "freq"])
    days = cp.covered_days(t)
    h = cp.hourly_curtailment(t).groupby("ts")["mwh"].sum()
    x = t[t["freq"].isin(["PT5M", "PT1H"])]
    iv = x.groupby(["ts_utc", "freq"], as_index=False)["value"].sum()
    iv["ts"] = pd.to_datetime(iv["ts_utc"], utc=True)
    five = iv["freq"] == "PT5M"
    iv["dur"] = np.where(five, 5 / 60, 1.0)
    iv["mwh"] = np.where(five, iv["value"] * 5 / 60, iv["value"])
    iv = iv[iv["mwh"] > 0][["ts", "mwh", "dur"]].sort_values("ts")
    del t, x
    tz = TZ["caiso"]
    local = iv["ts"].dt.tz_convert(tz)
    iv_day, iv_month = local.dt.strftime("%Y-%m-%d"), local.dt.strftime("%Y-%m")
    months_all = sorted({d[:7] for d in days})
    covered = {m: sorted(d for d in days if d[:7] == m) for m in months_all}
    whole = [m for m in months_all if len(covered[m]) >= NEAR_DAYS * pd.Period(m).days_in_month]
    prices = read_hubs(in_dir, [f"caiso:{n}" for n in HUBS["caiso"]], "2019-01-01", log)
    out = {"name": "CAISO", "whose": "operator", "table": cp.INPUT, "main_hub": HUBS["caiso"][0], "last_month": whole[-1],
           "hours": "CAISO's curtailment, five-minute to 2025 and hourly from 2026, on the days the table covers; valued from the first month the hub's prices are held", "hubs": {}}
    # the curtailed MWh of every hour of a month's covered days (0 where CAISO lists none)
    def month_series(m):
        idx = month_hours(m, tz)
        day = idx.tz_convert(tz).strftime("%Y-%m-%d")
        idx = idx[np.isin(day, covered[m])]
        return h.reindex(idx).fillna(0.0), len(month_hours(m, tz))  # a covered day's hour with no row had none curtailed (CAISO lists only the intervals with a curtailment)
    series = {m: month_series(m) for m in whole}
    for node in HUBS["caiso"]:
        sides = prices.get(f"caiso:{node}", {})
        out["hubs"][node] = {}
        for k in ("rt", "da"):
            if k not in sides:
                out["hubs"][node][k] = {"missing": "no price of this market is held for the hub"}
                continue
            p, months, missing = sides[k], {}, {}
            first = p.index.min().tz_convert(tz).strftime("%Y-%m")
            for m in whole:
                if m < first:
                    continue
                c, n = series[m]
                r = value_of(c, p)
                r.update(days_held=len(covered[m]), days_in_month=pd.Period(m).days_in_month, hours_in_month=n)
                if r["hours_priced"] < NEAR_HOURS * n:
                    missing[m] = f"the hub's price is held for {r['hours_priced']:,} of the month's {n:,} hours, under {NEAR_HOURS:.0%}"
                    continue
                months[m] = r
            years = {}
            for y in sorted({m[:4] for m in months}):
                yr = year_of(months, y, whole[-1], ["curtailed_mwh_priced", "value_usd", "hours_priced", "hours_curtailed_priced"])
                if "missing" not in yr and yr["curtailed_mwh_priced"] > 0:
                    yr["usd_per_mwh_curtailed"] = round(yr["value_usd"] / yr["curtailed_mwh_priced"], 2)
                    ms = [m for m in months if m[:4] == y]
                    for key in ("share_mwh_negative_pct", "share_mwh_under5_pct"):
                        yr[key] = round(sum(months[m].get(key, 0) * months[m]["curtailed_mwh_priced"] for m in ms) / yr["curtailed_mwh_priced"], 2)
                    yr["price_all_hours_mean"] = round(sum(months[m]["price_all_hours_mean"] * months[m]["hours_priced"] for m in ms) / yr["hours_priced"], 2)
                    yr["price_curtailed_hours_mean"] = round(sum(months[m].get("price_curtailed_hours_mean", 0) * months[m]["hours_curtailed_priced"] for m in ms) / max(1, yr["hours_curtailed_priced"]), 2)
                years[y] = yr
            out["hubs"][node][k] = {"freq": sides["freq"][k], "tables": sides["tables"][k], "first_month_held": first, "months": months, "years": years, "missing": missing}
            log(f"  caiso {node} {k}: {len(months)} months valued ({min(months) if months else '-'} to {max(months) if months else '-'}), {len(missing)} not")
    # the battery rule, per MW, for every whole month; and the fleet where CAISO's battery output is held
    bpath = os.path.join(in_dir, f"{cp.BATTERY}.csv")
    b = pd.read_csv(bpath, skiprows=ip.header_rows(bpath), usecols=["variable", "ts_utc", "value"])
    b = b[b["variable"] == "batteries_mw"]
    bat = cp.battery_hours(b)
    b5 = pd.Series(b["value"].values, index=pd.to_datetime(b["ts_utc"], utc=True)).sort_index()
    del b
    bl = bat.index.tz_convert(tz)
    bat = bat.assign(day=bl.strftime("%Y-%m-%d"))
    n_by_day = bat.groupby("day").size()
    bat_days = {d for d, n in n_by_day.items() if n == fe_day_hours(d, tz)}
    b5_month = b5.index.tz_convert(tz).strftime("%Y-%m")
    battery = {"months": {}, "years": {}, "fleet_table": cp.BATTERY,
               "fleet_scale": "the fleet's highest five-minute charging rate of the month, measured; its installed power is not in CAISO's battery output"}
    for m in whole:
        mine = iv[(iv_month == m).values & np.isin(iv_day.values, covered[m])]
        r = {"days_held": len(covered[m]), "days_in_month": pd.Period(m).days_in_month, "curtailed_mwh": round(float(mine["mwh"].sum()), 1), "absorb_mwh_per_mw": {}}
        for d in DURATIONS:
            r["absorb_mwh_per_mw"][str(d)] = round(float(absorbed(mine, 1.0, d, tz).sum()), 2)
        both = [d for d in covered[m] if d in bat_days]
        if len(both) >= NEAR_DAYS * pd.Period(m).days_in_month:
            mb = mine[np.isin(mine["ts"].dt.tz_convert(tz).dt.strftime("%Y-%m-%d").values, both)]
            peak = float(-b5[b5_month == m].min())
            bm = bat[bat["day"].isin(both)]
            cur_hours = set(mb["ts"].dt.floor("h"))
            in_cur = float(bm.loc[bm.index.isin(cur_hours), "charging_mwh"].sum())
            f = {"battery_days_held": len(both), "fleet_peak_charging_mw": round(peak, 0), "curtailed_mwh_battery_days": round(float(mb["mwh"].sum()), 1),
                 "fleet_charged_mwh": round(float(bm["charging_mwh"].sum()), 1), "fleet_charged_in_curtailed_hours_mwh": round(in_cur, 1),
                 "absorb_fleet_mwh": {}, "absorbable_pct_of_fleet_charged": {}, "fleet_charged_pct_of_absorbable": {}, "absorb_fleet_pct_of_curtailed": {}}
            for d in DURATIONS:
                a = float(absorbed(mb, peak, d, tz).sum())
                f["absorb_fleet_mwh"][str(d)] = round(a, 1)
                if in_cur > 0:
                    f["absorbable_pct_of_fleet_charged"][str(d)] = round(100 * a / in_cur, 2)
                if a > 0:
                    f["fleet_charged_pct_of_absorbable"][str(d)] = round(100 * in_cur / a, 2)
                if mb["mwh"].sum() > 0:
                    f["absorb_fleet_pct_of_curtailed"][str(d)] = round(100 * a / float(mb["mwh"].sum()), 2)
            r["fleet"] = f
        else:
            r["fleet_missing"] = f"CAISO's battery output is held for {len(both)} of the month's {pd.Period(m).days_in_month} days (it starts late August 2025)"
        battery["months"][m] = r
    for y in sorted({m[:4] for m in whole}):
        due = [f"{y}-{i:02d}" for i in range(1, 13) if f"{y}-{i:02d}" <= whole[-1]]
        if all(m in battery["months"] for m in due) and (y > whole[0][:4] or due[0] == whole[0]):
            battery["years"][y] = {"months": len(due), "curtailed_mwh": round(sum(battery["months"][m]["curtailed_mwh"] for m in due), 1),
                                   "absorb_mwh_per_mw": {str(d): round(sum(battery["months"][m]["absorb_mwh_per_mw"][str(d)] for m in due), 2) for d in DURATIONS}}
            fm = [m for m in due if "fleet" in battery["months"][m]]
            if len(fm) == len(due):
                F = [battery["months"][m]["fleet"] for m in due]
                in_cur = sum(f["fleet_charged_in_curtailed_hours_mwh"] for f in F)
                yr = {"fleet_charged_in_curtailed_hours_mwh": round(in_cur, 1), "absorb_fleet_mwh": {str(d): round(sum(f["absorb_fleet_mwh"][str(d)] for f in F), 1) for d in DURATIONS}}
                yr["absorbable_pct_of_fleet_charged"] = {k: round(100 * v / in_cur, 2) for k, v in yr["absorb_fleet_mwh"].items()} if in_cur > 0 else {}
                battery["years"][y]["fleet"] = yr
            else:
                battery["years"][y]["fleet_missing"] = f"the fleet is held for {len(fm)} of the year's {len(due)} months"
    out["battery"] = battery
    log(f"  caiso battery: {len(battery['months'])} months per MW, {sum('fleet' in r for r in battery['months'].values())} with the fleet")
    return out


def fe_day_hours(day, tz):
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return int(round((b - a) / pd.Timedelta(hours=1)))


def ercot(in_dir, ercot_dir, log):
    """Texas: the ERW's estimate (output below the High Sustained Limit) over the hours held, valued at the hub."""
    path = next((p for p in (os.path.join(d, f"{ERCOT_TABLE}.csv") for d in (ercot_dir, in_dir) if d) if os.path.exists(p)), None)
    base = {"name": "ERCOT", "whose": "erw_estimate", "table": ERCOT_TABLE, "main_hub": HUBS["ercot"][0]}
    if path is None:
        return {**base, "missing": f"{ERCOT_TABLE} is not on this machine: ERCOT's output below the High Sustained Limit is held by day only, and a day cannot be matched to an hour's price"}
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    w = d[d["entity"] == "ercot:system"].pivot_table(index="ts_utc", columns="variable", values="value", aggfunc="last")
    need = ["wind_generation_mw", "wind_hsl_mw", "solar_generation_mw", "solar_hsl_mw"]
    w = w.reindex(columns=need).dropna()
    w.index = pd.to_datetime(w.index, utc=True)
    w = w.sort_index()
    below = (w["wind_hsl_mw"] - w["wind_generation_mw"]).clip(lower=0) + (w["solar_hsl_mw"] - w["solar_generation_mw"]).clip(lower=0)
    hsl = w["wind_hsl_mw"] + w["solar_hsl_mw"]
    base.update(hours="output below the High Sustained Limit, max(0, HSL less output) by hour, wind and solar, system-wide; the hours ERCOT's public list held when it was read",
                first_hour=ip.utc_iso(below.index.min()), last_hour=ip.utc_iso(below.index.max()), hours_held=int(len(below)),
                below_hsl_mwh=round(float(below.sum()), 1), hsl_mwh=round(float(hsl.sum()), 1), share_below_hsl_pct=round(100 * float(below.sum()) / float(hsl.sum()), 2),
                months={}, months_missing="no whole month is held: ERCOT's public list keeps about nine days of these reports, and the history before 19 September 2026 is not openly published",
                read_from=os.path.relpath(path, ROOT).replace(os.sep, "/"), hubs={})
    prices = read_hubs(in_dir, [f"ercot:{n}" for n in HUBS["ercot"]], ip.utc_iso(below.index.min()), log)
    tz = TZ["ercot"]
    iv = pd.DataFrame({"ts": below.index, "mwh": below.values, "dur": 1.0})
    iv = iv[iv["mwh"] > 0]
    for node in HUBS["ercot"]:
        sides = prices.get(f"ercot:{node}", {})
        base["hubs"][node] = {}
        for k in ("rt", "da"):
            if k not in sides:
                base["hubs"][node][k] = {"missing": "no price of this market is held for the hub in these hours"}
                continue
            r = value_of(below, sides[k])
            if r["hours_priced"] == 0:
                base["hubs"][node][k] = {"missing": "no price of this market is held for the hub in these hours"}
                continue
            priced = sides[k].reindex(below.index).dropna().index
            r.update(first_hour_priced=ip.utc_iso(priced.min()), last_hour_priced=ip.utc_iso(priced.max()), window="the hours held, not a month")
            base["hubs"][node][k] = {"freq": sides["freq"][k], "tables": sides["tables"][k], "window": r}
            log(f"  ercot {node} {k}: {r['hours_priced']} of {r['hours']} hours priced")
    days = iv["ts"].dt.tz_convert(tz).dt.strftime("%Y-%m-%d")
    full = [d for d, n in below.groupby(below.index.tz_convert(tz).strftime("%Y-%m-%d")).size().items() if n == fe_day_hours(d, tz)]
    ivf = iv[days.isin(full).values]
    base["battery"] = {"window": {"days": len(full), "first_day": min(full) if full else None, "last_day": max(full) if full else None,
                                  "below_hsl_mwh": round(float(ivf["mwh"].sum()), 1),
                                  "absorb_mwh_per_mw": {str(d): round(float(absorbed(ivf, 1.0, d, tz).sum()), 2) for d in DURATIONS}},
                       "fleet_missing": "the battery-charging overlay holds CAISO's batteries only; no ERCOT fleet figure is compared here"}
    return base


def main(argv=None):
    ap = argparse.ArgumentParser(description="What curtailed energy is worth, grid by grid")
    ap.add_argument("--out-dir", help="a trial run: the file under this directory; nothing in site/data")
    ap.add_argument("--in-dir", help="read the tables from this directory instead of warehouse/output")
    ap.add_argument("--ercot-dir", help=f"a directory holding a trial copy of {ERCOT_TABLE}.csv, read before warehouse/output")
    a = ap.parse_args(argv)
    lines = []

    def log(s):
        lines.append(s)
        print(s)
    in_dir = a.in_dir or ip.OUT_DIR
    _, paused = pc.licenses()
    view = {"built": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "method": "warehouse/derived/curtailment_worth.py", "durations_hours": list(DURATIONS),
            "near_days": NEAR_DAYS, "near_hours": NEAR_HOURS, "threshold_usd_per_mwh": fe.THRESHOLD,
            "rules": {
                "value": "Each hour's curtailed MWh times the hub's price of that hour; an hour with no price is left out of the MWh and the dollars.",
                "flat_load": "1 MW running only in the hours with any curtailment pays the simple mean of those hours' prices (price_curtailed_hours_mean), against the mean of every hour held (price_all_hours_mean).",
                "battery": "Per MW of battery with D hours: in every interval with curtailment it charges at 1 MW, or at the curtailed MW when less, until it has taken in D MWh that local day. One cycle a day. Energy taken in at the meter; round-trip losses are not credited; the data does not locate a curtailment.",
                "fleet": "CAISO's batteries over the days both tables hold. The scale is the fleet's highest five-minute charging rate of the month, measured: its installed power is not in the data. The ratios are not bounded by 100.",
            },
            "grids": {"caiso": caiso(in_dir, log), "ercot": ercot(in_dir, a.ercot_dir, log),
                      "spp": {"name": "SPP", "whose": "operator", "table": "spp_curtailment_daily",
                              "missing": "SPP's curtailment is held by day, not by hour (its five-minute files were summed by day when read and are not kept), so an hour's price cannot be matched to it and no battery rule can run"}},
            "blank": {k: dict(name=b["name"], words=b["words"]) for k, b in dp.BLANK.items()},
            "not_held": {"nyiso": "no hourly curtailment series is published in an open form", "isone": "ISO-NE publishes monthly undelivered energy only; no hourly series"}}
    for k in paused:
        view["grids"].pop(k, None)
    target = os.path.join(a.out_dir, "worth.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(view, f, separators=(",", ":"), allow_nan=False)
    if a.out_dir:
        with open(os.path.join(a.out_dir, "worth.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    print(f"curtailment worth: written {target} ({os.path.getsize(target):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
