#!/usr/bin/env python3
"""The CAISO battery beside CAISO's market monitor's own figures for 2025 (session 246). Changes no table.

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "CAISO beside its market monitor (session 246)".

    python warehouse/analysis/battery_caiso_dmm.py

CAISO's Department of Market Monitoring models a battery much as this model does. Its 2025 Annual Report on Market
Issues and Performance (June 2026, section 1.3.3, Tables 1.7 and 1.8,
https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf) gives, by quarter of 2025,
the day-ahead revenue of a hypothetical 100 MW, 4-hour battery with a round trip of 0.85 that sells energy and
regulation (up and down) at each of more than 280 pricing nodes, and beside it what the real fleet was paid.

This runs the page's own builder (battery_stack.build_market) on CAISO twice and adds up the days of 2025 by quarter:

  page     the model as the page shows it: energy and all four reserves, round trip 0.86
  as_dmm   the same program with the market monitor's two choices this model can take: Regulation Up and Regulation
           Down only (no Spinning or Non-Spinning Reserve), and a round trip of 0.85

What it cannot take from the market monitor's model, and so what is left in the gap: its nodes (this model prices
energy at the SP15 hub), its monthly horizon with no limit on cycles (this model solves each day from empty, at most
one full cycle), and the energy its regulation awards are assumed to deploy (here an award is paid and moves no energy).

Writes warehouse/output/analysis_internal/battery_caiso_dmm_2025.csv (USD per kW, by variant, strategy, duration and
quarter) and prints the 4-hour day-ahead rows beside the market monitor's table. No request: the published figures
are typed below from the report, each with its page.
"""

import copy
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_caiso_dmm_2025.csv")
YEAR = "2025"
DMM_RTE = 0.85
REPORT = "CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026"
URL = "https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf"
# Table 1.8, "New battery net day-ahead market revenues by local capacity area", net revenues for energy and
# regulation, USD per kW-year, the report's page 120: (2025 Q1, Q2, Q3, Q4, Total)
DMM_TABLE_1_8 = {
    "CAISO System": (28.8, 22.8, 14.2, 11.5, 77.3),
    "LA Basin (SCE)": (21.9, 19.1, 11.0, 10.5, 62.6),
    "Big Creek/Ventura (SCE)": (22.9, 19.3, 11.2, 10.8, 64.2),
    "San Diego/Imperial Valley (SDG&E)": (22.3, 19.6, 12.8, 11.5, 66.3),
    "Greater Fresno (PG&E)": (39.6, 33.7, 24.0, 14.5, 111.7),
}
# the report's pages 119 and 120: "simulated revenues across all pricing nodes were $39/kW-yr for energy and $39/kW-year
# for regulation. Actual batteries in the CAISO balancing area with a full year of operation in 2025 had nearly
# $35/kW-yr in market revenues for energy and $9/kW-yr for regulation"
DMM_SIMULATED = {"energy": 39.0, "regulation": 39.0}
DMM_ACTUAL = {"energy": 35.0, "regulation": 9.0}


def run(variant):
    m = bs.MARKETS["caiso"]
    energy = {mk: bs.energy_prices("caiso", mk, lambda s: None)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices(m["as_table"], m["products"])
    days, left = bs.build_market("caiso", energy, reserve, lambda s: None, until=f"{YEAR}-12-31")
    rows = []
    for (strat, dur), dd in days.items():
        for day, v in dd.items():
            if day[:4] != YEAR:
                continue
            rows.append(dict(variant=variant, strategy=strat, duration_h=dur, day=day, energy=v["energy"],
                             regulation=v.get("regup", 0.0) + v.get("regdn", 0.0), reserves=v.get("spin", 0.0) + v.get("nonspin", 0.0),
                             total=v["total"]))
    out = [(d, why) for d, why in left["dayahead"] if d[:4] == YEAR]
    return pd.DataFrame(rows), out


def as_dmm():
    """The builder with Regulation Up and Down only and a round trip of 0.85, then everything put back."""
    saved = copy.deepcopy(bs.MARKETS["caiso"]["products"])
    solve, check = bs.solve_day, bs.check_day
    try:
        bs.MARKETS["caiso"]["products"] = [p for p in saved if p["key"] in ("regup", "regdn")]
        bs.ALL_MARKETS["caiso"] = bs.MARKETS["caiso"]
        bs.solve_day = lambda e, r, spec, dur, **k: solve(e, r, spec, dur, **{**k, "rte": DMM_RTE})
        bs.check_day = lambda sol, spec, dur, **k: check(sol, spec, dur, **{**k, "rte": DMM_RTE})
        return run("as_dmm")
    finally:
        bs.MARKETS["caiso"]["products"] = saved
        bs.ALL_MARKETS["caiso"] = bs.MARKETS["caiso"]
        bs.solve_day, bs.check_day = solve, check


def quarters(d):
    d = d.assign(quarter="Q" + ((d["day"].str[5:7].astype(int) - 1) // 3 + 1).astype(str))
    q = d.groupby(["variant", "strategy", "duration_h", "quarter"]).agg(days=("day", "nunique"), energy=("energy", "sum"), regulation=("regulation", "sum"),
                                                                        reserves=("reserves", "sum"), total=("total", "sum")).reset_index()
    y = d.groupby(["variant", "strategy", "duration_h"]).agg(days=("day", "nunique"), energy=("energy", "sum"), regulation=("regulation", "sum"),
                                                             reserves=("reserves", "sum"), total=("total", "sum")).reset_index().assign(quarter="year")
    out = pd.concat([q, y], ignore_index=True)
    for c in ("energy", "regulation", "reserves", "total"):
        out[c] = (out[c] / 1000).round(2)   # USD per MW to USD per kW
    return out.sort_values(["variant", "strategy", "duration_h", "quarter"]).reset_index(drop=True)


def main():
    page, left = run("page")
    dmm, _ = as_dmm()
    q = quarters(pd.concat([page, dmm], ignore_index=True))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal, for review (session 246): CAISO at the SP15 hub, the days of 2025 the model holds, USD per kW by quarter "
                "and for the year; variant page (the model as the page shows it) and as_dmm (Regulation Up and Down only, round trip 0.85: the two "
                f"choices of {REPORT}, Table 1.7, that the model can take); warehouse/analysis/battery_caiso_dmm.py\n")
        f.write(f"# Days of {YEAR} left out (never filled): " + ("; ".join(f"{d} {why}" for d, why in left) or "none") + "\n")
        q.to_csv(f, index=False, lineterminator="\n")
    show = q[(q["duration_h"] == 4)].pivot_table(index=["variant", "strategy"], columns="quarter", values=["energy", "regulation", "reserves", "total", "days"])
    print(f"CAISO, SP15, 4 hours, {YEAR}, USD per kW (days: the days held)")
    print(show.to_string())
    print(f"\ndays of {YEAR} left out:", "; ".join(f"{d} {why}" for d, why in left) or "none")
    print(f"\n{REPORT}, Table 1.8 (USD per kW-year, energy and regulation, day-ahead; Q1, Q2, Q3, Q4, total):")
    for k, v in DMM_TABLE_1_8.items():
        print(f"  {k}: {v}")
    print(f"  simulated, all nodes: energy {DMM_SIMULATED['energy']}, regulation {DMM_SIMULATED['regulation']}; the real fleet: energy {DMM_ACTUAL['energy']}, regulation {DMM_ACTUAL['regulation']}")
    print(f"written: {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
