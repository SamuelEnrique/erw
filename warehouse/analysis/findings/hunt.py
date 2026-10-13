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

Exit 0 ran (whatever it found), 1 failed, 2 bad input.
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
import run_finding  # noqa: E402

VERSION = "1.0.0"
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
         measure="worst_interval_multiple", n_col="n_intervals", n_floor=30000, unit="times the median", decimals=1, change_threshold=10.0,
         title="THE WORST PRICE SPIKE AGAINST THE MEDIAN", label="the year's dearest interval as a multiple of the year's median real-time price"),
    dict(name="spikes_against_median_grids", module="batteries_lunch_grids", sweep=None, region_col="grid", year_col="period", filter={"kind": "year"},
         measure="worst_interval_multiple", n_col="n_intervals", n_floor=8000, unit="times the median", decimals=1, change_threshold=10.0,
         title="THE WORST PRICE SPIKE AGAINST THE MEDIAN", label="the year's dearest interval as a multiple of the year's median real-time price"),
    dict(name="hours_above_1000", module="batteries_lunch_grids", sweep=None, region_col="grid", year_col="period", filter={"kind": "year"},
         measure="hours_ge_1000", n_col="n_intervals", n_floor=8000, unit="hours", decimals=1, change_threshold=5.0,
         title="HOURS ABOVE USD 1,000", label="hours of the year with a real-time price of USD 1,000 per MWh or more"),
    dict(name="gas_sets_price", module="gas_sets_price", sweep=None, region_col="grid", year_col="year", filter=None,
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


def fact_of(P, words, c):
    return (f"{words}: {P['label']}, {val(c['last'], P)} in {c['last_year']}, {c['direction']} from {val(c['first'], P)} in {c['first_year']}. "
            f"The direction holds in {c['years_held']} of the {c['years_after']} full years after {c['first_year']}.")


def region_tables(tables, region):
    """The module's tables without those that are another grid's by name: a draft names what its own rows rest on."""
    mine = grid_of(region)
    return [t for t in tables if not any(t.startswith(g + "_") for g in GRID_WORDS if g != mine)]


def caption_of(P, words, c, source_line):
    """The LinkedIn caption, computed from the claim's numbers. A draft for a person to edit: it states and does not explain."""
    t = {x["name"]: x["words"] for x in c["tests"]}
    return "\n".join([
        f"{words}: {P['label']}.",
        f"{c['first_year']}: {val(c['first'], P)}. {c['last_year']}: {val(c['last'], P)}. A change of {'+' if c['change'] > 0 else '-'}{val(abs(c['change']), P)}.",
        "",
        "Checked three ways before it was drafted:",
        f"1. More than one year: {t['holds in more than one year']}.",
        f"2. Another window: {t['survives a change of window']}.",
        f"3. The sample: {t['sample large enough']}.",
        "",
        source_line,
        "Computed by the Energy Research Warehouse (ERW). Every number names the table it came from.",
    ])


def csv_text(P, region, words, series, c, module, tables):
    buf = io.StringIO()
    buf.write(f"# Energy Research Warehouse (ERW): the weekly hunt, pattern {P['name']}, region {region} ({words})\n")
    buf.write(f"# Computed {common.now_iso()} by warehouse/analysis/findings/hunt.py from {module}.compute; method https://github.com/SamuelEnrique/erw/blob/main/{METHOD}\n")
    buf.write(f"# Rows: one per year held: {P['label']} ({P['unit']}), the observations it rests on, and whether the year is full\n")
    buf.write(f"# Sources: {', '.join(tables)}\n")
    buf.write("region,year,value,n_observations,full_year\n")
    for y, (v, n) in series.items():
        buf.write(f"{region},{y},{v!r},{n!r},{1 if y in c['years'] else 0}\n")
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


def build_draft(P, region, words, series, c, why, module_card, tables, out_dir):
    """One draft: the row of public.scanner_drafts, with its card and its files. The pictures are drawn here."""
    import card_image
    did = draft_id(P, region, c)
    fact = fact_of(P, words, c)
    # the module's own source line names every grid it read; this draft rests on one region's rows
    tables = region_tables(tables, region)
    source_line = (f"Source: {GRID_WORDS.get(grid_of(region), grid_of(region))}'s rows of the ERW tables {', '.join(tables)}; "
                   f"computed by the finding {P['module']} (warehouse/analysis/findings/).")
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
                                    f"read by year from the rows of the finding {P['module']} computed on this run's tables. Region: {words} ({region}). {tests_words} "
                                    f"Why it was drafted: {why}. A full year is not the year under way and holds at least {int(FULL_SHARE * 100)} percent of the fullest "
                                    f"year's observations. The claim states a change; it does not say what caused it. Method: {METHOD}."),
            "numbers": {"first": c["first"], "last": c["last"], "change": c["change"], "first_year": int(c["first_year"]), "last_year": int(c["last_year"]),
                        "years_held": c["years_held"], "years_after": c["years_after"], "n_first": c["n_first"], "n_last": c["n_last"],
                        "typical_move": c["typical_move"], "strength": c["strength"], "full_years": len(c["years"])},
            "source_line": source_line + " Found by the weekly hunt.", "tables": tables, "computed_at": common.now_iso(),
            "method": "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD,
            "scanner": {"version": VERSION, "rule": "hunt", "date": f"{c['last_year']}-12-31", "flag_id": did, "strength": c["strength"], "full_card": None},
            "hunt": {"pattern": P["name"], "module": P["module"], "region": str(region), "region_words": words, "why": why, "tests": c["tests"], "files": files}}
    caption = caption_of(P, words, c, source_line)
    card["hunt"]["caption"] = caption
    csv_name = files[0]
    texts = {files[0]: csv_text(P, region, words, series, c, P["module"], tables), files[1]: do_text(P, region, csv_name, c),
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
    mod = run_finding.load(P["module"])
    sweeps = [None] if not P.get("sweep") else list(mod.INPUTS[P["sweep"]]["choices"])
    out = []
    for choice in sweeps:
        params = run_finding.coerce(mod, {P["sweep"]: choice} if choice is not None else {})
        t0 = time.time()
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
            out.append((region, words, series, claim, reason, card, list(mod.TABLES)))
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
        for region, words, series, claim, reason, card, tables in got:
            key = f"{P['name']}|{region}"
            row = {"pattern": P["name"], "module": P["module"], "region": region, "region_words": words, "key": key, "drafted": False, "reason": reason}
            if claim is not None:
                row.update({k: claim[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "strength", "passed", "years_held", "years_after")})
                row["tests"] = claim["tests"]
            if claim is not None and claim["passed"]:
                why = news(key, claim, P, state)
                if why is None:
                    row["reason"] = "passes its tests; not new and not changed past its threshold since the last hunt"
                else:
                    drafts.append((claim["strength"], P, region, words, series, claim, why, card, tables, row))
            results.append(row)
    drafts.sort(key=lambda d: (-d[0], d[9]["key"]))
    built, per_pattern, seen = [], {}, {}
    for _, P, region, words, series, claim, why, card, tables, row in drafts:
        same = (P["measure"], claim["first_year"], claim["last_year"], round(claim["first"], 6), round(claim["last"], 6))
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
        d = build_draft(P, region, words, series, claim, why, card, tables, out_dir)
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the weekly hunt for deeper findings (session 233)")
    ap.add_argument("--weekly", action="store_true", help="the Saturday task: run the library, draft what passes and is news, load the drafts")
    ap.add_argument("--dry-run", action="store_true", help="run and test, write runs/hunt/<date>/, load nothing and keep the memory as it is")
    ap.add_argument("--only", help="a pattern: run only the patterns whose name it matches")
    ap.add_argument("--in-dir", default=common.DEFAULT_IN_DIR, help="the warehouse's output directory")
    ap.add_argument("--list", action="store_true", help="print the library and what is not in it yet")
    a = ap.parse_args(argv)
    if a.list:
        for P in PATTERNS:
            print(f"{P['name']}: {P['label']} ({P['unit']}); finding {P['module']}" + (f", once per {P['sweep']}" if P.get("sweep") else f", by {P['region_col']}"))
        for name, why in NOT_YET.items():
            print(f"not yet, {name}: {why}")
        return 0
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
