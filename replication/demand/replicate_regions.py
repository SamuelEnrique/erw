"""Energy Research Warehouse (ERW), session 8450 (chain 503, part E): the replication of "The whole country", the
fourth view of /demand (/demand?view=country).

Written from the method note (docs/methods/demand_growth.md, the section "The whole country", with its lines "Every
figure, in the view's order") and the contract of the files (docs/state/page_files_regions.md, sections 2 and 3) alone,
not from the page's code. Standard library only.

For each region and balancing authority whose file is on the site (site/data/regions/demand/<region>.json and
demand/ba/<code>.json, with index.json, written by the data machine from EIA's Form EIA-930), every figure the view
prints is recomputed here from the files and set beside the figure the site's own code draws (a figures file written
by site/scripts/demand-regions-figures.mjs):

- the summary of a place: the first and the last whole year's average and highest hour, their growth, the year so far;
- demand by day: the days drawn and those that hold a whole day's demand, the days of most and least demand, the
  highest hour, the two points a day of the chart (the highest hour, and the day's MWh over its hours used), and the
  newest seven days;
- year by year: each whole year's row and the year so far's, the chart's hovers, the hours left out;
- where the growth is: every cell by month and hour, the largest and the smallest, the bars by month and by hour;
- with the weather taken out: each year's figure for the figure chosen, the chart's year, the check on the fit's years;
- a region beside its grid: both averages and the difference by year, and in how many years the two differ;
- the tables at the foot: how many balancing authorities the index gives each region, and how many it lists.

A figure passes when ours is within half the last digit the page shows. A figure the rule gives that the page does not
show fails too, and so does a figure the page shows that the rule does not give. Exit 0 when every figure of every
view passes (also when no file is on the site yet: nothing to compare, said so), 1 when one does not, 2 on bad input.

    python replication/demand/replicate_regions.py --figures <figures.json> [--files <the folder of the page files>]
                                                   [--strict]

After the count the script reads each file against itself and against the contract (the growth rows against the
averages they are formed from, the difference of a region and its grid against the two averages, the days in order
and each array as long as the days, a year's highest hour against its days' highest hours, a whole day against its
hours). What does not agree is printed as a note for the data machine and fails nothing, unless --strict is given: a
file's fault is not the page's.

No row of a warehouse table is read and nothing is written. The files are public (EIA's Form EIA-930, public domain);
a file whose license line is not "public", or that the figures file gives as held, is not recomputed: the page draws
no figure from it, and a figure drawn for it fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
FIGURES = ["energy", "summer_peak", "winter_peak", "overnight_min"]


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def parse(shown):
    """A figure as the page shows it ("+1,234.5", "-10.0", "14,400") as a number and the size of its last digit."""
    s = shown.replace(",", "").replace("+", "").strip()
    value = float(s)
    step = 10 ** -len(s.split(".")[1]) if "." in s else 1.0
    return value, step


def path_of(key):
    """The file of a place under the folder of the page files: a region "ten", a balancing authority "ba-tva"."""
    return os.path.join("demand", "ba", f"{key[3:]}.json") if key.startswith("ba-") else os.path.join("demand", f"{key}.json")


def at(arr, i):
    return arr[i] if isinstance(arr, list) and i < len(arr) else None


def pad(n):
    return str(n).zfill(2)


# ---- the rules of the note, line by line

def whole_years(growth):
    """The whole years of a file's growth object: the years that hold an average, in order."""
    years = (growth or {}).get("years") or {}
    return sorted(y for y, row in years.items() if num((row or {}).get("avg_demand_mw")))


def has_years(growth):
    """A file with no base year, no last whole year or no whole year gives no figure of the summary, the years or the
    months and hours."""
    return bool(growth) and num(growth.get("base")) and num(growth.get("last_year")) and bool(whole_years(growth))


def year_so_far(growth):
    """The year so far: the newest year of the rows, when it is after the last whole year, holds an average of the
    year so far, and the file names the month it runs to. Returns (year, row) or None."""
    years = growth.get("years") or {}
    through = growth.get("ytd_through")
    if not (isinstance(through, str) and len(through) == 7 and through[4] == "-" and through[:4].isdigit() and through[5:].isdigit()):
        return None
    newest = max(years)
    row = years[newest] or {}
    if not num(row.get("ytd_avg_demand_mw")) or int(newest) <= growth["last_year"]:
        return None
    return newest, row


def put(out, key, value):
    if num(value):
        out[key] = float(value)


def of_summary(out, k, growth):
    ys = whole_years(growth)
    years = growth["years"]
    first, last = years[ys[0]], years[ys[-1]]
    from_base = int(ys[0]) == growth["base"]
    put(out, f"{k}|sum|avg0", first["avg_demand_mw"])
    put(out, f"{k}|sum|avg1", last["avg_demand_mw"])
    if from_base:
        put(out, f"{k}|sum|avg_growth", last.get("avg_demand_growth_since_2019_pct"))
    if num(first.get("peak_demand_mw")) and num(last.get("peak_demand_mw")):
        put(out, f"{k}|sum|peak0", first["peak_demand_mw"])
        put(out, f"{k}|sum|peak1", last["peak_demand_mw"])
        if from_base:
            put(out, f"{k}|sum|peak_growth", last.get("peak_demand_growth_since_2019_pct"))
    ytd = year_so_far(growth)
    if ytd:
        put(out, f"{k}|sum|ytd_growth", ytd[1].get("ytd_avg_demand_growth_since_2019_pct"))


def of_years(out, k, file):
    growth = file["growth"]
    years = growth["years"]
    for y in whole_years(growth):
        row = years[y]
        for name, key in (("avg", "avg_demand_mw"), ("avg_growth", "avg_demand_growth_since_2019_pct"), ("yoy", "avg_demand_growth_yoy_pct"),
                          ("peak", "peak_demand_mw"), ("peak_growth", "peak_demand_growth_since_2019_pct"), ("hours", "hours_used")):
            put(out, f"{k}|y|{y}|{name}", row.get(key))
        put(out, f"{k}|tip|year|{y}|avg", row.get("avg_demand_mw"))
        put(out, f"{k}|tip|year|{y}|peak", row.get("peak_demand_mw"))
    ytd = year_so_far(growth)
    if ytd:
        row = ytd[1]
        for name, key in (("avg", "ytd_avg_demand_mw"), ("avg_growth", "ytd_avg_demand_growth_since_2019_pct"), ("peak", "ytd_peak_demand_mw"),
                          ("peak_growth", "ytd_peak_demand_growth_since_2019_pct"), ("hours", "ytd_hours_used")):
            put(out, f"{k}|y|ytd|{name}", row.get(key))
    s = file.get("screened") or {}
    if all(num(s.get(x)) for x in ("jumps", "not_positive", "blank")):
        out[f"{k}|screen|jumps"] = float(s["jumps"])
        out[f"{k}|screen|zero"] = float(s["not_positive"])
        out[f"{k}|screen|blank"] = float(s["blank"])


def of_months_and_hours(out, k, growth):
    row = (growth["years"].get(str(int(growth["last_year"]))) or {})
    cells = []
    for m in range(1, 13):
        for h in range(24):
            pct, mw = row.get(f"growth_pct_m{pad(m)}_h{pad(h)}"), row.get(f"growth_mw_m{pad(m)}_h{pad(h)}")
            if num(pct) and num(mw):
                cells.append((pct, mw))
                out[f"{k}|tip|cell|{m}|{h}|pct"] = float(pct)
                out[f"{k}|tip|cell|{m}|{h}|mw"] = float(mw)
        put(out, f"{k}|tip|month|{m}|pct", row.get(f"growth_pct_m{pad(m)}"))
    for h in range(24):
        put(out, f"{k}|tip|hour|{h}|pct", row.get(f"growth_pct_h{pad(h)}"))
    if cells:
        most, least = cells[0], cells[0]
        for c in cells[1:]:            # the first in the order of months then hours when two are equal
            if c[0] > most[0]:
                most = c
            if c[0] < least[0]:
                least = c
        out[f"{k}|cell|most|pct"], out[f"{k}|cell|most|mw"] = float(most[0]), float(most[1])
        out[f"{k}|cell|least|pct"], out[f"{k}|cell|least|mw"] = float(least[0]), float(least[1])


def drawn_days(daily, days):
    """The positions of the days drawn: every day, or those of the year chosen."""
    return [i for i, d in enumerate(daily.get("days") or []) if days == "all" or d.startswith(f"{days}-")]


def of_days(out, k, daily, days, points):
    pos = drawn_days(daily, days)
    if not pos:
        return
    mwh = [at(daily.get("demand_mwh"), i) for i in pos]
    peak = [at(daily.get("peak_mw"), i) for i in pos]
    held = [v for v in mwh if num(v)]
    out[f"{k}|day|days"] = float(len(pos))
    out[f"{k}|day|held"] = float(len(held))
    if held:
        out[f"{k}|day|top_gwh"] = max(held) / 1000
        out[f"{k}|day|low_gwh"] = min(held) / 1000
    tops = [v for v in peak if num(v)]
    if tops:
        out[f"{k}|day|top_mw"] = float(max(tops))
    if points:
        for i in pos:
            day, p, e, h = daily["days"][i], at(daily.get("peak_mw"), i), at(daily.get("demand_mwh"), i), at(daily.get("hours"), i)
            if num(p):
                out[f"{k}|pt|{day}|peak"] = float(p)
            if num(e) and num(h) and h > 0:
                out[f"{k}|pt|{day}|avg"] = e / h


def of_newest(out, drawn, n):
    """The newest days: of the days each drawn place's last n positions name, the n newest; for each, a place's demand
    and highest hour where its file holds them."""
    days = set()
    for _, file in drawn:
        days.update(((file.get("daily") or {}).get("days") or [])[-n:])
    for day in sorted(days, reverse=True)[:n]:
        for k, file in drawn:
            daily = file.get("daily") or {}
            all_days = daily.get("days") or []
            if day not in all_days:
                continue
            i = len(all_days) - 1 - all_days[::-1].index(day)
            e, p = at(daily.get("demand_mwh"), i), at(daily.get("peak_mw"), i)
            if num(e):
                out[f"{k}|new|{day}|gwh"] = e / 1000
            if num(p):
                out[f"{k}|new|{day}|mw"] = float(p)


def fit_years(weather):
    """The years a region's fit was made on: the file's train line, else the years its holdout is keyed by."""
    if not weather:
        return []
    train = weather.get("train")
    if isinstance(train, list) and train:
        return sorted(int(y) for y in train)
    return sorted(int(y) for y in (weather.get("holdout") or {}) if str(y).isdigit())


def last_whole_year(with_weather, years):
    """The last whole year of the weather view: the newest year held when it runs to 31 December, else the newest year
    before it. Over two places: the largest newest year, partial when a place at that year stops before 31 December."""
    newest = max(w["newest"] for _, w in with_weather)
    partial = any(w["newest"] == newest and str(w.get("through", "")) < "12-31" for _, w in with_weather)
    if not partial:
        return str(int(newest))
    before = [y for y in years if int(y) < newest]
    return before[-1] if before else years[-1]


def of_weather(out, drawn, figure, year_asked):
    with_weather = [(k, f["weather"]) for k, f in drawn if f.get("weather") and fit_years(f["weather"])]
    if not with_weather:
        return
    years = sorted({y for _, w in with_weather for y in (w.get("years") or {})})
    year = year_asked if year_asked in years else last_whole_year(with_weather, years)
    train = fit_years(with_weather[0][1])
    for k, w in with_weather:
        for y in years:
            g = ((w.get("years") or {}).get(y) or {}).get(figure)
            if not g:
                continue
            put(out, f"{k}|w|{y}|mw", g.get("actual"))
            put(out, f"{k}|w|{y}|g", g.get("growth_pct"))
            put(out, f"{k}|w|{y}|w", g.get("weather_pct"))
            put(out, f"{k}|w|{y}|u", g.get("unexplained_pct"))
            put(out, f"{k}|w|{y}|pm", g.get("uncertainty_pct"))
            if y == year:
                put(out, f"{k}|tip|w|{y}|g", g.get("growth_pct"))
                put(out, f"{k}|tip|w|{y}|w", g.get("weather_pct"))
                put(out, f"{k}|tip|w|{y}|u", g.get("unexplained_pct"))
                put(out, f"{k}|tip|w|{y}|pm", g.get("uncertainty_pct"))
        for y in train:
            h = ((w.get("holdout") or {}).get(str(y)) or {}).get(figure)
            if h:
                put(out, f"{k}|h|{y}", h.get("unexplained_pct"))
        fit = w.get("fit") or {}
        put(out, f"{k}|h|hour", fit.get("oos_mape_pct"))
        put(out, f"{k}|h|day", fit.get("oos_daily_mape_pct"))


def of_alike(out, k, alike):
    years = (alike or {}).get("years") or {}
    if not years:
        return
    both = apart = 0
    for y in sorted(years):
        r = years[y] or {}
        region, grid, pct = r.get("region_avg_demand_mw"), r.get("grid_avg_demand_mw"), r.get("difference_pct")
        put(out, f"{k}|alike|{y}|region", region)
        put(out, f"{k}|alike|{y}|grid", grid)
        put(out, f"{k}|alike|{y}|pct", pct)
        if num(region) and num(grid):
            both += 1
            # the two differ when their whole MW differ, or the file's difference is held and not zero
            if int(region + 0.5) != int(grid + 0.5) or (num(pct) and pct != 0):
                apart += 1
    if both:
        out[f"{k}|alike|apart" if apart else f"{k}|alike|years"] = float(apart if apart else both)


def expected(view, files, newest_days):
    """Our own figures of one drawn view, keyed as the page keys them, each a float."""
    out = {}
    marks = [("a", view["a"])] + ([("b", view["b"])] if view.get("b") else [])
    drawn = [(f"cd|{m}", files[key]) for m, key in marks if key in files]
    for k, file in drawn:
        growth = file.get("growth")
        if has_years(growth):
            of_summary(out, k, growth)
            of_years(out, k, file)
            of_months_and_hours(out, k, growth)
        if (file.get("daily") or {}).get("days"):
            of_days(out, k, file["daily"], view.get("days") or "all", view["kind"] == "place")
        of_alike(out, k, file.get("alike"))
    of_newest(out, drawn, newest_days)
    of_weather(out, drawn, view.get("figure") or FIGURES[0], view.get("year") or "")
    keeps, drops = view.get("keeps"), view.get("drops") or []
    part = lambda key: "|".join(key.split("|")[2:])
    return {key: v for key, v in out.items() if (not keeps or any(part(key).startswith(p) for p in keeps)) and not any(part(key).startswith(p) for p in drops)}


def of_index(index):
    out = {}
    for r in index.get("regions") or []:
        if isinstance(r.get("bas"), list):
            out[f"index|{r['code']}|bas"] = float(len(r["bas"]))
    if index.get("bas"):
        out["index|bas"] = float(len(index["bas"]))
    return out


def compare(name, figures, ours):
    """(passed, total) of one set of figures against ours, the failures printed."""
    n = ok = 0
    for key, shown in sorted(figures.items()):
        n += 1
        if key not in ours:
            print(f"  FAIL {name} {key}: the page shows {shown}, the file gives no figure by the note's rule")
            continue
        try:
            value, step = parse(shown)
        except ValueError:
            print(f"  FAIL {name} {key}: the page shows {shown!r}, which is not a number")
            continue
        if abs(value - ours[key]) <= step / 2 + 1e-9:
            ok += 1
        else:
            print(f"  FAIL {name} {key}: the page shows {shown}, ours {ours[key]:.6f}")
    for key in sorted(k for k in ours if k not in figures):
        n += 1
        print(f"  FAIL {name} {key}: ours {ours[key]:.6f}, not on the page")
    return ok, n


# ---- a file against itself and against the contract: notes for the data machine

def day_hours(day, tz):
    """How many hours a local day has in its zone (23 or 25 when the clocks change), or None without the zone data."""
    try:
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(tz)
    except Exception:
        return None
    d = dt.date.fromisoformat(day)
    start = dt.datetime(d.year, d.month, d.day, tzinfo=zone)
    nxt = d + dt.timedelta(days=1)
    end = dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=zone)
    return round((end.astimezone(dt.timezone.utc) - start.astimezone(dt.timezone.utc)).total_seconds() / 3600)


def local_day(ts, tz):
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ZoneInfo(tz)).date().isoformat()
    except Exception:
        return None


def inner(key, file):
    """(agreeing, checked, notes) of one file read against itself. A growth is formed from two averages the file writes
    to a tenth of a MW, so it is allowed the half tenth of each."""
    notes = []
    n = ok = 0

    def check(cond, words):
        nonlocal n, ok
        n += 1
        if cond:
            ok += 1
        else:
            notes.append(f"  note {key}: {words}")

    def pct_ok(shown, new, old):
        slack = 0.005 + 100 * (0.05 / abs(old) + 0.05 * abs(new) / (old * old))
        return abs(shown - (new - old) / old * 100) <= slack + 1e-9

    growth = file.get("growth") or {}
    years = growth.get("years") or {}
    base = years.get(str(int(growth["base"]))) if num(growth.get("base")) else None
    for y in whole_years(growth):
        row = years[y]
        for measure, since, mw in (("avg_demand_mw", "avg_demand_growth_since_2019_pct", "avg_demand_growth_since_2019_mw"),
                                   ("peak_demand_mw", "peak_demand_growth_since_2019_pct", "peak_demand_growth_since_2019_mw")):
            if base and num(base.get(measure)) and num(row.get(measure)) and base[measure]:
                if num(row.get(since)):
                    check(pct_ok(row[since], row[measure], base[measure]), f"{y} {since} is {row[since]}, the two {measure} give {(row[measure] - base[measure]) / base[measure] * 100:.2f}")
                if num(row.get(mw)):
                    check(abs(row[mw] - (row[measure] - base[measure])) <= 0.051, f"{y} {mw} is {row[mw]}, the two {measure} give {row[measure] - base[measure]:.1f}")
        before = years.get(str(int(y) - 1)) or {}
        if num(row.get("avg_demand_growth_yoy_pct")) and num(before.get("avg_demand_mw")) and before["avg_demand_mw"]:
            check(pct_ok(row["avg_demand_growth_yoy_pct"], row["avg_demand_mw"], before["avg_demand_mw"]), f"{y} avg_demand_growth_yoy_pct is {row['avg_demand_growth_yoy_pct']}, the two averages give {(row['avg_demand_mw'] - before['avg_demand_mw']) / before['avg_demand_mw'] * 100:.2f}")
    alike = (file.get("alike") or {}).get("years") or {}
    for y, r in sorted(alike.items()):
        region, grid, pct = r.get("region_avg_demand_mw"), r.get("grid_avg_demand_mw"), r.get("difference_pct")
        if num(region) and num(grid) and num(pct) and grid:
            check(pct_ok(pct, region, grid), f"alike {y} difference_pct is {pct}, the region's less the grid's over the grid's is {(region - grid) / grid * 100:.2f}")
        own = (years.get(y) or {}).get("avg_demand_mw")
        if num(region) and num(own):
            check(abs(region - own) <= 0.051, f"alike {y} gives the region {region} MW, its own year row {own} MW")
    daily = file.get("daily") or {}
    days = daily.get("days") or []
    if days:
        check(all(isinstance(daily.get(a), list) and len(daily[a]) == len(days) for a in ("demand_mwh", "peak_mw", "peak_at", "hours")), "an array of daily is not as long as its days")
        gaps = sum(1 for a, b in zip(days, days[1:]) if dt.date.fromisoformat(b) - dt.date.fromisoformat(a) != dt.timedelta(days=1))
        check(gaps == 0, f"{gaps} breaks in the order of the days (the contract: every local day from the first held to the last)")
        tz = file.get("tz") or ""
        odd_whole = odd_at = 0
        seen = False
        for i, day in enumerate(days):
            e, h, p, when = at(daily.get("demand_mwh"), i), at(daily.get("hours"), i), at(daily.get("peak_mw"), i), at(daily.get("peak_at"), i)
            length = day_hours(day, tz)
            if length is not None and num(h):
                seen = True
                if num(e) != (h == length):
                    odd_whole += 1
            if num(p) and isinstance(when, str):
                where = local_day(when, tz)
                if where is not None and where != day:
                    odd_at += 1
        if seen:
            check(odd_whole == 0, f"{odd_whole} days whose demand is held without all the day's hours used, or not held with all of them")
            check(odd_at == 0, f"{odd_at} days whose highest hour (peak_at) is not an hour of that local day in {tz}")
        by_year = {}
        for i, day in enumerate(days):
            by_year.setdefault(day[:4], []).append(i)
        for y in whole_years(growth):
            pos = by_year.get(y) or []
            row = years[y]
            covered = pos and days[pos[0]] == f"{y}-01-01" and days[pos[-1]] == f"{y}-12-31"
            tops = [at(daily.get("peak_mw"), i) for i in pos if num(at(daily.get("peak_mw"), i))]
            if covered and tops and num(row.get("peak_demand_mw")):
                check(max(tops) <= row["peak_demand_mw"] + 0.051, f"{y}: a day's highest hour ({max(tops)} MW) is above the year's ({row['peak_demand_mw']} MW)")
            used = [at(daily.get("hours"), i) for i in pos]
            if covered and all(num(v) for v in used) and num(row.get("hours_used")):
                check(sum(used) == row["hours_used"], f"{y}: the days' hours used add to {sum(used)}, the year's hours_used is {row['hours_used']}")
    return ok, n, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", required=True)
    ap.add_argument("--files", default=os.path.join(ROOT, "site", "data", "regions"))
    ap.add_argument("--strict", action="store_true", help="a file that does not agree with itself fails the run")
    a = ap.parse_args()
    try:
        with open(a.figures, encoding="utf-8") as f:
            page = json.load(f)
        places, views, newest_days = page["places"], page["views"], int(page["newest_days"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"the figures file cannot be read: {e}")
        return 2
    files = {}
    for key, drawn in sorted(places.items()):
        where = os.path.join(a.files, path_of(key))
        if not drawn.get("file") or not os.path.exists(where):
            continue
        try:
            with open(where, encoding="utf-8") as f:
                file = json.load(f)
        except (OSError, ValueError) as e:
            print(f"the file of {key} cannot be read: {e}")
            return 2
        if file.get("license", "public") != "public" or drawn.get("held"):
            print(f"{key}: the file is not public, not recomputed (the page draws no figure)")
            continue
        files[key] = file
    if not any(d.get("file") for d in places.values()):
        print("no place's file is on the site yet: nothing to recompute")
        return 0
    total = passed = 0
    by_kind = {}
    for v in views:
        name = f"{v['kind']} {v['a']}{' and ' + v['b'] if v.get('b') else ''}" + (f" days={v['days']}" if v["kind"] == "days" else "") \
            + (f" {v['figure']}" if v["kind"] == "figure" else "") + (f" year={v['year']}" if v["kind"] == "year" else "")
        for key in v.get("clashes") or []:
            total += 1
            print(f"  FAIL {name} {key}: drawn twice with two values")
        ok, n = compare(name, v["figures"], expected(v, files, newest_days))
        total += n
        passed += ok
        k = by_kind.setdefault(v["kind"], [0, 0, 0])
        k[0] += 1
        k[1] += ok
        k[2] += n
    index_at = os.path.join(a.files, "index.json")
    if page.get("index", {}).get("file") and os.path.exists(index_at):
        with open(index_at, encoding="utf-8") as f:
            ok, n = compare("the tables at the foot", page["index"].get("figures") or {}, of_index(json.load(f)))
        total += n
        passed += ok
        print(f"the tables at the foot: {ok} of {n} figures")
    for kind, (count, ok, n) in by_kind.items():
        print(f"{kind}: {ok} of {n} figures over {count} views")
    print(f"{passed} of {total} figures over {len(views)} views of {len(files)} places")
    agree = checked = 0
    for key, file in sorted(files.items()):
        ok, n, notes = inner(key, file)
        agree += ok
        checked += n
        for line in notes[:12]:
            print(line)
        if len(notes) > 12:
            print(f"  note {key}: and {len(notes) - 12} more")
    print(f"the files against themselves: {agree} of {checked} checks agree")
    if passed != total:
        return 1
    return 1 if a.strict and agree != checked else 0


if __name__ == "__main__":
    sys.exit(main())
