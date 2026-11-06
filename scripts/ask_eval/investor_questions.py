#!/usr/bin/env python3
"""Session 3281 (the Ask evaluation chain of 6 November 2026, queue/done/199): twenty questions an energy investor asks of
Ask the warehouse, each expected answer computed from the live set by this script, never typed.

Energy Research Warehouse (ERW). No model call of any kind. Reads only: the live set's `catalogue`, `series`, `entities`
and `events` views (Supabase REST, the anon key from the repository's .env, or the main checkout's beside a worktree), 1,000
rows a page, through lab_questions.py's reader (session 2224). Writes warehouse/chat/eval/questions_investor.yaml (the set,
read by eval_s1113.py and eval_loop.py with --set investor) and warehouse/chat/eval/keys_investor.json.

    python scripts/ask_eval/investor_questions.py            computes the keys and writes both files
    python scripts/ask_eval/investor_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation

The twenty, by what an investor asks (the chain's prompt):
  - disclosed PPA prices by technology and year and their median, and a counterparty's deals and MW: energy_deals, held whole
    for a license since 21 October 2026, so the expected answer is the hold's words and no figure;
  - a datacenter operator's MW by grid: datacenter_facilities and datacenter_projects, held whole the same way; beside them the
    public large-load statements (large_load_public), the one public table of large loads by grid;
  - a grid's queue MW by status and fuel: the ISOs' own queue tables (entities, the ISO's fuel_technology) and Berkeley Lab's
    Queued Up (lbnl_interconnection_queue, its region and type_clean); NYISO's queue is held for a license (by grid);
  - the months to in-service by grid: interconnection_durations_summary (Berkeley Lab's completed projects, by the year they
    reached operation);
  - a reactor's outage days and the EIA-860M pipeline's MW that slipped a year by grid: the tables that hold them
    (eia_nuclear_outages_*, nuclear_fleet_status, generator_pipeline_by_grid) are on main but not in the live set Ask reads
    (the catalogue of 6 November 2026), so the expected answer is "not in the warehouse" in its first sentence and no figure;
    the run stops when one of them reaches the live set, so its key is written as a figure then;
  - one question outside the warehouse, answered "not in the warehouse" in one sentence (its first).

A key with `first: true` is met only when its text is in the answer's first sentence (eval_s1113.py grade_set).
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_questions as L  # noqa: E402  the reader, the hold and the key shapes of session 2224

ROOT = L.ROOT
EVAL = L.EVAL
OUT = os.path.join(EVAL, "questions_investor.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_investor.json")
TODAY = "2026-11-06"
DUR, LBNL, LL = "interconnection_durations_summary", "lbnl_interconnection_queue", "large_load_public"
NOT_LIVE = {"reactor": ("eia_nuclear_outages_daily", "eia_nuclear_outages_facility_daily", "eia_nuclear_outages_generator_daily", "nuclear_fleet_status"),
            "slip": ("generator_pipeline_by_grid", "eia860m_planned_generators")}
NIW = "not in the warehouse"


def entity_rows(table, select="capacity_mw,status,extra"):
    return L.get("entities", table_name=f"eq.{table}", select=select)


def queue_sum(table, status, field, values):
    """The sum of capacity_mw over one status and a set of values of one column of a queue table (the column in the
    entities view's extra), with the count of rows."""
    rows = [r for r in entity_rows(table) if r["status"] == status and (r.get("extra") or {}).get(field) in values]
    vals = [float(r["capacity_mw"]) for r in rows if r.get("capacity_mw") not in (None, "")]
    if not vals:
        raise SystemExit(f"{table} status {status} {field} {values}: no rows")
    return round(sum(vals), 4), len(rows), len(vals)


def year_row(table, entity, variable, year):
    return L.year_value(table, entity, variable, year)


def figure(qid, grid, via, question, table, values, note, text=()):
    q = L.figure(qid, grid, via, question, table, values[0], note, text)
    q["expected"] = [round(v, 4) for v in values]
    q["tolerance"] = max(L.tolerance(v) for v in values)
    return q


def build():
    cat = L.catalogue()
    for t in ("energy_deals", "datacenter_facilities", "datacenter_projects", "ercot_interconnection_queue", "caiso_interconnection_queue",
              "spp_interconnection_queue", "nyiso_interconnection_queue", DUR, LBNL, LL):
        if t not in cat or cat[t]["in_live_set"] not in ("yes", "review"):
            raise SystemExit(f"{t} is not in the live set's catalogue as yes or review")
    for kind, tables in NOT_LIVE.items():
        live = [t for t in tables if t in cat and cat[t]["in_live_set"] in ("yes", "review")]
        if live:
            raise SystemExit(f"{', '.join(live)} reached the live set: the {kind} question wants a figure key now")
    for t in ("energy_deals", "datacenter_facilities", "datacenter_projects"):
        if not L.held(t):
            raise SystemExit(f"{t} is no longer held whole: its questions want figure keys")
    qs = []
    lic = [L.LICENSE]
    # PPA prices and a counterparty's deals: energy_deals, held whole
    qs.append(L.refusal("iv01", "none", "general", "What was the median disclosed price of the wind power purchase agreements signed in 2025, in USD per MWh?", lic,
                        "energy_deals (price_value, technology wind, 2025, the median) is held whole for a license: the hold's words and no figure", hold=True, tables=["energy_deals"]))
    qs.append(L.refusal("iv02", "none", "general", "Across all technologies, what was the median disclosed power purchase agreement price in 2026, and how many deals disclosed a price?", lic,
                        "energy_deals (price_value, 2026, the median and the count) is held whole for a license: the hold's words and no figure", hold=True, tables=["energy_deals"]))
    qs.append(L.refusal("iv03", "none", "general", "How many power deals has Meta signed since the start of 2025, and for how many MW in total?", lic,
                        "energy_deals (buyer Meta, since 2025-01-01, the count and the sum of mw) is held whole for a license: the hold's words and no figure", hold=True, tables=["energy_deals"]))
    # a datacenter operator's MW by grid: the tracker, held whole
    qs.append(L.refusal("iv04", "none", "general", "How many MW of datacenter facilities does Microsoft operate in ERCOT, according to the datacenter tracker?", lic,
                        "datacenter_facilities (operator Microsoft, ERCOT, mw) is held whole for a license: the hold's words and no figure", hold=True, tables=["datacenter_facilities"]))
    qs.append(L.refusal("iv05", "none", "general", "Which datacenter developer has the most MW of projects in PJM in the datacenter tracker, and how many MW?", lic,
                        "datacenter_projects (developer, PJM, mw) is held whole for a license: the hold's words and no figure", hold=True, tables=["datacenter_projects"]))
    # the public large-load statements: the largest MW figure stated for ERCOT's grid
    rows = [r for r in L.get("events", table_name=f"eq.{LL}", select="mw,extra") if (r.get("extra") or {}).get("grid") == "ercot"
            and (r.get("extra") or {}).get("row_kind") == "mw" and r.get("mw") not in (None, "")]
    if not rows:
        raise SystemExit(f"{LL}: no ercot mw rows")
    v = max(float(r["mw"]) for r in rows)
    qs.append(figure("iv06", "none", "general", "What is the largest large-load figure, in MW, among the public large-load statements the warehouse holds for ERCOT's grid?", LL, [v],
                     f"{LL}: the maximum of mw over the {len(rows)} rows with grid ercot and row_kind mw (events)"))
    # a grid's queue MW by status and fuel: the ISOs' own tables
    for qid, grid, table, status, field, values, words in (
            ("iv07", "ERCOT", "ercot_interconnection_queue", "active", "fuel_technology", ("Solar - Photovoltaic Solar",), "solar photovoltaic"),
            ("iv08", "ERCOT", "ercot_interconnection_queue", "active", "fuel_technology", ("Other - Battery Energy Storage",), "battery storage"),
            ("iv09", "CAISO", "caiso_interconnection_queue", "active", "fuel_technology", ("Storage",), "standalone storage (fuel technology Storage)"),
            ("iv10", "SPP", "spp_interconnection_queue", "active", "fuel_technology", ("Wind",), "wind (fuel technology Wind)"),
            ("iv11", "ERCOT", "ercot_interconnection_queue", "completed", "fuel_technology", ("Gas - Combined-Cycle",), "gas combined-cycle")):
        mw, n, nv = queue_sum(table, status, field, values)
        qs.append(figure(qid, grid, "grid", f"How many MW of {words} are {status} in {grid}'s interconnection queue, summed over the requests?", table, [mw],
                         f"{table}: the sum of capacity_mw over the {n} rows with status {status} and {field} {' or '.join(values)} (the snapshot of {cat[table]['ts_max'][:10]})"))
    # Berkeley Lab's Queued Up: active solar in PJM
    rows =[r for r in entity_rows(LBNL) if r["status"] == "active" and (r.get("extra") or {}).get("region") == "PJM" and (r.get("extra") or {}).get("type_clean") == "Solar"]
    vals = [float(r["capacity_mw"]) for r in rows if r.get("capacity_mw") not in (None, "")]
    qs.append(figure("iv12", "none", "general", "In Berkeley Lab's Queued Up data, how many MW of solar-only requests were active in PJM's queue at the end of 2025?", LBNL, [round(sum(vals), 4)],
                     f"{LBNL}: the sum of capacity_mw over the {len(rows)} rows with status active, region PJM and type_clean Solar (the 2026 edition, requests through 2025)"))
    # the months to in-service by grid: Berkeley Lab's completed projects, by the year they reached operation
    for qid, ent, grid, var, year, words in (
            ("iv13", "lbnl_durations:ercot", "ERCOT", "median_months", 2025, "What was the median time from interconnection request to commercial operation for ERCOT projects that reached operation in 2025, in months?"),
            ("iv14", "lbnl_durations:caiso", "CAISO", "median_months", 2024, "What was the median time from interconnection request to commercial operation for CAISO projects that reached operation in 2024, in months?"),
            ("iv15", "lbnl_durations:pjm", "PJM", "median_months_5y", 2025, "Over the five years to 2025, what was the median time from interconnection request to commercial operation for PJM projects, in months?")):
        v = year_row(DUR, ent, var, year)
        qs.append(figure(qid, "none", "general", words, DUR, [v], f"{DUR}, {ent}, {var}: the {year} row (Berkeley Lab's completed projects, Queued Up 2026 edition)"))
    p = year_row(DUR, "lbnl_durations:spp", "projects", 2025)
    mw = year_row(DUR, "lbnl_durations:spp", "mw", 2025)
    qs.append(figure("iv16", "none", "general", "How many projects in SPP reached commercial operation in 2025 according to Berkeley Lab's interconnection durations, and how many MW were they?", DUR, [p, mw],
                     f"{DUR}, lbnl_durations:spp, projects and mw: the 2025 rows"))
    # a reactor's outage days and the EIA-860M slip: not in the live set
    qs.append(L.refusal("iv17", "none", "general", "How many days was Diablo Canyon unit 2 in a refueling or forced outage in 2025?", [NIW],
                        f"the outage tables ({', '.join(NOT_LIVE['reactor'])}) are on main but not in the live set Ask reads (catalogue of {TODAY}): "
                        "'not in the warehouse' in the first sentence and no figure"))
    qs[-1]["first"] = True
    qs.append(L.refusal("iv18", "none", "general", "How many MW of planned generators in ERCOT had their planned operating year pushed back by a year or more between EIA-860M's August and September 2026 editions?", [NIW],
                        f"the slip by grid is generator_pipeline_by_grid's (slipped_mw), on main but not in the live set Ask reads, nor is eia860m_planned_generators (catalogue of {TODAY}): "
                        "'not in the warehouse' in the first sentence and no figure"))
    qs[-1]["first"] = True
    # NYISO's queue: NYISO's own, held for a license (by grid)
    if not L.held("nyiso_interconnection_queue", "NYISO"):
        raise SystemExit("nyiso_interconnection_queue is no longer held for NYISO: iv19 wants a figure key")
    qs.append(L.refusal("iv19", "NYISO", "grid", "How many MW of offshore wind are active in NYISO's interconnection queue?", ["NYISO", L.LICENSE],
                        "nyiso_interconnection_queue is NYISO's own and held for a license (site/data/license_status.json): NYISO named, the hold's words, no figure", hold=True,
                        tables=["nyiso_interconnection_queue"]))
    # outside the warehouse
    qs.append(L.refusal("iv20", "none", "general", "What after-tax internal rate of return do utility-scale solar projects in Texas earn in 2026?", [NIW],
                        "no table of the warehouse holds project returns: the answer says so in its first sentence and states no figure"))
    qs[-1]["first"] = True
    for q in qs:
        q.setdefault("first", False)
    if [q["id"] for q in qs] != [f"iv{i:02d}" for i in range(1, 21)]:
        raise SystemExit("the twenty ids are not iv01 to iv20 in order")
    return qs


def yaml_text(qs, at):
    lines = [
        "# Energy Research Warehouse (ERW): 20 questions for Ask an energy investor asks, session 3281 (the Ask evaluation chain of 6 November 2026).",
        "# Disclosed PPA prices and a counterparty's deals (energy_deals) and a datacenter operator's MW (the tracker), all held whole for a license:",
        "# the hold's words, no figure; the public large-load statements; a grid's queue MW by status and fuel (the ISOs' own tables, Berkeley Lab's",
        "# Queued Up; NYISO's held); the months to in-service by grid; a reactor's outage days and the EIA-860M slip by grid, whose tables are not in",
        "# the live set Ask reads (\"not in the warehouse\" first); and one question outside the warehouse. Every expected number was computed before",
        f"# any model call from the live set (Supabase, the catalogue, series, entities and events views, the anon key, reads only) on {at[:10]} by",
        "# scripts/ask_eval/investor_questions.py, which writes this file; each note names the table, the filter, the column or variable, the",
        "# period and the aggregation. tolerance: 0.01 under 1,000, 0.5 from 1,000. A refusal key has no figure; hold: true marks a held table;",
        "# first: true asks the text in the answer's first sentence.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for q in qs:
        lines += [f"- id: {q['id']}", f"  grid: {q['grid']}", f"  via: {q['via']}", f"  question: {json.dumps(q['question'])}",
                  f"  expected: {json.dumps(q['expected'])}", f"  tolerance: {q['tolerance']}", f"  text: {json.dumps(q['text'])}",
                  f"  tables: {json.dumps(q['tables'])}", f"  refuse: {'true' if q['refuse'] else 'false'}", f"  hold: {'true' if q['hold'] else 'false'}",
                  f"  first: {'true' if q['first'] else 'false'}", f"  note: {json.dumps(q['note'])}"]
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
        json.dump({"_about": "Session 3281: the keys of questions_investor.yaml as computed from the live set by scripts/ask_eval/investor_questions.py, not a run.",
                   "computed_at_utc": at, "source": f"{L.base_url().split('//')[1].split('.')[0]} catalogue, series, entities and events views, anon key",
                   "keys": {q["id"]: {k: q[k] for k in ("expected", "tolerance", "text", "tables", "refuse", "hold", "first", "note")} for q in qs}}, f, indent=1)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)} and {os.path.relpath(KEYS_JSON, ROOT)}: {len(qs)} questions, keys computed at {at}")
    for q in qs:
        print(f"  {q['id']} {q['expected'] or q['text']}  {q['note'][:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
