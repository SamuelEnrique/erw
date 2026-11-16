#!/usr/bin/env python3
"""ERW, ERCOT peak premium: every row of the two derived tables recomputed from the 15-minute hub prices
(session 7507, chain 304).

replicate.py traces every figure of /explore/ercot-peak-premium to a row of ercot_peak_premium_annual or
ercot_peak_premium_monthly. This file traces those rows to their source: ERCOT's real-time settlement point prices at
the six trading hubs, every 15-minute interval since 2015, as the warehouse holds them (docs/methods/ercot_peak_premium.md,
"Input" and "Where the input is now"):

  - ercot_all_hub_prices_history.csv, the rows whose market is ercot_rtm (the yearly history, NP6-785-ER);
  - iso_rtm_hub_prices.csv, the rows whose market is ercot_rtm (the live window, NP6-905-CD).

It is written from the note alone, not from warehouse/derived/ercot_peak_premium.py: the local (America/Chicago) year,
month and clock hour in which an interval starts; the three blocks by that hour; minimum, quartiles, median and maximum
by linear interpolation at position (n - 1) * p / 100 of the sorted prices; the 99.9th percentile; the counts; six
decimals. No interval is left out and none is capped. The tables were computed up to their header's "Last input
interval": intervals after it are not used here either, so the partial year and month are recomputed on the same
intervals (--cutoff changes it).

    python replication/ercot_peak_premium/from_hourly.py [--in-dir DIR] [--cutoff 2026-09-28T04:45:00Z] [--means]

--means also prints, for the cross-check of the note (section "Beside published figures"), figures the tables do not
hold: each hub's plain mean of all intervals of each year, and of its peak block. They are printed, never written to a
table. Exit 0 when every row of both tables equals its recomputed value at six decimals, 1 when one does not or a row
is on one side only, 2 when an input cannot be read. Standard library only (zoneinfo needs the tzdata package on Windows).
"""
import argparse
import array
import csv
import datetime
import math
import os
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ANNUAL, MONTHLY = "ercot_peak_premium_annual", "ercot_peak_premium_monthly"
INPUTS = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices"]
CHICAGO = zoneinfo.ZoneInfo("America/Chicago")
UTC = datetime.timezone.utc
BLOCKS = ("overnight", "midday", "peak")
TOL = 0.0000005 + 1e-9      # the tables hold six decimals


def default_dir():
    for d in (os.environ.get("ERW_OUTPUT_DIR"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.isdir(d):
            return d
    return os.path.join(ROOT, "warehouse", "output")


def data_lines(path):
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if not line.startswith("#"):
                yield line


def header_value(path, start):
    """The first comment line of a table that begins with `start`, without it."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return None
            if line[1:].strip().startswith(start):
                return line[1:].strip()[len(start):].strip()
    return None


def block_of(h):
    """The note's table: overnight h >= 21 or h < 12, midday 12 <= h < 16, peak 16 <= h < 21."""
    if 12 <= h < 16:
        return 1
    if 16 <= h < 21:
        return 2
    return 0


def local_of(ts, cache={}):
    """(year, month, block) of the local hour in which the interval that starts at ts (UTC, ISO) starts."""
    key = ts[:13]
    got = cache.get(key)
    if got is None:
        t = datetime.datetime(int(ts[0:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13]), tzinfo=UTC).astimezone(CHICAGO)
        got = cache[key] = (t.year, t.month, block_of(t.hour))
    return got


def percentile(x, p):
    """numpy's default (linear): the sorted values interpolated at position (n - 1) * p / 100."""
    pos = (len(x) - 1) * p / 100.0
    lo = math.floor(pos)
    hi = min(lo + 1, len(x) - 1)
    return x[lo] + (x[hi] - x[lo]) * (pos - lo)


def metrics(blocks):
    """The note's "Metrics" for one hub and one period, from the prices of its three blocks."""
    sets = {name: sorted(blocks[i]) for i, name in enumerate(BLOCKS)}
    sets["all"] = sorted(sets["overnight"] + sets["midday"] + sets["peak"])
    out = {}
    for name, x in sets.items():
        if not x:
            continue
        out[f"{name}_min"], out[f"{name}_max"] = x[0], x[-1]
        out[f"{name}_q1"], out[f"{name}_median"], out[f"{name}_q3"] = percentile(x, 25), percentile(x, 50), percentile(x, 75)
    a = sets["all"]
    out["all_p999"] = percentile(a, 99.9)
    if "peak_q3" in out:
        out["peak_iqr"] = out["peak_q3"] - out["peak_q1"]
    out["all_iqr"] = out["all_q3"] - out["all_q1"]
    if out["all_median"] != 0:
        out["worst_interval_multiple"] = out["all_p999"] / out["all_median"]
    if "peak_median" in out and "midday_median" in out:
        out["peak_minus_midday_median"] = out["peak_median"] - out["midday_median"]
    out["n_scarcity"] = sum(1 for v in a if v >= 1000)
    out["n_negative"] = sum(1 for v in a if v <= 0)
    out["n_intervals"] = len(a)
    return out


def read_prices(in_dir, cutoff):
    """{(hub, year, month): [overnight, midday, peak] arrays of prices}, and the count of rows read and left out."""
    by = {}
    seen = set()
    used = after = twice = 0
    for name in INPUTS:
        rd = csv.reader(data_lines(os.path.join(in_dir, name + ".csv")))
        ix = {k: i for i, k in enumerate(next(rd))}
        e, v, t, val, mk = ix["entity"], ix["variable"], ix["ts_utc"], ix["value"], ix["market"]
        for r in rd:
            if r[mk] != "ercot_rtm" or r[v] != "spp_rtm":
                continue
            ts = r[t]
            if cutoff and ts > cutoff:
                after += 1
                continue
            # the note: no (hub, interval) appears twice. The history is one row an interval; the live window is small
            if name != INPUTS[0]:
                if (r[e], ts) in seen:
                    twice += 1
                    continue
            if ts >= "2026-08":
                seen.add((r[e], ts))
            y, m, b = local_of(ts)
            g = by.get((r[e], y, m))
            if g is None:
                g = by[(r[e], y, m)] = [array.array("d"), array.array("d"), array.array("d")]
            g[b].append(float(r[val]))
            used += 1
    return by, used, after, twice


def read_table(path):
    out = {}
    rd = csv.reader(data_lines(path))
    ix = {k: i for i, k in enumerate(next(rd))}
    for r in rd:
        out[(r[ix["entity"]], r[ix["variable"]], r[ix["ts_utc"]])] = float(r[ix["value"]])
    return out


def recompute(by):
    """The two tables' rows, recomputed: {(hub, variable, label)} -> value, for the months and for the years."""
    monthly, annual = {}, {}
    years = {}
    for (hub, y, m), blocks in by.items():
        for k, x in metrics(blocks).items():
            monthly[(hub, k, f"{y}-{m:02d}-01T00:00:00Z")] = x
        g = years.setdefault((hub, y), [array.array("d"), array.array("d"), array.array("d")])
        for i in range(3):
            g[i].extend(blocks[i])
    for (hub, y), blocks in years.items():
        for k, x in metrics(blocks).items():
            annual[(hub, k, f"{y}-01-01T00:00:00Z")] = x
    return monthly, annual, years


def compare(name, table, mine):
    same, differ, only_table, only_mine = 0, [], [], []
    for key, v in table.items():
        if key not in mine:
            only_table.append(key)
        elif abs(round(mine[key], 6) - v) <= TOL:
            same += 1
        else:
            differ.append((key, v, mine[key]))
    only_mine = [k for k in mine if k not in table]
    print(f"{name}: {same} of {len(table)} rows equal the value recomputed from the 15-minute prices at six decimals; "
          f"{len(differ)} differ; {len(only_table)} of the table have no interval here; {len(only_mine)} recomputed are not in the table")
    for key, v, x in sorted(differ)[:40]:
        print(f"  DIFFERS {key[0]} {key[1]} {key[2][:7]}: the table {v}, recomputed {round(x, 6)}")
    for key in sorted(only_table)[:10]:
        print(f"  ONLY IN THE TABLE {key}")
    for key in sorted(only_mine)[:10]:
        print(f"  ONLY RECOMPUTED {key}")
    return same, len(differ), len(only_table), len(only_mine)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default=default_dir())
    ap.add_argument("--cutoff", default=None)
    ap.add_argument("--means", action="store_true")
    a = ap.parse_args(argv[1:])
    try:
        annual_path = os.path.join(a.in_dir, ANNUAL + ".csv")
        cutoff = a.cutoff
        if cutoff is None:
            line = header_value(annual_path, "Last input interval:") or ""
            cutoff = line.split(";")[0].strip() or None
        by, used, after, twice = read_prices(a.in_dir, cutoff)
        t_annual, t_monthly = read_table(annual_path), read_table(os.path.join(a.in_dir, MONTHLY + ".csv"))
    except (OSError, KeyError, StopIteration, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    print(f"ERCOT peak premium, the derived tables from the 15-minute hub prices in {a.in_dir}")
    print(f"intervals used: {used:,} (hub and interval), up to and including {cutoff}; {after:,} later ones left out; {twice} held twice")
    monthly, annual, years = recompute(by)
    ra = compare(ANNUAL, t_annual, annual)
    rm = compare(MONTHLY, t_monthly, monthly)
    total = len(t_annual) + len(t_monthly)
    print(f"{ra[0] + rm[0]} of {total} rows of the two tables recomputed from the 15-minute prices")
    if a.means:
        print("For the cross-check only (not in a table): hub | year | intervals | mean of all intervals | mean of the peak block | intervals at or above 1,000 | maximum")
        for (hub, y) in sorted(years):
            b = years[(hub, y)]
            n = sum(len(x) for x in b)
            allsum = sum(sum(x) for x in b)
            top = max(max(x) for x in b if len(x))
            sc = sum(1 for x in b for v in x if v >= 1000)
            print(f"  {hub} | {y} | {n} | {allsum / n:.2f} | {sum(b[2]) / len(b[2]):.2f} | {sc} | {top:.2f}")
    bad = ra[1] + ra[2] + ra[3] + rm[1] + rm[2] + rm[3]
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
