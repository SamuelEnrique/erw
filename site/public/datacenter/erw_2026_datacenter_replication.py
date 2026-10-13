#!/usr/bin/env python3
"""ERW, What a datacenter pays (/cost-of-power): the headline numbers of the default case, rebuilt from
erw_2026_datacenter_hourly.csv. The Python mirror of erw_2026_datacenter_replication.do, step for step, for a reader
without Stata. Standard library only. It prints the do-file's lines, without Stata's padding of a number.
Session 228: and the answers "Will the power be there" (from the same file) and "How clean" (from
erw_2026_datacenter_carbon.csv beside it, when it is there).

    python erw_2026_datacenter_replication.py [erw_2026_datacenter_hourly.csv]

The default case: ERCOT, the North load zone (LZ_NORTH), a flat load of 100 MW, bought in real time. Method:
docs/methods/datacenter_pays_algorithm.md.
"""

import calendar
import csv
import math
import os
import sys

CSV_NAME = "erw_2026_datacenter_hourly.csv"
CARBON_NAME = "erw_2026_datacenter_carbon.csv"   # session 228: the grid's intensity by month and by hour (its 7 header lines; names on line 8)
CARBON_HEADER_LINES = 7
SCARCITY_USD = 1000.0        # session 228: an hour at or above it is counted short (the page's one level for every grid)
HEADER_LINES = 15            # the do-file: varnames(16) rowrange(17)
SENTINEL = -99999.0          # a price column: the hour's price is not held
NUMERIC = ["rt_usd_mwh", "da_usd_mwh", "hub_rt_usd_mwh", "in_last_twelve"]
RECODED = ["rt_usd_mwh", "da_usd_mwh", "hub_rt_usd_mwh"]
PRICES = {"rt": "rt_usd_mwh", "da": "da_usd_mwh", "hub": "hub_rt_usd_mwh"}
NEAR = 0.95                  # the do-file: hours held >= 0.95 * hours_due
# The reader's inputs at their defaults (the do-file's scalars)
MW, GPU_KW, PUE = 100, 1.3, 1.56


def destring(v):
    """destring, replace force: a number, or missing (None) when the text is not one."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def month_before(m, k):
    """The month k months before m (YYYY-MM): the do-file's ym - k."""
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def read(path):
    """import delimited ..., delimiter(comma) varnames(16) rowrange(17) stringcols(_all); then destring and the sentinel recode."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()
    rows = list(csv.DictReader(lines[HEADER_LINES:]))
    for r in rows:
        for c in NUMERIC:
            r[c] = destring(r[c])
        for c in RECODED:
            if r[c] == SENTINEL:
                r[c] = None
    return rows


def numbers(rows):
    """Every number the do-file displays, by name."""
    out = {}
    # hour by hour, then collapse to one row a month of US Central standard time
    months = {}
    for r in rows:
        m = months.setdefault(r["std_month"], dict(ym=r["std_month"], in_last_twelve=0, **{f"{k}_usd_per_mw": 0.0 for k in PRICES}, **{f"{k}_hours": 0 for k in PRICES}))
        for k, col in PRICES.items():
            if r[col] is not None:                    # collapse (sum): a missing value adds nothing
                m[f"{k}_usd_per_mw"] += r[col]
                m[f"{k}_hours"] += 1
        m["in_last_twelve"] = max(m["in_last_twelve"], int(r["in_last_twelve"]))
    table = sorted(months.values(), key=lambda x: x["ym"])
    for m in table:
        y, mo = int(m["ym"][:4]), int(m["ym"][5:7])
        m["hours_due"] = 24 * calendar.monthrange(y, mo)[1]
        for k in PRICES:
            m[f"{k}_counted"] = m[f"{k}_hours"] >= NEAR * m["hours_due"]
        m["rt_usd_mwh_month"] = m["rt_usd_per_mw"] / m["rt_hours"] if m["rt_hours"] > 0 else None
        m["calendar_year"] = y
    # last twelve months, market energy
    flagged = [m for m in table if m["in_last_twelve"] == 1]
    out["l12_first"], out["l12_last"] = (flagged[0]["ym"], flagged[-1]["ym"]) if flagged else (None, None)
    l12 = [m for m in flagged if m["rt_counted"]]
    out["l12_months"] = len(l12)
    out["l12_hours"] = sum(m["rt_hours"] for m in l12)
    out["l12_usd_per_mw"] = sum(m["rt_usd_per_mw"] for m in l12)
    out["l12_usd_mwh"] = out["l12_usd_per_mw"] / out["l12_hours"]
    out["l12_usd"] = out["l12_usd_per_mw"] * MW
    out["l12_mwh"] = out["l12_hours"] * MW
    # power per GPU-hour
    out["gpu_hour"] = out["l12_usd_mwh"] * GPU_KW * PUE / 1000
    out["gpus"] = MW * 1000 / (GPU_KW * PUE)
    # beside the zone: the hub in real time, and the zone bought day-ahead
    for v in ("hub", "da"):
        counted = [m for m in flagged if m[f"{v}_counted"]]
        out[f"{v}_months"] = len(counted)
        out[f"{v}_hours"] = sum(m[f"{v}_hours"] for m in counted)
        out[f"{v}_usd_mwh"] = sum(m[f"{v}_usd_per_mw"] for m in counted) / out[f"{v}_hours"]
    out["zone_less_hub"] = out["l12_usd_mwh"] - out["hub_usd_mwh"]
    # the months held, and those that count
    held = [m for m in table if m["rt_hours"] > 0]
    out["months_held"], out["first_held"], out["last_held"] = len(held), held[0]["ym"], held[-1]["ym"]
    out["months_counted"] = sum(1 for m in table if m["rt_counted"])
    # by calendar year
    out["years"] = []
    for y in sorted({m["calendar_year"] for m in table}):
        mine = [m for m in table if m["calendar_year"] == y]
        usd, hours = sum(m["rt_usd_per_mw"] * m["rt_counted"] for m in mine), sum(m["rt_hours"] * m["rt_counted"] for m in mine)
        out["years"].append(dict(year=y, months=sum(1 for m in mine if m["rt_counted"]), usd_per_mw=usd, hours=hours, usd_mwh=usd / hours if hours else None))
    # a bad month: keep, gsort -rt_usd_mwh_month ym, the row at the nearest rank
    kept = [m for m in table if m["rt_counted"] and month_before(out["l12_last"], 35) <= m["ym"] <= out["l12_last"]]
    out["w36_months"], out["w36_first"], out["w36_last"] = len(kept), min(m["ym"] for m in kept), max(m["ym"] for m in kept)
    ranked = sorted(kept, key=lambda m: (-m["rt_usd_mwh_month"], m["ym"]))
    out["bad_rank"] = max(1, math.ceil(0.1 * len(ranked)))
    bad = ranked[out["bad_rank"] - 1]
    out["bad_month"], out["bad_usd_mwh"], out["bad_usd"] = bad["ym"], bad["rt_usd_mwh_month"], bad["rt_usd_per_mw"] * MW
    out["months"] = table
    # session 228, "Will the power be there": the hours of the last twelve months at or above the scarcity level, a
    # flat MW's cost in them, and when they fell (the month, and the clock hour in standard time: hour_utc less 6)
    scarce = [r for r in rows if r["in_last_twelve"] == 1 and r["rt_usd_mwh"] is not None and r["rt_usd_mwh"] >= SCARCITY_USD]
    out["scarce_hours"] = len(scarce)
    out["scarce_usd"] = sum(r["rt_usd_mwh"] for r in scarce) * MW
    out["scarce_months"] = sorted({r["std_month"] for r in scarce})
    clock = sorted({(int(r["hour_utc"][11:13]) - 6) % 24 for r in scarce})
    out["scarce_clock"] = (clock[0], clock[-1]) if clock else None
    return out


def carbon(path, n):
    """Session 228, "How clean": the load's carbon from erw_2026_datacenter_carbon.csv. The default case is a flat
    load, so its energy in a month is the hours held, and its own hours over the hourly window weigh every hour
    held alike: the grid's mean over the hours the price and the intensity are both held."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()
    rows = list(csv.DictReader(lines[CARBON_HEADER_LINES:]))
    monthly = {r["ts_utc"][:7]: float(r["kg_co2_per_mwh"]) for r in rows if r["kind"] == "month"}
    hourly = {r["ts_utc"]: float(r["kg_co2_per_mwh"]) for r in rows if r["kind"] == "hour"}
    out = {}
    # the last twelve months at the grid's monthly average: each month's energy (a flat MW: its hours held) times
    # the month's intensity, over the months of the twelve whose intensity is held; the tonnes a year apply that rate
    # to the year's whole energy
    l12 = [m for m in n["months"] if m["in_last_twelve"] == 1 and m["rt_counted"]]
    kg = sum(m["rt_hours"] * monthly[m["ym"]] for m in l12 if m["ym"] in monthly)
    energy = sum(m["rt_hours"] for m in l12 if m["ym"] in monthly)
    out["co2_months"] = sum(1 for m in l12 if m["ym"] in monthly)
    out["co2_kg_mwh"] = kg / energy if energy else None
    out["co2_tonnes"] = (out["co2_kg_mwh"] * sum(m["rt_hours"] for m in l12) * MW) / 1000 if energy else None
    # the hourly window: the hours the hourly file holds whose price the hourly file of prices holds
    priced = {r["hour_utc"] for r in n["rows"] if r["rt_usd_mwh"] is not None}
    both = [v for ts, v in hourly.items() if ts in priced]
    out["window_hours"] = len(both)
    out["window_kg_mwh"] = sum(both) / len(both) if both else None
    out["window_from"], out["window_to"] = (min(ts for ts in hourly if ts in priced), max(ts for ts in hourly if ts in priced)) if both else (None, None)
    # by calendar year: the mean of the months held
    years = {}
    for m, v in monthly.items():
        years.setdefault(int(m[:4]), []).append(v)
    out["co2_years"] = [(y, sum(v) / len(v), len(v)) for y, v in sorted(years.items())]
    return out


def report(n):
    lines = [f"the last twelve months: {n['l12_first']} to {n['l12_last']}",
             f"months in the last twelve that count: {n['l12_months']}",
             f"hours held in the last twelve months: {n['l12_hours']}",
             f"market energy, a flat load, last twelve months, USD per MWh: {n['l12_usd_mwh']:.2f}",
             f"cost for 100 MW, USD: {n['l12_usd']:,.0f}",
             f"energy for 100 MW, MWh: {n['l12_mwh']:,.0f}",
             f"power per GPU-hour, USD: {n['gpu_hour']:.4f}",
             f"GPUs that 100 MW powers: {n['gpus']:,.0f}",
             f"months of the twelve that count at the hub: {n['hub_months']}",
             f"the hub beside it, a flat load, USD per MWh: {n['hub_usd_mwh']:.2f}",
             f"the load zone less its hub, USD per MWh: {n['zone_less_hub']:.2f}",
             f"months of the twelve that count day-ahead: {n['da_months']}",
             f"bought day-ahead, a flat load, the same twelve months, USD per MWh: {n['da_usd_mwh']:.2f}",
             f"months held: {n['months_held']}, {n['first_held']} to {n['last_held']}",
             f"months that count: {n['months_counted']}"]
    lines += [f"year {y['year']}: months that count {y['months']}, a flat load, USD per MWh: " + (f"{y['usd_mwh']:.2f}" if y["usd_mwh"] is not None else ".") for y in n["years"]]
    lines += [f"months that count of the 36: {n['w36_months']}, {n['w36_first']} to {n['w36_last']}",
              f"a bad month, nearest rank {n['bad_rank']}: {n['bad_month']}, USD per MWh: {n['bad_usd_mwh']:.2f}",
              f"the bad month's cost for 100 MW, USD: {n['bad_usd']:,.0f}"]
    # session 228
    lines += [f"hours of the last twelve months at or above USD {SCARCITY_USD:.0f} per MWh: {n['scarce_hours']}",
              f"what a flat load of 100 MW paid in them, USD: {n['scarce_usd']:,.0f}",
              f"the months they fell in: {', '.join(n['scarce_months']) if n['scarce_months'] else 'none'}",
              "the clock hours they fell in, standard time: " + (f"{n['scarce_clock'][0]:02d}:00 to {n['scarce_clock'][1] + 1:02d}:00" if n["scarce_clock"] else "none")]
    if "co2_kg_mwh" in n:
        lines += [f"months of the twelve with an intensity: {n['co2_months']}",
                  f"this load's carbon, last twelve months at the grid's monthly average, kg CO2 per MWh: {n['co2_kg_mwh']:.2f}",
                  f"tonnes of CO2 a year for 100 MW: {n['co2_tonnes']:,.0f}",
                  f"hours of the hourly window the price and the intensity are both held: {n['window_hours']}, {n['window_from']} to {n['window_to']}",
                  f"a flat load's own hours over them, kg CO2 per MWh (the grid's mean): {n['window_kg_mwh']:.2f}"]
        lines += [f"year {y}: months held {k}, kg CO2 per MWh: {v:.2f}" for y, v, k in n["co2_years"]]
    return lines


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_NAME)
    rows = read(path)
    n = numbers(rows)
    n["rows"] = rows
    carbon_path = os.path.join(os.path.dirname(os.path.abspath(path)), CARBON_NAME)
    if os.path.exists(carbon_path):
        n.update(carbon(carbon_path, n))
    print("\n".join(report(n)))
