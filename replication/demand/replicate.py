#!/usr/bin/env python3
"""ERW, demand growth since 2019 (/demand, as metered): an independent replication of every figure of the page's file
(session 7014, chain 301; the done line's tool 22).

Written from docs/methods/demand_growth.md ("Input", "Which hours are used", "The rows") and the workbooks it names, not
from warehouse/derived/demand_growth.py. It reads EIA-930's per-area workbooks (sheet "Published Hourly Data"): EIA's
"Adjusted demand" for a balancing authority, "Demand" for the Lower 48; an hour dated by its start (EIA's UTC time is the
hour's end); California's hours from 2023-10-31 23:00 to 2025-12-02 23:00 UTC read one hour earlier, a row landing on an
hour already held dropped (docs/methods/eia930_caiso_break.md, "The late hours"). An hour is used when it is held, above
zero, and within 25 percent of the median of the four hours around it (the two before and the two after that are held
and above zero); the hours left out are counted from 2019 to the workbook's last row, EIA's blank last day included.
Then, per local year: the mean of the used hours and their count when at least 95 percent of the year's hours are used;
the highest used hour (none for the Lower 48); the same over 1 January to the end of the file's last whole month; the
mean of each calendar month (95 percent), of each local hour of the day over the year, of each month's hour (90 percent);
growth since 2019 and on the year before; on the last whole year's row the change from 2019 of every month, hour and
cell. It compares each with site/data/demand_growth.json, and the counts of hours screened out. Prints N of N.

    python replication/demand/replicate.py --workbooks DIR [--site DIR]

DIR holds the nine workbooks (`*_ERCO.xlsx` ... `*_Region_US48.xlsx`), as saved in warehouse/raw/eia930_emissions/<run>/
on the data machine, or downloaded from https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx. EIA
revises its file; a workbook fetched on another day can differ in a few hours. Needs openpyxl (the one library beyond
Python's own: the workbooks are Excel files). Figures are compared to half a unit of their printed last decimal.
Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read.
"""
import argparse
import datetime as dt
import glob
import json
import os
import statistics
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UTC = dt.timezone.utc
LATE_FROM = dt.datetime(2023, 10, 31, 23, tzinfo=UTC)
LATE_TO = dt.datetime(2025, 12, 2, 23, tzinfo=UTC)
FILE_OF = {"US48": "Region_US48"}


def read_hours(path, area):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Published Hourly Data"]
    it = ws.iter_rows(values_only=True)
    head = list(next(it))
    col = head.index("Demand" if area == "US48" else "Adjusted demand")
    ut = head.index("UTC time")
    out = {}
    for r in it:
        if r[ut] is None:
            continue
        start = r[ut].replace(tzinfo=UTC) - dt.timedelta(hours=1)
        out[start] = r[col]
    wb.close()
    if area == "CISO":
        moved = {}
        for t, v in out.items():
            if LATE_FROM <= t < LATE_TO:
                t2 = t - dt.timedelta(hours=1)
                if t2 < LATE_FROM:
                    continue   # the first late row lands on an hour that holds its own value
                moved[t2] = v
            else:
                moved[t] = v
        out = moved   # 2025-12-02 22:00 UTC is left empty, not filled
    return out


def screen(hours, first, last):
    """{start: value} of the used hours from first to last (both UTC, last excluded), and the counts left out."""
    held = sorted(t for t, v in hours.items() if v is not None and v > 0)   # neighbours: hours held and above zero
    idx = {t: i for i, t in enumerate(held)}
    used, n_blank, n_np, n_jump = {}, 0, 0, 0
    t = first
    while t < last:
        if t not in hours:   # no row (California's emptied hour): nothing to count
            t += dt.timedelta(hours=1)
            continue
        v = hours[t]
        if v is None:
            n_blank += 1
        elif v <= 0:
            n_np += 1
        else:
            i = idx[t]
            around = [hours[x] for x in held[max(0, i - 2):i] + held[i + 1:i + 3]]
            med = statistics.median(around)
            if abs(v - med) <= 0.25 * med:
                used[t] = float(v)
            else:
                n_jump += 1
        t += dt.timedelta(hours=1)
    return used, {"blank": n_blank, "not_positive": n_np, "jumps": n_jump}


def area_figures(used, tz, years, ytd_end_month, peak):
    by = defaultdict(list)          # (year, key) -> values
    span = defaultdict(int)         # (year, key) -> hours in the window
    for y in years:
        a = dt.datetime(y, 1, 1, tzinfo=tz).astimezone(UTC)
        b = dt.datetime(y + 1, 1, 1, tzinfo=tz).astimezone(UTC)
        ye = dt.datetime(y, ytd_end_month + 1, 1, tzinfo=tz).astimezone(UTC) if ytd_end_month < 12 else b
        t = a
        while t < b:
            lt = t.astimezone(tz)
            keys = ["year", f"m{lt.month:02d}", f"h{lt.hour:02d}", f"m{lt.month:02d}_h{lt.hour:02d}"]
            if t < ye:
                keys.append("ytd")
            for k in keys:
                span[(y, k)] += 1
                if t in used:
                    by[(y, k)].append((used[t], t))
            t += dt.timedelta(hours=1)
    out = {}
    for y in years:
        f, at = {}, {}
        yr = by[(y, "year")]
        if span[(y, "year")] and len(yr) >= 0.95 * span[(y, "year")]:
            f["avg_demand_mw"] = sum(v for v, _ in yr) / len(yr)
            f["hours_used"] = len(yr)
            f["hours_in_year"] = span[(y, "year")]
            if peak:
                v, t = max(yr)
                f["peak_demand_mw"], at["peak_demand_mw"] = v, t
        yt = by[(y, "ytd")]
        if yt:
            f["ytd_avg_demand_mw"] = sum(v for v, _ in yt) / len(yt)
            f["ytd_hours_used"] = len(yt)
            f["ytd_hours_in_window"] = span[(y, "ytd")]
            if peak:
                v, t = max(yt)
                f["ytd_peak_demand_mw"], at["ytd_peak_demand_mw"] = v, t
        for m in range(1, 13):
            xs = by[(y, f"m{m:02d}")]
            if span[(y, f"m{m:02d}")] and len(xs) >= 0.95 * span[(y, f"m{m:02d}")]:
                f[f"avg_demand_mw_m{m:02d}"] = sum(v for v, _ in xs) / len(xs)
            for h in range(24):
                k = f"m{m:02d}_h{h:02d}"
                xs = by[(y, k)]
                if span[(y, k)] and len(xs) >= 0.9 * span[(y, k)]:
                    f[f"avg_demand_mw_{k}"] = sum(v for v, _ in xs) / len(xs)
        if "avg_demand_mw" in f:
            for h in range(24):
                xs = by[(y, f"h{h:02d}")]
                if xs:
                    f[f"avg_demand_mw_h{h:02d}"] = sum(v for v, _ in xs) / len(xs)
        out[y] = (f, at)
    return out


def decimals(x):
    s = repr(float(x))
    return 0 if "e" in s else len(s.split(".")[1])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Demand growth's replication")
    ap.add_argument("--workbooks", required=True)
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    ap.add_argument("--areas", default="")
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "demand_growth.json"), encoding="utf-8") as f:
            page = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    base, last_year = page["base"], page["last_year"]
    ytd_year, ytd_month = (int(x) for x in page["ytd_through"].split("-"))
    years = list(range(base, ytd_year + 1))
    n, misses = 0, []

    def check(what, mine, theirs):
        nonlocal n
        n += 1
        if isinstance(theirs, (int, float)) and isinstance(mine, (int, float)) and not isinstance(theirs, bool):
            ok = abs(mine - theirs) <= 0.5 * 10 ** -decimals(theirs) + 1e-6
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    for area in [x for x in page["order"] if not a.areas or x in a.areas.split(",")]:
        spec = page["areas"][area]
        files = sorted(glob.glob(os.path.join(a.workbooks, f"*_{FILE_OF.get(area, area)}.xlsx")))
        if not files:
            print(f"the inputs could not be read: no workbook for {area} in {a.workbooks}")
            return 2
        tz = ZoneInfo(spec["tz"])
        hours = read_hours(files[-1], area)
        first = dt.datetime(base, 1, 1, tzinfo=tz).astimezone(UTC)
        last = dt.datetime(ytd_year, ytd_month + 1, 1, tzinfo=tz).astimezone(UTC) if ytd_month < 12 else \
            dt.datetime(ytd_year + 1, 1, 1, tzinfo=tz).astimezone(UTC)
        used, counts = screen(hours, first, max(hours) + dt.timedelta(hours=1))   # counted to the workbook's last row
        for k, v in spec.get("screened", {}).items():
            check(f"{area} screened {k}", counts.get(k), v)
        got = area_figures(used, tz, years, ytd_month, area != "US48")
        mine_all = {}
        for y in years:
            f, at = got[y]
            if y == ytd_year:   # the partial year: its year to date and its months only
                f = {k: v for k, v in f.items() if k.startswith("ytd_") or (k.startswith("avg_demand_mw_m") and "_h" not in k)}
            b0 = got[base][0]
            for k in ("avg_demand_mw", "peak_demand_mw", "ytd_avg_demand_mw", "ytd_peak_demand_mw"):
                if k in f and k in b0 and y != base:
                    f[k.replace("_mw", "_growth_since_2019_pct")] = (f[k] / b0[k] - 1) * 100
            prev = got.get(y - 1, ({}, {}))[0]
            if "avg_demand_mw" in f and "avg_demand_mw" in prev:
                f["avg_demand_growth_yoy_pct"] = (f["avg_demand_mw"] / prev["avg_demand_mw"] - 1) * 100
            if y == last_year:
                for k in list(f):
                    if k.startswith("avg_demand_mw_") and k in b0:
                        s = k[len("avg_demand_mw_"):]
                        a1, b1 = round(f[k], 1), round(b0[k], 1)   # the change of the printed means
                        f[f"growth_mw_{s}"] = a1 - b1
                        f[f"growth_pct_{s}"] = (a1 / b1 - 1) * 100
            mine_all[y] = (f, at)
        for y in years:
            f, at = mine_all[y]
            theirs = spec["years"].get(str(y), {})
            for k in sorted(set(theirs) | set(f)):
                check(f"{area} {y} {k}", f.get(k), theirs.get(k))
            for k, t in spec.get("at", {}).get(str(y), {}).items():
                mt = at.get(k)
                check(f"{area} {y} at {k}", mt and mt.strftime("%Y-%m-%dT%H:%M:%SZ"), t)
    print(f"Demand growth, the workbooks in {a.workbooks} against demand_growth.json (built {page['built']}): "
          f"{len(page['order'])} areas, {years[0]} to {years[-1]} (year to date through {page['ytd_through']})")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
