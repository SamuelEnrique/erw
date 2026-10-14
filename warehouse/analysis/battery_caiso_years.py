#!/usr/bin/env python3
"""The CAISO battery, year by year, beside the market monitor (session 273). Changes no table.

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "CAISO beside its market monitor". Session 273 pulled
CAISO's prices back to July 2023, so 2024 is a whole year held as well as 2025. This runs session 246's comparison
(warehouse/analysis/battery_caiso_dmm.py: the page's model, and the same program the market monitor's way) for each
whole year, and sets beside it what the market monitor published for the real fleet:

    2025   "nearly $35/kW-yr in market revenues for energy and $9/kW-yr for regulation" (2025 Annual Report, section 1.3.3)
    2024   "Net market revenue for these resources was $53/kW-yr in 2024", "nearly 82 percent" from energy
           (2024 Special Report on Battery Storage, 29 May 2025, section 2.9.1)

    python warehouse/analysis/battery_caiso_years.py

Writes warehouse/output/analysis_internal/battery_caiso_years.csv (USD per kW by year, variant, strategy, duration)
and prints the 4-hour day-ahead rows. No request: the published figures are typed below from the reports.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import battery_caiso_dmm as d  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_caiso_years.csv")
YEARS = ("2024", "2025")
FLEET = {"2025": "energy 35, regulation 9 (2025 Annual Report, section 1.3.3)",
         "2024": "53 in all, nearly 82 percent from energy (2024 Special Report on Battery Storage, section 2.9.1)"}


def main():
    out = []
    for y in YEARS:
        d.YEAR = y
        page, left = d.run("page")
        dmm, _ = d.as_dmm()
        q = d.quarters(pd.concat([page, dmm], ignore_index=True))
        q = q[q["quarter"] == "year"].assign(year=y, days_left_out="; ".join(f"{a} {b}" for a, b in left))
        out.append(q)
    t = pd.concat(out, ignore_index=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal (session 273): CAISO at the SP15 hub, each whole year held, USD per kW; variant page (the page's "
                "model) and as_dmm (Regulation Up and Down only, round trip 0.85); warehouse/analysis/battery_caiso_years.py\n")
        t.to_csv(f, index=False, lineterminator="\n")
    show = t[t["duration_h"] == 4]
    print(show[["year", "variant", "strategy", "days", "energy", "regulation", "reserves", "total"]].to_string(index=False))
    for y in YEARS:
        print(f"the real fleet, {y}: {FLEET[y]}")
    print(f"written: {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
