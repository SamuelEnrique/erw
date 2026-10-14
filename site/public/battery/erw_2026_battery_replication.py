#!/usr/bin/env python3
"""ERW, What a battery earns (/cost-of-power/battery): the headline numbers of the default case, rebuilt from
erw_2026_battery_dispatch.csv. The Python mirror of erw_2026_battery_replication.do, step for step, for a reader
without Stata. Standard library only.

    python erw_2026_battery_replication.py [erw_2026_battery_dispatch.csv]

The default case: ERCOT, a 4-hour battery, perfect foresight, 100 MW. Method: docs/methods/battery_earns_algorithm.md.
Session 263: the defaults are the page's since the owner's ruling of 12 October 2026 (20 percent debt, a hurdle rate of
12 percent), and the file rebuilds scenario A's column too: NPV at the hurdle rate, IRR, the breakeven toll and the
merchant tail, line for line with site/lib/battery/finance.ts.
"""

import calendar
import csv
import math
import os
import sys

CSV_NAME = "erw_2026_battery_dispatch.csv"
HEADER_LINES = 14            # the do-file: varnames(15) rowrange(16)
SENTINEL = -999.0
PRODUCTS = ["regup", "regdn", "rrs", "ecrs", "nspin"]
STREAMS = ["energy"] + PRODUCTS + ["ancillary", "total"]
NUMERIC = (["hour_of_day", "in_last_twelve", "switch_used", "price_energy_usd_mwh"] + [f"price_{k}_usd_mw" for k in PRODUCTS]
           + ["charge_mw", "discharge_mw", "soc_mwh"] + [f"award_{k}_mw" for k in PRODUCTS]
           + ["revenue_energy_usd"] + [f"revenue_{k}_usd" for k in PRODUCTS] + ["revenue_ancillary_usd", "revenue_total_usd"])
RECODED = [f"{a}_{k}_{u}" for a, u in (("price", "usd_mw"), ("award", "mw"), ("revenue", "usd")) for k in PRODUCTS]
# The reader's inputs at their defaults (the do-file's scalars): Lazard LCOE+ June 2025, its storage cases
MW, FOM_USD_KW_YEAR, CAPEX_USD_KW, DEBT_SHARE, DEBT_RATE, DEBT_YEARS = 100, 22, 1110, 0.2, 0.08, 20
LIFE_YEARS, DEGRADATION, HURDLE_PCT, TOLL_TARGET = 20, 0.026, 12, 1.25
IRR_LOW, IRR_HIGH = -99, 1000                     # the bracket of the IRR search, percent a year


def npv_kw(rate_pct, revenue_kw, debt_kw, debt_years):
    """The NPV to equity, USD per kW, at rate_pct percent: equity paid in at year 0, then each year's revenue (cut by the
    degradation each year after the first) less fixed O&M less the debt payment while the debt lasts (finance.ts, flows
    and npv; no contract)."""
    v = -CAPEX_USD_KW * (1 - DEBT_SHARE)
    for t in range(1, LIFE_YEARS + 1):
        flow = revenue_kw * (1 - DEGRADATION) ** (t - 1) - FOM_USD_KW_YEAR - (debt_kw if t <= debt_years else 0)
        v += flow / (1 + rate_pct / 100) ** t
    return v


def irr_pct(revenue_kw, debt_kw, debt_years):
    """finance.ts, irr: bisection between -99 and 1,000 percent, at most 200 halvings or until the bracket is 1e-10 wide;
    None when the NPV has the same sign at both ends."""
    lo, hi = IRR_LOW, IRR_HIGH
    flo, fhi = npv_kw(lo, revenue_kw, debt_kw, debt_years), npv_kw(hi, revenue_kw, debt_kw, debt_years)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if (flo > 0) == (fhi > 0):
        return None
    for _ in range(200):
        if hi - lo <= 1e-10:
            break
        mid = (lo + hi) / 2
        fm = npv_kw(mid, revenue_kw, debt_kw, debt_years)
        if fm == 0:
            return mid
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def half_up(v):
    """Stata's round() and JavaScript's Math.round() on a positive number: halves go up."""
    return math.floor(v + 0.5)


def destring(v):
    """destring, replace force: a number, or missing (None) when the text is not one."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def read(path):
    """import delimited ..., varnames(15) rowrange(16) stringcols(_all); then destring and the sentinel recodes."""
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
    debt_years = min(DEBT_YEARS, LIFE_YEARS)                     # the term, cut to the project life
    crf = DEBT_RATE / (1 - (1 + DEBT_RATE) ** (-debt_years))
    out["debt_service"] = half_up(CAPEX_USD_KW * 1000 * DEBT_SHARE * crf * MW)
    out["debt_kw"] = CAPEX_USD_KW * DEBT_SHARE * crf             # USD per kW a year
    # revenue is price times megawatts, hour by hour
    out["check_energy"] = max(abs(r["revenue_energy_usd"] - r["price_energy_usd_mwh"] * (r["discharge_mw"] - r["charge_mw"])) for r in rows)
    for k in PRODUCTS:
        ds = [abs(r[f"revenue_{k}_usd"] - r[f"price_{k}_usd_mw"] * r[f"award_{k}_mw"]) for r in rows if r[f"revenue_{k}_usd"] is not None]
        out[f"check_{k}"] = max(ds) if ds else None
    # collapse to one row a local month
    months = {}
    for r in rows:
        m = months.setdefault(r["local_month"], dict(month=r["local_month"], days=set(), in_last_twelve=0, **{f"revenue_{k}_usd": 0.0 for k in STREAMS}))
        for k in STREAMS:
            m[f"revenue_{k}_usd"] += r[f"revenue_{k}_usd"] or 0.0      # collapse (sum): a missing value adds nothing
        m["days"].add(r["local_day"])
        m["in_last_twelve"] = max(m["in_last_twelve"], int(r["in_last_twelve"]))
    table = []
    for m in sorted(months.values(), key=lambda x: x["month"]):
        m["days_held"] = len(m.pop("days"))
        m["days_in_month"] = calendar.monthrange(int(m["month"][:4]), int(m["month"][5:7]))[1]
        m["held"] = m["days_held"] / m["days_in_month"] >= 0.9 - 1e-9
        table.append(m)
    # the last twelve months
    l12 = [m for m in table if m["in_last_twelve"] == 1 and m["held"]]
    for k in STREAMS:
        out[f"l12_{k}"] = sum(m[f"revenue_{k}_usd"] for m in l12)
        out[f"l12_{k}_usd"] = half_up(out[f"l12_{k}"] * MW)
    out["l12_months"] = len(l12)
    out["l12_first"], out["l12_last"] = (l12[0]["month"], l12[-1]["month"]) if l12 else (None, None)
    out["l12_kw_total"] = out["l12_total"] / 1000
    out["l12_share_ancillary"] = half_up(100 * out["l12_ancillary"] / out["l12_total"])
    out["cover"] = (out["l12_total"] * MW - FOM_USD_KW_YEAR * 1000 * MW) / out["debt_service"]
    # scenario A at its defaults: the last twelve months' revenue every year of the life (finance.ts, resultOf)
    rev = out["l12_kw_total"]
    out["a_coverage"] = (rev - FOM_USD_KW_YEAR) / out["debt_kw"]
    out["npv_kw"] = npv_kw(HURDLE_PCT, rev, out["debt_kw"], debt_years)
    out["npv_usd"] = half_up(out["npv_kw"] * 1000 * MW)
    out["irr"] = irr_pct(rev, out["debt_kw"], debt_years)
    out["toll"] = (TOLL_TARGET * out["debt_kw"] + FOM_USD_KW_YEAR) / 12
    out["tail_years"] = max(0, LIFE_YEARS - debt_years)
    out["tail_usd"] = half_up(sum((rev * (1 - DEGRADATION) ** (t - 1) - FOM_USD_KW_YEAR) / (1 + HURDLE_PCT / 100) ** t
                                  for t in range(debt_years + 1, LIFE_YEARS + 1)) * 1000 * MW)
    # the chart's full calendar years inside the file
    for y in ("2024", "2025"):
        ys = [m for m in table if m["month"][:4] == y and m["held"]]
        out[f"year_{y}_months"] = len(ys)
        out[f"year_{y}_energy_kw"] = sum(m["revenue_energy_usd"] for m in ys) / 1000
        out[f"year_{y}_ancillary_kw"] = sum(m["revenue_ancillary_usd"] for m in ys) / 1000
    # a bad month: nearest rank
    held = sorted((m for m in table if m["held"]), key=lambda m: (m["revenue_total_usd"], m["month"]))
    out["n36"] = len(held)
    rank = max(1, math.ceil(0.1 * len(held)))
    out["bad_month"] = held[rank - 1]["month"]
    out["p10_36_usd"] = half_up(held[rank - 1]["revenue_total_usd"] * MW)
    out["months"] = table
    return out


def report(n):
    lines = [f"largest difference, energy revenue against price times megawatts, USD: {n['check_energy']:.8f}"]
    lines += [f"largest difference, {k} revenue against price times megawatts, USD: {n[f'check_{k}']:.8f}" for k in PRODUCTS]
    lines += [f"last twelve months, {k}, USD for 100 MW: {n[f'l12_{k}_usd']:,}" for k in STREAMS]
    lines += [f"months in the last twelve that are held: {n['l12_months']}",
              f"last twelve months, all streams, USD per kW: {n['l12_kw_total']:.2f}",
              f"share from ancillary services, percent: {n['l12_share_ancillary']}",
              f"annual debt payments, USD: {n['debt_service']:,}",
              f"debt coverage, last twelve months, times: {n['cover']:.2f}",
              f"scenario A, debt coverage, times: {n['a_coverage']:.2f}",
              f"scenario A, NPV at the hurdle rate, USD per kW: {n['npv_kw']:.2f}",
              f"scenario A, NPV at the hurdle rate, USD for 100 MW: {n['npv_usd']:,}",
              "scenario A, IRR, percent a year: " + ("none" if n["irr"] is None else f"{n['irr']:.1f}"),
              f"scenario A, breakeven toll, USD per kW-month: {n['toll']:.2f}",
              f"scenario A, merchant tail, years: {n['tail_years']}, USD for 100 MW: {n['tail_usd']:,}"]
    lines += [f"calendar year {y}, months held: {n[f'year_{y}_months']}, energy USD per kW: {n[f'year_{y}_energy_kw']:.2f}, "
              f"ancillary USD per kW: {n[f'year_{y}_ancillary_kw']:.2f}" for y in ("2024", "2025")]
    lines += [f"months held of the 36: {n['n36']}", f"a bad month: {n['bad_month']}, USD for 100 MW: {n['p10_36_usd']:,}"]
    return lines


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_NAME)
    print("\n".join(report(numbers(read(path)))))
