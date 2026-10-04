#!/usr/bin/env python3
"""Reserves that are called: the next battery model, for review (session 79). Nothing live reads it.

Energy Research Warehouse (ERW). The battery revenue stack (warehouse/derived/battery_stack.py, the page
/cost-of-power/battery) pays a battery the capacity price of every reserve it holds and never asks it to deliver:
"reserves are never deployed". Session 74 found that this, not the size of the fleet, is what the model's early years
rest on. This analysis adds a strategy beside the two the page has:

    foresight  the page's upper bound: energy at the hourly real-time price, ancillary at day-ahead prices; never called
    dayahead   the page's day-ahead schedule; never called
    called     foresight, and when ERCOT released a reserve the battery delivers its award as energy, is paid the
               real-time price for it, and spends state of charge

When a reserve is called. No table held carries ERCOT's deployments, and no pull was made. The calls are ERCOT's own
published list of events, transcribed from one cited document:

    ERCOT, "ERCOT Ancillary Services Study", Final White Paper, September 2024, Appendix 2 "Historical Use of AS"
    https://www.ercot.com/files/docs/2024/10/07/ERCOT-Ancillary-Services-Study-Final-White-Paper.pdf
    Responsive Reserve: every event in which RRS was released, 2018-01-01 to 2024-07-31 (184 events)
    ECRS:               every event in which ECRS was released, 2023-06-10 to 2024-07-31 (53 events)
    Non-Spin:           every event in which off-line Non-Spin was deployed, 2018-01-01 to 2024-07-31 (93 events)

Each event has a start and an end. The share of an hour a product is called is the part of the hour inside its events.

What is assumed, plainly:
    1. During an event the battery's whole award of that product is called. ERCOT's list gives the most MW released in
       an event, not the share of the reserve procured, so the share is not scaled. This is the most a battery is called.
    2. The event times are Central prevailing time (the document does not say; ERCOT's operating reports are).
    3. Regulation Up and Regulation Down are not called here. ERCOT deploys regulation every four seconds, and the
       document gives no figure for how much; no share is invented. For regulation "called" is still the price-taker.
    4. Non-Spin follows the off-line deployment events. On-line Non-Spin, which a battery provides, is released to the
       real-time dispatch continuously behind a USD 75 offer floor (the same document, section 8), so it is called
       more often than these events; the document gives no start date for that rule, and it is not modelled.
    5. The calls are known in advance, as the real-time prices are in "foresight". So "called" is still an upper
       bound: the best a battery could do knowing when it would be called.

The program of one day, per MW, beside the page's (battery_stack.structure): with s the share of the hour product j is
called and a its award,
    state of charge   falls by s x a / eta in the hour, as a discharge does
    energy            s x a MWh is paid the hour's real-time price, on top of the award's capacity price
    stored energy     behind an award: a x max(required hours, s) / eta at the hour's start, and
                      a x max(required hours - s, 0) / eta at its end (what is still owed after delivering)
    one cycle a day   discharges and called energy together
    charging          in an hour the battery holds a called award, it charges at most in the part of the hour not called
                      (a switch per called hour, a mixed-integer program on those days)
With every share at zero this is the page's program, and a test holds it to that.

Days. A Central day is solved only inside the events' window (2018-01-01 to 2024-07-31) and only when every hour of
the energy price and of every ancillary product bought that day is held, as the page does; never filled. All three
strategies are solved on the same days, so each year's fall is like for like; the page's yearly figures rest on more
days from August 2024.

    python warehouse/analysis/battery_called.py            # writes warehouse/output/analysis_internal/battery_called_*.csv
"""

import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))
import battery_stack as bs  # noqa: E402
import price_board as pb  # noqa: E402

OUT_DIR = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
EVENTS = os.path.join(OUT_DIR, "ercot_as_release_events.csv")
DOC = ("ERCOT, ERCOT Ancillary Services Study, Final White Paper, September 2024, Appendix 2 (Historical Use of AS), "
       "https://www.ercot.com/files/docs/2024/10/07/ERCOT-Ancillary-Services-Study-Final-White-Paper.pdf")
WINDOW = ("2018-01-01", "2024-07-31")          # the Central days ERCOT's lists of RRS and off-line Non-Spin events cover
ECRS_FROM = "2023-06-10"                       # the ECRS list starts with the product
CALLED = ("rrs", "ecrs", "nspin")              # the products the events cover; regulation is not called (assumption 3)
EVENT_TZ = "America/Chicago"                   # assumption 2
TOL = 1e-6


def read_events(path=EVENTS):
    """ERCOT's events: product, start and end as UTC timestamps (from the Central times of the document)."""
    d = pd.read_csv(path, comment="#", dtype=str, keep_default_na=False)
    for c in ("start", "end"):
        local = pd.to_datetime(d[c + "_central"], format="%Y-%m-%d %H:%M")
        d[c] = local.dt.tz_localize(EVENT_TZ, ambiguous=True, nonexistent="shift_forward").dt.tz_convert("UTC")
    if (d["end"] < d["start"]).any():
        raise RuntimeError("an event ends before it starts")
    return d[["product", "start", "end"]]


def hour_shares(events, product):
    """{UTC hour start: the share of the hour inside the product's events}, at most 1."""
    out = {}
    for _, e in events[events["product"] == product].iterrows():
        h = e["start"].floor("h")
        while h < e["end"]:
            lo, hi = max(h, e["start"]), min(h + pd.Timedelta(hours=1), e["end"])
            out[h] = out.get(h, 0.0) + (hi - lo).total_seconds() / 3600
            h += pd.Timedelta(hours=1)
    return {h: min(1.0, v) for h, v in out.items() if v > 0}


def structure_called(T, duration, spec, eta, S):
    """The day's constraints with calls: A x <= b over x = [charge (T), discharge (T), one block of T per product].
    S: one array of T shares per product. With S all zero the rows are battery_stack.structure's."""
    K = len(spec)
    n = T * (2 + K)
    c0, d0 = 0, T
    r0 = [T * (2 + j) for j in range(K)]
    rows, b = [], []

    def soc_row(t):
        row = np.zeros(n)
        if t >= 0:
            row[c0:c0 + t + 1] = eta
            row[d0:d0 + t + 1] = -1 / eta
            for j, (is_up, _) in enumerate(spec):
                if is_up:
                    row[r0[j]:r0[j] + t + 1] = -np.asarray(S[j][:t + 1]) / eta   # energy delivered on call
        return row

    for t in range(T):
        s = soc_row(t)
        rows.append(s); b.append(duration)
        rows.append(-s); b.append(0.0)
    cyc = np.zeros(n)
    cyc[d0:d0 + T] = 1 / eta
    for j, (is_up, _) in enumerate(spec):
        if is_up:
            cyc[r0[j]:r0[j] + T] = np.asarray(S[j]) / eta
    rows.append(cyc); b.append(duration)
    for t in range(T):
        up = np.zeros(n); up[d0 + t] = 1
        dn = np.zeros(n); dn[c0 + t] = 1
        start_up, end_up, need_dn = np.zeros(n), np.zeros(n), np.zeros(n)
        for j, (is_up, hours) in enumerate(spec):
            if is_up:
                up[r0[j] + t] = 1
                start_up[r0[j] + t] = max(hours, S[j][t]) / eta
                end_up[r0[j] + t] = max(hours - S[j][t], 0.0) / eta
            else:
                dn[r0[j] + t] = 1
                need_dn[r0[j] + t] = hours * eta
        rows.append(up); b.append(1.0)
        rows.append(dn); b.append(1.0)
        for need, s in ((start_up, soc_row(t - 1)), (end_up, soc_row(t))):   # the page's row order: start, then end
            if start_up.any():
                rows.append(need - s); b.append(0.0)
            if need_dn.any():
                rows.append(need_dn + s); b.append(duration)
    return sparse.csr_matrix(np.array(rows)), np.array(b), n


def solve_day_called(energy, reserves, spec, duration, shares, rte=bs.RTE):
    """One day's optimum for 1 MW when reserves are called. shares: one list of T shares per product (None or zeros for
    a product never called; a downward product may not be called). Returns the page's dict (battery_stack.solve_day) and
    called (the energy revenue of the calls, per product) and called_mwh."""
    T, K = len(energy), len(spec)
    eta = math.sqrt(rte)
    S = [np.zeros(T) if s is None else np.clip(np.asarray(s, dtype=float), 0, 1) for s in shares]
    for (is_up, _), s in zip(spec, S):
        if not is_up and s.any():
            raise RuntimeError("a downward product cannot be called in this model")
    A, b, n = structure_called(T, duration, tuple(spec), eta, S)
    p = np.asarray(energy, dtype=float)
    obj = np.concatenate([p, -p] + [-(np.asarray(r, dtype=float) + p * s) for r, s in zip(reserves, S)])
    smax = np.max(np.array(S), axis=0) if K else np.zeros(T)
    call_hours = np.flatnonzero(smax > 0)
    neg = np.flatnonzero(p < 0)
    x = None
    need_mip = len(call_hours) > 0
    if not need_mip:
        res = linprog(obj, A_ub=A, b_ub=b, bounds=[(0, 1)] * n, method="highs")
        if res.status != 0:
            raise RuntimeError(f"the linear program did not solve: {res.message}")
        x = res.x
        need_mip = bool(np.any(np.minimum(x[neg], x[T + neg]) > TOL))
    if need_mip:
        # switches: at a negative price, charge or discharge (as the page); in a called hour, y = 1 lets the battery hold
        # the called products, and then it charges only in the part of the hour not called
        N, M = len(neg), len(call_hours)
        extra = np.zeros((2 * N + 2 * M, n + N + M))
        for i, t in enumerate(neg):
            extra[i, t], extra[i, n + i] = 1, -1                      # charge <= u
            extra[N + i, T + t], extra[N + i, n + i] = 1, 1           # discharge <= 1 - u
        rhs = np.concatenate([np.zeros(N), np.ones(N), np.zeros(M), np.ones(M)])
        for i, t in enumerate(call_hours):
            for j in range(K):
                if S[j][t] > 0:
                    extra[2 * N + i, T * (2 + j) + t] = 1             # the called products' awards <= y
            extra[2 * N + i, n + N + i] = -1
            extra[2 * N + M + i, t], extra[2 * N + M + i, n + N + i] = 1, smax[t]   # charge <= 1 - share x y
        A2 = sparse.vstack([sparse.hstack([A, sparse.csr_matrix((A.shape[0], N + M))]), sparse.csr_matrix(extra)]).tocsr()
        res = milp(np.concatenate([obj, np.zeros(N + M)]), constraints=LinearConstraint(A2, -np.inf, np.concatenate([b, rhs])),
                   integrality=np.concatenate([np.zeros(n), np.ones(N + M)]), bounds=Bounds(0, 1))
        if res.status != 0:
            raise RuntimeError(f"the mixed-integer program did not solve: {res.message}")
        x = res.x[:n].copy()
    else:
        x = x.copy()
    both = np.minimum(x[:T], x[T:2 * T] / (eta * eta))
    both[p < 0] = 0
    x[:T] -= both
    x[T:2 * T] -= both * eta * eta
    x = np.clip(x, 0, 1)
    c, d = x[:T], x[T:2 * T]
    awards = [x[T * (2 + j):T * (3 + j)] for j in range(K)]
    called_mwh = [S[j] * awards[j] if spec[j][0] else np.zeros(T) for j in range(K)]
    e_rev = float(p @ (d - c))
    r_rev = [float(np.asarray(reserves[j], dtype=float) @ awards[j]) for j in range(K)]
    k_rev = [float(p @ called_mwh[j]) for j in range(K)]
    soc = np.cumsum(eta * c - d / eta - sum(called_mwh) / eta)
    return dict(total=e_rev + sum(r_rev) + sum(k_rev), energy=e_rev, reserve=r_rev, called=k_rev, charge=c, discharge=d,
                awards=awards, soc=soc, mip=need_mip, delivered=float(d.sum() + sum(m.sum() for m in called_mwh)),
                called_mwh=float(sum(m.sum() for m in called_mwh)), shares=S)


def check_day_called(sol, spec, duration, rte=bs.RTE, tol=1e-6):
    """Every constraint of the day with calls, hour by hour; the list of violations (empty when all hold)."""
    eta = math.sqrt(rte)
    c, d, soc, aw, S = sol["charge"], sol["discharge"], sol["soc"], sol["awards"], sol["shares"]
    bad = []
    prev = 0.0
    for t in range(len(c)):
        ups = [j for j, (is_up, _) in enumerate(spec) if is_up]
        up = sum(aw[j][t] for j in ups)
        dn = sum(aw[j][t] for j, (is_up, _) in enumerate(spec) if not is_up)
        if d[t] + up > 1 + tol:
            bad.append(f"hour {t}: discharge plus upward reserves {d[t] + up:.6f} MW per MW")
        if c[t] + dn > 1 + tol:
            bad.append(f"hour {t}: charge plus downward regulation {c[t] + dn:.6f} MW per MW")
        if soc[t] < -tol or soc[t] > duration + tol:
            bad.append(f"hour {t}: state of charge {soc[t]:.6f} outside 0 to {duration}")
        start = sum(aw[j][t] * max(spec[j][1], S[j][t]) / eta for j in ups)
        end = sum(aw[j][t] * max(spec[j][1] - S[j][t], 0.0) / eta for j in ups)
        if start > prev + tol:
            bad.append(f"hour {t}: upward reserves need {start:.6f} MWh at the hour's start, {prev:.6f} stored")
        if end > soc[t] + tol:
            bad.append(f"hour {t}: upward reserves still owe {end:.6f} MWh at the hour's end, {soc[t]:.6f} stored")
        need_dn = sum(aw[j][t] * h * eta for j, (is_up, h) in enumerate(spec) if not is_up)
        if need_dn > duration - max(prev, soc[t]) + tol:
            bad.append(f"hour {t}: downward regulation needs {need_dn:.6f} MWh of room")
        called = [j for j in ups if S[j][t] > 0 and aw[j][t] > tol]
        if called and c[t] > 1 - max(S[j][t] for j in called) + tol:
            bad.append(f"hour {t}: charging {c[t]:.6f} while called for {max(S[j][t] for j in called):.4f} of the hour")
        prev = soc[t]
    if ((d + sum(S[j] * aw[j] for j, (is_up, _) in enumerate(spec) if is_up)) / eta).sum() > duration + tol:
        bad.append("more than one full cycle, discharges and called energy together")
    return bad


def main():
    m = bs.MARKETS["ercot"]
    tz = pb.TZ["ercot"]
    quiet = lambda msg: None  # noqa: E731
    energy = {mk: bs.energy_prices("ercot", mk, quiet)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices("ercot_as_prices", m["products"])
    events = read_events()
    share = {k: hour_shares(events, k) for k in CALLED}
    rows, left = [], []
    for ts in pd.date_range(WINDOW[0], WINDOW[1], freq="D"):
        day = ts.strftime("%Y-%m-%d")
        hrs = bs.day_hours(day, tz)
        prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
        pr = [reserve[p["key"]].reindex(hrs) for p in prods]
        ep = {mk: energy[mk].reindex(hrs) for mk in ("rtm", "dam")}
        if any(s.isna().any() for s in pr):
            left.append((day, "an ancillary price not held"))
            continue
        if ep["rtm"].isna().any() or ep["dam"].isna().any():
            left.append((day, "an energy price not held"))
            continue
        spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
        S = [np.array([share[p["key"]].get(h, 0.0) for h in hrs]) if p["key"] in CALLED else np.zeros(len(hrs)) for p in prods]
        for dur in bs.DURATIONS:
            sols = {"foresight": bs.solve_day(ep["rtm"].values, [s.values for s in pr], spec, dur),
                    "dayahead": bs.solve_day(ep["dam"].values, [s.values for s in pr], spec, dur)}
            for name, sol in sols.items():
                bad = bs.check_day(sol, spec, dur)
                if bad:
                    raise RuntimeError(f"{day} {name} {dur}h: {bad[0]}")
            if any(s.any() for s in S):
                sol = solve_day_called(ep["rtm"].values, [s.values for s in pr], spec, dur, S)
                bad = check_day_called(sol, spec, dur)
                if bad:
                    raise RuntimeError(f"{day} called {dur}h: {bad[0]}")
            else:  # a day with no event is the price-taker's day: the same program, not solved twice
                f = sols["foresight"]
                sol = dict(f, called=[0.0] * len(prods), called_mwh=0.0)
            sols["called"] = sol
            for name, sol in sols.items():
                r = dict(day=day, duration_h=dur, strategy=name, total=round(sol["total"], 4), energy=round(sol["energy"], 4),
                         called_energy=round(sum(sol.get("called", [0.0])), 4), called_mwh=round(sol.get("called_mwh", 0.0), 4))
                for p, v in zip(prods, sol["reserve"]):
                    r[p["key"]] = round(v, 4)
                for p, s in zip(prods, S):
                    if p["key"] in CALLED:
                        r[f"hours_called_{p['key']}"] = round(float(s.sum()), 4)
                rows.append(r)
    os.makedirs(OUT_DIR, exist_ok=True)
    d = pd.DataFrame(rows)
    keys = [p["key"] for p in m["products"]]
    note = (f"ERCOT HB_HUBAVG, USD per MW of rated power; calls from {DOC}; during an event the whole award is called "
            "(assumed), regulation is never called (no figure held), Non-Spin by the off-line deployment events, the "
            "calls known in advance. All three strategies on the same Central days, "
            f"{WINDOW[0]} to {WINDOW[1]}; days left out (a price not held): {len(left)}.")
    daily = os.path.join(OUT_DIR, "battery_called_ercot_daily.csv")
    with open(daily, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal, for review (session 79): reserves that are called, by Central day "
                f"(warehouse/analysis/battery_called.py). {note}\n")
        d.to_csv(f, index=False, lineterminator="\n")
    y = d.assign(year=d["day"].str[:4]).groupby(["year", "duration_h", "strategy"])
    agg = y[["total", "energy", "called_energy", "called_mwh"] + keys].sum().round(2)
    agg["ancillary"] = y[keys].sum().sum(axis=1).round(2)
    agg["days"] = y.size()
    hours = d[d["strategy"] == "called"].assign(year=lambda z: z["day"].str[:4]).groupby(["year", "duration_h"])[
        [f"hours_called_{k}" for k in CALLED]].sum().round(2)
    agg = agg.reset_index().merge(hours.reset_index(), on=["year", "duration_h"], how="left")
    yearly = os.path.join(OUT_DIR, "battery_called_ercot_yearly.csv")
    with open(yearly, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal, for review (session 79): reserves that are called, by year, duration, strategy and "
                f"stream (warehouse/analysis/battery_called.py). {note} total = energy + called_energy + ancillary; "
                "called_energy is the real-time price paid for energy delivered on call.\n")
        agg.to_csv(f, index=False, lineterminator="\n")
    print(f"{len(d):,} day rows, {d['day'].nunique():,} days solved, {len(left)} left out -> "
          f"{os.path.relpath(daily, ROOT)}, {os.path.relpath(yearly, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
