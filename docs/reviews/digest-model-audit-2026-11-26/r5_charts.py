"""Session 10235: the Digests' charts of the day, each figure of the printed sentence set against its record
(docs/digest/charts/<date>.json) and, where the main checkout holds the table, re-done from the table: the month's value,
the record before it (the highest earlier value of the series), its month, the first month and the count of months.

Run: python r5_charts.py <output dir> <repo root> > r5_charts.out
"""
import csv
import json
import os
import re
import sys

OUT, ROOT = sys.argv[1], sys.argv[2]
DATES = ["2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23",
         "2026-11-06", "2026-11-12"]


def chart_text(v):
    a = abs(v)
    nd = 0 if a >= 10000 else 1 if a >= 100 else 2 if a >= 1 else 4
    return f"{v:,.{nd}f}"


for d in DATES:
    rec = json.load(open(os.path.join(ROOT, "docs", "digest", "charts", d + ".json"), encoding="utf-8"))
    md = open(os.path.join(ROOT, "docs", "digest", d + ".md"), encoding="utf-8").read()
    sec = re.search(r"## ERW's Chart of the Day\n(.*?)(?:\n## |\Z)", md, re.S)
    print(f"\n== {d}: table {rec.get('table')}; rule {rec.get('flag', {}).get('rule', rec.get('rule'))}")
    if not sec:
        print(f"  the issue prints NO chart section; the record exists (fact: {rec.get('fact', '')[:160]})")
        continue
    n = rec.get("numbers", {})
    fact = rec.get("fact", "")
    print(f"  printed fact equals the record's fact: {fact in sec.group(1)}")
    for k in ("value", "old_record"):
        if k in n:
            t = chart_text(float(n[k]))
            print(f"  record {k} {n[k]} drawn as {t}: {'in the sentence' if t in fact else 'NOT in the sentence'}")
    flag = rec.get("flag", {})
    cmp_ = flag.get("compared", {})
    pts = rec.get("points") or {}
    if pts.get("series"):
        xs, vs = pts["x"], pts["series"][0]["values"]
        if len(vs) >= 2 and "old_record" in n:
            prior = [(v, x) for v, x in zip(vs[:-1], xs[:-1]) if v is not None]
            if flag.get("direction", "high") == "high":
                top = max(prior)
                print(f"  the chart's own points: highest before the last {top[0]:,.2f} in {top[1][:7]}; record printed {float(n['old_record']):,.2f} ({cmp_.get('old_record_date', '')[:7]})"
                      + ("  << A POINT DRAWN ON THE CHART BEATS THE PRINTED RECORD" if top[0] > float(n["old_record"]) + 1e-6 else ""))
    # re-done from the table where it is here
    path = os.path.join(OUT, rec["table"] + ".csv")
    ser = flag.get("series") or {}
    if not os.path.exists(path) or not ser:
        print(f"  table {rec['table']} is not on this machine: the figures rest on the record alone")
        continue
    ent, var = ser.get("entity"), ser.get("variable")
    vals = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if r["entity"] == ent and r["variable"] == var:
                vals[r["ts_utc"][:7]] = float(r["value"])
    month = flag.get("date", "")[:7]
    v = vals.get(month)
    before = {m: x for m, x in vals.items() if m < month}
    top = max(before.items(), key=lambda kv: kv[1]) if before else None
    low = min(before.items(), key=lambda kv: kv[1]) if before else None
    rec_old = top if flag.get("direction", "high") == "high" else low
    first = min(vals) if vals else None
    print(f"  table now: {month} = {v}; record before it {rec_old[1]:,.2f} in {rec_old[0]}; first month {first}; months held {len(vals)} "
          f"(to {max(vals)})")
    print(f"  printed: value {chart_text(float(n['value']))}, record {chart_text(float(n['old_record']))} in {cmp_.get('old_record_date', '')[:7]}; "
          f"re-done: value {chart_text(v) if v is not None else None}, record {chart_text(rec_old[1])} in {rec_old[0]}")
