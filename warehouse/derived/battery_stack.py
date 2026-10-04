#!/usr/bin/env python3
"""The battery revenue stack (session 67): what a grid battery earns from energy and ancillary services together.

Energy Research Warehouse (ERW). Writes two derived series tables:

    warehouse/output/battery_stack_monthly.csv        per market, hub, duration, strategy and local month
    warehouse/output/battery_stack_stress_daily.csv   the same per local day, for the days of the ERCOT stress events
                                                      (Winter Storm Uri, Winter Storm Elliott, the 2023 heat)

Scope: ERCOT (HB_HUBAVG, 2018 on) and CAISO (TH_SP15_GEN-APND, 2024-09 on; ancillary prices of the expanded system
region). Durations 2, 4 and 8 hours. Every result is per MW of rated power.

Session 86, the grids in review: NYISO (the N.Y.C. zone; regulation and 10-minute spinning reserve) and SPP
(SPPNORTH_HUB; regulation up and down, spinning and supplemental reserve), the two other grids whose energy and
reserve prices are both public (nyiso_as_prices, spp_as_prices, session 85). They are written to a table of their
own, battery_stack_review_monthly, and to site/data/battery_stack_review.json for the page's internal view, so the
live table and every live number stay as they were; a person moves a grid into MARKETS to release it. ISO-NE's and
MISO's reserve prices are internal (their terms forbid republishing), so those grids are not modeled: HELD.

Co-optimization, not addition. A battery cannot sell its full power as energy and be paid to hold the same power in
reserve in the same hour. For each local day one linear program (scipy's HiGHS) splits the battery hour by hour
between charging, discharging and each ancillary product, subject to:
    power      discharge plus upward reserves within rated power; charge plus downward regulation within rated power
    energy     state of charge between empty and full (duration x power), each day from empty, round trip 86 percent,
               at most one full cycle a day (the seller tab's battery, warehouse/derived/merchant_revenue.py)
    reserves   stored energy to deliver every awarded upward reserve for its product's required duration, at the
               start and at the end of the hour; room to absorb awarded downward regulation for its duration
Reserves are never deployed: an award pays its capacity price and moves no energy. A day whose relaxation charges and
discharges in the same hour (it pays only at negative prices) is solved again with one charge-or-discharge switch per
hour, as a mixed-integer program.

Two strategies:
    foresight  perfect foresight, the upper bound: energy at the hourly real-time price, ancillary at day-ahead prices
    dayahead   the day-ahead schedule: energy and ancillary at day-ahead prices, no real-time trading; it assumes the
               battery's offers clear at the day-ahead price

Never filled. A local day is solved only when every hour of its energy price and of every ancillary product bought on
that day is held; any other day is left out and counted (days_left_out), never estimated.

    python warehouse/derived/battery_stack.py
    python warehouse/derived/battery_stack.py --out-dir C:/scratch   # a trial run: nothing in warehouse/output
    python warehouse/derived/battery_stack.py --review-only           # the grids in review only: the live tables untouched

Method: docs/methods/battery_stack.md.
"""

import argparse
import datetime as dt
import json
import math
import os
import sys
import traceback

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import cost_of_power as cp  # noqa: E402
import event_window as ew  # noqa: E402  (the stress events' windows)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

NAME = "battery_stack_monthly"
STRESS_NAME = "battery_stack_stress_daily"
SOURCE = "erw:battery_stack"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md"
RTE = 0.86                  # round trip, as the seller tab's battery (Lazard LCOS v10.0, low end); tested equal
DURATIONS = [2, 4, 8]
STRATEGIES = {"foresight": "rtm", "dayahead": "dam"}  # the energy price each strategy is paid
STRESS = ["uri_2021", "elliott_2022", "ercot_heat_2023"]
ONE_HOUR = ("not verified in session 67: one hour is assumed, by the session's rule for a requirement that could "
            "not be checked against the market operator's own document")
NPRR1096 = ("ERCOT NPRR 1096, Require Sustained Two-Hour Capability for ECRS and Four-Hour Capability for Non-Spin, "
            "approved 2022-05-12, effective 2022-12-09, https://www.ercot.com/mktrules/issues/NPRR1096")
NPRR1282 = ("ERCOT NPRR 1282, Ancillary Service Duration under Real-Time Co-Optimization, approved 2025-07-31, "
            "effective 2025-12-05, https://www.ercot.com/mktrules/issues/NPRR1282")
# Session 76 (Samuel's ruling on session 74's reading of the tariff): California's requirements, cited. The model's
# awards are day-ahead, so Regulation keeps its hour, now the tariff's own; Spinning and Non-Spinning Reserve take 30 minutes.
CAISO_TARIFF = "CAISO tariff Section 8 as of 2026-05-01"
CAISO_REG = (CAISO_TARIFF + ", section 8.4.1.1(g): Regulation dispatchable on a continuous basis for at least sixty (60) "
             "minutes in the Day-Ahead Market, https://www.caiso.com/documents/section-8-ancillary-services-as-of-may-1-2026.pdf")
CAISO_RESERVE = (CAISO_TARIFF + ", section 8.4.3: Spinning and Non-Spinning Reserve maintained for at least thirty (30) "
                 "minutes, https://www.caiso.com/documents/section-8-ancillary-services-as-of-may-1-2026.pdf")

# Each product: its key in the table, its direction, its price series (entity, variable), the first local day it was
# bought (None: from the table's start) and its required duration by period: (first local day, hours, source), the
# last period whose first day is on or before the day applies.
MARKETS = {
    "ercot": dict(
        label="ERCOT", start="2018-01-01", as_table="ercot_as_prices", geo="US-TX",
        products=[
            dict(key="regup", label="Regulation Up", up=True, entity="ercot:REGUP", variable="mcpc_dam", first=None,
                 hours=[("2018-01-01", 1.0, ONE_HOUR), ("2025-12-05", 0.5, NPRR1282)]),
            dict(key="regdn", label="Regulation Down", up=False, entity="ercot:REGDN", variable="mcpc_dam", first=None,
                 hours=[("2018-01-01", 1.0, ONE_HOUR), ("2025-12-05", 0.5, NPRR1282)]),
            dict(key="rrs", label="Responsive Reserve", up=True, entity="ercot:RRS", variable="mcpc_dam", first=None,
                 hours=[("2018-01-01", 1.0, ONE_HOUR), ("2025-12-05", 0.5, NPRR1282)]),
            dict(key="ecrs", label="ERCOT Contingency Reserve Service", up=True, entity="ercot:ECRS",
                 variable="mcpc_dam", first="2023-06-10",
                 hours=[("2023-06-10", 2.0, NPRR1096), ("2025-12-05", 1.0, NPRR1282)]),
            dict(key="nspin", label="Non-Spin", up=True, entity="ercot:NSPIN", variable="mcpc_dam", first=None,
                 hours=[("2018-01-01", 1.0, ONE_HOUR), ("2022-12-09", 4.0, NPRR1096)]),
        ]),
    "caiso": dict(
        label="CAISO", start="2024-09-01", as_table="caiso_as_prices", geo="US-CA",
        products=[
            dict(key="regup", label="Regulation Up", up=True, entity="caiso:AS_CAISO_EXP", variable="as_price_dam_ru",
                 first=None, hours=[("2024-09-01", 1.0, CAISO_REG)]),
            dict(key="regdn", label="Regulation Down", up=False, entity="caiso:AS_CAISO_EXP", variable="as_price_dam_rd",
                 first=None, hours=[("2024-09-01", 1.0, CAISO_REG)]),
            dict(key="spin", label="Spinning Reserve", up=True, entity="caiso:AS_CAISO_EXP", variable="as_price_dam_sr",
                 first=None, hours=[("2024-09-01", 0.5, CAISO_RESERVE)]),
            dict(key="nonspin", label="Non-Spinning Reserve", up=True, entity="caiso:AS_CAISO_EXP",
                 variable="as_price_dam_nr", first=None, hours=[("2024-09-01", 0.5, CAISO_RESERVE)]),
        ]),
}
PRODUCT_KEYS = sorted({p["key"] for m in MARKETS.values() for p in m["products"]})

# Session 86: the grids in review. Same shape as MARKETS. A product's `up` may also be "both": one award that must be
# able to move up and down (NYISO buys regulation as one capacity product), so it takes the battery's power in both
# directions and needs stored energy and room behind it.
REVIEW_NAME = "battery_stack_review_monthly"
REVIEW_SNAPSHOT = os.path.join(ROOT, "site", "data", "battery_stack_review.json")
# Session 102, from session 100's reading of the operators' own documents (docs/methods/reserve_quantities_nyiso_spp.md):
# SPP's 60 minutes and NYISO's one hour for operating reserves are the operators' rules; NYISO's tariff states no time for
# regulation, so its one hour stays an assumption, labeled as one. The hours are as session 86 assumed: no figure moves.
NYISO_RESERVE = ("NYISO Market Administration and Control Area Services Tariff, section 4.4.2.1 (Real-Time Dispatch, Overview), "
                 "effective 9/16/2026: operating reserves scheduled from an Energy Storage Resource must be sustainable for one hour, "
                 "https://nyisoviewer.etariff.biz/ViewerDocLibrary/MasterTariffs/9FullTariffNYISOMST.pdf")
NYISO_ASSUMED = ("assumed: one hour; NYISO's Market Administration and Control Area Services Tariff, Rate Schedule 3, section "
                 "15.3.2.1(e), states no time (NYISO may reduce a storage resource's regulation capacity to account for its "
                 "energy level)")
SPP_RULE = ("SPP Integrated Marketplace Protocols, Revision 119 (latest revision 7/17/2026), section 4.2.2 (Offer Submittal): "
            "a continuous duration of 60 minutes for regulation, spinning reserve and supplemental reserve, "
            "https://www.spp.org/spp-documents-filings/?id=18162")
REVIEW_MARKETS = {
    "nyiso": dict(
        label="NYISO", start="2024-09-01", as_table="nyiso_as_prices", geo="US-NY",
        products=[
            dict(key="reg", label="Regulation Capacity", up="both", entity="nyiso:NYCA", variable="as_price_dam_reg",
                 first=None, hours=[("2024-09-01", 1.0, NYISO_ASSUMED)]),
            dict(key="spin", label="10-Minute Spinning Reserve", up=True, entity="nyiso:N.Y.C.",
                 variable="as_price_dam_spin10", first=None, hours=[("2024-09-01", 1.0, NYISO_RESERVE)]),
        ],
        # not modeled, and why nothing is lost: checked in every hour held by not_above()
        dominated=[("nyiso:N.Y.C.", "as_price_dam_nsync10", "10-Minute Non-Synchronous Reserve"),
                   ("nyiso:N.Y.C.", "as_price_dam_op30", "30-Minute Operating Reserve")],
        dominant=("nyiso:N.Y.C.", "as_price_dam_spin10")),
    "spp": dict(
        label="SPP", start="2024-09-01", as_table="spp_as_prices", geo=None,
        products=[
            dict(key="regup", label="Regulation Up", up=True, entity="spp:SPP", variable="as_price_dam_regup",
                 first=None, hours=[("2024-09-01", 1.0, SPP_RULE)]),
            dict(key="regdn", label="Regulation Down", up=False, entity="spp:SPP", variable="as_price_dam_regdn",
                 first=None, hours=[("2024-09-01", 1.0, SPP_RULE)]),
            dict(key="spin", label="Spinning Reserve", up=True, entity="spp:SPP", variable="as_price_dam_spin",
                 first=None, hours=[("2024-09-01", 1.0, SPP_RULE)]),
            dict(key="supp", label="Supplemental Reserve", up=True, entity="spp:SPP", variable="as_price_dam_supp",
                 first=None, hours=[("2024-09-01", 1.0, SPP_RULE)]),
        ]),
}
# Not modeled in SPP: the ramp capability products (RampUP, RampDN) and the uncertainty product (UncUP). What a battery
# must hold behind them was not read, and adding a paid product on an assumption would only raise the result.
# Held, not shown: a grid whose reserve prices are internal. Its result would be a derived table of an internal input
# (Decision 23: the most restrictive license of the inputs), so it is not built and the page says why.
HELD = {"isone": "held, not shown: license needed", "miso": "held, not shown: license needed"}
ALL_MARKETS = {**MARKETS, **REVIEW_MARKETS}


def sides(up):
    """(takes upward power, takes downward power) of a product's direction: True, False or "both"."""
    return (True, True) if up == "both" else (bool(up), not bool(up))
r4 = pb.r4
TOL = 1e-6


def required_hours(product, day):
    """The product's required duration on a local day (YYYY-MM-DD), and its source."""
    h = None
    for first, hours, src in product["hours"]:
        if first <= day:
            h = (hours, src)
    if h is None:
        raise RuntimeError(f"{product['key']}: no duration requirement on {day}")
    return h


_STRUCT = {}


def structure(T, duration, spec, eta):
    """The constraint matrix of one day, for T hours, a duration and the products' (up, hours) tuple: A x <= b over
    x = [charge (T), discharge (T), one block of T per product]. Cached: only the prices change from day to day."""
    k = (T, duration, spec, eta)
    if k in _STRUCT:
        return _STRUCT[k]
    K = len(spec)
    n = T * (2 + K)
    c0, d0 = 0, T
    r0 = [T * (2 + j) for j in range(K)]
    rows, b = [], []

    def soc_row(t):
        """State of charge after hour t (t = -1: the empty start) as a row of coefficients."""
        row = np.zeros(n)
        if t >= 0:
            row[c0:c0 + t + 1] = eta
            row[d0:d0 + t + 1] = -1 / eta
        return row

    for t in range(T):
        s = soc_row(t)
        rows.append(s); b.append(duration)           # full
        rows.append(-s); b.append(0.0)               # empty
    cyc = np.zeros(n)
    cyc[d0:d0 + T] = 1 / eta
    rows.append(cyc); b.append(duration)             # at most one full cycle a day
    for t in range(T):
        up = np.zeros(n); up[d0 + t] = 1
        dn = np.zeros(n); dn[c0 + t] = 1
        need_up = np.zeros(n)
        need_dn = np.zeros(n)
        for j, (is_up, hours) in enumerate(spec):
            goes_up, goes_dn = sides(is_up)
            if goes_up:
                up[r0[j] + t] = 1
                need_up[r0[j] + t] = hours / eta      # energy drawn from the battery to deliver the reserve
            if goes_dn:
                dn[r0[j] + t] = 1
                need_dn[r0[j] + t] = hours * eta      # energy the battery would store if the regulation were called
        rows.append(up); b.append(1.0)               # power: discharge plus upward reserves
        rows.append(dn); b.append(1.0)               # power: charge plus downward regulation
        for s in (soc_row(t - 1), soc_row(t)):       # energy behind the reserves, at the hour's start and its end
            if need_up.any():
                rows.append(need_up - s); b.append(0.0)
            if need_dn.any():
                rows.append(need_dn + s); b.append(duration)
    A = sparse.csr_matrix(np.array(rows))
    _STRUCT[k] = (A, np.array(b), n)
    return _STRUCT[k]


def solve_day(energy, reserves, spec, duration, rte=RTE, force_switch=False, caps=None):
    """One day's optimum for 1 MW. energy: the T hourly energy prices; reserves: one list of T capacity prices per
    product; spec: the products' (up, required hours). Returns a dict: total, energy, reserve (per product), the hourly
    charge, discharge, awards and state of charge, and whether the mixed-integer program was needed.
    Session 74: caps, one list of T values per product (or None): the most of each hour's award the battery may hold,
    per MW of its power, between 0 and 1 (the fleet-limited strategy, warehouse/analysis/battery_fleet_limited.py).
    None, or a cap of 1 everywhere, is the program of sessions 67 to 73 exactly."""
    T = len(energy)
    K = len(spec)
    eta = math.sqrt(rte)
    A, b, n = structure(T, duration, tuple(spec), eta)
    ub = np.ones(n)
    if caps is not None:
        for j, cap in enumerate(caps):
            ub[T * (2 + j):T * (3 + j)] = np.clip(np.asarray(cap, dtype=float), 0, 1)
    p = np.asarray(energy, dtype=float)
    obj = np.concatenate([p, -p] + [-np.asarray(r, dtype=float) for r in reserves])  # minimize cost less revenue
    neg = np.flatnonzero(p < 0) if not force_switch else np.arange(T)
    mip = bool(force_switch)
    x = None
    if not mip:
        res = linprog(obj, A_ub=A, b_ub=b, bounds=list(zip(np.zeros(n), ub)), method="highs")
        if res.status != 0:
            raise RuntimeError(f"the linear program did not solve: {res.message}")
        x = res.x
        # charging and discharging in one hour pays only at a negative price: only a switch forbids it there
        mip = bool(np.any(np.minimum(x[neg], x[T + neg]) > TOL))
    if mip:
        # one switch per negative-price hour: u = 1 charging allowed, u = 0 discharging allowed
        N = len(neg)
        sw = np.zeros((2 * N, n + N))
        for i, t in enumerate(neg):
            sw[i, t], sw[i, n + i] = 1, -1                   # charge <= u
            sw[N + i, T + t], sw[N + i, n + i] = 1, 1        # discharge <= 1 - u
        A2 = sparse.vstack([sparse.hstack([A, sparse.csr_matrix((A.shape[0], N))]), sparse.csr_matrix(sw)]).tocsr()
        b2 = np.concatenate([b, np.zeros(N), np.ones(N)])
        res = milp(np.concatenate([obj, np.zeros(N)]), constraints=LinearConstraint(A2, -np.inf, b2),
                   integrality=np.concatenate([np.zeros(n), np.ones(N)]), bounds=Bounds(0, np.concatenate([ub, np.ones(N)])))
        if res.status != 0:
            raise RuntimeError(f"the mixed-integer program did not solve: {res.message}")
        x = res.x[:n].copy()
    else:
        x = x.copy()
    # at a price of zero or more, charging and discharging together never pays; where a tie left both, net them
    # (the state of charge is unchanged, every limit is looser, and the revenue is the same or higher)
    both = np.minimum(x[:T], x[T:2 * T] / (eta * eta))
    both[p < 0] = 0
    x[:T] -= both
    x[T:2 * T] -= both * eta * eta
    x = np.clip(x, 0, 1)
    c, d = x[:T], x[T:2 * T]
    awards = [x[T * (2 + j):T * (3 + j)] for j in range(K)]
    e_rev = float(p @ (d - c))
    r_rev = [float(np.asarray(reserves[j], dtype=float) @ awards[j]) for j in range(K)]
    soc = np.cumsum(eta * c - d / eta)
    return dict(total=e_rev + sum(r_rev), energy=e_rev, reserve=r_rev, charge=c, discharge=d, awards=awards, soc=soc,
                mip=mip, delivered=float(d.sum()))


def check_day(sol, spec, duration, rte=RTE, tol=1e-6):
    """Every constraint of the day on a solution, hour by hour; the list of violations (empty when all hold)."""
    eta = math.sqrt(rte)
    c, d, soc, aw = sol["charge"], sol["discharge"], sol["soc"], sol["awards"]
    bad = []
    prev = 0.0
    for t in range(len(c)):
        up = sum(aw[j][t] for j, (is_up, _) in enumerate(spec) if sides(is_up)[0])
        dn = sum(aw[j][t] for j, (is_up, _) in enumerate(spec) if sides(is_up)[1])
        need_up = sum(aw[j][t] * h / eta for j, (is_up, h) in enumerate(spec) if sides(is_up)[0])
        need_dn = sum(aw[j][t] * h * eta for j, (is_up, h) in enumerate(spec) if sides(is_up)[1])
        if d[t] + up > 1 + tol:
            bad.append(f"hour {t}: discharge plus upward reserves {d[t] + up:.6f} MW per MW")
        if c[t] + dn > 1 + tol:
            bad.append(f"hour {t}: charge plus downward regulation {c[t] + dn:.6f} MW per MW")
        if soc[t] < -tol or soc[t] > duration + tol:
            bad.append(f"hour {t}: state of charge {soc[t]:.6f} outside 0 to {duration}")
        if need_up > min(prev, soc[t]) + tol:
            bad.append(f"hour {t}: upward reserves need {need_up:.6f} MWh, {min(prev, soc[t]):.6f} stored")
        if need_dn > duration - max(prev, soc[t]) + tol:
            bad.append(f"hour {t}: downward regulation needs {need_dn:.6f} MWh of room")
        prev = soc[t]
    if (d / eta).sum() > duration + tol:
        bad.append(f"more than one full cycle: {(d / eta).sum():.6f} MWh taken out")
    return bad


def as_prices(table, products):
    """{product key: hourly Series (UTC hour start)} from an ancillary price table."""
    a = pb.read_table(table)
    out = {}
    for p in products:
        x = a[(a["entity"] == p["entity"]) & (a["variable"] == p["variable"])]
        s = pd.Series(x["value"].values, index=pd.DatetimeIndex(x["ts"])).sort_index()
        if s.index.duplicated().any():
            raise RuntimeError(f"{table}: two prices for one hour of {p['entity']} {p['variable']}")
        out[p["key"]] = s
    return out


def energy_prices(iso, mk, log):
    """The hourly energy price of a market's main hub (complete hours only), and the tables it came from. On a machine
    without the ERCOT history (the GitHub runner: the yearly history is never restored there) ERCOT's price is the
    rolling table alone, and keep_fuller carries the months it does not reach."""
    table, market = pb.TABLES[(iso, mk)]
    if iso == "ercot" and not os.path.exists(os.path.join(ip.OUT_DIR, pb.HISTORY + ".csv")):
        df = pb.read_table(table, market=market, node=pb.MAIN[iso])
        log(f"  {iso} {mk}: {pb.HISTORY} is not on this machine; {len(df)} intervals of {table} only")
        return cp.hourly(df.sort_values("ts")), f"{table} ({pb.HISTORY} not on this machine)"
    df, table = cp.prices_of(iso, mk, log)
    return cp.hourly(df), f"{table} and {pb.HISTORY if iso == 'ercot' else cp.HUB_HISTORY}"


def day_hours(day, tz):
    """The UTC hour starts of a local day (23, 24 or 25 of them)."""
    a = pd.Timestamp(day).tz_localize(tz)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz)
    return pd.date_range(a.tz_convert("UTC"), b.tz_convert("UTC"), freq="h", inclusive="left")


def build_market(iso, energy, reserve, log, until=None):
    """Every local day of a market, solved for each strategy and duration.
    energy: {"rtm": hourly Series, "dam": hourly Series}; reserve: {product key: hourly Series}.
    Returns (days, left): days[(strategy, duration)][day] = the day's result; left[strategy] = [(day, reason)]."""
    m = ALL_MARKETS[iso]
    tz = pb.TZ[iso]
    last_as = min(s.index.max() for s in reserve.values())
    days, left = {(s, d): {} for s in STRATEGIES for d in DURATIONS}, {s: [] for s in STRATEGIES}
    for strat, mk in STRATEGIES.items():
        e = energy[mk]
        first = max(pd.Timestamp(m["start"]), e.index.min().tz_convert(tz).tz_localize(None).normalize())
        end = min(e.index.max(), last_as).tz_convert(tz).tz_localize(None).normalize()
        if until is not None:
            end = min(end, pd.Timestamp(until))
        n_mip = 0
        for ts in pd.date_range(first, end, freq="D"):
            day = ts.strftime("%Y-%m-%d")
            hrs = day_hours(day, tz)
            prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
            pr = [reserve[p["key"]].reindex(hrs) for p in prods]
            short = [p["key"] for p, s in zip(prods, pr) if s.isna().any()]
            ep = e.reindex(hrs)
            if short:
                left[strat].append((day, "ancillary: " + ", ".join(short)))
                continue
            if ep.isna().any():
                left[strat].append((day, f"energy: {int(ep.isna().sum())} of {len(hrs)} hours not held"))
                continue
            spec = tuple((p["up"], required_hours(p, day)[0]) for p in prods)
            for dur in DURATIONS:
                sol = solve_day(ep.values, [s.values for s in pr], spec, dur)
                bad = check_day(sol, spec, dur)
                if bad:
                    raise RuntimeError(f"{iso} {strat} {dur}h {day}: a constraint does not hold: {bad[0]}")
                n_mip += sol["mip"]
                days[(strat, dur)][day] = dict(energy=sol["energy"], total=sol["total"], delivered=sol["delivered"],
                                               **{p["key"]: v for p, v in zip(prods, sol["reserve"])})
        log(f"  {iso} {strat}: {len(days[(strat, DURATIONS[0])])} days solved, {len(left[strat])} left out, "
            f"{first:%Y-%m-%d} to {end:%Y-%m-%d}; {n_mip} day-durations needed the charge-or-discharge switch")
    return days, left


def days_in(month):
    a = pd.Timestamp(month + "-01")
    return int(((a + pd.offsets.MonthBegin(1)) - a).days)


def monthly_rows(iso, days, left, base):
    """The monthly table's rows of a market: variables <strategy>_<N>h_<metric>."""
    m = ALL_MARKETS[iso]
    keys = [p["key"] for p in m["products"]]
    rows = []
    for (strat, dur), by_day in sorted(days.items()):
        months = sorted({d[:7] for d in by_day} | {d[:7] for d, _ in left[strat]})
        for mo in months:
            ds = [v for d, v in by_day.items() if d[:7] == mo]
            lo = [(d, why) for d, why in left[strat] if d[:7] == mo]
            t = f"{mo}-01T00:00:00Z"
            pre = f"{strat}_{dur}h_"

            def add(metric, value, unit):
                rows.append(dict(base, ts_utc=t, variable=pre + metric, value=value, unit=unit,
                                 x_strategy=strat, x_duration_hours=dur, x_metric=metric))
            add("days_held", len(ds), "count")
            add("days_left_out", len(lo), "count")
            add("days_left_out_ancillary", sum(1 for _, why in lo if why.startswith("ancillary")), "count")
            add("days_left_out_energy", sum(1 for _, why in lo if why.startswith("energy")), "count")
            add("days_in_month", days_in(mo), "count")
            if not ds:
                continue  # no day held: no revenue row, never a zero
            energy = sum(v["energy"] for v in ds)
            by = {k: sum(v[k] for v in ds if k in v) for k in keys if any(k in v for v in ds)}
            add("revenue_energy_usd_per_mw", r4(energy), "USD/MW")
            for k, v in by.items():
                add(f"revenue_{k}_usd_per_mw", r4(v), "USD/MW")
            add("revenue_ancillary_usd_per_mw", r4(sum(by.values())), "USD/MW")
            add("revenue_total_usd_per_mw", r4(energy + sum(by.values())), "USD/MW")
            add("discharged_mwh_per_mw", r4(sum(v["delivered"] for v in ds)), "MWh/MW")
    return rows


def stress_rows(iso, days, base):
    """The stress table's rows: each held local day inside a stress event's window, per strategy and duration."""
    m = MARKETS[iso]
    keys = [p["key"] for p in m["products"]]
    wins = {w["event"]: (w["start"], w["end"]) for w in ew.EVENTS + ew.MULTI if w["event"] in STRESS}
    rows = []
    for (strat, dur), by_day in sorted(days.items()):
        for event in STRESS:
            a, b = wins[event]
            for day in sorted(d for d in by_day if a <= d <= b):
                v = by_day[day]
                pre = f"{strat}_{dur}h_"
                anc = sum(v[k] for k in keys if k in v)

                def add(metric, value):
                    rows.append(dict(base, ts_utc=f"{day}T00:00:00Z", freq="P1D", variable=pre + metric, value=r4(value),
                                     unit="USD/MW", x_strategy=strat, x_duration_hours=dur, x_metric=metric, event=event))
                add("revenue_energy_usd_per_mw", v["energy"])
                add("revenue_ancillary_usd_per_mw", anc)
                add("revenue_total_usd_per_mw", v["energy"] + anc)
    return rows


def keep_fuller(name, new, cols, log):
    """Never replace a month with one resting on fewer days. On a machine without the full price history (the GitHub
    runner holds the rolling tables only), a (hub, strategy, duration, month) whose earlier file held more days keeps
    its earlier rows, and earlier months this run could not reach are carried."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return new, 0
    old = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    if list(old.columns) != cols:
        raise RuntimeError(f"{name}: the earlier file's columns differ; nothing written")
    old["value"] = old["value"].astype(float)
    old["x_duration_hours"] = old["x_duration_hours"].astype(int)
    if new.empty:  # this machine's inputs reach none of the table's days (the stress days, without the ERCOT history)
        log(f"{name}: this machine's inputs reach none of its periods; the earlier file's {len(old)} rows are kept")
        return old, len(old)
    grp = ["entity", "x_strategy", "x_duration_hours", "ts_utc"]

    def held(df):
        if name == STRESS_NAME:
            return df.groupby(grp).size()  # a day is whole or absent
        return df[df["x_metric"] == "days_held"].set_index(grp)["value"]
    ho, hn = held(old), held(new)
    keep = [k for k in ho.index if k not in hn.index or ho[k] > hn[k]]
    if not keep:
        return new, 0
    ks = set(keep)
    ko = old[[k in ks for k in zip(*(old[c] for c in grp))]]
    kn = new[[k not in ks for k in zip(*(new[c] for c in grp))]]
    log(f"{name}: {len(ks)} (hub, strategy, duration, period) kept from the earlier file, which rests on more days "
        f"than this machine's inputs give ({len(ko)} rows)")
    return pd.concat([ko, kn], ignore_index=True), len(ko)


def carry_retrieved(name, out, key):
    """A row whose value did not change keeps its earlier retrieved_at (Decision 21), so the Supabase loader, which
    compares every column, rewrites only new or revised rows."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return out
    old = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    old["value"] = old["value"].astype(float)
    prev = {tuple(r[:-2]): (r[-2], r[-1]) for r in zip(*(old[c] for c in key), old["value"], old["retrieved_at"])}
    got = [prev.get(k) for k in zip(*(out[c] for c in key))]
    out = out.copy()
    out["retrieved_at"] = [g[1] if g is not None and g[0] == v else r
                           for g, v, r in zip(got, out["value"], out["retrieved_at"])]
    return out


def write_table(name, out, cols, header, log):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    ip._require_lock(path, f"writing {name}")  # the data lock (session 59), as ip.write_csv
    key = ["entity", "variable", "ts_utc"]
    if out.duplicated(key).any():
        raise RuntimeError(f"{name}: two rows share an (entity, variable, ts_utc) key")
    out = carry_retrieved(name, out, key).sort_values(key).reset_index(drop=True)[cols]
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        for h in header + [f"File holds {len(out)} rows, {out['ts_utc'].min()} to {out['ts_utc'].max()}, rewritten by this run."]:
            f.write("# " + h + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(path + ".tmp", path)
    log(f"{name}: {len(out)} rows")
    print(f"{name}.csv: rows={len(out)}")
    return len(out)


def not_above(table, entity, variable, others):
    """Session 86: the hours in which a product left out of the model is priced above the product kept in its place.
    {label: (hours compared, hours above)}. Zero above means leaving it out loses nothing: the kept product pays at
    least as much for the same megawatt in every hour."""
    a = pb.read_table(table)
    ref = a[(a["entity"] == entity) & (a["variable"] == variable)].set_index("ts")["value"]
    out = {}
    for e, v, label in others:
        o = a[(a["entity"] == e) & (a["variable"] == v)].set_index("ts")["value"]
        both = pd.concat([ref, o], axis=1, join="inner")
        out[label] = (len(both), int((both.iloc[:, 1] > both.iloc[:, 0] + 1e-9).sum()))
    return out


def review(in_dir, log, retrieved, only=None):
    """Session 86: the rows of the grids in review, and what the header states. A grid whose reserve table is not on
    this machine is skipped and named (the GitHub runner does not hold them)."""
    rows, used, counts, lines, skipped, checks = [], [], [], [], [], []
    for iso, m in REVIEW_MARKETS.items():
        if only and iso not in only:
            continue
        need = [m["as_table"], pb.TABLES[(iso, "rtm")][0], pb.TABLES[(iso, "dam")][0]]
        missing = [t for t in need if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
        if missing:
            skipped.append(f"{m['label']}: {', '.join(missing)} not on this machine")
            log(f"  review: {skipped[-1]}; the grid is left as the earlier file has it")
            continue
        energy = {}
        for mk in ("rtm", "dam"):
            energy[mk], tables = energy_prices(iso, mk, log)
            used.append(f"{iso} {mk}: {tables}, {len(energy[mk])} complete hours "
                        f"{ip.utc_iso(energy[mk].index.min())} to {ip.utc_iso(energy[mk].index.max())}")
        reserve = as_prices(m["as_table"], m["products"])
        if "dominated" in m:
            for label, (n, above) in not_above(m["as_table"], *m["dominant"], m["dominated"]).items():
                checks.append(f"{m['label']} {label}: priced above the product kept in {above} of {n} hours")
        days, left = build_market(iso, energy, reserve, log)
        hub = pb.MAIN[iso]
        geo = m["geo"] or sorted(set(pb.read_table(m["as_table"])["geo"]))[0]
        base = dict(entity=f"{iso}:{hub}", freq="P1M", geo=geo, market=iso, node=hub, source=SOURCE,
                    source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        rows += monthly_rows(iso, days, left, base)
        for strat in STRATEGIES:
            n = len(days[(strat, DURATIONS[0])])
            counts.append(f"{m['label']} {strat}: {n} days held, {len(left[strat])} left out"
                          + (" (" + "; ".join(f"{d} {why}" for d, why in left[strat][:8])
                             + ("; ..." if len(left[strat]) > 8 else "") + ")" if left[strat] else ""))
            for d, why in left[strat]:
                log(f"  left out: {iso} {strat} {d}: {why}")
        for p in m["products"]:
            for first, hours, src in p["hours"]:
                lines.append(f"{m['label']} {p['label']} ({p['key']}, {'up and down' if p['up'] == 'both' else 'up' if p['up'] else 'down'}), "
                             f"from {first}: {hours:g} hour(s); {src}")
    return rows, used, counts, lines, skipped, checks


def review_snapshot(table, run_id):
    """The page's file: the review table's rows by grid, compact. Every number in it is a row of the table."""
    grids = {}
    for iso, m in REVIEW_MARKETS.items():
        e = f"{iso}:{pb.MAIN[iso]}"
        t = table[table["entity"] == e].sort_values(["variable", "ts_utc"])
        if len(t):
            grids[iso] = dict(entity=e, rows=[[v, ts, float(x)] for v, ts, x in zip(t["variable"], t["ts_utc"], t["value"])])
    return dict(table=REVIEW_NAME, built=run_id, grids=grids)


def write_review(in_dir, log, retrieved, run_id, snapshot, out_dir=None):
    """Build and write the review table (and the page's snapshot); a list of status entries."""
    rows, used, counts, lines, skipped, checks = review(in_dir, log, retrieved)
    if out_dir:
        ip.set_out_dir(out_dir)  # the inputs are read; from here every write goes under the trial directory
    if not rows:
        msg = "no grid in review could be built: " + "; ".join(skipped)
        log(msg)
        return [dict(table=REVIEW_NAME, market="derived", status="skipped", detail=msg[:300])]
    cols = ip.SERIES_COLS + ["x_strategy", "x_duration_hours", "x_metric"]
    out, kept = keep_fuller(REVIEW_NAME, pd.DataFrame(rows)[cols], cols, log)
    n = write_table(REVIEW_NAME, out, cols, [
        "Energy Research Warehouse (ERW): the battery revenue stack on the grids in review (NYISO, SPP), energy and "
        "ancillary services co-optimized, per MW, by market, hub, duration (2, 4, 8 hours), strategy and local month "
        "(derived, session 86)",
        "Shape: series (docs/datastandard.md v0), partition column market; freq P1M, ts_utc the first day of the "
        "market's local month at 00:00:00Z. The variables are those of battery_stack_monthly: <strategy>_<N>h_<metric>, "
        "also in x_strategy, x_duration_hours and x_metric.",
        "In review: these grids are not in battery_stack_monthly and are not shown to visitors. The model is the one "
        "of battery_stack_monthly (docs/methods/battery_stack.md): round trip " + str(RTE) + ", each local day from empty, "
        "at most one full cycle a day, hourly, per MW; reserves are paid and never deployed.",
        "Required duration of each product: " + " | ".join(lines),
        "Products left out: NYISO's 10-Minute Non-Synchronous Reserve and 30-Minute Operating Reserve (a battery "
        "that can hold spinning reserve is paid at least as much for it: " + "; ".join(checks) + "); SPP's ramp "
        "capability and uncertainty products (RampUP, RampDN, UncUP: what a battery must hold behind them was not read).",
        "Never filled: a local day is solved only when every hour of the energy price and of every ancillary product "
        "is held. " + " | ".join(counts) + (" | skipped on this machine: " + "; ".join(skipped) if skipped else ""),
        "Not built: ISO-NE and MISO. Their reserve prices (isone_as_prices, miso_as_prices) are internal, so a result "
        "would be internal too; the page shows \"held, not shown: license needed\". PJM is not held.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/battery_stack.py",
        f"Run log: warehouse/output/logs/battery_stack_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, the battery revenue stack (docs/methods/battery_stack.md), {METHOD_URL}",
        "Derived from: iso_hub_prices_history; iso_rtm_hub_prices; iso_dam_hub_prices; nyiso_rtm_zone_prices; "
        "nyiso_dam_zone_prices; nyiso_as_prices; spp_as_prices",
        "Inputs: " + "; ".join(used),
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); every "
        "input is public (SPP's terms allow copying with citation and not commercial publication: spp_as_prices).",
        f"Kept from the earlier file (it rests on more days than this machine's inputs give): {kept} rows.",
    ], log)
    ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                        "report": "The battery revenue stack: energy and ancillary services co-optimized, per MW "
                                  "(docs/methods/battery_stack.md)",
                        "report_url": METHOD_URL, "document_list": "", "license": "public",
                        "tables": [NAME, STRESS_NAME, REVIEW_NAME]}])
    if snapshot:
        path = os.path.join(out_dir, "battery_stack_review.json") if out_dir else REVIEW_SNAPSHOT
        held = ip.read_series(os.path.join(ip.OUT_DIR, REVIEW_NAME + ".csv"), cols)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(review_snapshot(held, run_id), f, separators=(",", ":"), sort_keys=True)
            f.write("\n")
        log(f"review snapshot: {os.path.relpath(path, ROOT)}")
    return [dict(table=REVIEW_NAME, market="derived", status="ok", detail=f"{n} rows" + ("; " + "; ".join(skipped) if skipped else ""))]


def duration_lines():
    out = []
    for iso, m in MARKETS.items():
        for p in m["products"]:
            for first, hours, src in p["hours"]:
                out.append(f"{m['label']} {p['label']} ({p['key']}), from {first}: {hours:g} hour(s); {src}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the battery revenue stack (energy and ancillary services, co-optimized)")
    ap.add_argument("--out-dir", help="write the tables, log, registry and status under this directory; the inputs are "
                    "still read from warehouse/output")
    ap.add_argument("--review-only", action="store_true", help="session 86: build only the grids in review "
                    "(battery_stack_review_monthly); the live tables are not touched")
    ap.add_argument("--snapshot", action="store_true", help="session 86: also write site/data/battery_stack_review.json")
    a = ap.parse_args(argv)
    in_dir = ip.OUT_DIR
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if a.review_only:
        out_dir = os.path.abspath(a.out_dir) if a.out_dir else in_dir
        os.makedirs(os.path.join(out_dir, "logs"), exist_ok=True)
        log = ip.Log(os.path.join(out_dir, "logs", f"battery_stack_{run_id}.log"))
        try:
            retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            status = write_review(in_dir, log, retrieved, run_id, a.snapshot, a.out_dir)
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"FAILED:\n{tb}")
            print(f"battery_stack {REVIEW_NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            status = [dict(table=REVIEW_NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300])]
        ip.write_status("battery_stack_review", run_id, status)
        log.close()
        return 0 if all(s["status"] in ("ok", "skipped") for s in status) else 1
    missing = [t for t in ("ercot_as_prices", "caiso_as_prices", "iso_rtm_hub_prices", "iso_dam_hub_prices")
               if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if missing:
        # session 10 ruling 3: a derived script without its inputs skips with a warning
        print(f"battery_stack SKIPPED: input tables not on this machine: {', '.join(missing)}")
        ip.write_status("battery_stack", run_id, [dict(table=NAME, market="derived", status="skipped",
                                                       detail="inputs missing: " + ", ".join(missing))])
        return 0
    out_dir = os.path.abspath(a.out_dir) if a.out_dir else in_dir
    os.makedirs(os.path.join(out_dir, "logs"), exist_ok=True)
    log = ip.Log(os.path.join(out_dir, "logs", f"battery_stack_{run_id}.log"))
    status = []
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        rows, srows, used, counts = [], [], [], []
        for iso, m in MARKETS.items():
            energy = {}
            for mk in ("rtm", "dam"):
                energy[mk], tables = energy_prices(iso, mk, log)
                used.append(f"{iso} {mk}: {tables}, {len(energy[mk])} complete hours "
                            f"{ip.utc_iso(energy[mk].index.min())} to {ip.utc_iso(energy[mk].index.max())}")
            reserve = as_prices(m["as_table"], m["products"])
            days, left = build_market(iso, energy, reserve, log)
            hub = pb.MAIN[iso]
            base = dict(entity=f"{iso}:{hub}", freq="P1M", geo=m["geo"], market=iso, node=hub, source=SOURCE,
                        source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
            rows += monthly_rows(iso, days, left, base)
            srows += stress_rows(iso, days, base)
            for strat in STRATEGIES:
                n = len(days[(strat, DURATIONS[0])])
                counts.append(f"{m['label']} {strat}: {n} days held, {len(left[strat])} left out"
                              + (" (" + "; ".join(f"{d} {why}" for d, why in left[strat][:8])
                                 + ("; ..." if len(left[strat]) > 8 else "") + ")" if left[strat] else ""))
                for d, why in left[strat]:
                    log(f"  left out: {iso} {strat} {d}: {why}")
        if a.out_dir:
            ip.set_out_dir(a.out_dir)
        cols = ip.SERIES_COLS + ["x_strategy", "x_duration_hours", "x_metric"]
        scols = cols + ["event"]
        out, kept = keep_fuller(NAME, pd.DataFrame(rows)[cols], cols, log)
        sout, skept = keep_fuller(STRESS_NAME, pd.DataFrame(srows, columns=scols), scols, log)
        if sout.empty:
            raise RuntimeError(f"{STRESS_NAME}: no stress day could be built and no earlier file holds one")
        common = [
            f"Round trip {RTE} (the seller tab's battery: Lazard LCOS v10.0, utility-scale, low end); each local day from "
            "empty; at most one full cycle a day; hourly; per MW of rated power. Reserves are not deployed: an award is "
            "paid its capacity price and moves no energy.",
            "Strategies: foresight (perfect foresight, the upper bound: energy at the hourly mean of the real-time price, "
            "ancillary at day-ahead prices, all known in advance); dayahead (the day-ahead schedule: energy and ancillary "
            "at day-ahead prices, no real-time trading; assumes offers clear at the day-ahead price).",
            "Required duration of each product (stored energy behind an upward reserve; room behind downward regulation): "
            + " | ".join(duration_lines()),
            "Never filled: a local day is solved only when every hour of the energy price and of every ancillary product "
            "bought that day is held. " + " | ".join(counts),
            f"Retrieved: {run_id} (UTC) by warehouse/derived/battery_stack.py",
            f"Run log: warehouse/output/logs/battery_stack_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the battery revenue stack (docs/methods/battery_stack.md), {METHOD_URL}",
            "Derived from: ercot_all_hub_prices_history; iso_hub_prices_history; iso_rtm_hub_prices; iso_dam_hub_prices; "
            "ercot_as_prices; caiso_as_prices",
            "The stress events' windows are those of warehouse/derived/event_window.py (the code, not a table).",
            "Inputs: " + "; ".join(used),
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); every "
            "input is public. No capacity price is in it: iso_all_capacity_prices is internal and is not read.",
        ]
        n1 = write_table(NAME, out, cols, [
            "Energy Research Warehouse (ERW): the battery revenue stack, energy and ancillary services co-optimized, per MW, "
            "by market, hub, duration (2, 4, 8 hours), strategy and local month (derived, session 67)",
            "Shape: series (docs/datastandard.md v0), partition column market; freq P1M, ts_utc the first day of the "
            "market's local month at 00:00:00Z. Variables <strategy>_<N>h_<metric>, also in x_strategy, x_duration_hours and "
            "x_metric: revenue_energy_usd_per_mw, revenue_<product>_usd_per_mw, revenue_ancillary_usd_per_mw (the products' "
            "sum), revenue_total_usd_per_mw (USD/MW, the month's held days), discharged_mwh_per_mw, days_held, "
            "days_left_out (with _ancillary and _energy, the reason), days_in_month. A month with no day held has no "
            "revenue row.",
        ] + common + [f"Kept from the earlier file (it rests on more days than this machine's inputs give): {kept} rows."], log)
        n2 = write_table(STRESS_NAME, sout, scols, [
            "Energy Research Warehouse (ERW): the battery revenue stack on ERCOT's stress days, per MW and local day "
            "(Winter Storm Uri 2021, Winter Storm Elliott 2022, the summer 2023 heat), by duration and strategy (derived, session 67)",
            "Shape: series (docs/datastandard.md v0), partition column market; freq P1D, ts_utc the local day at 00:00:00Z. "
            "Variables <strategy>_<N>h_<metric>: revenue_energy_usd_per_mw, revenue_ancillary_usd_per_mw, "
            "revenue_total_usd_per_mw (USD/MW); event the event whose window holds the day "
            "(event_window.py: " + "; ".join(f"{w['event']} {w['start']} to {w['end']}" for w in ew.EVENTS + ew.MULTI if w["event"] in STRESS) + ").",
        ] + common + [f"Kept from the earlier file: {skept} rows."], log)
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "The battery revenue stack: energy and ancillary services co-optimized, per MW "
                                      "(docs/methods/battery_stack.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public",
                            "tables": [NAME, STRESS_NAME]}])
        status.append(dict(table=NAME, market="derived", status="ok", detail=f"{n1} rows"))
        status.append(dict(table=STRESS_NAME, market="derived", status="ok", detail=f"{n2} rows"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"battery_stack {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status = [dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300])]
    ip.write_status("battery_stack", run_id, status)
    log.close()
    return 0 if all(s["status"] == "ok" for s in status) else 1


if __name__ == "__main__":
    sys.exit(main())
