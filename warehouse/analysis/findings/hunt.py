#!/usr/bin/env python3
"""The weekly hunt for deeper findings (session 233): the hand-built findings as a library of patterns that runs by itself.

Energy Research Warehouse (ERW). Samuel's ruling of 12 October 2026: deeper findings are hunted automatically and
published only after he approves them at /internal/findings (he runs the Stata first). Nothing posts to LinkedIn: the
tool prepares the image and the caption for him. Method: docs/methods/automated_analysis_findings.md, "The weekly hunt".

A finding of this folder was written once, for one grid and one question. A PATTERN below is that question asked of
every region the finding's own code can compute: its module is run on this machine's newest tables, the measure is read
by year for each region from the module's own rows, and three tests decide whether what it shows is worth a person's
time. No model is called and no sentence is written by one: the fact, the callouts, the caption and the files are
computed from the numbers.

    the claim        the measure in the last full year against the first full year, for one region
    test 1, years    "holds in more than one year": at least two full years after the first lie on the claim's side
                     of the first year's value
    test 2, window   "survives a change of window": the direction is the same when the window starts a year later and
                     when it ends a year earlier (four full years needed)
    test 3, sample   "sample large enough": the first and the last year are complete (each holds at least 90 percent
                     of the fullest year's observations, and at least the pattern's floor)
    new or changed   a claim is drafted when it passes the three tests and is new, or its change moved by more than the
                     pattern's threshold since the last hunt, or its last full year is a newer one
                     (runs/hunt/state.json is the memory)
    how many         the strongest first (the change in typical year-to-year moves of the measure), at most
                     MAX_PER_PATTERN regions of one pattern and MAX_DRAFTS drafts a hunt; two patterns that read the
                     same numbers are drafted once. What is left out stays in runs/hunt/<date>/hunt.json, with its reason

Only public-licensed publishers: a region of a grid that license_status.csv marks "license needed" (ISO-NE, MISO,
NYISO) or that a ruling holds (daily_chart.HELD: NYISO, SPP) is never drafted. The module may read those tables to
compute its other regions; nothing of them leaves the machine.

A draft is a row of public.scanner_drafts (rule "hunt", migration 031) with its card (chart, callouts, numbers,
footnote) and its files: the CSV, a Stata do-file, a Python mirror, the two LinkedIn pictures (1200 x 627 and
1080 x 1080) and the caption. It waits at /internal/findings. Approved, it appears on /analysis and can be chosen for
the Roundup (roundup_pick.py reads an approved draft's card).

    python warehouse/analysis/findings/hunt.py --weekly               # the Saturday task: run, test, draft, load
    python warehouse/analysis/findings/hunt.py --dry-run              # run and test; write runs/hunt/<date>/; load nothing
    python warehouse/analysis/findings/hunt.py --only negative_prices # one pattern
    python warehouse/analysis/findings/hunt.py --list                 # the library, and what is not in it yet
    python warehouse/analysis/findings/hunt.py --fix-source-lines --dry-run   # session 258: the stored drafts' source lines

A draft's source line (session 258): it names the tables that brought its region's rows in the claim's years, read
from what the finding read on this run (tables_used), and no table the finding read for another grid.

Exit 0 ran (whatever it found), 1 failed, 2 bad input.

Session 251, 13 October 2026: from 7 patterns to 20. Thirteen pattern families are measures the hunt computes itself
(hunt_measures.py: a pattern with "fn"), each for every public grid and region it applies to, some with a second
number of the same region and year printed beside the claim ("context": stated, never tested). Session 252's two
lessons: a pattern whose measure is one interval of a year ("one_interval") is computed and kept in the run's file and
never drafted; and a draft's source line names only the tables its own region's rows come from (OWN_TABLES for a
finding's pattern, the measure's own list for a family).
"""

import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import daily_chart  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures  # noqa: E402
import run_finding  # noqa: E402

VERSION = "1.1.0"                  # 1.1.0, session 251: thirteen measure families; session 252's two lessons
OUT = os.path.join(ROOT, "runs", "hunt")
STATE = os.path.join(OUT, "state.json")
MAX_DRAFTS = 12                    # the strongest claims of a hunt; the rest are kept in the run's file, not drafted
MAX_PER_PATTERN = 2                # of one pattern: six hubs of one grid tell one story, and the two strongest tell it
FULL_SHARE = 0.90                  # a full year holds this share of the fullest year's observations
METHOD = "docs/methods/automated_analysis_findings.md"
GRID_WORDS = {"ercot": "ERCOT", "caiso": "CAISO", "pjm": "PJM", "nyiso": "NYISO", "isone": "ISO-NE", "miso": "MISO", "spp": "SPP"}
LICENSE_GRIDS = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "SPP": "spp", "PJM": "pjm", "ERCOT": "ercot", "CAISO": "caiso"}

# The library. module: the finding whose compute() is run. sweep: an input run once per choice (each choice a region).
# region_col: the rows' column that names the region (None: the swept input is the region). year_col, filter: which
# rows are a year's. measure: the column read. n_col, n_floor: the sample and its floor. change_threshold: how far the
# change must move, in the measure's unit, before a claim drafted before is drafted again.
PATTERNS = [
    dict(name="spikes_against_median", module="batteries_lunch", sweep="hub", region_col=None, year_col="period", filter={"kind": "year"},
         measure="worst_interval_multiple", n_col="n_intervals", n_floor=30000, unit="times the median", decimals=1, change_threshold=10.0, one_interval=True,
         title="THE WORST PRICE SPIKE AGAINST THE MEDIAN", label="the year's dearest interval as a multiple of the year's median real-time price"),
    dict(name="spikes_against_median_grids", module="batteries_lunch_grids", sweep=None, region_col="grid", year_col="period", filter={"kind": "year"},
         measure="worst_interval_multiple", n_col="n_intervals", n_floor=8000, unit="times the median", decimals=1, change_threshold=10.0, one_interval=True,
         title="THE WORST PRICE SPIKE AGAINST THE MEDIAN", label="the year's dearest interval as a multiple of the year's median real-time price"),
    dict(name="hours_above_1000", module="batteries_lunch_grids", sweep=None, region_col="grid", year_col="period", filter={"kind": "year"},
         measure="hours_ge_1000", n_col="n_intervals", n_floor=8000, unit="hours", decimals=1, change_threshold=5.0,
         title="HOURS ABOVE USD 1,000", label="hours of the year with a real-time price of USD 1,000 per MWh or more"),
    dict(name="gas_sets_price", module="gas_sets_price", sweep=None, region_col="grid", year_col="year", filter=None,
         measure_tables=["eia_fuel_spot_prices"],          # session 258: the measure is a price against Henry Hub's
         measure="share_below_hr7", n_col="n_hours", n_floor=8000, unit="percent of hours", decimals=1, change_threshold=3.0,
         title="HOURS PRICED BELOW A GAS PLANT'S FUEL COST", label="share of the year's hours with the real-time price below a 7.0 heat rate times Henry Hub"),
    dict(name="negative_prices", module="negative_prices_west", sweep=None, region_col="hub", year_col="year", filter=None, words_col="words",
         measure="share_pct", n_col="n_hours", n_floor=8000, unit="percent of hours", decimals=2, change_threshold=1.0,
         title="HOURS WITH A PRICE BELOW ZERO", label="share of the year's hours with a real-time price below zero"),
    dict(name="peak_hour_evening", module="peak_hour_grids", sweep=None, region_col="grid", year_col="year", filter=None,
         measure="share_evening_pct", n_col="n_days", n_floor=330, unit="percent of days", decimals=1, change_threshold=5.0,
         title="THE DAY'S DEAREST HOUR FALLS IN THE EVENING", label="share of the year's days whose highest real-time price fell in the evening"),
    dict(name="peak_hour_midday", module="peak_hour_grids", sweep=None, region_col="grid", year_col="year", filter=None,
         measure="share_midday_pct", n_col="n_days", n_floor=330, unit="percent of days", decimals=1, change_threshold=5.0,
         title="THE DAY'S DEAREST HOUR FALLS AT MIDDAY", label="share of the year's days whose highest real-time price fell at midday"),
]


def family(name, fn, unit, decimals, n_floor, change_threshold, title, label, context=None):
    """A pattern of session 251: a measure by region and year that hunt_measures.<fn> computes from warehouse tables.
    context: {"label", "unit", "decimals"} of the second number printed beside the claim, when the family has one."""
    return dict(name=name, module="hunt_measures", fn=fn, sweep=None, region_col="region", year_col="year", filter=None, words_col="words",
                measure="value", n_col="n", n_floor=n_floor, unit=unit, decimals=decimals, change_threshold=change_threshold, title=title, label=label,
                context=context)


PATTERNS += [
    family("solar_capture_rate", "solar_capture_rate", "percent of the average price", 1, 8000, 5.0, "SOLAR'S CAPTURE RATE",
           "what a solar plant earned per MWh as a percent of the year's time-weighted average price at the grid's hub",
           context={"label": "solar's share of the grid's generation", "unit": "percent", "decimals": 1}),
    family("evening_ramp", "evening_ramp", "MW per hour", 0, 8000, 200.0, "THE EVENING RAMP",
           "the median day's largest one-hour rise of net load between 2 PM and 10 PM local"),
    family("battery_evening_discharge", "battery_evening_discharge", "percent of discharge", 1, 8000, 5.0, "BATTERY DISCHARGE IN THE EVENING",
           "share of the year's battery discharge delivered from 5 PM to 10 PM local, the hours in which the day's dearest price most often falls"),
    family("implied_heat_rate", "implied_heat_rate", "MMBtu per MWh", 2, 200, 1.0, "THE IMPLIED HEAT RATE",
           "the median day's mean real-time price divided by that day's Henry Hub spot price"),
    family("negative_hours_zones", "negative_hours_zones", "percent of hours", 2, 8000, 1.0, "HOURS WITH A PRICE BELOW ZERO, BY ZONE",
           "share of the year's hours with a mean real-time price below zero"),
    family("da_rt_spread", "da_rt_spread", "USD per MWh", 2, 1000, 1.0, "DAY-AHEAD AGAINST REAL-TIME, BY PART OF THE DAY",
           "the median hour's day-ahead price minus its real-time price"),
    family("scarcity_hours", "scarcity_hours", "percent of hours", 1, 8000, 3.0, "HOURS WITH A RESERVE ADDER ABOVE ZERO",
           "share of the year's hours with ERCOT's on-line reserve price adder (RTORPA) above zero",
           context={"label": "the year's mean demand", "unit": "MW", "decimals": 0}),
    family("curtailment_share", "curtailment_share", "percent of output", 2, 8000, 0.5, "WIND AND SOLAR CURTAILED",
           "share of the year's wind and solar output that was curtailed",
           context={"label": "operating batteries at the year's end", "unit": "MW", "decimals": 0}),
    family("stress_day_imports", "stress_day_imports", "percent of demand", 1, 330, 3.0, "NET IMPORTS ON STRESS DAYS",
           "net imports as a percent of demand on the year's stress days, its 5 percent of days with the highest demand"),
    family("demand_growth_weather_adjusted", "demand_growth_weather_adjusted", "percent above the 2019 to 2021 base", 1, 8000, 2.0,
           "DEMAND GROWTH THAT WEATHER DOES NOT EXPLAIN", "the year's energy above the 2019 to 2021 base that temperature does not explain"),
    family("peak_hour_carbon", "peak_hour_carbon", "percent above the all-hours mean", 1, 8000, 2.0, "THE CARBON OF THE EVENING PEAK",
           "carbon intensity of the electricity used from 5 PM to 10 PM local against the year's all-hours mean"),
    family("wind_night_share", "wind_night_share", "percent of generation", 1, 330, 2.0, "WIND'S SHARE OF THE NIGHT",
           "wind's share of the grid's generation from midnight to 6 AM local",
           context={"label": "the median night hour's real-time price minus the median hour's", "unit": "USD per MWh", "decimals": 2}),
    family("record_days", "record_days", "days", 0, 330, 2.0, "RECORD-SETTING DAYS",
           "days of the year with demand above the highest day of every earlier year held"),
]
# Session 252's second lesson, for the patterns that read a finding: the tables a grid's own rows of the measure come
# from. A finding's TABLES names every table it reads for every grid and for its regressors; a draft names these.
PRICES_ERCOT = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices"]
PRICES_CAISO = ["iso_hub_prices_history", "iso_rtm_hub_prices"]
OWN_TABLES = {
    "batteries_lunch": {"ercot": PRICES_ERCOT},
    "batteries_lunch_grids": {"ercot": PRICES_ERCOT, "caiso": PRICES_CAISO},
    "gas_sets_price": {"ercot": PRICES_ERCOT + ["eia_fuel_spot_prices"], "caiso": ["iso_rtm_hub_prices", "eia_fuel_spot_prices"]},
    "negative_prices_west": {"ercot": PRICES_ERCOT},
    "peak_hour_grids": {"ercot": PRICES_ERCOT, "caiso": PRICES_CAISO},
}
# The findings of this folder that are not patterns yet, each with the reason. A pattern here must be a measure by
# region and by year; these are another kind of claim, and their three tests have to be written for that kind first.
NOT_YET = {
    "queue_divorce": "a level by technology over one cohort of requests, not a measure by year: its tests (the level across cohorts) are not written",
    "who_rescues_whom": "one event is one episode: 'holds in more than one year' has to be defined across events before it can be tested",
    "batteries_curtailment": "a regression coefficient over 14 months: its tests (the coefficient by year, the sample by month) need two full years of CAISO's battery intervals",
    "batteries_curtailment_hourly": "a regression coefficient by hour: its tests (the coefficient year by year, which the card already says does not hold in every year) are not written as a pattern",
    "peak_hour_moved": "covered by peak_hour_grids, which computes the same measure for every grid (ERCOT and CAISO among them)",
    "impact_study": "needs an event or a date chosen by a person: it is asked for at /analysis, not hunted",
}


# ---------------------------------------------------------------------------------------------------------------------
# which regions may be drafted
# ---------------------------------------------------------------------------------------------------------------------
def grid_of(region):
    r = str(region).lower()
    return "ercot" if r.startswith("hb_") else re.split(r"[_:]", r)[0]


def blocked_grids(meta_dir=None):
    """The grids whose publisher needs a license (license_status.csv) or is held by a ruling (daily_chart.HELD)."""
    out = set(daily_chart.HELD)
    for r in daily_chart._csv(os.path.join(meta_dir or daily_chart.META_DIR, "license_status.csv")):
        if r.get("status") == "license needed":
            out |= {LICENSE_GRIDS[p.strip()] for p in r.get("publishers", "").split(";") if p.strip() in LICENSE_GRIDS}
    return out


def region_words(P, region, rows):
    if P.get("words_col"):
        w = next((r.get(P["words_col"]) for r in rows if str(r.get(P["region_col"])) == region and r.get(P["words_col"])), None)
        if w:
            return str(w)
    if str(region).startswith("HB_"):
        return f"ERCOT, {region}"
    return GRID_WORDS.get(str(region).lower(), str(region))


# ---------------------------------------------------------------------------------------------------------------------
# the measure by year, and the three tests
# ---------------------------------------------------------------------------------------------------------------------
def _number(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else f


def yearly(rows, P, region):
    """{year: (value, n)} for a region, from the module's own rows. A year's first row is taken (the peak-hour rows
    repeat a year's figures on each of its 24 hour rows)."""
    out = {}
    for r in rows:
        if P.get("filter") and any(str(r.get(k)) != str(v) for k, v in P["filter"].items()):
            continue
        if P.get("region_col") and str(r.get(P["region_col"])) != str(region):
            continue
        y = str(r.get(P["year_col"]))
        y = y[:-2] if re.fullmatch(r"\d{4}\.0", y) else y
        v, n = _number(r.get(P["measure"])), _number(r.get(P["n_col"]))
        if re.fullmatch(r"\d{4}", y) and v is not None and n is not None and y not in out:
            out[y] = (v, n)
    return dict(sorted(out.items()))


def full_years(series, P, this_year):
    """The years that are whole: not the year under way, and holding FULL_SHARE of the fullest year's observations."""
    if not series:
        return []
    most = max(n for _, n in series.values())
    return [y for y, (_, n) in series.items() if int(y) < int(this_year) and n >= FULL_SHARE * most]


def sign(x):
    return (x > 0) - (x < 0)


def spread(values):
    """The robust size of a typical year-to-year move: 1.4826 times the median absolute first difference."""
    d = sorted(abs(b - a) for a, b in zip(values, values[1:]))
    if not d:
        return 0.0
    m = d[len(d) // 2] if len(d) % 2 else (d[len(d) // 2 - 1] + d[len(d) // 2]) / 2
    return 1.4826 * m


def test_claim(series, P, this_year):
    """The claim for one region and its three tests. None when there is no claim to test (fewer than two full years,
    or no change). Returns {first_year, last_year, first, last, change, direction, tests: [{name, passed, words}],
    passed, strength, years, values}."""
    full = full_years(series, P, this_year)
    if len(full) < 2:
        return None
    y0, y1 = full[0], full[-1]
    v0, v1 = series[y0][0], series[y1][0]
    change = v1 - v0
    if change == 0:
        return None
    s = sign(change)
    later = full[1:]
    held = [y for y in later if sign(series[y][0] - v0) == s]
    t1 = {"name": "holds in more than one year", "passed": len(held) >= 2,
          "words": f"{len(held)} of the {len(later)} full years after {y0} lie {'above' if s > 0 else 'below'} {y0}'s value"}
    if len(full) >= 4:
        a, b = series[full[1]][0], series[full[-2]][0]
        ok = sign(v1 - a) == s and sign(b - v0) == s
        t2 = {"name": "survives a change of window", "passed": ok,
              "words": f"from {full[1]} to {y1} the change is {common.fmt(v1 - a, P['decimals'])}, from {y0} to {full[-2]} it is {common.fmt(b - v0, P['decimals'])}"}
    else:
        t2 = {"name": "survives a change of window", "passed": False, "words": f"only {len(full)} full years are held; four are needed to move the window"}
    n0, n1 = series[y0][1], series[y1][1]
    t3 = {"name": "sample large enough", "passed": min(n0, n1) >= P["n_floor"],
          "words": f"{y0} holds {common.fmt(n0, 0)} and {y1} holds {common.fmt(n1, 0)} observations; the floor is {common.fmt(P['n_floor'], 0)}"}
    vals = [series[y][0] for y in full]
    sp = spread(vals)
    return {"first_year": y0, "last_year": y1, "first": v0, "last": v1, "change": change, "direction": "up" if s > 0 else "down",
            "tests": [t1, t2, t3], "passed": t1["passed"] and t2["passed"] and t3["passed"], "years": full, "values": vals,
            "n_first": n0, "n_last": n1, "years_held": len(held), "years_after": len(later), "typical_move": sp,
            "strength": round(abs(change) / sp, 4) if sp > 0 else 0.0}


def news(key, claim, P, state):
    """Why a passing claim is drafted, or None: new, a newer last year, or its change moved past the threshold."""
    old = state.get(key)
    if not old:
        return "new: this pattern had not been drafted for this region"
    if str(old.get("last_year")) != str(claim["last_year"]):
        return f"a newer last full year ({claim['last_year']}; it was {old.get('last_year')})"
    moved = abs(claim["change"] - float(old.get("change", 0.0)))
    if moved > P["change_threshold"]:
        return f"the change moved by {common.fmt(moved, P['decimals'])} {P['unit']} since the last hunt (threshold {common.fmt(P['change_threshold'], P['decimals'])})"
    return None


# ---------------------------------------------------------------------------------------------------------------------
# a draft: the card, the caption, the files
# ---------------------------------------------------------------------------------------------------------------------
def val(v, P):
    return f"{common.fmt(v, P['decimals'])} {P['unit']}"


def fact_of(P, words, c, beside=""):
    return (f"{words}: {P['label']}, {val(c['last'], P)} in {c['last_year']}, {c['direction']} from {val(c['first'], P)} in {c['first_year']}. "
            f"The direction holds in {c['years_held']} of the {c['years_after']} full years after {c['first_year']}.{beside}")


def beside_of(P, c, context):
    """The family's second number in the claim's two years, as a sentence, or "" when it is not held in both."""
    X = P.get("context")
    if not X or not context:
        return ""
    a, b = context.get(str(c["first_year"])), context.get(str(c["last_year"]))
    if a is None or b is None:
        return ""
    return (f" Beside it, {X['label']}: {common.fmt(a, X['decimals'])} {X['unit']} in {c['first_year']}, "
            f"{common.fmt(b, X['decimals'])} {X['unit']} in {c['last_year']}.")


def region_tables(tables, region, module=None):
    """The tables a draft names: those its own region's rows rest on. A finding's pattern has them in OWN_TABLES by
    grid (session 252); without an entry, the module's tables without those that are another grid's by name.
    Since session 258 this is the rule of a finding's draft built without the record of what its finding read (a test,
    a caller with its own compute): wherever the reads are known, tables_used below decides instead, from the rows."""
    mine = grid_of(region)
    if module in OWN_TABLES and mine in OWN_TABLES[module]:
        return list(OWN_TABLES[module][mine])
    return [t for t in tables if not any(t.startswith(g + "_") for g in GRID_WORDS if g != mine)]


def _local_years(ts):
    """The local years a UTC timestamp can lie in: every grid here is behind UTC, so 1 January's first hours are
    also the year before's."""
    y = ts[:4]
    return (y, str(int(y) - 1)) if ts[5:10] == "01-01" and ts[11:13] < "12" else (y,)


def tables_used(reads, region, years, file_years=(), P=None):
    """Session 258 (session 252's ruling 6): the tables a draft's source line names, decided from what the finding read
    (findings_common.record_reads) and not from a list. A table of prices by market is named when it brought rows of
    this region's grid in the claim's years that no earlier read had brought (a finding reads its history first and
    the live window second, and keeps a timestamp once). Returns

        tables       the tables with this grid's rows in the claim's years (the full years the card shows)
        other_years  the tables that brought this grid's rows only to the file's other years (the year under way)
        helpers      the tables without a market that the pattern's measure itself needs (P["measure_tables"]: a
                     table of this kind cannot be given to a grid by its rows, so the pattern says it), if read

    A table the finding read only for another grid's rows, or for a column the measure does not use, is in none."""
    mine, want, rest = grid_of(region), {str(y) for y in years}, {str(y) for y in file_years} - {str(y) for y in years}
    seen, named, other = {}, [], []
    for rd in reads:
        for key, ts in (rd["groups"] or {}).items():
            new = ts - seen.setdefault(key, set())
            seen[key] |= ts
            if not new or grid_of(key[0]) != mine:
                continue
            ys = {y for t in new for y in _local_years(t)}
            if ys & want and rd["table"] not in named:
                named.append(rd["table"])
            elif ys & rest and rd["table"] not in other:
                other.append(rd["table"])
    helpers = [t for t in (P or {}).get("measure_tables", []) if any(rd["table"] == t and rd["rows"] for rd in reads)]
    return {"tables": named, "other_years": [t for t in other if t not in named], "helpers": [t for t in helpers if t not in named]}


def source_line_of(P, region, tables, helpers=()):
    """A draft's source line: this grid's rows of the tables that hold them, then the tables the measure also needs."""
    grid = GRID_WORDS.get(grid_of(region), grid_of(region))
    also = f", with the ERW table{'s' if len(helpers) != 1 else ''} {', '.join(helpers)}" if helpers else ""
    return (f"Source: {grid}'s rows of the ERW table{'s' if len(tables) != 1 else ''} {', '.join(tables)}{also}; "
            f"computed by the finding {P['module']} (warehouse/analysis/findings/).")


def sources_comment(region, tables, helpers=(), other_years=()):
    """The CSV's "# Sources:" line: every table a row of the file rests on, the year under way's said apart."""
    grid = GRID_WORDS.get(grid_of(region), grid_of(region))
    more = f"; the rows with full_year 0 also read {grid}'s rows of {', '.join(other_years)}" if other_years else ""
    return f"# Sources: {', '.join(list(tables) + list(helpers))}{more}\n"


def caption_of(P, words, c, source_line, beside=""):
    """The LinkedIn caption, computed from the claim's numbers. A draft for a person to edit: it states and does not explain."""
    t = {x["name"]: x["words"] for x in c["tests"]}
    return "\n".join([
        f"{words}: {P['label']}.",
        f"{c['first_year']}: {val(c['first'], P)}. {c['last_year']}: {val(c['last'], P)}. A change of {'+' if c['change'] > 0 else '-'}{val(abs(c['change']), P)}.",
        *([beside.strip()] if beside else []),
        "",
        "Checked three ways before it was drafted:",
        f"1. More than one year: {t['holds in more than one year']}.",
        f"2. Another window: {t['survives a change of window']}.",
        f"3. The sample: {t['sample large enough']}.",
        "",
        source_line,
        "Computed by the Energy Research Warehouse (ERW). Every number names the table it came from.",
    ])


def csv_text(P, region, words, series, c, module, tables, context=None, helpers=(), other_years=()):
    buf = io.StringIO()
    X = P.get("context") if context else None
    by = f"{module}.{P['fn']}" if P.get("fn") else f"{module}.compute"
    buf.write(f"# Energy Research Warehouse (ERW): the weekly hunt, pattern {P['name']}, region {region} ({words})\n")
    buf.write(f"# Computed {common.now_iso()} by warehouse/analysis/findings/hunt.py from {by}; method https://github.com/SamuelEnrique/erw/blob/main/{METHOD}\n")
    buf.write(f"# Rows: one per year held: {P['label']} ({P['unit']}), the observations it rests on, and whether the year is full"
              + (f"; context_value: {X['label']} ({X['unit']}), blank where not held" if X else "") + "\n")
    buf.write(sources_comment(region, tables, helpers, other_years))   # session 258: the year under way's tables said apart
    buf.write("region,year,value,n_observations,full_year" + (",context_value" if X else "") + "\n")
    for y, (v, n) in series.items():
        extra = ("," + ("" if context.get(y) is None else repr(context[y]))) if X else ""
        buf.write(f"{region},{y},{v!r},{n!r},{1 if y in c['years'] else 0}{extra}\n")
    return buf.getvalue()


def do_text(P, region, csv_name, c):
    """The Stata do-file, to the owner's rules (findings_common.do_file): it reads the draft's CSV and shows the claim
    and the three tests."""
    y0, y1 = c["first_year"], c["last_year"]
    return common.do_file([
        f"* ERW weekly hunt, pattern {P['name']}, region {region}. Reproduces the draft's numbers from {csv_name}.",
        "* The CSV's first four lines are comments; its fifth line holds the variable names.",
        "clear all",
        f'import delimited "{csv_name}", varnames(5) rowrange(6) stringcols(_all) clear',
        *common.do_destring(["year", "value", "n_observations", "full_year"]),
        *common.do_sentinels(["year", "value", "n_observations", "full_year"]),
        "sort year",
        "list year value n_observations full_year, noobs",
        "* The claim: the last full year against the first full year.",
        f"summarize value if year == {y0}",
        "scalar first_value = r(mean)",
        f"summarize value if year == {y1}",
        "scalar last_value = r(mean)",
        "display \"change, last full year minus first full year: \" last_value - first_value",
        "* Test 1, more than one year: full years after the first on the claim's side of the first year's value.",
        f"count if full_year == 1 & year > {y0} & sign(value - first_value) == sign(last_value - first_value)",
        "* Test 2, another window: one year later at the start, one year earlier at the end.",
        "generate byte keep_full = full_year == 1",
        "sort keep_full year",
        "by keep_full: generate rank_full = _n if keep_full == 1",
        "by keep_full: generate count_full = _N if keep_full == 1",
        "summarize value if rank_full == 2",
        "display \"from the second full year: \" last_value - r(mean)",
        "summarize value if rank_full == count_full - 1",
        "display \"to the year before the last: \" r(mean) - first_value",
        "* Test 3, the sample: the observations of the two end years.",
        f"list year n_observations if year == {y0} | year == {y1}, noobs",
    ])


PY_MIRROR = '''"""ERW weekly hunt: the Python mirror of a draft. Reads the draft's CSV and recomputes the claim and its three tests.

    python {py_name} {csv_name}

Pattern {name}, region {region}. Floor of the sample: {n_floor}. A full year is not the year under way and holds
at least {full_share} of the fullest year's observations. No package beyond the standard library.
"""
import csv
import sys

rows = [r for r in csv.DictReader(ln for ln in open(sys.argv[1] if len(sys.argv) > 1 else "{csv_name}", encoding="utf-8") if not ln.startswith("#"))]
series = {{r["year"]: (float(r["value"]), float(r["n_observations"])) for r in rows}}
full = [r["year"] for r in rows if r["full_year"] == "1"]
sign = lambda x: (x > 0) - (x < 0)  # noqa: E731
y0, y1 = full[0], full[-1]
v0, v1 = series[y0][0], series[y1][0]
change = v1 - v0
print(f"claim: {{v0}} in {{y0}}, {{v1}} in {{y1}}; change {{change}}")
held = [y for y in full[1:] if sign(series[y][0] - v0) == sign(change)]
print(f"test 1, more than one year: {{len(held)}} of {{len(full) - 1}} full years after {{y0}} on the claim's side: {{'pass' if len(held) >= 2 else 'fail'}}")
if len(full) >= 4:
    a, b = series[full[1]][0], series[full[-2]][0]
    ok = sign(v1 - a) == sign(change) and sign(b - v0) == sign(change)
    print(f"test 2, another window: from {{full[1]}} the change is {{v1 - a}}, to {{full[-2]}} it is {{b - v0}}: {{'pass' if ok else 'fail'}}")
else:
    print(f"test 2, another window: only {{len(full)}} full years, four needed: fail")
n0, n1 = series[y0][1], series[y1][1]
print(f"test 3, the sample: {{n0}} and {{n1}} observations, floor {n_floor}: {{'pass' if min(n0, n1) >= {n_floor} else 'fail'}}")
'''


def draft_id(P, region, c):
    return "scan-hunt-" + hashlib.sha1(f"{P['name']}|{region}|{c['last_year']}|{round(c['change'], 3)}".encode("utf-8")).hexdigest()[:12]


def build_draft(P, region, words, series, c, why, module_card, tables, out_dir, used=None):
    """One draft: the row of public.scanner_drafts, with its card and its files. The pictures are drawn here.
    used: tables_used() for this region and claim (session 258). Without it the tables are the module's, less those
    that are another grid's by name."""
    import card_image
    did = draft_id(P, region, c)
    context = (module_card or {}).get("context") if P.get("context") else None
    beside = beside_of(P, c, context)
    fact = fact_of(P, words, c, beside)
    # the module's own source line names every grid it read; this draft rests on one region's rows
    helpers, other_years = [], []
    if P.get("fn"):
        tables = list(tables)                            # the measure's own list for this region
        source_line = (f"Source: the rows for {words} of the ERW tables {', '.join(tables)}; "
                       f"computed by the hunt's measure {P['fn']} (warehouse/analysis/findings/hunt_measures.py).")
        read_words = f"computed by year by the hunt's measure {P['fn']} (hunt_measures.py) on this run's tables"
    else:
        if used and used.get("tables"):                  # session 258: decided from the rows the finding read
            tables, helpers, other_years = list(used["tables"]), list(used.get("helpers", [])), list(used.get("other_years", []))
        else:                                            # no record of the reads: session 251's list by grid, then the names
            tables = region_tables(tables, region, P["module"])
        source_line = source_line_of(P, region, tables, helpers)
        read_words = f"read by year from the rows of the finding {P['module']} computed on this run's tables"
    shown = list(c["years"])                             # the full years the claim rests on; the CSV holds every year
    tests_words = " ".join(f"{t['name'].capitalize()}: {t['words']} ({'passed' if t['passed'] else 'failed'})." for t in c["tests"])
    files = [f"{did}.csv", f"{did}.do", f"{did}.py", f"{did}_1200x627.png", f"{did}_1080x1080.png", f"{did}_caption.txt"]
    card = {"id": "hunt_pattern", "card_id": did, "title": f"{P['title']}: {words.upper()}", "kind": "visual", "subtitle": fact, "draft": True,
            "params": {"pattern": P["name"], "region": str(region)}, "inputs_words": {"pattern": P["name"], "region": words},
            "chart": {"kind": "flag_line", "x": shown, "x_label": "full years held; the last one is marked",
                      "series": [{"name": f"{words}: {P['label']}", "type": "line", "unit": P["unit"], "values": [common.round6(series[y][0]) for y in shown]}],
                      "mark": {"x": c["last_year"], "value": common.round6(c["last"]), "label": "the last full year"},
                      "ref_lines": [{"name": f"{c['first_year']}", "value": common.round6(c["first"])}], "y_left_label": P["unit"], "decimals": P["decimals"]},
            "callouts": [common.callout("The claim", c["first_year"], val(c["first"], P), c["last_year"], val(c["last"], P)),
                         common.callout("How large", "typical yearly move", val(c["typical_move"], P), "this change, in those", common.fmt(c["strength"], 1)),
                         common.callout("The three tests", "years on its side", f"{c['years_held']} of {c['years_after']}",
                                        "tests passed", f"{sum(1 for t in c['tests'] if t['passed'])} of 3")],
            "why": "", "footnote": (f"A draft raised by the weekly hunt, version {VERSION}, on {common.now_iso()[:10]}; not reviewed. Pattern {P['name']}: {P['label']}, "
                                    f"{read_words}. Region: {words} ({region}). {tests_words}{beside}{' That second number is stated, not tested.' if beside else ''} "
                                    f"Why it was drafted: {why}. A full year is not the year under way and holds at least {int(FULL_SHARE * 100)} percent of the fullest "
                                    f"year's observations. The claim states a change; it does not say what caused it. Method: {METHOD}."),
            "numbers": {"first": c["first"], "last": c["last"], "change": c["change"], "first_year": int(c["first_year"]), "last_year": int(c["last_year"]),
                        "years_held": c["years_held"], "years_after": c["years_after"], "n_first": c["n_first"], "n_last": c["n_last"],
                        "typical_move": c["typical_move"], "strength": c["strength"], "full_years": len(c["years"]),
                        **({"context_first": context.get(str(c["first_year"])), "context_last": context.get(str(c["last_year"]))} if beside else {})},
            "source_line": source_line + " Found by the weekly hunt.", "tables": tables + helpers, "computed_at": common.now_iso(),
            "method": "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD,
            "scanner": {"version": VERSION, "rule": "hunt", "date": f"{c['last_year']}-12-31", "flag_id": did, "strength": c["strength"], "full_card": None},
            "hunt": {"pattern": P["name"], "module": P["module"], "region": str(region), "region_words": words, "why": why, "tests": c["tests"], "files": files,
                     **({"measure": P["fn"]} if P.get("fn") else {}), **({"context": dict(P["context"], values=context)} if beside else {})}}
    caption = caption_of(P, words, c, source_line, beside)
    card["hunt"]["caption"] = caption
    csv_name = files[0]
    texts = {files[0]: csv_text(P, region, words, series, c, P["module"], tables, context if beside else None, helpers, other_years),
             files[1]: do_text(P, region, csv_name, c),
             files[2]: PY_MIRROR.format(py_name=files[2], csv_name=csv_name, name=P["name"], region=region, n_floor=P["n_floor"], full_share=FULL_SHARE),
             files[5]: caption + "\n"}
    stored = {}
    os.makedirs(out_dir, exist_ok=True)
    for name, text in texts.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        stored[name] = {"kind": "text", "content": text}
    for name, size in ((files[3], "linkedin_wide"), (files[4], "linkedin_square")):
        p = card_image.render(card, os.path.join(out_dir, name), size, fact=fact)
        with open(p, "rb") as f:
            stored[name] = {"kind": "png", "content": base64.b64encode(f.read()).decode("ascii")}
    with open(os.path.join(out_dir, did + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(card, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    flag = {"id": did, "rule": "hunt", "pattern": P["name"], "module": P["module"], "region": str(region), "hunt_version": VERSION,
            "claim": {k: c[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "years", "values", "n_first", "n_last",
                                        "years_held", "years_after", "typical_move", "strength")},
            "tests": c["tests"], "why": why, "thresholds": {"n_floor": P["n_floor"], "change_threshold": P["change_threshold"], "full_share": FULL_SHARE}}
    return {"id": did, "flag_key": f"hunt|{P['module']}|{P['name']}|{region}", "rule": "hunt", "table_name": tables[0], "series_key": f"pattern={P['name']}|region={region}",
            "flag_date": f"{c['last_year']}-12-31", "value": c["change"], "strength": c["strength"], "scanner_version": VERSION, "flag": flag, "card": card,
            "files": stored, "_state": {"last_year": c["last_year"], "change": c["change"], "first_year": c["first_year"]}}


# ---------------------------------------------------------------------------------------------------------------------
# the hunt
# ---------------------------------------------------------------------------------------------------------------------
def read_state(path=None):
    try:
        with open(path or STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def run_pattern(P, in_dir, this_year, blocked, log=print, compute=None):
    """Every region's claim for one pattern: [(region, words, series, claim or None, reason not drafted or None, card, tables)]."""
    if P.get("fn"):
        return run_family(P, in_dir, this_year, blocked, log, compute)
    mod = run_finding.load(P["module"])
    sweeps = [None] if not P.get("sweep") else list(mod.INPUTS[P["sweep"]]["choices"])
    out = []
    for choice in sweeps:
        params = run_finding.coerce(mod, {P["sweep"]: choice} if choice is not None else {})
        t0 = time.time()
        with common.record_reads() as reads:             # session 258: what this run read, for each draft's source line
            rows, meta = (compute or mod.compute)(params, in_dir)
        card = mod.card(rows, params, meta)
        regions = [str(choice)] if not P.get("region_col") else sorted({str(r.get(P["region_col"])) for r in rows if r.get(P["region_col"]) not in (None, "")})
        log(f"  {P['name']}{' ' + str(choice) if choice is not None else ''}: {len(rows)} rows, {len(regions)} region(s), {round(time.time() - t0, 1)} s")
        for region in regions:
            words = region_words(P, region, rows)
            if grid_of(region) in blocked:
                out.append((region, words, {}, None, f"{GRID_WORDS.get(grid_of(region), grid_of(region))} needs a license or is held: never drafted", card, list(mod.TABLES)))
                continue
            series = yearly(rows, P, region)
            claim = test_claim(series, P, this_year)
            reason = None
            if claim is None:
                reason = "no claim: fewer than two full years, or no change"
            elif not claim["passed"]:
                reason = "failed: " + "; ".join(t["name"] for t in claim["tests"] if not t["passed"])
            used = tables_used(reads, region, claim["years"], list(series), P) if claim is not None and reads else None
            out.append((region, words, series, claim, reason, card, list(mod.TABLES), used))
    return out


def run_family(P, in_dir, this_year, blocked, log=print, compute=None):
    """run_pattern for a measure of hunt_measures.py: the same seven fields a region. The sixth holds the family's
    second number by year ({"context": {year: value}}); the seventh the tables that region's own rows come from."""
    t0 = time.time()
    got = (compute or hunt_measures.run)(P["fn"], in_dir)
    rows = got["rows"]
    regions = sorted({str(r["region"]) for r in rows})
    log(f"  {P['name']}: {len(rows)} rows, {len(regions)} region(s), {round(time.time() - t0, 1)} s")
    out = []
    for region in regions:
        words = region_words(P, region, rows)
        tables = list(got["tables"].get(region, []))
        if grid_of(region) in blocked:
            out.append((region, words, {}, None, f"{GRID_WORDS.get(grid_of(region), grid_of(region))} needs a license or is held: never drafted", {}, tables))
            continue
        series = yearly(rows, P, region)
        context = {str(r["year"]): r["context"] for r in rows if str(r["region"]) == region and r.get("context") is not None}
        claim = test_claim(series, P, this_year)
        reason = None
        if claim is None:
            reason = "no claim: fewer than two full years, or no change"
        elif not claim["passed"]:
            reason = "failed: " + "; ".join(t["name"] for t in claim["tests"] if not t["passed"])
        out.append((region, words, series, claim, reason, {"context": context}, tables))
    return out


def hunt(in_dir=None, only=None, dry_run=False, log=print, now=None, state_path=None, out_root=None, load=None):
    """Run the library. Returns the summary dict (also written to runs/hunt/<date>/hunt.json)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    day = now.strftime("%Y-%m-%d")
    out_dir = os.path.join(out_root or OUT, day)
    os.makedirs(out_dir, exist_ok=True)
    state = read_state(state_path)
    blocked = blocked_grids()
    results, drafts, failed = [], [], []
    for P in PATTERNS:
        if only and not re.search(only, P["name"]):
            continue
        try:
            got = run_pattern(P, in_dir or common.DEFAULT_IN_DIR, now.year, blocked, log)
        except common.NoData as exc:
            failed.append({"pattern": P["name"], "reason": f"a table is not on this machine: {str(exc)[:160]}"})
            log(f"  {P['name']}: NOT RUN, a table is not on this machine: {exc}")
            continue
        except Exception as exc:
            failed.append({"pattern": P["name"], "reason": f"{type(exc).__name__}: {str(exc)[:160]}"})
            log(f"  {P['name']}: FAILED: {traceback.format_exc()}")
            continue
        for region, words, series, claim, reason, card, tables, *more in got:   # more: tables_used, since session 258
            key = f"{P['name']}|{region}"
            row = {"pattern": P["name"], "module": P["module"], "region": region, "region_words": words, "key": key, "drafted": False, "reason": reason}
            if claim is not None:
                row.update({k: claim[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "strength", "passed", "years_held", "years_after")})
                row["tests"] = claim["tests"]
            if claim is not None and claim["passed"] and P.get("one_interval"):
                # session 252: the measure is one interval of a year, and most of each spike claim was one year's fall
                row["reason"] = "passes its tests; the measure is one interval of a year, so it is kept here and never drafted (session 252)"
            elif claim is not None and claim["passed"]:
                why = news(key, claim, P, state)
                if why is None:
                    row["reason"] = "passes its tests; not new and not changed past its threshold since the last hunt"
                else:
                    drafts.append((claim["strength"], P, region, words, series, claim, why, card, tables, row, more[0] if more else None))
            results.append(row)
    drafts.sort(key=lambda d: (-d[0], d[9]["key"]))
    built, per_pattern, seen = [], {}, {}
    for _, P, region, words, series, claim, why, card, tables, row, used in drafts:
        same = (P.get("fn") or P["measure"], claim["first_year"], claim["last_year"], round(claim["first"], 6), round(claim["last"], 6))
        if same in seen:                                 # two patterns that read one number (a grid's hub average, twice)
            row["reason"] = f"passes its tests and is news; the same numbers as {seen[same]}, drafted once"
            continue
        if per_pattern.get(P["name"], 0) >= MAX_PER_PATTERN:
            row["reason"] = f"passes its tests and is news ({why}); beyond the {MAX_PER_PATTERN} strongest regions of its pattern, so kept here and not drafted"
            continue
        if len(built) >= MAX_DRAFTS:
            row["reason"] = f"passes its tests and is news ({why}); beyond the {MAX_DRAFTS} strongest of this hunt, so kept here and not drafted"
            continue
        seen[same] = row["key"]
        per_pattern[P["name"]] = per_pattern.get(P["name"], 0) + 1
        d = build_draft(P, region, words, series, claim, why, card, tables, out_dir, used)
        row.update(drafted=True, draft_id=d["id"], reason=why, fact=d["card"]["subtitle"])
        built.append((d, row["key"]))
    loaded = 0
    if built and not dry_run:
        loaded_ids = (load or load_drafts)([d for d, _ in built], log)
        loaded = len(loaded_ids)
        for d, key in built:
            if d["id"] in loaded_ids:
                state[key] = d["_state"]
        with open(state_path or STATE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, indent=1, sort_keys=True)
            f.write("\n")
    summary = {"hunt_version": VERSION, "day": day, "computed_at": common.now_iso(), "patterns": [P["name"] for P in PATTERNS if not only or re.search(only, P["name"])],
               "not_yet": NOT_YET, "blocked_grids": sorted(blocked), "claims": len(results), "passed": sum(1 for r in results if r.get("passed")),
               "drafts": len(built), "loaded": loaded, "dry_run": bool(dry_run), "failed": failed, "results": results}
    with open(os.path.join(out_dir, "hunt.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    log(f"hunt {VERSION} on {day}: {len(summary['patterns'])} patterns, {len(results)} claims, {summary['passed']} pass the three tests, "
        f"{len(built)} drafts{' (dry run: none loaded)' if dry_run else f', {loaded} added to the review list'}; {len(failed)} pattern(s) not run")
    return summary


def load_drafts(drafts, log=print, get=None, post=None):
    """Add the hunt's drafts to the review list (public.scanner_drafts). A draft raised before under the same id, or
    whose claim still has an open draft, is not added again. Returns the ids added."""
    import requests
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import lock
    import urllib.parse
    url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("the load needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
    u = urllib.parse.urlparse(url)
    base, h = f"{u.scheme}://{u.netloc}/rest/v1/scanner_drafts", {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    r = (get or requests.get)(base, params={"select": "id,flag_key,state", "limit": "5000"}, headers=h, timeout=30)
    r.raise_for_status()
    have = r.json()
    ids = {x["id"] for x in have}
    open_keys = {x["flag_key"] for x in have if x.get("state") in ("draft", "full_card_asked")}
    rows = [d for d in drafts if d["id"] not in ids and d["flag_key"] not in open_keys]
    added = []
    for d in rows:                                       # one row a request: a row holds two pictures
        body = {k: d[k] for k in ("id", "flag_key", "rule", "table_name", "series_key", "flag_date", "value", "strength", "scanner_version", "flag", "card", "files")}
        w = (post or requests.post)(base, data=json.dumps([body], default=common.round6, allow_nan=False), headers={**h, "Prefer": "return=minimal"}, timeout=120)
        w.raise_for_status()
        added.append(d["id"])
    log(f"{len(added)} draft(s) added to scanner_drafts; {len(drafts) - len(added)} already there or with an open draft")
    return added


# ---------------------------------------------------------------------------------------------------------------------
# session 258: the drafts already on the review list, their source line by the rule above
# ---------------------------------------------------------------------------------------------------------------------
def _without_source(card):
    """A card without the three places its source line lives: what must be equal before and after a rewrite."""
    c = json.loads(json.dumps(card))
    c.pop("source_line", None)
    c.pop("tables", None)
    (c.get("hunt") or {}).pop("caption", None)
    return c


def rewrite_draft(row, used, out_dir):
    """One stored hunt draft with its source line by tables_used: the card's line and tables, the caption, the CSV's
    "# Sources:" line and the two pictures (the line is burned into them). Returns (the changed columns or None when
    the line already says it, the old line, the new line). No number, claim or chart point changes: it is checked
    here, and a difference raises."""
    import card_image
    card, files = json.loads(json.dumps(row["card"])), dict(row["files"])
    P = next(p for p in PATTERNS if p["name"] == card["hunt"]["pattern"])
    region = card["hunt"]["region"]
    if not used or not used.get("tables"):
        raise ValueError(f"{row['id']}: the finding read no row of {region} in the claim's years; nothing is rewritten")
    tables, helpers, other = list(used["tables"]), list(used.get("helpers", [])), list(used.get("other_years", []))
    tail = " Found by the weekly hunt."
    old = card["source_line"][:-len(tail)] if card["source_line"].endswith(tail) else card["source_line"]
    new = source_line_of(P, region, tables, helpers)
    names = card["hunt"]["files"]
    csv_old = files[names[0]]["content"]
    lines = csv_old.split("\n")
    at = [i for i, ln in enumerate(lines) if ln.startswith("# Sources:")]
    if len(at) != 1 or old not in card["hunt"]["caption"] or old not in files[names[5]]["content"]:
        raise ValueError(f"{row['id']}: the stored line is not where the hunt writes it; nothing is rewritten")
    lines[at[0]] = sources_comment(region, tables, helpers, other).rstrip("\n")
    csv_new = "\n".join(lines)
    if new == old and csv_new == csv_old and card.get("tables") == tables + helpers:
        return None, old, new
    card["source_line"], card["tables"] = new + tail, tables + helpers
    card["hunt"]["caption"] = card["hunt"]["caption"].replace(old, new)
    files[names[0]] = {"kind": "text", "content": csv_new}
    files[names[5]] = {"kind": "text", "content": files[names[5]]["content"].replace(old, new)}
    if _without_source(card) != _without_source(row["card"]) or [ln for ln in csv_new.split("\n") if not ln.startswith("# Sources:")] != [
            ln for ln in csv_old.split("\n") if not ln.startswith("# Sources:")]:
        raise ValueError(f"{row['id']}: more than the source line would change; nothing is rewritten")
    os.makedirs(out_dir, exist_ok=True)
    for name, size in ((names[3], "linkedin_wide"), (names[4], "linkedin_square")):
        p = card_image.render(card, os.path.join(out_dir, name), size, fact=card["subtitle"])
        with open(p, "rb") as f:
            files[name] = {"kind": "png", "content": base64.b64encode(f.read()).decode("ascii")}
    return {"card": card, "files": files, "table_name": tables[0]}, old, new


def fix_source_lines(in_dir=None, dry_run=False, log=print, get=None, patch=None, compute=None, out_dir=None):
    """Every hunt draft of public.scanner_drafts: its finding is run again on this machine's tables under the record
    of its reads, and its source line is rewritten to name only the tables that brought its region's rows. Run on the
    data machine (it holds the tables and the service key). --dry-run prints each line and writes nothing.
    Returns [{id, state, old, new, written}]."""
    import requests
    import urllib.parse
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import lock
    url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("the rewrite needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
    u = urllib.parse.urlparse(url)
    base, h = f"{u.scheme}://{u.netloc}/rest/v1/scanner_drafts", {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    r = (get or requests.get)(base, params={"rule": "eq.hunt", "select": "id,state,table_name,flag,card,files", "order": "id"}, headers=h, timeout=120)
    r.raise_for_status()
    rows = r.json()
    out_dir = out_dir or os.path.join(OUT, "source_lines")
    reads_of, out = {}, []
    for row in rows:
        hunt_part = row["card"]["hunt"]
        P = next((p for p in PATTERNS if p["name"] == hunt_part["pattern"]), None)
        if P is None:
            raise ValueError(f"{row['id']}: pattern {hunt_part['pattern']} is not in the library")
        region = hunt_part["region"]
        if P.get("fn"):                                  # session 251: a measure's draft was built from its own region's tables
            line = row["card"].get("source_line", "")
            log(f"{row['id']} ({row.get('state')}, {P['name']}, {region}): left as it is, a measure of hunt_measures.py names its own region's tables")
            out.append({"id": row["id"], "state": row.get("state"), "old": line, "new": line, "changed": False, "written": False})
            continue
        mod = run_finding.load(P["module"])
        choice = region if P.get("sweep") else None
        if (P["module"], choice) not in reads_of:        # one run of a finding serves every draft that rests on it
            with common.record_reads() as reads:
                (compute or mod.compute)(run_finding.coerce(mod, {P["sweep"]: choice} if choice is not None else {}), in_dir or common.DEFAULT_IN_DIR)
            reads_of[(P["module"], choice)] = reads
        file_years = [ln.split(",")[1] for ln in row["files"][hunt_part["files"][0]]["content"].split("\n") if ln and not ln.startswith("#")][1:]
        used = tables_used(reads_of[(P["module"], choice)], region, row["flag"]["claim"]["years"], file_years, P)
        body, old, new = rewrite_draft(row, used, out_dir)
        written = False
        if body is not None and not dry_run:
            w = (patch or requests.patch)(base, params={"id": f"eq.{row['id']}"}, data=json.dumps(body, default=common.round6, allow_nan=False),
                                          headers={**h, "Prefer": "return=minimal"}, timeout=120)
            w.raise_for_status()
            written = True
        log(f"{row['id']} ({row.get('state')}, {P['name']}, {region}): {'already right' if body is None else ('rewritten' if written else 'would be rewritten')}")
        if body is not None:
            log(f"  was: {old}\n  is:  {new}\n  the file's other years: {', '.join(used['other_years']) or 'no other table'}")
        out.append({"id": row["id"], "state": row.get("state"), "old": old, "new": new, "changed": body is not None, "written": written})
    log(f"{len(out)} hunt draft(s): {sum(1 for o in out if o['changed'])} with a line to rewrite, {sum(1 for o in out if o['written'])} written"
        f"{' (dry run: nothing written)' if dry_run else ''}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the weekly hunt for deeper findings (session 233)")
    ap.add_argument("--fix-source-lines", action="store_true", help="session 258: rewrite the source line of the hunt drafts already on the review list "
                    "(with --dry-run: print each line, write nothing)")
    ap.add_argument("--weekly", action="store_true", help="the Saturday task: run the library, draft what passes and is news, load the drafts")
    ap.add_argument("--dry-run", action="store_true", help="run and test, write runs/hunt/<date>/, load nothing and keep the memory as it is")
    ap.add_argument("--only", help="a pattern: run only the patterns whose name it matches")
    ap.add_argument("--in-dir", default=common.DEFAULT_IN_DIR, help="the warehouse's output directory")
    ap.add_argument("--list", action="store_true", help="print the library and what is not in it yet")
    a = ap.parse_args(argv)
    if a.list:
        for P in PATTERNS:
            print(f"{P['name']}: {P['label']} ({P['unit']}); " + (f"measure hunt_measures.{P['fn']}" if P.get("fn") else f"finding {P['module']}")
                  + (f", once per {P['sweep']}" if P.get("sweep") else f", by {P['region_col']}") + (", never drafted: one interval a year" if P.get("one_interval") else ""))
        for name, why in NOT_YET.items():
            print(f"not yet, {name}: {why}")
        return 0
    if a.fix_source_lines:
        try:
            fix_source_lines(a.in_dir, dry_run=a.dry_run)
            return 0
        except Exception:
            print(f"the rewrite FAILED:\n{traceback.format_exc()}", file=sys.stderr)
            return 1
    if not a.weekly and not a.dry_run:
        ap.error("--weekly, --dry-run or --list")
    try:
        hunt(a.in_dir, a.only, dry_run=a.dry_run)
        return 0
    except Exception:
        print(f"hunt FAILED:\n{traceback.format_exc()}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
