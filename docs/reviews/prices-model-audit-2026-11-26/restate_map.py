"""Session 10218: an independent restatement of site/data/regions/prices_map.json (the Grid tool map's "Price" colors)
from the page's own hourly files (site/public/board/h/<hub>.json: each hour's day-ahead price to the cent), written from
docs/methods/prices_map.md: the day's mean, on-peak (hours beginning 06:00 to 21:00 local, Monday to Friday, CAISO to
Saturday, NERC holidays off) and off-peak means, four dearest less four cheapest hours, and the mean and share of hours
below zero over the 30 and the 365 local days ending on the day, each only when 95 percent of its hours are held.
Standard library only; the shown grids only (the file holds no figure of another).

    python restate_map.py <site dir>
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

SITE = sys.argv[1]
UTC = dt.timezone.utc
m = json.load(open(os.path.join(SITE, "data", "regions", "prices_map.json"), encoding="utf-8"))


def holidays(y):
    def mon(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31, sep1, nov1 = dt.date(y, 5, 31), dt.date(y, 9, 1), dt.date(y, 11, 1)
    return {mon(dt.date(y, 1, 1)), may31 - dt.timedelta(days=may31.weekday()), mon(dt.date(y, 7, 4)),
            sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7), nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21),
            mon(dt.date(y, 12, 25))}


HOL = set().union(*(holidays(y) for y in range(2024, 2029)))
tot = same = 0
worst = 0.0
lines = []
for h in m["hubs"]:
    ent = h["entity"]
    hid = ent.replace(":", "-").replace("_", "-").replace(".", "-").lower()
    path = os.path.join(SITE, "public", "board", "h", hid + ".json")
    if not os.path.exists(path):
        lines.append(f"{ent}: no hourly file on the page")
        continue
    f = json.load(open(path, encoding="utf-8"))
    tz = ZoneInfo(f["tz"])
    hours = {(f["t0"] + i) * 3600: v for i, v in enumerate(f.get("da") or []) if v is not None}
    d = dt.date.fromisoformat(h["day"])

    def mid(x):
        return int(dt.datetime(x.year, x.month, x.day, tzinfo=tz).timestamp())

    a, b = mid(d), mid(d + dt.timedelta(days=1))
    day = [(s, hours[s]) for s in range(a, b, 3600) if s in hours]
    whole = len(day) == (b - a) // 3600
    sat_ok = ent.startswith("caiso:")
    pk, op = [], []
    for s, v in day:
        loc = dt.datetime.fromtimestamp(s, tz)
        wk = loc.weekday() < 5 or (sat_ok and loc.weekday() == 5)
        (pk if (wk and loc.date() not in HOL and 6 <= loc.hour <= 21) else op).append(v)
    vals = sorted(v for _, v in day)
    got = {"day_avg": sum(vals) / len(vals) if whole else None,
           "day_on_peak": sum(pk) / len(pk) if pk else None, "day_off_peak": sum(op) / len(op) if op else None,
           "day_spread_top4_bottom4": sum(vals[-4:]) / 4 - sum(vals[:4]) / 4}
    for key, n in (("30d", 30), ("12m", 365)):
        wa, wb = mid(d - dt.timedelta(days=n - 1)), b
        w = [hours[s] for s in range(wa, wb, 3600) if s in hours]
        want = (wb - wa) // 3600
        if len(w) >= 0.95 * want:
            got[f"avg_{key}"], got[f"negative_share_{key}_pct"] = sum(w) / len(w), 100 * sum(1 for v in w if v < 0) / len(w)
        else:
            got[f"avg_{key}"] = got[f"negative_share_{key}_pct"] = None
            got[f"why_{key}"] = f"{len(w):,} of {want:,}"
    # the newer whole days the page's own hourly file holds after the map's day
    newer = []
    x = d + dt.timedelta(days=1)
    while mid(x) < max(hours) :
        n_h = sum(1 for s in range(mid(x), mid(x + dt.timedelta(days=1)), 3600) if s in hours)
        if n_h == (mid(x + dt.timedelta(days=1)) - mid(x)) // 3600:
            newer.append(x.isoformat())
        x += dt.timedelta(days=1)
    diffs = []
    for k in ("day_avg", "day_on_peak", "day_off_peak", "day_spread_top4_bottom4", "avg_30d", "negative_share_30d_pct", "avg_12m", "negative_share_12m_pct"):
        tot += 1
        fv, gv = h.get(k), got.get(k)
        if fv is None and gv is None:
            same += 1
            continue
        if fv is None or gv is None:
            diffs.append(f"{k} file {fv} restated {gv} {got.get('why_' + k[-3:], '')}")
            continue
        gap = abs(round(gv, 2) - fv)
        worst = max(worst, gap)
        if gap < 0.005:
            same += 1
        else:
            diffs.append(f"{k} file {fv} restated {round(gv, 2)}")
    lines.append(f"{ent} day {h['day']} ({'whole' if whole else 'NOT whole'}): " + ("all equal" if not diffs else "; ".join(diffs))
                 + f"; newer whole days in the page's hourly file: {newer[:6]}{' ...' if len(newer) > 6 else ''} ({len(newer)})")
print(f"figures compared {tot}, equal to the cent {same}; largest gap {worst:.2f}")
print("\n".join(lines))
# the colors the default view draws: each shown area's day_avg on the scale, green the lowest, red the highest
ba = {k: v for k, v in m["bas"].items() if v.get("state") == "shown"}
for meas in ("day_avg", "day_on_peak", "day_off_peak", "day_spread_top4_bottom4", "avg_30d", "avg_12m", "negative_share_30d_pct", "negative_share_12m_pct"):
    vs = {k: v.get(meas) for k, v in ba.items() if isinstance(v.get(meas), (int, float))}
    if not vs:
        print(f"scale {meas}: no area")
        continue
    lo, hi = min(vs.values()), max(vs.values())
    pos = {k: round((v - lo) / ((hi - lo) or 1), 3) for k, v in vs.items()}
    print(f"scale {meas}: green {lo} to red {hi}; areas colored {len(vs)} of {len(m['bas'])} named; position on the scale {pos}")
