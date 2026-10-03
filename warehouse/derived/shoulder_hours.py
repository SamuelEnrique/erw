#!/usr/bin/env python3
"""The shoulder hours: midday surplus, the evening shoulder, and how much of it the battery fleet covers (session 75).

Energy Research Warehouse (ERW), derived table shoulder_hours_monthly. Method: docs/methods/shoulder_hours.md.
Page: /shoulder, "The shoulder hours" (in review).

    python warehouse/derived/shoulder_hours.py

For ERCOT and CAISO, by local month from January 2019, from hourly demand and generation by fuel. "Shoulder" is this
table's term, defined here, not an industry standard.

Inputs (no request is made):
- EIA-930 hourly demand, solar and wind (and battery for ERCOT) from the per-balancing-authority workbooks the emissions
  connector saved (warehouse/raw/eia930_emissions/<run>/<BA>.xlsx, sheet Published Hourly Data, EIA's Adjusted columns;
  solar is SUN plus SNB, wind WND plus WNB; an hour is dated by its start). California stops after November 2025: EIA's
  generation series for California changed on 16 December 2025 (docs/methods/eia930_caiso_break.md); its solar and wind
  did not break there, but this table does not mix a changed series in.
- CAISO's battery output: caiso_battery_storage (CAISO's own, 5-minute, from August 2025), averaged to the hour.
- CAISO's curtailment: caiso_curtailment_daily (curtailed_solar_mwh plus curtailed_wind_mwh). ERCOT's is not held.
- The fleet: storage_buildout_monthly, battery_operating_mw and battery_operating_mwh of the grid and month.

The average day of a month: for each local hour (0 to 23), the mean over the month's complete days (every hour of
demand, solar and wind held) of demand, solar, wind, net load (demand less solar and wind) and battery output (positive
discharging). A month is written only when at least 90 percent of its days are complete; never filled.

On the average day:
- midday surplus: the run of hours around net load's lowest hour in which net load is below its daily mean; its MWh are
  the sum of (mean less net load) over those hours;
- evening shoulder: from the first hour after solar's highest hour in which solar is below half of that highest value,
  to the first hour, after net load has risen above its daily mean, in which net load is back at or below that mean;
  if net load stays above it to midnight the shoulder ends at midnight and is flagged (shoulder_runs_to_midnight);
  if net load does not rise above its mean after the start, the shoulder is 0 hours. Its MWh are the sum of (net load less mean) over its hours;
- the fleet: fleet_hours = battery_operating_mwh / battery_operating_mw (its average duration);
  shoulder_hours_covered = min(shoulder_hours, fleet_hours): the hours the fleet can run at its rated power through the
  shoulder; shoulder_hours_needed = shoulder_mwh_above_mean / battery_operating_mw: the hours a fleet of that power would
  have to run at rated power to deliver all of the shoulder's MWh above the mean.
"""

import glob
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

NAME = "shoulder_hours_monthly"
SOURCE = "erw:shoulder_hours"
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
GRIDS = {
    "ercot": dict(ba="ERCO", tz="America/Chicago", geo="US-TX", last=None),
    "caiso": dict(ba="CISO", tz="America/Los_Angeles", geo="US-CA", last="2025-11"),  # the last month before EIA's break
}
FIRST = "2019-01"
NEAR = 0.9
COLS = {"Adjusted demand": "demand", "Adjusted SUN Gen": "sun", "Adjusted SNB Gen": "snb", "Adjusted WND Gen": "wnd",
        "Adjusted WNB Gen": "wnb", "Adjusted BAT Gen": "bat"}


def workbook(ba):
    files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def hourly(ba):
    """EIA-930 hourly MW (MWh in the hour) by hour start, UTC: demand, solar, wind, battery."""
    import openpyxl
    path = workbook(ba)
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    t = head.index("UTC time")
    idx = {v: head.index(k) for k, v in COLS.items() if k in head}
    out = []
    for r in rows:
        ts = r[t]
        if ts is None or ts.year < 2018:
            continue
        rec = {"ts": ts - timedelta(hours=1)}
        for k, i in idx.items():
            v = r[i]
            rec[k] = float(v) if isinstance(v, (int, float)) else np.nan
        out.append(rec)
    d = pd.DataFrame(out)
    d["ts"] = pd.to_datetime(d["ts"]).dt.tz_localize("UTC")
    for k in ("sun", "snb", "wnd", "wnb", "bat"):
        if k not in d:
            d[k] = np.nan
    d["solar"] = d[["sun", "snb"]].sum(axis=1, min_count=1)
    d["wind"] = d[["wnd", "wnb"]].sum(axis=1, min_count=1)
    return d[["ts", "demand", "solar", "wind", "bat"]], path


def day_metrics(avg):
    """The midday surplus and the evening shoulder of one average day. avg: 24 rows (local hours 0 to 23) with demand,
    solar, wind and net_load. Returns a dict of the day's figures (hours as local hours of the day)."""
    nl = avg["net_load"].to_numpy(dtype=float)
    sol = avg["solar"].to_numpy(dtype=float)
    mean = float(nl.mean())
    low = int(nl.argmin())
    a = low
    while a - 1 >= 0 and nl[a - 1] < mean:
        a -= 1
    b = low
    while b + 1 <= 23 and nl[b + 1] < mean:
        b += 1
    trough = range(a, b + 1) if nl[low] < mean else range(0)
    out = dict(net_load_mean_mw=mean, midday_low_hour=low, midday_surplus_hours=len(trough),
               midday_surplus_mwh=float(sum(mean - nl[h] for h in trough)))
    peak = int(sol.argmax())
    start = next((h for h in range(peak + 1, 24) if sol[h] < 0.5 * sol[peak]), None)
    if start is None or sol[peak] <= 0:
        out.update(shoulder_start_hour=np.nan, shoulder_end_hour=np.nan, shoulder_hours=np.nan,
                   shoulder_mwh_above_mean=np.nan, shoulder_runs_to_midnight=np.nan)
        return out
    rise = next((h for h in range(start, 24) if nl[h] > mean), None)  # net load must be above its mean to fall back
    if rise is None:
        out.update(shoulder_start_hour=start, shoulder_end_hour=start, shoulder_hours=0, shoulder_mwh_above_mean=0.0,
                   shoulder_runs_to_midnight=0)
        return out
    end = next((h for h in range(rise + 1, 24) if nl[h] <= mean), None)
    to_midnight = end is None
    end = 24 if to_midnight else end
    out.update(shoulder_start_hour=start, shoulder_end_hour=end, shoulder_hours=end - start,
               shoulder_mwh_above_mean=float(sum(max(0.0, nl[h] - mean) for h in range(start, end))),
               shoulder_runs_to_midnight=int(to_midnight))
    return out


def fleet_metrics(shoulder_hours, shoulder_mwh, mw, mwh):
    """The fleet's hours against the shoulder. Hours covered never exceed the fleet's MWh over its MW."""
    if mw is None or mwh is None or not mw > 0 or shoulder_hours is None or np.isnan(shoulder_hours):
        return {}
    fh = mwh / mw
    return dict(fleet_mw=mw, fleet_mwh=mwh, fleet_hours=fh, shoulder_hours_covered=min(shoulder_hours, fh),
                shoulder_hours_needed=shoulder_mwh / mw)


def caiso_battery():
    s = pb.read_table("caiso_battery_storage")
    s = s[s["variable"] == "batteries_mw"]
    x = pd.Series(s["value"].values, index=pd.DatetimeIndex(s["ts"]))
    n = x.groupby(x.index.floor("h")).size()
    h = x.groupby(x.index.floor("h")).mean()
    return h[n == 12]


def curtailment_by_month():
    c = pb.read_table("caiso_curtailment_daily")
    c = c[c["variable"].isin(["curtailed_solar_mwh", "curtailed_wind_mwh"])]
    c["m"] = pd.DatetimeIndex(c["ts"]).strftime("%Y-%m")
    days = c.groupby("m")["ts"].nunique()
    return c.groupby("m")["value"].sum(), days


def fleet_by_month(grid):
    f = pb.read_table("storage_buildout_monthly")
    f = f[f["entity"] == f"iso:{grid}"]
    f["m"] = pd.DatetimeIndex(f["ts"]).strftime("%Y-%m")
    return f.pivot_table(index="m", columns="variable", values="value", aggfunc="first")


def build(grid, log):
    g = GRIDS[grid]
    h, path = hourly(g["ba"])
    if grid == "caiso":
        cb = caiso_battery()
        h = h.set_index("ts")
        h["bat"] = cb.reindex(h.index)
        h = h.reset_index()
    h["local"] = h["ts"].dt.tz_convert(g["tz"])
    h["day"] = h["local"].dt.strftime("%Y-%m-%d")
    h["hour"] = h["local"].dt.hour
    h["m"] = h["local"].dt.strftime("%Y-%m")
    h = h[(h["m"] >= FIRST) & ((g["last"] is None) | (h["m"] <= (g["last"] or "9999")))]
    h["net_load"] = h["demand"] - h["solar"] - h["wind"]
    need = h.groupby("day")["ts"].size()
    ok = h.dropna(subset=["demand", "solar", "wind"]).groupby("day").size()
    full = {d for d in need.index if ok.get(d, 0) == need[d] and need[d] in (23, 24, 25)}
    curt, curt_days = curtailment_by_month() if grid == "caiso" else (None, None)
    fl = fleet_by_month(grid)
    rows = []
    for m, x in h.groupby("m"):
        dim = pd.Period(m).days_in_month
        days = sorted(set(x["day"]) & full)
        if len(days) < NEAR * dim:
            log(f"  {grid} {m}: {len(days)} of {dim} days complete, not written")
            continue
        x = x[x["day"].isin(days)]
        avg = x.groupby("hour")[["demand", "solar", "wind", "net_load", "bat"]].mean().reindex(range(24))
        if avg[["demand", "solar", "wind"]].isna().any().any():
            log(f"  {grid} {m}: a local hour of the average day not held, not written")
            continue
        v = dict(days_held=len(days), days_in_month=dim)
        for k in ("demand", "solar", "wind", "net_load"):
            for hr in range(24):
                v[f"avg_{k}_mw_h{hr:02d}"] = avg.loc[hr, k]
        if x.groupby("day")["bat"].apply(lambda b: b.notna().all()).all():  # battery output in every hour of every held day
            for hr in range(24):
                v[f"avg_battery_mw_h{hr:02d}"] = avg.loc[hr, "bat"]
        dm = day_metrics(avg)
        v.update({k: val for k, val in dm.items() if not (isinstance(val, float) and np.isnan(val))})
        if curt is not None and m in curt.index and curt_days.get(m, 0) == dim:
            v["curtailed_mwh_per_day"] = float(curt[m]) / dim
        if m in fl.index and "battery_operating_mw" in fl.columns:
            mw = fl.loc[m].get("battery_operating_mw")
            mwh = fl.loc[m].get("battery_operating_mwh")
            v.update(fleet_metrics(dm.get("shoulder_hours"), dm.get("shoulder_mwh_above_mean", 0.0),
                                   None if pd.isna(mw) else float(mw), None if pd.isna(mwh) else float(mwh)))
        ts = f"{m}-01T00:00:00Z"
        for k, val in v.items():
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            unit = ("MW" if k.endswith("_mw") or "_mw_h" in k else "MWh" if k.endswith("_mwh") or k.endswith("_mwh_per_day")
                    else "hour" if k.endswith("_hours") or k.endswith("_covered") or k.endswith("_needed") or k.endswith("_hour") else "count")
            rows.append(dict(entity=f"iso:{grid}", variable=k, ts_utc=ts, value=round(float(val), 4), unit=unit, freq="P1M",
                             geo=g["geo"], market="", node="", source=SOURCE, source_url="docs/methods/shoulder_hours.md",
                             retrieved_at=ip.utc_iso(pd.Timestamp.now(tz="UTC")), vintage=""))
    log(f"  {grid}: {len({r['ts_utc'] for r in rows})} months from {os.path.relpath(path, ROOT)}")
    return rows, path


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"shoulder_hours_{run_id}.log"))
    rows, paths = [], []
    for grid in GRIDS:
        r, p = build(grid, log)
        rows += r
        paths.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    s = pd.DataFrame(rows)[ip.SERIES_COLS]
    header = [
        "Energy Research Warehouse (ERW): the shoulder hours, ERCOT and CAISO, by local month (session 75)",
        "Shape: series (docs/datastandard.md v0). freq P1M; ts_utc is the first day of the local month at 00:00:00Z. The average "
        "day by local hour (avg_<demand|solar|wind|net_load|battery>_mw_hHH), the midday surplus, the evening shoulder and the "
        "battery fleet against it; definitions in docs/methods/shoulder_hours.md (\"shoulder\" is this table's term).",
        "Window: from 2019-01; CAISO to 2025-11 (EIA's California generation series changed on 2025-12-16, "
        "docs/methods/eia930_caiso_break.md); a month with fewer than 90 percent of its days complete is not written.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/shoulder_hours.py",
        f"Run log: warehouse/output/logs/shoulder_hours_{run_id}.log",
        "Derived from: storage_buildout_monthly; caiso_battery_storage; caiso_curtailment_daily",
        f"Source: {SOURCE} EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks "
        f"(https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx), read from {'; '.join(paths)}",
        "License: public",
    ]
    ip.write_csv(s, NAME, header, log)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="The shoulder hours by grid and month (docs/methods/shoulder_hours.md)",
                            report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/shoulder_hours.md",
                            document_list="docs/methods/shoulder_hours.md", license="public", tables=[NAME])])
    log.close()
    print(f"{NAME}: {len(s):,} rows, {s['ts_utc'].nunique()} months, {s['entity'].nunique()} grids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
