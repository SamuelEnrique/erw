#!/usr/bin/env python3
"""Are the real-time days the hub history leaves out stress days? (session 65, check D3; internal, not a table)

Energy Research Warehouse (ERW). iso_hub_prices_history writes a real-time day only when every interval of the day
is there (session 13), so a day whose 5-minute feed had a hole is left out whole. Session 64 left out 28 ISO-NE and
21 NYISO real-time days (and 1 CAISO) of 2024-09-01 to 2025-08-31. If those days are the tight ones, every real-time
average built on the table (cost_of_power_monthly, merchant_revenue_monthly, ai_power_regions) is biased low.

The real-time price of a left-out day is by definition not held, so the test uses the day-ahead price, which is
held for nearly all of them: for each left-out day, the day-ahead mean of that day against the day-ahead mean of the
kept days of the same local month.

    python warehouse/derived/dropped_rt_days.py

Reads warehouse/output/iso_hub_prices_history.csv only. Writes, under warehouse/output/analysis_internal/ (gitignored,
never uploaded, not a warehouse table):

    dropped_rt_days.csv           one row per left-out real-time day
    dropped_rt_days_summary.csv   one row per ISO and window

Nothing is estimated into the warehouse: the "implied" figures say how far a month's day-ahead mean over the kept
days sits from its mean over all days, as a guide to the size and sign of the real-time bias, no more.
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
SRC = os.path.join(ROOT, "warehouse", "output", "iso_hub_prices_history.csv")
OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
HUBS = {  # iso: (entity, local time zone, real-time intervals per hour)
    "isone": ("isone:.H.INTERNAL_HUB", "America/New_York", 4),
    "nyiso": ("nyiso:N.Y.C.", "America/New_York", 4),
    "caiso": ("caiso:TH_SP15_GEN-APND", "America/Los_Angeles", 4),
    "miso": ("miso:INDIANA.HUB", "EST", 1),
    "spp": ("spp:SPPNORTH_HUB", "America/Chicago", 4),
}
WINDOWS = {"2024-09-01 to 2025-08-31 (session 64)": ("2024-09-01", "2025-08-31"),
           "2025-09-01 to 2026-08-31 (session 49)": ("2025-09-01", "2026-08-31")}


def read(path=SRC):
    with open(path, encoding="utf-8") as f:
        n = 0
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    d = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=["entity", "ts_utc", "value", "market"])
    d["value"] = pd.to_numeric(d["value"])
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def day_hours(day, tz):
    a = pd.Timestamp(day).tz_localize(tz)
    return int(((a + pd.DateOffset(days=1)) - a) / pd.Timedelta(hours=1))


def analyse(d, iso):
    """(days, summary rows) for one ISO: every local day of the windows, kept or left out."""
    entity, tz, per_hour = HUBS[iso]
    x = d[d["entity"] == entity].copy()
    x["day"] = x["ts"].dt.tz_convert(tz).dt.strftime("%Y-%m-%d")
    da = x[x["market"] == f"{iso}_dam"].groupby("day")["value"].agg(da_mean="mean", da_hours="size")
    rt = x[x["market"] == f"{iso}_rtm"].groupby("day")["value"].agg(rt_mean="mean", rt_n="size")
    rows = []
    for label, (a, b) in WINDOWS.items():
        for day in pd.date_range(a, b, freq="D").strftime("%Y-%m-%d"):
            h = day_hours(day, tz)
            kept = day in rt.index and rt.at[day, "rt_n"] == h * per_hour
            da_ok = day in da.index and da.at[day, "da_hours"] == h
            rows.append({"iso": iso, "entity": entity, "window": label, "day": day, "month": day[:7],
                         "rt_kept": kept, "rt_intervals_held": int(rt.at[day, "rt_n"]) if day in rt.index else 0,
                         "da_complete": da_ok, "da_hours_held": int(da.at[day, "da_hours"]) if day in da.index else 0,
                         "da_mean": round(float(da.at[day, "da_mean"]), 4) if da_ok else None})
    days = pd.DataFrame(rows)
    kept_month = days[days["rt_kept"] & days["da_complete"]].groupby(["window", "month"])["da_mean"].mean()
    all_month = days[days["da_complete"]].groupby(["window", "month"])["da_mean"].mean()
    out = days[~days["rt_kept"]].copy()
    key = list(zip(out["window"], out["month"]))
    out["da_mean_kept_days_same_month"] = [round(float(kept_month.get(k)), 4) if k in kept_month.index else None for k in key]
    out["da_diff"] = (out["da_mean"] - out["da_mean_kept_days_same_month"]).round(4)
    out["da_ratio"] = (out["da_mean"] / out["da_mean_kept_days_same_month"]).round(4)
    summ = []
    for label in WINDOWS:
        o = out[(out["window"] == label)]
        w = days[days["window"] == label]
        c = o.dropna(subset=["da_diff"])
        kept_all = w[w["rt_kept"] & w["da_complete"]]["da_mean"].mean()
        every = w[w["da_complete"]]["da_mean"].mean()
        months = sorted(o["month"].unique())
        worst = None
        for m in months:
            k, e = kept_month.get((label, m)), all_month.get((label, m))
            if k is not None and e is not None and (worst is None or abs(e - k) > abs(worst[1])):
                worst = (m, e - k)
        summ.append({
            "iso": iso, "entity": entity, "window": label, "days_in_window": len(w), "rt_days_left_out": len(o),
            "left_out_with_day_ahead": len(c),
            "mean_da_left_out": round(float(c["da_mean"].mean()), 2) if len(c) else None,
            "mean_da_kept_same_months": round(float(c["da_mean_kept_days_same_month"].mean()), 2) if len(c) else None,
            "mean_diff": round(float(c["da_diff"].mean()), 2) if len(c) else None,
            "median_diff": round(float(c["da_diff"].median()), 2) if len(c) else None,
            "share_above_month_mean": round(float((c["da_diff"] > 0).mean()), 3) if len(c) else None,
            "largest_diff": round(float(c["da_diff"].max()), 2) if len(c) else None,
            "largest_diff_day": c.loc[c["da_diff"].idxmax(), "day"] if len(c) else None,
            # the day-ahead mean of the window over the kept days, and over every day: their gap is the size the
            # real-time bias would have if real time moved with day ahead on the left-out days
            "window_da_mean_kept_days": round(float(kept_all), 3) if pd.notna(kept_all) else None,
            "window_da_mean_all_days": round(float(every), 3) if pd.notna(every) else None,
            "implied_bias_window": round(float(kept_all - every), 3) if pd.notna(kept_all) and pd.notna(every) else None,
            "month_most_affected": worst[0] if worst else None,
            "implied_bias_that_month": round(float(-worst[1]), 3) if worst else None,
        })
    return out, pd.DataFrame(summ)


def main():
    d = read()
    days, summ = [], []
    for iso in HUBS:
        o, s = analyse(d, iso)
        days.append(o)
        summ.append(s)
    days, summ = pd.concat(days, ignore_index=True), pd.concat(summ, ignore_index=True)
    os.makedirs(OUT, exist_ok=True)
    head = ("# Energy Research Warehouse (ERW), session 65, internal analysis (not a warehouse table): {}\n"
            "# Derived from: iso_hub_prices_history. Built by warehouse/derived/dropped_rt_days.py at {}.\n"
            "# Prices in USD/MWh. Days are the hub's local operating days. A real-time day is left out when the table "
            "does not hold every interval of it.\n")
    now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    for name, frame, what in (("dropped_rt_days.csv", days, "each real-time day the hub history leaves out, with its "
                               "day-ahead mean against the kept days of the same month"),
                              ("dropped_rt_days_summary.csv", summ, "per ISO and window, the left-out real-time days "
                               "against the kept days, on day-ahead prices")):
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
            f.write(head.format(what, now))
            frame.to_csv(f, index=False, lineterminator="\n")
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(summ.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
