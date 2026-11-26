"""Audit of Automated Analysis (session 10204): does the "Batteries ate their own lunch?" fit depend on its first year?

Runs the card's own module (warehouse/analysis/findings/batteries_lunch.py: compute, then numbers_from_rows) at
first years 2019 (the default and the only choice the page offers below 2020), 2017 and 2015, reading the main
checkout's tables (never written). No model, no network.

Run: python runs/a9_lunch_start.py <folder of the tables> > runs/a9.out
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import batteries_lunch as bl  # noqa: E402

D = sys.argv[1]


def main():
    keys = ("reg_multiple_coef", "reg_multiple_se", "reg_multiple_p", "reg_multiple_r2")
    for fy in (2019, 2017, 2015):
        rows, meta = bl.compute({"first_year": fy}, D)
        n, f = bl.numbers_from_rows(rows, meta)
        print(f"first year {fy}: " + ", ".join(f"{k} {n[k]:.6g}" for k in keys)
              + f"; regression months {n['reg_n']} ({n['reg_first']} to {n['reg_last']}); fleet first month {n['fleet_first_month']} {n['fleet_first_mw']} MW")


if __name__ == "__main__":
    main()
