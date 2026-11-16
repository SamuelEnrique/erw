#!/usr/bin/env python3
"""ERW, The shoulder hours (/shoulder): the replication a reader can run (session 7503, chain 304).

Written from the method notes (docs/methods/shoulder.md, which points to docs/methods/shoulder_hours.md) and the public
tables alone, not from the page's code. Every figure the page shows is computed again here and set beside the figure
the page itself draws on the same rows (site/scripts/shoulder-figures.mjs, run with node, or a file of its output):

  - a figure with a rule on public tables is recomputed by the rule: the midday surplus, the evening shoulder, the
    second measure and the evening peak from the average day's 24 hours (the table's avg_* rows); the fleet from
    storage_buildout_monthly; California's curtailment from caiso_curtailment_daily; the hours covered and needed; the
    yearly rows from the monthly ones and from the ten ranked days; a ranked day's hours needed and battery hours;
  - a figure whose only source is the hourly data (an hour of the average day, a ranked day's own measures, the count
    of days ranked) is the table's row here, and replication/shoulder/from_hourly.py recomputes a sample of those from
    EIA's hourly workbooks.

    python replication/shoulder/replicate.py                 # N of N, or each difference named
    python replication/shoulder/replicate.py --write         # also writes page_figures.json and page_figures.csv
    python replication/shoulder/replicate.py --headline      # only the do-file's five lines (replicate.do)

    --in-dir DIR   the folder of the tables (default: warehouse/output of this repository, else $ERW_OUTPUT_DIR)
    --page FILE    the page's figures as a file (the JSON the node script writes) instead of running node

A difference is inside the tolerance when it is at most half the last digit the page shows. Exit 0 when every figure
is inside it or its difference is the one kind this file names (a rounding edge, EDGE), 1 when another differs or a figure is on one side only,
2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
TABLE = "shoulder_hours_monthly"
# The note, "The views": the three grids of the panel, the table's entity of each, and the grid whose fleet it is set against.
GRIDS = [("ercot", "iso:ercot", "iso:ercot"), ("caiso", "iso:caiso", "iso:caiso"), ("caiso-own", "iso:caiso_own", "iso:caiso")]
# The note, "The month the page opens on": the figures the summary sentence and the headline numbers state.
REQUIRED = ["days_held", "shoulder_hours", "shoulder_start_hour", "shoulder_end_hour", "shoulder_mwh_above_mean", "fleet_mw", "fleet_mwh", "fleet_hours",
            "shoulder_hours_covered", "shoulder_hours_needed", "midday_surplus_mwh", "midday_surplus_hours", "midday_low_hour",
            "shoulder2_hours", "shoulder2_start_hour", "shoulder2_end_hour", "shoulder2_mwh_above_midpoint", "shoulder2_hours_needed", "evening_peak_mw", "evening_peak_hour"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# A difference this file names instead of failing on. One kind exists: a rounding edge. The table's builder computes a
# figure from the hourly means before they are rounded; this file starts from the table's average day, which holds four
# decimals. Summed over up to 24 hours the two can differ by about 0.001 MWh (and by one part in ten million after a
# division), which moves a figure across the edge of the page's last digit a few times in twenty thousand. Such a
# figure is within half the last digit plus that carried rounding, is counted apart, and is listed.
EDGE = 1e-7


def read_table(path):
    """The rows of a standard series table: comment lines begin with #."""
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def r4(x):
    """The table writes four decimals."""
    return None if x is None else round(x + 0.0, 4)


# ---------------------------------------------------------------------------------------------------------------------
# The rules of docs/methods/shoulder_hours.md, on one day of 24 hours (the average day of a month, or one day).

def measures(net, solar):
    """The midday surplus, the evening shoulder, the evening peak and the second measure of a day of 24 local hours."""
    mean = sum(net) / 24
    out = {"net_load_mean_mw": mean}
    # the midday surplus: the run of hours around net load's lowest hour in which net load is below its daily mean
    low = min(range(24), key=lambda h: (net[h], h))
    a = b = low
    while a - 1 >= 0 and net[a - 1] < mean:
        a -= 1
    while b + 1 <= 23 and net[b + 1] < mean:
        b += 1
    run = range(a, b + 1) if net[low] < mean else range(0)
    out.update(midday_low_hour=low, midday_surplus_hours=len(run), midday_surplus_mwh=sum(mean - net[h] for h in run))
    # the evening shoulder: from the first hour after solar's highest hour in which solar is below half of that highest
    # value, to the first hour, after net load has risen above its daily mean, in which it is back at or below it. Its
    # MWh above the mean count only the hours in which net load is above the mean: an early hour of the shoulder in
    # which net load has not yet risen above it adds nothing and takes nothing away
    top = max(range(24), key=lambda h: (solar[h], -h))
    start = next((h for h in range(top + 1, 24) if solar[h] < solar[top] / 2), None)
    if start is None:
        return out
    rise = next((h for h in range(start, 24) if net[h] > mean), None)
    if rise is None:
        out.update(shoulder_start_hour=start, shoulder_end_hour=start, shoulder_hours=0, shoulder_mwh_above_mean=0.0, shoulder_runs_to_midnight=0)
        return out
    end = next((h for h in range(rise + 1, 24) if net[h] <= mean), 24)
    out.update(shoulder_start_hour=start, shoulder_end_hour=end, shoulder_hours=end - start, shoulder_runs_to_midnight=1 if end == 24 else 0,
               shoulder_mwh_above_mean=sum(max(0.0, net[h] - mean) for h in range(start, end)))
    # the evening peak: net load's highest hour from the shoulder's start to midnight; the second measure: the run of
    # hours around it in which net load is above the midpoint between the daily mean and that peak, no earlier than
    # the first shoulder's start
    peak = max(range(start, 24), key=lambda h: (net[h], -h))
    level = (mean + net[peak]) / 2
    a = b = peak
    while a - 1 >= start and net[a - 1] > level:
        a -= 1
    while b + 1 <= 23 and net[b + 1] > level:
        b += 1
    run = range(a, b + 1) if net[peak] > level else range(0)
    out.update(evening_peak_hour=peak, evening_peak_mw=net[peak], shoulder2_level_mw=level,
               shoulder2_start_hour=a, shoulder2_end_hour=b + 1 if len(run) else a, shoulder2_hours=len(run),
               shoulder2_mwh_above_midpoint=sum(net[h] - level for h in run),
               shoulder2_runs_to_midnight=1 if len(run) and b == 23 else 0)
    return out


def against_fleet(m, mw, mwh):
    """The fleet set against a day's two measures: its hours, the hours covered and the hours needed."""
    out = {}
    if mw is None or mwh is None or mw <= 0:
        return out
    hours = r4(mwh / mw)
    out.update(fleet_mw=mw, fleet_mwh=mwh, fleet_hours=hours)
    if "shoulder_hours" in m:
        out.update(shoulder_hours_covered=min(m["shoulder_hours"], hours), shoulder_hours_needed=m["shoulder_mwh_above_mean"] / mw)
    if "shoulder2_hours" in m:
        out.update(shoulder2_hours_covered=min(m["shoulder2_hours"], hours), shoulder2_hours_needed=m["shoulder2_mwh_above_midpoint"] / mw)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# The tables

class Tables:
    def __init__(self, in_dir):
        self.dir = in_dir
        self.t = {}            # (entity, variable, YYYY-MM-DD) -> value, the shoulder table
        for r in read_table(os.path.join(in_dir, TABLE + ".csv")):
            self.t[(r["entity"], r["variable"], r["ts_utc"][:10])] = float(r["value"])
        self.fleet = {}        # (grid entity, mw or mwh, YYYY-MM) -> value, EIA-860M through storage_buildout_monthly
        for r in read_table(os.path.join(in_dir, "storage_buildout_monthly.csv")):
            if r["variable"] in ("battery_operating_mw", "battery_operating_mwh"):
                self.fleet[(r["entity"], r["variable"][len("battery_operating_"):], r["ts_utc"][:7])] = float(r["value"])
        self.curtailed = {}    # YYYY-MM -> [MWh of each day held], CAISO's curtailed solar plus curtailed wind
        days = {}
        for r in read_table(os.path.join(in_dir, "caiso_curtailment_daily.csv")):
            if r["variable"] in ("curtailed_solar_mwh", "curtailed_wind_mwh"):
                days[r["ts_utc"][:10]] = days.get(r["ts_utc"][:10], 0.0) + float(r["value"])
        for d, v in days.items():
            self.curtailed.setdefault(d[:7], []).append(v)

    def months(self, entity):
        return sorted({k[2][:7] for k in self.t if k[0] == entity and k[1] == "days_held"})

    def years(self, entity):
        return sorted({k[2][:4] for k in self.t if k[0] == entity and k[1] == "year_months_held"})

    def day(self, entity, series, month):
        v = [self.t.get((entity, f"avg_{series}_mw_h{h:02d}", month + "-01")) for h in range(24)]
        return v if all(x is not None for x in v) else None


def replicate(T):
    """Every row of the table the note gives a rule for, recomputed: {(entity, variable, date): value}; and, for the rows
    whose only source is the hourly data, the table's own value. The second dict says which is which."""
    R, basis = {}, {}

    def put(entity, variable, date, value, how):
        if value is not None:
            R[(entity, variable, date)] = value
            basis[(entity, variable, date)] = how

    for _, entity, fleet_entity in GRIDS:
        monthly = {}
        for month in T.months(entity):
            date = month + "-01"
            net, solar = T.day(entity, "net_load", month), T.day(entity, "solar", month)
            for series in ("demand", "solar", "wind", "net_load", "battery"):
                for h in range(24):
                    k = (entity, f"avg_{series}_mw_h{h:02d}", date)
                    put(*k, T.t.get(k), "the table's row (the hourly data: from_hourly.py)")
            for v in ("days_held", "days_in_month"):
                put(entity, v, date, T.t.get((entity, v, date)), "the table's row (the hourly data: from_hourly.py)")
            if net is None or solar is None:
                continue
            m = measures(net, solar)
            m.update(against_fleet(m, T.fleet.get((fleet_entity, "mw", month)), T.fleet.get((fleet_entity, "mwh", month))))
            if entity != "iso:ercot" and T.curtailed.get(month):
                m["curtailed_mwh_per_day"] = sum(T.curtailed[month]) / len(T.curtailed[month])
            monthly[month] = m
            for v, x in m.items():
                put(entity, v, date, x, "recomputed from the average day, the fleet and the curtailment tables")
        # the ranked days: their own measures are the table's rows; the hours needed and the battery hours are set
        # against the fleet of the day's month here
        ranked = {}
        for (e, v, d), x in T.t.items():
            if e == entity and (v == "worst_rank" or v.startswith("day_")):
                ranked.setdefault(d, {})[v] = x
        for d, row in ranked.items():
            mw = T.fleet.get((fleet_entity, "mw", d[:7]))
            for v, x in row.items():
                put(entity, v, d, x, "the table's row (the hourly data: from_hourly.py)")
            if mw:
                put(entity, "day_fleet_mw", d, mw, "recomputed: the fleet of the day's month")
                put(entity, "day_shoulder_hours_needed", d, row["day_shoulder_mwh_above_mean"] / mw, "recomputed: the day's energy over the fleet's MW")
                if "day_shoulder2_mwh_above_midpoint" in row:
                    put(entity, "day_shoulder2_hours_needed", d, row["day_shoulder2_mwh_above_midpoint"] / mw, "recomputed: the day's energy over the fleet's MW")
                if "day_battery_discharge_mwh" in row:
                    put(entity, "day_battery_hours", d, row["day_battery_discharge_mwh"] / mw, "recomputed: the discharge over the fleet's MW")
            else:
                for v in ("day_fleet_mw", "day_shoulder_hours_needed", "day_shoulder2_hours_needed", "day_battery_hours"):
                    R.pop((entity, v, d), None)
                    basis.pop((entity, v, d), None)
        # the yearly rows: the mean over the year's months held; the fleet at the year's last month that has one; the
        # mean of the ten ranked days (the hours needed only when all ten have them)
        for year in sorted({m[:4] for m in monthly}):
            date = year + "-01-01"
            ms = [m for m in monthly if m.startswith(year)]
            put(entity, "year_months_held", date, len(ms), "recomputed: the months held")
            for v in ("shoulder_hours", "shoulder_mwh_above_mean", "shoulder_start_hour", "shoulder_runs_to_midnight", "midday_surplus_hours", "midday_surplus_mwh",
                      "curtailed_mwh_per_day", "shoulder_hours_covered", "shoulder_hours_needed", "shoulder2_hours", "shoulder2_mwh_above_midpoint",
                      "shoulder2_runs_to_midnight", "shoulder2_hours_covered", "shoulder2_hours_needed"):
                xs = [r4(monthly[m][v]) for m in ms if v in monthly[m]]
                if xs:
                    put(entity, "year_mean_" + v, date, sum(xs) / len(xs), "recomputed: the mean over the year's months held")
            with_fleet = [m for m in ms if "fleet_mw" in monthly[m]]
            if with_fleet:
                for v in ("fleet_mw", "fleet_mwh", "fleet_hours"):
                    put(entity, "year_end_" + v, date, monthly[with_fleet[-1]][v], "recomputed: the fleet at the year's last month that has one")
            put(entity, "year_days_ranked", date, T.t.get((entity, "year_days_ranked", date)), "the table's row (the hourly data: from_hourly.py)")
            ten = sorted((d for d in ranked if d.startswith(year) and "worst_rank" in ranked[d]), key=lambda d: ranked[d]["worst_rank"])
            if ten:
                put(entity, "year_worst10_days", date, len(ten), "recomputed: the days ranked")
                for v, whole in (("shoulder_mwh_above_mean", False), ("shoulder_hours", False), ("shoulder2_hours", False), ("shoulder_hours_needed", True),
                                 ("shoulder2_hours_needed", True), ("battery_hours", True)):
                    xs = [r4(R[(entity, "day_" + v, d)]) for d in ten if (entity, "day_" + v, d) in R]
                    if xs and (len(xs) == len(ten) or not whole):
                        put(entity, "year_worst10_mean_" + v, date, sum(xs) / len(xs), "recomputed: the mean of the ten ranked days")
    return R, basis


def opening(T, entity):
    """The month a grid opens on: the latest that holds every figure of REQUIRED; the newest held when none does."""
    months = T.months(entity)
    complete = [m for m in months if all((entity, v, m + "-01") in T.t for v in REQUIRED)]
    return (complete or months or [None])[-1]


# ---------------------------------------------------------------------------------------------------------------------
# The page's figures and the comparison

def page_figures(in_dir, page_file):
    if page_file:
        with open(page_file, encoding="utf-8") as f:
            return json.load(f)
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    done = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/shoulder-figures.mjs", os.path.join(in_dir, TABLE + ".csv"), out],
                          cwd=SITE, capture_output=True, text=True)
    if done.returncode != 0:
        raise OSError("node scripts/shoulder-figures.mjs failed: " + (done.stderr or done.stdout)[-600:])
    with open(out, encoding="utf-8") as f:
        page = json.load(f)
    os.remove(out)
    return page


def number(text):
    """A figure as the page writes it: "19:00" is hour 19, "59,771.00" a number; the tolerance is half its last digit."""
    t = text.strip()
    if t.endswith(":00") and t[:-3].isdigit():
        return float(t[:-3]), 0.5
    t = t.replace(",", "")
    return float(t), (0.5 * 10 ** -len(t.split(".")[1]) if "." in t else 0.5)


def month_of_name(name):
    month, year = name.split(" ")
    return f"{year}-{MONTH_NAMES.index(month) + 1:02d}"


def compare(T, page):
    """[(figure, where, page text, replication, difference, tolerance, ok, basis)] for every figure the page draws."""
    R, basis = replicate(T)
    rows = []

    def one(figure, where, text, key):
        got = R.get(key)
        if text in ("not held", ""):
            rows.append((figure, where, text, got, None, None, got is None, basis.get(key, "not held on either side")))
            return
        shown, tol = number(text)
        if got is None:
            rows.append((figure, where, text, None, None, tol, False, "no rule gave it"))
            return
        diff = r4(got) - shown          # the table holds four decimals, and the page shows the table's value
        how = basis[key]
        ok = abs(diff) <= tol + 1e-9
        if not ok and how.startswith("recomputed") and abs(diff) <= tol + EDGE * max(1.0, abs(shown)) + 0.0013:
            how = "ROUNDING EDGE: " + how
        rows.append((figure, where, text, got, diff, tol, ok, how))

    for key, v in page["keyed"].items():
        _, _, entity, variable, ts = key.split("|")
        one(key, "a checked number", v["text"], (entity, variable, ts[:10]))
    for key, text in page["chart_day"].items():
        entity, variable, name = key.split("|")
        one(f"chart|{entity}|{variable}|{month_of_name(name)}", "the average day's chart, on hover", text, (entity, variable, month_of_name(name) + "-01"))
    for key, v in page["chart_month"].items():
        entity, name = key.split("|")
        m = month_of_name(name)
        one(f"months|{entity}|shoulder_hours|{m}", "the months' chart, on hover", v["shoulder"], (entity, "shoulder_hours", m + "-01"))
        one(f"months|{entity}|shoulder_hours_covered|{m}", "the months' chart, on hover", v["covered"], (entity, "shoulder_hours_covered", m + "-01"))
    for slug, entity, _ in GRIDS:
        ours = opening(T, entity)
        for v in page["views"]:
            if v["grid"] == slug and v["asked"] is None:
                theirs = month_of_name(v["drawn"]) if v["drawn"] else None
                rows.append((f"opening|{entity}", "the month a grid opens on", theirs, ours, None, None, theirs == ours, "recomputed: the latest month that holds every figure"))
    # the words that carry a figure: "(midnight)" in the summary exactly where the shoulder runs to midnight
    for v in page["views"]:
        entity = next(e for s, e, _ in GRIDS if s == v["grid"])
        if not v["drawn"]:
            continue
        m = month_of_name(v["drawn"])
        ours = R.get((entity, "shoulder_runs_to_midnight", m + "-01")) == 1
        rows.append((f"midnight|{entity}|{m}", "the summary's \"(midnight)\"", "yes" if v["midnight"] else "no", "yes" if ours else "no", None, None, v["midnight"] == ours,
                     "recomputed from the average day"))
    return rows


def headline(T, out=print):
    """The do-file's five lines (replicate.do), step for step: ERCOT, the month the page opens on."""
    entity, fleet_entity = "iso:ercot", "iso:ercot"
    month = opening(T, entity)
    m = measures(T.day(entity, "net_load", month), T.day(entity, "solar", month))
    m.update(against_fleet(m, T.fleet.get((fleet_entity, "mw", month)), T.fleet.get((fleet_entity, "mwh", month))))
    year = month[:4]
    ten = [d for (e, v, d) in T.t if e == entity and v == "worst_rank" and d.startswith(year)]
    needed = [round(T.t[(entity, "day_shoulder_mwh_above_mean", d)] / T.fleet[(fleet_entity, "mw", d[:7])], 4) for d in ten if (fleet_entity, "mw", d[:7]) in T.fleet]
    out(f"ERCOT, {MONTH_NAMES[int(month[5:]) - 1]} {month[:4]} (the month the page opens on)")
    if not needed:
        needed = [float("nan")]
    out(f"1. the evening shoulder, hours: {m['shoulder_hours']} (from {m['shoulder_start_hour']:02d}:00 to {m['shoulder_end_hour']:02d}:00)")
    out(f"2. net load above its daily mean in the shoulder, MWh: {m['shoulder_mwh_above_mean']:,.2f}")
    out(f"3. the fleet's hours at full power (MWh over MW), and the hours of the shoulder it covers: {m['fleet_hours']:.2f} and {m['shoulder_hours_covered']:.2f}")
    out(f"4. hours the fleet would need to deliver all of it: {m['shoulder_hours_needed']:.2f}")
    out(f"5. the same on the ten worst days of {year}, their mean: {sum(needed) / len(needed):.2f} ({len(needed)} days)")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--page", default=None)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true")
    a = ap.parse_args(argv[1:])
    in_dir = a.in_dir or next((d for d in (os.path.join(ROOT, "warehouse", "output"), os.environ.get("ERW_OUTPUT_DIR", "")) if d and os.path.exists(os.path.join(d, TABLE + ".csv"))), None)
    try:
        if not in_dir:
            raise OSError(f"{TABLE}.csv is in neither warehouse/output nor $ERW_OUTPUT_DIR: name its folder with --in-dir")
        T = Tables(in_dir)
        if a.headline:
            headline(T)
            return 0
        page = page_figures(in_dir, a.page)
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    rows = compare(T, page)
    bad = [r for r in rows if not r[6] and not r[7].startswith("ROUNDING EDGE")]
    named = [r for r in rows if not r[6] and r[7].startswith("ROUNDING EDGE")]
    recomputed = sum(1 for r in rows if r[7].startswith("recomputed"))
    print(f"The shoulder hours, {len(page['views'])} views of the page ({len(T.t):,} rows of {TABLE})")
    for r in bad[:40]:
        print(f"DIFFERS {r[0]} ({r[1]}): the page {r[2]}, the replication {r[3]}; {r[7]}")
    for r in named:
        print(f"named   {r[0]}: the page {r[2]}, the replication {r[3]:.6f}; a rounding edge (the table's four decimals carried through a sum)")
    print(f"{len(rows) - len(bad) - len(named)} of {len(rows)} inside the tolerance; {len(named)} named (a rounding edge); {len(bad)} differ; {recomputed} recomputed by the note's rules, "
          f"{len(rows) - recomputed} the table's rows of the hourly data (a sample recomputed by from_hourly.py)")
    if a.write:
        write(T, page, rows)
    return 0 if not bad else 1


def write(T, page, rows):
    """page_figures.json and page_figures.csv: the figures of the three views a reader meets with no month named (every
    checked number, the average day's chart and the months' chart of each), and the count over every view."""
    keep = set()
    for v in page["views"]:
        if v["asked"] is None:
            keep.update(v.get("keys") or [])
    opened = {next(e for s, e, _ in GRIDS if s == v["grid"]): month_of_name(v["drawn"]) for v in page["views"] if v["asked"] is None and v["drawn"]}

    def kept(r):
        p = r[0].split("|")
        if r[0] in keep or p[0] in ("opening", "months"):
            return True
        return p[0] in ("chart", "midnight") and opened.get(p[1]) == p[-1]

    figures = [{"key": r[0], "where": r[1], "page": r[2], "replication": (round(r[3], 4) if isinstance(r[3], float) else r[3]), "tolerance": r[5], "inside": r[6], "basis": r[7]}
               for r in rows if kept(r)]
    about = (f"The shoulder hours (/shoulder): the figures of the three views a reader meets with no month named (ERCOT {opened.get('iso:ercot')}, CAISO by EIA-930 "
             f"{opened.get('iso:caiso')}, CAISO's own data {opened.get('iso:caiso_own')}), each as the page's own code draws it on the rows of {TABLE} "
             f"(site/scripts/shoulder-figures.mjs) beside the replication's value (replication/shoulder/replicate.py). The run itself compares every view: "
             f"{len(page['views'])} views, {len(rows)} figures, {sum(1 for r in rows if r[6])} inside the tolerance (half the page's last shown digit).")
    with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_about": about, "table_rows": len(T.t), "views": len(page["views"]), "figures_all_views": len(rows),
                   "inside_all_views": sum(1 for r in rows if r[6]), "opening": opened, "figures": figures}, f, indent=1)
        f.write("\n")
    with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW, the shoulder hours: the figures of the three opening views, the page beside the replication (replication/shoulder/replicate.py --write); {len(rows)} figures over every view\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "where", "page", "replication", "tolerance", "inside", "basis"])
        for x in figures:
            w.writerow([x["key"], x["where"], x["page"], x["replication"], x["tolerance"], "yes" if x["inside"] else "NO", x["basis"]])
    print(f"written: page_figures.json and page_figures.csv, {len(figures)} figures of the three opening views")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
