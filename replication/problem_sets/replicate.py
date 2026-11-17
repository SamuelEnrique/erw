"""Energy Research Warehouse (ERW), session 7534 (chain 304): the replication of the problem sets (/learn/problems).

Written from the method note (docs/methods/problem_sets.md, which points to the notes of the tables and pages each set
reads) and each question's own stated rule, not from the page's code (site/lib/problems.ts). Standard library only.
Two parts:

1. The live sets. Every figure each set's page shows (the worked example and the five questions: every answer, every
   step of the worked solution, the one-line computation, the day), recomputed from the rows the page was given
   (live_rows.csv, every read the five sets made of the live set, kept by site/scripts/problem-sets-figures.mjs with its
   time in live_reads.json, the hourly network snapshot with them) and the committed files the questions name
   (site/data/bill_rules.json, site/data/severance_rules.json, site/data/merchant_snapshot.json, and the game's battery
   as docs/methods/battery_game.md states it). Each figure is compared, by its check key, with the figure the page
   shows (page_figures.json, written by the same script with the pages drawn to HTML). A figure passes when ours is
   within half the page's last shown digit (0.005 for a figure shown to two decimals, 0.5 for a whole number). And every
   answer the page gives in words (a day, a month, an hour, a hub, a neighbor, "the same day" or not) is recomputed and
   looked for in the page's words.
2. The dated edition (site/data/problem_editions/<date>.json, the teacher's copy): every figure of every answer and
   worked solution, recomputed from the rows the question's own download holds (site/public/problems/<date>/<set>-<id>.csv)
   and the same committed files. A figure that its download gives only as its own value ("computed") and that cannot
   be recomputed from a committed file (the network's hour of 15 October is not kept) is counted and named, not passed.

    python replication/problem_sets/replicate.py [--detail]

Exit 0 when every figure passes or is named, 1 when one does not, 2 on bad input. Every table read is public (the rows
a license holds never reach the page: lib/supabase.ts reads a held table's public rows only).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import sys
import urllib.parse
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "site", "data")
EDITIONS = os.path.join(DATA, "problem_editions")
PUBLIC = os.path.join(ROOT, "site", "public", "problems")
DAY = dt.timedelta(days=1)
CENTRAL = ZoneInfo("America/Chicago")

# The game's battery and fleet, as docs/methods/battery_game.md states them (13.5 kWh, 90 percent round trip; the
# fictional fleet of 10,000 homes, ruling 3a). The square root of the round trip each way (set D question 3's words).
BATTERY_KWH, ROUND_TRIP, FLEET_HOMES = 13.5, 0.90, 10_000
# The seller's model (docs/methods/cost_of_power.md, "The page"): Lazard's midpoints, 60 percent debt at 8 percent over
# the life; a month counts when the asset's hours (a battery's days) are at least 90 percent of the month's.
LAZARD = {"solar": (1375, 12.5, 35), "battery_4h": (1110, 22.0, 20)}
DEBT_SHARE, DEBT_RATE, NEAR = 0.6, 0.08, 0.9
NEAR_FULL_B2 = 0.95   # set B question 2: every hub holds at least 95 percent of its hours (the note, ruling 4)
HUB_NAMES = {"caiso:TH_NP15_GEN-APND": "CAISO NP15", "caiso:TH_SP15_GEN-APND": "CAISO SP15", "ercot:HB_HUBAVG": "ERCOT hub average",
             "isone:.H.INTERNAL_HUB": "ISO-NE internal hub", "miso:INDIANA.HUB": "MISO Indiana hub", "nyiso:N.Y.C.": "NYISO New York City",
             "spp:SPPNORTH_HUB": "SPP North hub"}
# Differences the script knows of and names (check key or word id: reason); each is a numbered row of
# docs/reviews/problem-sets-faults-2026-11-16.md. Empty when every figure is inside half the last shown digit.
NAMED: dict[str, str] = {}


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def tol(v: float) -> float:
    return 0.5 if float(v).is_integer() else 0.005


# ------------------------------------------------------------------ the kept reads
def load_live():
    reads = json.load(open(os.path.join(HERE, "live_reads.json"), encoding="utf-8"))
    meta = {}
    for r in reads["reads"]:
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(r["address"]).query))
        meta[r["id"]] = (q["table_name"][3:], q.get("event", "eq.")[3:])
    rows: dict[tuple, dict] = {}
    with open(os.path.join(HERE, "live_rows.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            table, event = meta[int(r["read"])]
            rows[(table, event, r["entity"], r["variable"], r["ts_utc"])] = float(r["value"])
    return reads, rows


class Rows:
    """The rows of one table (and event): (entity, variable) -> {ts text: value}."""

    def __init__(self, rows, table, event=""):
        self.d: dict[tuple, dict] = defaultdict(dict)
        for (t, e, ent, var, ts), v in rows.items():
            if t == table and e == event:
                self.d[(ent, var)][ts] = v
        self.table, self.event = table, event

    def get(self, ent, var):
        return self.d.get((ent, var), {})

    def entities(self):
        return sorted({k[0] for k in self.d})

    def key(self, ent, var, ts):
        return f"series|{self.table}|{ent}|{var}|{ts}" + (f"|{self.event}" if self.event else "")


class Out:
    def __init__(self):
        self.fig: dict[str, float] = {}
        self.words: dict[str, list[str]] = defaultdict(list)   # question id -> phrases its words must hold

    def put(self, k, v):
        self.fig[k] = v
        return (k, v)

    def calc(self, op, a, b):
        k = f"calc|{op}|{a[0].replace('|', '~')}|{b[0].replace('|', '~')}"
        v = a[1] / b[1] if op == "ratio" else a[1] - b[1] if op == "diff" else a[1] / b[1] * 100
        return self.put(k, v)


def day_of(ts: str) -> str:
    return ts[:10]


# ------------------------------------------------------------------ set A: know your grid
def set_a(rows, o: Out):
    D, G, S, C = (Rows(rows, t) for t in ("eia930_all_demand", "eia930_all_generation", "storage_daily_cycle", "carbon_intensity_daily"))
    E, CA = "eia930:ERCO", "eia930:CISO"

    def hours_on(r: Rows, ent, var, d):
        return {ts: v for ts, v in r.get(ent, var).items() if day_of(iso(parse_ts(ts))) == d}

    days = sorted({day_of(iso(parse_ts(ts))) for (e, v), m in D.d.items() for ts in m}, reverse=True)
    whole = lambda r, ent, var, d: len(hours_on(r, ent, var, d)) == 24
    # questions 1 and 2: the newest UTC day both tables hold in full, both grids, every variable asked
    d0 = next(d for d in days if all(whole(D, e, "demand_mw", d) for e in (E, CA))
              and all(whole(G, e, v, d) for e in (E, CA) for v in ("net_generation_mw", "net_generation_natural_gas_mw")))
    o.put(f"fullday|know-your-grid|{d0}", d0)
    s0 = f"{d0}T00:00:00Z"
    s1 = iso(parse_ts(s0) + DAY)
    pk = {e: o.put(f"series_max|eia930_all_demand|demand_mw|{s0}|{s1}|{e}", max(hours_on(D, e, "demand_mw", d0).values())) for e in (E, CA)}
    o.calc("ratio", pk[E], pk[CA])
    o.words["a1"] += [d0]
    sm = {(e, v): o.put(f"series_sum|eia930_all_generation|{v}|{s0}|{s1}|{e}", sum(hours_on(G, e, v, d0).values()))
          for e in (E, CA) for v in ("net_generation_mw", "net_generation_natural_gas_mw")}
    for e in (E, CA):
        o.calc("pct", sm[(e, "net_generation_natural_gas_mw")], sm[(e, "net_generation_mw")])
    # question 3: the latest day both grids' battery rows are held (ERCOT from EIA-930, CAISO's own)
    dis = {e: S.get(e, "mwh_discharged") for e in (E, "caiso:ISO")}
    both = sorted(set(map(day_of, dis[E])) & set(map(day_of, dis["caiso:ISO"])))[-1]
    ts_of = lambda m, d: next(t for t in m if day_of(t) == d)
    bE = o.put(S.key(E, "mwh_discharged", ts_of(dis[E], both)), dis[E][ts_of(dis[E], both)])
    bC = o.put(S.key("caiso:ISO", "mwh_discharged", ts_of(dis["caiso:ISO"], both)), dis["caiso:ISO"][ts_of(dis["caiso:ISO"], both)])
    o.calc("ratio", bC, bE)
    o.words["a3"] += [both]
    # question 4: carbon intensity, the latest day both are held
    ci = {e: C.get(e, "intensity_generation") for e in (E, CA)}
    cd = sorted(set(map(day_of, ci[E])) & set(map(day_of, ci[CA])))[-1]
    iE = o.put(C.key(E, "intensity_generation", ts_of(ci[E], cd)), ci[E][ts_of(ci[E], cd)])
    iC = o.put(C.key(CA, "intensity_generation", ts_of(ci[CA], cd)), ci[CA][ts_of(ci[CA], cd)])
    o.calc("diff", iE, iC)
    o.words["a4"] += [cd]
    # question 5: the newest battery day of ERCOT whose Central-time day of hourly demand is whole
    dem = {parse_ts(ts): v for ts, v in D.get(E, "demand_mw").items()}
    for d in sorted(map(day_of, dis[E]), reverse=True):
        a = dt.datetime.fromisoformat(d).replace(tzinfo=CENTRAL)
        b = (a + dt.timedelta(hours=30)).replace(hour=0, tzinfo=CENTRAL)
        b = dt.datetime(b.year, b.month, b.day, tzinfo=CENTRAL)
        want = int((b.astimezone(dt.timezone.utc) - a.astimezone(dt.timezone.utc)).total_seconds() // 3600)
        inside = {t: v for t, v in dem.items() if a <= t < b}
        if len(inside) == want:
            b5 = o.put(S.key(E, "mwh_discharged", ts_of(dis[E], d)), dis[E][ts_of(dis[E], d)])
            dd = o.put(f"series_sum|eia930_all_demand|demand_mw|{iso(a)}|{iso(b)}|{E}", sum(inside.values()))
            o.calc("pct", b5, dd)
            o.words["a5"] += [d]
            break
    # the worked example: question 1's method on the day before, when both grids' demand holds its 24 hours
    prev = day_of(iso(parse_ts(s0) - DAY))
    dx = prev if all(whole(D, e, "demand_mw", prev) for e in (E, CA)) else d0
    x0 = f"{dx}T00:00:00Z"
    x1 = iso(parse_ts(x0) + DAY)
    xp = {e: o.put(f"series_max|eia930_all_demand|demand_mw|{x0}|{x1}|{e}", max(hours_on(D, e, "demand_mw", dx).values())) for e in (E, CA)}
    o.calc("ratio", xp[E], xp[CA])
    o.words["ax"] += [dx]


# ------------------------------------------------------------------ set B: prices and your bill
def full_months(M: Rows, ent):
    h = M.get(ent, "rt_hours")
    return sorted(ts for ts, n in M.get(ent, "hours_in_month").items() if h.get(ts) == n)


def bill_totals():
    """The two default bills of /learn/bill, from the tariffs' own stated rules in site/data/bill_rules.json: PG&E by
    E-TOU-C's total rates (Sheet 2: energy at the season's peak and off-peak totals, less the baseline credit on the
    territory's baseline allowance times the days, plus the Base Services Charge of the tier times the days); Oncor by its
    fixed monthly charges, its per-kWh charges and riders, and the retailer's default energy charge."""
    b = json.load(open(os.path.join(DATA, "bill_rules.json"), encoding="utf-8"))["bills"]
    ca, x = b["CA"], b["CA"]["defaults"]
    s = ca["seasons"][x["season"]]
    allowance = ca["baseline_quantities"]["code_B"][x["territory"]][0 if x["season"] == "summer" else 1] * x["days"]
    base = min(allowance, x["kwh"])
    total_ca = (x["kwh"] * (x["peak_share"] * s["peak"] + (1 - x["peak_share"]) * s["offpeak"]) + base * ca["baseline_credit"]["rate"]
                + x["days"] * ca["base_services"]["tiers"][x["income_tier"]] + (ca["climate_credit"]["rate"] if x["climate_credit"] else 0))
    tx = b["TX"]
    kwh_tx = tx["defaults"]["kwh"]
    total_tx = (kwh_tx * tx["energy_default"]["rate"] + sum(l["rate"] for l in tx["fixed"] if l["basis"] == "per_month")
                + kwh_tx * sum(l["rate"] for l in tx["per_kwh"]))
    return {"CA": (total_ca, x["kwh"], ca["wholesale_entity"]), "TX": (total_tx, kwh_tx, tx["wholesale_entity"])}


def set_b(rows, o: Out):
    M, P = Rows(rows, "cost_of_power_monthly"), Rows(rows, "cost_of_power_hourly_profile")
    E = "ercot:HB_HUBAVG"
    full = full_months(M, E)
    m = full[-1]
    lw = o.put(M.key(E, "rt_load_weighted", m), M.get(E, "rt_load_weighted")[m])
    sm = o.put(M.key(E, "rt_simple_mean", m), M.get(E, "rt_simple_mean")[m])
    o.calc("diff", lw, sm)
    o.words["b1"] += [m[:7]]
    mx = full[-2] if len(full) > 1 else m
    xl = o.put(M.key(E, "rt_load_weighted", mx), M.get(E, "rt_load_weighted")[mx])
    xs = o.put(M.key(E, "rt_simple_mean", mx), M.get(E, "rt_simple_mean")[mx])
    o.calc("diff", xl, xs)
    o.words["bx"] += [mx[:7]]
    # question 2: every hub the rows hold, the latest month each holds at least 95 percent of its hours
    ents = M.entities()
    near = lambda e, t: t in M.get(e, "rt_hours") and t in M.get(e, "hours_in_month") and M.get(e, "rt_hours")[t] >= NEAR_FULL_B2 * M.get(e, "hours_in_month")[t]
    common = sorted(t for t in M.get(ents[0], "hours_in_month") if all(near(e, t) for e in ents))[-1]
    prem = {e: o.put(M.key(e, "rt_shape_premium", common), M.get(e, "rt_shape_premium")[common]) for e in ents}
    top = max(ents, key=lambda e: prem[e][1])
    low = min(ents, key=lambda e: prem[e][1])
    for e in ents:   # a hub short of its hours is named with them
        h, n = M.get(e, "rt_hours")[common], M.get(e, "hours_in_month")[common]
        if h < n:
            o.put(M.key(e, "rt_hours", common), h)
            o.put(M.key(e, "hours_in_month", common), n)
    o.words["b2"] += [common[:7], f"{len(ents)} hubs", f"largest {HUB_NAMES[top]}", f"smallest {HUB_NAMES[low]}"]
    # questions 3 and 4: the wholesale share of the two default bills
    for s, qid in (("CA", "b3"), ("TX", "b4")):
        total, kwh, ent = bill_totals()[s]
        fm = full_months(M, ent)
        mm = fm[-1]
        price = o.put(M.key(ent, "rt_load_weighted", mm), M.get(ent, "rt_load_weighted")[mm])
        tot = o.put(f"bill|{s}|total", total)
        wh = o.put(f"bill|{s}|wholesale|{mm}", kwh * price[1] / 1000)
        o.put(f"bill|{s}|share|{mm}", wh[1] / tot[1] * 100)
        o.words[qid] += [f"{kwh} kWh", mm[:7]]
    # question 5 and set D question 3: the profile's latest month that is complete for ERCOT's hub average
    pm = sorted({ts for (e, v), mm_ in P.d.items() if e == E for ts in mm_ if day_of(ts) in {day_of(t) for t in full}})[-1]
    cells = {v: mm_[pm] for (e, v), mm_ in P.d.items() if e == E and v.startswith("rt_mean_h") and pm in mm_}
    lo, hi = min(cells, key=cells.get), max(cells, key=cells.get)
    LO = o.put(P.key(E, lo, pm), cells[lo])
    HI = o.put(P.key(E, hi, pm), cells[hi])
    o.calc("diff", HI, LO)
    o.words["b5"] += [pm[:7], f"cheapest {lo[-2:]}:00", f"dearest {hi[-2:]}:00"]
    return pm, lo, hi, cells


# ------------------------------------------------------------------ set C: when the grid broke
def set_c(rows, o: Out):
    def ev(event, ent, var):
        r = Rows(rows, "event_window_daily", event)
        return r, r.get(ent, var)

    r, uri = ev("uri_2021", "ercot:HB_HUBAVG", "rt_max")
    u21 = max((t for t in uri if t.startswith("2021")), key=uri.get)
    ub = max((t for t in uri if not t.startswith("2021")), key=uri.get)
    U = o.put(r.key("ercot:HB_HUBAVG", "rt_max", u21), uri[u21])
    UB = o.put(r.key("ercot:HB_HUBAVG", "rt_max", ub), uri[ub])
    o.calc("ratio", U, UB)
    o.words["c1"] += [day_of(u21), day_of(ub)]
    r, cai = ev("caiso_heat_2020", "eia930:CISO", "demand_max_pct_vs_baseline")
    chi = max(cai, key=cai.get)
    c14 = next(t for t in cai if day_of(t) == "2020-08-14")
    o.calc("diff", o.put(r.key("eia930:CISO", "demand_max_pct_vs_baseline", chi), cai[chi]), o.put(r.key("eia930:CISO", "demand_max_pct_vs_baseline", c14), cai[c14]))
    o.words["c2"] += [day_of(chi)]
    r, pj = ev("elliott_2022", "eia930:PJM", "demand_max_mw")
    ptop = max((t for t in pj if t >= "2022-12-19"), key=pj.get)
    o.put(r.key("eia930:PJM", "demand_max_mw", ptop), pj[ptop])
    _, pp = ev("elliott_2022", "eia930:PJM", "demand_max_pct_vs_baseline")
    o.put(r.key("eia930:PJM", "demand_max_pct_vs_baseline", ptop), pp[ptop])
    o.words["c3"] += [day_of(ptop)]
    r, e23 = ev("ercot_heat_2023", "ercot:HB_HUBAVG", "rt_max")
    etop = max((t for t in e23 if t >= "2023-08-01"), key=e23.get)
    U2 = o.put(r.key("ercot:HB_HUBAVG", "rt_max", etop), e23[etop])
    _, ed = ev("ercot_heat_2023", "eia930:ERCO", "demand_max_mw")
    edem = max((t for t in ed if t >= "2023-08-01"), key=ed.get)
    o.put(r.key("eia930:ERCO", "demand_max_mw", edem), ed[edem])
    o.words["c4"] += [f"Highest price {day_of(etop)}", f"highest demand {day_of(edem)}", "the same day." if day_of(etop) == day_of(edem) else "different days."]
    o.calc("ratio", U, U2)
    r, ud = ev("uri_2021", "eia930:ERCO", "demand_max_mw")
    h21 = max((t for t in ud if t.startswith("2021")), key=ud.get)
    hb = max((t for t in ud if not t.startswith("2021")), key=ud.get)
    o.calc("ratio", o.put(r.key("eia930:ERCO", "demand_max_mw", h21), ud[h21]), o.put(r.key("eia930:ERCO", "demand_max_mw", hb), ud[hb]))
    o.words["cx"] += [day_of(h21), day_of(hb)]


# ------------------------------------------------------------------ set D: storage and taxes
def sev_rules():
    return json.load(open(os.path.join(DATA, "severance_rules.json"), encoding="utf-8"))


def tax(rules, state, product, volume, price):
    """The base production tax (no fee) by the rules file's rates: Texas oil 4.6 percent of value or 4.6 cents a barrel,
    whichever is more; Louisiana oil 12.5 percent (a well completed before July 2025); New Mexico oil its three
    percent-of-value taxes (severance, emergency school, conservation; the district ad valorem at its default, none);
    Texas gas 7.5 percent of value."""
    p = rules["states"][state]["products"][product]
    value = volume * price
    total = 0.0
    for b in p["base"]:
        rate = b["rate"]
        if rate == "variant":
            rate = next(v["rate"] for v in p["variants"] if v["id"] == "la_oil_pre2025")
        if not isinstance(rate, (int, float)):
            continue   # New Mexico's district ad valorem: the question takes none
        t = value * rate
        if "min_per_unit" in b:
            t = max(t, volume * b["min_per_unit"])
        total += t
    return total


def set_d(rows, o: Out, profile):
    S, F = Rows(rows, "storage_daily_cycle"), Rows(rows, "eia_fuel_spot_prices")
    E = "eia930:ERCO"
    dis, chg = S.get(E, "mwh_discharged"), S.get(E, "mwh_charged")
    days = sorted(map(day_of, dis))
    last7 = days[-7:]
    s0, s1 = f"{last7[0]}T00:00:00Z", iso(parse_ts(f"{last7[-1]}T00:00:00Z") + DAY)
    inr = lambda ts: parse_ts(s0) <= parse_ts(ts) < parse_ts(s1)
    out = o.put(f"series_sum|storage_daily_cycle|mwh_discharged|{s0}|{s1}|{E}", sum(v for t, v in dis.items() if inr(t)))
    inn = o.put(f"series_sum|storage_daily_cycle|mwh_charged|{s0}|{s1}|{E}", sum(v for t, v in chg.items() if inr(t)))
    o.calc("pct", out, inn)
    o.put("battery|round_trip_pct", ROUND_TRIP * 100)
    o.words["d1"] += [f"({last7[0]} to {last7[-1]})"]
    # question 2: the latest day holding both peak hours
    pc, pd = S.get(E, "peak_charge_hour"), S.get(E, "peak_discharge_hour")
    dl = max(set(map(day_of, pc)) & set(map(day_of, pd)))
    t = next(x for x in pc if day_of(x) == dl)
    o.calc("diff", o.put(S.key(E, "peak_discharge_hour", t), pd[t]), o.put(S.key(E, "peak_charge_hour", t), pc[t]))
    o.words["d2"] += [dl]
    # question 3: one cycle of the game's battery at the profile month's cheapest and dearest hours
    pm, lo, hi, cells = profile
    each = math.sqrt(ROUND_TRIP)
    bought, delivered = BATTERY_KWH / each, BATTERY_KWH * each
    o.put("battery|bought_kwh", bought)
    o.put("battery|delivered_kwh", delivered)
    cash = (delivered * cells[hi] - bought * cells[lo]) / 1000
    key = f"cost_of_power_hourly_profile|ercot:HB_HUBAVG|{pm}|{lo}|{hi}"
    o.put(f"battery|cycle|{key}", cash)
    o.put(f"battery|cycle_fleet|{key}", cash * FLEET_HOMES)
    o.put(f"series|cost_of_power_hourly_profile|ercot:HB_HUBAVG|{lo}|{pm}", cells[lo])
    o.put(f"series|cost_of_power_hourly_profile|ercot:HB_HUBAVG|{hi}|{pm}", cells[hi])
    o.words["d3"] += [pm[:7]]
    # question 4: the latest complete month of WTI Cushing (a later month has begun), three states' oil tax
    wti = F.get("eia:wti_cushing", "spot_price")
    held = sorted({t[:7] for t in wti})
    mo = held[-2]
    mean = lambda m_, ent: [v for t_, v in F.get(ent, "spot_price").items() if t_.startswith(m_)]
    w = mean(mo, "eia:wti_cushing")
    W = o.put(f"spotmean|eia:wti_cushing|{mo}", sum(w) / len(w))
    rules = sev_rules()
    txo = o.put(f"sev|TX|oil|1000|{mo}|base", tax(rules, "TX", "oil", 1000, W[1]))
    lao = o.put(f"sev|LA|oil|1000|{mo}|base", tax(rules, "LA", "oil", 1000, W[1]))
    o.put(f"sev|NM|oil|1000|{mo}|base", tax(rules, "NM", "oil", 1000, W[1]))
    o.calc("ratio", lao, txo)
    o.words["d4"] += [mo]
    # question 5: the latest held month at or before it with a certified price; Henry Hub's mean; the credit's tier
    lp = next(x for x in rules["states"]["TX"]["products"]["gas"]["options"] if x["id"] == "tx_lp_gas")
    cert = {p["period"]: p["price"] for p in lp["certified"]["prices"]}
    gm = max(m_ for m_ in held if m_ <= mo and m_ in cert)
    hh = mean(gm, "eia:henry_hub")
    H = o.put(f"spotmean|eia:henry_hub|{gm}", sum(hh) / len(hh))
    o.put(f"sevcert|tx_lp_gas|{gm}", cert[gm])
    pct = next(b["pct"] for b in lp["bounds"] if b["above"] is None or cert[gm] > b["above"])
    o.put(f"sevcredit|tx_lp_gas|{gm}", pct)
    g0 = tax(rules, "TX", "gas", 2400, H[1])
    o.put(f"sev|TX|gas|2400|{gm}|base", g0)
    o.put(f"sev|TX|gas|2400|{gm}|tx_lp_gas", g0 * (1 - pct / 100))
    o.words["d5"] += [gm]
    # the worked example: one day, the latest holding both the discharge and the charge
    dx = max(set(map(day_of, dis)) & set(map(day_of, chg)))
    t = next(x for x in dis if day_of(x) == dx)
    o.calc("pct", o.put(S.key(E, "mwh_discharged", t), dis[t]), o.put(S.key(E, "mwh_charged", t), chg[t]))
    o.words["dx"] += [dx]


# ------------------------------------------------------------------ set E: networks and money
def crf(rate, n):
    return rate / (1 - (1 + rate) ** -n)


def set_e(network, o: Out):
    hours = network["hours"]
    ties = lambda h: [(l["b"] if l["a"] == "ERCO" else l["a"], (1 if l["a"] == "ERCO" else -1) * l["mw"][h])
                      for l in network["links"] if "ERCO" in (l["a"], l["b"]) and l["mw"][h] is not None]
    hi = max(i for i in range(len(hours)) if ties(i))
    H = hours[hi]
    tt = sorted(ties(hi), key=lambda x: (-abs(x[1]), x[0]))
    name = {n["id"]: n["name"] for n in network["nodes"]}
    o.put(f"net|ties|ERCO|{H}", len(tt))
    o.put(f"net|maxflow|ERCO|{H}", abs(tt[0][1]))
    o.words["e1"] += [f"{'out to' if tt[0][1] > 0 else 'in from'} {name.get(tt[0][0], tt[0][0])}", H[:13].replace("T", " ") + ":00 UTC"]
    net = defaultdict(float)
    for l in network["links"]:
        v = l["mw"][hi]
        if v is None:
            continue
        net[l["a"]] += v
        net[l["b"]] -= v
    order = sorted(net.items(), key=lambda x: (-x[1], x[0]))
    o.put(f"net|topexport|{H}", order[0][1])
    o.words["e2"] += [f"({order[0][0]})", f"({order[1][0]}), about {round(order[1][1]):,} MW"]
    snap = json.load(open(os.path.join(DATA, "merchant_snapshot.json"), encoding="utf-8"))["isos"]["ercot"]
    months = snap["months"]
    days_in = lambda m: (dt.date(int(m[:4]) + (m[5:] == "12"), int(m[5:]) % 12 + 1, 1) - dt.date(int(m[:4]), int(m[5:]), 1)).days

    def held(asset):
        out = []
        for m, r in sorted(months.items()):
            a = r.get(asset)
            if not a or a.get("hours") is None:
                continue
            need = r["him"] if not asset.startswith("battery") else r["him"] / 24
            if a["hours"] >= NEAR * need:
                out.append(m)
        return out

    capex, fom, life = LAZARD["solar"]
    ds_solar = round(capex * 1000 * 100 * DEBT_SHARE * crf(DEBT_RATE, life))
    sol = f"mr|iso=ercot&asset=solar&mw=100&mwh=0&ds={ds_solar}&hr=10.725&vom=4.25&fom={fom:g}"
    hs = held("solar")
    for m in hs[-2:]:
        a = months[m]["solar"]
        cap = a["sales_per_mw"] / a["energy_per_mw"]
        o.put(f"{sol}|capture:{m}", cap)
        o.put(f"{sol}|flat:{m}", a["flat_price"])
        o.put(f"{sol}|rate:{m}", cap / a["flat_price"] * 100)
    o.words["e3"] += [hs[-1]]
    o.words["ex"] += [hs[-2]]
    capex, fom, life = LAZARD["battery_4h"]
    ds = round(capex * 1000 * 100 * DEBT_SHARE * crf(DEBT_RATE, life))
    bat = f"mr|iso=ercot&asset=battery&mw=100&mwh=400&ds={ds}&hr=10.725&vom=4.25&fom={fom:g}"
    hb = held("battery_4h")
    dscr = [(months[m]["battery_4h"]["revenue_per_mw"] * 100 - fom * 1000 * 100 / 12) / (ds / 12) for m in hb]
    n = o.put(f"{bat}|n", len(hb))
    u = o.put(f"{bat}|under1", sum(1 for x in dscr if x < 1))
    o.calc("diff", n, u)
    o.words["e4"] += [f"{ds:,} USD", f"{hb[0]} to {hb[-1]}"]
    st = snap["stress"]["uri_2021"]
    win = [d for d in st["days"] if d["window"]]
    base = [d for d in st["days"] if not d["window"]]
    mrs = f"mrs|{sol[3:]}|uri_2021"
    total = o.put(f"{sol}|stress_total:uri_2021", sum(d["solar"] for d in win) * 100)
    bmean = sum(d["solar"] for d in base) / len(base) * 100
    o.put(f"{sol}|stress_week:uri_2021", bmean * 7)
    o.put(f"{mrs}|days", len(win))
    o.put(f"{mrs}|base_mean", bmean)
    normal = o.put(f"{mrs}|base_window", bmean * len(win))
    o.calc("ratio", total, normal)
    o.words["e5"] += [f"the {len(win)} days from {st['start']} to {st['end']}"]


# ------------------------------------------------------------------ compare
def compare_live(page, o: Out, detail):
    passed = failed = named = 0
    lines, fails = [], []
    for slug, s in page["sets"].items():
        seen = set()
        for q in s["questions"]:
            text = " | ".join([q["q"], q["answer"], q["line"] or "", *q["steps"], q["words"]])
            for f in q["figures"]:
                k = f["k"]
                if (q["id"], k) in seen:
                    continue
                seen.add((q["id"], k))
                if f["where"] == "day":
                    ok = o.fig.get(k) == f["shown"]
                    ours, theirs, diff = o.fig.get(k), f["shown"], ""
                else:
                    ours, theirs = o.fig.get(k), f["v"]
                    ok = ours is not None and abs(ours - theirs) <= tol(theirs) + 1e-9
                    diff = "" if ours is None else f"{ours - theirs:+.6g}"
                tag = "pass" if ok else ("named" if k in NAMED else "FAIL")
                passed += tag == "pass"
                named += tag == "named"
                failed += tag == "FAIL"
                lines.append(f"{slug},{q['id']},figure,{k},{f['shown']},{'' if ours is None else repr(ours)},{diff},{tag}")
                if tag == "FAIL":
                    fails.append(f"  {slug} {q['id']} {k}: page {theirs}, ours {ours}")
            for w in o.words.get(q["id"], []):
                ok = w in text
                tag = "pass" if ok else ("named" if f"{q['id']}:{w}" in NAMED else "FAIL")
                passed += tag == "pass"
                named += tag == "named"
                failed += tag == "FAIL"
                lines.append(f"{slug},{q['id']},words,{w},,,,{tag}")
                if tag == "FAIL":
                    fails.append(f"  {slug} {q['id']} words: {w!r} not in the page's words")
    return passed, failed, named, lines, fails


def edition_rows(date, slug, qid):
    path = os.path.join(PUBLIC, date, f"{slug}-{qid}.csv")
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def edition_value(k, rows, figs, rules, snap_ercot, bills):
    """One figure of an edition from its question's download and the committed files; None when it cannot be."""
    p = k.split("|")
    num = lambda r: float(r["value"])
    if p[0] == "series":
        t, ent, var, ts = p[1:5]
        ev = p[5] if len(p) > 5 else ""
        r = [r for r in rows if r["source"] == t and r["entity"] == ent and r["variable"] == var and r["ts_utc"] == ts and r["event"] == ev]
        return num(r[0]) if r else None
    if p[0] in ("series_max", "series_sum"):
        t, var, a, b, ent = p[1:6]
        vals = [num(r) for r in rows if r["source"] == t and r["entity"] == ent and r["variable"] == var and parse_ts(a) <= parse_ts(r["ts_utc"]) < parse_ts(b)]
        if not vals:
            return None
        return max(vals) if p[0] == "series_max" else sum(vals)
    if p[0] == "spotmean":
        vals = [num(r) for r in rows if r["entity"] == p[1] and r["ts_utc"].startswith(p[2])]
        return sum(vals) / len(vals) if vals else None
    if p[0] == "calc":
        a, b = (edition_value(x.replace("~", "|"), rows, figs, rules, snap_ercot, bills) for x in p[2:4])
        if a is None or b is None:
            return None
        return a / b if p[1] == "ratio" else a - b if p[1] == "diff" else a / b * 100
    if p[0] == "battery":
        each = math.sqrt(ROUND_TRIP)
        if p[1] == "round_trip_pct":
            return ROUND_TRIP * 100
        if p[1] == "bought_kwh":
            return BATTERY_KWH / each
        if p[1] == "delivered_kwh":
            return BATTERY_KWH * each
        if p[1] in ("cycle", "cycle_fleet"):
            t, ent, ts, lo, hi = p[2:7]
            v = {r["variable"]: num(r) for r in rows if r["source"] == t and r["ts_utc"] == ts}
            if lo not in v or hi not in v:
                return None
            cash = (BATTERY_KWH * each * v[hi] - BATTERY_KWH / each * v[lo]) / 1000
            return cash * (FLEET_HOMES if p[1] == "cycle_fleet" else 1)
    if p[0] == "bill":
        total, kwh, ent = bills[p[1]]
        if p[2] == "total":
            return total
        price = [num(r) for r in rows if r["source"] == "cost_of_power_monthly" and r["entity"] == ent and r["variable"] == "rt_load_weighted" and r["ts_utc"] == p[3]]
        if not price:
            return None
        wh = kwh * price[0] / 1000
        return wh if p[2] == "wholesale" else wh / total * 100
    if p[0] == "sev":
        state, product, vol, month, opt = p[1:6]
        ent = "eia:wti_cushing" if product == "oil" else "eia:henry_hub"
        vals = [num(r) for r in rows if r["entity"] == ent and r["ts_utc"].startswith(month)]
        if not vals:
            return None
        base = tax(rules, state, product, float(vol), sum(vals) / len(vals))
        if opt == "base":
            return base
        pct = edition_value(f"sevcredit|{opt}|{month}", rows, figs, rules, snap_ercot, bills)
        return base * (1 - pct / 100)
    if p[0] in ("sevcert", "sevcredit"):
        lp = next(x for x in rules["states"]["TX"]["products"]["gas"]["options"] if x["id"] == p[1])
        cert = {x["period"]: x["price"] for x in lp["certified"]["prices"]}.get(p[2])
        if cert is None:
            return None
        return cert if p[0] == "sevcert" else next(b["pct"] for b in lp["bounds"] if b["above"] is None or cert > b["above"])
    return None   # mr|, mrs| (recomputed in part 1's way below), net| (the hour is not kept)


def compare_edition(o_template, detail):
    passed = failed = named = 0
    lines, fails = [], []
    rules = sev_rules()
    bills = bill_totals()
    for date in json.load(open(os.path.join(EDITIONS, "index.json"), encoding="utf-8"))["editions"]:
        e = json.load(open(os.path.join(EDITIONS, f"{date}.json"), encoding="utf-8"))
        for s in e["sets"]:
            for q in s["questions"]:
                rows = edition_rows(date, s["slug"], q["id"])
                seen = set()
                for parts in [q["answer"], *q["steps"]]:
                    for f in parts:
                        if isinstance(f, str) or f["k"] in seen:
                            continue
                        seen.add(f["k"])
                        k = f["k"]
                        ours = edition_value(k, rows, None, rules, None, bills)
                        if ours is None and k in o_template.fig:
                            ours = o_template.fig[k]     # a seller's-model figure: the committed snapshot, as part 1
                        ok = ours is not None and abs(ours - f["v"]) <= tol(f["v"]) + 1e-9
                        why = NAMED.get(f"edition:{k.split('|')[0]}")
                        tag = "pass" if ok else ("named" if why else "FAIL")
                        passed += tag == "pass"
                        named += tag == "named"
                        failed += tag == "FAIL"
                        lines.append(f"edition {date},{s['slug']}:{q['id']},figure,{k},{f['v']},{'' if ours is None else repr(ours)},,{tag}")
                        if tag == "FAIL":
                            fails.append(f"  edition {date} {s['slug']} {q['id']} {k}: edition {f['v']}, ours {ours}")
    return passed, failed, named, lines, fails


NAMED["edition:net"] = ("faults row 9: the network's hour of the edition (2026-10-13T03:00Z) is not kept, and the question's download "
                        "holds the answer itself, not the tie rows, so the figure cannot be recomputed from the edition")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", action="store_true", help="print every figure")
    ap.add_argument("--write", action="store_true", help="write replication_rows.csv beside this file")
    a = ap.parse_args(argv)
    try:
        reads, rows = load_live()
        page = json.load(open(os.path.join(HERE, "page_figures.json"), encoding="utf-8"))
    except (OSError, ValueError, KeyError) as e:
        print(f"bad input: {e}")
        return 2
    o = Out()
    set_a(rows, o)
    profile = set_b(rows, o)
    set_c(rows, o)
    set_d(rows, o, profile)
    set_e(reads["network"], o)
    p1, f1, n1, l1, x1 = compare_live(page, o, a.detail)
    # the edition's seller's-model figures are the committed snapshot's, as in part 1 (set E of 15 October asked the same months)
    oe = Out()
    set_e(reads["network"], oe)
    p2, f2, n2, l2, x2 = compare_edition(oe, a.detail)
    print(f"Problem sets, live (read {reads['now']}): {p1 + f1 + n1} checks (figures by check key, and answers in words): {p1} pass, {n1} named, {f1} differ")
    print(f"Problem sets, the dated edition: {p2 + f2 + n2} figures: {p2} pass, {n2} named, {f2} differ")
    for line in x1 + x2:
        print(line)
    if a.detail:
        for line in l1 + l2:
            print(line)
    if a.write:
        with open(os.path.join(HERE, "replication_rows.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# The replication of the problem sets, every check, by replication/problem_sets/replicate.py on the reads of {reads['now']}.\n")
            f.write("part,question,kind,key_or_words,page_shows,ours,difference,result\n")
            for line in l1 + l2:
                f.write(line + "\n")
    names = [k for k in NAMED if any(k in line for line in l1 + l2) or k.startswith("edition:")]
    for k in names:
        print(f"named: {k}: {NAMED[k]}")
    return 1 if f1 + f2 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
