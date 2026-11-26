"""Session 10227 (play audit): the home battery game re-done from its method note and its page's words, with none of the
site's code. The rules as docs/methods/battery_game.md and the page state them:

- a 15-minute interval at full power moves kW x 0.25 kWh at the meter; the square root of the round trip on the way in
  and again on the way out; the battery starts half full; charge stops at full, discharge at the reserve (Hard only);
- the fleet call: the clock hour (four intervals from the day's start) of the highest mean price, the earliest on a tie;
  each kWh delivered in it earns that hour's mean price again, never below zero;
- money starts at $5; the play ends in the interval it falls below $0;
- Hard: wear USD 0.11 per kWh taken out of the battery; the call hour's prices climb 25, 50, 75, 90 percent of the way to
  USD 5,000 (a price at or above the cap is left alone); the next eight intervals the grid is down and the house takes
  1.5 kW at the meter from the battery; if the battery cannot carry an interval, the lights go out, the round ends, and
  the whole outage's need is charged at USD 35,000 per MWh.

Two independent optima: (1) a dynamic programme over the three actions, written here; (2) a mixed-integer programme of a
battery free to run at any power from zero to full (scipy's HiGHS), and its linear relaxation. The plays: the best, a
naive clock rule, a bad one, selling first, idling.

    python restate.py      (reads runs/c10227/extract.json and site/data/battery_levels.json; writes restate.json, plays.json)
"""
import json
import math
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

CAP, RAMP, OUT_N, HOUSE_KW, VOLL, MONEY0 = 5000.0, (0.25, 0.5, 0.75, 0.9), 8, 1.5, 35000.0, 5.0


def rules(mode="normal", kwh=13.5, kw=5.0, rte=0.9, reserve=0.25, deg=0.11):
    hard = mode == "hard"
    return dict(mode=mode, kwh=kwh, kw=kw, eta=math.sqrt(rte), reserve=kwh * reserve if hard else 0.0, deg=deg if hard else 0.0,
                start=kwh / 2, emergency=hard)


def call_hour(p):
    best, first = -math.inf, 0
    for i in range(0, len(p) - 3, 4):
        m = (p[i] + p[i + 1] + p[i + 2] + p[i + 3]) / 4
        if m > best:
            best, first = m, i
    return first, best


def game_prices(p, R):
    """The prices traded at, and the outage's intervals (a set)."""
    if not R["emergency"]:
        return list(p), set()
    q = list(p)
    f, _ = call_hour(p)
    for k in range(4):
        if q[f + k] < CAP:
            q[f + k] = q[f + k] + (CAP - q[f + k]) * RAMP[k]
    return q, set(range(f + 4, min(len(p), f + 4 + OUT_N)))


def sim(p, acts, R):
    q, out = game_prices(p, R)
    f, m = call_hour(q)
    bonus_p = 0.0 if R.get("no_bonus") else max(0.0, m)
    g = R["kw"] * 0.25
    eta = R["eta"]
    need = HOUSE_KW * 0.25
    soc, cash, wear, bonus = R["start"], 0.0, 0.0, 0.0
    bought = cost = sold = rev = 0.0
    end, why, penalty = None, "", 0.0
    for i in range(len(q)):
        if i in out:
            take = need / eta
            if soc + 1e-12 < take:
                penalty = len(out) * need * VOLL / 1000
                end, why = i, "lights_out"
                break
            soc -= take
            continue
        a = acts[i]
        if a == 1:
            put = min(g * eta, R["kwh"] - soc)
            if put > 0:
                soc = R["kwh"] if put == R["kwh"] - soc else soc + put
                cash -= put / eta * q[i] / 1000
                bought += put / eta
                cost += put / eta * q[i]
        elif a == -1:
            room = soc - R["reserve"]
            if room > 0:
                take = min(g / eta, room)
                soc = R["reserve"] if take == room else soc - take
                out_kwh = take * eta
                cash += out_kwh * q[i] / 1000
                wear += take * R["deg"]
                sold += out_kwh
                rev += out_kwh * q[i]
                if f <= i <= f + 3:
                    bonus += out_kwh * bonus_p / 1000
        if MONEY0 + cash - wear + bonus < 0:
            end, why = i, "bankrupt"
            break
    score = cash - wear + bonus - penalty
    return dict(score=score, cash=cash, wear=wear, bonus=bonus, penalty=penalty, end=end, why=why, soc_end=soc,
                bought=bought, sold=sold, buy_avg=cost / bought if bought else None, sell_avg=rev / sold if sold else None)


def dp(p, R, min_end=None):
    """The best of every play of the three actions: each reachable state of charge kept at its best value. min_end: the
    charge the play must hold at the day's end (None: free, the game's rule); an early end then does not count."""
    q, out = game_prices(p, R)
    f, m = call_hour(q)
    bonus_p = 0.0 if R.get("no_bonus") else max(0.0, m)
    g, eta, need = R["kw"] * 0.25, R["eta"], HOUSE_KW * 0.25
    layer = {round(R["start"] * 1e9): (R["start"], 0.0, ())}
    ended = None
    for i in range(len(q)):
        nxt = {}
        for soc, val, path in layer.values():
            if i in out:
                take = need / eta
                if soc + 1e-12 < take:
                    v = val - len(out) * need * VOLL / 1000
                    if ended is None or v > ended[0]:
                        ended = (v, path + (0,))
                    continue
                s2 = soc - take
                k = round(s2 * 1e9)
                if k not in nxt or val > nxt[k][1]:
                    nxt[k] = (s2, val, path + (0,))
                continue
            for a in (1, 0, -1):
                s2, v = soc, val
                if a == 1:
                    put = min(g * eta, R["kwh"] - soc)
                    if put > 0:
                        s2 = R["kwh"] if put == R["kwh"] - soc else soc + put
                        v -= put / eta * q[i] / 1000
                elif a == -1:
                    room = soc - R["reserve"]
                    if room > 0:
                        take = min(g / eta, room)
                        s2 = R["reserve"] if take == room else soc - take
                        v += take * eta * q[i] / 1000 - take * R["deg"]
                        if f <= i <= f + 3:
                            v += take * eta * bonus_p / 1000
                if MONEY0 + v < 0:
                    if ended is None or v > ended[0]:
                        ended = (v, path + (a,))
                    continue
                k = round(s2 * 1e9)
                if k not in nxt or v > nxt[k][1]:
                    nxt[k] = (s2, v, path + (a,))
        layer = nxt
    if min_end is not None:
        layer = {k: t for k, t in layer.items() if t[0] >= min_end - 1e-9}
        ended = None
    best = max(layer.values(), key=lambda t: t[1]) if layer else None
    if ended is not None and (best is None or ended[0] > best[1]):
        acts = list(ended[1]) + [0] * (len(q) - len(ended[1]))
        return ended[0], acts, len(layer)
    return best[1], list(best[2]), len(layer)


def mip(p, R, integer=True, end_at_least=None, buy_add=None):
    """A battery free to run at any power from zero to full, every price known. Lights are kept on in the outage (the
    game's penalty makes that the best play on every case the game tests). end_at_least: the charge it must hold at the
    day's end (None: free). buy_add: USD/MWh added to every price it buys at (a retail charge), or None."""
    q, out = game_prices(p, R)
    f, m = call_hour(q)
    bonus_p = 0.0 if R.get("no_bonus") else max(0.0, m)
    n, g, eta = len(q), R["kw"] * 0.25, R["eta"]
    # variables: c (0..n-1), d (n..2n-1), s after interval (2n..3n-1), z charge (3n..4n-1), y discharge (4n..5n-1)
    N = 5 * n
    C, D, S, Z, Y = 0, n, 2 * n, 3 * n, 4 * n
    obj = np.zeros(N)
    for i in range(n):
        buy = buy_add[i] if isinstance(buy_add, list) else q[i] + (buy_add or 0.0)  # a list: the price bought at, each interval
        obj[C + i] = buy / 1000
        obj[D + i] = -(q[i] / 1000 + (bonus_p / 1000 if f <= i <= f + 3 else 0.0) - R["deg"] / eta)
    lo, hi = np.zeros(N), np.zeros(N)
    hi[C:C + n] = g
    hi[D:D + n] = g
    hi[S:S + n] = R["kwh"]
    hi[Z:Z + n] = 1
    hi[Y:Y + n] = 1
    A, b_lo, b_hi = [], [], []

    def row(coefs, l, h):
        r = np.zeros(N)
        for j, v in coefs:
            r[j] += v
        A.append(r); b_lo.append(l); b_hi.append(h)

    for i in range(n):
        prev = [] if i == 0 else [(S + i - 1, 1.0)]
        s0 = R["start"] if i == 0 else 0.0
        if i in out:
            hi[C + i] = hi[D + i] = 0
            hi[Z + i] = hi[Y + i] = 0
            take = HOUSE_KW * 0.25 / eta
            row([(S + i, 1.0)] + [(j, -v) for j, v in prev], s0 - take, s0 - take)
            continue
        # s_i = s_{i-1} + eta c - d / eta
        row([(S + i, 1.0), (C + i, -eta), (D + i, 1 / eta)] + [(j, -v) for j, v in prev], s0, s0)
        row([(C + i, 1.0), (Z + i, -g)], -np.inf, 0)
        row([(D + i, 1.0), (Y + i, -g)], -np.inf, 0)
        row([(Z + i, 1.0), (Y + i, 1.0)], -np.inf, 1)
        if R["reserve"] > 0:  # after a discharge the charge is at least the reserve
            row([(S + i, 1.0), (Y + i, -R["kwh"])], R["reserve"] - R["kwh"], np.inf)
    if end_at_least is not None:
        lo[S + n - 1] = end_at_least
    integ = np.zeros(N)
    if integer:
        integ[Z:] = 1
    res = milp(obj, constraints=LinearConstraint(np.array(A), b_lo, b_hi), bounds=Bounds(lo, hi), integrality=integ,
               options={"mip_rel_gap": 1e-9})
    if res.status != 0:
        return None
    return -res.fun


def hours_of(level):
    tz = ZoneInfo(level.get("tz") or "America/Chicago")
    return [datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(tz).hour for t in level["ts_utc"]]


def plays_for(level):
    h = hours_of(level)
    n = len(h)
    naive = [1 if 2 <= x < 5 else -1 if 17 <= x < 20 else 0 for x in h]
    bad = [1 if 17 <= x < 20 else -1 if 2 <= x < 5 else 0 for x in h]
    sell_first = [-1] * 8 + [0] * (n - 8)
    return {"naive": naive, "bad": bad, "sell_first": sell_first, "idle": [0] * n}


def load_levels():
    lv = json.load(open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8"))["levels"]
    ex = json.load(open(os.path.join(HERE, "extract.json"), encoding="utf-8"))
    day = sorted(ex["recent_rt"])[-1]
    r = sorted(ex["recent_rt"][day]["ercot:HB_HUBAVG"])
    today = {"slug": "today", "date": day, "grid": "ERCOT", "tz": "America/Chicago", "ts_utc": [x[0] for x in r], "price": [x[1] for x in r]}
    return [today] + lv, ex


def main():
    levels, _ = load_levels()
    out, plays = {}, {}
    for L in levels:
        p = L["price"]
        pl = plays_for(L)
        for mode in ("normal", "hard"):
            R = rules(mode)
            best, acts, states = dp(p, R)
            pl_m = dict(pl, best=acts)
            plays[f"{L['date']}|{mode}"] = pl_m
            res = {k: sim(p, a, R) for k, a in pl_m.items()}
            cont = mip(p, R, True)
            relax = mip(p, R, False)
            out[f"{L['date']}|{mode}"] = {"slug": L["slug"], "n": len(p), "dp": best, "dp_states_end": states, "mip_any_power": cont, "lp_relaxed": relax, "plays": res}
            print(f"{L['slug']:>16} {L['date']} {mode:>6} n={len(p)} dp={best:.6f} sim(best)={res['best']['score']:.6f} any-power={cont:.6f} "
                  f"lp={relax:.6f} naive={res['naive']['score']:.4f} bad={res['bad']['score']:.4f} sell_first={res['sell_first']['score']:.4f} "
                  f"end_soc(best)={res['best']['soc_end']:.4f} why={res['best']['why'] or '-'}")
    json.dump(out, open(os.path.join(HERE, "restate.json"), "w"), indent=1)
    json.dump({k: v for k, v in plays.items()}, open(os.path.join(HERE, "plays.json"), "w"))


if __name__ == "__main__":
    main()
