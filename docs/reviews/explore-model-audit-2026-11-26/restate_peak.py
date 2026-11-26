"""Session 10231: an independent restatement of the ERCOT peak premium explorer's default view.

Written from docs/methods/ercot_peak_premium.md ("Time-of-day blocks", "Notation", "Metrics"), with the standard library
alone: no numpy, no pandas, no time zone library, nothing of the warehouse's or the site's code. Central time is placed
by the United States' rule since 2007 (the clocks go forward at 02:00 local on the second Sunday of March, 08:00 UTC,
and back at 02:00 daylight time on the first Sunday of November, 07:00 UTC). A percentile is linear at (n - 1) p / 100.

    python restate_peak.py <hubavg.csv> <ercot_peak_premium_annual.csv> <ercot_peak_premium_monthly.csv> <peak_opening.json>

Prints: every annual and monthly row of HB_HUBAVG for 2015 to 2025 against the table, and every keyed figure of the
page's default view (as drawn by site/scripts/peak-premium-figures.mjs) against the restatement written by the page's
rule (two decimals, a tie away from zero; a count whole).
"""
import csv
import datetime as dt
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

HUB = "ercot:HB_HUBAVG"
UTC = dt.timezone.utc


def nth_sunday(y, m, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


DST = {}


def local(t):
    """The America/Chicago wall time of a UTC moment."""
    y = t.year
    if y not in DST:
        a = nth_sunday(y, 3, 2)
        b = nth_sunday(y, 11, 1)
        DST[y] = (dt.datetime(a.year, a.month, a.day, 8, tzinfo=UTC), dt.datetime(b.year, b.month, b.day, 7, tzinfo=UTC))
    a, b = DST[y]
    off = -5 if a <= t < b else -6
    return (t + dt.timedelta(hours=off)).replace(tzinfo=None)


def pct(sorted_v, p):
    n = len(sorted_v)
    pos = (n - 1) * p / 100.0
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    return sorted_v[lo] + (sorted_v[hi] - sorted_v[lo]) * (pos - lo)


def block(h):
    if 16 <= h < 21:
        return "peak"
    if 12 <= h < 16:
        return "midday"
    return "overnight"


def five(v):
    s = sorted(v)
    return {"min": s[0], "q1": pct(s, 25), "median": pct(s, 50), "q3": pct(s, 75), "max": s[-1]}, s


def metrics(items):
    """items: list of (local hour, price). The note's table of variables."""
    out = {}
    by = {"overnight": [], "midday": [], "peak": []}
    for h, x in items:
        by[block(h)].append(x)
    for b, v in by.items():
        f, _ = five(v)
        for k, x in f.items():
            out[f"{b}_{k}"] = x
    allv = [x for _, x in items]
    f, s = five(allv)
    for k, x in f.items():
        out[f"all_{k}"] = x
    ks = sorted(by["peak"])
    ms = sorted(by["midday"])
    out["all_p999"] = pct(s, 99.9)
    out["peak_iqr"] = pct(ks, 75) - pct(ks, 25)
    out["all_iqr"] = pct(s, 75) - pct(s, 25)
    out["worst_interval_multiple"] = out["all_p999"] / pct(s, 50)
    out["peak_minus_midday_median"] = pct(ks, 50) - pct(ms, 50)
    out["n_scarcity"] = float(sum(1 for x in allv if x >= 1000))
    out["n_negative"] = float(sum(1 for x in allv if x <= 0))
    out["n_intervals"] = float(len(allv))
    return out


def load_prices(path, var="spp_rtm"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["variable"] != var:
                continue
            t = dt.datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            rows.append((t, local(t), float(r["value"])))
    rows.sort()
    return rows


def load_table(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["entity"] == HUB:
                out[(r["variable"], r["ts_utc"])] = float(r["value"])
    return out


def text(v, unit):
    if unit == "count":
        return f"{int(round(v)):,}"
    q = Decimal(repr(round(v, 6))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{q:,.2f}"


def main():
    prices, annual_f, monthly_f, opening_f = sys.argv[1:5]
    rows = load_prices(prices)
    years = {}
    months = {}
    for t, l, x in rows:
        if 2015 <= l.year <= 2025:
            years.setdefault(l.year, []).append((l.hour, x))
            months.setdefault((l.year, l.month), []).append((l.hour, x))
    A = load_table(annual_f)
    M = load_table(monthly_f)
    restated = {}
    eq = tot = 0
    worst = (0.0, None)
    for y, items in sorted(years.items()):
        m = metrics(items)
        for k, v in m.items():
            restated[("annual", k, y)] = v
            ts = f"{y}-01-01T00:00:00Z"
            if (k, ts) in A:
                tot += 1
                d = abs(round(v, 6) - A[(k, ts)])
                if d < 5e-7:
                    eq += 1
                elif d > worst[0]:
                    worst = (d, (k, y, v, A[(k, ts)]))
    print(f"annual rows of HB_HUBAVG 2015 to 2025 equal at six decimals: {eq} of {tot}; worst {worst}")
    eq = tot = 0
    worst = (0.0, None)
    for (y, mo), items in sorted(months.items()):
        m = metrics(items)
        for k, v in m.items():
            restated[("monthly", k, y, mo)] = v
            ts = f"{y}-{mo:02d}-01T00:00:00Z"
            if (k, ts) in M:
                tot += 1
                d = abs(round(v, 6) - M[(k, ts)])
                if d < 5e-7:
                    eq += 1
                elif d > worst[0]:
                    worst = (d, (k, y, mo, v, M[(k, ts)]))
    print(f"monthly rows of HB_HUBAVG 2015 to 2025 equal at six decimals: {eq} of {tot}; worst {worst}")
    # interval counts and the daylight saving days
    for y in (2015, 2025):
        print(f"{y}: intervals {len(years[y])}; peak {sum(1 for h, _ in years[y] if 16 <= h < 21)}, midday {sum(1 for h, _ in years[y] if 12 <= h < 16)}, overnight {sum(1 for h, _ in years[y] if h >= 21 or h < 12)}")
        days = {}
        for t, l, x in rows:
            if l.year == y:
                days[l.date()] = days.get(l.date(), 0) + 1
        odd = {str(d): n for d, n in days.items() if n != 96}
        print(f"  days not of 96 intervals: {odd}")
    # the page's default view, as drawn
    op = json.load(open(opening_f, encoding="utf-8"))
    view = op["views"][0]
    print(f"default view: {view['q']} keyed figures {view['keyed']}; headline labels {view['headline_labels']}")
    good = 0
    bad = []
    for key in view["keys"]:
        _, table, ent, var, ts = key.split("|")
        y = int(ts[:4])
        unit = "count" if var.startswith("n_") else "USD"
        v = restated[("annual", var, y)] if table.endswith("annual") else restated[("monthly", var, y, int(ts[5:7]))]
        shown = op["keyed"][key]["text"]
        mine = text(v, unit)
        if mine == shown:
            good += 1
        else:
            bad.append((key, shown, mine, v))
    print(f"default view: {good} of {len(view['keys'])} drawn figures equal the restatement as written; differing: {bad}")
    print("the default view, figure by figure (page text):")
    seen = set()
    for key in view["keys"]:
        if key in seen:
            continue
        seen.add(key)
        print("  ", key.split("|", 3)[3], op["keyed"][key]["text"])


if __name__ == "__main__":
    main()
