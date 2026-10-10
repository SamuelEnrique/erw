#!/usr/bin/env python3
"""ERW, What a generator earns (/cost-of-power/seller): the headline numbers of the default case, rebuilt from
erw_2026_generator_hourly.csv. The Python mirror of erw_2026_generator_replication.do, step for step, for a reader
without Stata. Standard library only. It prints the do-file's lines, without Stata's padding of a number.

    python erw_2026_generator_replication.py [erw_2026_generator_hourly.csv]

The default case: ERCOT, solar, 100 MW, priced at the hub average (HB_HUBAVG) in real time. Method:
docs/methods/cost_of_power.md.
"""

import calendar
import csv
import math
import os
import sys

CSV_NAME = "erw_2026_generator_hourly.csv"
HEADER_LINES = 16            # the do-file: varnames(17) rowrange(18)
SENTINEL = -99999.0          # solar_mwh: EIA's value for the hour is blank
NUMERIC = ["price_usd_mwh", "solar_mwh", "nameplate_mw", "in_last_twelve"]
RECODED = ["solar_mwh"]
CAPTURE_FIRST = "2019-01"    # the do-file: ym >= tm(2019m1)
CAPTURE_SUMS = ["capture_usd", "capture_mwh", "capture_price_sum", "capture_hours"]
# The reader's inputs at their defaults (the do-file's scalars)
MW, FOM_USD_KW_YEAR, CAPEX_USD_KW, DEBT_SHARE, DEBT_RATE, DEBT_YEARS = 100, 12.5, 1375, 0.6, 0.08, 35


def stata_round(v):
    """Stata's round(): to the nearest whole number, a half away from zero."""
    return math.copysign(math.floor(abs(v) + 0.5), v)


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
    """import delimited ..., varnames(17) rowrange(18) stringcols(_all); then destring and the sentinel recode."""
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
    out["debt_service"] = int(stata_round(CAPEX_USD_KW * 1000 * DEBT_SHARE * DEBT_RATE / (1 - (1 + DEBT_RATE) ** (-DEBT_YEARS)) * MW))
    # hour by hour, then collapse to one row a local month
    months = {}
    for r in rows:
        price, solar, nameplate = r["price_usd_mwh"], r["solar_mwh"], r["nameplate_mw"]
        output = solar / nameplate if solar is not None and nameplate is not None and nameplate > 0 else None
        model_hour = output is not None and price is not None
        revenue = price * output if model_hour else None
        capture_hour = solar is not None and price is not None and r["local_month"] >= CAPTURE_FIRST
        m = months.setdefault(r["local_month"], dict(ym=r["local_month"], revenue_usd_per_mw=0.0, energy_mwh_per_mw=0.0, hours=0, capture_hours=0,
                                                     capture_price_sum=0.0, capture_mwh=0.0, capture_usd=0.0, in_last_twelve=0))
        if revenue is not None:                       # collapse (sum): a missing value adds nothing
            m["revenue_usd_per_mw"] += revenue
        if output is not None:
            m["energy_mwh_per_mw"] += output
        m["hours"] += int(model_hour)
        if capture_hour:
            m["capture_hours"] += 1
            m["capture_price_sum"] += price
            m["capture_mwh"] += max(0.0, solar)
            m["capture_usd"] += price * max(0.0, solar)
        m["in_last_twelve"] = max(m["in_last_twelve"], int(r["in_last_twelve"]))
    table = sorted(months.values(), key=lambda x: x["ym"])
    for m in table:
        y, mo = int(m["ym"][:4]), int(m["ym"][5:7])
        m["hours_in_month"] = 24 * calendar.monthrange(y, mo)[1] - (mo == 3) + (mo == 11)
        m["held"] = m["hours"] / m["hours_in_month"] >= 0.9 - 1e-9 and m["energy_mwh_per_mw"] > 0
        m["capture_counted"] = m["capture_hours"] >= 0.95 * m["hours_in_month"] - 1e-9
        m["revenue_usd_per_mw"] = stata_round(m["revenue_usd_per_mw"] * 10000) / 10000     # the snapshot's four decimals
        m["revenue_usd"] = m["revenue_usd_per_mw"] * MW
        m["cfads_usd"] = m["revenue_usd"] - FOM_USD_KW_YEAR * 1000 * MW / 12
        m["cover"] = m["cfads_usd"] / (out["debt_service"] / 12)
        m["calendar_year"] = y
    # revenue, last twelve months
    flagged = [m for m in table if m["in_last_twelve"] == 1]
    out["l12_first"], out["l12_last"] = (flagged[0]["ym"], flagged[-1]["ym"]) if flagged else (None, None)
    l12 = [m for m in flagged if m["held"]]
    out["l12_usd_per_mw"] = sum(m["revenue_usd_per_mw"] for m in l12)
    out["l12_months"] = len(l12)
    out["l12_kw"] = out["l12_usd_per_mw"] / 1000
    # the long-run averages
    held_in_year = {}
    for m in table:
        held_in_year[m["calendar_year"]] = held_in_year.get(m["calendar_year"], 0) + int(m["held"])
    for m in table:
        m["full_year"] = held_in_year[m["calendar_year"]] == 12
    full = [m for m in table if m["full_year"]]
    out["first_full_year"], out["last_full_year"] = (min(m["calendar_year"] for m in full), max(m["calendar_year"] for m in full)) if full else (None, None)
    out["full_years"] = len(full) // 12
    out["three_from"] = out["last_full_year"] - 2 if full else None
    three = [m for m in full if m["calendar_year"] >= out["three_from"]]
    out["three_months"] = len(three)                 # 36 when the three years are all full
    out["three_kw"] = sum(m["revenue_usd_per_mw"] for m in three) / 3 / 1000
    out["every_kw"] = sum(m["revenue_usd_per_mw"] for m in full) / out["full_years"] / 1000 if full else None
    # the price received at the hub average
    counted = [m for m in flagged if m["capture_counted"]]
    out["capture_months"] = len(counted)
    s = {v: sum(m[v] for m in counted) for v in CAPTURE_SUMS}
    out["capture_hours"] = s["capture_hours"]
    out["price_received"] = s["capture_usd"] / s["capture_mwh"]
    out["flat_average"] = s["capture_price_sum"] / s["capture_hours"]
    out["difference"] = out["price_received"] - out["flat_average"]
    out["difference_pct"] = 100 * (out["price_received"] - out["flat_average"]) / out["flat_average"]
    # debt coverage, last twelve months
    out["cover"] = (out["l12_usd_per_mw"] * MW - FOM_USD_KW_YEAR * 1000 * MW) / out["debt_service"]
    # trailing twelve months
    cum = 0.0
    for i, m in enumerate(table):
        before = table[i - 1] if i else None
        m["streak"] = int(m["held"])
        if m["held"] and before is not None and before["ym"] == month_before(m["ym"], 1):
            m["streak"] = before["streak"] + 1
        cum += m["cfads_usd"]
        m["cum_cfads_usd"] = cum
        m["ttm_cover"] = (cum - (table[i - 12]["cum_cfads_usd"] if i >= 12 else 0)) / out["debt_service"] if m["streak"] >= 12 else None
    windows = [m for m in table if m["ttm_cover"] is not None]
    out["newest_window"] = windows[-1]["ym"] if windows else None
    out["newest_window_cover"] = windows[-1]["ttm_cover"] if windows else None
    out["windows"] = len(windows)
    out["ttm_min"] = min(m["ttm_cover"] for m in windows) if windows else None
    out["ttm_under1"] = sum(1 for m in windows if m["ttm_cover"] < 1)
    out["ttm_under125"] = sum(1 for m in windows if m["ttm_cover"] < 1.25)
    # month by month, for 100 MW
    held = [m for m in table if m["held"]]
    out["n"] = len(held)
    out["first_held"], out["last_held"] = (held[0]["ym"], held[-1]["ym"]) if held else (None, None)
    out["under1"] = sum(1 for m in held if m["cover"] < 1)
    out["under125"] = sum(1 for m in held if m["cover"] < 1.25)
    out["annual_mean"] = sum(m["revenue_usd"] for m in held) / len(held) * 12 if held else None
    # the median month, the 10th-percentile month (nearest rank) and the worst three
    ranked = sorted(held, key=lambda m: (m["revenue_usd"], m["ym"]))
    median_rank, p10_rank = max(1, math.ceil(0.5 * len(ranked))), max(1, math.ceil(0.1 * len(ranked)))
    out["median_month"], out["median_usd"] = ranked[median_rank - 1]["ym"], ranked[median_rank - 1]["revenue_usd"]
    out["p10_month"], out["p10_usd"] = ranked[p10_rank - 1]["ym"], ranked[p10_rank - 1]["revenue_usd"]
    out["worst"] = [(m["ym"], m["revenue_usd"]) for m in ranked[:3]]
    out["months"] = table
    return out


def report(n):
    lines = [f"the last twelve months: {n['l12_first']} to {n['l12_last']}",
             f"months in the last twelve that are held: {n['l12_months']}",
             f"revenue, last twelve months, USD per kW: {n['l12_kw']:.2f}",
             f"the last three full years: {n['three_from']} to {n['last_full_year']}, months held in them: {n['three_months']}",
             f"long-run average of the last three full years, USD per kW a year: {n['three_kw']:.2f}",
             f"full years held: {n['full_years']}, {n['first_full_year']} to {n['last_full_year']}",
             f"long-run average of every full year held, USD per kW a year: {n['every_kw']:.2f}",
             f"months in the last twelve that count for the capture price: {n['capture_months']}",
             f"hours used for the capture price: {n['capture_hours']}",
             f"price received, weighted by generation, USD per MWh: {n['price_received']:.2f}",
             f"flat average over the same hours, USD per MWh: {n['flat_average']:.2f}",
             f"difference, USD per MWh: {n['difference']:.2f}",
             f"difference, percent of the flat average: {n['difference_pct']:.1f}",
             f"annual debt payments, USD: {n['debt_service']:,}",
             f"debt coverage, last twelve months, times: {n['cover']:.2f}",
             f"the newest twelve-month window ends {n['newest_window']}, coverage, times: {n['newest_window_cover']:.2f}",
             f"twelve-month windows: {n['windows']}",
             f"lowest twelve-month coverage, times: {n['ttm_min']:.2f}",
             f"twelve-month windows under 1.0 times: {n['ttm_under1']}",
             f"twelve-month windows under 1.25 times: {n['ttm_under125']}",
             f"months held: {n['n']}, {n['first_held']} to {n['last_held']}",
             f"months held that covered less than 1.0 times: {n['under1']}",
             f"months held that covered less than 1.25 times: {n['under125']}",
             f"the year's average, twelve times the mean month, USD for 100 MW: {n['annual_mean']:,.2f}",
             f"median month: {n['median_month']}, USD for 100 MW: {n['median_usd']:,.2f}",
             f"10th-percentile month, nearest rank: {n['p10_month']}, USD for 100 MW: {n['p10_usd']:,.2f}"]
    lines += [f"worst month {i}: {m}, USD for 100 MW: {v:,.2f}" for i, (m, v) in enumerate(n["worst"], 1)]
    return lines


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_NAME)
    print("\n".join(report(numbers(read(path)))))
