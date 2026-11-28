"""Audit of /equities, session 11403: the page's default figures made again from its own files, by an independent
restatement written from the method note's words (docs/methods/equities.md) and the page's stated rules, not from the
builder or site/lib/equities.ts.

1. Every company's newest filed period (index.json `newest_filed`, the table of every company) from its series file.
2. The default page (A = the list's first company): the revenue line over 3-month periods, its last point, and the
   newest period's columns.
3. The energy prices' latest values and their five moves, from the daily rows of energy_prices.json.
4. The series files against the list: one a company, no other.
No request, no write."""
import calendar
import datetime as dt
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
SUMS = ("revenue", "net_income", "capex")
ENDS = ("debt", "shares_outstanding")


def rows_of(s):
    cols = s["quarterly_columns"]
    return [dict(zip(cols, r)) for r in s["quarterly"]]


def newer(a, b):
    """a filed after b: the filing day, then the accession number (two filings of one day)."""
    return b is None or (a["filed"] or "", a["accession"] or "") > (b["filed"] or "", b["accession"] or "")


def newest(rows):
    if not rows:
        return None
    end = max(r["period_end"] for r in rows)
    at = [r for r in rows if r["period_end"] == end]
    out = {"period_end": end}
    for k in SUMS:
        cand = [r for r in at if r[k] is not None and r["months"] is not None]
        if not cand:
            out[k] = None
            continue
        m = min(r["months"] for r in cand)
        pick = None
        for r in cand:
            if r["months"] == m and newer(r, pick):
                pick = r
        out[k] = {"months": m, "v": pick[k]}
    for k in ENDS:
        pick = None
        for r in at:
            if r[k] is not None and newer(r, pick):
                pick = r
        out[k] = pick[k] if pick else None
    head = None
    for r in at:
        if newer(r, head):
            head = r
    out.update({"form": head["form"], "filed": head["filed"], "url": head["url"]})
    return out


bad, n = 0, 0
files = set(os.listdir(os.path.join(D, "series")))
listed = set()
for c in idx["companies"]:
    listed.add(c["file"].split("/")[1])
    s = json.load(open(os.path.join(D, c["file"]), encoding="utf-8"))
    mine = newest(rows_of(s))
    theirs = c.get("newest_filed")
    n += 1
    if (mine is None) != (theirs is None):
        print(f"NEWEST DIFFERS (one is empty): {c['ticker']} mine {mine} file {theirs}")
        bad += 1
        continue
    if mine is None:
        continue
    for k in ("period_end", "form", "filed", "url", *SUMS, *ENDS):
        if mine[k] != theirs.get(k):
            print(f"NEWEST DIFFERS: {c['ticker']} {k}: mine {mine[k]} file {theirs.get(k)}")
            bad += 1
    if (s["quarterly"] != []) != (c["fundamentals_status"] == "shown"):
        print(f"STATUS DIFFERS: {c['ticker']} {c['fundamentals_status']} with {len(s['quarterly'])} rows")
        bad += 1
print(f"1. newest filed period: {n} companies, {bad} figures differ")
print(f"4. series files {len(files)}, listed {len(listed)}; files no company names: {sorted(files - listed)}; "
      f"names with no file: {sorted(listed - files)}")

# 2. the default page: A is the list's first company (no segment line, no index in the list)
first = idx["companies"][0]
s = json.load(open(os.path.join(D, first["file"]), encoding="utf-8"))
rows = rows_of(s)
line = {}
for r in rows:
    if r["months"] == 3 and r["revenue"] is not None:
        if newer(r, line.get(r["period_end"])):
            line[r["period_end"]] = r
pts = sorted(line.items())
print(f"2. default A: {first['ticker']} {first['name']}; revenue over 3-month periods: {len(pts)} points, "
      f"{pts[0][0]} to {pts[-1][0]}; last {pts[-1][1]['revenue']:,} USD = {pts[-1][1]['revenue'] / 1e6:,.0f} million "
      f"({pts[-1][1]['form']}, filed {pts[-1][1]['filed']})")
end = max(r["period_end"] for r in rows)
for m in sorted({r["months"] for r in rows if r["period_end"] == end and r["months"] is not None}):
    own = [r for r in rows if r["period_end"] == end and r["months"] == m]
    cells = []
    for k in SUMS:
        pick = None
        for r in own:
            if r[k] is not None and newer(r, pick):
                pick = r
        cells.append(f"{k} {pick[k] / 1e6:,.0f}" if pick else f"{k} not filed")
    for k in ENDS:
        pick = None
        for r in rows:
            if r["period_end"] == end and r[k] is not None and newer(r, pick):
                pick = r
        cells.append(f"{k} {pick[k] / 1e6:,.{1 if k == 'shares_outstanding' else 0}f}" if pick else f"{k} not filed")
    print(f"   newest column, {m} months to {end}: " + "; ".join(cells))

# 3. energy prices: latest and the five moves, from the daily rows
P = json.load(open(os.path.join(D, "energy_prices.json"), encoding="utf-8"))


def back_months(day, n):
    y, m = day.year, day.month - n
    while m < 1:
        y, m = y - 1, m + 12
    return dt.date(y, m, min(day.day, calendar.monthrange(y, m)[1]))


def at_or_before(pts, day):
    p = [x for x in pts if x[0] <= day.isoformat()]
    return p[-1] if p else None


badp = 0
for sr in P["series"]:
    pts = [(d, v) for d, v in P["daily"].get(sr["id"], []) if v is not None]
    if sr["status"] != "shown":
        if pts or sr["last_value"] or any(sr["moves"].values()):
            print(f"HELD SERIES CARRIES A VALUE: {sr['id']}")
            badp += 1
        continue
    last_d, last_v = pts[-1]
    day = dt.date.fromisoformat(last_d)
    bases = {"d": pts[-2] if len(pts) > 1 else None, "w": at_or_before(pts, day - dt.timedelta(days=7)),
             "m": at_or_before(pts, back_months(day, 1)), "ytd": at_or_before(pts, dt.date(day.year - 1, 12, 31)),
             "y": at_or_before(pts, back_months(day, 12))}
    if sr["last_value"] != {"t": last_d, "v": last_v}:
        print(f"LATEST DIFFERS: {sr['id']} {sr['last_value']} against {last_d} {last_v}")
        badp += 1
    out = []
    for k, b in bases.items():
        f = sr["moves"].get(k)
        if b is None:
            if f is not None:
                print(f"MOVE DIFFERS: {sr['id']} {k}: mine none, file {f}")
                badp += 1
            out.append(f"{k} none")
            continue
        ch = round(last_v - b[1], 4)
        pct = round((last_v - b[1]) / b[1] * 100, 2) if b[1] else None
        if f is None or f["t"] != b[0] or abs(f["v"] - b[1]) > 1e-9 or abs(f["ch"] - ch) > 1e-9 or f["pct"] != pct:
            print(f"MOVE DIFFERS: {sr['id']} {k}: mine {b[0]} {b[1]} {ch} {pct}, file {f}")
            badp += 1
        out.append(f"{k} {pct:+.2f}% from {b[0]}" if pct is not None else f"{k} {ch:+.4f}")
    print(f"3. {sr['id']:20s} {sr['freq']} last {last_v} on {last_d}; " + "; ".join(out))
print(f"3. energy prices: {badp} figures differ")
