"""Session 10214 (demand audit): an independent restatement of every figure /demand's as-metered view can print, from
EIA-930's hourly demand, with none of the warehouse's or the site's code. Standard library only. Written from
docs/methods/demand_growth.md ("Input", "Which hours are used", "The rows", "The rule in full").

Input: runs/c10214/hours/<BA>.csv (extract.py: the hour's start, EIA's Demand, EIA's Adjusted demand, from the
workbooks of 3 October 2026), and optionally the October 2026 hours from the main copy's eia930_all_demand (EIA's API,
demand_mw), used only where the workbook has no value, so the year so far through October can be formed.

Memory: each area's file is read row by row, twice. Pass 1 keeps one UTC year of values at a time (for that year's
median of the hours that pass the neighbour test); pass 2 keeps only sums, counts and maxima. The range test (a third to
three times the area's median hour over the whole read) is decided from the yearly medians: the whole-history median lies
between the smallest and the largest of them, and the script reports any hour whose fate that band leaves open.

Usage: python restate.py <hours dir> <site demand_growth.json> <out json> [--october <eia930_all_demand.csv>] [--column demand|adjusted_demand] [--no-neighbour] [--base YEAR]
"""
import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

AREAS = {"ERCO": "America/Chicago", "CISO": "America/Los_Angeles", "PJM": "America/New_York", "MISO": "America/Chicago",
         "SWPP": "America/Chicago", "NYIS": "America/New_York", "ISNE": "America/New_York", "US48": "America/New_York"}
LATE_FROM = datetime(2023, 10, 31, 23, tzinfo=timezone.utc)
LATE_TO = datetime(2025, 12, 2, 23, tzinfo=timezone.utc)
JUMP, NEAR_YEAR, NEAR_CELL = 0.25, 0.95, 0.90
H = timedelta(hours=1)


def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def rows_of(path, ba, column, october):
    """(hour start, value or None) in time order, one row an hour as the workbook has them; California's late hours set
    back (the first lands on its own neighbour's row and is dropped; the hour before LATE_TO is left with no row)."""
    seen = set()
    last = None
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ts = parse(r["ts_start_utc"])
            if ts in seen:
                continue
            seen.add(ts)
            raw = r[column] if ba != "US48" else r["demand"]
            v = float(raw) if raw not in ("", None) else None
            if v is None and october is not None and ts in october:
                v = october[ts]
            if ba == "CISO" and LATE_FROM <= ts < LATE_TO:
                if ts == LATE_FROM:
                    continue
                ts = ts - H
            last = ts
            yield ts, v
    if october is not None and last is not None and october:
        t, end = last + H, min(max(october), datetime(2026, 11, 1, 5, tzinfo=timezone.utc))
        while t <= end:   # a row for every hour, blank where the API has none, as the workbook writes them
            yield t, october.get(t)
            t += H


def median(xs):
    return statistics.median(xs) if xs else None


def neighbour_screen(stream, neighbour=True):
    """Rule 1 to 3: held, above zero, within JUMP of the median of those of the two rows before and two after that are
    held and above zero (a neighbour that is not drops out). Yields (ts, raw value, kept value or None)."""
    PAD = (None, None)   # past either end of the file a neighbour is missing, as a shift past the end is

    def judge(win):
        ts, v = win[2]
        if v is None or v <= 0:
            return ts, v, None
        if not neighbour:
            return ts, v, v
        around = [w[1] for j, w in enumerate(win) if j != 2 and w[1] is not None and w[1] > 0]
        m = median(around)
        if m is not None and abs(v - m) > JUMP * m:
            return ts, v, None
        return ts, v, v

    # rows by position: a window of five, the row judged in the middle
    win = deque([PAD, PAD], maxlen=5)
    for row in stream:
        win.append(row)
        if len(win) == 5:
            yield judge(win)
    for _ in range(2):
        win.append(PAD)
        if len(win) == 5 and win[2] is not PAD:
            yield judge(win)


def local_parts(ts, tz):
    t = ts.astimezone(tz)
    return t.year, t.month, t.hour


def hours_between(a, b, tz):
    ta = datetime(a[0], a[1], 1, tzinfo=tz).astimezone(timezone.utc)
    tb = datetime(b[0], b[1], 1, tzinfo=tz).astimezone(timezone.utc)
    return int((tb - ta) / H)


def area(path, ba, column, october, base, neighbour):
    tz = ZoneInfo(AREAS[ba])
    # pass 1: yearly medians of the hours that pass rules 1 to 3
    meds, cur, year = [], [], None
    for ts, v, k in neighbour_screen(rows_of(path, ba, column, october), neighbour):
        if year is not None and ts.year != year:
            meds.append(median(cur)) if cur else None
            cur = []
        year = ts.year
        if k is not None:
            cur.append(k)
    if cur:
        meds.append(median(cur))
    lo, hi = min(meds), max(meds)
    open_fate = 0
    # pass 2: aggregates
    S = defaultdict(lambda: [0.0, 0, None, None, 0])  # key -> [sum, used, max, first ts of max, rows]
    blank = zero = jumps = 0
    last_used = None
    newest = 0
    since = datetime(base, 1, 1, tzinfo=tz).astimezone(timezone.utc)
    for ts, v, k in neighbour_screen(rows_of(path, ba, column, october), neighbour):
        if k is not None:
            if (lo / 3 <= k < hi / 3) or (3 * lo < k <= 3 * hi):
                open_fate += 1
            if k < lo / 3 or k > 3 * hi:
                k = None
        y, m, h = local_parts(ts, tz)
        if ts >= since:
            if v is None:
                blank += 1
            elif v <= 0:
                zero += 1
            elif k is None:
                jumps += 1
        if y < base:
            continue
        newest = max(newest, y)
        for key in ((y,), (y, m), (y, "h", h), (y, m, h)):
            s = S[key]
            s[4] += 1
            if k is not None:
                s[0] += k
                s[1] += 1
                if s[2] is None or k > s[2]:
                    s[2], s[3] = k, ts
        if k is not None:
            last_used = ts
    return dict(S=S, tz=tz, newest=newest, last_used=last_used, screened=dict(blank=blank, not_positive=zero, jumps=jumps), band=(lo, hi), open_fate=open_fate)


def summarize(a, ytd_m, base):
    S, tz, newest = a["S"], a["tz"], a["newest"]
    out, at = {}, {}
    rnd = lambda x: round(x, 1)
    for y in sorted({k[0] for k in S}):
        r, t = {}, {}
        n = hours_between((y, 1), (y + 1, 1), tz)
        s = S[(y,)]
        if y < newest and s[1] >= NEAR_YEAR * n:
            r.update(avg_demand_mw=rnd(s[0] / s[1]), hours_used=s[1], hours_in_year=n)
            r["peak_demand_mw"] = rnd(s[2])
            t["peak_demand_mw"] = s[3].strftime("%Y-%m-%dT%H:%M:%SZ")
            for h in range(24):
                c = S.get((y, "h", h))
                if c and c[1]:
                    r[f"avg_demand_mw_h{h:02d}"] = rnd(c[0] / c[1])
        wn = hours_between((y, 1), (y + (ytd_m == 12), ytd_m % 12 + 1), tz)
        su = sum(S[(y, m)][0] for m in range(1, ytd_m + 1) if (y, m) in S)
        cu = sum(S[(y, m)][1] for m in range(1, ytd_m + 1) if (y, m) in S)
        if cu >= NEAR_YEAR * wn and cu:
            r.update(ytd_avg_demand_mw=rnd(su / cu), ytd_hours_used=cu, ytd_hours_in_window=wn)
            best = None
            for m in range(1, ytd_m + 1):
                c = S.get((y, m))
                if c and c[2] is not None and (best is None or c[2] > best[0] or (c[2] == best[0] and c[3] < best[1])):
                    best = (c[2], c[3])
            r["ytd_peak_demand_mw"] = rnd(best[0])
            t["ytd_peak_demand_mw"] = best[1].strftime("%Y-%m-%dT%H:%M:%SZ")
        for m in range(1, 13):
            if (y, m) not in S or (y == newest and m > ytd_m):
                continue
            mn = hours_between((y, m), (y + (m == 12), m % 12 + 1), tz)
            c = S[(y, m)]
            if c[1] < NEAR_YEAR * mn:
                continue
            r[f"avg_demand_mw_m{m:02d}"] = rnd(c[0] / c[1])
            if y < newest:
                for h in range(24):
                    cell = S.get((y, m, h))
                    if cell and cell[1] >= NEAR_CELL * cell[4]:
                        r[f"avg_demand_mw_m{m:02d}_h{h:02d}"] = rnd(cell[0] / cell[1])
        if r:
            out[y], at[y] = r, t
    b = out.get(base, {})
    pct = lambda new, old: round(100 * (new - old) / old, 2)
    for y, r in out.items():
        if y == base:
            continue
        for k, name in (("avg_demand_mw", "avg_demand_growth_since_2019_pct"), ("peak_demand_mw", "peak_demand_growth_since_2019_pct"),
                        ("ytd_avg_demand_mw", "ytd_avg_demand_growth_since_2019_pct"), ("ytd_peak_demand_mw", "ytd_peak_demand_growth_since_2019_pct")):
            if k in r and k in b:
                r[name] = pct(r[k], b[k])
        if "avg_demand_mw" in r and "avg_demand_mw" in out.get(y - 1, {}):
            r["avg_demand_growth_yoy_pct"] = pct(r["avg_demand_mw"], out[y - 1]["avg_demand_mw"])
    whole = [y for y, r in out.items() if "avg_demand_mw" in r]
    if whole and base in whole:
        r = out[max(whole)]
        for k in [k for k in list(r) if k.startswith("avg_demand_mw_")]:
            if k in b:
                r["growth_mw_" + k[14:]] = round(r[k] - b[k], 1)
                r["growth_pct_" + k[14:]] = pct(r[k], b[k])
        for k, name in (("avg_demand_mw", "avg_demand_growth_since_2019_mw"), ("peak_demand_mw", "peak_demand_growth_since_2019_mw")):
            if k in r and k in b:
                r[name] = round(r[k] - b[k], 1)
    nr = out.get(newest, {})
    if newest != base and "ytd_avg_demand_mw" in nr and "ytd_avg_demand_mw" in b:
        nr["ytd_avg_demand_growth_since_2019_mw"] = round(nr["ytd_avg_demand_mw"] - b["ytd_avg_demand_mw"], 1)
    return out, at


def october_hours(path, ba):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(row for row in f if not row.startswith("#"))
        head = next(rd)
        e, vv, t, val = head.index("entity"), head.index("variable"), head.index("ts_utc"), head.index("value")
        for r in rd:
            if r[e] == f"eia930:{ba}" and r[vv] == "demand_mw" and r[val] != "":
                out[parse(r[t].replace("+00:00", "Z")[:19] + "Z")] = float(r[val])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hours")
    ap.add_argument("site")
    ap.add_argument("out")
    ap.add_argument("--october")
    ap.add_argument("--column", default="adjusted_demand")
    ap.add_argument("--no-neighbour", action="store_true")
    ap.add_argument("--base", type=int, default=2019)
    ap.add_argument("--ytd-month", type=int, default=None, help="the year so far's last month; default: from ERCOT's last used hour")
    a = ap.parse_args()
    site = json.load(open(a.site, encoding="utf-8"))
    res, ytd_m = {}, a.ytd_month
    for ba in AREAS:
        octo = october_hours(a.october, ba) if a.october else None
        x = area(f"{a.hours}/{ba}.csv", ba, a.column, octo, a.base, not a.no_neighbour)
        if ytd_m is None:
            end = x["last_used"].astimezone(x["tz"])
            ytd_m = end.month - 1 if (end + H).month == end.month else end.month
        out, at = summarize(x, ytd_m, a.base)
        if ba == "US48":
            for r in out.values():
                for k in [k for k in r if "peak" in k]:
                    del r[k]
            at = {y: {} for y in at}
        res[ba] = dict(years={str(y): r for y, r in out.items()}, at={str(y): t for y, t in at.items()}, screened=x["screened"],
                       band=x["band"], open_fate=x["open_fate"], last_used=x["last_used"].strftime("%Y-%m-%dT%H:%M:%SZ"))
    json.dump(dict(ytd_month=ytd_m, areas=res), open(a.out, "w", encoding="utf-8"), indent=0)
    # compare with the page's file
    same = diff = only_site = only_mine = 0
    lines = []
    for ba, r in res.items():
        sa = site["areas"][ba]
        for y in sorted(set(sa["years"]) | set(r["years"])):
            s, m = sa["years"].get(y, {}), r["years"].get(y, {})
            for k in sorted(set(s) | set(m)):
                if k in s and k in m:
                    if abs(s[k] - m[k]) < 1e-9:
                        same += 1
                    else:
                        diff += 1
                        lines.append(f"DIFF {ba} {y} {k}: page {s[k]} restated {m[k]}")
                elif k in s:
                    only_site += 1
                    lines.append(f"PAGE ONLY {ba} {y} {k}: {s[k]}")
                else:
                    only_mine += 1
                    lines.append(f"RESTATED ONLY {ba} {y} {k}: {m[k]}")
            for k in set(sa["at"].get(y, {})) | set(r["at"].get(y, {})):
                if sa["at"].get(y, {}).get(k) == r["at"].get(y, {}).get(k):
                    same += 1
                else:
                    diff += 1
                    lines.append(f"DIFF {ba} {y} at {k}: page {sa['at'].get(y, {}).get(k)} restated {r['at'].get(y, {}).get(k)}")
        for k in ("blank", "not_positive", "jumps"):
            lines.append(f"SCREEN {ba} {k}: page {sa['screened'][k]} restated {r['screened'][k]}")
        lines.append(f"BAND {ba}: yearly medians {r['band'][0]:.1f} to {r['band'][1]:.1f}; hours whose range test the band leaves open: {r['open_fate']}; last used hour {r['last_used']}")
    print(f"column {a.column}; base {a.base}; ytd month {ytd_m}; neighbour test {'off' if a.no_neighbour else 'on'}; october from API: {'yes' if a.october else 'no'}")
    print(f"values and peak hours: {same} equal, {diff} differ, {only_site} on the page only, {only_mine} restated only")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
