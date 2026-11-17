"""The home battery game (/play/battery): every number the end screen shows a player, recomputed from the game's own
stated rules and the price tables it reads.

Energy Research Warehouse (ERW), session 7535 (chain 304, part A). Written from docs/methods/battery_game.md and the
public tables alone, not from the page's code: the rules below are the note's sentences, each named where it is used.

What it reads:
- replication/battery_game/cases.json: the plays (a frozen level, a mode, the settings, the 15-minute actions). The
  perfect play's actions are the page's own plan; the others are stated rules (wait all day, the 8 cheapest and 8
  dearest intervals, charge all day, sell all day on Hard with no reserve).
- replication/battery_game/page_figures.json: what the page printed for each case (site/scripts/battery-game-figures.mjs
  draws the end screen with the site's own components and reads each number off the words).
- site/data/battery_levels.json: the seven frozen days (prices, timestamps, the rooftop solar shape).
- With --tables DIR (default: warehouse/output of this copy): the price tables the days were frozen from
  (ercot_all_hub_prices_history, iso_rtm_hub_prices, iso_hub_prices_history), to check every frozen price against its
  row, and the claims the day list makes about each day ("the lowest average ... since 2015", "the narrowest range").
  Absent tables are said, never filled.

    python replication/battery_game/replicate.py [--tables DIR] [--verbose]

Prints one line per difference and "N of N" at the end; exits 0 when every figure is inside half the page's last
shown digit (times and words: equal), 1 otherwise.
"""
import argparse
import csv
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ---- the note's rules ("The battery's settings", "Difficulties", "Version 3", "Version 4", "Version 5") -------------
CAP = 5000.0                       # Version 3: the spike climbs toward USD 5,000/MWh
RAMP = [0.25, 0.5, 0.75, 0.9]      # Version 3: interval k of the hour is p + (5000 - p) x r_k
OUTAGE_INTERVALS = 8               # Version 3: the eight intervals (two hours) after the spike, clipped at the day's end
HOUSE_KW = 1.5                     # Version 3: the house draws 1.5 kW in the outage
VOLL = 35000.0                     # Version 4: lights out at USD 35,000 per MWh, the PUCT's value of lost load
START_MONEY = 5.0                  # Version 3: every play starts with $5
SOLAR_KW = 5.0                     # Version 4: a 5 kW rooftop array
FLEET = 10000                      # Version 5: the fleet of 10,000 homes
MIN = 15                           # each interval is 15 minutes


def rules(settings, difficulty, addons):
    """Difficulties: Easy and Normal enforce neither the reserve nor the wear; Hard enforces both, has the emergency,
    and alone may carry the rooftop add-on."""
    hard = difficulty == "hard"
    return {
        "kwh": settings["kwh"], "kw": settings["kw"], "rte": settings["rte"], "eta": math.sqrt(settings["rte"]),
        "reserve": settings["kwh"] * settings["reserve"] if hard else 0.0, "deg": settings["deg"] if hard else 0.0,
        "start": settings["kwh"] * 0.5, "emergency": hard, "solar": hard and "solar" in addons,
    }


def call_hour(p):
    """The fleet call: the day's dearest clock hour (four intervals from the day's start), the earliest on a tie."""
    best, first = -math.inf, 0
    for i in range(0, len(p) - 3, 4):
        m = (p[i] + p[i + 1] + p[i + 2] + p[i + 3]) / 4
        if m > best:
            best, first = m, i
    return first, best


def emergency(real, R):
    """Version 3: on Hard, the dearest hour of the real prices climbs toward the cap (a price already at or above the cap
    is left: 'On Uri the dearest hour is already above the cap, so the game leaves it unchanged'), then the outage."""
    if not R["emergency"]:
        return list(real), None, None
    first, _ = call_hour(real)
    p = list(real)
    for k in range(4):
        if p[first + k] < CAP:
            p[first + k] = p[first + k] + (CAP - p[first + k]) * RAMP[k]
    o0, o1 = first + 4, min(len(real) - 1, first + 3 + OUTAGE_INTERVALS)
    return p, (first, first + 3), ((o0, o1) if o0 <= o1 else None)


def roof_kwh(level, R):
    """Version 4: 5 kW times the fleet's output per MW installed, kept between 0 and 1, for 15 minutes."""
    if not R["solar"]:
        return [0.0] * len(level["price"])
    return [SOLAR_KW * min(1.0, max(0.0, v)) * MIN / 60 for v in level["solar"]]


def move(soc, a, price, R):
    """The fixed rules: each interval at full power moves kW x 0.25 kWh at the meter; the efficiency is split evenly (the
    square root of the round trip in, and again out); a charge stops at full, a sale at the reserve (Hard) or empty; the
    wear is charged per kWh taken out of the battery, before the outbound loss."""
    grid = R["kw"] * MIN / 60
    if a == 1:
        stored = min(grid * R["eta"], R["kwh"] - soc)
        if stored <= 0:
            return soc, 0.0, 0.0, 0.0, 0.0
        bought = stored / R["eta"]
        return (R["kwh"] if stored == R["kwh"] - soc else soc + stored), -bought * price / 1000, 0.0, 0.0, bought
    if a == -1:
        room = soc - R["reserve"]
        if room <= 0:
            return soc, 0.0, 0.0, 0.0, 0.0
        taken = min(grid / R["eta"], room)
        out = taken * R["eta"]
        return (R["reserve"] if taken == room else soc - taken), out * price / 1000, taken * R["deg"], out, 0.0
    return soc, 0.0, 0.0, 0.0, 0.0


def roof_money(sun, price, stored, R):
    """Version 4, 'Below zero the roof is curtailed': at a price of zero or more the roof's power earns the price
    whatever the battery does; below zero it earns only as far as the charging battery takes it (that power replaces
    grid power the battery would have been paid to take), and the rest is switched off."""
    if price >= 0 or sun <= 0:
        return sun * price / 1000
    return min(sun, max(0.0, stored) / R["eta"]) * price / 1000


def outage_move(soc, sun, R):
    """Version 4, 'In the outage': the roof carries the house first; what is left charges the battery up to its power and
    its room; what the roof does not cover comes from the battery at the outbound loss. None: lights out (the battery
    holds less than one interval's draw)."""
    need = HOUSE_KW * MIN / 60
    if sun >= need:
        stored = min((sun - need) * R["eta"], R["kw"] * MIN / 60 * R["eta"], R["kwh"] - soc)
        return soc if stored <= 0 else (R["kwh"] if stored == R["kwh"] - soc else soc + stored)
    taken = (need - sun) / R["eta"]
    return None if soc + 1e-12 < taken else soc - taken


def play(level, actions, R):
    """A whole play. Money is $5 plus the market cash, less the wear, plus the fleet bonus and the roof's sales; in the
    first interval it falls below $0 the game ends (that interval's trade stands; nothing after it counts). On Hard the
    spiked prices are the ones traded; in the outage the action is ignored; lights out ends the round and charges the
    unserved energy of the whole outage (the house's need less the roof) at the value of lost load. The fleet bonus: each
    kWh delivered in the call hour earns the hour's mean price again, never below zero (the hour and its mean read on the
    prices played)."""
    real = level["price"]
    P, spike, out = emergency(real, R)
    vf, vmean = call_hour(P)
    bonus_price = max(0.0, vmean)
    sun = roof_kwh(level, R)
    need = HOUSE_KW * MIN / 60
    soc = R["start"]
    s = {"cash": 0.0, "wear": 0.0, "bonus": 0.0, "roof": 0.0, "penalty": 0.0, "unserved": 0.0, "end": None, "why": "",
         "out_start": None, "bought": 0.0, "cost": 0.0, "sold": 0.0, "revenue": 0.0, "vpp_kwh": 0.0}
    path, gain = [soc], [0.0] * len(P)
    for i in range(len(P)):
        if out and out[0] <= i <= out[1]:
            if i == out[0]:
                s["out_start"] = soc
            nxt = outage_move(soc, sun[i], R)
            if nxt is None:
                kwh = sum(max(0.0, need - sun[j]) for j in range(out[0], out[1] + 1))
                s["penalty"], s["unserved"], gain[i] = kwh * VOLL / 1000, kwh, -kwh * VOLL / 1000
                soc = 0.0
                path.append(soc)
                s["end"], s["why"] = i, "lights_out"
                break
            soc = nxt
            path.append(soc)
            continue
        new, cash, wear, out_kwh, bought = move(soc, actions[i], P[i], R)
        roof = roof_money(sun[i], P[i], new - soc, R)
        in_call = vf <= i <= vf + 3
        b = out_kwh * bonus_price / 1000 if in_call else 0.0
        if in_call:
            s["vpp_kwh"] += out_kwh
        s["cash"] += cash
        s["wear"] += wear
        s["roof"] += roof
        s["bonus"] += b
        s["bought"] += bought
        s["cost"] += bought * P[i]
        s["sold"] += out_kwh
        s["revenue"] += out_kwh * P[i]
        gain[i] = cash - wear + roof + b
        soc = new
        path.append(soc)
        if START_MONEY + s["cash"] - s["wear"] + s["roof"] + s["bonus"] < 0:
            s["end"], s["why"] = i, "bankrupt"
            break
    s["score"] = s["cash"] - s["wear"] + s["bonus"] + s["roof"] - s["penalty"]
    s["need"] = sum(max(0.0, need - sun[j]) / R["eta"] for j in range(out[0], out[1] + 1)) if out else 0.0
    s.update(path=path, gain=gain, P=P, spike=spike, out=out, call=vf)
    return s


def best_score(level, R):
    """'The perfect-foresight optimum': dynamic programming over every state of charge the three actions can reach; two
    paths that meet at one state keep the better; a path that goes bankrupt or dark ends with the score it had and
    competes with every path that continues; in the outage the only move is the forced draw."""
    real = level["price"]
    P, spike, out = emergency(real, R)
    vf, vmean = call_hour(P)
    bonus_price = max(0.0, vmean)
    sun = roof_kwh(level, R)
    need = HOUSE_KW * MIN / 60
    layer = {round(R["start"] * 1e9): (R["start"], 0.0)}
    ended = -math.inf
    for i in range(len(P)):
        nxt = {}
        if out and out[0] <= i <= out[1]:
            dark = sum(max(0.0, need - sun[j]) for j in range(out[0], out[1] + 1)) * VOLL / 1000
            for soc, v in layer.values():
                new = outage_move(soc, sun[i], R)
                if new is None:
                    ended = max(ended, v - dark)
                    continue
                k = round(new * 1e9)
                if k not in nxt or v > nxt[k][1]:
                    nxt[k] = (new, v)
            layer = nxt
            continue
        in_call = vf <= i <= vf + 3
        for soc, v in layer.values():
            for a in (1, 0, -1):
                new, cash, wear, out_kwh, _ = move(soc, a, P[i], R)
                val = v + cash - wear + roof_money(sun[i], P[i], new - soc, R) + (out_kwh * bonus_price / 1000 if in_call else 0.0)
                if START_MONEY + val < 0:
                    ended = max(ended, val)
                    continue
                k = round(new * 1e9)
                if k not in nxt or val > nxt[k][1]:
                    nxt[k] = (new, val)
        layer = nxt
    return max([v for _, v in layer.values()] + [ended])


def no_battery(level, R):
    """The end table (session 290): no battery; with the roof, its power sold as it is made (switched off below zero,
    nothing in the outage)."""
    P, _, out = emergency(level["price"], R)
    sun = roof_kwh(level, R)
    return sum(roof_money(sun[i], P[i], 0.0, R) for i in range(len(P)) if not (out and out[0] <= i <= out[1]))


# ---- what the page prints, as the note words it ----------------------------------------------------------------------
def clock(level, i):
    tz = ZoneInfo(level.get("tz") or "America/Chicago")
    return datetime.strptime(level["ts_utc"][i], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(tz).strftime("%H:%M")


def clock_end(level, i):
    tz = ZoneInfo(level.get("tz") or "America/Chicago")
    t = datetime.strptime(level["ts_utc"][i], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) + timedelta(minutes=15)
    return t.astimezone(tz).strftime("%H:%M")


def js_round(x):
    return math.floor(x + 0.5)


def moves_of(path):
    """What the battery did in each interval, read from its charge: up is a charge, down a sale, else a wait."""
    return [1 if path[i + 1] - path[i] > 1e-12 else -1 if path[i + 1] - path[i] < -1e-12 else 0 for i in range(len(path) - 1)]


def runs_text(level, did, which):
    """The debrief's runs: 'HH:MM to HH:MM', the first four joined by commas and 'and', then ', and N more'."""
    out, i = [], 0
    while i < len(did):
        if did[i] != which:
            i += 1
            continue
        j = i
        while j + 1 < len(did) and did[j + 1] == which:
            j += 1
        out.append(f"{clock(level, i)} to {clock_end(level, j)}")
        i = j + 1
    if not out:
        return None
    if len(out) == 1:
        return out[0]
    shown = out[:4]
    more = f", and {len(out) - 4} more" if len(out) > 4 else ""
    return f"{', '.join(shown[:-1])} and {shown[-1]}{more}"


def worst_hour(level, mine, perfect, R):
    """Session 66, the end's hour: the clock hour where the play earned the least against the perfect battery (the two
    plays' per-interval earnings summed by hour; the first such hour on a tie), what the perfect battery did in most of
    its intervals (on a tie: sold, then charged, then held), and the mean price of those intervals."""
    P, out = mine["P"], mine["out"]
    real = level["price"]
    best = None
    for first in range(0, len(P), 4):
        last = min(len(P) - 1, first + 3)
        a = sum(mine["gain"][first:last + 1])
        b = sum(perfect["gain"][first:last + 1])
        if b - a <= 1e-9 or (best and b - a <= best["lost"]):
            continue
        did = []
        for i in range(first, last + 1):
            o = out and out[0] <= i <= out[1]
            d = perfect["path"][i + 1] - perfect["path"][i] if i + 1 < len(perfect["path"]) else 0.0
            did.append(0 if o else 1 if d > 1e-12 else -1 if d < -1e-12 else 0)
        most = -1
        for y in (1, 0):
            if did.count(y) > did.count(most):
                most = y
        at = [first + k for k, v in enumerate(did) if v == most]
        price = sum(P[i] for i in at) / len(at)
        realp = sum(real[i] for i in at) / len(at)
        spike = any(P[i] != real[i] for i in at)
        overlaps = bool(out and first <= out[1] and last >= out[0])
        best = {"lost": b - a, "from": clock(level, first), "to": clock_end(level, last), "mine": a, "perfect": b, "did": most,
                "dark": most == 0 and overlaps, "price": price, "real": realp, "spike": spike}
    return best


def expected(case, level, R, cache):
    """Every figure the page prints for one case, recomputed."""
    key = (case["level"], case["mode"])
    if key not in cache:
        cache[key] = best_score(level, R)
    opt = cache[key]
    mine = play(level, case["actions"], R)
    plan = next(c for c in CASES if c["level"] == case["level"] and c["mode"] == case["mode"] and c["play"] == "perfect")
    perfect = play(level, plan["actions"], R)
    e = {}
    # the end table (session 290)
    for who, s in (("you", mine), ("perfect", perfect)):
        if s is None:
            continue
        e[f"end_{who}_earned"] = s["score"] if who == "you" else opt
        e[f"end_{who}_bought_kwh"] = s["bought"]
        e[f"end_{who}_sold_kwh"] = s["sold"]
        if s["bought"] > 0:
            e[f"end_{who}_bought_price"] = s["cost"] / s["bought"]
        if s["sold"] > 0:
            e[f"end_{who}_sold_price"] = s["revenue"] / s["sold"]
    e["end_none_earned"] = no_battery(level, R)
    e["end_none_bought_kwh"] = "none"
    e["end_none_sold_kwh"] = "none"
    if perfect is not None:
        if perfect["bought"] > 0 and perfect["sold"] > 0:
            bp, sp = perfect["cost"] / perfect["bought"], perfect["revenue"] / perfect["sold"]
            e.update(why_buy_price=bp, why_sell_price=sp, why_spread=sp - bp, why_loss_pct=js_round((1 - R["rte"]) * 100))
            if R["deg"] > 0:
                e["why_wear"] = R["deg"]
        elif perfect["sold"] > 0:
            e["why_sell_price"] = perfect["revenue"] / perfect["sold"]
        else:
            e["why_wait"] = "no hour paid"
    # the early end
    e["early_end"] = mine["why"] or "none"
    if mine["why"]:
        e["early_at"] = clock(level, mine["end"])
    if mine["why"] == "lights_out":
        e.update(early_unserved_kwh=mine["unserved"], early_voll=VOLL, early_penalty=mine["penalty"], early_need_kwh=mine["need"], early_start_kwh=mine["out_start"] or 0.0)
    # the hour lost the most (Normal and Hard)
    if case["difficulty"] != "easy" and perfect is not None:
        w = worst_hour(level, mine, perfect, R)
        if w is None:
            e["worst"] = "matched"
        else:
            e.update(worst_from=w["from"], worst_to=w["to"], worst_perfect=w["perfect"], worst_mine=w["mine"])
            if w["dark"]:
                e["worst_did"] = "grid down"
            else:
                e["worst_did"] = {-1: "sold power", 1: "charged up (bought power)", 0: "waited"}[w["did"]]
                e["worst_price"] = w["price"]
                if w["spike"]:
                    e["worst_real"] = w["real"]
    # in detail, and the two fleets (session 7551, the read's row 1: the line in detail is printed on Easy too)
    e["detail_cash"] = mine["cash"]
    if mine["wear"] > 0:
        e["detail_wear"] = mine["wear"]
    if mine["bonus"] > 0:
        e["detail_bonus"] = mine["bonus"]
    if R["solar"]:
        e["detail_roof"] = mine["roof"]
    if mine["penalty"] > 0:
        e["detail_penalty"] = mine["penalty"]
    e["fleet_mine"] = mine["score"] * FLEET
    e["fleet_perfect"] = opt * FLEET
    # session 7551 (the read's row 2): the trades' own money (the market alone) per kW of the battery's power
    e["real_mine_kw"] = mine["cash"] / R["kw"]
    e["real_perfect_kw"] = perfect["cash"] / R["kw"]
    e["share_pct"] = js_round(mine["score"] / opt * 100) if opt > 0 else "none"
    return e, mine, perfect, opt


def day_expected(level, R, plan_actions, opt):
    """The debrief and Hard's notice, once a level and mode."""
    e = {}
    real = level["price"]
    pk, lo = real.index(max(real)), real.index(min(real))
    perfect = play(level, plan_actions, R)
    did = moves_of(perfect["path"])
    # the debrief names the plan's trades ("buy when power is cheap, sell when it is dear"); in the outage there is no
    # market and no trade (the battery carries the house, or the roof charges it), so those intervals are not runs
    o = perfect["out"]
    market = [0 if (o and o[0] <= i <= o[1]) else d for i, d in enumerate(did)]
    e.update(deb_peak=real[pk], deb_peak_at=clock(level, pk), deb_low=real[lo], deb_low_at=clock(level, lo), deb_vpp_at=clock(level, perfect["call"]))
    ch, dis = runs_text(level, market, 1), runs_text(level, market, -1)
    e["deb_charged"] = f"charged {ch}" if ch else "never charged"
    e["deb_discharged"] = f"discharged {dis}" if dis else "never discharged"
    e.update(deb_kwh=R["kwh"], deb_kw=R["kw"], deb_loss_pct=js_round((1 - R["rte"]) * 100))
    if R["reserve"] > 0:
        e["deb_reserve_kwh"] = R["reserve"]
    if R["deg"] > 0:
        e["deb_wear"] = R["deg"]
    if R["emergency"]:
        need = perfect["need"]
        if need > 0:
            e.update(keep_need=need, keep_reserve=R["reserve"])
            if R["reserve"] + 1e-9 >= need:
                e["keep_verdict"] = "enough by itself"
            else:
                e["keep_verdict"] = f"so keep at least {need:.2f} kWh"
                e["keep_at_least"] = need
            e["outage_charge"] = need * R["eta"] * VOLL / 1000
        else:
            # the roof carries the house through the whole outage: the battery cannot run dry, and the banner says so
            # (faults file, row 5: it said a dark house would pay $0.00)
            e["keep"] = "roof" if R["solar"] else "none"
            e["outage_charge"] = "roof" if R["solar"] else 0.0
    # the plan as the page states it scores the optimum, and keeps no move that moves nothing (faults file, row 3)
    noop = sum(1 for i, a in enumerate(plan_actions) if a != 0 and did[i] == 0 and not (perfect["out"] and perfect["out"][0] <= i <= perfect["out"][1]) and (perfect["end"] is None or i <= perfect["end"]))
    return e, perfect["score"], noop


def glance_expected(level):
    """Version 5, the day at a glance (session 3600 added the typical range): the lowest, the mean and the highest real
    price; the standard deviation of the day's own intervals (divided by their count); the mean plus or minus one
    deviation, kept within the lowest and the highest."""
    p = level["price"]
    n = len(p)
    avg = sum(p) / n
    sd = math.sqrt(sum((v - avg) ** 2 for v in p) / n)
    return {"glance_lo": min(p), "glance_avg": avg, "glance_hi": max(p), "glance_typ_lo": max(min(p), avg - sd), "glance_typ_hi": min(max(p), avg + sd),
            "glance_cheap": avg, "glance_n": n, "glance_sd": sd}


RULES_PAGE = {  # the page's rules section, from the note
    "start_money": START_MONEY, "ramp": "25, 50, 75, 90", "cap": CAP, "house_kw": HOUSE_KW, "voll": VOLL,
    "lights_out_2h": VOLL * HOUSE_KW * 2 / 1000,              # 'USD 105.00 for a whole two-hour outage'
    "voll_study": 35685.0, "voll_residential": 3964.0, "solar_kw": SOLAR_KW,
    "reserve_pct": 25, "reserve_kwh": 13.5 * 0.25, "outage_need_kwh": HOUSE_KW * 2 / math.sqrt(0.9),
    "fleet_mw": FLEET * 5 / 1000, "fleet_mwh": FLEET * 13.5 / 1000, "deg_default": 721 * 25 / 158000, "kwh_default": 13.5, "kw_default": 5.0, "rte_default_pct": 90,
}


def same(shown, want):
    """A figure is the same when it is inside half the page's last shown digit; a time or a phrase when it is equal."""
    if isinstance(want, str):
        return shown == want, 0.0
    s = shown.replace("$", "").replace(",", "")
    try:
        v = float(s)
    except ValueError:
        return False, math.inf
    dec = len(s.split(".")[1]) if "." in s else 0
    return abs(v - want) <= 0.5 * 10 ** -dec + 1e-9, abs(v - want)


# ---- the price tables ------------------------------------------------------------------------------------------------
def read_rows(path, keep):
    """The rows of a warehouse table the test keeps (the '#' header skipped)."""
    with open(path, encoding="utf-8") as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        return [r for r in rows if keep(r)]


def tables_check(levels, tdir, verbose):
    """Every frozen price against its row, and the day list's claims against the tables."""
    out = []
    if not tdir or not os.path.isdir(tdir):
        return [("tables", None, f"not on this copy ({tdir}): the frozen prices are not checked against their rows")]
    want = {}
    for lv in levels:
        want.setdefault(lv["table"], []).append(lv)
    hub_days = {}
    for table, lvs in want.items():
        path = os.path.join(tdir, f"{table}.csv")
        if not os.path.exists(path):
            out.append((table, None, f"{table}.csv is not on this copy: {', '.join(l['date'] for l in lvs)} not checked"))
            continue
        ents = {(l["entity"], l["variable"]) for l in lvs}
        rows = read_rows(path, lambda r: (r["entity"], r["variable"]) in ents)
        by = {(r["entity"], r["variable"], r["ts_utc"]): r for r in rows}
        for lv in lvs:
            bad = 0
            for ts, v in zip(lv["ts_utc"], lv["price"]):
                r = by.get((lv["entity"], lv["variable"], ts))
                if r is None or abs(float(r["value"]) - v) > 1e-9:
                    bad += 1
            out.append((table, bad == 0, f"{lv['date']} {lv['entity']} {lv['variable']}: {len(lv['price']) - bad} of {len(lv['price'])} prices equal their rows"))
        if table == "ercot_all_hub_prices_history":
            for r in rows:
                if r["entity"] == "ercot:HB_HUBAVG" and r["variable"] == "spp_rtm":
                    d = datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/Chicago")).date().isoformat()
                    hub_days.setdefault(d, {})[r["ts_utc"]] = float(r["value"])
    if hub_days:
        def n_of(d):
            """The 15-minute intervals of an operating day: 96, or 92 and 100 on the clock changes."""
            tz = ZoneInfo("America/Chicago")
            a = datetime.fromisoformat(d + "T00:00").replace(tzinfo=tz)
            b = datetime.fromisoformat((a.date() + timedelta(days=1)).isoformat() + "T00:00").replace(tzinfo=tz)
            return round((b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() / 900)
        full = {d: list(v.values()) for d, v in hub_days.items() if len(v) == n_of(d)}
        means = {d: sum(v) / len(v) for d, v in full.items()}
        low = min(means, key=means.get)
        out.append(("claim", low == "2025-01-05", f"'the lowest average real-time price of any day since 2015': the table's lowest of {len(full)} complete days is {low}, mean {means[low]:.4f} USD/MWh (the page's day 2025-01-05, mean {means.get('2025-01-05', float('nan')):.4f})"))
        spring = {d: max(v) - min(v) for d, v in full.items() if "2026-03-01" <= d <= "2026-05-31"}
        if spring:
            nar = min(spring, key=spring.get)
            out.append(("claim", nar == "2026-04-26", f"'the narrowest range of real-time prices of any day, March to May 2026': the table's narrowest of {len(spring)} complete days is {nar}, {spring[nar]:.2f} USD/MWh"))
    return out


def day_claims(levels):
    """The figures the day list prints in a day's line, from the day's own prices."""
    out = []
    by = {l["slug"]: l for l in levels}
    h = by["heat"]
    out.append(("why heat", f"{max(h['price']):,.2f}", "3,842.89"))
    c = by["caiso-solar-noon"]
    mid = [v for i, v in enumerate(c["price"]) if "10:00" <= clock(c, i) <= "14:45"]
    out.append(("why caiso-solar-noon", f"{sum(mid) / len(mid):.2f}", "-22.13"))
    d = by["caiso-duck"]
    a = [v for i, v in enumerate(d["price"]) if "12:00" <= clock(d, i) <= "14:45"]
    b = [v for i, v in enumerate(d["price"]) if "18:00" <= clock(d, i) <= "20:45"]
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    out += [("why caiso-duck, 12:00 to 15:00", f"{ma:.2f}", "53.37"), ("why caiso-duck, 18:00 to 21:00", f"{mb:.2f}", "462.27"), ("why caiso-duck, the rise", f"{mb - ma:.2f}", "408.90")]
    return out


def headlines(by):
    """The five headline figures replicate.do recomputes, here from the same rules (heat = 2023-08-10, Normal, the
    default battery; the plays are cases.json's)."""
    heat = by["heat"]
    R = rules({"kwh": 13.5, "kw": 5, "rte": 0.9, "reserve": 0.25, "deg": 0.11}, "normal", [])
    plan = next(c for c in CASES if c["id"] == "heat|normal|perfect")["actions"]
    rule8 = next(c for c in CASES if c["id"] == "heat|normal|rule8")["actions"]
    g = glance_expected(heat)
    perfect, plain = play(heat, plan, R)["score"], play(heat, rule8, R)["score"]
    d = {x[0]: x[1] for x in day_claims(list(by.values()))}
    return [
        ("1. heat, the day at a glance: lowest, average, highest, USD/MWh", f"{g['glance_lo']:.2f}, {g['glance_avg']:.4f}, {g['glance_hi']:.2f}"),
        ("2. heat, Normal: the perfect battery's score, USD", f"{perfect:.4f}"),
        ("3. heat, Normal: the plain rule's score (8 cheapest charge, 8 dearest sell), USD", f"{plain:.4f}"),
        ("4. heat, Normal: the perfect battery's fleet of 10,000 homes, USD", f"{perfect * FLEET:.2f}"),
        ("5. caiso-duck: the rise from the 12:00 to 15:00 mean to the 18:00 to 21:00 mean, USD/MWh", d["why caiso-duck, the rise"]),
    ]


def write_stata(by):
    """stata_input.csv: one row an interval of the heat day and the duck day (slug, i, the local clock, the real price,
    the perfect plan's and the plain rule's actions on Normal), for replicate.do."""
    path = os.path.join(HERE, "stata_input.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["slug", "i", "clock", "price", "act_perfect", "act_rule8"])
        for slug in ("heat", "caiso-duck"):
            lv = by[slug]
            plan = next(c for c in CASES if c["id"] == f"{slug}|normal|perfect")["actions"]
            rule8 = next(c for c in CASES if c["id"] == f"{slug}|normal|rule8")["actions"]
            for i, p in enumerate(lv["price"]):
                w.writerow([slug, i, clock(lv, i), repr(p), plan[i], rule8[i]])
    print(f"wrote {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--write", action="store_true", help="write stata_input.csv for replicate.do")
    a = ap.parse_args()
    global CASES
    CASES = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]
    shown = {}
    for f in json.load(open(os.path.join(HERE, "page_figures.json"), encoding="utf-8"))["figures"]:
        shown.setdefault(f["case"], {})[f["key"]] = f["shown"]
    levels = json.load(open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8"))["levels"]
    by = {l["slug"]: l for l in levels}
    want = {}
    cache, plans = {}, {}
    notes = []
    for c in CASES:
        lv = by[c["level"]]
        R = rules(c["settings"], c["difficulty"], c["addons"])
        e, mine, perfect, opt = expected(c, lv, R, cache)
        want[c["id"]] = e
        lm = f"{c['level']}|{c['mode']}"
        if c["play"] == "perfect" and lm not in plans:
            plans[lm] = True
            d, plan_score, noop = day_expected(lv, R, c["actions"], opt)
            if c["difficulty"] != "easy" or R["emergency"]:
                want[f"{lm}|day"] = {k: v for k, v in d.items() if c["difficulty"] != "easy" or k.startswith(("keep", "outage"))}
            if abs(plan_score - opt) > 1e-9:
                notes.append(f"DIFF {lm}: the page's perfect plan scores {plan_score:.6f}, the optimum found here {opt:.6f}")
            if noop:
                notes.append(f"DIFF {lm}: the page's perfect plan keeps {noop} moves that move nothing")
    for lv in levels:
        want[f"{lv['slug']}|glance"] = glance_expected(lv)
    want["page|rules"] = RULES_PAGE
    n = ok = 0
    for case, figs in shown.items():
        for key, s in figs.items():
            n += 1
            w = want.get(case, {}).get(key)
            if w is None:
                print(f"DIFF {case} {key}: the page shows {s!r}; nothing here says it should")
                continue
            if isinstance(w, (int, float)) and not isinstance(w, bool):
                good, d = same(s, float(w))
            else:
                good, d = same(s, str(w))
            if good:
                ok += 1
                if a.verbose:
                    print(f"ok   {case} {key}: {s}")
            else:
                print(f"DIFF {case} {key}: the page shows {s!r}, the rules give {w!r}")
    # what the rules say the page should show and it does not
    for case, keys in want.items():
        for key in keys:
            if key not in shown.get(case, {}):
                print(f"MISSING {case} {key}: the rules give {keys[key]!r}; the page shows nothing")
                n += 1
    for line in notes:
        print(line)
    print(f"\nthe day list's figures, from each day's own prices:")
    for what, got, page in day_claims(levels):
        n += 1
        good = got == page
        ok += good
        print(f"{'ok  ' if good else 'DIFF'} {what}: {got} (the page: {page})")
    print(f"\nthe frozen prices against the tables ({a.tables}):")
    for table, good, line in tables_check(levels, a.tables, a.verbose):
        if good is None:
            print(f"not read {line}")
            continue
        n += 1
        ok += bool(good)
        print(f"{'ok  ' if good else 'DIFF'} {line}")
    print("\nthe five headline figures (replicate.do):")
    for what, v in headlines(by):
        print(f"     {what}: {v}")
    if a.write:
        write_stata(by)
    print(f"\n{ok} of {n} figures inside half the page's last shown digit (times and words equal)")
    sys.exit(0 if ok == n and not [l for l in notes if l.startswith("DIFF")] else 1)


CASES = []
if __name__ == "__main__":
    main()
