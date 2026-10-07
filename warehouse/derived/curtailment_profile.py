#!/usr/bin/env python3
"""CAISO curtailment by hour of the day, by month and by reason, against battery charging (session 98).

Energy Research Warehouse (ERW). One derived table, caiso_curtailment_profile, from caiso_curtailment_intervals (CAISO's
wind and solar curtailment by 5-minute interval to 2025 and by hour from 2026) and caiso_battery_storage (CAISO's
5-minute battery output, from late August 2025). Method: docs/methods/caiso_curtailment_intervals.md. Page:
/curtailment (in review; until session 144 its own page, /curtailment/v2, which now redirects there).

    python warehouse/derived/curtailment_profile.py                 # the table, under the data lock
    python warehouse/derived/curtailment_profile.py --out-dir DIR   # a trial run: nothing in warehouse/output
    python warehouse/derived/curtailment_profile.py --snapshot      # also the site's own copy (site/data/curtailment_profile.json)

No request is made. Entity caiso:ISO; freq P1M; ts_utc the first day of the local (Pacific) month. A month is written
when at least 90 percent of its days are covered by the source (a day CAISO's report could not be read for is not a
day of zero); its figures are sums over the covered days, never scaled up.

    days_held, days_in_month
    curtailed_<fuel>_mwh                                      wind, solar
    curtailed_<fuel>_local_mwh, _system_mwh, _unspecified_mwh  CAISO's reason: local congestion, system-wide oversupply,
                                                              or none published (before 2022, and part of 2022)
    curtailed_<fuel>_econ_mwh, _ss_mwh, _oi_mwh               from 2026 only: economic bids, self-schedule cuts, operator
                                                              instructions (CAISO's three categories, each local or system)
    curtailed_<fuel>_mwh_hHH                                  the month's MWh in local hour HH (00 to 23)

and, for a month in which CAISO's battery output is held for at least 90 percent of the days (from September 2025),
over the days both tables hold:
    battery_days_held
    avg_curtailed_mw_hHH, avg_battery_charging_mw_hHH         the average day: wind and solar curtailed, and what the
                                                              batteries took in (charging only, as a positive number)
    curtailed_mwh_battery_days, battery_charging_mwh          the two over those days
    curtailed_while_charging_share_pct                        the share of the curtailed MWh that fell in hours in which
                                                              the batteries were charging on balance

What the data does not locate: CAISO publishes one figure for its whole system. Not the plant, not the node or zone,
and for "local" not which constraint. A local curtailment is behind a congested line somewhere; the file does not say
where, so nothing here says whether a battery at a given place could have taken it.
"""

import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "caiso_curtailment_profile"
INPUT = "caiso_curtailment_intervals"
BATTERY = "caiso_battery_storage"
SOURCE = "erw:caiso_curtailment_profile"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/caiso_curtailment_intervals.md"
SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment_profile.json")
TZ = "America/Los_Angeles"
NEAR = 0.90
FUELS = ("solar", "wind")
REASONS = ("local", "system", "unspecified")
CATS = ("econ", "ss", "oi")


def hourly_curtailment(t):
    """The interval rows as MWh by hour (UTC), fuel, reason and category: a 5-minute MW is MW x 5/60 MWh."""
    x = t[t["freq"].isin(["PT5M", "PT1H"])].copy()
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True).dt.floor("h")
    x["mwh"] = x["value"].where(x["freq"] == "PT1H", x["value"] * 5 / 60)
    parts = x["variable"].str.split("_")
    x["fuel"] = parts.str[1]
    last = parts.str[-2]
    x["reason"] = last.where(last.isin(["local", "system"]), "unspecified")
    x["cat"] = parts.str[2].where(parts.str[2].isin(CATS), "")
    return x.groupby(["ts", "fuel", "reason", "cat"], as_index=False)["mwh"].sum()


def covered_days(t):
    d = t[t["freq"] == "P1D"]
    return set(d["ts_utc"].str[:10])


def battery_hours(b):
    """CAISO's batteries by hour (UTC): the mean MW of the hour's twelve 5-minute values (an hour short of one is not
    held), and the charging part of it in MWh (the intervals below zero, as a positive number)."""
    s = b[b["variable"] == "batteries_mw"]
    v = pd.Series(s["value"].values, index=pd.to_datetime(s["ts_utc"], utc=True)).sort_index()
    g = v.groupby(v.index.floor("h"))
    ok = g.size() == 12
    return pd.DataFrame({"net_mw": g.mean()[ok], "charging_mwh": (-v.clip(upper=0) * 5 / 60).groupby(v.index.floor("h")).sum()[ok]})


def summarize(h, days, bat):
    """{month: {variable: value}} from the hourly curtailment, the covered days and the battery hours."""
    local = h["ts"].dt.tz_convert(TZ)
    h = h.assign(day=local.dt.strftime("%Y-%m-%d"), month=local.dt.strftime("%Y-%m"), hour=local.dt.hour)
    out = {}
    bat = bat.copy()
    if len(bat):
        bl = bat.index.tz_convert(TZ)
        bat["day"], bat["hour"] = bl.strftime("%Y-%m-%d"), bl.hour
        full = bat.groupby("day").size()
        bat_days = set(full.index[[n == int(((pd.Timestamp(d) + pd.Timedelta(days=1)).tz_localize(TZ) - pd.Timestamp(d).tz_localize(TZ)) / pd.Timedelta(hours=1)) for d, n in full.items()]])
    else:
        bat_days = set()
    for month in sorted({d[:7] for d in days}):
        in_month = pd.Period(month).days_in_month
        held = sorted(d for d in days if d[:7] == month)
        if len(held) < NEAR * in_month:
            continue
        m = h[(h["month"] == month) & h["day"].isin(held)]
        r = {"days_held": len(held), "days_in_month": in_month}
        for fuel in FUELS:
            f = m[m["fuel"] == fuel]
            r[f"curtailed_{fuel}_mwh"] = round(float(f["mwh"].sum()), 1)
            for reason in REASONS:
                r[f"curtailed_{fuel}_{reason}_mwh"] = round(float(f[f["reason"] == reason]["mwh"].sum()), 1)
            if (f["cat"] != "").any() or month >= "2026-01":
                for cat in CATS:
                    r[f"curtailed_{fuel}_{cat}_mwh"] = round(float(f[f["cat"] == cat]["mwh"].sum()), 1)
            by = f.groupby("hour")["mwh"].sum()
            for hh in range(24):
                r[f"curtailed_{fuel}_mwh_h{hh:02d}"] = round(float(by.get(hh, 0.0)), 1)
        both = [d for d in held if d in bat_days]
        if len(both) >= NEAR * in_month:
            c = m[m["day"].isin(both)].groupby("ts")["mwh"].sum()
            b = bat[bat["day"].isin(both)]
            r["battery_days_held"] = len(both)
            ch = h.drop_duplicates("ts").set_index("ts")["hour"]
            cur_by = c.groupby(ch.reindex(c.index).values).sum()
            bat_by = b.groupby("hour")["charging_mwh"].sum()
            for hh in range(24):
                r[f"avg_curtailed_mw_h{hh:02d}"] = round(float(cur_by.get(hh, 0.0)) / len(both), 1)
                r[f"avg_battery_charging_mw_h{hh:02d}"] = round(float(bat_by.get(hh, 0.0)) / len(both), 1)
            r["curtailed_mwh_battery_days"] = round(float(c.sum()), 1)
            r["battery_charging_mwh"] = round(float(b["charging_mwh"].sum()), 1)
            charging = set(b.index[b["net_mw"] < 0])
            if c.sum() > 0:
                r["curtailed_while_charging_share_pct"] = round(100 * float(c[c.index.isin(charging)].sum()) / float(c.sum()), 2)
        out[month] = r
    return out


def year_of(months, year):
    """A year for the site's copy: the sums of its months (every figure in MWh adds), when all its months to date are held."""
    have = sorted(m for m in months if m[:4] == year)
    due = [f"{year}-{i:02d}" for i in range(1, 13) if f"{year}-{i:02d}" <= max(months)]
    if have != due:
        return None
    r = {"months": len(have), "days_held": sum(months[m]["days_held"] for m in have), "days_in_period": sum(months[m]["days_in_month"] for m in have)}
    keys = sorted({k for m in have for k in months[m] if k.startswith("curtailed_") and k not in ("curtailed_mwh_battery_days", "curtailed_while_charging_share_pct")})
    for k in keys:
        r[k] = round(sum(months[m].get(k, 0.0) for m in have), 1)
    return r


def unit_of(v):
    return "pct" if v.endswith("_pct") else "count" if v.startswith(("days_", "battery_days")) else "MW" if v.startswith("avg_") else "MWh"


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO curtailment by hour of the day, month and reason, against battery charging")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/curtailment_profile.json)")
    a = ap.parse_args(argv)
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"curtailment_profile_{run_id}.log"))
    t = pd.read_csv(os.path.join(inputs, f"{INPUT}.csv"), skiprows=ip.header_rows(os.path.join(inputs, f"{INPUT}.csv")), usecols=["variable", "ts_utc", "value", "freq"])
    b = pd.read_csv(os.path.join(inputs, f"{BATTERY}.csv"), skiprows=ip.header_rows(os.path.join(inputs, f"{BATTERY}.csv")), usecols=["variable", "ts_utc", "value"])
    days = covered_days(t)
    bat = battery_hours(b)
    months = summarize(hourly_curtailment(t), days, bat)
    log(f"  {INPUT}: {len(t):,} rows, {len(days):,} days covered; {BATTERY}: {len(bat):,} whole hours from {bat.index.min()} to {bat.index.max()}; "
        f"{len(months)} months written, {sum('battery_days_held' in r for r in months.values())} with the batteries")
    rows = [dict(entity="caiso:ISO", variable=k, ts_utc=f"{m}-01T00:00:00Z", value=v, unit=unit_of(k), freq="P1M", geo="US-CA", market="", node="", source=SOURCE,
                 source_url=METHOD_URL, retrieved_at=retrieved, vintage="") for m, r in months.items() for k, v in r.items()]
    out = pd.DataFrame(rows)[ip.SERIES_COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole from its inputs each run
    ip.write_csv(out, NAME, [
        "Energy Research Warehouse (ERW): CAISO wind and solar curtailment by hour of the day, by month and by reason, against battery charging (session 98)",
        "Shape: series (docs/datastandard.md v0). Entity caiso:ISO; freq P1M; ts_utc the first day of the Pacific month. curtailed_<fuel>_mwh; by CAISO's reason "
        "(_local_, _system_, _unspecified_); from 2026 by its category (_econ_, _ss_, _oi_); by local hour (_mwh_hHH); and, where CAISO's battery output is held, "
        "the average day of curtailment and of battery charging (avg_curtailed_mw_hHH, avg_battery_charging_mw_hHH) and the share of curtailment in hours the "
        "batteries were charging. Definitions: docs/methods/caiso_curtailment_intervals.md.",
        f"Window: {min(months)} to {max(months)}. A month is written when at least {NEAR:.0%} of its days are covered; sums are over the covered days. One figure "
        "for the whole system: the data does not locate a curtailment.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/curtailment_profile.py", f"Run log: warehouse/output/logs/curtailment_profile_{run_id}.log",
        f"Derived from: {INPUT}; {BATTERY}",
        f"Source: {SOURCE} from California ISO, Production and curtailments data and the Daily Renewable Report (curtailment), and Today's Outlook (batteries)",
        "License: public, with credit to the California ISO (its terms: materials \"may be used by you provided that you keep intact all copyright, trademark and "
        "other proprietary notices and that you credit the California ISO\")",
    ], log, key=["entity", "variable", "ts_utc"])
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="CAISO curtailment by hour, month and reason, against battery charging (docs/methods/caiso_curtailment_intervals.md)", report_url=METHOD_URL,
                            document_list="docs/methods/caiso_curtailment_intervals.md", license="public", tables=[NAME])])
    if a.snapshot:
        years = {}
        for y in sorted({m[:4] for m in months}):
            v = year_of(months, y)
            if v:
                years[y] = v
        all_days = pd.date_range(min(days), max(days), freq="D").strftime("%Y-%m-%d")
        os.makedirs(os.path.dirname(SITE_FILE), exist_ok=True)
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(table=NAME, input=INPUT, built=retrieved, first=min(months), last=max(months), near=NEAR, first_day=min(days), last_day=max(days),
                           days_not_held=[d for d in all_days if d not in days], months=months, years=years), f, separators=(",", ":"))
    log.close()
    print(f"{NAME}: {len(out):,} rows, {len(months)} months ({min(months)} to {max(months)}), {sum('battery_days_held' in r for r in months.values())} with the batteries"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
