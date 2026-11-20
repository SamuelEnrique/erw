"""Session 9840, the battery model audit (docs/reviews/battery-model-audit-2026-11-20.md): a helper of its tests, not a
test itself. A sparse restatement of battery_stack.solve_day's program with switches, so one rule can be changed at a time:
  q      intervals per hour for energy (1: the model's hourly program; 4: 15-minute energy prices)
  blocks how the state of charge resets: each local day from empty (the model), or each block of several days
  dur    the duration bound (the model: s <= D at the storage side)
Reserves stay hourly. With q = 1 and one-day blocks the program is the model's own (checked in e1)."""
import math

import numpy as np
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

TOL = 1e-6


def sides(up):
    return (True, True) if up == "both" else (bool(up), not bool(up))


def solve_block(hours, dur, rte=0.86, cycles=1.0, q=1, mip_ok=True, reg_deploy=0.0, end_empty=False, deploy_in_cycle=True):
    """hours: list of dicts in time order, one per local hour of the block:
         {"day": "YYYY-MM-DD", "p": [q energy prices], "a": [K prices], "spec": ((up, h), ...) of K products}
    The products may differ in count by day? No: every day here has the same K (ERCOT from 2023-06-10).
    reg_deploy: a stylised deployment of regulation, the fraction of each regulation award delivered as energy in its hour
      (Reg Up discharged, Reg Down charged), paid at the hour's energy price, with the round-trip losses on the stored
      energy. 0 is the model. Returns dict(total, energy, reserve, mip)."""
    H = len(hours)
    K = len(hours[0]["a"])
    N = H * q
    dt = 1.0 / q
    eta = math.sqrt(rte)
    # variable layout
    c0, d0, s0, r0 = 0, N, 2 * N, 3 * N
    nv = 3 * N + H * K
    rid = lambda h, k: r0 + h * K + k  # noqa: E731
    obj = np.zeros(nv)
    for h, hr in enumerate(hours):
        for j in range(q):
            i = h * q + j
            obj[c0 + i] = hr["p"][j] * dt
            obj[d0 + i] = -hr["p"][j] * dt
        for k in range(K):
            obj[rid(h, k)] = -hr["a"][k]
            if reg_deploy and hr["keys"][k] in ("regup", "regdn"):
                ph = float(np.mean(hr["p"]))
                # deployed energy paid at the hour's price: Reg Up sells it, Reg Down buys it
                obj[rid(h, k)] += (-ph if hr["keys"][k] == "regup" else ph) * reg_deploy
    rows, cols, vals, lo, hi = [], [], [], [], []
    m = 0

    def add(entries, l, u):
        nonlocal m
        for cidx, v in entries:
            rows.append(m); cols.append(cidx); vals.append(v)
        lo.append(l); hi.append(u)
        m += 1
    # state of charge: s_i - s_{i-1} - eta dt c_i + dt/eta d_i = 0 (s_{-1} = 0 at the block start, and at each day start
    # when the block is one day). With deployment, the regulation energy moves the state of charge too.
    for h, hr in enumerate(hours):
        up_reg = [k for k, (u, hh) in enumerate(hr["spec"]) if reg_deploy and hr["keys"][k] == "regup"]
        dn_reg = [k for k, (u, hh) in enumerate(hr["spec"]) if reg_deploy and hr["keys"][k] == "regdn"]
        for j in range(q):
            i = h * q + j
            e = [(s0 + i, 1.0), (c0 + i, -eta * dt), (d0 + i, dt / eta)]
            if i > 0:
                e.append((s0 + i - 1, -1.0))
            for k in up_reg:
                e.append((rid(h, k), reg_deploy * dt / eta))
            for k in dn_reg:
                e.append((rid(h, k), -reg_deploy * dt * eta))
            add(e, 0.0, 0.0)
    for h, hr in enumerate(hours):
        ups = [k for k, (u, hh) in enumerate(hr["spec"]) if sides(u)[0]]
        dns = [k for k, (u, hh) in enumerate(hr["spec"]) if sides(u)[1]]
        for j in range(q):
            i = h * q + j
            add([(d0 + i, 1.0)] + [(rid(h, k), 1.0) for k in ups], -np.inf, 1.0)
            add([(c0 + i, 1.0)] + [(rid(h, k), 1.0) for k in dns], -np.inf, 1.0)
        # energy behind upward reserves and room behind regulation down, at every boundary of the hour
        pts = [h * q - 1] + [h * q + j for j in range(q)]   # index of s at the boundary; -1 means the block start (0)
        for pt in pts:
            need_up = [(rid(h, k), hr["spec"][k][1] / eta) for k in ups]
            need_dn = [(rid(h, k), hr["spec"][k][1] * eta) for k in dns]
            if pt < 0:
                if need_up:
                    add(need_up, -np.inf, 0.0)
                if need_dn:
                    add(need_dn, -np.inf, dur)
            else:
                if need_up:
                    add(need_up + [(s0 + pt, -1.0)], -np.inf, 0.0)
                if need_dn:
                    add(need_dn + [(s0 + pt, 1.0)], -np.inf, dur)
    # one cycle per local day: sum d dt / eta <= cycles x D
    days = {}
    for h, hr in enumerate(hours):
        days.setdefault(hr["day"], []).append(h)
    for d, hs in days.items():
        e = [(d0 + h * q + j, dt / eta) for h in hs for j in range(q)]
        if reg_deploy and deploy_in_cycle:  # deployed Reg Up takes energy out of the battery too
            e += [(rid(h, k), reg_deploy / eta) for h in hs for k in range(K) if hours[h]["keys"][k] == "regup"]
        add(e, -np.inf, cycles * dur)
    if end_empty:
        add([(s0 + N - 1, 1.0)], 0.0, 0.0)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(m, nv))
    lb = np.zeros(nv)
    ub = np.ones(nv)
    ub[s0:s0 + N] = dur
    lo, hi = np.array(lo), np.array(hi)
    res = milp(obj, constraints=LinearConstraint(A, lo, hi), integrality=np.zeros(nv), bounds=Bounds(lb, ub))
    if res.status != 0:
        raise RuntimeError(res.message)
    x = res.x
    p = np.concatenate([np.asarray(hr["p"], float) for hr in hours])
    neg = np.flatnonzero(p < 0)
    used_mip = False
    if mip_ok and len(neg) and np.any(np.minimum(x[c0 + neg], x[d0 + neg]) > TOL):
        used_mip = True
        nb = len(neg)
        A2 = sparse.hstack([A, sparse.csr_matrix((m, nb))]).tolil()
        extra_r, extra_c, extra_v, el, eh = [], [], [], [], []
        rr = 0
        for b, i in enumerate(neg):
            extra_r += [rr, rr]; extra_c += [c0 + i, nv + b]; extra_v += [1.0, -1.0]; el.append(-np.inf); eh.append(0.0); rr += 1
            extra_r += [rr, rr]; extra_c += [d0 + i, nv + b]; extra_v += [1.0, 1.0]; el.append(-np.inf); eh.append(1.0); rr += 1
        E = sparse.csr_matrix((extra_v, (extra_r, extra_c)), shape=(rr, nv + nb))
        A3 = sparse.vstack([A2.tocsr(), E]).tocsr()
        res = milp(np.concatenate([obj, np.zeros(nb)]), constraints=LinearConstraint(A3, np.concatenate([lo, el]), np.concatenate([hi, eh])),
                   integrality=np.concatenate([np.zeros(nv), np.ones(nb)]), bounds=Bounds(np.zeros(nv + nb), np.concatenate([ub, np.ones(nb)])))
        if res.status != 0:
            raise RuntimeError(res.message)
        x = res.x[:nv]
    c, d = x[c0:c0 + N], x[d0:d0 + N]
    e_rev = float((p * (d - c)).sum() * dt)
    r = x[r0:].reshape(H, K)
    a = np.array([hr["a"] for hr in hours], float)
    r_rev = (a * r).sum(axis=0)
    out = dict(total=e_rev + float(r_rev.sum()), energy=e_rev, reserve=r_rev, mip=used_mip, soc_end=float(x[s0 + N - 1]),
               x=x, N=N, H=H, K=K)
    if reg_deploy:
        # the regulation energy delivered and taken, paid at the hour's energy price (the hour's mean when q > 1)
        ph = np.array([np.mean(hr["p"]) for hr in hours])
        kup = [k for k, kk in enumerate(hours[0]["keys"]) if kk == "regup"]
        kdn = [k for k, kk in enumerate(hours[0]["keys"]) if kk == "regdn"]
        dep = float((ph * reg_deploy * (r[:, kup].sum(axis=1) - r[:, kdn].sum(axis=1))).sum())
        out["deploy_energy"] = dep
        out["total"] += dep   # the objective already counted it; the total now equals the objective's value
    return out
