#!/usr/bin/env python3
"""ERW, the interconnection queue explorer (/explore/interconnection): the replication a reader can run (session 7509,
chain 304).

Written from the method note (docs/methods/interconnection_explorer.md, and the table's own note, docs/methods/
energy_projects.md, "Queue statistics") and the rows alone, not from the page's code. Two parts:

  A. The page against its table. Every figure the page draws, for each queue, both counts (positions and MW) and every
     first and last entry year it offers, is read again here from iso_queue_statistics as the note says the page reads
     it (which rows a view draws, in which place, written how), and set beside what the page's own code draws on the
     same file (site/scripts/interconnection-figures.mjs, run with node, or a file of its output). A figure is inside
     the tolerance when it differs by at most half the last digit the page shows.
  B. The table against the queues. Every row of iso_queue_statistics is computed again from the project-level queue
     tables (<iso>_interconnection_queue) by the note's rule, for each of the six queues whose table is in the folder.

    python replication/interconnection/fetch_rows.py --from <warehouse/output>   # the tables, into rows/ (not in git)
    python replication/interconnection/replicate.py            # part A: N of N, or each difference named
    python replication/interconnection/replicate.py --queues   # parts A and B
    python replication/interconnection/replicate.py --write    # also writes page_figures.json and page_figures.csv
    python replication/interconnection/replicate.py --headline # only the do-file's lines (replicate.do)

    --rows DIR    another folder of tables (default: this folder's rows/)
    --page FILE   the page's figures as a file (the JSON the node script writes) instead of running node

Licenses: iso_queue_statistics is held by grid ("license needed" for NYISO, MISO and ISO-NE since 21 October 2026,
site/data/license_status.json). The page reads and draws no row of a held queue, and neither does part A; part B counts
a held queue's rows that agree and prints no value of them. No row of any table is committed here: page_figures.csv
holds the figures the page draws for CAISO, ERCOT and SPP, whose queue tables are public.

Exit 0 when every figure and every view agrees or its difference is one this file names (NAMED below), 1 when another
differs, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import decimal
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
TABLE = "iso_queue_statistics"

# The explorer's note, "The filters": the six queues in the page's order, and the names the table's header gives them.
QUEUES = [("caiso", "CAISO"), ("ercot", "ERCOT"), ("nyiso", "NYISO"), ("miso", "MISO"), ("spp", "SPP"), ("isone", "ISO-NE")]
NAME = dict(QUEUES)
# "Licenses": held by grid since 21 October 2026 (site/data/license_status.json names the publishers).
HELD_FROM = "2026-10-21"
# "What it draws": the four statuses, in the page's order, and the two counts.
STATUSES = ["operating", "withdrawn", "waiting", "status_not_stated"]
STATUS_HEAD = ["Reached operation", "Withdrawn", "Still waiting", "Status not stated"]
# "What a queue does not hold" (session 7518): ERCOT's first and third groups are headed by what they are, in its own
# view (the headlines, the chart, the table of years); the six queues' table keeps the common words and says so in a tip
OWN_HEAD = {"ercot": {"operating": "Agreement signed", "waiting": "No agreement yet"}}
# "What it draws", 5 (session 7518): in positions the six queues' table also draws these three rows of the entry year
QUEUE_COLUMNS = [("withdrawal_rate", "Withdrawn, share of entered"), ("wait_years_median", "Median wait, years"), ("wait_positions", "Waits counted")]
# "Where the other queues are counted" (session 7518): the queues Berkeley Lab's Queued Up counts on /queues that this page does not show
QUEUED_UP = {"pjm", "miso", "nyiso", "isone"}
MEASURES = {"positions": "positions", "mw": "MW"}
# the table's note, "What counts": the statuses of the queue connector that make each group
GROUPS = {"operating": {"completed"}, "withdrawn": {"withdrawn"}, "waiting": {"active", "suspended"}, "status_not_stated": {""}}
NO_WITHDRAWN = {"ercot"}          # its report lists active and completed positions only
NO_IN_SERVICE = {"miso", "isone"}  # their tables hold no in-service date

# A difference this file names instead of failing on: the key (or its start), and why the two sides differ.
NAMED = {}
# Part B: a queue whose table in the folder is not the run the statistics were built from is compared and reported, and
# its differences are the run's, not a fault of the rule (the header's "Inputs read" line names the run and its rows).


def read_table(path):
    """A standard ERW table: its comment lines (without the mark) and its rows. The header is skipped by its count of
    lines, never by a comment character: a '#' inside a cell (a project named "Unit #2") is data (the table's note)."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    head = [re.sub(r"^#\s?", "", l).rstrip("\r") for l in lines[:n]]
    rows = list(csv.DictReader(lines[n:]))
    return head, rows


def held_grids(today=None):
    """The queues the page holds today: the grids of the table's publishers that ask for a license."""
    with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
        t = json.load(f)["tables"].get(TABLE, {})
    today = today or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    if t.get("status") != "license needed" or today < t.get("from", HELD_FROM):
        return []
    by_name = {v: k for k, v in QUEUES}
    return sorted(by_name[p] for p in t.get("publishers", []) if p in by_name)


def text_of(variable, v):
    """How the page writes a figure (the explorer's note, "How a figure is written"): positions whole, the rest with
    two decimals, each with thousands separators; a value exactly halfway (a share of 0.625) is rounded away from
    zero (0.63), on the value as the table writes it."""
    if variable.startswith("positions_") or variable == "wait_positions" or variable == "undated":
        return f"{round(v):,}"
    return f"{decimal.Decimal(repr(v)).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP):,}"


def tolerance(variable):
    return 0.5 if (variable.startswith("positions_") or variable in ("wait_positions", "undated")) else 0.005


def key_of(queue, year, variable):
    return f"series|{TABLE}|{queue}:queue_{year}|{variable}|{year}-01-01T00:00:00Z"


class Statistics:
    """iso_queue_statistics as the page reads it: one value a queue, an entry year and a variable; and its header."""

    def __init__(self, head, rows):
        self.head = head
        self.value = {}
        for r in rows:
            m = re.fullmatch(r"([a-z]+):queue_(\d{4})", r["entity"])
            if m:
                self.value[(m.group(1), int(m.group(2)), r["variable"])] = float(r["value"])
        self.n_rows = len(rows)
        inputs = next((l for l in head if l.startswith("Inputs read:")), "")
        # the year each queue's input was retrieved in: an entry year at or after it is not over ("A year not over")
        self.retrieved = {}
        self.input_rows = {}
        for q, _ in QUEUES:
            m = re.search(rf"{q}_interconnection_queue \((\d+) rows; retrieved (\d{{4}})(\d{{2}})(\d{{2}})T", inputs)
            if m:
                self.input_rows[q] = int(m.group(1))
                self.retrieved[q] = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
        undated = next((l for l in head if l.startswith("Positions with no queue date")), "")
        self.undated = {}
        for q, name in QUEUES:
            m = re.search(rf"(?:: |, ){re.escape(name)} ([\d,]+)", undated)
            if m:
                self.undated[q] = int(m.group(1).replace(",", ""))
        self.built = next((l for l in head if l.startswith("Retrieved:")), "")

    def years(self, queue):
        return sorted({y for (q, y, _v) in self.value if q == queue})

    def partial(self, queue, year):
        r = self.retrieved.get(queue)
        return year >= (int(r[:4]) if r else dt.datetime.now(dt.timezone.utc).year)

    def has(self, queue, variable):
        return any(q == queue and v == variable for (q, _y, v) in self.value)


def expected_view(S, held, q):
    """What the note says the page draws at one address: the filters as chosen, the three headline numbers, the table
    of every entry year and the six queues side by side, each cell as the key of the row it shows or the words in its
    place."""
    asked = []
    queue = q.get("queue") or "caiso"
    if queue not in NAME:
        queue, _ = "caiso", asked.append("queue")
    measure = q.get("measure") or "positions"
    if measure not in MEASURES:
        measure, _ = "positions", asked.append("measure")
    out = {"queue": queue, "measure": measure, "held": queue in held}
    if queue in held:
        out["asked"] = asked
        return out
    years = S.years(queue)
    complete = [y for y in years if not S.partial(queue, y)]
    first = years[0]
    last = complete[-1] if complete else years[-1]
    a, b = q.get("from") or str(first), q.get("to") or str(last)
    if a not in map(str, years):
        a, _ = str(first), asked.append("first year")
    if b not in map(str, years):
        b, _ = str(last), asked.append("last year")
    lo, hi = sorted((int(a), int(b)))
    span = [y for y in years if lo <= y <= hi]
    prefix = "mw" if measure == "mw" else "positions"
    third = "withdrawal_rate" if S.has(queue, "withdrawal_rate") else f"{prefix}_waiting"
    unit = MEASURES[measure]
    own = [OWN_HEAD.get(queue, {}).get(s, h) for s, h in zip(STATUSES, STATUS_HEAD)]
    third_label = "Withdrawn, share of positions entered" if third == "withdrawal_rate" else f"{own[2]}, {unit}"
    extra = [] if measure == "mw" else QUEUE_COLUMNS
    cell = lambda qq, y, v: key_of(qq, y, v) if (qq, y, v) in S.value else "not held"
    out.update({
        "asked": asked, "lo": lo, "hi": hi, "years": len(years),
        "marked": [f"{y} (partial)" for y in years if S.partial(queue, y)],
        "headlines": [
            {"label": f"{label}, {NAME[queue]}, entered {hi}", "key": cell(queue, hi, v), "note_key": (cell(queue, lo, v) if lo != hi else None)}
            for v, label in ((f"{prefix}_entered", f"Entered, {unit}"), (f"{prefix}_operating", f"{own[0]}, {unit}"), (third, third_label))],
        "years_head": ["Entry year", "Entered"] + own + ([] if measure == "mw" else ["Withdrawn, share of entered", "Median wait, years", "Waits counted"]),
        "queues_head": ["Queue", "Entered"] + STATUS_HEAD + [label for _v, label in extra],
        "own_words_rows": sorted(NAME[k] for k in OWN_HEAD if k not in held),
        "years_rows": [
            {"label": f"{y}{' (partial)' if S.partial(queue, y) else ''}", "muted": S.partial(queue, y),
             "cells": [cell(queue, y, f"{prefix}_entered")] + [cell(queue, y, f"{prefix}_{s}") for s in STATUSES]
             + ([] if measure == "mw" else [cell(queue, y, "withdrawal_rate"), cell(queue, y, "wait_years_median"), cell(queue, y, "wait_positions")])}
            for y in span],
        "queues_rows": [
            {"label": name, "highlight": False, "cells": ["license needed"]} if k in held else
            {"label": name, "highlight": k == queue, "cells": [cell(k, hi, f"{prefix}_entered")] + [cell(k, hi, f"{prefix}_{s}") for s in STATUSES]
             + [cell(k, hi, v) for v, _label in extra]}
            for k, name in QUEUES],
        "undated": S.undated.get(queue),
        "charts": [f"{NAME[queue]}'s queue by entry year and status, {lo} to {hi}, {unit}"]
        + ([f"{NAME[queue]}: the share of each entry year's positions withdrawn"] if S.has(queue, "withdrawal_rate") else [])
        + ([f"{NAME[queue]}: the median wait from entry to operation"] if S.has(queue, "wait_years_median") else []),
    })
    return out


def compare_view(S, held, v):
    """The differences between one view as the page drew it and as the note says it is drawn (an empty list: none)."""
    e = expected_view(S, held, v["q"])
    bad = []
    f = v["filters"]
    def want(what, page, mine):
        if page != mine:
            bad.append(f"{what}: the page {page!r}, the note {mine!r}")
    want("queue chosen", f.get("queue", {}).get("chosen"), e["queue"])
    want("count chosen", f.get("measure", {}).get("chosen"), e["measure"])
    want("address not held, said", sorted(re.findall(r"queue|measure|first year|last year", v["asked_unknown"] or "")), sorted(e["asked"]))
    # session 7518: an address that asks for PJM is told where PJM is counted; a held queue's line points to the same page
    if "asked_pjm" in v:
        want("PJM asked for, said where it is counted", bool(v["asked_pjm"]) and "/queues?grid=pjm&tech=all" in v["links"], v["q"].get("queue") == "pjm")
    if e["held"] and "held_elsewhere" in v:
        want("a held queue, said where Queued Up counts it", v["held_elsewhere"], e["queue"] if e["queue"] in QUEUED_UP else None)
    if e["held"]:
        want("figures of a held queue", v["keyed"], 0)
        want("the held line", bool(v["held_line"]) and "license needed" in v["held_line"], True)
        want("a year filter of a held queue", "from" in f or "to" in f, False)
        want("the decisions drawn under a hold", v.get("decisions"), 12)
        return bad
    want("first entry year chosen", f["from"]["chosen"], str(e["lo"]))
    want("last entry year chosen", f["to"]["chosen"], str(e["hi"]))
    want("years offered", f["from"]["options"], e["years"])
    want("years marked partial", f["from"]["marked"], e["marked"])
    want("headline numbers", [(h["label"], h["key"], h["note_key"] or None) for h in v["headlines"]],
         [(h["label"], h["key"], h["note_key"] if h["note_key"] != "not held" else None) for h in e["headlines"]])
    for h, eh in zip(v["headlines"], e["headlines"]):
        if eh["note_key"] == "not held":
            want("a first year's figure not held", (h["note"] or "").endswith("not held"), True)
    yt = v["years_table"] or {"head": [], "rows": []}
    want("the years table's columns", yt["head"], e["years_head"])
    want("the years table's rows", [(r["label"], r["muted"], r["cells"]) for r in yt["rows"]], [(r["label"], r["muted"], r["cells"]) for r in e["years_rows"]])
    qt = v["queues_table"] or {"rows": [], "head": []}
    want("the six queues' columns", qt.get("head"), e["queues_head"])
    want("the six queues' rows", [(r["label"], r["highlight"], r["cells"]) for r in qt["rows"]], [(r["label"], r["highlight"], r["cells"]) for r in e["queues_rows"]])
    want("the queues whose row says its statuses have words of their own", sorted(r["label"] for r in qt["rows"] if r.get("label_tip")), e["own_words_rows"])
    if "wait_tip" in v:
        want("the wait's chart says whose waits it counts", bool(v["wait_tip"]), S.has(e["queue"], "wait_years_median"))
        want("the line on the load side, with its two pages", bool(v["load_side"]) and "/datacenters" in v["links"] and "/cost-of-power?view=allgrids" in v["links"], True)
    want("the header's count of positions with no queue date", v["undated_line"], [f"{e['undated']:,}", NAME[e["queue"]]] if e["undated"] is not None else None)
    want("charts", v["charts"], e["charts"])
    # "What a queue does not hold": one line for each queue the page shows that has one
    want("the line on what the queue does not hold", v["not_held_line"], e["queue"] if e["queue"] in ("caiso", "ercot", "spp", "miso", "isone") else None)
    want("the decisions drawn", v.get("decisions"), 12)
    keys = [h["key"] for h in e["headlines"]] + [h["note_key"] for h in e["headlines"] if h["note_key"]]
    keys += [c for r in e["years_rows"] for c in r["cells"]] + [c for r in e["queues_rows"] for c in r["cells"]]
    mine = sorted(k for k in keys if k.startswith("series|")) + ([f"series_hdr|{TABLE}|iso:{e['queue']}|Positions with no queue date|{NAME[e['queue']]}"] if e["undated"] is not None else [])
    want("the figures drawn (their keys)", sorted(v["keys"]), sorted(mine))
    return bad


def run_node(table_file, coverage):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not on the path: give --page FILE (the JSON site/scripts/interconnection-figures.mjs writes)")
    out = os.path.join(tempfile.mkdtemp(prefix="erw_interconnection_"), "page.json")
    cmd = [node, "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/interconnection-figures.mjs", os.path.abspath(table_file), out]
    if coverage and os.path.exists(coverage):
        cmd.append(f"--coverage={os.path.abspath(coverage)}")
    r = subprocess.run(cmd, cwd=SITE, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f"the page could not be drawn (exit {r.returncode}): {(r.stderr or r.stdout)[-600:]}")
    return out


def part_a(S, page, held):
    """Every distinct figure and every view of the page against the table. Returns (figures, views, bad lines)."""
    figures, bad = [], []
    for key, f in sorted(page["keyed"].items()):
        p = key.split("|")
        if p[0] == "series_hdr":
            q = p[2].split(":")[1]
            variable, year, mine = "undated", "", S.undated.get(q)
        else:
            q, year = p[2].split(":queue_")
            variable, mine = p[3], S.value.get((q, int(year), p[3]))
        tol = tolerance(variable)
        shown = float(f["text"].replace(",", "")) if re.fullmatch(r"-?[\d,]+(\.\d+)?", f["text"]) else None
        inside = mine is not None and shown is not None and abs(shown - mine) <= tol + 1e-9 and f["text"] == text_of(variable, mine)
        why = next((w for k, w in NAMED.items() if key.startswith(k)), None)
        figures.append({"queue": q, "entry_year": year, "variable": variable, "key": key, "page": f["text"], "replication": mine, "tolerance": tol, "inside": inside, "named": why})
        if q in held:
            bad.append(f"a figure of a held queue is drawn: {key}")
        if not inside and not why:
            bad.append(f"{key}: the page shows {f['text']!r}, the table holds {mine!r} (written {text_of(variable, mine) if mine is not None else 'nothing'!r})")
    views = []
    for v in page["views"]:
        d = compare_view(S, held, v)
        views.append({"q": v["q"], "why": v["why"], "figures": v["keyed"], "not_held_cells": v["not_held"], "as_the_note_says": not d})
        for line in d:
            bad.append(f"view {v['q']}: {line}")
    return figures, views, bad


def part_b(S, rows_dir, held):
    """The table's rows computed again from the queue tables, by the table's note. Returns the report's lines and a
    summary per queue; a held queue's values are never printed."""
    lines, summary, bad = [], {}, []
    for q, name in QUEUES:
        path = os.path.join(rows_dir, f"{q}_interconnection_queue.csv")
        if not os.path.exists(path):
            lines.append(f"  {name}: {os.path.basename(path)} is not in {rows_dir}; not compared")
            continue
        head, rows = read_table(path)
        mine, undated = {}, 0
        by_year = {}
        for r in rows:
            d = (r.get("queue_date") or "").strip()
            if not re.match(r"\d{4}-\d{2}-\d{2}", d):
                undated += 1
                continue
            by_year.setdefault(int(d[:4]), []).append(r)
        for y, rs in by_year.items():
            groups = {"entered": rs}
            for g, words in GROUPS.items():
                if g == "withdrawn" and q in NO_WITHDRAWN:
                    continue
                groups[g] = [r for r in rs if (r.get("status") or "").strip() in words]
            for g, members in groups.items():
                mine[(y, f"positions_{g}")] = float(len(members))
                mws = [float(r["capacity_mw"]) for r in members if (r.get("capacity_mw") or "").strip() != ""]
                if mws:
                    mine[(y, f"mw_{g}")] = sum(mws)
                elif not members:   # session 7020 (done-line request 17): no position is 0 MW, not "not held"
                    mine[(y, f"mw_{g}")] = 0.0
            if "withdrawn" in groups and rs:
                mine[(y, "withdrawal_rate")] = len(groups["withdrawn"]) / len(rs)
            if q not in NO_IN_SERVICE:
                waits = []
                for r in groups["operating"]:
                    a, b = (r.get("queue_date") or "")[:10], (r.get("actual_in_service_date") or "")[:10]
                    try:
                        da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
                    except ValueError:
                        continue
                    if db >= da:
                        waits.append((db - da).days / 365.25)
                mine[(y, "wait_positions")] = float(len(waits))
                if waits:
                    mine[(y, "wait_years_median")] = statistics.median(waits)
                    mine[(y, "wait_years_mean")] = sum(waits) / len(waits)
        theirs = {(y, v): x for (qq, y, v), x in S.value.items() if qq == q}
        keys = sorted(set(mine) | set(theirs))
        same = [k for k in keys if k in mine and k in theirs and abs(mine[k] - theirs[k]) <= 1.5e-6 * max(1.0, abs(theirs[k]))]
        differ = [k for k in keys if k not in same]
        # the same run of the queue: the day its rows were retrieved is the day the statistics' header names for it,
        # and the row count is the one the header gives
        pulled = max((r.get("retrieved_at") or "")[:10] for r in rows) if rows else ""
        same_run = len(rows) == S.input_rows.get(q) and pulled == S.retrieved.get(q)
        if same_run and differ:
            bad.append(f"part B, {name}: {len(differ)} rows of the statistics differ from the same run of the queue table")
        summary[q] = {"rows_in_the_queue_table": len(rows), "rows_the_statistics_read": S.input_rows.get(q), "statistics_rows": len(theirs),
                      "computed_rows": len(mine), "equal": len(same), "differ": len(differ), "undated": undated, "undated_in_header": S.undated.get(q),
                      "held": q in held, "queue_table_retrieved": pulled, "statistics_read_the_pull_of": S.retrieved.get(q), "same_run": same_run}
        lines.append(f"  {name}: {len(same)} of {len(keys)} rows equal at six decimals; positions with no queue date {undated} (the header: {S.undated.get(q)}); "
                     f"the queue table here holds {len(rows):,} rows retrieved {pulled}, the statistics read {S.input_rows.get(q, 0):,} retrieved {S.retrieved.get(q)}"
                     + ("" if same_run or not differ else " (another run of the queue: a difference may be the run's)") + (" [held: no value printed]" if q in held else ""))
        if q not in held:
            for k in differ[:12]:
                lines.append(f"      {q}:queue_{k[0]} {k[1]}: from the queue table {mine.get(k)!r}, the statistics {theirs.get(k)!r}")
            if len(differ) > 12:
                lines.append(f"      and {len(differ) - 12} more")
    return lines, summary, bad


def headline(S):
    """The do-file's five lines (replicate.do), from the table."""
    f = lambda q, y, v: text_of(v, S.value[(q, y, v)]) if (q, y, v) in S.value else "not held"
    cy = [y for y in S.years("caiso") if not S.partial("caiso", y)][-1]
    ey = [y for y in S.years("ercot") if not S.partial("ercot", y)][-1]
    sy = [y for y in S.years("spp") if not S.partial("spp", y)][-1]
    return [
        f"1. CAISO, positions entered {cy}: {f('caiso', cy, 'positions_entered')}",
        f"2. CAISO, positions entered {cy} that reached operation: {f('caiso', cy, 'positions_operating')}",
        f"3. CAISO, withdrawn share of the positions entered {cy}: {f('caiso', cy, 'withdrawal_rate')}",
        f"4. ERCOT, MW entered {ey} and MW of them still waiting: {f('ercot', ey, 'mw_entered')} and {f('ercot', ey, 'mw_waiting')}",
        f"5. SPP, positions entered {sy} and the withdrawn share: {f('spp', sy, 'positions_entered')} and {f('spp', sy, 'withdrawal_rate')}",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The interconnection queue explorer, recomputed (session 7509)")
    ap.add_argument("--rows", default=os.path.join(HERE, "rows"))
    ap.add_argument("--page")
    ap.add_argument("--queues", action="store_true", help="also part B: the table's rows from the queue tables")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true")
    a = ap.parse_args(argv)
    table_file = os.path.join(a.rows, f"{TABLE}.csv")
    try:
        head, rows = read_table(table_file)
    except OSError as e:
        print(f"cannot read {table_file}: {e}. Run fetch_rows.py first.")
        return 2
    S = Statistics(head, rows)
    if a.headline:
        print("\n".join(headline(S)))
        return 0
    held = held_grids()
    try:
        page_file = a.page or run_node(table_file, os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"))
        with open(page_file, encoding="utf-8") as f:
            page = json.load(f)
    except (OSError, RuntimeError, ValueError) as e:
        print(f"cannot read the page's figures: {e}")
        return 2
    if sorted(page.get("held", [])) != held:
        print(f"the page holds {page.get('held')}, the license file says {held}")
        return 1
    figures, views, bad = part_a(S, page, held)
    # the note's own checks on the table: the four statuses make up the positions entered; the share is withdrawn over entered
    sums = 0
    for (q, y, v), x in S.value.items():
        if v != "positions_entered":
            continue
        parts = sum(S.value.get((q, y, f"positions_{s}"), 0.0) for s in STATUSES)
        sums += 1
        if abs(parts - x) > 1e-9:
            bad.append(f"{q}:queue_{y}: the four statuses add to {parts:g}, positions entered {x:g}" + (" [held]" if q in held else ""))
        r = S.value.get((q, y, "withdrawal_rate"))
        if r is not None and abs(r - S.value.get((q, y, "positions_withdrawn"), 0.0) / x) > 1e-6:
            bad.append(f"{q}:queue_{y}: the withdrawal rate is not withdrawn over entered")
    n_in = sum(1 for f in figures if f["inside"])
    v_ok = sum(1 for v in views if v["as_the_note_says"])
    print(f"table: {S.n_rows:,} rows; {S.built}")
    print(f"part A: {n_in:,} of {len(figures):,} figures inside the tolerance; {v_ok} of {len(views)} views drawn as the note says; "
          f"{sums} queue-years whose four statuses make up the positions entered; held and not read: {', '.join(NAME[h] for h in held) or 'none'}")
    summary = None
    if a.queues:
        lines, summary, bad_b = part_b(S, a.rows, held)
        bad += bad_b
        print("part B: the table's rows computed again from the queue tables")
        print("\n".join(lines))
    for line in bad[:60]:
        print("DIFFERS  " + line)
    if a.write:
        opening = next(v for v in page["views"] if not v["q"])
        js = {
            "_about": "The interconnection queue explorer (/explore/interconnection): every figure the page draws for each queue it shows (CAISO, ERCOT, SPP), in positions and in MW, for every first and last entry year it offers, as the page's own code draws it on iso_queue_statistics (site/scripts/interconnection-figures.mjs), beside the replication's reading of the table (replication/interconnection/replicate.py, written from docs/methods/interconnection_explorer.md). A figure's check key is series|iso_queue_statistics|<queue>:queue_<entry year>|<variable>|<year>. The tolerance is half the last digit shown: 0.5 for a count, 0.005 for MW, a share or a wait in years. The figures are in page_figures.csv, one line each. NYISO, MISO and ISO-NE are held (license needed): none of their figures is drawn or kept.",
            "table": {"rows": S.n_rows, "built": S.built, "inputs_retrieved": S.retrieved, "positions_with_no_queue_date": {q: n for q, n in S.undated.items() if q not in held}},
            "held": held,
            "views": len(views), "views_as_the_note_says": v_ok,
            "figures": len(figures), "figures_inside_the_tolerance": n_in,
            "queue_years_whose_statuses_make_up_the_entered": sums,
            "opening": {"queue": "caiso", "count": "positions", "headlines": [
                {"label": h["label"], "key": h["key"], "page": page["keyed"].get(h["key"], {}).get("text"),
                 "first_year": page["keyed"].get(h["note_key"] or "", {}).get("text")} for h in opening["headlines"]]},
            "views_list": [{"address": "&".join(f"{k}={x}" for k, x in v["q"].items()), "why": v["why"], "figures": v["figures"], "cells_not_held": v["not_held_cells"], "as_the_note_says": v["as_the_note_says"]} for v in views],
            "named_differences": NAMED,
        }
        if summary is not None:
            js["table_from_the_queue_tables"] = summary
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(js, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="\n") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["queue", "entry_year", "variable", "page", "replication", "tolerance"])
            for x in figures:
                w.writerow([x["queue"], x["entry_year"], x["variable"], x["page"], f"{x['replication']:.6f}" if x["replication"] is not None else "", x["tolerance"]])
        print("written: page_figures.json, page_figures.csv")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
