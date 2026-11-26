"""Session 10231: the peak premium weighted by load, HB_HUBAVG, 2015 and 2025. Each 15-minute real-time price is weighted
by ERCOT's own system load of its hour (ercot_zone_load_hourly, entity ercot:system, read only from the main copy),
as the market monitor weights its averages. Prints the plain and load-weighted means of the peak and midday blocks,
the load-weighted median of each block, and the load-weighted mean of all intervals.

    python measures_load.py <hubavg.csv> <ercot_zone_load_hourly.csv>
"""
import csv
import datetime as dt
import sys

from restate_peak import load_prices, local

UTC = dt.timezone.utc


def wmedian(pairs):
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)
    acc = 0.0
    for x, w in pairs:
        acc += w
        if acc >= tot / 2:
            return x


def main():
    rt = [r for r in load_prices(sys.argv[1]) if r[1].year in (2015, 2025)]
    load = {}
    with open(sys.argv[2], newline="", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["entity"] != "ercot:system":
                continue
            ts = r["ts_utc"]
            if not (ts.startswith("2015") or ts.startswith("2025") or ts.startswith("2016-01-01") or ts.startswith("2026-01-01")):
                continue
            load[dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)] = float(r["value"])
    for y in (2015, 2025):
        blocks = {"peak": [], "midday": [], "all": []}
        missing = 0
        for t, l, x in rt:
            if l.year != y:
                continue
            w = load.get(t.replace(minute=0))
            if w is None:
                missing += 1
                continue
            blocks["all"].append((x, w))
            if 16 <= l.hour < 21:
                blocks["peak"].append((x, w))
            elif 12 <= l.hour < 16:
                blocks["midday"].append((x, w))
        def wmean(p):
            return sum(x * w for x, w in p) / sum(w for _, w in p)
        def mean(p):
            return sum(x for x, _ in p) / len(p)
        pk, md = blocks["peak"], blocks["midday"]
        print(f"{y}: intervals without a load hour {missing}")
        print(f"  plain means: peak {mean(pk):.2f}, midday {mean(md):.2f}, difference {mean(pk) - mean(md):.2f}; all {mean(blocks['all']):.2f}")
        print(f"  load-weighted means: peak {wmean(pk):.2f}, midday {wmean(md):.2f}, difference {wmean(pk) - wmean(md):.2f}; all {wmean(blocks['all']):.2f}")
        print(f"  load-weighted medians: peak {wmedian(pk):.2f}, midday {wmedian(md):.2f}, difference {wmedian(pk) - wmedian(md):.2f}")


if __name__ == "__main__":
    main()
