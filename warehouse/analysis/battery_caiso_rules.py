#!/usr/bin/env python3
"""CAISO's verified duration rules against the assumed hour, for review (session 74). Changes no table.

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "California's rules, verified (session 74)".

    python warehouse/analysis/battery_caiso_rules.py

Session 67 assumed every CAISO reserve needs one hour of stored energy behind it. CAISO's tariff (Section 8, as of
1 May 2026, https://www.caiso.com/documents/section-8-ancillary-services-as-of-may-1-2026.pdf):
- 8.4.1.1(g): "Regulation capacity offered must be dispatchable on a continuous basis for at least sixty (60) minutes in
  the Day-Ahead Market and at least thirty (30) minutes in the Real-Time Market": the model's awards are day-ahead, so
  one hour stands for Regulation Up and Down.
- 8.4.3: "Each resource scheduled to provide Spinning Reserve and each resource scheduled to provide Non-Spinning Reserve
  must be capable of maintaining that output ... for at least thirty (30) minutes": half an hour, not one.

This runs the page's own builder (battery_stack.build_market) on CAISO twice, the assumed rules and the verified ones,
and writes the yearly sums of both to warehouse/output/analysis_internal/battery_caiso_rules_yearly.csv.
"""

import copy
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_caiso_rules_yearly.csv")
TARIFF = ("CAISO tariff Section 8 as of 2026-05-01, section 8.4.3: Spinning and Non-Spinning Reserve maintained for at "
          "least thirty (30) minutes")


def run(rules):
    m = bs.MARKETS["caiso"]
    energy = {mk: bs.energy_prices("caiso", mk, print)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices(m["as_table"], m["products"])
    days, left = bs.build_market("caiso", energy, reserve, print)
    rows = []
    for (strat, dur), dd in days.items():
        for day, v in dd.items():
            rows.append(dict(rules=rules, strategy=strat, duration_h=dur, day=day, **{k: v.get(k, 0.0) for k in ["energy", "total", "regup", "regdn", "spin", "nonspin"]}))
    return pd.DataFrame(rows)


def main():
    assumed = run("assumed_1h")
    saved = copy.deepcopy(bs.MARKETS["caiso"]["products"])
    try:
        for p in bs.MARKETS["caiso"]["products"]:
            if p["key"] in ("spin", "nonspin"):
                p["hours"] = [("2024-09-01", 0.5, TARIFF)]
        verified = run("verified_tariff")
    finally:
        bs.MARKETS["caiso"]["products"] = saved
    d = pd.concat([assumed, verified], ignore_index=True)
    d["year"] = d["day"].str.slice(0, 4)
    y = d.groupby(["rules", "strategy", "duration_h", "year"]).agg(days=("day", "nunique"), energy=("energy", "sum"), total=("total", "sum"),
                                                                    regup=("regup", "sum"), regdn=("regdn", "sum"), spin=("spin", "sum"),
                                                                    nonspin=("nonspin", "sum")).reset_index()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal, for review (session 74): CAISO SP15, USD per MW by calendar year (the held days), the page's "
                "program under the assumed one-hour rules and under the tariff's (Spinning and Non-Spinning Reserve 30 minutes, "
                "section 8.4.3; Regulation 60 minutes day-ahead, section 8.4.1.1(g)); warehouse/analysis/battery_caiso_rules.py\n")
        y.round(4).to_csv(f, index=False, lineterminator="\n")
    print(y.assign(total_kw=(y["total"] / 1000).round(1), anc_kw=((y["total"] - y["energy"]) / 1000).round(1),
                   spin_kw=(y["spin"] / 1000).round(2), nonspin_kw=(y["nonspin"] / 1000).round(2))
          [["rules", "strategy", "duration_h", "year", "days", "total_kw", "anc_kw", "spin_kw", "nonspin_kw"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
