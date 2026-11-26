"""Session 10209: every public figure of the board's week table (the trader view's face) restated independently.

    restate_week.py <iso_trader_daily.csv> <board.json of the same run> <site dir>

Part A: the week table of the board built 21 October 2026 (git 47b1fbc7e), whose trader table is the one on disk
        (run 20261021T143618Z), every public figure (ERCOT, CAISO, SPP) made again from the table by the rule as
        docs/methods/trader_view.md ("On the page") and docs/methods/price_board.md ("The week, by hub") state it:
        for each grid and measure, the latest 7 days the grid holds the measure; a mean needs all 7; the change on the
        7 before; the largest spread and the hours over the 7; the newest volatility; the newest day-ahead mean.
Part B: the board of 25 November 2026 (site/data/board.json): SP15, NP15 and SPP North, every figure, made from the
        page's own hourly files and Henry Hub series (the trader rule: Monday to Friday, hours ending 7 to 22).
Never a held grid's value.
"""
import collections
import csv
import datetime as dt
import json
import os
import statistics
import sys
from zoneinfo import ZoneInfo

TABLE, BOARD, SITE = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "site"
PUBLIC = {"ercot": "ERCOT", "caiso": "CAISO", "spp": "SPP"}
MEANS = ["da_mean_usd", "da_onpeak_mean_usd", "da_offpeak_mean_usd", "da_rt_spread_mean_usd", "implied_heat_rate"]
UTC = dt.timezone.utc
TOL = 0.00005 + 1e-9


def slug(entity):
    return entity.replace(":", "-").replace("_", "-").replace(".", "-").lower()


class Tally:
    def __init__(self):
        self.n, self.ok, self.notes = collections.Counter(), collections.Counter(), []

    def add(self, kind, mine, theirs, who, tol=TOL):
        self.n[kind] += 1
        good = (mine is None and theirs is None) or (mine is not None and theirs is not None and abs(mine - theirs) <= tol)
        self.ok[kind] += good
        if not good:
            self.notes.append(f"    {kind} {who}: mine {mine} file {theirs}")

    def show(self, title):
        print(title)
        for k in sorted(self.n):
            print(f"  {k:38s} {self.n[k]:4d} compared, {self.ok[k]:4d} agree")
        print(f"  in all: {sum(self.n.values())} figures, {sum(self.ok.values())} agree")
        for line in self.notes:
            print(line)


def part_a():
    by = {}
    with open(TABLE, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            if r["market"] in PUBLIC:
                by[(r["market"], r["entity"], r["variable"], r["ts_utc"][:10])] = float(r["value"])
    b = json.load(open(BOARD, encoding="utf-8"))
    rows = {w["hub"]: w for w in b["week"]}
    t = Tally()
    for iso in PUBLIC:
        keys = [k for k in by if k[0] == iso]
        days = sorted({k[3] for k in keys})
        days_of = {v: sorted({k[3] for k in keys if k[2] == v}) for v in {k[2] for k in keys}}
        ents = sorted({k[1] for k in keys})
        for e in ents:
            w = rows.get(slug(e))
            if w is None:
                print(f"  {e}: no week row in the file")
                continue
            last = days[-1]
            mine_last = by.get((iso, e, "da_mean_usd", last))
            t.add("Day-ahead, latest", None if mine_last is None else round(mine_last, 4), w.get("last_da", {}).get("v"), e)
            t.add("Day-ahead, latest: its date", 0, 0 if w.get("last_da", {}).get("t") == last else 1, e)
            for v in MEANS:
                wk, pv = days_of.get(v, [])[-7:], days_of.get(v, [])[-14:-7]
                cur = [by[(iso, e, v, d)] for d in wk if (iso, e, v, d) in by]
                prv = [by[(iso, e, v, d)] for d in pv if (iso, e, v, d) in by]
                a = sum(cur) / 7 if len(wk) == 7 and len(cur) == 7 else None
                p = sum(prv) / 7 if len(pv) == 7 and len(prv) == 7 else None
                m = w["means"].get(v)
                t.add(f"{v} week mean", None if a is None else round(a, 4), m["v"] if m else None, e)
                if a is not None and m:
                    t.add(f"{v} change on the 7 before", None if p is None else round(a - p, 4), m["ch"], e)
                    t.add(f"{v} week's end", 0, 0 if m["end"] == wk[-1] else 1, e)
            for v, fn, name in (("da_rt_spread_max_usd", max, "max_spread"), ("hours_rt_over_da_50", sum, "hours50")):
                wk = days_of.get(v, [])[-7:]
                vals = [by.get((iso, e, v, d)) for d in wk]
                mine = round(fn(vals), 4) if len(vals) == 7 and None not in vals else None
                t.add(name, mine, w.get(name, {}).get("v"), e)
            vols = [d for d in days if (iso, e, "da_volatility_30d_usd", d) in by]
            t.add("30-day volatility", round(by[(iso, e, "da_volatility_30d_usd", vols[-1])], 4) if vols else None, w.get("vol", {}).get("v"), e)
            if vols:
                t.add("30-day volatility: its date", 0, 0 if w["vol"]["t"] == vols[-1] else 1, e)
    t.show(f"--- Part A: the week table of the board built {b['built']}, from iso_trader_daily of the same run")
    # the on-peak rule: the note says all 7 days; the code takes a mean of at least 1
    print("  the on-peak week's rule: hubs whose latest 7 on-peak days are not all held (the note: 'no data'; the code: a mean of those held):",
          sum(1 for w in b["week"] if w["grid"] in PUBLIC.values()) and "see the count above (none differ when every hub holds all 7)")


def hours(hid):
    f = json.load(open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8"))
    tz = ZoneInfo(f["tz"])
    out = {}
    for m in ("da", "rt"):
        by = collections.defaultdict(list)
        for i, v in enumerate(f.get(m) or []):
            if v is None:
                continue
            u = dt.datetime.fromtimestamp((f["t0"] + i) * 3600, tz=UTC)
            by[u.astimezone(tz).date()].append((u, v))
        whole = {}
        for d, hv in by.items():
            a = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(UTC)
            n = d + dt.timedelta(days=1)
            want = round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(UTC) - a).total_seconds() / 3600)
            if len(hv) == want:
                whole[d] = sorted(hv)
        out[m] = whole
    return out, tz


def holidays(y):
    def mon(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31, sep1, nov1 = dt.date(y, 5, 31), dt.date(y, 9, 1), dt.date(y, 11, 1)
    return {mon(dt.date(y, 1, 1)), may31 - dt.timedelta(days=may31.weekday()), mon(dt.date(y, 7, 4)),
            sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7), nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21),
            mon(dt.date(y, 12, 25))}


def part_b():
    b = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
    rows = {w["hub"]: w for w in b["week"]}
    s = json.load(open(os.path.join(SITE, "public", "board", "s", "eia-henry-hub-spot.json"), encoding="utf-8"))
    t0 = dt.date.fromisoformat(s["t0"])
    hh = {t0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}
    t = Tally()
    for hid in ("caiso-th-sp15-gen-apnd", "caiso-th-np15-gen-apnd", "spp-sppnorth-hub"):
        f, tz = hours(hid)
        daily = collections.defaultdict(dict)
        for d, hv in f["da"].items():
            vals = [v for _, v in hv]
            work = d.weekday() < 5 and d not in holidays(d.year)
            on = [v for u, v in hv if work and 6 <= u.astimezone(tz).hour <= 21]
            off = [v for u, v in hv if not (work and 6 <= u.astimezone(tz).hour <= 21)]
            m = sum(vals) / len(vals)
            daily["da_mean_usd"][d] = m
            if on:
                daily["da_onpeak_mean_usd"][d] = sum(on) / len(on)
            daily["da_offpeak_mean_usd"][d] = sum(off) / len(off)
            g = next((hh[d - dt.timedelta(days=k)] for k in range(5) if d - dt.timedelta(days=k) in hh), None)
            if g and g > 0:
                daily["implied_heat_rate"][d] = m / g
            r = f["rt"].get(d)
            if r and len(r) == len(hv) and all(a[0] == c[0] for a, c in zip(hv, r)):
                sp = [c[1] - a[1] for a, c in zip(hv, r)]
                daily["da_rt_spread_mean_usd"][d] = sum(sp) / len(sp)
                daily["max"][d] = max(sp)
                daily["h50"][d] = sum(1 for x in sp if x > 50)
        w = rows[hid]
        for v in MEANS:
            ds = sorted(daily[v])
            if len(ds) < 7:
                t.add(f"{v} week mean", None, w["means"].get(v, {}).get("v"), hid)
                continue
            wk, pv = ds[-7:], ds[-14:-7]
            a = sum(daily[v][d] for d in wk) / 7
            p = sum(daily[v][d] for d in pv) / 7
            m = w["means"].get(v)
            # the hourly file holds each hour to the cent, so a week's mean agrees to the cent
            t.add(f"{v} week mean, to the cent", round(a, 2), round(m["v"], 2) if m else None, hid, tol=0.005 + 1e-9)
            t.add(f"{v} change, to the cent", round(a - p, 2), round(m["ch"], 2) if m else None, hid, tol=0.0101)
            t.add(f"{v} week's end", 0, 0 if m and m["end"] == str(wk[-1]) else 1, hid)
        for k, name, fn in (("max", "max_spread", max), ("h50", "hours50", sum)):
            ds = sorted(daily[k])[-7:]
            mine = fn(daily[k][d] for d in ds) if len(ds) == 7 else None
            theirs = w.get(name, {}).get("v")
            t.add(name, None if mine is None else round(mine, 2), None if theirs is None else round(theirs, 2), hid, tol=0.005 + 1e-9)
        ds = sorted(daily["da_mean_usd"])
        end = ds[-1]
        win = [end - dt.timedelta(days=k) for k in range(30, -1, -1)]
        if all(d in daily["da_mean_usd"] for d in win):
            ch = [daily["da_mean_usd"][win[i]] - daily["da_mean_usd"][win[i - 1]] for i in range(1, 31)]
            t.add("30-day volatility, to the cent", round(statistics.stdev(ch), 2), round(w["vol"]["v"], 2), hid, tol=0.005 + 1e-9)
        t.add("Day-ahead, latest, to the cent", round(daily["da_mean_usd"][end], 2), round(w["last_da"]["v"], 2), hid, tol=0.005 + 1e-9)
    t.show(f"\n--- Part B: the board of {b['built']}, three public hubs whose hourly files reach the week's end, from the page's own files")


if __name__ == "__main__":
    part_a()
    part_b()
