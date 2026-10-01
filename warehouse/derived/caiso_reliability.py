#!/usr/bin/env python3
"""How tight was it: CAISO's evenings, day by day (session 58, California reliability v1, /grid/caiso).

Energy Research Warehouse (ERW) derived table, public: warehouse/output/caiso_reliability_daily.csv, one row per
variable and local (Pacific) day, from 2018-07-01 (the start of EIA's per-BA workbook) to the latest complete day held:

    entity eia930:CISO  (EIA-930 demand, CAISO's balancing authority: EIA's CISO workbook, sheet Published Hourly Data,
                         the emissions connector's extract; hourly, each value the hour's mean MW)
        peak_demand_mw          the day's highest hour of demand, MW
        peak_hour               that hour's local start, 0 to 23 (the earliest on a tie)
        afternoon_mean_mw       the mean of the hours starting 12:00, 13:00 and 14:00 (12:00 to 15:00), MW
        evening_peak_mw         the highest of the hours starting 17:00 to 20:00 (17:00 to 21:00), MW
        evening_peak_hour       that hour's local start (the earliest on a tie)
        evening_ramp_mw         evening_peak_mw less afternoon_mean_mw: the rise into the evening, MW
    entity caiso:ISO    (CAISO Today's Outlook, caiso_battery_storage, 5-minute; 2025-08-24 on)
        battery_mw_evening_peak the batteries' mean output over the evening peak hour (its twelve 5-minute intervals), MW;
                                positive is discharge
        battery_share_pct       battery_mw_evening_peak over evening_peak_mw, percent
    entity caiso:ISO    (caiso_grid_emergencies: CAISO's Grid Emergencies History Report)
        notices_<type>          the day's notices of a type (flex_alert, rmo, eea_watch, eea1 to eea3, alert, warning, stage1
                                to stage3, transmission_emergency...), written only for a day with one, count

A day is written only when every hour of it is present (24, or 23 and 25 on the clock changes); the battery figures only
when the evening peak hour has all twelve intervals. The day's available supply (CAISO's Today's Outlook "available
resources") is not held, so peak demand is not set against it: stated on the page.

    python warehouse/derived/caiso_reliability.py
"""

import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import eia930_emissions as em  # noqa: E402

NAME = "caiso_reliability_daily"
SOURCE = "erw:caiso_reliability"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/california_reliability.md"
TZ = "America/Los_Angeles"
AFTERNOON, EVENING = (12, 13, 14), (17, 18, 19, 20)


def demand_days(log):
    ex = em.latest_extract("ciso")
    if not ex:
        raise RuntimeError("no CISO extract under warehouse/raw/eia930_emissions/")
    url, lm, got = em.extract_meta(ex)
    x = em.read_extract(ex)[["ts_utc", "demand_mwh"]].dropna()
    t = pd.to_datetime(x["ts_utc"], utc=True).dt.tz_convert(TZ)
    x = x.assign(day=t.dt.strftime("%Y-%m-%d"), hour=t.dt.hour, ts=t)
    need = {d: int(((pd.Timestamp(d).tz_localize(TZ) + pd.DateOffset(days=1)).normalize() - pd.Timestamp(d).tz_localize(TZ)).total_seconds() // 3600)
            for d in x["day"].unique()}
    size = x.groupby("day").size()
    full = [d for d in size.index if size[d] == need[d]]
    log(f"CISO demand: {len(x):,} hours in the extract ({url}, last modified {lm}, retrieved {got}); {len(full)} complete Pacific days")
    return x[x["day"].isin(full)], f"{url} (last modified {lm})"


def battery_hours(log):
    path = os.path.join(ip.OUT_DIR, "caiso_battery_storage.csv")
    b = ip.read_series(path, ip.SERIES_COLS)
    b = b[(b["entity"] == "caiso:ISO") & (b["variable"] == "batteries_mw")]
    t = pd.to_datetime(b["ts_utc"], utc=True).dt.tz_convert(TZ)
    b = b.assign(day=t.dt.strftime("%Y-%m-%d"), hour=t.dt.hour, value=pd.to_numeric(b["value"]))
    g = b.groupby(["day", "hour"])["value"].agg(["mean", "size"])
    log(f"CAISO batteries: {len(b):,} 5-minute values, {b['day'].min()} to {b['day'].max()}")
    return g[g["size"] == 12]["mean"]


def notices(log):
    path = os.path.join(ip.OUT_DIR, "caiso_grid_emergencies.csv")
    n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    e = pd.read_csv(path, skiprows=n, dtype=str)
    log(f"notices: {len(e)} rows of caiso_grid_emergencies, {e['event_date'].min()} to {e['event_date'].max()}")
    return e.groupby(["event_date", "event_type"]).size()


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"caiso_reliability_{run_id}.log"))
    results = []
    try:
        d, ex_url = demand_days(log)
        bat = battery_hours(log)
        nt = notices(log)
        rows = []
        add = lambda ent, var, day, v, unit: rows.append((ent, var, f"{day}T00:00:00Z", v, unit))  # noqa: E731
        for day, g in d.groupby("day"):
            v = g.set_index("hour")["demand_mwh"]
            # a 25-hour day repeats an hour: the hour's highest value stands for it in the evening and afternoon sets
            v = v.groupby(level=0).max()
            pk_h = int(v.idxmax())
            add("eia930:CISO", "peak_demand_mw", day, float(v.max()), "MW")
            add("eia930:CISO", "peak_hour", day, pk_h, "hour")
            if all(h in v.index for h in AFTERNOON + EVENING):
                am = float(v[list(AFTERNOON)].mean())
                ev = v[list(EVENING)]
                eh = int(ev.idxmax())
                add("eia930:CISO", "afternoon_mean_mw", day, round(am, 4), "MW")
                add("eia930:CISO", "evening_peak_mw", day, float(ev.max()), "MW")
                add("eia930:CISO", "evening_peak_hour", day, eh, "hour")
                add("eia930:CISO", "evening_ramp_mw", day, round(float(ev.max()) - am, 4), "MW")
                if (day, eh) in bat.index:
                    b = float(bat[(day, eh)])
                    add("caiso:ISO", "battery_mw_evening_peak", day, round(b, 4), "MW")
                    add("caiso:ISO", "battery_share_pct", day, round(b / float(ev.max()) * 100, 4), "pct")
        for (day, typ), k in nt.items():
            add("caiso:ISO", f"notices_{typ}", day, int(k), "count")
        s = pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value", "unit"])
        s = s.assign(freq="P1D", geo="US-CA", market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        s = s[ip.SERIES_COLS]
        first, last = s[s["entity"] == "eia930:CISO"]["ts_utc"].min()[:10], s[s["entity"] == "eia930:CISO"]["ts_utc"].max()[:10]
        header = [
            "Energy Research Warehouse (ERW): how tight was it, CAISO's evenings day by day (derived, session 58, California reliability v1)",
            "Shape: series (docs/datastandard.md v0); freq P1D, ts_utc the local (Pacific) day at 00:00:00Z (decision 11). eia930:CISO: "
            "peak_demand_mw, peak_hour, afternoon_mean_mw (hours starting 12 to 14), evening_peak_mw and evening_peak_hour (hours starting 17 "
            "to 20), evening_ramp_mw (the evening peak less the afternoon mean); caiso:ISO: battery_mw_evening_peak (the batteries' mean over "
            "the evening peak hour, 2025-08-24 on) and battery_share_pct (over the evening peak), notices_<type> (the day's CAISO notices).",
            f"Days: {first} to {last}, complete Pacific days only. The day's available supply is not held, so peak demand is not set against it.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/caiso_reliability.py",
            f"Run log: warehouse/output/logs/caiso_reliability_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, California reliability method (docs/methods/california_reliability.md), {METHOD_URL}",
            f"Derived from: caiso_battery_storage; caiso_grid_emergencies; and EIA's CISO workbook, {ex_url}, the hourly demand of eia930_all_demand",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): EIA, CAISO (credit the California ISO).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rebuilt whole from its inputs each run
        ip.write_csv(s, NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)", report="California reliability, how tight was it (warehouse/derived/caiso_reliability.py)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        msg = f"{len(s)} rows, {first} to {last}"
        log(msg)
        print(f"caiso_reliability: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"caiso_reliability FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("caiso_reliability", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
