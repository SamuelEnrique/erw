#!/usr/bin/env python3
"""Session 2224 (chain 152): twenty questions a lab's energy team asks of Ask the warehouse, each expected answer
computed from the live set by this script, never typed.

Energy Research Warehouse (ERW). No model call of any kind. Reads only: the live set's `catalogue`, `series` and
`entities` views (Supabase REST, the anon key from the repository's .env, or the main checkout's beside a worktree),
1,000 rows a page. Writes warehouse/chat/eval/questions_s2224.yaml (the set, read by eval_s1113.py and eval_loop.py with
--set s2224) and warehouse/chat/eval/keys_s2224.json (the keys with the time they were computed) beside the other sets.

    python scripts/ask_eval/lab_questions.py            computes the keys and writes both files
    python scripts/ask_eval/lab_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation
                                                        in any key (the day's live set against the stored keys)

The twenty, by what the team asks (the chain's prompt): disclosed PPA prices by technology and buyer (energy_deals, a
table held whole for a license since 21 October 2026: the expected answer is the hold's words and no figure); MW in each
grid's interconnection queue (the ISOs' queue tables, entities, the sum of capacity_mw by status; MISO's is paused, so
its answer is the pause's words); the datacenter tracker's MW by grid and operator (datacenter_facilities and
datacenter_projects, held whole: the hold's words); storage on each grid (storage_buildout_monthly, the September 2026
row); a grid's day-ahead average and peak (cost_of_power_monthly's da_simple_mean for October 2026, price_board_peak_offpeak's
yearly peak mean for 2026 so far; a grid's reserve margin from grid_peak_vs_capacity, 2025); a node's basis
(node_basis_summary, ERCOT's hub average, October 2026); and one question the warehouse does not hold at all. Two keys
(l17, l18) read tables whose catalogue row says in_live_set review: the site's tools read them and the Python loop's
package did not (session 2223's finding), so they test that both loops read what the live set allows.

Each key's note names the table, the entity or filter, the variable or column, the period and the aggregation. Tolerance
0.01 under 1,000 and 0.5 from 1,000 (as questions_s1114.yaml). A refusal key (refuse: true) has no figure and names the
words the answer must carry; `hold: true` marks a table held whole, whose answer may be a refusal or an answer in the
hold's words, with no figure either way.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV_ROOT = ROOT if os.path.exists(os.path.join(ROOT, ".env")) else os.path.join(os.path.dirname(ROOT), "erw")
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
OUT = os.path.join(EVAL, "questions_s2224.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_s2224.json")
TODAY = "2026-11-06"
SB, CP, PB, GP, NB = "storage_buildout_monthly", "cost_of_power_monthly", "price_board_peak_offpeak", "grid_peak_vs_capacity", "node_basis_summary"
E, SP15, SPPN = "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB"
LICENSE = "license needed"


def env(name):
    if os.environ.get(name):
        return os.environ[name].strip()
    for line in open(os.path.join(ENV_ROOT, ".env"), encoding="utf-8"):
        m = re.match(rf"^{name}=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"')
    raise SystemExit(f"{name} not in .env")


def base_url():
    u = env("SUPABASE_URL").rstrip("/")
    return u if u.endswith("/rest/v1") else u + "/rest/v1"


def get(path, **q):
    url, key = base_url(), env("SUPABASE_ANON_KEY")
    out, off = [], 0
    while True:
        qq = dict(q)
        qq["limit"], qq["offset"] = "1000", str(off)
        req = urllib.request.Request(f"{url}/{path}?" + urllib.parse.urlencode(qq), headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            page = json.loads(r.read())
        out += page
        if len(page) < 1000:
            return out
        off += 1000


def month_value(table, entity, variable, month):
    """The one monthly row's value (ts_utc the first of the month); the run stops when it is missing or doubled."""
    rows = get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
               **{"and": f"(ts_utc.gte.{month}-01,ts_utc.lt.{next_month(month)}-01)"})
    rows = [r for r in rows if r["value"] is not None]
    if len(rows) != 1:
        raise SystemExit(f"{table} {entity} {variable} {month}: {len(rows)} rows, one expected")
    return float(rows[0]["value"])


def year_value(table, entity, variable, year):
    rows = get("series", table_name=f"eq.{table}", entity=f"eq.{entity}", variable=f"eq.{variable}", select="ts_utc,value",
               **{"and": f"(ts_utc.gte.{year}-01-01,ts_utc.lt.{year + 1}-01-01)"})
    rows = [r for r in rows if r["value"] is not None]
    if len(rows) != 1:
        raise SystemExit(f"{table} {entity} {variable} {year}: {len(rows)} rows, one expected")
    return float(rows[0]["value"])


def next_month(month):
    y, m = int(month[:4]), int(month[5:7])
    return f"{y + (m == 12)}-{(m % 12) + 1:02d}"


def queue_mw(table, status):
    """The sum of capacity_mw over the rows of one status of a queue table (entities), and their count."""
    rows = get("entities", table_name=f"eq.{table}", status=f"eq.{status}", select="capacity_mw")
    vals = [float(r["capacity_mw"]) for r in rows if r.get("capacity_mw") not in (None, "")]
    if not vals:
        raise SystemExit(f"{table} status {status}: no rows")
    return round(sum(vals), 4), len(rows)


def catalogue():
    return {c["table_name"]: c for c in get("catalogue", select="table_name,in_live_set,license,n_rows,ts_min,ts_max")}


def held(table, grid=None):
    """Whether the site holds the table for a license (site/data/license_status.json, the file both loops read): whole, or
    the given grid's rows of it. A figure key is never written for a held table (the first asking of 6 November 2026
    wrote one for ISO-NE's queue, and the loop's right answer, the hold's words, was graded wrong)."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
    import license_hold as hold
    if not hold.license_needed(table):
        return False
    if hold.held_whole(table):
        return True
    return bool(grid) and hold.held_row(table, f"{hold.GRID_PREFIX.get(grid, grid.lower())}:x")


def tolerance(x):
    return 0.5 if abs(x) >= 1000 else 0.01


def figure(qid, grid, via, question, table, value, note, text=()):
    if held(table, grid if grid != "none" else None):
        raise SystemExit(f"{qid}: {table} is held for a license ({grid}); a figure key cannot be written for it")
    return {"id": qid, "grid": grid, "via": via, "question": question, "expected": [round(value, 4)], "tolerance": tolerance(value),
            "text": list(text), "tables": [table], "refuse": False, "hold": False, "note": note}


def refusal(qid, grid, via, question, text, note, hold=False, tables=()):
    return {"id": qid, "grid": grid, "via": via, "question": question, "expected": [], "tolerance": 0.01, "text": list(text),
            "tables": list(tables), "refuse": True, "hold": hold, "note": note}


def build():
    cat = catalogue()
    for t in ("energy_deals", "datacenter_facilities", "datacenter_projects", "miso_interconnection_queue", SB, CP, PB, GP, NB,
              "ercot_interconnection_queue", "caiso_interconnection_queue", "spp_interconnection_queue", "isone_interconnection_queue"):
        if t not in cat or cat[t]["in_live_set"] not in ("yes", "review"):
            raise SystemExit(f"{t} is not in the live set's catalogue as yes or review")
    qs = []
    # PPA prices: energy_deals is held whole for a license (site/data/license_status.json, since 21 October 2026)
    qs.append(refusal("l01", "none", "general", "What was the average disclosed price of the solar power purchase agreements signed in 2026, in USD per MWh?",
                      [LICENSE], "energy_deals (price_value, technology solar, 2026) is held whole for a license: the answer carries the hold's words and no figure", hold=True, tables=["energy_deals"]))
    qs.append(refusal("l02", "none", "general", "Which buyer signed the largest power purchase agreement by MW in 2026, and for how many MW?",
                      [LICENSE], "energy_deals (buyer, mw, 2026) is held whole for a license: the hold's words and no figure", hold=True, tables=["energy_deals"]))
    # the datacenter tracker: held whole
    # l03 is asked through the general chat: a grid's scoped chat sees the grid's tables alone, and the tracker's tables are no
    # grid's, so ERCOT's chat answered "not in the warehouse" without the hold's words at the first asking (02:05 UTC)
    qs.append(refusal("l03", "none", "general", "How many MW of datacenter projects does the tracker hold in ERCOT?",
                      [LICENSE], "datacenter_projects (mw, ERCOT) is held whole for a license: the hold's words and no figure", hold=True, tables=["datacenter_projects"]))
    qs.append(refusal("l04", "none", "general", "Which datacenter operator has the most MW of facilities in the tracker, and how many MW?",
                      [LICENSE], "datacenter_facilities (operator, mw) is held whole for a license: the hold's words and no figure", hold=True, tables=["datacenter_facilities"]))
    # the interconnection queues: MW by status, the ISOs' own tables (entities, a snapshot)
    for qid, grid, table, status, words in (("l05", "ERCOT", "ercot_interconnection_queue", "active", "ERCOT's interconnection queue"),
                                            ("l06", "CAISO", "caiso_interconnection_queue", "active", "CAISO's interconnection queue"),
                                            ("l07", "SPP", "spp_interconnection_queue", "active", "SPP's interconnection queue")):
        mw, n = queue_mw(table, status)
        qs.append(figure(qid, grid, "grid", f"How many MW are {status} in {words}, summed over its {status} requests?", table, mw,
                         f"{table}: the sum of capacity_mw over the {n} rows with status {status} (the snapshot of {cat[table]['ts_max'][:10]})"))
    # ISO-NE's queue is ISO-NE's own table, held for a license (by grid): the hold's answer, as session 1112 grades a held grid
    if not held("isone_interconnection_queue", "ISO-NE"):
        raise SystemExit("isone_interconnection_queue is no longer held: l08 wants a figure key again")
    qs.append(refusal("l08", "ISO-NE", "grid", "How many MW are active in ISO-NE's interconnection queue, summed over its active requests?", [LICENSE],
                      "isone_interconnection_queue is ISO-NE's own and held for a license (site/data/license_status.json): the hold's words and no figure, as a refusal or as an answer", hold=True, tables=["isone_interconnection_queue"]))
    mw, n = queue_mw("caiso_interconnection_queue", "withdrawn")
    qs.append(figure("l09", "CAISO", "grid", "How many MW are withdrawn in CAISO's interconnection queue, summed over its withdrawn requests?", "caiso_interconnection_queue", mw,
                     f"caiso_interconnection_queue: the sum of capacity_mw over the {n} rows with status withdrawn (the snapshot of {cat['caiso_interconnection_queue']['ts_max'][:10]})"))
    qs.append(refusal("l10", "MISO", "grid", "How many MW are active in MISO's interconnection queue?", ["paused"],
                      "miso_interconnection_queue is MISO's own: MISO is paused while its terms are reviewed (since 4 October 2026), so the answer is the pause's words and no figure", tables=["miso_interconnection_queue"]))
    # storage on the grids: the September 2026 rows of storage_buildout_monthly
    for qid, grid, via, ent, var, words in (("l11", "ERCOT", "grid", "iso:ercot", "battery_operating_mw", "How many MW of battery storage were operating in ERCOT in September 2026?"),
                                            ("l12", "CAISO", "grid", "iso:caiso", "battery_planned_mw", "How many MW of battery storage were planned in CAISO as of September 2026?"),
                                            ("l13", "none", "general", "us:total", "battery_operating_mw", "How many MW of battery storage were operating in the United States in September 2026?"),
                                            ("l14", "ERCOT", "grid", "iso:ercot", "battery_operating_mwh_per_mw", "What was the average duration of ERCOT's operating battery fleet in September 2026, in MWh per MW?")):
        v = month_value(SB, ent, var, "2026-09")
        qs.append(figure(qid, grid, via, words, SB, v, f"{SB}, {ent}, {var}: the 2026-09 row"))
    # a grid's day-ahead average and peak: the month must be whole in the table (its day-ahead hours equal to the hours in the
    # month), as questions_s1114.yaml's keys were checked; October 2026 held 48 of 744 hours at the first asking, so September
    for qid, grid, ent, words in (("l15", "ERCOT", E, "ERCOT's hub average"), ("l16", "SPP", SPPN, "SPP's North hub")):
        month = "2026-09"
        hours, in_month = month_value(CP, ent, "da_hours", month), month_value(CP, ent, "hours_in_month", month)
        if hours != in_month:
            raise SystemExit(f"{CP} {ent} {month}: da_hours {hours} is not the month's {in_month} hours")
        v = month_value(CP, ent, "da_simple_mean", month)
        qs.append(figure(qid, grid, "grid", f"What was the simple average day-ahead price at {words} in September 2026, in USD per MWh?", CP, v,
                         f"{CP}, {ent}, da_simple_mean: the {month} row; checked whole: da_hours = hours_in_month = {int(in_month)}"))
    v = year_value(GP, "grid_peak_vs_capacity:ercot", "capacity_over_peak_pct", 2025)
    # l17 through the general chat: the grids' chats see the tables the rule of docs/grids/grid_tables.json admits, and a table whose
    # entities are <table>:<grid> (grid_peak_vs_capacity:ercot) is not among ERCOT's, so its chat said "not in the warehouse" (02:19 UTC)
    qs.append(figure("l17", "none", "general", "By what percentage did ERCOT's installed capacity exceed its 2025 peak demand, the grid's reserve margin on capacity?", GP, v,
                     f"{GP}, grid_peak_vs_capacity:ercot, capacity_over_peak_pct: the 2025 row (in_live_set review)"))
    v = month_value(NB, E, "dam_all_basis_p50", "2026-10")
    qs.append(figure("l18", "ERCOT", "grid", "What was the median day-ahead basis of ERCOT's nodes to the hub average in October 2026, in USD per MWh?", NB, v,
                     f"{NB}, {E}, dam_all_basis_p50: the 2026-10 row (in_live_set review)"))
    v = year_value(PB, E, "da_year_peak_mean", 2026)
    qs.append(figure("l19", "ERCOT", "grid", "What has the mean day-ahead peak-hours price at ERCOT's hub average been in 2026 so far, in USD per MWh?", PB, v,
                     f"{PB}, {E}, da_year_peak_mean: the 2026 row (the year so far)"))
    # outside the warehouse
    qs.append(refusal("l20", "none", "general", "What was the average monthly rent of a data hall in Northern Virginia in 2026, in USD per kW?",
                      ["not in the warehouse"], "no table of the warehouse holds colocation rents: the answer says so in one sentence and states no figure"))
    if [q["id"] for q in qs] != [f"l{i:02d}" for i in range(1, 21)]:
        raise SystemExit("the twenty ids are not l01 to l20 in order")
    return qs


def yaml_text(qs, at):
    lines = [
        "# Energy Research Warehouse (ERW): 20 questions for Ask a lab's energy team asks, session 2224 (chain 152, the night of 5 November 2026).",
        "# Disclosed PPA prices, the datacenter tracker's MW (both held whole for a license: the hold's words, no figure), MW in each grid's",
        "# interconnection queue (MISO's paused: the pause's words), storage on the grids, a grid's day-ahead average, peak and reserve margin,",
        f"# a node's basis, and one question outside the warehouse. Every expected number was computed before any model call from the live set",
        f"# (Supabase, the catalogue, series and entities views, the anon key, reads only) on {at[:10]} by scripts/ask_eval/lab_questions.py, which",
        "# writes this file; each note names the table, the entity or filter, the variable or column, the period and the aggregation. `via` as in",
        "# questions_s302.yaml (grid: the grid's scoped chat; general: no grid). tolerance: 0.01 under 1,000, 0.5 from 1,000. A refusal key has",
        "# no figure and names the words the answer must carry; hold: true marks a table held whole, whose answer may be a refusal or an answer",
        "# in the hold's words, with no figure either way.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for q in qs:
        lines += [f"- id: {q['id']}", f"  grid: {q['grid']}", f"  via: {q['via']}", f"  question: {json.dumps(q['question'])}",
                  f"  expected: {json.dumps(q['expected'])}", f"  tolerance: {q['tolerance']}", f"  text: {json.dumps(q['text'])}",
                  f"  tables: {json.dumps(q['tables'])}", f"  refuse: {'true' if q['refuse'] else 'false'}", f"  hold: {'true' if q['hold'] else 'false'}",
                  f"  note: {json.dumps(q['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


def main(argv):
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = build()
    if "--check" in argv:
        import yaml
        with open(OUT, encoding="utf-8") as f:
            stored = {q["id"]: q for q in yaml.safe_load(f)["questions"]}
        off = [q["id"] for q in qs if q["id"] not in stored or stored[q["id"]]["expected"] != q["expected"] or stored[q["id"]]["question"] != q["question"]]
        print("keys on disk differ from today's live set: " + ", ".join(off) if off else "keys on disk are today's live set's")
        return 1 if off else 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(yaml_text(qs, at))
    with open(KEYS_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_about": "Session 2224 (chain 152): the keys of questions_s2224.yaml as computed from the live set by scripts/ask_eval/lab_questions.py, not a run.",
                   "computed_at_utc": at, "source": f"{base_url().split('//')[1].split('.')[0]} catalogue, series and entities views, anon key",
                   "keys": {q["id"]: {k: q[k] for k in ("expected", "tolerance", "text", "tables", "refuse", "hold", "note")} for q in qs}}, f, indent=1)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)} and {os.path.relpath(KEYS_JSON, ROOT)}: {len(qs)} questions, keys computed at {at}")
    for q in qs:
        print(f"  {q['id']} {q['expected'] or q['text']}  {q['note'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
