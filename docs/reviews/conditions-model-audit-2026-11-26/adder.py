"""Session 10219: ERCOT's online reserve adder (rtorpa_mean, hourly) against /conditions' scarcity strip.

argv: worktree, output folder (read only), out JSON. Standard library only.
  1. Every daily adder_hours and adder_max in the page file restated from the table (Central local days).
  2. The hours above zero by size of the adder, and how many show as 0.0 on the page's hourly chart (one decimal).
  3. The glance figure "Most hours with the adder above zero in a day" in each event window, against the same count at
     USD 1 and USD 100 (the level the datacenter page uses), and in the page's twelve months to its end.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT, OUTDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CT = ZoneInfo("America/Chicago")
hours = {}
with open(os.path.join(OUTDIR, "ercot_rtm_price_adders.csv"), encoding="utf-8", newline="") as fh:
    rd = csv.reader(ln for ln in fh if not ln.startswith("#"))
    head = next(rd)
    iv, it, ix = head.index("variable"), head.index("ts_utc"), head.index("value")
    for r in rd:
        if r[iv] == "rtorpa_mean":
            hours[r[it]] = float(r[ix])
by_day = defaultdict(list)
for ts, v in hours.items():
    t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(CT)
    by_day[t.strftime("%Y-%m-%d")].append(v)
with open(os.path.join(ROOT, "site", "data", "conditions", "ercot.json"), encoding="utf-8") as fh:
    f = json.load(fh)
dc = f["daily_columns"]
ih, im = dc.index("adder_hours"), dc.index("adder_max")
checked = same = 0
differ = []
for r in f["daily"]:
    if r[ih] is None:
        if r[0] in by_day:
            differ.append((r[0], "file none", len(by_day[r[0]])))
        continue
    vals = by_day.get(r[0], [])
    n = sum(1 for v in vals if v > 0)
    mx = round(max(vals), 1) if vals else None
    checked += 2
    same += (n == r[ih]) + (mx == r[im])
    if n != r[ih] or mx != r[im]:
        differ.append((r[0], r[ih], n, r[im], mx))
win = [v for ts, v in hours.items() if ts >= "2018-07-01"]
bands = [("0", lambda v: v <= 0), ("above 0, under 0.05 (0.0 on the chart)", lambda v: 0 < v < 0.05),
         ("0.05 to 1", lambda v: 0.05 <= v < 1), ("1 to 10", lambda v: 1 <= v < 10), ("10 to 100", lambda v: 10 <= v < 100),
         ("100 to 1,000", lambda v: 100 <= v < 1000), ("1,000 and above", lambda v: v >= 1000)]
band_all = {name: sum(1 for v in hours.values() if fn(v)) for name, fn in bands}
band_win = {name: sum(1 for v in win if fn(v)) for name, fn in bands}
pos = [v for v in hours.values() if v > 0]
pos.sort()
med = pos[len(pos) // 2] if pos else None


def glance(start, end, level):
    best = None
    for d in sorted(by_day):
        if start <= d <= end:
            n = sum(1 for v in by_day[d] if (v > 0 if level == 0 else v >= level))
            if best is None or n > best[1]:
                best = (d, n)
    return best


evs = [w for w in f["windows"] if w["id"] != "recent"]
gl = {w["id"]: {"above_0": glance(w["start"], w["end"], 0), "at_1": glance(w["start"], w["end"], 1), "at_100": glance(w["start"], w["end"], 100),
               "hours_above_0": sum(1 for d in by_day if w["start"] <= d <= w["end"] for v in by_day[d] if v > 0),
               "hours_at_1": sum(1 for d in by_day if w["start"] <= d <= w["end"] for v in by_day[d] if v >= 1),
               "hours_at_100": sum(1 for d in by_day if w["start"] <= d <= w["end"] for v in by_day[d] if v >= 100)} for w in evs}
years = {}
for y in range(2018, 2026):
    vs = [v for ts, v in hours.items() if ts[:4] == str(y) and ts >= "2018-07-01"]
    years[y] = {"hours": len(vs), "above_0": sum(1 for v in vs if v > 0), "at_1": sum(1 for v in vs if v >= 1), "at_100": sum(1 for v in vs if v >= 100)}
res = {"hours_held": len(hours), "first": min(hours), "last": max(hours), "daily_checked": checked, "daily_same": same,
       "daily_differ": differ[:20], "n_differ": len(differ), "bands_all": band_all, "bands_since_2018_07": band_win,
       "median_positive": med, "glance_by_event": gl, "years": years}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("glance_by_event",)}, indent=1))
for k, v in gl.items():
    print(k, v)
