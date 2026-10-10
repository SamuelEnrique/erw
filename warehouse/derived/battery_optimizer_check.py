#!/usr/bin/env python3
"""A second, independent check of the battery model's optimizer (session 178).

Energy Research Warehouse (ERW). The battery model (warehouse/derived/battery_stack.py) solves one linear program a day.
This script does not import it. It reads only the hourly export (site/public/battery/erw_2026_battery_dispatch.csv: the
prices the model used, its decisions and its revenue) and, day by day, asks three questions of the model's answer:

    1. Is the model's dispatch allowed? Every limit of the day is recomputed here from the hourly columns.
    2. Could any dispatch have earned more? The day's problem is written again from scratch, in another form (the state
       of charge is a variable of its own, tied to charging and discharging by an equation), and solved by another
       algorithm named explicitly (HiGHS interior point; the model leaves the choice of method to HiGHS).
    3. Is that optimum itself right? Its dual prices give a ceiling that needs no trust in any solver: for ANY
       non-negative prices on the limits, the ceiling computed below in plain arithmetic is an upper bound on what any
       allowed dispatch can earn (weak duality). When the model's revenue reaches the ceiling, it is proven optimal.

A day on which the model used its charge-or-discharge switch (it forbids charging and discharging in one hour when the
price is negative) is not a linear program: its ceiling is the linear one, which may stand above it, and its optimum is
found here by this script's own mixed-integer form and, when the day has few enough negative-price hours, by trying
every pattern of switches.

    python warehouse/derived/battery_optimizer_check.py --out-dir C:/.../runs/session178
    python warehouse/derived/battery_optimizer_check.py --all --out-dir DIR     # every day of the file, not the sample

The sample: SAMPLE_PER_MONTH days of each of the last twelve months, drawn with random.Random(SEED), and added to them
the highest-revenue day, every day of the last twelve months with a negative energy price that used the switch, the
day with the most negative energy price, and the two daylight-saving days. Exit 0 when every day passes, 1 otherwise.
Method: docs/methods/battery_earns_algorithm.md.
"""

import argparse
import csv
import itertools
import math
import os
import random
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
SEED = 178
SAMPLE_PER_MONTH = 3
RTE = 0.86
DURATION = 4.0
SENTINEL = -999.0
# The products, written here from the operator's rules and not read from the model: (key, takes upward power,
# [(first local day, hours of stored energy behind 1 MW)]). ERCOT NPRR 1096 (Non-Spin four hours, ECRS two) and
# NPRR 1282 (from 5 December 2025: regulation and Responsive Reserve 30 minutes, ECRS one hour).
PRODUCTS = [
    ("regup", True, [("2018-01-01", 1.0), ("2025-12-05", 0.5)]),
    ("regdn", False, [("2018-01-01", 1.0), ("2025-12-05", 0.5)]),
    ("rrs", True, [("2018-01-01", 1.0), ("2025-12-05", 0.5)]),
    ("ecrs", True, [("2023-06-10", 2.0), ("2025-12-05", 1.0)]),
    ("nspin", True, [("2018-01-01", 1.0), ("2022-12-09", 4.0)]),
]
FEAS_TOL = 5e-5    # the file writes megawatts to six decimals: a limit may be passed by rounding alone
GAP_TOL = 1e-4     # USD per MW and day: the file writes revenue to eight decimals, 25 hours and eight columns


def read_days(path=CSV):
    """{local day: [row, ...]} of the export, numbers as floats, the hours in order."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    days = {}
    for r in csv.DictReader(lines):
        row = {k: (v if k in ("hour_utc", "hour_local", "local_day", "local_month") else float(v)) for k, v in r.items()}
        days.setdefault(r["local_day"], []).append(row)
    for rows in days.values():
        rows.sort(key=lambda r: r["hour_utc"])
    return days


def hours_behind(key, day):
    """The stored energy 1 MW of a product must have behind it on a local day, in hours."""
    h = None
    for _, _, periods in [p for p in PRODUCTS if p[0] == key]:
        for first, hours in periods:
            if first <= day:
                h = hours
    return h


def bought(rows):
    """The products with a price on the day: [(key, takes upward power, hours behind)]."""
    return [(k, up, hours_behind(k, rows[0]["local_day"])) for k, up, _ in PRODUCTS if rows[0][f"price_{k}_usd_mw"] != SENTINEL]


def feasible(rows, prods, duration=DURATION, tol=FEAS_TOL):
    """The limits the model's own dispatch breaks, recomputed from the hourly columns; empty when none."""
    eta = math.sqrt(RTE)
    bad, soc = [], 0.0
    out = 0.0
    for t, r in enumerate(rows):
        prev = soc
        soc = prev + eta * r["charge_mw"] - r["discharge_mw"] / eta
        out += r["discharge_mw"] / eta
        up = sum(r[f"award_{k}_mw"] for k, is_up, _ in prods if is_up)
        dn = sum(r[f"award_{k}_mw"] for k, is_up, _ in prods if not is_up)
        need_up = sum(r[f"award_{k}_mw"] * h / eta for k, is_up, h in prods if is_up)
        need_dn = sum(r[f"award_{k}_mw"] * h * eta for k, is_up, h in prods if not is_up)
        if abs(soc - r["soc_mwh"]) > tol:
            bad.append(f"hour {t}: the state of charge written, {r['soc_mwh']}, is not charging and discharging summed, {soc:.6f}")
        if min(r["charge_mw"], r["discharge_mw"]) < -tol or max(r["charge_mw"], r["discharge_mw"]) > 1 + tol:
            bad.append(f"hour {t}: charge or discharge outside 0 to 1 MW")
        if r["discharge_mw"] + up > 1 + tol:
            bad.append(f"hour {t}: discharge plus upward reserves {r['discharge_mw'] + up:.6f} MW")
        if r["charge_mw"] + dn > 1 + tol:
            bad.append(f"hour {t}: charge plus downward regulation {r['charge_mw'] + dn:.6f} MW")
        if soc < -tol or soc > duration + tol:
            bad.append(f"hour {t}: state of charge {soc:.6f} MWh")
        if need_up > min(prev, soc) + tol:
            bad.append(f"hour {t}: upward reserves need {need_up:.6f} MWh, {min(prev, soc):.6f} stored")
        if need_dn > duration - max(prev, soc) + tol:
            bad.append(f"hour {t}: downward regulation needs {need_dn:.6f} MWh of room")
        if r["price_energy_usd_mwh"] < 0 and min(r["charge_mw"], r["discharge_mw"]) > tol:
            bad.append(f"hour {t}: charging and discharging together at a negative price")
    if out > duration + tol:
        bad.append(f"more than one full cycle: {out:.6f} MWh taken out")
    return bad


def program(rows, prods, duration=DURATION):
    """The day written from scratch: minimize cost'x with A_ub x <= b_ub, A_eq x = b_eq, lo <= x <= hi, over
    x = [charge (T), discharge (T), state of charge at each hour's end (T), one block of T per product]."""
    T, K = len(rows), len(prods)
    eta = math.sqrt(RTE)
    n = T * (3 + K)
    C, D, S = 0, T, 2 * T
    R = [T * (3 + j) for j in range(K)]
    cost = np.zeros(n)
    for t, r in enumerate(rows):
        cost[C + t] = r["price_energy_usd_mwh"]
        cost[D + t] = -r["price_energy_usd_mwh"]
        for j, (k, _, _) in enumerate(prods):
            cost[R[j] + t] = -r[f"price_{k}_usd_mw"]
    a_eq, b_eq = np.zeros((T, n)), np.zeros(T)
    for t in range(T):                       # stored energy: s_t = s_(t-1) + eta c_t - d_t / eta, from empty
        a_eq[t, S + t] = 1
        if t:
            a_eq[t, S + t - 1] = -1
        a_eq[t, C + t] = -eta
        a_eq[t, D + t] = 1 / eta
    a_ub, b_ub = [], []
    for t in range(T):
        up, dn, eu, ed = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        up[D + t] = 1
        dn[C + t] = 1
        for j, (_, is_up, h) in enumerate(prods):
            if is_up:
                up[R[j] + t] = 1
                eu[R[j] + t] = h / eta
            else:
                dn[R[j] + t] = 1
                ed[R[j] + t] = h * eta
        a_ub += [up, dn]
        b_ub += [1.0, 1.0]
        for s in ([S + t - 1] if t else []) + [S + t]:   # the energy behind the reserves, at the hour's two ends
            x = eu.copy(); x[s] -= 1
            a_ub.append(x); b_ub.append(0.0)
            x = ed.copy(); x[s] += 1
            a_ub.append(x); b_ub.append(duration)
        if not t:                                         # the first hour starts empty: nothing is behind an upward reserve
            a_ub.append(eu); b_ub.append(0.0)
            a_ub.append(ed); b_ub.append(duration)
    cyc = np.zeros(n)
    cyc[D:D + T] = 1 / eta
    a_ub.append(cyc); b_ub.append(duration)               # at most one full cycle a day
    hi = np.ones(n)
    hi[S:S + T] = duration
    return cost, np.array(a_ub), np.array(b_ub), a_eq, b_eq, np.zeros(n), hi


def ceiling(cost, a_ub, b_ub, a_eq, b_eq, lo, hi, y, z):
    """Weak duality in plain arithmetic: for any y >= 0 on the limits and any z on the equations, no allowed x costs
    less than -y.b_ub - z.b_eq + sum_i min over [lo_i, hi_i] of (cost + A_ub'y + A_eq'z)_i x_i. Returned as revenue:
    the most any allowed dispatch can earn."""
    y = np.maximum(y, 0.0)
    reduced = cost + a_ub.T @ y + a_eq.T @ z
    least = np.where(reduced >= 0, reduced * lo, reduced * hi).sum()
    return float(y @ b_ub + z @ b_eq - least)


def optimum(rows, prods, duration=DURATION):
    """(the independent optimum, the ceiling from its dual prices, its charge and discharge) of the linear day."""
    cost, a_ub, b_ub, a_eq, b_eq, lo, hi = program(rows, prods, duration)
    res = linprog(cost, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=list(zip(lo, hi)), method="highs-ipm")
    if res.status != 0:
        raise RuntimeError(f"{rows[0]['local_day']}: the independent program did not solve: {res.message}")
    cap = ceiling(cost, a_ub, b_ub, a_eq, b_eq, lo, hi, -np.asarray(res.ineqlin.marginals), -np.asarray(res.eqlin.marginals))
    T = len(rows)
    return -float(res.fun), cap, res.x[:T], res.x[T:2 * T]


def optimum_switched(rows, prods, duration=DURATION, enumerate_up_to=12):
    """The day with no charging and discharging together in a negative-price hour: this script's own mixed-integer
    form, and, with few enough such hours, every pattern of switches tried one by one. (mixed-integer optimum,
    enumerated optimum or None, number of negative-price hours)."""
    cost, a_ub, b_ub, a_eq, b_eq, lo, hi = program(rows, prods, duration)
    T, n = len(rows), len(cost)
    neg = [t for t, r in enumerate(rows) if r["price_energy_usd_mwh"] < 0]
    N = len(neg)
    sw = np.zeros((2 * N, n + N))
    for i, t in enumerate(neg):
        sw[i, t], sw[i, n + i] = 1, -1                  # charge <= u
        sw[N + i, T + t], sw[N + i, n + i] = 1, 1       # discharge <= 1 - u
    pad = np.zeros((a_ub.shape[0], N))
    cons = [LinearConstraint(np.hstack([a_ub, pad]), -np.inf, b_ub),
            LinearConstraint(np.hstack([a_eq, np.zeros((a_eq.shape[0], N))]), b_eq, b_eq),
            LinearConstraint(sw, -np.inf, np.concatenate([np.zeros(N), np.ones(N)]))]
    res = milp(np.concatenate([cost, np.zeros(N)]), constraints=cons,
               integrality=np.concatenate([np.zeros(n), np.ones(N)]),
               bounds=Bounds(np.concatenate([lo, np.zeros(N)]), np.concatenate([hi, np.ones(N)])))
    if res.status != 0:
        raise RuntimeError(f"{rows[0]['local_day']}: the independent mixed-integer program did not solve: {res.message}")
    best = None
    if N <= enumerate_up_to:
        best = -math.inf
        for pattern in itertools.product((0, 1), repeat=N):
            h = hi.copy()
            for u, t in zip(pattern, neg):
                h[t if not u else T + t] = 0.0           # u = 0: no charging in the hour; u = 1: no discharging
            r = linprog(cost, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=list(zip(lo, h)), method="highs")
            if r.status == 0:
                best = max(best, -float(r.fun))
    return -float(res.fun), best, N


def sample(days, seed=SEED, per_month=SAMPLE_PER_MONTH):
    """The stated sample: {day: why it is in it}."""
    twelve = sorted(d for d, rows in days.items() if rows[0]["in_last_twelve"] == 1)
    rng = random.Random(seed)
    picked = {}
    for month in sorted({d[:7] for d in twelve}):
        for d in sorted(rng.sample([x for x in twelve if x[:7] == month], per_month)):
            picked[d] = "random"
    total = {d: sum(r["revenue_total_usd"] for r in days[d]) for d in twelve}
    low = {d: min(r["price_energy_usd_mwh"] for r in days[d]) for d in twelve}
    forced = {max(total, key=total.get): "the highest-revenue day", min(low, key=low.get): "the most negative energy price"}
    for d in twelve:
        if len(days[d]) != 24:
            forced[d] = f"daylight saving, {len(days[d])} hours"
        if days[d][0]["switch_used"] == 1:
            forced[d] = "the switch was used"
    for d, why in forced.items():
        picked[d] = why if d not in picked else f"{why}; also drawn at random"
    return dict(sorted(picked.items()))


def check(days, which):
    """One result per day of `which` ({day: why})."""
    out = []
    for day, why in which.items():
        rows = days[day]
        prods = bought(rows)
        model = sum(r["revenue_total_usd"] for r in rows)
        opt, cap, c, d = optimum(rows, prods)
        row = dict(day=day, why=why, hours=len(rows), negative_hours=sum(r["price_energy_usd_mwh"] < 0 for r in rows),
                   switch_used=int(rows[0]["switch_used"]), model_usd=model, lp_optimum_usd=opt, ceiling_usd=cap,
                   exact_usd=opt, enumerated_usd="", broken="; ".join(feasible(rows, prods)))
        if row["switch_used"]:
            mip, brute, _ = optimum_switched(rows, prods)
            row["exact_usd"] = mip
            row["enumerated_usd"] = "" if brute is None else brute
        row["gap_usd"] = model - row["exact_usd"]                 # above zero: the model beats the optimum, a bug
        row["gap_rel"] = row["gap_usd"] / abs(row["exact_usd"]) if abs(row["exact_usd"]) > 1e-9 else 0.0
        row["above_ceiling_usd"] = model - cap                    # above zero: the model beats what any dispatch can earn
        out.append(row)
    return out


def summary(results):
    worst = max(results, key=lambda r: abs(r["gap_usd"]))
    worst_rel = max(results, key=lambda r: abs(r["gap_rel"]))
    return dict(
        days=len(results), broken=[r["day"] for r in results if r["broken"]],
        largest_abs_gap_usd=abs(worst["gap_usd"]), largest_abs_gap_day=worst["day"],
        largest_rel_gap=abs(worst_rel["gap_rel"]), largest_rel_gap_day=worst_rel["day"],
        above=[r["day"] for r in results if r["gap_usd"] > GAP_TOL], below=[r["day"] for r in results if r["gap_usd"] < -GAP_TOL],
        above_ceiling=[r["day"] for r in results if r["above_ceiling_usd"] > GAP_TOL],
        ceiling_reached=sum(1 for r in results if abs(r["above_ceiling_usd"]) <= GAP_TOL),
        ceiling_slack_usd=max((r["ceiling_usd"] - r["lp_optimum_usd"] for r in results), default=0.0),
        enumerated_differs=[r["day"] for r in results if r["enumerated_usd"] != "" and abs(r["enumerated_usd"] - r["exact_usd"]) > GAP_TOL],
        revenue_usd=sum(r["model_usd"] for r in results))


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: an independent check of the battery model's optimizer, from the hourly export alone")
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--all", action="store_true", help="every day of the file, not the sample")
    ap.add_argument("--out-dir", help="write optimizer_check_<sample|all>.csv here")
    a = ap.parse_args(argv)
    if not os.path.exists(a.csv):
        print(f"battery_optimizer_check SKIPPED: {a.csv} is not on this machine")
        return 0
    days = read_days(a.csv)
    which = {d: "every day" for d in sorted(days)} if a.all else sample(days)
    results = check(days, which)
    s = summary(results)
    label = "all" if a.all else "sample"
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        path = os.path.join(a.out_dir, f"optimizer_check_{label}.csv")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# ERW session 178: the battery model's daily revenue beside an independent optimum; {label}; seed {SEED}; "
                    f"USD per MW of rated power; from {os.path.basename(a.csv)}\n")
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(results)
    print(f"{label}: {s['days']} days, model revenue {s['revenue_usd']:.2f} USD per MW")
    print(f"largest absolute gap {s['largest_abs_gap_usd']:.8f} USD per MW ({s['largest_abs_gap_day']}); "
          f"largest relative gap {s['largest_rel_gap']:.3e} ({s['largest_rel_gap_day']})")
    print(f"model above the optimum on {len(s['above'])} days, below it on {len(s['below'])} days (tolerance {GAP_TOL} USD per MW)")
    print(f"ceiling by weak duality reached on {s['ceiling_reached']} of {s['days']} days; model above the ceiling on "
          f"{len(s['above_ceiling'])}; the ceiling stands at most {s['ceiling_slack_usd']:.8f} USD above the independent optimum")
    print(f"days whose dispatch breaks a limit: {len(s['broken'])}; enumerated optimum differs on {len(s['enumerated_differs'])} days")
    for r in results:
        if r["switch_used"]:
            print(f"switch day {r['day']}: model {r['model_usd']:.6f}, mixed-integer {r['exact_usd']:.6f}, enumerated "
                  f"{r['enumerated_usd']}, linear ceiling {r['ceiling_usd']:.6f}, {r['negative_hours']} negative-price hours")
    ok = not (s["broken"] or s["above"] or s["below"] or s["above_ceiling"] or s["enumerated_differs"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
