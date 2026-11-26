"""Audit of Automated Analysis (session 10204): the hunt's five tests under a series with no trend.

Runs the engine's own hunt.test_claim on simulated yearly series that have no trend at all:
  iid: independent normal years (a level with noise);
  rw: a random walk (each year the last plus independent normal noise; no drift);
  ar: AR(1) with rho 0.7 (persistent, mean-reverting, no trend).
For each length of full years (the forty's lengths) it prints the share of series that pass all five tests.
Also: a straight line with no noise, its strength by length (the strength counts years, not signal).
Run: python runs/a1_hunt_null.py  (ERW_SPEND_CAP_USD=0; no model, no table, no network)
"""
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import hunt  # noqa: E402

P = {"n_floor": 1, "decimals": 2, "unit": "u"}
LENGTHS = [6, 7, 9, 11, 25, 45]
N = 4000
rng = np.random.default_rng(10204)


def series_of(vals, start=2000):
    return {str(start + i): (float(v), 1.0) for i, v in enumerate(vals)}


def sim(kind, n):
    e = rng.standard_normal(n)
    if kind == "iid":
        return e
    if kind == "rw":
        return np.cumsum(e)
    x = np.zeros(n)
    x[0] = e[0] / np.sqrt(1 - 0.49)
    for i in range(1, n):
        x[i] = 0.7 * x[i - 1] + e[i]
    return x


def main():
    print("kind,full_years,share_passing_all_five,share_p_trend_below_0.05,median_strength_of_passing")
    for kind in ("iid", "ar", "rw"):
        for n in LENGTHS:
            passed, low_p, strengths = 0, 0, []
            for _ in range(N):
                c = hunt.test_claim(series_of(sim(kind, n)), P, 2100)
                if c is None:
                    continue
                if c["passed"]:
                    passed += 1
                    strengths.append(c["strength"])
                if c["p_trend"] is not None and c["p_trend"] < 0.05:
                    low_p += 1
            med = float(np.median(strengths)) if strengths else float("nan")
            print(f"{kind},{n},{passed / N:.4f},{low_p / N:.4f},{med:.2f}")
    print()
    print("a straight line with no noise: full_years,strength")
    for n in LENGTHS:
        c = hunt.test_claim(series_of(np.arange(n, dtype=float)), P, 2100)
        print(f"{n},{c['strength']}")


if __name__ == "__main__":
    main()
