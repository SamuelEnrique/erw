#!/usr/bin/env python3
"""The hours behind "What a datacenter pays", as one CSV, for replication (session 190).

Energy Research Warehouse (ERW). The page /cost-of-power computes every cost figure on the server, on each request,
from its own files of hourly prices (site/data/datacenter, written by warehouse/derived/datacenter_page.py) with
site/lib/datacenter.ts. This script writes the hours of the page's default case, one row an hour, so that a reader can
rebuild every headline number of the default page without the page:

    site/public/datacenter/erw_2026_datacenter_hourly.csv

The default case is the page's own (site/lib/datacenter.ts, inputsOf with no query): ERCOT, the North load zone
LZ_NORTH, a flat load of 100 MW, bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56. The file is per MW of
load, as the page's library is; the page scales by the reader's size. The window is every hour the page's files hold
of LZ_NORTH in real time, from the first to the last. Beside the real-time price stand the zone's day-ahead price (what
a flexible load decides from, and what the same load pays buying day-ahead) and the real-time price of the trading hub
the page shows beside the zone (HB_NORTH). The column in_last_twelve marks the page's last twelve months.

Nothing is estimated and nothing is modelled. The hours are read from the page's files as they are, and the script
refuses to write unless, recomputed from the rows as they are written (their text):

    (a) the hours run unbroken from the first to the last, and each hour's three prices are the files' own, to the
        cent, with the sentinel exactly where a file holds no price;
    (b) every month's hours held and sum of prices, for each of the three series, equal the months the page computes
        (this file's months_of, the Python of lib/datacenter.ts monthsOfYear for a flat load);
    (c) in_last_twelve marks the page's last twelve months, whole and nothing else.

    python warehouse/derived/datacenter_hourly_export.py
    python warehouse/derived/datacenter_hourly_export.py --out C:/scratch/trial.csv
    python warehouse/derived/datacenter_hourly_export.py --tables C:/.../warehouse/output    # also set against the tables

It reads committed files only (the page's files, and warehouse/metadata/coverage.csv for each table's last run), so it
runs on any machine: no table of warehouse/output is needed, none is written, no request is made and no data lock is
taken. With --tables it also sets every hour of the file against the price tables as they stand in that directory
(read only): the day-ahead price as the table holds it, and for real time the mean of the hour's four 15-minute
prices, held only when all four rows are there. That check is a report (--report names its file) and its exit code;
the CSV is written from the page's files either way. Method: docs/methods/datacenter_pays_algorithm.md.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV_NAME = "erw_2026_datacenter_hourly.csv"
OUT = os.path.join(ROOT, "site", "public", "datacenter", CSV_NAME)
SITE_DIR = os.path.join(ROOT, "site", "data", "datacenter")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
GRID, REGION, BUY = "ercot", "LZ_NORTH", "rt"    # the page's defaults (lib/datacenter.ts inputsOf; the index's main region)
MW, GPU_KW, PUE = 100, 1.3, 1.56                  # lib/datacenter.ts DEFAULTS and ASSUMED
NEAR = 0.95                                       # lib/datacenter.ts NEAR: a month counts with this share of its hours
HEADER_LINES = 15                                 # the do-file reads the column names from line 16
SENTINEL = -99999                                 # a price column: the hour's price is not held
COLUMNS = ["hour_utc", "std_month", "rt_usd_mwh", "da_usd_mwh", "hub_rt_usd_mwh", "in_last_twelve"]
SERIES = ["rt", "da", "hub"]                      # the three price columns, in the order of COLUMNS
TOL_SUM = 1e-6                                    # a month's sum of prices: the rows hold cents, as the files do
TOL_TABLE = 0.005 + 1e-9                          # an hour against the tables: the files hold the price to the cent
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ISO = "%Y-%m-%dT%H:%M:%SZ"
# header lines that move while no hour of the default case does: the export's own time; the build stamp of the page's
# files (the weekly refresh rewrites the index for other regions); each table's last run (the daily run moves it)
VOLATILE = ("# Exported: ", "# Read from the page's own files: ", "# Last run (UTC) of each table")


# ---------------------------------------------------------------------------------------------------------------------
# the page's arithmetic for a flat load, in Python (site/lib/datacenter.ts; tests/test_session190_replication.py sets
# it beside node on the library itself)
# ---------------------------------------------------------------------------------------------------------------------

def leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def hours_in(y):
    return 8784 if leap(y) else 8760


def month_starts(y):
    """The first hour of each month of a year, and the year's end: thirteen indexes (lib: monthStarts)."""
    out = [0]
    for m in range(12):
        out.append(out[m] + 24 * (DAYS[m] + (1 if m == 1 and leap(y) else 0)))
    return out


def prev_month(m, k):
    """The month k months before m (YYYY-MM)."""
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def expand(f, region, buy):
    """A year's prices at one region and market, one entry an hour of the year, None where not held (lib: expand)."""
    out = [None] * f["hours"]
    s = f["regions"].get(region, {}).get(buy)
    if s:
        for i, v in enumerate(s["v"]):
            out[s["s"] + i] = v
    return out


def months_of(years):
    """Every month held of a flat load, oldest first (lib: monthsOfYear with every weight 1). `years`: {year: the
    year's hourly prices}. A month: m, due (its calendar hours), held, flat (the sum of the prices held, USD per MW),
    complete (held at least NEAR of due)."""
    out = []
    for y in sorted(years):
        st, p = month_starts(y), years[y]
        for m in range(12):
            vals = [v for v in p[st[m]:st[m + 1]] if v is not None]
            if not vals:
                continue
            due = st[m + 1] - st[m]
            out.append(dict(m=f"{y}-{m + 1:02d}", due=due, held=len(vals), flat=math.fsum(vals), complete=len(vals) >= NEAR * due))
    return out


def last_twelve(ms):
    """The last twelve consecutive complete months, oldest first; None when no twelve are held (lib: lastTwelve)."""
    by = {r["m"]: r for r in ms}
    for r in reversed(ms):
        if not r["complete"]:
            continue
        twelve = [by.get(prev_month(r["m"], k)) for k in range(12)]
        if all(t and t["complete"] for t in twelve):
            return twelve[::-1]
    return None


def last36(ms):
    """The complete months of the 36 that end with the last twelve months (lib: last36)."""
    done = [r for r in ms if r["complete"]]
    if not done:
        return None
    l12 = last_twelve(ms)
    to = (l12[11] if l12 else done[-1])["m"]
    frm = prev_month(to, 35)
    return dict(frm=frm, to=to, months=[r for r in done if frm <= r["m"] <= to])


def bad_month(ms):
    """The month at the top tenth by cost per MWh, nearest rank (lib: badMonth; a flat load's energy is its hours)."""
    ranked = sorted((r for r in ms if r["complete"] and r["held"] > 0), key=lambda r: (-(r["flat"] / r["held"]), r["m"]))
    return ranked[max(0, math.ceil(0.1 * len(ranked)) - 1)] if ranked else None


def span(ms):
    held, flat = sum(r["held"] for r in ms), math.fsum(r["flat"] for r in ms)
    return dict(months=len(ms), held=held, due=sum(r["due"] for r in ms), cost=flat, per=flat / held if held else None)


# ---------------------------------------------------------------------------------------------------------------------
# the page's files
# ---------------------------------------------------------------------------------------------------------------------

def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha_of(path):
    """The sha256 of a file's bytes with LF line ends."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def fmt(v):
    """A price as the CSV writes it: to the cent, trailing zeros dropped, never an exponent, never minus zero."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def hour_utc(y, i, std):
    """The UTC start of hour i of year y in a grid's standard time."""
    return dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(hours=i + std)


def page_facts(site_dir=SITE_DIR):
    """What the page's own files hold for the default case, and what the page computes from them: the three series by
    year, each one's months, the last twelve months, the 36, the bad month and the hub beside the zone. No table is read."""
    index = read_json(os.path.join(site_dir, "index.json"))
    g = index["grids"][GRID]
    if g["main"] != REGION:
        raise RuntimeError(f"the index names {g['main']} as {GRID}'s default region, this export is written for {REGION}: nothing written")
    region = next(r for r in g["regions"] if r["id"] == REGION)
    ref = region.get("ref")
    if not ref or BUY not in region:
        raise RuntimeError(f"{REGION} holds no real-time price or names no hub beside it: nothing written")
    files = {y: read_json(os.path.join(site_dir, f"{GRID}_{y}.json")) for y in g["years"]}
    series = {"rt": {y: expand(f, REGION, "rt") for y, f in files.items()}, "da": {y: expand(f, REGION, "da") for y, f in files.items()},
              "hub": {y: expand(f, ref, "rt") for y, f in files.items()}}
    months = {k: months_of(v) for k, v in series.items()}
    l12 = last_twelve(months["rt"])
    if l12 is None:
        raise RuntimeError(f"the page's files hold no twelve complete months in a row of {REGION} in real time: nothing written")
    names = [r["m"] for r in l12]
    hub12 = [r for r in months["hub"] if names[0] <= r["m"] <= names[-1] and r["complete"]]
    da12 = [r for r in months["da"] if r["m"] in names and r["complete"]]
    w36 = last36(months["rt"])
    return dict(index=index, grid=g, region=region, ref=ref, std=g["std_hours_behind_utc"], files=files, series=series, months=months, l12=names,
                s12=span(l12), w36=w36, bad=bad_month(w36["months"]), hub12=span(hub12) if len(hub12) == 12 else None,
                da12=span(da12) if len(da12) == 12 and last_twelve(months["da"]) and [r["m"] for r in last_twelve(months["da"])] == names else None,
                site_dir=site_dir)


def build(facts):
    """The rows of the window: every hour from the first to the last hour held of the default region's real-time price."""
    std, rows = facts["std"], []
    held = [(y, i) for y in sorted(facts["series"]["rt"]) for i, v in enumerate(facts["series"]["rt"][y]) if v is not None]
    if not held:
        return rows
    first, last = held[0], held[-1]
    for y in sorted(facts["series"]["rt"]):
        st = month_starts(y)
        month_of = [m for m in range(12) for _ in range(st[m + 1] - st[m])]
        for i in range(hours_in(y)):
            if (y, i) < first or (y, i) > last:
                continue
            m = f"{y}-{month_of[i] + 1:02d}"
            rows.append(dict(hour_utc=hour_utc(y, i, std).strftime(ISO), std_month=m, rt=facts["series"]["rt"][y][i], da=facts["series"]["da"][y][i],
                             hub=facts["series"]["hub"][y][i], in_last_twelve=int(m in facts["l12"])))
    return rows


def render(rows):
    """The data lines of the CSV, as text."""
    return [",".join([r["hour_utc"], r["std_month"]] + [str(SENTINEL) if r[k] is None else fmt(r[k]) for k in SERIES] + [str(r["in_last_twelve"])]) for r in rows]


def months_of_lines(lines):
    """Each month recomputed from the CSV's own text, for each of the three series: hours held and the sum of the
    prices; with the flags seen and the hours' values by UTC hour. This is what a reader of the file has."""
    months, hours = {}, {}
    for line in lines:
        hour, month, rt, da, hub, flag = line.split(",")
        vals = dict(rt=float(rt), da=float(da), hub=float(hub))
        hours[hour] = vals
        m = months.setdefault(month, dict(rows=0, flags=set(), **{k: [] for k in SERIES}))
        m["rows"] += 1
        m["flags"].add(flag)
        for k in SERIES:
            if vals[k] != SENTINEL:
                m[k].append(vals[k])
    return months, hours


def agree(lines, facts):
    """(a), (b) and (c) from the CSV's own text (its data lines) and page_facts(). The list of differences, empty when
    the file is the page's own data, hour by hour; and the months recomputed."""
    months, hours = months_of_lines(lines)
    bad, std = [], facts["std"]
    # (a) the hours, unbroken, and each one's three prices
    stamps = sorted(hours)
    if len(stamps) != len(lines):
        bad.append(f"{len(lines) - len(stamps)} rows repeat an hour")
    if stamps:
        a, b = (dt.datetime.strptime(s, ISO).replace(tzinfo=dt.timezone.utc) for s in (stamps[0], stamps[-1]))
        due = int((b - a).total_seconds() // 3600) + 1
        if due != len(stamps):
            bad.append(f"hours: {len(stamps)} rows between {stamps[0]} and {stamps[-1]}, which span {due} hours")
    seen, n_bad = 0, 0
    for y in sorted(facts["series"]["rt"]):
        for i in range(hours_in(y)):
            want = {k: facts["series"][k][y][i] for k in SERIES}
            got = hours.get(hour_utc(y, i, std).strftime(ISO))
            if got is None:
                if want["rt"] is not None:
                    n_bad += 1
                    if n_bad <= 20:
                        bad.append(f"hour {hour_utc(y, i, std).strftime(ISO)}: the page's files hold a real-time price, the rows hold no such hour")
                continue
            seen += 1
            for k in SERIES:
                w = SENTINEL if want[k] is None else want[k]
                if abs(got[k] - w) > 1e-9:
                    n_bad += 1
                    if n_bad <= 20:
                        bad.append(f"hour {hour_utc(y, i, std).strftime(ISO)} {k}: the row holds {got[k]}, the page's file {want[k]}")
    if seen != len(hours):
        bad.append(f"{len(hours) - seen} rows lie outside the years of the page's files")
    if n_bad > 20:
        bad.append(f"and {n_bad - 20} more hours that are not the page's files'")
    # (b) every month, for each series
    for k in SERIES:
        want = {r["m"]: r for r in facts["months"][k] if r["m"] in months}
        for m in sorted(months):
            got, w = months[m][k], want.get(m)
            if w is None:
                if got:
                    bad.append(f"month {m} {k}: {len(got)} hours in the rows, none in the page's files")
                continue
            # the first and the last month of the window hold the zone's hours only as far as the window runs
            if len(got) != w["held"] and not (k != "rt" and m in (min(months), max(months))):
                bad.append(f"month {m} {k} hours: the rows hold {len(got)}, the page's files {w['held']}")
            elif len(got) == w["held"] and abs(math.fsum(got) - w["flat"]) > TOL_SUM:
                bad.append(f"month {m} {k} sum of prices: the rows give {math.fsum(got):.6f}, the page's files {w['flat']:.6f}")
    # (c) the flag marks the twelve months, whole
    flagged = sorted(m for m, v in months.items() if v["flags"] == {"1"})
    if flagged != facts["l12"] or any(len(v["flags"]) != 1 for v in months.values()):
        bad.append(f"in_last_twelve marks {flagged[:1]} to {flagged[-1:]}, the page's last twelve months are {facts['l12'][0]} to {facts['l12'][-1]}")
    return bad, months


def last_runs(tables):
    """Each table's last run and license as warehouse/metadata/coverage.csv states them (a committed file)."""
    with open(COVERAGE, encoding="utf-8", newline="") as f:
        cov = {r["table"]: r for r in csv.DictReader(f)}
    return {t: (cov[t]["last_run"], cov[t]["license"], cov[t]["source_report"]) if t in cov else ("not stated", "not stated", "not stated") for t in tables}


def head_lines(rows, facts, months, run_at):
    region, ref, index = facts["region"], facts["ref"], facts["index"]
    hub = next(r for r in facts["grid"]["regions"] if r["id"] == ref)
    zone_tables, hub_tables = sorted(set(region["rt"]["tables"]) | set(region["da"]["tables"])), sorted(hub["rt"]["tables"])
    runs = last_runs(zone_tables + [t for t in hub_tables if t not in zone_tables])
    internal = [t for t, (_, lic, _) in runs.items() if lic != "public"]
    if internal:
        raise RuntimeError(f"a table behind the default case is not public in coverage.csv ({', '.join(internal)}): nothing written")
    l12, n_miss = facts["l12"], {k: sum(1 for r in rows if r[k] is None) for k in SERIES}
    counted = sum(1 for r in facts["months"]["rt"] if r["complete"] and r["m"] in months)
    years = sorted(facts["files"])
    head = [
        "Energy Research Warehouse (ERW): the hours behind What a datacenter pays; the default case of /cost-of-power (session 190)",
        f"Case: ERCOT; the North load zone {REGION}; a flat load; bought in real time; per 1 MW of load (the page's default size is {MW} MW). "
        "A zone price is an average over many points: not a site",
        f"Window: every hour from {rows[0]['hour_utc']} to {rows[-1]['hour_utc']}: the first to the last hour the page's files hold of {REGION} in real time. "
        f"in_last_twelve = 1 marks {l12[0]} to {l12[-1]}: the page's last twelve months",
        f"Rows: one per hour of the window ({len(rows)} rows); hour_utc is the hour's start. Hours are counted in US Central standard time all year "
        f"(UTC less {facts['std']} hours; no daylight saving shift): std_month is the hour's month on that clock; every day has 24 hours",
        f"rt_usd_mwh: the real-time settlement point price of {REGION} in USD per MWh; the mean of the hour's four 15-minute prices; held only when "
        "all four are; to the cent",
        f"da_usd_mwh: the day-ahead settlement point price of {REGION} for the hour in USD per MWh. hub_rt_usd_mwh: the real-time price of the trading "
        f"hub the page shows beside the zone ({ref}); made as rt_usd_mwh is",
        f"Sentinel: {SENTINEL} in rt_usd_mwh or da_usd_mwh or hub_rt_usd_mwh means the price of that hour is not held "
        f"({n_miss['rt']} and {n_miss['da']} and {n_miss['hub']} hours in this file); such an hour is in no sum and is never filled",
        "The page's arithmetic: a flat load pays the mean of the hourly prices held; a month counts when at least "
        f"{NEAR:.2f} of its calendar hours are held; the last twelve months are the newest twelve counted months in a row; a bad month is the month at "
        "the top tenth by cost per MWh (nearest rank) of the counted months among the 36 that end with the last twelve",
        f"Source tables (ERW; warehouse/output): {REGION} from {'; '.join(zone_tables)} (ERCOT NP4-180-ER day-ahead and NP6-785-ER real time); "
        f"{ref} from {'; '.join(hub_tables)} (the same two reports; and ERCOT NP6-905-CD for the newest days)",
        "Last run (UTC) of each table as warehouse/metadata/coverage.csv stated it at export: " + "; ".join(f"{t} {runs[t][0]}" for t in runs),
        f"Read from the page's own files: site/data/datacenter/index.json (built {index['built']}; sha256 {sha_of(os.path.join(facts['site_dir'], 'index.json'))[:16]}) "
        f"and {GRID}_{years[0]}.json to {GRID}_{years[-1]}.json; written by warehouse/derived/datacenter_page.py "
        f"(sha256 {sha_of(os.path.join(HERE, 'datacenter_page.py'))[:16]}). No table is read at export",
        f"Check at export; from these rows as written: every hour's three prices are the files' own; each of {len(months)} months gives the hours held "
        f"and the sum of prices the page computes ({counted} months counted); in_last_twelve marks the page's twelve months",
        f"Exported: {run_at} (UTC) by warehouse/derived/datacenter_hourly_export.py. Method: "
        "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_pays_algorithm.md",
        "License: public. Derived by the ERW from ERCOT's public prices (https://www.ercot.com/help/terms). Wholesale energy only: no delivery; no "
        "ancillary or capacity charge; no retail margin; no tax. Not a forecast; not what any customer paid",
        f"Stata: import delimited using {CSV_NAME}; delimiter(comma) varnames({HEADER_LINES + 1}) rowrange({HEADER_LINES + 2}) stringcols(_all). "
        "These comment lines hold no comma and no double quote",
    ]
    if len(head) != HEADER_LINES:
        raise RuntimeError(f"the header holds {len(head)} lines, the do-file expects {HEADER_LINES}")
    for line in head:
        if "," in line or '"' in line or "\n" in line:
            raise RuntimeError(f"a header line holds a comma, a quote or a line break: {line[:80]}")
    return head


def write(head, lines, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for line in head:
            f.write("# " + line + "\n")
        f.write(",".join(COLUMNS) + "\n")
        for line in lines:
            f.write(line + "\n")
    os.replace(out + ".tmp", out)
    return os.path.getsize(out)


def same_data(out, head, lines):
    """True when the file already written holds these rows and this header but for the three lines of VOLATILE: a run
    that changes no hour of the default case leaves the file, and those three lines, as they are."""
    if not os.path.exists(out):
        return False
    with open(out, encoding="utf-8", newline="") as f:
        had = f.read().split("\n")
    keep = lambda rows: [r for r in rows if not r.startswith(VOLATILE)]  # noqa: E731
    return keep(had) == keep(["# " + h for h in head] + [",".join(COLUMNS)] + lines + [""])


# ---------------------------------------------------------------------------------------------------------------------
# --tables: every hour of the file against the price tables as they stand (read only; the data machine, or another
# copy's warehouse/output). An independent read: plain text, no pandas, none of the builder's functions.
# ---------------------------------------------------------------------------------------------------------------------

def table_rows(path, entity, market):
    """{interval start (UTC, as the table writes it): its value as text} for one settlement point and market of a price
    table, read as text; and the number of rows that repeat an interval."""
    out, cols, repeats = {}, None, 0
    needle = f"ercot:{entity},"
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if line.startswith("#"):
                continue
            if cols is None:
                cols = line.strip().split(",")
                i_e, i_t, i_v, i_m = (cols.index(c) for c in ("entity", "ts_utc", "value", "market"))
                continue
            if not line.startswith(needle):
                continue
            c = next(csv.reader([line]))
            if c[i_e] != f"ercot:{entity}" or c[i_m] != market:
                continue
            if c[i_t] in out:
                repeats += 1
            out[c[i_t]] = c[i_v]
    return out, repeats


def check_tables(lines, facts, tables_dir, log):
    """Each hour of the CSV against the tables: day-ahead as the table holds it; real time the mean of the hour's four
    15-minute rows, held only when all four are there. Returns the number of hours that differ by more than half a cent
    or are held on one side only."""
    region, ref = facts["region"], facts["ref"]
    hub = next(r for r in facts["grid"]["regions"] if r["id"] == ref)
    _months, hours = months_of_lines(lines)
    plan = [("rt", REGION, "ercot_rtm", region["rt"]["tables"], 4), ("da", REGION, "ercot_dam", region["da"]["tables"], 1), ("hub", ref, "ercot_rtm", hub["rt"]["tables"], 4)]
    wrong = 0
    for k, entity, market, tables, per_hour in plan:
        rows, used = {}, []
        for t in tables:      # the builder's order: the history first; an interval both hold is the earlier table's
            path = os.path.join(tables_dir, f"{t}.csv")
            if not os.path.exists(path):
                log(f"  {k}: {t} is not in {tables_dir}")
                continue
            got, repeats = table_rows(path, entity, market)
            used.append(f"{t} ({len(got):,} rows{f'; {repeats} repeat an interval' if repeats else ''})")
            for ts, v in got.items():
                rows.setdefault(ts, v)
        merged = {}
        for ts, v in rows.items():
            merged.setdefault(ts[:13], []).append(v)
        table = {}
        blank = 0
        for h, vals in merged.items():
            if len(vals) != per_hour:
                continue
            nums = [float(v) for v in vals if v != ""]
            blank += len(vals) - len(nums)
            if nums:
                table[h + ":00:00Z"] = math.fsum(nums) / len(nums)
        both = only_csv = only_table = differ = 0
        worst, worst_at, sum_csv, sum_table = 0.0, "", 0.0, 0.0
        for h, vals in hours.items():
            v, t = (None if vals[k] == SENTINEL else vals[k]), table.get(h)
            if v is None and t is None:
                continue
            if t is None:
                only_csv += 1
                continue
            if v is None:
                only_table += 1
                continue
            both += 1
            sum_csv += v
            sum_table += t
            d = abs(v - t)
            if d > worst:
                worst, worst_at = d, h
            if d > TOL_TABLE:
                differ += 1
        short = sum(1 for vals in merged.values() if len(vals) != per_hour)
        log(f"  {k} ({entity}, {market}): tables {', '.join(used) or 'none'}; hours in both {both:,}; differing by more than half a cent {differ}; "
            f"largest difference {worst:.6f} at {worst_at or 'none'}; in the file only {only_csv}; in the tables only {only_table}; "
            f"hours of the tables without {per_hour} rows {short}; blank values {blank}; mean over the hours in both: file {sum_csv / both if both else float('nan'):.6f}, "
            f"tables unrounded {sum_table / both if both else float('nan'):.6f}")
        wrong += differ + only_table
        if k != "hub":
            wrong += only_csv      # the hub's newest days are in the daily table, which another machine may hold newer
    return wrong


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the hours behind What a datacenter pays for the page's default case, as one CSV")
    ap.add_argument("--out", default=OUT, help="the CSV to write")
    ap.add_argument("--site-dir", default=SITE_DIR, help="the page's files (site/data/datacenter); read only")
    ap.add_argument("--tables", help="also set every hour against the price tables in this directory (a warehouse/output; read only)")
    ap.add_argument("--report", help="with --tables: write the check's lines to this file as well")
    a = ap.parse_args(argv)
    if not os.path.exists(os.path.join(a.site_dir, "index.json")):
        print(f"datacenter_hourly_export SKIPPED: the page's files are not under {a.site_dir}")
        return 0
    run_at = dt.datetime.now(dt.timezone.utc).strftime(ISO)
    try:
        facts = page_facts(a.site_dir)
        rows = build(facts)
        if not rows:
            raise RuntimeError("the page's files hold no hour of the default case; nothing written")
        for r in rows:
            if SENTINEL in (r["rt"], r["da"], r["hub"]):
                raise RuntimeError(f"a real price equals the sentinel at {r['hour_utc']}; nothing written")
        lines = render(rows)
        bad, months = agree(lines, facts)
        if bad:
            print(f"datacenter_hourly_export FAILED: {len(bad)} differences between the rows as written and the page's files; nothing written", file=sys.stderr)
            for line in bad[:80]:
                print("  " + line, file=sys.stderr)
            return 1
        head = head_lines(rows, facts, months, run_at)
    except RuntimeError as e:
        print(f"datacenter_hourly_export FAILED: {e}", file=sys.stderr)
        return 1
    out = os.path.abspath(a.out)
    if same_data(out, head, lines):
        print(f"{os.path.basename(out)}: unchanged (the page's files hold the same hours); left as it is")
        size = os.path.getsize(out)
    else:
        size = write(head, lines, out)
    s12, bad_m = facts["s12"], facts["bad"]
    print(f"{os.path.basename(out)}: rows={len(rows)} months={len(months)} bytes={size} window={rows[0]['hour_utc']}..{rows[-1]['hour_utc']} "
          f"last_twelve={facts['l12'][0]}..{facts['l12'][-1]} per_mwh={s12['per']:.6f} bad_month={bad_m['m']} "
          f"not_held={ {k: sum(1 for r in rows if r[k] is None) for k in SERIES} }")
    if a.tables:
        said = []

        def log(line):
            said.append(line)
            print(line)
        log(f"datacenter_hourly_export --tables {os.path.abspath(a.tables)} at {run_at}: every hour of {os.path.basename(out)} against the price tables as they stand")
        wrong = check_tables(lines, facts, os.path.abspath(a.tables), log)
        log(f"  result: {wrong} hours differ or are held on one side only" if wrong else "  result: every hour compared is the tables' own, to half a cent")
        if a.report:
            with open(a.report, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(said) + "\n")
        return 1 if wrong else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
