#!/usr/bin/env python3
"""What ERCOT's storage fleet offered to sell in real time, by price, by month (session 7019, chain 301; done-line
request 30).

Energy Research Warehouse (ERW). Writes warehouse/output/ercot_storage_rt_offers_monthly.csv from the 60-day SCED
disclosure zips the data machine keeps (warehouse/raw/ercot_60d_sced/zips, the file 60d_ESR_Data_in_SCED: each SCED run's
energy offer curve of every Energy Storage Resource, the columns "SCED1 Curve-MW<n>" and "SCED1 Curve-Price<n>", which
ercot_sced_esr_hourly leaves out). No request is made.

For each run and resource, the MW offered to sell at a price of P or less is the curve's MW at P, the curve read as
piecewise linear between its points (MW rising from charging, below zero, to discharging), clipped at zero: a price
limit below the curve's first price offers nothing to sell. Each run's MW is held until the next SCED run of the day (the
day's last run until the end of the day), as ercot_sced_esr_hourly integrates. Summed over a local (Central) month, for
P of USD 0, 25, 50, 100, 250 and 1,000 per MWh and at any price (the curve's highest MW). Entity ercot:esr_fleet:

  offered_sell_le_<P>_mwh, offered_sell_any_mwh      MWh offered to sell at P or less, and at any price
  offered_sell_le_<P>_share_pct                      that over the MWh offered at any price
  offered_sell_le_<P>_mwh_per_mw_day, ..._any_...     over the fleet's MW and the days held
  mw                                                  the fleet's MW: each resource's highest HSL of the month, added up
  days_held, resources, runs                          counts

A curve is an offer, not a dispatch: what was offered at a price is not what ran. Months from February 2026.

    python warehouse/lock.py run --task "storage offers" -- <python> warehouse/derived/ercot_storage_rt_offers.py
    python warehouse/derived/ercot_storage_rt_offers.py --out-dir DIR      # a trial: nothing in warehouse/output
"""
import argparse
import calendar
import csv
import datetime as dt
import glob
import io
import math
import os
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "ercot_storage_rt_offers_monthly"
ZIPS = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_sced", "zips")
TZ = "America/Chicago"
FIRST_MONTH = "2026-02"
LIMITS = [0, 25, 50, 100, 250, 1000]
ENTITY = "ercot:esr_fleet"
SOURCE = "erw:ercot_storage_rt_offers"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md"


def mw_at(m, p, limit):
    """The MW of each row's curve at a price limit: m and p are (rows x points) arrays, NaN where a point is empty."""
    best = np.full(m.shape[0], -np.inf)
    first = p[:, 0]
    for i in range(m.shape[1]):
        mi, pi = m[:, i], p[:, i]
        ok = ~np.isnan(mi) & ~np.isnan(pi) & (pi <= limit)
        best = np.where(ok, np.maximum(best, mi), best)
        if i + 1 < m.shape[1]:
            mj, pj = m[:, i + 1], p[:, i + 1]
            seg = ok & ~np.isnan(mj) & ~np.isnan(pj) & (pj > pi)
            frac = np.clip((limit - pi) / np.where(seg, pj - pi, 1.0), 0.0, 1.0)
            val = mi + frac * (mj - mi)
            best = np.where(seg, np.maximum(best, val), best)
    out = np.where(np.isneginf(best) | (first > limit), 0.0, best)
    return np.clip(out, 0.0, None)


def read_zip(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if "60d_ESR_Data_in_SCED" in n]
    if len(names) != 1:
        return None
    d = pd.read_csv(z.open(names[0]), dtype=str, keep_default_na=False)
    return d


def day_frame(d):
    """One row a run and resource: the local time, the run's held hours, the HSL and the MW offered at each limit."""
    ts = pd.to_datetime(d["SCED Time Stamp"], format="%m/%d/%Y %H:%M:%S")
    second = d["Repeated Hour Flag"].str.upper().eq("Y")
    local = ts.dt.tz_localize(TZ, ambiguous=(~second).to_numpy(), nonexistent="NaT")
    keep = local.notna()
    d, local = d[keep].reset_index(drop=True), local[keep].reset_index(drop=True)
    runs = np.sort(local.unique())
    day_end = (local.dt.normalize() + pd.Timedelta(days=1)).dt.tz_localize(None).dt.tz_localize(TZ, ambiguous=True, nonexistent="shift_forward")
    nxt = pd.Series(runs).shift(-1)
    held_to = local.map(dict(zip(runs, nxt)))
    end = held_to.where(held_to.notna() & (held_to.dt.date == local.dt.date), day_end)
    hours = (end - local).dt.total_seconds() / 3600.0
    npts = sum(1 for c in d.columns if c.startswith("SCED1 Curve-MW"))
    m = np.column_stack([pd.to_numeric(d[f"SCED1 Curve-MW{i}"].where(d[f"SCED1 Curve-MW{i}"] != ""), errors="coerce") for i in range(1, npts + 1)])
    p = np.column_stack([pd.to_numeric(d[f"SCED1 Curve-Price{i}"].where(d[f"SCED1 Curve-Price{i}"] != ""), errors="coerce") for i in range(1, npts + 1)])
    out = pd.DataFrame({"resource": d["Resource Name"], "local": local, "hours": hours.to_numpy(),
                        "hsl": pd.to_numeric(d["HSL"].where(d["HSL"] != ""), errors="coerce").to_numpy()})
    for lim in LIMITS:
        out[f"le_{lim}"] = mw_at(m, p, lim) * out["hours"]
    anym = np.nanmax(np.where(np.isnan(m), -np.inf, m), axis=1)
    out["any"] = np.clip(np.where(np.isneginf(anym), 0.0, anym), 0.0, None) * out["hours"]
    return out


def build(zips, log):
    files = sorted(glob.glob(os.path.join(zips, "*.zip")))
    parts, skipped = [], []
    for f in files:
        try:
            d = read_zip(f)
        except zipfile.BadZipFile:
            skipped.append(os.path.basename(f) + " (not a zip)")
            continue
        if d is None:
            skipped.append(os.path.basename(f) + " (no ESR file)")
            continue
        fr = day_frame(d)
        fr["month"] = fr["local"].dt.strftime("%Y-%m")
        fr["day"] = fr["local"].dt.strftime("%Y-%m-%d")
        g = fr.groupby(["month", "day", "resource"], as_index=False).agg(
            hsl=("hsl", "max"), runs=("hours", "size"), **{c: (c, "sum") for c in [f"le_{x}" for x in LIMITS] + ["any"]})
        parts.append(g)
    if not parts:
        raise RuntimeError(f"no 60-day SCED zip read under {zips}")
    a = pd.concat(parts, ignore_index=True)
    a = a[a["month"] >= FIRST_MONTH]
    out = {}
    for month, g in a.groupby("month"):
        days = sorted(set(g["day"]))
        mw = math.fsum(g.groupby("resource")["hsl"].max().clip(lower=0).fillna(0.0))
        v = {"days_held": len(days), "days_in_month": calendar.monthrange(int(month[:4]), int(month[5:]))[1],
             "resources": int(g["resource"].nunique()), "runs": int(g["runs"].sum()), "mw": round(mw, 4)}
        anyv = math.fsum(g["any"])
        v["offered_sell_any_mwh"] = round(anyv, 3)
        for lim in LIMITS:
            x = math.fsum(g[f"le_{lim}"])
            v[f"offered_sell_le_{lim}_mwh"] = round(x, 3)
            if anyv > 0:
                v[f"offered_sell_le_{lim}_share_pct"] = round(100 * x / anyv, 4)
            if mw > 0:
                v[f"offered_sell_le_{lim}_mwh_per_mw_day"] = round(x / mw / len(days), 4)
        if mw > 0:
            v["offered_sell_any_mwh_per_mw_day"] = round(anyv / mw / len(days), 4)
        out[month] = v
    log(f"  {len(files)} zips, {len(skipped)} not read{' (' + '; '.join(skipped[:3]) + ')' if skipped else ''}; months {', '.join(sorted(out))}")
    return out, skipped, len(files)


def unit_of(var):
    if var == "mw":
        return "MW"
    if var.endswith("_share_pct"):
        return "pct"
    if var.endswith("_mwh_per_mw_day"):
        return "MWh/MW/day"
    if var.endswith("_mwh"):
        return "MWh"
    return "count"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT storage: real-time offers to sell by price, by month (session 7019)")
    ap.add_argument("--out-dir", help="a trial: the table and its log under this folder")
    ap.add_argument("--zips", default=ZIPS)
    a = ap.parse_args(argv)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        months, skipped, nfiles = build(a.zips, log)
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        recs = [dict(entity=ENTITY, variable=k, ts_utc=f"{mo}-01T00:00:00Z", value=val, unit=unit_of(k), freq="P1M", geo="US-TX",
                     market="ercot_rtm", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=got, vintage="")
                for mo, v in sorted(months.items()) for k, val in v.items()]
        s = pd.DataFrame(recs, columns=ip.SERIES_COLS).sort_values(["entity", "variable", "ts_utc"])
        header = [
            "Energy Research Warehouse (ERW): what ERCOT's storage fleet offered to sell in real time, by price, by local month (derived, session 7019)",
            "Shape: series (docs/datastandard.md v0); entity ercot:esr_fleet, freq P1M, ts_utc the first day of the local (Central) month at "
            "00:00:00Z. Variables: offered_sell_le_<P>_mwh for P of 0, 25, 50, 100, 250 and 1,000 USD/MWh, offered_sell_any_mwh; each as "
            "_share_pct of the any-price MWh and as _mwh_per_mw_day over the fleet's mw and the days held; mw (each resource's highest HSL of "
            "the month, added up); days_held, days_in_month, resources, runs (count).",
            "Method: each SCED run's energy offer curve (SCED1 Curve-MW and -Price, as submitted, before mitigation) read as piecewise linear; "
            "the MW at a price limit clipped at zero (nothing offered to sell below the curve's first price); each run's MW held until the "
            "next SCED run of the day, the day's last run until the end of the day. An offer is not a dispatch.",
            f"Input: {nfiles} 60-day SCED disclosure zips under warehouse/raw/ercot_60d_sced/zips ({len(skipped)} not read); months from {FIRST_MONTH}.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_rt_offers.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: ercot:NP3-965-ER ERCOT, 60-Day SCED Disclosure Reports (60d_ESR_Data_in_SCED), https://www.ercot.com/mp/data-products/data-product-details?id=NP3-965-ER",
            "License: public (ERCOT's terms allow raw data to be used, reproduced and redistributed in compilations, charts and analyses, https://www.ercot.com/help/terms).",
        ]
        ip.write_csv(s, NAME, header, log)
        print(f"{NAME}: {len(s):,} rows, months {', '.join(sorted(months))}")
        rc = 0
    except Exception as exc:
        log(f"FAILED: {exc!r}")
        print(f"{NAME} FAILED: {exc!r}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
