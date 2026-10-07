#!/usr/bin/env python3
"""Texas on the curtailment page: the ERW's estimate (output below the High Sustained Limit) by hour and by day for the
days ERCOT's public list held, output by ERCOT's own wind and solar regions, and the yearly output (session 144).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made. Writes the page's file,
site/data/curtailment/ercot.json, from two tables of warehouse/connectors/ercot_wind_solar_history.py:

    ercot_wind_solar_hsl_hourly      system-wide output and HSL by hour (about nine days), and output by region
    ercot_wind_solar_output_hourly   system-wide output by hour from ERCOT's yearly workbooks (2023 to 2025), no HSL

    python warehouse/derived/ercot_estimate_page.py                  # the site's file
    python warehouse/derived/ercot_estimate_page.py --in-dir DIR     # read the two tables from DIR
    python warehouse/derived/ercot_estimate_page.py --out-dir DIR    # a trial: the file under DIR, nothing in site/data

The rules (the connector's own functions, wide() and sums(), do the adding, so the page and the table cannot differ):
    An hour.   Output below HSL is max(0, HSL less output), wind and solar each on its own; an hour with output above
               the limit adds nothing below it, and its excess is kept apart ("above_hsl_mwh") so the page can show
               the morning and evening pattern of solar. Nothing is netted.
    A day.     The Central clock day. "whole" when every hour of it (23, 24 or 25) is held with output and HSL.
    A month.   Written only when at least 95 percent of its hours are held, over the hours held, never scaled up.
               Otherwise the month is named with its reason and carries no figure.
    A region.  Output only. ERCOT prints the actual HSL system-wide and not by region, so a region has no estimate.
    A year.    The sum of the workbook's hourly output, with the hours held and the hours of the year. No HSL.
The estimate is the ERW's, never ERCOT's: ERCOT publishes no curtailment figure.
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
import ercot_wind_solar_history as ew  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment", "ercot.json")
HOURLY, OUTPUT = ew.NAME_H, ew.NAME_O
NEAR_HOURS = ew.MIN_SHARE_OF_HOURS
TZ = ew.TZ
FUELS = ("wind", "solar")
MONTH_REASON = ("ERCOT's public list keeps about nine days of these reports, so a month fills only while the ERW reads the list "
                "at least once a week; the history before the first reading is not openly published")
REGION_REASON = "ERCOT prints the actual High Sustained Limit system-wide only; a region has output and no limit"
YEAR_REASON = "ERCOT's yearly workbooks hold output and no High Sustained Limit"


def read(in_dir, table):
    path = os.path.join(in_dir, f"{table}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{table}.csv is not in {in_dir}")
    return pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value", "retrieved_at"])


def r1(v):
    return round(float(v), 1)


def share(below, hsl):
    """Below HSL over HSL in percent, or None when there is no limit to divide by or the result would pass 100."""
    if not hsl or hsl <= 0 or below < 0:
        return None
    s = 100 * below / hsl
    return None if s > 100 else round(s, 2)


def fuel_figures(g):
    """One fuel's sums over a set of hours held with output and HSL."""
    below = (g["hsl"] - g["gen"]).clip(lower=0).sum()
    above = (g["gen"] - g["hsl"]).clip(lower=0).sum()
    return {"generation_mwh": r1(g["gen"].sum()), "hsl_mwh": r1(g["hsl"].sum()), "below_hsl_mwh": r1(below), "above_hsl_mwh": r1(above),
            "share_pct": share(float(below), float(g["hsl"].sum()))}


def both(parts):
    b, h = sum(p["below_hsl_mwh"] for p in parts), sum(p["hsl_mwh"] for p in parts)
    return {"generation_mwh": r1(sum(p["generation_mwh"] for p in parts)), "hsl_mwh": r1(h), "below_hsl_mwh": r1(b), "share_pct": share(b, h)}


def build(hourly, output):
    """The page's file from the two tables' rows (frames with entity, variable, ts_utc, value, retrieved_at)."""
    w = ew.wide(hourly)
    sysw = w[(w["entity"] == "ercot:system") & w["gen"].notna() & w["hsl"].notna()].copy()
    if sysw.empty:
        raise RuntimeError(f"{HOURLY} holds no system-wide hour with output and HSL")
    sysw["local"] = sysw["ts"].dt.tz_convert(TZ)
    sysw["day"] = sysw["local"].dt.strftime("%Y-%m-%d")
    sysw["hod"] = sysw["local"].dt.hour
    # an hour is on the chart only when both fuels hold it
    wide_h = sysw.pivot(index="ts", columns="fuel", values=["gen", "hsl"]).dropna()
    hours = [{"ts": ip.utc_iso(ts), "local": ts.tz_convert(TZ).strftime("%Y-%m-%d %H:00"),
              "wind_gen": round(float(r[("gen", "wind")]), 2), "wind_hsl": round(float(r[("hsl", "wind")]), 2),
              "solar_gen": round(float(r[("gen", "solar")]), 2), "solar_hsl": round(float(r[("hsl", "solar")]), 2)} for ts, r in wide_h.iterrows()]

    day_sums = ew.sums(w[w["entity"] == "ercot:system"], "D")
    days = {}
    for day, g in sysw.groupby("day", sort=True):
        s = day_sums[day_sums["period"] == day]
        held = int(s["hours_held"].min()) if len(s) == len(FUELS) else 0
        in_day = int(s["hours_in_period"].max())
        parts = {f: fuel_figures(g[g["fuel"] == f]) for f in FUELS}
        days[day] = {"hours_held": held, "hours_in_day": in_day, "whole": held == in_day, **parts, "both": both(list(parts.values()))}
    whole_days = [d for d, r in days.items() if r["whole"]]
    gw = sysw[sysw["day"].isin(whole_days)]
    win_parts = {f: fuel_figures(gw[gw["fuel"] == f]) for f in FUELS}
    all_parts = {f: fuel_figures(sysw[sysw["fuel"] == f]) for f in FUELS}

    month_sums = ew.sums(w[w["entity"] == "ercot:system"], "M")
    months = {}
    for m, s in month_sums.groupby("period", sort=True):
        held, in_month = int(s["hours_held"].min()), int(s["hours_in_period"].max())
        if held < NEAR_HOURS * in_month:
            months[m] = {"hours_held": held, "hours_in_month": in_month,
                         "missing": f"{held:,} of the month's {in_month:,} hours are held, under {NEAR_HOURS:.0%}: {MONTH_REASON}"}
            continue
        g = sysw[sysw["local"].dt.strftime("%Y-%m") == m]
        parts = {f: fuel_figures(g[g["fuel"] == f]) for f in FUELS}
        months[m] = {"hours_held": held, "hours_in_month": in_month, **parts, "both": both(list(parts.values()))}

    by_hour = []
    for h in range(24):
        g = gw[gw["hod"] == h]
        row = {"hour": h, "hours": int(len(g[g["fuel"] == "wind"]))}
        for f in FUELS:
            x = g[g["fuel"] == f]
            row[f"{f}_below_mwh"] = r1((x["hsl"] - x["gen"]).clip(lower=0).sum())
            row[f"{f}_above_mwh"] = r1((x["gen"] - x["hsl"]).clip(lower=0).sum())
        by_hour.append(row)

    # regions: output only, over the whole days, each as a share of the regions' sum (the regions' sum, not the
    # system-wide figure: ERCOT prints the two in different reports and they differ by 0.01 to 0.02 MW an hour)
    reg = w[w["entity"] != "ercot:system"].copy()
    reg["day"] = reg["ts"].dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
    reg = reg[reg["day"].isin(whole_days) & reg["gen"].notna()]
    regions = {}
    for f in FUELS:
        x = reg[reg["fuel"] == f].groupby("entity")["gen"].agg(["sum", "size"])
        total = float(x["sum"].sum())
        regions[f] = [{"id": e.split(":")[-1], "entity": e, "hours_held": int(r["size"]), "generation_mwh": r1(r["sum"]),
                       "share_of_fuel_pct": round(100 * float(r["sum"]) / total, 2) if total > 0 else None}
                      for e, r in x.sort_values("sum", ascending=False).iterrows()]

    years = {}
    o = output[output["entity"] == "ercot:system"].copy()
    o["ts"] = pd.to_datetime(o["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    o["year"] = o["ts"].dt.tz_convert(TZ).dt.strftime("%Y")
    for y, g in o.groupby("year", sort=True):
        a, b = pd.Timestamp(f"{y}-01-01").tz_localize(TZ), pd.Timestamp(f"{int(y) + 1}-01-01").tz_localize(TZ)
        in_year = int((b - a) / pd.Timedelta(hours=1))
        row = {"hours_in_year": in_year}
        for f in FUELS:
            x = g[g["variable"] == f"{f}_generation_mw"]
            row[f"{f}_hours_held"] = int(len(x))
            row[f"{f}_generation_mwh"] = r1(x["value"].sum())
        row["whole"] = all(row[f"{f}_hours_held"] >= NEAR_HOURS * in_year for f in FUELS)
        years[y] = row

    retrieved = max(str(hourly["retrieved_at"].max()), str(output["retrieved_at"].max()) if len(output) else "")
    return {
        "built": retrieved, "method": "warehouse/derived/ercot_estimate_page.py", "tables": [HOURLY, OUTPUT], "whose": "erw_estimate",
        "near_hours": NEAR_HOURS, "time": "Hours and days are US Central clock time.",
        "first_hour": hours[0]["ts"], "last_hour": hours[-1]["ts"], "hours_held": len(hours),
        "first_day": whole_days[0] if whole_days else None, "last_day": whole_days[-1] if whole_days else None, "whole_days": len(whole_days),
        "hours": hours, "days": days,
        "window": {**win_parts, "both": both(list(win_parts.values()))},
        "all_hours": {**all_parts, "both": both(list(all_parts.values()))},
        "by_hour_of_day": by_hour,
        "months": months, "month_reason": MONTH_REASON,
        "regions": regions, "region_limit": "no limit published", "region_reason": REGION_REASON,
        "years": years, "year_limit": "no limit published", "year_reason": YEAR_REASON,
        "history": "not held yet",
        "history_reason": "ERCOT openly publishes the High Sustained Limit for about nine days, system-wide; its history back to 2016 is not open, so the estimate starts with the first reading (28 September 2026)",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Texas on the curtailment page: the ERW's estimate by hour and day, output by region and by year")
    ap.add_argument("--in-dir", help="read the two tables from this directory instead of warehouse/output")
    ap.add_argument("--out-dir", help="a trial run: the file under this directory; nothing in site/data")
    a = ap.parse_args(argv)
    in_dir = a.in_dir or ip.OUT_DIR
    try:
        out = build(read(in_dir, HOURLY), read(in_dir, OUTPUT))
    except Exception as e:  # fail loudly: no file is better than a partial one
        print(f"FAILED: {type(e).__name__}: {e}")
        return 1
    path = os.path.join(a.out_dir, "ercot.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(out, separators=(",", ":"), allow_nan=False)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    w = out["window"]["both"]
    print(f"wrote {path}: {out['hours_held']} hours, {out['whole_days']} whole days ({out['first_day']} to {out['last_day']}), "
          f"below HSL {w['below_hsl_mwh']:,} MWh of {w['hsl_mwh']:,} ({w['share_pct']} percent); months {', '.join(f'{m}: ' + ('held' if 'both' in r else 'not held') for m, r in out['months'].items())}; "
          f"years {', '.join(out['years'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
