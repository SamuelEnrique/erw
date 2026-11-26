"""Session 10232 (reports audit), r1: every figure the two draft reports drew, re-done from the warehouse CSVs by an
independent evaluator of its check key (no import of the site's code or of the builders), set against the drawn raw
value and the shown text, to the digit.

    python runs/c10232/r1_keys.py <csv dir> <drawn dir> <tag>

Keys: series|<table>|<entity>|<variable>|<ts>  (the CSV row);  shape|<entity>|<market>|<stat>|<start>|<end>  (the
period statistics over complete months, restated from the method: a month is complete when <market>_hours equals
hours_in_month; n, npos (premium > 0), mean premium, usdmw = sum of premium x hours);  calc|<op>|<a>|<b> with "~" for
"|" in a and b (ratio a/b, diff a-b, pct a/b x 100).
"""
import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

CSV_DIR, DRAWN, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
_cache = {}


def table(name):
    if name not in _cache:
        rows = {}
        with open(os.path.join(CSV_DIR, name + ".csv"), encoding="utf-8") as f:
            lines = (ln for ln in f if not ln.startswith("#"))
            for r in csv.DictReader(lines):
                rows[(r["entity"], r["variable"], r["ts_utc"][:10])] = float(r["value"])
        _cache[name] = rows
    return _cache[name]


def months(entity, market):
    rows = table("cost_of_power_monthly")
    by = {}
    for (e, v, ts), val in rows.items():
        if e == entity:
            by.setdefault(ts, {})[v] = val
    out = []
    for ts in sorted(by):
        m = by[ts]
        if f"{market}_shape_premium" not in m:
            continue
        out.append(dict(ts=ts, premium=m[f"{market}_shape_premium"], hours=m.get(f"{market}_hours"),
                        complete=m.get(f"{market}_hours") == m.get("hours_in_month")))
    return out


def shape(entity, market, stat, start, end):
    ms = [m for m in months(entity, market) if m["complete"] and start <= m["ts"] < end]
    if stat == "n":
        return float(len(ms))
    if stat == "npos":
        return float(sum(1 for m in ms if m["premium"] > 0))
    if stat == "mean":
        return sum(m["premium"] for m in ms) / len(ms)
    if stat == "usdmw":
        return sum(m["premium"] * m["hours"] for m in ms)
    raise ValueError(stat)


def value(key):
    p = key.split("|")
    if p[0] == "series":
        return table(p[1])[(p[2], p[3], p[4][:10])]
    if p[0] == "shape":
        return shape(p[1], p[2], p[3], p[4], p[5])
    if p[0] == "calc":
        a, b = value(p[2].replace("~", "|")), value(p[3].replace("~", "|"))
        return a / b if p[1] == "ratio" else a - b if p[1] == "diff" else a / b * 100
    raise ValueError(key)


def fmt2(v):
    # the shortest decimal of the double, rounded half away from zero: what ICU's toLocaleString does (an exact binary
    # value of 134810.0849999... reads "134810.085" there and shows .09)
    d = Decimal(repr(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}"


def shown(v, drawn):
    if "million" in drawn or "billion" in drawn:
        big = 1e9 if "billion" in drawn else 1e6
        d = Decimal(v / big).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP).normalize()
        s = f"{d:,f}" if d != d.to_integral() else f"{int(d):,}"
        return f"{s} {'billion' if big == 1e9 else 'million'}"
    if float(v).is_integer():
        return f"{int(round(v)):,}"
    return fmt2(v)


bad = 0
total = 0
for page in ("shape-premium", "ai-gigawatts"):
    figs = json.load(open(os.path.join(DRAWN, f"{TAG}_{page}_n.json"), encoding="utf-8"))
    seen = set()
    for f in figs:
        total += 1
        v = value(f["key"])
        raw = float(f["raw"])
        ok_raw = abs(v - raw) <= 1e-9 * max(1.0, abs(v))
        ok_shown = shown(v, f["shown"]) == f["shown"].strip()
        if not (ok_raw and ok_shown):
            bad += 1
            print(f"MISMATCH {page}: {f['key']} drawn raw {raw} shown {f['shown']!r}; restated {v} shown {shown(v, f['shown'])!r}")
        seen.add(f["key"])
    print(f"{page}: {len(figs)} figures drawn ({len(seen)} distinct keys); re-done independently")
print(f"total {total} figures, {bad} mismatches")
sys.exit(1 if bad else 0)
