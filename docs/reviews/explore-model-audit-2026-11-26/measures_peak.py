"""Session 10231: the ERCOT peak premium, one rule changed at a time, HB_HUBAVG, 2015 and 2025 (and every whole year
for the definitions that move most). Standard library; the local clock and the percentile of restate_peak.py.

    python measures_peak.py <hubavg.csv> <site/data/forecast/deflator.json>
"""
import datetime as dt
import json
import statistics
import sys

from restate_peak import load_prices, pct

YEARS = list(range(2015, 2026))


def nerc_holidays(y):
    """NERC's six off-peak holidays, a Sunday holiday moved to Monday (New Year's, Memorial Day, Independence Day,
    Labor Day, Thanksgiving, Christmas)."""
    def obs(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31 = dt.date(y, 5, 31)
    memorial = may31 - dt.timedelta(days=(may31.weekday() - 0) % 7)
    sep1 = dt.date(y, 9, 1)
    labor = sep1 + dt.timedelta(days=(0 - sep1.weekday()) % 7)
    nov1 = dt.date(y, 11, 1)
    thanks = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21)
    return {obs(dt.date(y, 1, 1)), memorial, obs(dt.date(y, 7, 4)), labor, thanks, obs(dt.date(y, 12, 25))}


def dst_days(y):
    from restate_peak import nth_sunday
    return {nth_sunday(y, 3, 2), nth_sunday(y, 11, 1)}


def med(v):
    s = sorted(v)
    return pct(s, 50)


def iqr(v):
    s = sorted(v)
    return pct(s, 75) - pct(s, 25)


def premium(rows, peak=(16, 21), mid=(12, 16), keep=lambda l: True):
    K = [x for _, l, x in rows if keep(l) and peak[0] <= l.hour < peak[1]]
    M = [x for _, l, x in rows if keep(l) and mid[0] <= l.hour < mid[1]]
    return med(K) - med(M), iqr(K), med(K), med(M), iqr(M), statistics.fmean(K) - statistics.fmean(M), len(K), len(M)


def daily(rows, peak=(16, 21), mid=(12, 16)):
    """Each local day's peak-block mean less its midday-block mean: the median and the mean over the days."""
    d = {}
    for _, l, x in rows:
        k = l.date()
        s = d.setdefault(k, [[], []])
        if peak[0] <= l.hour < peak[1]:
            s[0].append(x)
        elif mid[0] <= l.hour < mid[1]:
            s[1].append(x)
    diffs = [statistics.fmean(a) - statistics.fmean(b) for a, b in d.values() if a and b]
    return med(diffs), statistics.fmean(diffs), len(diffs), sum(1 for x in diffs if x > 0) / len(diffs)


def f(x):
    return f"{x:,.2f}"


def main():
    rt = load_prices(sys.argv[1], "spp_rtm")
    da = load_prices(sys.argv[1], "spp_dam")
    defl = json.load(open(sys.argv[2], encoding="utf-8"))["index"]
    R = {y: [r for r in rt if r[1].year == y] for y in YEARS}
    D = {y: [r for r in da if r[1].year == y] for y in YEARS}
    print("held: real time", {y: len(R[y]) for y in (2015, 2025)}, "day-ahead hours", {y: len(D[y]) for y in (2015, 2025)})
    base = {y: premium(R[y]) for y in YEARS}
    print("\nBASE (the page): peak median minus midday median; peak IQR; peak median; midday median; midday IQR; mean difference")
    for y in YEARS:
        p = base[y]
        print(f"  {y}: premium {f(p[0])}; peak IQR {f(p[1])}; peak median {f(p[2])}; midday median {f(p[3])}; midday IQR {f(p[4])}; means' difference {f(p[5])}")
    b15, b25 = base[2015], base[2025]
    print(f"\nthe change 2015 to 2025: premium {f(b25[0] - b15[0])} = peak median {f(b25[2] - b15[2])} less midday median {f(b25[3] - b15[3])}")
    print(f"'wider': peak IQR less midday IQR: 2015 {f(b15[1] - b15[4])}, 2025 {f(b25[1] - b25[4])}")

    def row(name, fn):
        a, b = fn(2015), fn(2025)
        print(f"  {name}: premium 2015 {f(a[0])}, 2025 {f(b[0])}; peak IQR 2015 {f(a[1])}, 2025 {f(b[1])}")

    print("\nONE RULE AT A TIME (premium = peak median less midday median; IQR of the peak block)")
    row("the page: peak 16-21, midday 12-16, every day, real time", lambda y: premium(R[y]))
    print(" the peak block's hours")
    for pk in ((17, 21), (18, 22), (19, 21), (15, 20), (16, 20), (17, 20)):
        row(f"peak {pk[0]}:00-{pk[1]}:00", lambda y, pk=pk: premium(R[y], peak=pk))
    print(" the midday block's hours")
    for md in ((10, 15), (11, 15), (12, 15), (13, 16)):
        row(f"midday {md[0]}:00-{md[1]}:00", lambda y, md=md: premium(R[y], mid=md))
    print(" the averaging")
    for y in (2015, 2025):
        p = base[y]
        dm, dmean, nd, share = daily(R[y])
        print(f"  {y}: means (peak mean less midday mean) {f(p[5])}; median of daily differences {f(dm)}; mean of daily differences {f(dmean)}; days {nd}; days with the peak above midday {share * 100:.1f} percent")
    print(" day-ahead against real time (hourly day-ahead prices, blocks by the hour's start)")
    row("day-ahead", lambda y: premium(D[y]))
    for y in (2015, 2025):
        dm, dmean, nd, share = daily(D[y])
        p = premium(D[y])
        print(f"  {y} day-ahead: peak median {f(p[2])}, midday median {f(p[3])}; means' difference {f(p[5])}; median of daily differences {f(dm)}")
    print(" days")
    row("weekdays only", lambda y: premium(R[y], keep=lambda l: l.weekday() < 5))
    row("weekdays, NERC holidays out", lambda y: premium(R[y], keep=lambda l, y=y: l.weekday() < 5 and l.date() not in nerc_holidays(y)))
    row("NERC holidays out only", lambda y: premium(R[y], keep=lambda l, y=y: l.date() not in nerc_holidays(y)))
    row("the two clock-change days out", lambda y: premium(R[y], keep=lambda l, y=y: l.date() not in dst_days(y)))
    row("summer only (June to September)", lambda y: premium(R[y], keep=lambda l: 6 <= l.month <= 9))
    print(" the dollars")
    k = defl["2025"] / defl["2015"]
    print(f"  GDP deflator 2015 to 2025: {defl['2015']} to {defl['2025']}, factor {k:.4f}")
    print(f"  in 2025 dollars, 2015: premium {f(b15[0] * k)}, peak IQR {f(b15[1] * k)}, median all intervals: see the table x {k:.4f}")
    print(f"  peak IQR 2015 to 2025: nominal x{b25[1] / b15[1]:.2f}; in 2025 dollars x{b25[1] / (b15[1] * k):.2f}")
    print(" the industry's on-peak block (06:00 to 22:00 weekdays, NERC holidays off), real time and day-ahead")
    for y in (2015, 2025):
        on = [x for _, l, x in R[y] if l.weekday() < 5 and l.date() not in nerc_holidays(y) and 6 <= l.hour < 22]
        off = [x for _, l, x in R[y] if not (l.weekday() < 5 and l.date() not in nerc_holidays(y) and 6 <= l.hour < 22)]
        ond = [x for _, l, x in D[y] if l.weekday() < 5 and l.date() not in nerc_holidays(y) and 6 <= l.hour < 22]
        print(f"  {y}: real time on-peak mean {f(statistics.fmean(on))}, median {f(med(on))}; off-peak median {f(med(off))}; day-ahead on-peak mean {f(statistics.fmean(ond))}")


if __name__ == "__main__":
    main()
