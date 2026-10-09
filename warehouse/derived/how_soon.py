"""Energy Research Warehouse (ERW), session 163: the one file the block "How long a large load waits" reads, in the
section "How soon" of "What a datacenter pays" (/cost-of-power, in review).

    python warehouse/derived/how_soon.py                                        # on the data machine: site/data/datacenter/how_soon.json
    python warehouse/derived/how_soon.py --in-dir C:/.../erw/warehouse/output   # from a working copy that holds no tables
    python warehouse/derived/how_soon.py --in-dir DIR --out-dir TRIAL           # a trial: TRIAL/how_soon.json, nothing in site/data

Reads two INTERNAL tables and writes AGGREGATES ONLY. Nothing else of the tables reaches the site:

    large_load_waits        one row a request and stage interval, measured from dated copies of public queues
                            (warehouse/connectors/large_load_waits.py, sessions 155 and 160)
    large_load_statements   one row a figure as a document states it (sessions 139, 141 and 151)

What the file holds, by grid of the page:

    measured here    for each stage interval: the count of requests behind it; of those measured, the median's lower and
                     upper bound and the range all of them lie within; of those still waiting, the count and the range
                     of their days so far, marked a lower bound; counts of the two other labels. The copies read: how
                     many, the first and last day, the requests seen and followed.
    stated           the entity's own figures of a wait, as written: the figure, whether it is a measurement of the
                     entity's own or an expectation, what it covers, who stated it, the document, its date, page and
                     address. No sentence of a document is copied (the statements are internal until a person rules on
                     each publisher's terms; session 154's rule: a figure and a link, not a sentence).
    not measured     why (ERCOT's reports name no request), with the counts the waits table's own header records.

What it never holds: a request's name, its queue position, its megawatts, its size class, its own dates or any single
request's row. The rules, stated here and tested (tests/test_session163.py):

    MIN_FOR_MEDIAN = 5   a median is given on five or more measured requests (the table's own rule, session 155)
    MIN_FOR_BOUNDS = 2   on two to four the file holds the count and the group's two bounds (the least "at least" and
                         the greatest "at most"), never each request's own range; on one it holds the count and the
                         words "too few to show": a figure on one request is that request's row

A duration is a range between two copies, never a midpoint; nothing is filled, interpolated or smoothed. A lower bound is
marked a lower bound wherever it stands. An entity is shown only where ENTITY_GRID places it on one of the page's
grids; any other entity in the table is left out of the file and named in the summary this builder prints (session 165
appends further queues: they change nothing here until a line of ENTITY_GRID names them). MISO is never a key of the
file's measured grids: it is paused. No request is made to anyone and no model is called.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "site", "data", "datacenter", "how_soon.json")
WAITS, STATEMENTS = "large_load_waits", "large_load_statements"
MIN_FOR_MEDIAN = 5
MIN_FOR_BOUNDS = 2
TOO_FEW = "too few to show"
EM_DASH = chr(0x2014)

# Which entity of large_load_waits stands for which grid of the page. Written down, one line an entity: an entity not
# named here is left out of the file and named in the printed summary. MISO has no line and gets none while it is paused.
ENTITY_GRID = {
    "New York ISO": "nyiso",
    "ERCOT": "ercot",
    "California ISO": "caiso",
    "ISO New England": "isone",
    "Southwest Power Pool": "spp",
    "PJM Interconnection": "pjm",
    # session 171: Virginia (Dominion) under PJM's region. The line takes effect when the waits table holds Dominion's
    # requests followed from dated copies; on 9 October 2026 it holds none (the commission's robots file disallows every
    # agent not named, so no filing of PUR-2026-00011 was fetched: docs/methods/large_load_waits.md).
    "Dominion Energy Virginia": "pjm",
}
# Whose stated figures stand under which grid (entity_group of large_load_statements). Texas: ERCOT and Oncor, the two
# session 160's table lists. Another grid's line is added here when a person wants its entities' figures shown.
# Session 171: Dominion's own stated timelines (its filings in PUR-2026-00011 and its PJM load forecast documentation,
# read by sessions 151 and 154) stand under PJM's grid, labeled Dominion's; the statements of others about Dominion
# (Amazon's, Google's) are not Dominion's and are not shown. PJM's prices stay licensed and unshown: this is the waits block.
STATED_GROUPS = {
    "nyiso": ["New York ISO"],
    "ercot": ["ERCOT", "Oncor Electric Delivery"],
    "pjm": ["Dominion Energy Virginia"],
}
PLACES = {"nyiso": "New York", "ercot": "Texas", "pjm": "Virginia"}
PAUSED = ["miso"]
# The page's grids that are not measured and have no line above read "not measured yet" (the site's words, lib/howsoon.ts).

# The stage intervals the block shows, in this order, each with the page's label and the words the summary sentence
# uses. An interval of the table that is not here ("in stage", by the publisher's status words) is left out and counted.
STAGES = [
    ("request to study", "Request to the first study status", "from request to the first study status"),
    ("system impact study, pending or in progress to approved", "System impact study, pending to approved", "through the system impact study from pending to approved"),
    ("request to agreement", "Request to a signed agreement", "from request to a signed agreement"),
    ("study to agreement", "First study status to a signed agreement", "from the first study status to a signed agreement"),
    ("request to construction", "Request to under construction", "from request to under construction"),
    ("request to energized", "Request to in service", "from request to in service"),
    ("agreement to energized", "Signed agreement to in service", "from a signed agreement to in service"),
    ("request to withdrawal", "Request to withdrawal", "from request to withdrawal"),
]
# The stage whose measured figure leads the summary sentence where it holds enough requests, then the stage a stated
# figure stands beside.
SERVICE = "request to energized"
LEAD = ["system impact study, pending or in progress to approved"]

# A stated figure set beside the stage it speaks of: (entity group, what it covers as the table words it, the figure as
# written) -> (the interval, a mark for the face or "", what differs, for the hover). The words are this builder's,
# from the notes of sessions 151 and 155; no sentence of a document is copied.
BESIDE = [
    (("New York ISO", "System Impact Study (SIS)", "nine months"),
     ("system impact study, pending or in progress to approved", "",
      "Not the same start: NYISO's figure runs from the customer's study selection, a day no copy shows; the measurement runs from the first copy that shows the study pending.")),
    (("New York ISO", "System Impact Study (SIS)", "90-day"),
     ("system impact study, pending or in progress to approved", "proposed",
      "A step of a procedure NYISO proposed in July 2026, not the one the measured requests went through.")),
    (("New York ISO", "project scoping call", "2 weeks"),
     ("request to study", "",
      "Not the same start or end: NYISO's figure runs from its finding a request complete to its scheduling a scoping call, and no copy shows either day.")),
]
# A note for the hover of a group of stated figures, by entity group and the start of what they cover.
GROUP_NOTES = [
    ("ERCOT", "Batch Zero study, step", "ERCOT wrote each step and not their sum: the steps are not added here."),
]
# Why a grid has no measured wait although its reports were read: the clause of the waits table's own header that
# records it, and the words around the counts it gives.
NOT_MEASURED = {
    "ercot": {
        "entity": "ERCOT",
        "clause": re.compile(r"ERCOT[^:.;]*: (\d+) status reports read \((\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)\), (\d+) name a request"),
        "what": "large load status reports",
        "why": "Each report gives totals by stage for the whole system and names no request, so no request can be followed from copy to copy and no wait is measured from them.",
    },
}
SOURCE_WORDS = {
    "nyiso:interconnection_queue_dated_copies": "NYISO's interconnection queue workbook (its load requests)",
}
READ_FROM = "the Internet Archive's Wayback Machine and the publisher's own site"
BASIS_ORDER = {"measured": 0, "expected": 1, "general statement": 2}


def read_table(path):
    """The header comment lines (without the #) and the rows of one table."""
    head, lines = [], []
    with open(path, encoding="utf-8", newline="") as f:
        for ln in f:
            if ln.startswith("#") and not lines:
                head.append(ln[1:].strip())
            else:
                lines.append(ln)
    return head, list(csv.DictReader(lines))


def find(name, dirs):
    for d in dirs:
        p = os.path.join(d, name + ".csv")
        if os.path.exists(p):
            return p
    return None


def header_value(head, start):
    for h in head:
        if h.startswith(start):
            return h[len(start):].strip()
    return ""


def num(text):
    """A whole number of days as an int, a half as a float; "" as None. Never rounded."""
    if text is None or str(text).strip() == "":
        return None
    v = float(text)
    return int(v) if v == int(v) else v


def median(values):
    v = sorted(values)
    m = len(v) // 2
    return v[m] if len(v) % 2 else num((v[m - 1] + v[m]) / 2)


def figure(rows):
    """The aggregates of one entity's rows of one interval, and nothing of any one request."""
    meas = [(num(r["days_at_least"]), num(r["days_at_most"])) for r in rows if r["label"] == "measured"]
    if any(a is None or b is None for a, b in meas):
        raise SystemExit("a row labeled measured holds no days_at_least or no days_at_most: the table is not as its header says")
    low = sorted(num(r["days_at_least"]) for r in rows if r["label"] == "lower bound" and r["days_at_least"] != "")
    low_n = sum(1 for r in rows if r["label"] == "lower bound")
    two_n = sum(1 for r in rows if r["label"] == "two copies only")
    up_n = sum(1 for r in rows if r["label"] == "upper bound")
    other = sorted({r["label"] for r in rows} - {"measured", "lower bound", "two copies only", "upper bound"})
    measured = {"n": len(meas), "form": "none"}
    if len(meas) >= MIN_FOR_MEDIAN:
        measured.update(form="median", median_at_least=median([a for a, _ in meas]), median_at_most=median([b for _, b in meas]),
                        least=min(a for a, _ in meas), most=max(b for _, b in meas))
    elif len(meas) >= MIN_FOR_BOUNDS:
        measured.update(form="bounds", least=min(a for a, _ in meas), most=max(b for _, b in meas))
    elif meas:
        measured.update(form="too few", words=TOO_FEW)
    waiting = {"n": low_n, "lower_bound": True, "form": "none"}
    if len(low) >= MIN_FOR_BOUNDS and len(low) == low_n:
        waiting.update(form="range", least=low[0], most=low[-1])
    elif low_n:
        waiting.update(form="too few", words=TOO_FEW)
    out = {"requests": len(rows), "measured": measured, "waiting": waiting,
           "two_copies_only": {"n": two_n, "lower_bound": True}, "ended_before_first_copy": {"n": up_n}}
    if other:
        out["other_labels"] = {"n": sum(1 for r in rows if r["label"] in other), "labels": other}
    return out


def statistic_of(row):
    """Whether a figure the entity measured itself is an average or a median, by the word its own sentence uses."""
    if row.get("wait_basis") != "measured":
        return ""
    s = row.get("sentence", "")
    if re.search(r"\bmedian\b", s, re.I):
        return "median"
    if re.search(r"\baverage\b", s, re.I):
        return "average"
    return ""


def stated_of(rows, groups):
    """The distinct wait figures the grid's own entities state, as written, with no sentence of any document."""
    out = []
    for r in rows:
        if r.get("row_kind") != "wait" or r.get("entity_group") not in groups:
            continue
        if r.get("wait_counted") != "yes" or r.get("wait_figure_holder") != "yes" or r.get("source_flag", "") != "":
            continue
        if r.get("load_scope", "").startswith("all distribution"):
            continue
        url = r.get("source_url", "")
        if not url.startswith("https://") or "@" in url or "%40" in url:
            continue
        s = {"stated_by": r["entity_group"], "figure": r["quantity_as_written"].strip(), "basis": r["wait_basis"], "statistic": statistic_of(r),
             "covers": r["status"].strip(), "document": r["document_title"].strip(), "document_type": r["document_type"].strip(),
             "date": r["event_date"], "date_basis": r.get("event_date_basis", ""), "page": r.get("page", "").strip(), "url": url, "mark": "", "note": ""}
        for (group, covers, fig), (interval, mark, differs) in BESIDE:
            if (s["stated_by"], s["covers"], s["figure"]) == (group, covers, fig):
                s["beside"], s["mark"], s["note"] = interval, mark, differs
        for group, start, note in GROUP_NOTES:
            if s["stated_by"] == group and s["covers"].startswith(start):
                s["note"] = note
        out.append(s)
    out.sort(key=lambda s: (BASIS_ORDER.get(s["basis"], 9), s["date"], s["stated_by"], s["statistic"], s["covers"], s["figure"]))
    return out


def build(w_head, w_rows, s_head, s_rows, now=None):
    """The file, and what was left out (for the printed summary)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    this_run = header_value(w_head, "This run:")
    by_entity = {}
    for r in w_rows:
        by_entity.setdefault(r["entity"], []).append(r)
    grids, left_entities, left_intervals = {}, [], {}
    known = [i for i, _, _ in STAGES]
    for entity, rows in sorted(by_entity.items()):
        grid = ENTITY_GRID.get(entity)
        if grid is None or grid in PAUSED:
            left_entities.append({"entity": entity, "rows": len(rows), "why": "paused" if grid in PAUSED else "on none of the page's grids (ENTITY_GRID)"})
            continue
        if grid in grids:
            raise SystemExit(f"two entities of {WAITS} stand for the grid {grid}: ENTITY_GRID must name one")
        m = re.search(re.escape(entity) + r": (\d+) copies read \((\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)\), (\d+) requests seen, (\d+) followed", this_run)
        followed = len({r["request_id"] for r in rows})
        copies = {"n": int(m.group(1)) if m else None,
                  "first": m.group(2) if m else min(r["first_copy_date"] for r in rows if r["first_copy_date"]),
                  "last": m.group(3) if m else max(r["last_copy_date"] for r in rows if r["last_copy_date"]),
                  "requests_seen": int(m.group(4)) if m else None, "requests_followed": followed,
                  "what": "; ".join(SOURCE_WORDS.get(s, s) for s in sorted({r["source"] for r in rows})), "read_from": READ_FROM,
                  "retrieved": max(r["retrieved_at"] for r in rows)}
        if m and int(m.group(5)) != followed:
            raise SystemExit(f"{entity}: the table's header says {m.group(5)} requests followed and its rows hold {followed}")
        stages = []
        for interval, label, phrase in STAGES:
            rs = [r for r in rows if r["interval"] == interval]
            if not rs:
                continue
            if len({r["request_id"] for r in rs}) != len(rs):
                raise SystemExit(f"{entity}, {interval}: more than one row for a request, so a count of rows is not a count of requests")
            stages.append(dict({"interval": interval, "label": label, "phrase": phrase}, **figure(rs), stated=[]))
        for r in rows:
            if r["interval"] not in known:
                left_intervals[r["interval"]] = left_intervals.get(r["interval"], 0) + 1
        grids[grid] = {"state": "measured", "entity": entity, "copies": copies, "stages": stages, "stated": []}
    for grid, spec in NOT_MEASURED.items():
        if grid in grids:
            continue
        m = spec["clause"].search(this_run)
        grids[grid] = {"state": "not measured here", "entity": spec["entity"], "stages": [], "stated": [],
                       "reports": {"n": int(m.group(1)) if m else None, "first": m.group(2) if m else None, "last": m.group(3) if m else None,
                                   "requests_named": int(m.group(4)) if m else None, "what": spec["what"], "why": spec["why"], "read_from": READ_FROM}}
    stated_left = []
    for grid, groups in STATED_GROUPS.items():
        if grid in PAUSED:
            continue
        g = grids.setdefault(grid, {"state": "not measured yet", "stages": [], "stated": []})
        for s in stated_of(s_rows, groups):
            stage = next((st for st in g["stages"] if st["interval"] == s.get("beside")), None)
            s.pop("beside", None)
            (stage["stated"] if stage else g["stated"]).append(s)
    for (group, covers, fig), _ in BESIDE:
        if not any(s["stated_by"] == group and s["covers"] == covers and s["figure"] == fig for g in grids.values() for st in g["stages"] for s in st["stated"]):
            stated_left.append(f"{group}: {fig} ({covers})")
    for grid, place in PLACES.items():
        if grid in grids:
            grids[grid]["place"] = place
    file = {
        "built_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "built_by": "warehouse/derived/how_soon.py",
        "holds": "aggregates only: counts, bounds and medians by stage, and stated figures with their documents; no request, no name, no queue position and no size of a request",
        "unit": "days",
        "rule": {"min_for_median": MIN_FOR_MEDIAN, "min_for_bounds": MIN_FOR_BOUNDS, "too_few": TOO_FEW},
        "summary": {"service": SERVICE, "lead": LEAD},
        "tables": {
            WAITS: {"license": "internal", "rows": len(w_rows), "retrieved": header_value(w_head, "Retrieved:").split(" ")[0]},
            STATEMENTS: {"license": "internal", "rows": len(s_rows), "retrieved": header_value(s_head, "Retrieved:").split(" ")[0]},
        },
        "paused": PAUSED,
        "grids": grids,
        # an entity left out is named in the printed summary only, never in the file
        "left_out": {"entities": len(left_entities), "interval_rows": sum(left_intervals.values()), "intervals": sorted(left_intervals)},
    }
    return file, {"entities": left_entities, "intervals": left_intervals, "beside_unmatched": stated_left}


FORBIDDEN_KEYS = ("request_id", "request_name", "queue_position", "queue_date", "mw", "megawatt", "size_class", "parties", "event_id", "sentence")


def check(file, w_rows):
    """Refuse to write a file that holds a request-level field, a request's name or a lettered queue position, or a
    character this repository does not write. The test repeats this from the raw rows, by its own code."""
    text = json.dumps(file, ensure_ascii=False)
    if EM_DASH in text:
        raise SystemExit("a value of the file holds an em dash (a document's title, most likely): the file is not written")
    def keys(v):
        if isinstance(v, dict):
            for k, x in v.items():
                yield k
                yield from keys(x)
        elif isinstance(v, list):
            for x in v:
                yield from keys(x)
    for k in keys(file):
        if k.lower() in FORBIDDEN_KEYS or "mw" in re.split(r"[^a-z]+", k.lower()):
            raise SystemExit(f"the file holds a request-level field: {k}")
    low = text.lower()
    # session 171: the names of the requests of the entities whose rows are in the file (the measured grids). A request of an
    # entity the file leaves out cannot be in it; its name can only match by chance a phrase the page's own documents use
    # (a Bonneville request named "Data Center" against the title of a Dominion letter about data center load). The same rule
    # as the page check of session 163. A request's own values stay refused whatever its entity (FORBIDDEN_KEYS above).
    shown = {g.get("entity") for g in file.get("grids", {}).values() if g.get("state") == "measured"}
    for r in w_rows:
        if r.get("entity") not in shown:
            continue
        for name in [r.get("request_name", "")] + re.split(r"[;|]", r.get("request_names_seen", "")):
            name = name.strip().lower()
            if len(name) >= 4 and name in low:
                raise SystemExit("the file holds a request's name: it is not written")


def summary(file, left):
    lines = [f"how_soon: {file['tables'][WAITS]['rows']} rows of {WAITS}, {file['tables'][STATEMENTS]['rows']} of {STATEMENTS}"]
    for grid, g in file["grids"].items():
        n_stated = len(g["stated"]) + sum(len(st["stated"]) for st in g["stages"])
        if g["state"] == "measured":
            c = g["copies"]
            lines.append(f"  {grid}: measured, {g['entity']}: {c['n']} copies ({c['first']} to {c['last']}), {c['requests_followed']} requests followed, {len(g['stages'])} stages, {n_stated} stated figures")
            for st in g["stages"]:
                m, wt = st["measured"], st["waiting"]
                shown = (f"median at least {m['median_at_least']}, at most {m['median_at_most']}; all within {m['least']} to {m['most']}" if m["form"] == "median"
                         else f"between {m['least']} and {m['most']}" if m["form"] == "bounds" else m.get("words", "none"))
                lines.append(f"    {st['interval']}: {st['requests']} requests; measured {m['n']} ({shown}); lower bounds {wt['n']}"
                             + (f" (at least {wt['least']} to {wt['most']})" if wt["form"] == "range" else "") + f"; stated beside {len(st['stated'])}")
        else:
            r = g.get("reports") or {}
            lines.append(f"  {grid}: {g['state']}" + (f": {r.get('n')} reports, {r.get('requests_named')} name a request" if r else "") + f"; {n_stated} stated figures")
    for e in left["entities"]:
        lines.append(f"  LEFT OUT, entity: {e['entity']} ({e['rows']} rows): {e['why']}")
    for i, n in sorted(left["intervals"].items()):
        lines.append(f"  left out, interval not shown: {i} ({n} rows of the entities shown)")
    for b in left["beside_unmatched"]:
        lines.append(f"  NOTE: a stated figure this builder sets beside a stage is not in the table: {b}")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--in-dir", action="append", default=[], help="a directory of tables; may be given more than once, the first that holds a table wins (default: warehouse/output)")
    ap.add_argument("--out-dir", help="a trial run: how_soon.json under this directory; nothing in site/data")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in args.in_dir] or [os.path.join(ROOT, "warehouse", "output")]
    paths = {name: find(name, dirs) for name in (WAITS, STATEMENTS)}
    missing = [n for n, p in paths.items() if not p]
    if missing:
        print(f"how_soon: FAILED: not found in {dirs}: {', '.join(missing)}. No file is written.", file=sys.stderr)
        return 1
    w_head, w_rows = read_table(paths[WAITS])
    s_head, s_rows = read_table(paths[STATEMENTS])
    for name, head in ((WAITS, w_head), (STATEMENTS, s_head)):
        if not header_value(head, "License:").startswith("internal"):
            print(f"how_soon: note: {name} no longer says it is internal; this builder still writes aggregates only")
    file, left = build(w_head, w_rows, s_head, s_rows)
    check(file, w_rows)
    out = os.path.join(os.path.abspath(args.out_dir), "how_soon.json") if args.out_dir else OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    same = False
    if os.path.exists(out):
        try:
            with open(out, encoding="utf-8") as f:
                old = json.load(f)
            same = {k: v for k, v in old.items() if k != "built_at_utc"} == {k: v for k, v in file.items() if k != "built_at_utc"}
        except (OSError, ValueError):
            same = False
    if not same:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(file, f, ensure_ascii=False, indent=1)
            f.write("\n")
    for ln in summary(file, left):
        print(ln)
    print(f"how_soon: {'unchanged' if same else 'written'}: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
