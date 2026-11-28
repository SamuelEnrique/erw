#!/usr/bin/env python3
"""ERW, where the next gigawatts can go (the All grids tab's regions section): an independent replication of the
files site/data/siting/regions/ (session 11200, chain 760, part B's done line).

Written from docs/methods/siting_regions.md and the tables alone, not from warehouse/derived/siting_regions.py.
Standard library only. It reads the warehouse's tables (warehouse/output, or --tables DIR; on Redivis the same tables)
and the files, and recomputes, for every place the index lists:

  the places      every authority of at least 5,000 MW peak in the period is listed, and no other
  tightness       peak demand of the period and of the 12 months before, its growth, the peak hour (a region: its
                  members' sum, members reporting 90 percent of hours, an hour kept when every counted member has one)
  price           at every hub shown: the mean, the 95th percentile (linear between ranks), hours above USD 100, below
                  zero, and hours held, each market, an hour being the mean of its intervals
  congestion      each hub's share of its price that was congestion (hour-weighted)
  queue           active megawatts and requests, the withdrawn share of requests entered 2000 to 2020 that ended
  mix_carbon      each fuel's share of net generation; the mean carbon intensity
  imports         net imports as a share of demand, over the period and its 100 highest-demand hours
  spare           curtailed wind and solar megawatt-hours
  forecast        the operator's and the ERW forecast's mean absolute percentage error, last 730 days
  datacenters     facilities and projects counted, megawatts stated summed (operators: by the table's grid)

Prints N of N and each difference. Exit 0 when all agree, 1 when one does not, 2 when the inputs cannot be read.

    python replication/siting_regions/replicate.py [--tables DIR] [--site DIR]
"""
import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(10 ** 9)

OPS = {"op-caiso": ("caiso", "CISO"), "op-ercot": ("ercot", "ERCO"), "op-spp": ("spp", "SWPP"),
       "op-miso": ("miso", "MISO"), "op-pjm": ("pjm", "PJM"), "op-nyiso": ("nyiso", "NYIS"),
       "op-isone": ("isone", "ISNE")}
LBNL_REGION = {"caiso": "CAISO", "ercot": "ERCOT", "spp": "SPP", "miso": "MISO", "pjm": "PJM", "nyiso": "NYISO",
               "isone": "ISO-NE"}
GRID_NAME = LBNL_REGION
CURTAIL = {"caiso": "caiso:ISO", "spp": "spp:SPP"}


def rows(tables, name, cols):
    """Yield dicts of the named columns of a table, its '#' header lines skipped."""
    path = os.path.join(tables, name + ".csv")
    with open(path, encoding="utf-8", newline="") as fh:
        lines = (ln for ln in fh if not ln.startswith("#"))
        rd = csv.reader(lines)
        head = next(rd)
        ix = [head.index(c) for c in cols]
        for r in rd:
            yield [r[i] for i in ix]


def f(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def quantile(vals, q):
    s = sorted(vals)
    if not s:
        return None
    pos = (len(s) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


class Check:
    def __init__(self):
        self.n, self.bad = 0, []

    def eq(self, what, got, want, tol):
        self.n += 1
        if got is None and want is None:
            return
        if got is None or want is None or abs(got - want) > tol:
            self.bad.append(f"{what}: file {got}, replication {want}")


def period(built):
    d = date.fromisoformat(built[:10]).replace(day=1)
    start = d.replace(year=d.year - 1)
    return start.replace(year=start.year - 1).isoformat(), start.isoformat(), d.isoformat()


def screened(series):
    """docs/methods/impossible_hours.md: an hour of demand is used when held, above zero, within 25 percent of the median
    of the four hours around it in the series (two before, two after, those held and above zero), and within 1/3 to 3
    times the median of the hours passing those tests. series: {ts: v}; returns the hours used."""
    ts = sorted(series)
    vals = [series[t] if series[t] is not None and series[t] > 0 else None for t in ts]
    kept = []
    for i, v in enumerate(vals):
        if v is None:
            kept.append(None)
            continue
        around = [vals[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < len(vals) and vals[j] is not None]
        if around:
            s = sorted(around)
            n = len(s)
            med = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
            if abs(v - med) > 0.25 * med:
                kept.append(None)
                continue
        kept.append(v)
    ok = sorted(v for v in kept if v is not None)
    if not ok:
        return {}
    n = len(ok)
    med = ok[n // 2] if n % 2 else (ok[n // 2 - 1] + ok[n // 2]) / 2
    return {t: v for t, v in zip(ts, kept) if v is not None and med / 3 <= v <= 3 * med}


def members_sum(series, members):
    """series: ba -> {ts: v}. The method note's region sum."""
    hours = set()
    for b in members:
        hours |= set(series.get(b, {}))
    counted = [b for b in members if series.get(b) and len(series[b]) >= 0.9 * len(hours)]
    out = {}
    for ts in hours:
        vals = [series[b].get(ts) for b in counted]
        if counted and all(v is not None for v in vals):
            out[ts] = sum(vals)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site", "data"))
    ap.add_argument("--files", help="the folder of the regions files (default: SITE/siting/regions)")
    a = ap.parse_args()
    try:
        fdir = a.files or os.path.join(a.site, "siting", "regions")
        idx = json.load(open(os.path.join(fdir, "index.json"), encoding="utf-8"))
        places = {p["id"]: p for p in idx["places"]}
        files = {pid: json.load(open(os.path.join(fdir, p["file"]), encoding="utf-8"))
                 for pid, p in places.items()}
        grid_index = json.load(open(os.path.join(a.site, "regions", "index.json"), encoding="utf-8"))
    except (OSError, ValueError, KeyError) as e:
        print(f"cannot read the files: {e}")
        return 2
    if idx.get("example"):
        print("the files are the contract's examples: nothing to replicate")
        return 2
    p0, p1, p2 = period(idx["built"])
    C = Check()
    bas = {b["code"]: b for b in grid_index["bas"]}

    # demand and total interchange, two years
    dem = defaultdict(dict)
    for e, var, ts, v in rows(a.tables, "eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"]):
        if var == "demand_mw" and p0 <= ts < p2:
            dem[e.replace("eia930:", "")][ts] = f(v)   # a blank kept as None: it is a place in the row order
    dem = defaultdict(dict, {b: screened(s) for b, s in dem.items()})
    ti = defaultdict(dict)
    for e, var, ts, v in rows(a.tables, "eia930_ba_supply_hourly", ["entity", "variable", "ts_utc", "value"]):
        if var == "total_interchange_mw" and p1 <= ts < p2 and f(v) is not None:
            ti[e.replace("eia930:", "")][ts] = f(v)

    # the places: every other active US authority of at least 5,000 MW
    want = set()
    opbas = {ba for _o, ba in OPS.values()}
    for code, b in bas.items():
        if b.get("us") and b.get("active") and not b.get("generation_only") and code not in opbas:
            cur = [v for ts, v in dem.get(code, {}).items() if p1 <= ts]
            if cur and max(cur) >= 5000:
                want.add("ba-" + code.lower())
    got = {pid for pid, p in places.items() if p["kind"] == "ba"}
    C.n += 1
    if want != got:
        C.bad.append(f"the authorities listed: missing {sorted(want - got)}, extra {sorted(got - want)}")

    def series_of(p, src, lo, hi):
        if p["kind"] == "region":
            full = members_sum({b: src.get(b, {}) for b in p["members"]}, p["members"])
        else:
            full = src.get(p["members"][0], {})
        return {ts: v for ts, v in full.items() if lo <= ts < hi}

    for pid, p in places.items():
        t = files[pid]["sections"]["tightness"]
        cur = series_of(p, dem, p1, p2)
        pri = series_of(p, dem, p0, p1)
        pk = max(cur.values()) if cur else None
        pp = max(pri.values()) if pri else None
        C.eq(f"{pid} peak_mw", t["peak_mw"]["v"], round(pk) if pk is not None else None, 0.5)
        C.eq(f"{pid} peak_prior_mw", t["peak_prior_mw"]["v"], round(pp) if pp is not None else None, 0.5)
        g = (pk / pp - 1) * 100 if pk and pp else None
        C.eq(f"{pid} peak_growth_pct", t["peak_growth_pct"]["v"], g, 0.051)
        # imports
        im = files[pid]["sections"]["imports"]
        d = cur
        tt = series_of(p, ti, p1, p2)
        both = [(d[ts], tt[ts], ts) for ts in d if ts in tt]
        if both:
            share = -sum(x[1] for x in both) / sum(x[0] for x in both) * 100
            top = sorted(both, key=lambda x: (-x[0], x[2]))[:100]
            sp = -sum(x[1] for x in top) / sum(x[0] for x in top) * 100
        else:
            share = sp = None
        C.eq(f"{pid} net_import_share_pct", im["net_import_share_pct"]["v"], share, 0.051)
        C.eq(f"{pid} net_import_share_peak_pct", im["net_import_share_peak_pct"]["v"], sp, 0.051)

    # prices at every hub shown
    hub_hours = defaultdict(list)     # (entity, market, hour) -> values
    want_hubs = {(h["hub_id"], h["market"]) for fdoc in files.values() for h in fdoc["sections"]["price"]["hubs"]
                 if h.get("hub_id") and h.get("hours") and h["hours"]["v"]}
    ents = {e for e, _m in want_hubs}
    for e, var, ts, v in rows(a.tables, "ercot_all_hub_prices_history", ["entity", "variable", "ts_utc", "value"]):
        if e in ents and p1 <= ts < p2 and f(v) is not None:
            hub_hours[(e, "day-ahead" if var == "spp_dam" else "real-time", ts[:13])].append(f(v))
    for e, mk, ts, v in rows(a.tables, "iso_hub_prices_history", ["entity", "market", "ts_utc", "value"]):
        if e in ents and p1 <= ts < p2 and f(v) is not None:
            hub_hours[(e, "day-ahead" if mk.endswith("dam") else "real-time", ts[:13])].append(f(v))
    for t, mk in (("iso_dam_hub_prices", "day-ahead"), ("iso_rtm_hub_prices", "real-time")):
        for e, ts, v in rows(a.tables, t, ["entity", "ts_utc", "value"]):
            if e in ents and p1 <= ts < p2 and f(v) is not None and not e.startswith("ercot:"):
                hub_hours[(e, mk, ts[:13])].append(f(v))
    hourly = defaultdict(list)
    for (e, mk, _h), vals in hub_hours.items():
        hourly[(e, mk)].append(round(sum(vals) / len(vals), 6))
    for pid, fdoc in files.items():
        for h in fdoc["sections"]["price"]["hubs"]:
            if not h.get("hub_id") or not h.get("hours") or h["hours"]["v"] is None:
                continue
            vals = hourly.get((h["hub_id"], h["market"]), [])
            tag = f"{pid} {h['hub_id']} {h['market']}"
            C.eq(tag + " hours", h["hours"]["v"], len(vals), 0)
            if h["mean"]["held"]:
                continue
            C.eq(tag + " mean", h["mean"]["v"], sum(vals) / len(vals), 0.006)
            C.eq(tag + " p95", h["p95"]["v"], quantile(vals, 0.95), 0.006)
            C.eq(tag + " hours_over_100", h["hours_over_100"]["v"], sum(1 for v in vals if v > 100), 0)
            C.eq(tag + " hours_below_0", h["hours_below_0"]["v"], sum(1 for v in vals if v < 0), 0)

    # congestion share at each hub shown
    cm = defaultdict(lambda: defaultdict(dict))
    for e, var, ts, v in rows(a.tables, "price_congestion_monthly", ["entity", "variable", "ts_utc", "value"]):
        if p1 <= ts < p2:
            cm[e][ts][var] = f(v)
    for pid, fdoc in files.items():
        for h in fdoc["sections"]["congestion"]["hubs"]:
            if h["congestion_share_pct"]["held"]:
                continue
            months = cm[h["hub_id"]].values()
            hrs = sum(m.get("hours_held") or 0 for m in months)
            lmp = sum((m.get("lmp_mean") or 0) * (m.get("hours_held") or 0) for m in months) / hrs
            con = sum((m.get("congestion_mean") or 0) * (m.get("hours_held") or 0) for m in months) / hrs
            C.eq(f"{pid} {h['hub_id']} congestion_share_pct", h["congestion_share_pct"]["v"], con / lmp * 100, 0.051)

    # queue, operators only (Berkeley Lab's region of the same name)
    q = list(rows(a.tables, "lbnl_interconnection_queue", ["region", "q_status", "q_year", "capacity_mw"]))
    for pid, (op, _ba) in OPS.items():
        s = files[pid]["sections"]["queue"]
        mine = [r for r in q if r[0] == LBNL_REGION[op]]
        act = [f(r[3]) or 0 for r in mine if r[1] == "active"]
        C.eq(f"{pid} active_mw", s["active_mw"]["v"], round(sum(act)), 0.5)
        C.eq(f"{pid} active_projects", s["active_projects"]["v"], len(act), 0)
        ended = [r for r in mine if r[1] in ("withdrawn", "operational") and f(r[2]) and 2000 <= f(r[2]) <= 2020]
        tot = sum(f(r[3]) or 0 for r in ended)
        wd = sum(f(r[3]) or 0 for r in ended if r[1] == "withdrawn")
        C.eq(f"{pid} withdrawn_share_pct", s["withdrawn_share_pct"]["v"], wd / tot * 100 if tot else None, 0.051)

    # mix and carbon
    fuel = defaultdict(lambda: defaultdict(float))
    codes = {p["code"] if p["kind"] != "operator" else p["members"][0] for p in places.values()}
    for e, var, ts, v in rows(a.tables, "eia930_region_fuel_hourly", ["entity", "variable", "ts_utc", "value"]):
        c = e.replace("eia930:", "")
        if c in codes and p1 <= ts < p2 and f(v) is not None:
            fuel[c][var.replace("net_generation_", "").replace("_mw", "")] += f(v)
    carb = defaultdict(list)
    for e, var, ts, v in rows(a.tables, "carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"]):
        if var == "intensity_demand" and p1 <= ts < p2 and f(v) is not None:
            carb[e.replace("eia930:", "")].append(f(v))
    for pid, p in places.items():
        s = files[pid]["sections"]["mix_carbon"]
        c = p["code"] if p["kind"] != "operator" else p["members"][0]
        # the method note: a region whose one member is an operator's authority shares that grid's mix and carbon
        one = {q["members"][0]: q["code"] for q in places.values() if q["kind"] == "region" and len(q["members"]) == 1}
        mc = one.get(c, c) if p["kind"] == "operator" else c
        cc = p["members"][0] if p["kind"] == "region" and len(p["members"]) == 1 else c
        tot = sum(fuel[mc].values())
        for m in s["mix"]:
            k = m.get("key", m["fuel"])
            C.eq(f"{pid} mix {k}", m["share_pct"]["v"], fuel[mc][k] / tot * 100 if tot else None, 0.006)
        if not s["intensity"]["held"]:
            C.eq(f"{pid} intensity", s["intensity"]["v"], sum(carb[cc]) / len(carb[cc]), 0.051)

    # curtailment
    cu = defaultdict(float)
    for e, var, ts, v in rows(a.tables, "iso_curtailment_monthly", ["entity", "variable", "ts_utc", "value"]):
        if p1 <= ts < p2 and f(v) is not None:
            cu[(e, var)] += f(v)
    for pid, (op, _ba) in OPS.items():
        s = files[pid]["sections"]["spare"]
        if op in CURTAIL and not s["curtailed_wind_mwh"]["held"]:
            C.eq(f"{pid} curtailed_wind_mwh", s["curtailed_wind_mwh"]["v"], round(cu[(CURTAIL[op], "curtailed_wind_mwh")]), 0.5)
            C.eq(f"{pid} curtailed_solar_mwh", s["curtailed_solar_mwh"]["v"], round(cu[(CURTAIL[op], "curtailed_solar_mwh")]), 0.5)

    # forecast
    sc = json.load(open(os.path.join(a.site, "predict", "scores.json"), encoding="utf-8"))
    ix = {c: i for i, c in enumerate(sc["rows_columns"])}
    mape = {}
    for r in sc["rows"]:
        if r[ix["series"]] == "demand" and r[ix["cut"]] == "last_2_years" and r[ix["method"]] in ("erw", "operator"):
            mape[(r[ix["place"]], r[ix["method"]])] = r[ix["mape"]]
    for pid, p in places.items():
        s = files[pid]["sections"]["forecast"]
        key = "ba-" + p["members"][0].lower() if p["kind"] == "operator" else pid
        for m, k in (("erw", "erw_mape_pct"), ("operator", "operator_mape_pct")):
            w = mape.get((key, m))
            C.eq(f"{pid} {k}", s[k]["v"], round(w, 2) if w is not None else None, 0.0051)

    # datacenters, operators (by the table's grid); a table the site holds for a license shows no figure
    status = {}
    lp = os.path.join(a.site, "license_status.json")
    if os.path.exists(lp):
        status = json.load(open(lp, encoding="utf-8")).get("tables") or {}
    for t, key_n, key_mw in (("datacenter_facilities", "facilities_n", "facilities_mw_stated"),
                             ("datacenter_projects", "projects_n", "projects_mw_stated")):
        held = (status.get(t) or {}).get("status") == "license needed"
        dc = list(rows(a.tables, t, ["grid", "mw"]))
        for pid, (op, _ba) in OPS.items():
            s = files[pid]["sections"]["datacenters"]
            mine = [r for r in dc if r[0] == GRID_NAME[op]]
            if held:
                C.n += 1
                if s[key_n]["v"] is not None or s[key_mw]["v"] is not None or s["list"]:
                    C.bad.append(f"{pid} {t}: held for a license, yet a figure or a row is shown")
                continue
            C.eq(f"{pid} {key_n}", s[key_n]["v"], len(mine), 0)
            C.eq(f"{pid} {key_mw}", s[key_mw]["v"], round(sum(f(r[1]) or 0 for r in mine)), 0.5)

    # the trend of the peak: each month's highest hour over the 24 months
    for pid, p in places.items():
        tr = files[pid]["sections"]["tightness"]["peak_mw"].get("trend")
        if not tr:
            continue
        full = series_of(p, dem, p0, p2)
        by = defaultdict(float)
        for ts, v in full.items():
            by[ts[:7]] = max(by[ts[:7]], v)
        for m, v in zip(tr["months"], tr["v"]):
            C.eq(f"{pid} peak trend {m}", v, round(by[m], 2) if m in by else None, 0.006)

    print(f"{C.n - len(C.bad)} of {C.n} checks agree")
    for b in C.bad[:60]:
        print("  differs:", b)
    return 0 if not C.bad else 1


if __name__ == "__main__":
    sys.exit(main())
