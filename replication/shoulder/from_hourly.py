#!/usr/bin/env python3
"""ERW, The shoulder hours: a sample of the table's own rows recomputed from EIA's hourly data (session 7503, chain 304).

replicate.py traces every figure of the page to shoulder_hours_monthly. This file traces a sample of that table's rows
to their source: EIA Form EIA-930, the per-balancing-authority workbook (sheet "Published Hourly Data"), read as
docs/methods/shoulder_hours.md says ("Inputs", "The average day", "The worst days"). For each grid and month named it
recomputes the average day hour by hour (demand, solar, wind, net load and, for ERCOT, battery output), the days held,
and from them every measure of the month (California's late hours of November 2023 to December 2025 set back one hour,
docs/methods/eia930_caiso_break.md; an impossible hour of demand left blank, docs/methods/impossible_hours.md); for each grid and year named, the count of days ranked, the ten days with
the most shoulder energy and each day's own measures. Each value is set beside the table's row.

    python replication/shoulder/from_hourly.py --workbook ERCO=<ERCO.xlsx or a CSV of its sheet> --workbook CISO=<...>
        [--in-dir DIR] [--months iso:ercot=2019-07,2024-01,2026-08 ...] [--years iso:ercot=2025 ...] [--write]

The workbooks are EIA's (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ERCO.xlsx and CISO.xlsx, about
75 and 97 MB); the table's header names the copies its builder read. A workbook retrieved later can differ in its
newest months, which EIA revises: a difference there is the revision, not the rule. An .xlsx needs openpyxl; a CSV of
the sheet (the same columns, the first row their names) needs nothing. Exit 0 when every value is inside 0.00006 of
the table's row (the table holds four decimals), 1 when one is not, 2 when an input cannot be read.
"""
import argparse
import csv
import datetime
import json
import os
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replicate as rep  # noqa: E402  (the rules of the note, written once)

BA = {"iso:ercot": ("ERCO", "America/Chicago"), "iso:caiso": ("CISO", "America/Los_Angeles")}
DEFAULT_MONTHS = {"iso:ercot": ["2019-07", "2024-01", "2025-03", "2026-08"], "iso:caiso": ["2019-07", "2021-04", "2024-01", "2025-11"]}
DEFAULT_YEARS = {"iso:ercot": ["2025"], "iso:caiso": ["2024"]}
TOL = 0.00006
LAST = {"iso:caiso": "2025-11"}   # the note, "Inputs": California by EIA-930 stops after November 2025


def sheet_rows(path):
    """The rows of the sheet "Published Hourly Data" as dicts, from the workbook or from a CSV of the sheet."""
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8", newline="") as f:
            yield from csv.DictReader(f)
        return
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    it = ws.iter_rows(values_only=True)
    names = next(it)
    for row in it:
        yield {k: ("" if v is None else v) for k, v in zip(names, row)}


def num(v):
    if v is None or v == "":
        return None
    return float(v)


# docs/methods/eia930_caiso_break.md, "The late hours": in EIA's California workbook a value whose hour starts from
# 2023-10-31T23:00Z up to, not including, 2025-12-02T23:00Z belongs to the hour before the one it is stamped with.
LATE = {"CISO": (datetime.datetime(2023, 10, 31, 23), datetime.datetime(2025, 12, 2, 23))}
FIRST_YEAR = 2018   # the history read: rows whose stamp (the hour's end) is in 2018 or later


def screen(demand):
    """docs/methods/impossible_hours.md, rule A, on {hour start: demand}: an hour of demand is used when it is held, above
    zero, within 25 percent of the median of the four hours around it (the two before and the two after, those held and
    above zero), and between one third of and three times the median of the hours that pass those three tests. An hour
    that fails is a blank."""
    import statistics
    hour = datetime.timedelta(hours=1)
    passed = {}
    for t, v in demand.items():
        if v is None or v <= 0:
            continue
        around = [demand.get(t + k * hour) for k in (-2, -1, 1, 2)]
        around = [x for x in around if x is not None and x > 0]
        if around and abs(v - statistics.median(around)) > 0.25 * statistics.median(around):
            continue
        passed[t] = v
    if not passed:
        return passed
    mid = statistics.median(passed.values())
    return {t: v for t, v in passed.items() if mid / 3 <= v <= 3 * mid}


def hours(path, zone, ba=None):
    """{local date: [(local hour, demand, solar, wind, battery)]}: an hour is dated by its start (EIA's "UTC time" is
    the hour's end), in the grid's local time, daylight saving included. EIA's Adjusted columns; solar is SUN plus SNB,
    wind is WND plus WNB (a blank SNB or WNB beside a held SUN or WND adds nothing). California's late hours are read
    one hour earlier (the first of them lands on an hour that holds its own value and is dropped; the last hour before
    the stamps are right again is then empty). An impossible hour of demand is a blank."""
    tz, utc = zoneinfo.ZoneInfo(zone), datetime.timezone.utc
    late = LATE.get(ba)
    kept, moved = {}, {}
    for r in sheet_rows(path):
        t = r["UTC time"]
        if not isinstance(t, datetime.datetime):
            t = datetime.datetime.strptime(str(t)[:19], "%Y-%m-%d %H:%M:%S")
        if t.year < FIRST_YEAR:
            continue
        start = t - datetime.timedelta(hours=1)
        sun, wnd = num(r["Adjusted SUN Gen"]), num(r["Adjusted WND Gen"])
        snb, wnb = num(r["Adjusted SNB Gen"]), num(r["Adjusted WNB Gen"])
        solar = None if sun is None and snb is None else (sun or 0.0) + (snb or 0.0)
        wind = None if wnd is None and wnb is None else (wnd or 0.0) + (wnb or 0.0)
        rec = [num(r["Adjusted demand"]), solar, wind, num(r["Adjusted BAT Gen"])]
        if late and late[0] <= start < late[1]:
            moved[start - datetime.timedelta(hours=1)] = rec
        else:
            kept[start] = rec
    for t, rec in moved.items():
        kept.setdefault(t, rec)
    good = screen({t: rec[0] for t, rec in kept.items()})
    days = {}
    for t in sorted(kept):
        d, s, w, b = kept[t]
        local = t.replace(tzinfo=utc).astimezone(tz)
        days.setdefault(local.strftime("%Y-%m-%d"), []).append((local.hour, good.get(t), s, w, b))
    return days


def expected_hours(day, zone):
    """The hours of a local day: 24, or 23 or 25 on a day the clocks change."""
    tz = zoneinfo.ZoneInfo(zone)
    y, m, d = (int(x) for x in day.split("-"))
    a = datetime.datetime(y, m, d, tzinfo=tz)
    b = datetime.datetime.combine(datetime.date(y, m, d) + datetime.timedelta(days=1), datetime.time(), tzinfo=tz)
    return round((b.astimezone(datetime.timezone.utc) - a.astimezone(datetime.timezone.utc)).total_seconds() / 3600)


def complete(rows, day, zone):
    """A complete day holds every hour of demand, solar and wind."""
    return len(rows) == expected_hours(day, zone) and all(d is not None and s is not None and w is not None for _, d, s, w, _ in rows)


def average_day(days, month, zone):
    """The month's average day over its complete days, and how many they are."""
    held = {d: rows for d, rows in days.items() if d.startswith(month) and complete(rows, d, zone)}
    out = {"days_held": len(held)}
    if not held:
        return out
    acc = {s: [[] for _ in range(24)] for s in ("demand", "solar", "wind", "net_load", "battery")}
    battery = all(b is not None for rows in held.values() for *_, b in rows)
    for rows in held.values():
        for h, d, s, w, b in rows:
            acc["demand"][h].append(d)
            acc["solar"][h].append(s)
            acc["wind"][h].append(w)
            acc["net_load"][h].append(d - s - w)
            if battery:
                acc["battery"][h].append(b)
    for s, by_hour in acc.items():
        if all(by_hour):
            for h in range(24):
                out[f"avg_{s}_mw_h{h:02d}"] = sum(by_hour[h]) / len(by_hour[h])
    net, solar = [out[f"avg_net_load_mw_h{h:02d}"] for h in range(24)], [out[f"avg_solar_mw_h{h:02d}"] for h in range(24)]
    out.update(rep.measures(net, solar))
    return out


def ranked_days(days, year, zone, last=None):
    """Each complete day of 24 local hours measured on its own hours; the ten with the most shoulder energy, ranked. The
    count is of the days that can be ranked: complete, 24 hours, and with a shoulder of at least one hour."""
    measured = {}
    for d, rows in days.items():
        if d.startswith(year) and (last is None or d[:7] <= last) and len(rows) == 24 and complete(rows, d, zone):
            rows = sorted(rows)
            m = rep.measures([x[1] - x[2] - x[3] for x in rows], [x[2] for x in rows])
            if m.get("shoulder_hours"):      # a day with no shoulder (0 hours) is not ranked and not counted
                if all(x[4] is not None for x in rows):
                    span = range(m["shoulder_start_hour"], m["shoulder_end_hour"])
                    m["battery_discharge_mwh"] = sum(max(0.0, rows[h][4]) for h in span)
                measured[d] = m
    ten = sorted(measured, key=lambda d: (-measured[d]["shoulder_mwh_above_mean"], d))[:10]
    return len(measured), [(i + 1, d, measured[d]) for i, d in enumerate(ten)]


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workbook", action="append", default=[], help="BA=path, for ERCO and CISO")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--months", action="append", default=[])
    ap.add_argument("--years", action="append", default=[])
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv[1:])
    books = dict(w.split("=", 1) for w in a.workbook)
    months = {e: v.split(",") for e, v in (x.split("=", 1) for x in a.months)} or DEFAULT_MONTHS
    years = {e: v.split(",") for e, v in (x.split("=", 1) for x in a.years)} or DEFAULT_YEARS
    in_dir = a.in_dir or os.path.join(rep.ROOT, "warehouse", "output")
    try:
        T = rep.Tables(in_dir)
    except OSError as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    rows, sample = [], []

    def one(entity, variable, date, got):
        held = T.t.get((entity, variable, date))
        if got is None and held is None:
            return
        ok = got is not None and held is not None and abs(got - held) <= TOL
        rows.append((entity, variable, date, got, held, ok))

    for entity in sorted(set(months) | set(years)):
        ba, zone = BA[entity]
        if ba not in books:
            print(f"{entity}: no workbook named for {ba}; not recomputed")
            continue
        try:
            days = hours(books[ba], zone, ba)
        except (OSError, KeyError, ValueError) as exc:
            print(f"the workbook of {ba} could not be read: {exc}")
            return 2
        for month in months.get(entity, []):
            before = len(rows)
            m = average_day(days, month, zone)
            for v, x in m.items():
                if v in ("shoulder2_level_mw",) or v.startswith(("avg_", "days_", "net_load", "midday", "shoulder", "evening")):
                    one(entity, v, month + "-01", x)
            got = rows[before:]
            sample.append({"entity": entity, "month": month, "values": len(got), "inside": sum(1 for r in got if r[5])})
        for year in years.get(entity, []):
            before = len(rows)
            # session 7022: a workbook newer than the table holds days past the table's window (whole months to the
            # newest month the table holds), so the year is ranked only through that month, as the table's builder did
            held_months = sorted({d[:7] for (e, v, d) in T.t if e == entity and v.startswith("avg_demand_mw_h")})
            last = min(x for x in (LAST.get(entity), held_months[-1] if held_months else None) if x) if (LAST.get(entity) or held_months) else None
            n, ten = ranked_days(days, year, zone, last)
            one(entity, "year_days_ranked", year + "-01-01", n)
            held_ten = sorted(d for (e, v, d) in T.t if e == entity and v == "worst_rank" and d.startswith(year))
            rows.append((entity, "the ten days ranked", year, None, None, sorted(d for _, d, _ in ten) == held_ten))
            for rank, d, m in ten:
                one(entity, "worst_rank", d, rank)
                for v in ("shoulder_mwh_above_mean", "shoulder_hours", "shoulder_start_hour", "shoulder_runs_to_midnight", "net_load_mean_mw", "evening_peak_mw",
                          "shoulder2_hours", "shoulder2_start_hour", "shoulder2_end_hour", "shoulder2_mwh_above_midpoint", "battery_discharge_mwh"):
                    if v in m:
                        one(entity, "day_" + v, d, m[v])
            got = rows[before:]
            sample.append({"entity": entity, "year": year, "values": len(got), "inside": sum(1 for r in got if r[5])})
    bad = [r for r in rows if not r[5]]
    for s in sample:
        print(f"{s['entity']} {s.get('month') or s.get('year')}: {s['inside']} of {s['values']} values equal the table's rows")
    for e, v, d, got, held, _ in bad[:40]:
        print(f"DIFFERS {e} {v} {d}: from the hours {got}, the table {held}")
    print(f"{len(rows) - len(bad)} of {len(rows)} values recomputed from the hourly data equal the table's rows (to {TOL})")
    if a.write:
        with open(os.path.join(HERE, "hourly_sample.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"_about": "A sample of shoulder_hours_monthly recomputed from EIA-930's hourly workbooks (replication/shoulder/from_hourly.py): by grid and month, "
                                 "the average day hour by hour and its measures; by grid and year, the days ranked and the ten days' own measures.",
                       "workbooks": {k: os.path.basename(v) for k, v in books.items()}, "tolerance": TOL, "values": len(rows), "equal": len(rows) - len(bad),
                       "sample": sample, "differences": [{"entity": e, "variable": v, "date": d, "from_the_hours": got, "the_table": held} for e, v, d, got, held, _ in bad]}, f, indent=1)
            f.write("\n")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
