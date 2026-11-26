"""Session 10222 (supply audit): every figure of /supply's default view, re-done from the page's own file and the
warehouse's tables by the method note alone (docs/methods/supply_and_trade.md), with no code of the warehouse or the
site imported; standard library only.

    python restate.py <supply.json> <drawn page .html> <output dir of the tables> <out.json>

The history of each series is the table as this machine holds it (the main copy's warehouse/output, read only); the
newest values, which those tables do not reach, are the page file's own last 52 values (its spark). Where both hold a
date the file's value is used and the difference is counted (a revision between the two copies). Burn rows are
restated apart (burn.py) and set beside the page's here only through the file.

Rules, as the note states them:
  period before   weekly: the value 7 days before the latest (or nearest within 3 days); monthly: the month before
  last year       weekly: the value 364 days before, or the nearest within 3 days; monthly: the same month a year before
  five years      the values 52, 104, 156, 208, 260 weeks before (monthly: the same month), all five or none; their
                  mean, lowest and highest; "outside" when the latest is below the lowest or above the highest
  change          latest less the period before; against the mean of the same change in the five years before, each
                  taken at the five-year dates and one period before each; outside when beyond their lowest or highest
  percent         of the base, only when the base is above zero
  units           thousand barrels shown as million (over 1,000); gas trade MMcf over 1,000 and the month's days
"""
import csv
import datetime as dt
import html as H
import json
import re
import sys
from collections import defaultdict

fpath, hpath, outdir, outp = sys.argv[1:5]
OVERLAY_SEASON = len(sys.argv) > 5 and sys.argv[5] == "--season"
F = json.load(open(fpath, encoding="utf-8"))
page = open(hpath, encoding="utf-8").read()
NEAR = 3


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def table(name, keep=None):
    out = defaultdict(dict)
    meta = {}
    with open(f"{outdir}/{name}.csv", encoding="utf-8") as f:
        rd = csv.DictReader(l for l in f if not l.startswith("#"))
        for r in rd:
            if r["value"] in ("", None):
                continue
            key = (r["entity"], r.get("variable", ""))
            if keep and not keep(r):
                continue
            out[key][dt.date.fromisoformat(r["ts_utc"][:10])] = float(r["value"])
            meta[r["entity"]] = (r.get("unit", ""), r.get("node", ""))
    return out, meta


def by_entity(t, variable=None):
    s = defaultdict(dict)
    for (e, v), d in t.items():
        if variable is None or v == variable:
            s[e].update(d)
    return s


def at(s, target, freq):
    if freq == "M":
        return (target, s[target]) if target in s else None
    c = [d for d in s if abs((d - target).days) <= NEAR]
    if not c:
        return None
    d = min(c, key=lambda x: (abs((x - target).days), x))
    return d, s[d]


def back(d, k, freq):
    return dt.date(d.year - k, d.month, 1) if freq == "M" else d - dt.timedelta(days=364 * k)


def step(d, freq):
    if freq == "W":
        return d - dt.timedelta(days=7)
    return dt.date(d.year - (d.month == 1), 12 if d.month == 1 else d.month - 1, 1)


def figures(s, freq):
    d0 = max(s)
    v0 = s[d0]
    out = {"t": d0.isoformat(), "v": v0}
    p = at(s, step(d0, freq), freq)
    out["prev"] = None if p is None else {"t": p[0].isoformat(), "v": p[1], "ch": v0 - p[1]}
    y = at(s, back(d0, 1, freq), freq)
    out["year"] = None if y is None else {"t": y[0].isoformat(), "v": y[1], "ch": v0 - y[1], "pct": (100 * (v0 - y[1]) / y[1]) if y[1] > 0 else None}
    five = [at(s, back(d0, k, freq), freq) for k in range(1, 6)]
    out["avg5"] = None
    if all(five):
        vals = [x[1] for x in five]
        m = sum(vals) / 5
        out["avg5"] = {"v": m, "lo": min(vals), "hi": max(vals), "ch": v0 - m, "pct": (100 * (v0 - m) / m) if m > 0 else None, "outside": v0 < min(vals) or v0 > max(vals)}
    out["change"] = None
    if p is not None:
        chs = []
        for x in five:
            b = None if x is None else at(s, step(x[0], freq), freq)
            chs.append(None if b is None else x[1] - b[1])
        ch = v0 - p[1]
        c = {"v": ch, "avg5": None, "lo": None, "hi": None, "surprise": None, "outside": False}
        if all(z is not None for z in chs):
            m = sum(chs) / 5
            c.update(avg5=m, lo=min(chs), hi=max(chs), surprise=ch - m, outside=ch < min(chs) or ch > max(chs))
        out["change"] = c
    return out


# ---- the series of each row: the table's history, the file's newest values over it ----
rows = {r["id"]: r for r in F["rows"]}
series, revisions = {}, {}
gas, _ = table("eia_gas_storage_weekly")
pet, pmeta = table("eia_petroleum_supply_weekly", keep=lambda r: r["entity"].startswith("eia:W"))
_, gmeta = table("eia_gas_storage_weekly")
for t, meta in ((gas, gmeta), (pet, pmeta)):
    for e, s in by_entity(t).items():
        rid = slug(e)
        if rid in rows:
            scale = 0.001 if meta[e][0] == "kbbl" else 1.0
            series[rid] = {d: v * scale for d, v in s.items()}
basin, _ = table("eia_basin_production_monthly")
for (e, v), s in basin.items():
    if slug(e) in rows:
        series[slug(e)] = dict(s)
trade, tmeta = table("eia_gas_trade_monthly")
te = by_entity(trade)


def days_in(d):
    n = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return (n - d).days


def per_day(s):
    return {d: v / 1000.0 / days_in(d) for d, v in s.items()}


for e, s in te.items():
    if slug(e) in rows:
        series[slug(e)] = per_day(s)
lng = te["eia:N9133US2"]
newest = max(lng)
terms = {e: s for e, s in te.items() if "_ENG_Y" in e and e.endswith("-Z00_MMCF")}
major = {e for e, s in terms.items() if any((newest - d).days <= 366 and v >= 5000.0 for d, v in s.items())}
series["erw-lng-other-points"] = per_day({d: v - sum(terms[e].get(d, 0.0) for e in major) for d, v in lng.items()})
cot, _ = table("cftc_cot_positions")
for (e, v), s in cot.items():
    if v == "managed_money_net" and slug(e) in rows:
        series[slug(e)] = dict(s)


def cleared(name, tzname, entity):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tzname)
    t, _ = table(name)
    per = defaultdict(lambda: [0, 0.0])
    for (e, v), s in t.items():
        if entity and e != entity:
            continue
        for d, val in s.items():
            pass
    # the table keyed by date loses the hour: read the hours again
    hours = defaultdict(lambda: [0, 0.0])
    with open(f"{outdir}/{name}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["value"] == "" or (entity and r["entity"] != entity):
                continue
            ts = dt.datetime.fromisoformat(r["ts_utc"].replace("Z", "+00:00")).astimezone(tz)
            k = (ts.date(), r["entity"])
            hours[k][0] += 1
            hours[k][1] += float(r["value"])
    def exp(d):
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        n = d + dt.timedelta(days=1)
        b = dt.datetime(n.year, n.month, n.day, tzinfo=tz)
        return round((b - a).total_seconds() / 3600) if False else round((b.astimezone(dt.timezone.utc) - a.astimezone(dt.timezone.utc)).total_seconds() / 3600)
    days = defaultdict(list)
    for (d, e), (n, mwh) in hours.items():
        days[d].append((n == exp(d), mwh))
    daily = {d: sum(m for _, m in v) for d, v in days.items() if all(w for w, _ in v)}
    wk = defaultdict(list)
    for d, v in daily.items():
        wk[d + dt.timedelta(days=(4 - d.weekday()) % 7)].append(v)
    return {e: sum(v) / 7 for e, v in wk.items() if len(v) == 7}


series["cleared-caiso"] = cleared("caiso_dam_cleared_energy", "America/Los_Angeles", None)
series["cleared-spp"] = cleared("spp_dam_cleared_energy", "America/Chicago", "spp:SPP")
series["cleared-spp-west"] = cleared("spp_dam_cleared_energy", "America/Chicago", "spp:SWPW")

# the burn rows: burn.py's weeks from EIA-930's workbook (to 2 October 2026; California to the join), the file's
# newest weeks over them; the seven grids together as the sum over the weeks all seven hold
import glob
import os
burn = defaultdict(dict)
for path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(outp)), "burn_*.csv")):
    if path.endswith("_cmp.csv"):
        continue
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if "grid" in r:
                burn[(r["grid"], r["fuel"])][dt.date.fromisoformat(r["week_end"])] = float(r["value"])
for (grid, fuel), s in burn.items():
    series[f"burn-{grid}-{fuel.replace('_', '-')}"] = dict(s)
for fuel in ("natural_gas", "coal", "oil"):
    gs = [g for (g, f) in burn if f == fuel]
    if len(gs) == 7:
        common = set.intersection(*(set(burn[(g, fuel)]) for g in gs))
        series[f"burn-all-{fuel.replace('_', '-')}"] = {w: sum(burn[(g, fuel)][w] for g in gs) for w in common}

# overlay the file's newest values (its spark) and count the revisions between the two copies
result = {}
for rid, r in rows.items():
    if r["status"] != "ok":
        continue
    s = dict(series.get(rid, {}))
    hist_n = len(s)
    rev = []
    over = list(zip(r["spark"]["t"], r["spark"]["v"]))
    if OVERLAY_SEASON:
        # the file's own year-before values (season.last at back(d, 1)) and this year's (season.cur)
        for t, c, l in zip(r["season"]["t"], r["season"]["cur"], r["season"]["last"]):
            d = dt.date.fromisoformat(t)
            if c is not None:
                over.append((t, c))
            if l is not None:
                b = back(d, 1, r["freq"])
                near = at(s, b, r["freq"]) if r["freq"] == "W" else (b, None)
                over.append(((near[0] if near else b).isoformat(), l))
    for t, v in over:
        d = dt.date.fromisoformat(t)
        if d in s and abs(round(s[d], 4) - v) > 1.5e-4:
            rev.append((t, round(s[d], 4), v))
        s[d] = v
    revisions[rid] = rev
    result[rid] = (figures(s, r["freq"]), hist_n)

# ---- the file against the restatement ----
def close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= 6e-5 * max(1.0, abs(b))


def cmp_row(r, x):
    bad = []
    if not close(r["last"]["v"], x["v"]) or r["last"]["t"] != x["t"]:
        bad.append("last")
    for k in ("prev", "year"):
        a, b = r.get(k), x[k]
        if (a is None) != (b is None) or (a and (a["t"] != b["t"] or not close(a["ch"], b["ch"]))):
            bad.append(k)
        elif a and k == "year" and not close(a["pct"], b["pct"]):
            bad.append("year.pct")
    a, b = r.get("avg5"), x["avg5"]
    if (a is None) != (b is None) or (a and (not close(a["v"], b["v"]) or not close(a["lo"], b["lo"]) or not close(a["hi"], b["hi"]) or a["outside"] != b["outside"])):
        bad.append("avg5")
    a, b = r.get("change"), x["change"]
    if (a is None) != (b is None):
        bad.append("change")
    elif a:
        if (a["surprise"] is None) != (b["surprise"] is None) or (a["surprise"] is not None and (not close(a["surprise"], b["surprise"]) or not close(a["lo"], b["lo"]) or not close(a["hi"], b["hi"]))) or a["outside"] != b["outside"]:
            bad.append("change")
    return bad


# ---- the page's words for a figure, restated from the page's stated digits ----
UNIT_WORDS = {"thousand bbl/d": "kb/d", "kbbl/d": "kb/d", "thousand short tons/d": "k short tons/d", "percent": "%", "bcf": "Bcf", "bcf/d": "Bcf/d"}
MINUS = chr(0x2212)


def places(v, unit):
    if unit == "contracts":
        return 0
    if unit in ("percent", "%"):
        return 1
    a = abs(v)
    return 0 if a >= 1000 else 1 if a >= 100 else 2


def fmt(v, unit, ref=None):
    p = places(v if ref is None else ref, unit)
    from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
    q = Decimal(repr(abs(v))).quantize(Decimal(1).scaleb(-p), rounding=ROUND_HALF_UP)
    s = f"{q:,.{p}f}"
    return ("-" if v < 0 and float(q) != 0 else "") + s


def signed(v, unit, ref):
    t = fmt(abs(v), unit, ref)
    if float(t.replace(",", "")) == 0:
        return t
    return ("+" if v > 0 else MINUS) + t


def pct(v):
    from decimal import Decimal, ROUND_HALF_UP
    t = f"{Decimal(repr(abs(v))).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}"
    if float(t) == 0:
        return t + "%"
    return ("+" if v > 0 else MINUS) + t + "%"


def tag(sense, diff, unit, ref):
    if not re.search(r"[1-9]", signed(diff, unit, ref)) or not sense or diff == 0:
        return ""
    return "looser" if diff * sense > 0 else "tighter"


MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def datew(t, freq):
    y, m, d = map(int, t.split("-"))
    return f"{MON[m-1]} {y}" if freq == "M" else f"{d} {MON[m-1]} {y}"


NH = "not held yet"


def cells(r, x):
    u = UNIT_WORDS.get(r["unit"], r["unit"])
    ref = x["v"]
    c = [fmt(x["v"], u) + u, datew(x["t"], r["freq"])]
    c.append(NH if not x["prev"] else signed(x["prev"]["ch"], u, ref) + tag(r["sense"], x["prev"]["ch"], u, ref))
    y = x["year"]
    c.append(NH if not y else signed(y["ch"], u, ref) + (pct(y["pct"]) if y["pct"] is not None else "") + tag(r["sense"], y["ch"], u, ref))
    a = x["avg5"]
    c.append(NH if not a else fmt(a["v"], u, ref))
    c.append(NH if not a else signed(a["ch"], u, ref) + (pct(a["pct"]) if a["pct"] is not None else "") + tag(r["sense"], a["ch"], u, ref))
    ch = x["change"]
    c.append(NH if not ch or ch["surprise"] is None else signed(ch["surprise"], u, ref) + ("outside range" if ch["outside"] else ""))
    return c


def drawn_cells(rid):
    m = re.search(r'<tr[^>]*data-row="' + re.escape(rid) + r'"[^>]*>(.*?)</tr>', page, re.S)
    if not m:
        return None
    tds = re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), re.S)
    return [re.sub(r"\s+", "", H.unescape(re.sub(r"<[^>]+>", "", t))) for t in tds]


report = {"rows": {}, "summary": {}}
n_cells = n_eq = n_file = n_file_eq = 0
for rid, (x, hist_n) in result.items():
    r = rows[rid]
    bad = cmp_row(r, x)
    n_file += 1
    n_file_eq += not bad
    want = [re.sub(r"\s+", "", w) for w in cells(r, x)]
    got = drawn_cells(rid)
    diffs = []
    for i, w in enumerate(want):
        n_cells += 1
        g = got[i] if got and i < len(got) else None
        if g == w:
            n_eq += 1
        else:
            diffs.append((i, w, g))
    report["rows"][rid] = {"file_vs_restated": bad, "cells_diff": diffs, "history_points": hist_n, "revisions": revisions[rid][:5], "n_revisions": len(revisions[rid]),
                           "restated": x}
report["summary"] = {"rows": n_file, "rows_equal_to_file": n_file_eq, "cells": n_cells, "cells_equal_to_page": n_eq, "major_lng": sorted(major)}

# headline cards and the surprises list
heads = ["eia-nw2-epg0-swo-r48-bcf", "eia-wcestus1", "eia-w-epc0-sax-ycuok-mbbl", "eia-wgtstus1", "eia-wdistus1"]
hc = []
for rid in heads:
    x = result[rid][0]
    r = rows[rid]
    u = UNIT_WORDS.get(r["unit"], r["unit"])
    m = re.search(r'data-n="head\|' + re.escape(rid) + r'">([^<]*)<', page)
    hc.append((rid, fmt(x["v"], u), m.group(1) if m else None))
report["headline"] = hc
outs = [(rid, x) for rid, (x, _) in result.items() if x["change"] and x["change"]["outside"] and x["change"]["surprise"] is not None]
far = lambda x: abs(x["change"]["surprise"]) / ((x["change"]["hi"] or 0) - (x["change"]["lo"] or 0)) if ((x["change"]["hi"] or 0) - (x["change"]["lo"] or 0)) > 0 else 0
# the burn rows' outside flags come from the file (restated apart)
for rid, r in rows.items():
    if r["group"] == "burn" and r["status"] == "ok" and r.get("change") and r["change"]["outside"] and r["change"]["surprise"] is not None:
        outs.append((rid, {"change": r["change"]}))
outs.sort(key=lambda kv: -far(kv[1]))
want_sur = [rid for rid, _ in outs[:8]]
got_sur = re.findall(r'href="/supply\?s=([^#"]+)#chart" class="min-w-0 truncate', page)
report["surprises"] = {"restated": want_sur, "drawn": got_sur, "equal": want_sur == got_sur}
json.dump(report, open(outp, "w", encoding="utf-8"), indent=1, default=str)
print(json.dumps(report["summary"]))
print("headline", hc)
print("surprises equal", want_sur == got_sur, want_sur, got_sur)
for rid, v in report["rows"].items():
    if v["file_vs_restated"] or v["cells_diff"]:
        print(rid, v["file_vs_restated"], v["cells_diff"][:3], "revisions", v["n_revisions"], v["revisions"][:2])
