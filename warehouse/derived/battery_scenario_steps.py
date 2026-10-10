#!/usr/bin/env python3
"""The battery model run again at a few stated steps of round-trip efficiency and of the daily cycle limit (session 179).

Energy Research Warehouse (ERW). "What a battery earns" (/cost-of-power/battery) lets a reader set ten assumptions and
compare two scenarios. Eight of them are arithmetic on the model's monthly revenue and are computed in the browser. Two
are not: the round-trip efficiency and the cycles a day are inside every day's optimization (the state of charge, the
energy behind each reserve, the cycle limit), so revenue is not a formula of them. This script runs the model itself
(warehouse/derived/battery_stack.py, solve_day) for each step the page offers and writes the monthly totals:

    site/data/battery_scenario_steps.json

Steps. Round trip 0.86, 0.89, 0.92: the low end, the midpoint and the high end of Lazard's 86 to 92 percent for
utility-scale standalone storage (LCOS v10.0; docs/methods/cost_of_power.md). Cycle limit 0.5, 1, 1.5 and 2 full cycles
a day: 1 is the model's rule, the others are the reader's steps, not a source's. The page offers exactly these and
interpolates nothing.

Cases. ERCOT and CAISO, both strategies, 2, 4 and 8 hours: the cases the page opens to a visitor. For each, the window
is the 36 local months of the page's "bad month" (which end with the last of the page's last twelve months), found from
battery_stack_monthly by the page's own rule (battery_dispatch_export.py, last_36).

The model is not changed. The efficiency is solve_day's own argument. The cycle limit is one right-hand side of the
model's constraint matrix (battery_stack.structure: the row "at most one full cycle a day", bound = the duration); this
script multiplies that one bound by the step, after asserting that the row is the cycle row. Every solution is checked
against every limit by the model's check_day, with the cycle limit checked here at its step.

It refuses to write unless the default cell (0.86, 1) reproduces battery_stack_monthly: each month's total to within
half a cent per MW and the same count of solved days. So the file's other cells differ from the page's own numbers in
the two assumptions only.

    python warehouse/derived/battery_scenario_steps.py --in-dir C:/.../warehouse/output
    python warehouse/derived/battery_scenario_steps.py --in-dir DIR --out C:/scratch/trial.json --only ercot:foresight:4

It writes nothing under warehouse/output and needs no data lock: the tables are read, the JSON is a site file. The page
uses a cell only while the file's months and default cell still equal the live table's (lib/battery/finance.ts,
stepMonths); otherwise it offers the default step alone and says so. Method: docs/methods/battery_earns_algorithm.md,
section 11.1.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import battery_dispatch_export as ex  # noqa: E402
import battery_stack as bs  # noqa: E402
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "battery_scenario_steps.json")
RTE_STEPS = [0.86, 0.89, 0.92]          # Lazard LCOS v10.0: 86 to 92 percent, and the midpoint
CYCLE_STEPS = [0.5, 1.0, 1.5, 2.0]      # full cycles a day; 1 is the model's rule
GRIDS = ["ercot", "caiso"]               # the grids the page opens to a visitor
TOL = 0.005                              # USD per MW and month: the default cell against battery_stack_monthly
CYCLE_MESSAGE = "more than one full cycle"

_cycles = 1.0
_model_structure = bs.structure


def structure_at_step(T, duration, spec, eta):
    """The model's constraint matrix with the cycle row's bound multiplied by the step in force. At a step of 1 it is
    the model's own object, untouched."""
    A, b, n = _model_structure(T, duration, spec, eta)
    if _cycles == 1.0:
        return A, b, n
    row = A.getrow(2 * T).toarray().ravel()
    want = np.zeros(n)
    want[T:2 * T] = 1 / eta
    if not (np.allclose(row, want) and b[2 * T] == duration):
        raise RuntimeError("battery_stack.structure: row 2T is not the cycle row any more; this script must be read again")
    b2 = b.copy()
    b2[2 * T] = _cycles * duration
    return A, b2, n


def solve(energy, reserves, spec, duration, rte, cycles):
    """One day by the model's solve_day at an efficiency and a cycle limit, checked against every limit."""
    global _cycles
    _cycles = float(cycles)
    bs.structure = structure_at_step
    try:
        sol = bs.solve_day(energy, reserves, spec, duration, rte=rte)
    finally:
        bs.structure = _model_structure
        _cycles = 1.0
    bad = [m for m in bs.check_day(sol, spec, duration, rte=rte) if not m.startswith(CYCLE_MESSAGE)]
    taken = float((sol["discharge"] / np.sqrt(rte)).sum())
    if taken > cycles * duration + 1e-6:
        bad.append(f"more than {cycles} full cycles: {taken:.6f} MWh taken out")
    if bad:
        raise RuntimeError(f"a constraint does not hold at round trip {rte}, cycles {cycles}: {bad[0]}")
    return sol


def cell_key(rte, cycles):
    return f"{round(rte * 100)}|{cycles:g}"


def build_case(grid, strat, energy, reserve, monthly, log):
    """{duration: case} for one grid and strategy: every cell's monthly totals over the page's 36-month window."""
    m = bs.MARKETS[grid]
    tz = pb.TZ[grid]
    entity = f"{grid}:{pb.MAIN[grid]}"
    out = {}
    for dur in bs.DURATIONS:
        months = ex.months_of(monthly, entity, strat, dur)
        win = ex.last_36(months)
        if win is None:
            log(f"  {grid} {strat} {dur}h: no held month, no case written")
            continue
        first, last, held = win
        l12 = ex.last_twelve(months)
        a = pd.Timestamp(first + "-01")
        b = pd.Timestamp(last + "-01") + pd.offsets.MonthBegin(1) - pd.Timedelta(days=1)
        cells = {cell_key(r, c): {} for r in RTE_STEPS for c in CYCLE_STEPS}
        days = {}
        t0 = time.time()
        for ts in pd.date_range(a, b, freq="D"):
            day = ts.strftime("%Y-%m-%d")
            if day[:7] not in held:
                continue
            hrs = bs.day_hours(day, tz)
            prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
            pr = [reserve[p["key"]].reindex(hrs) for p in prods]
            ep = energy.reindex(hrs)
            if any(s.isna().any() for s in pr) or ep.isna().any():
                continue                      # the model leaves the day out; so does every cell
            spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
            days[day[:7]] = days.get(day[:7], 0) + 1
            for r in RTE_STEPS:
                for c in CYCLE_STEPS:
                    sol = solve(ep.values, [s.values for s in pr], spec, dur, r, c)
                    k = cell_key(r, c)
                    cells[k][day[:7]] = cells[k].get(day[:7], 0.0) + sol["total"]
        # the default cell must be the page's own table, month by month
        base = cells[cell_key(bs.RTE, 1.0)]
        bad = []
        for mo in held:
            want = months[mo].get("revenue_total_usd_per_mw")
            if mo not in base or want is None or abs(base[mo] - want) > TOL:
                bad.append(f"{mo}: this run {base.get(mo)}, the table {want}")
            if days.get(mo) != months[mo].get("days_held"):
                bad.append(f"{mo} days: {days.get(mo)} here, {months[mo].get('days_held')} in the table")
        if bad:
            raise RuntimeError(f"{grid} {strat} {dur}h: the default cell is not {bs.NAME}: " + "; ".join(bad[:6]))
        out[dur] = dict(first=first, last=last, last_twelve=[l12[0], l12[-1]] if l12 else None, months=held,
                        days=[days[mo] for mo in held],
                        table=[round(months[mo]["revenue_total_usd_per_mw"], 4) for mo in held],
                        cells={k: [round(v[mo], 4) for mo in held] for k, v in cells.items()})
        log(f"  {grid} {strat} {dur}h: {len(held)} months {first}..{last}, {sum(days.values())} days, "
            f"{len(cells)} cells, {time.time() - t0:.0f} s")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the battery model at the page's steps of efficiency and of the cycle limit")
    ap.add_argument("--in-dir", default=ip.OUT_DIR, help="read the tables from this directory; nothing is written there")
    ap.add_argument("--out", default=OUT, help="the JSON to write")
    ap.add_argument("--only", default="", help="grid:strategy:duration, for a trial (for example ercot:foresight:4)")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir)
    only = a.only.split(":") if a.only else None
    grids = [g for g in GRIDS if not only or g == only[0]]
    need = [bs.NAME] + [bs.MARKETS[g]["as_table"] for g in grids] + [pb.TABLES[(g, "rtm")][0] for g in grids]
    missing = sorted({t for t in need if not os.path.exists(os.path.join(in_dir, t + ".csv"))})
    if missing:
        print(f"battery_scenario_steps SKIPPED: input tables not on this machine: {', '.join(missing)}")
        return 0
    ip.OUT_DIR = in_dir                    # the readers of price_board and cost_of_power read ip.OUT_DIR
    run_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    monthly = ex.read_monthly(in_dir)
    cases, tables = {}, {}
    for grid in grids:
        m = bs.MARKETS[grid]
        reserve = bs.as_prices(m["as_table"], m["products"])
        tables[m["as_table"]] = True
        for strat, mk in bs.STRATEGIES.items():
            if only and strat != only[1]:
                continue
            energy, src = bs.energy_prices(grid, mk, print)
            if "not on this machine" in src:
                print(f"battery_scenario_steps FAILED: {src}; the window cannot be solved here; nothing written", file=sys.stderr)
                return 1
            tables[pb.TABLES[(grid, mk)][0]] = True
            got = build_case(grid, strat, energy, reserve, monthly, print)
            for dur, case in got.items():
                if only and str(dur) != only[2]:
                    continue
                cases[f"{grid}|{strat}|{dur}"] = case
    sha, commit = ex.model_version()

    def got_at(t):
        return ex.header_value(os.path.join(in_dir, t + ".csv"), "Retrieved: ").split(" (UTC)")[0] or "not stated"
    doc = dict(
        what="ERW: the battery model's monthly total revenue (USD per MW of rated power) at each step of round-trip efficiency "
             "and of the daily cycle limit the page /cost-of-power/battery offers. cells: '<round trip percent>|<cycles a day>'; "
             "one value per month of months. table: the same months in battery_stack_monthly when this file was built.",
        built=run_at,
        built_by="warehouse/derived/battery_scenario_steps.py",
        method="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_earns_algorithm.md",
        model=dict(file="warehouse/derived/battery_stack.py", sha256=sha, commit=commit),
        retrieved={t: got_at(t) for t in [bs.NAME] + sorted(tables)},
        rte_steps=[round(r * 100) for r in RTE_STEPS], cycle_steps=CYCLE_STEPS,
        default=dict(rte=round(bs.RTE * 100), cycles=1),
        tolerance_usd_per_mw=TOL,
        cases=cases,
    )
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"))
        f.write("\n")
    os.replace(out + ".tmp", out)
    print(f"{os.path.basename(out)}: cases={len(cases)} cells={len(RTE_STEPS) * len(CYCLE_STEPS)} bytes={os.path.getsize(out)} built={run_at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
