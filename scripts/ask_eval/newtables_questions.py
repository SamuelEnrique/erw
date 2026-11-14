#!/usr/bin/env python3
"""Session 6111 (chain 280): questions for the AI chat over the warehouse drawn from the tables that landed in the week
of 9 November 2026, each expected answer computed from the table by this script, never typed.

Energy Research Warehouse (ERW). No model call of any kind, no request: the tables are read from this machine's own
files through the erw package's local backend (ERW_DATA_DIR, else the repository's warehouse/output, else the main
checkout's beside a worktree), as scripts/sync.py restored them from the archive. The live set does not hold these
tables yet, so the keys cannot be read with a visitor's key as the other sets' are; each key carries the run of the
table it was computed from, and --check says when a table has moved.

    python scripts/ask_eval/newtables_questions.py            computes the keys and writes the two files
    python scripts/ask_eval/newtables_questions.py --check    exit 1 when the YAML on disk differs from a fresh computation

Writes warehouse/chat/eval/questions_newtables.yaml (read by eval_s1113.py, eval_loop.py and eval_site.py with
--set newtables) and warehouse/chat/eval/keys_newtables.json.

The tables (warehouse/metadata/coverage.csv on 14 November 2026 against 8 November):

  utility_large_load_rules          events, 100 rows: one row a large-load connection rule of a US utility or commission
  utility_large_load_rule_changes   events, 94 rows: a filing, order or other change to such a rule, 18 August to 13 November 2026
  state_large_load_laws             events, 27 rows: the states' large-load laws and bills of the 2025 and 2026 sessions
  forecast_tool_parameters          series, 768 rows: the forecast tool's parameters (EIA's capital costs, JEDI's shares, gas defaults)
  deal_counterparties               entities, 532 rows: the parties of the deals table, one row a company
  iso_reserve_margin_reports        series, 5 rows: what CAISO's summer assessment printed of its reserve margin

Two more landed and are not asked about: ferc714_forecast_growth and ferc714_planning_area_forecasts are on no copy this
machine can read (not on Redivis, sync.py's line), and datacenter_tracker_rollups is internal.

Kinds (a question's `kind`; `sector` is the table's short name here, so the scores read by table):

  figure     the table holds the answer: a number (count: true for a count of rows), or a word (the key's text)
  outside    the table does not hold it (a technology, a utility, a state, a period or a quantity it has no row or column
             for): "not in the warehouse", the missing thing named, no figure
  unstated   the table has the row, and its cell says the documents read do not state the thing ("not published"): the
             answer says so in the key's words and gives no figure, as a refusal or as an answer (eval_s1113.py grade_set)

Tolerance 0.01 under 1,000 and 0.5 from 1,000, as the other sets. A text entry with "|" is met by any one of its parts.
"""
import datetime as dt
import json
import os
import re
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
OUT = os.path.join(EVAL, "questions_newtables.yaml")
KEYS_JSON = os.path.join(EVAL, "keys_newtables.json")
TODAY = "2026-11-14"
RULES, CHANGES, LAWS, PARAMS, PARTIES, RESERVE = ("utility_large_load_rules", "utility_large_load_rule_changes", "state_large_load_laws",
                                                 "forecast_tool_parameters", "deal_counterparties", "iso_reserve_margin_reports")
TABLES = (RULES, CHANGES, LAWS, PARAMS, PARTIES, RESERVE)
KINDS = ("figure", "outside", "unstated")
SECTORS = ("rules", "changes", "laws", "forecast", "counterparties", "reserve")
NOT_IN = "not in the warehouse"
_frames = {}


def data_dir():
    """Where the tables' files are: ERW_DATA_DIR, the repository's own warehouse/output, or the main checkout's beside a
    worktree (a worktree holds no warehouse data)."""
    for d in (os.environ.get("ERW_DATA_DIR"), os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, RULES + ".csv")):
            return d
    raise SystemExit(f"{RULES}.csv is on no data folder of this machine: python scripts/sync.py --tables '^{RULES}$' restores it")


def frame(table):
    """A table's rows, as the Python chat's tools read them (erw.fetch on the local backend)."""
    if table not in _frames:
        os.environ["ERW_DATA_DIR"] = data_dir()
        sys.path.insert(0, os.path.join(ROOT, "package", "src"))
        import erw
        erw.set_backend("local")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _frames[table] = erw.fetch(table)
    return _frames[table]


def run_of(table):
    """The run the table's file says it was written by (its header's 'Retrieved:' line), so a key names its vintage."""
    with open(os.path.join(data_dir(), table + ".csv"), encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", line)
            if m:
                return m.group(1)
    return None


def tolerance(x):
    return 0.01 if abs(x) < 1000 else 0.5


def q(qid, sector, kind, question, table, note, expected=(), text=(), count=False, refuse=False):
    exp = [round(float(x), 6) for x in expected]
    return {"id": qid, "sector": sector, "kind": kind, "grid": "none", "via": "general", "question": question, "expected": exp,
            "tolerance": tolerance(exp[0]) if exp else 0.01, "text": list(text), "tables": [table] if kind == "figure" else [],
            "refuse": refuse, "hold": False, "count": count, "note": note}


def one(df, what):
    if len(df) != 1:
        raise SystemExit(f"{what}: {len(df)} rows, one expected")
    return df.iloc[0]


def top(series, what):
    """The value that is alone at the top of a count, and its count; the script stops on a tie (the question would have
    two answers)."""
    c = series.value_counts()
    if len(c) > 1 and c.iloc[0] == c.iloc[1]:
        raise SystemExit(f"{what}: a tie at the top ({c.index[0]}, {c.index[1]})")
    return c.index[0], int(c.iloc[0])


def day_words(day):
    """The ways an answer may write a date: 2026-07-01, 1 July 2026, July 1, 2026."""
    d = dt.date.fromisoformat(str(day)[:10])
    month = d.strftime("%B")
    return f"{d.isoformat()}|{d.day} {month} {d.year}|{month} {d.day}, {d.year}|{month} {d.day} {d.year}"


def param(entity, variable):
    f = frame(PARAMS)
    return float(one(f[(f["entity"] == entity) & (f["variable"] == variable)], f"{PARAMS} {entity} {variable}")["value"])


def build_forecast():
    f = frame(PARAMS)
    eia, jedi, gas = "forecast:eia_capex:{}:{}".format, "forecast:jedi_{}:{}:us".format, "forecast:gas:natural_gas:us"
    out = []
    asked = (("fc01", "utility_pv", "utility-scale solar PV"), ("fc02", "land_based_wind", "land-based wind"),
             ("fc03", "natural_gas", "a natural gas combined-cycle plant"), ("fc04", "geothermal", "geothermal"))
    for qid, tech, words in asked:
        out.append(q(qid, "forecast", "figure", f"In the forecast tool's parameters, what is EIA's overnight capital cost for {words} for the US as a whole, in USD per kW?",
                     PARAMS, f"{PARAMS}, {eia(tech, 'us')}, overnight_cost (USD/kW, 2023 dollars): the one row", [param(eia(tech, "us"), "overnight_cost")]))
    out.append(q("fc05", "forecast", "figure", "In the forecast tool's parameters, what is EIA's overnight capital cost for utility-scale solar PV in Texas, in USD per kW?",
                 PARAMS, f"{PARAMS}, {eia('utility_pv', 'tx')}, overnight_cost: the state's row", [param(eia("utility_pv", "tx"), "overnight_cost")]))
    wind = f[(f["variable"] == "overnight_cost") & (f["x_technology"] == "land_based_wind")]
    hi = wind[wind["value"] == wind["value"].max()]
    place = one(hi, "the dearest place for land-based wind")
    city = place["x_place"].split("_", 1)[1].replace("_", " ")
    out.append(q("fc06", "forecast", "figure", "In the forecast tool's parameters, which place has the highest overnight capital cost for land-based wind, and what is it in USD per kW?",
                 PARAMS, f"{PARAMS}, overnight_cost of x_technology land_based_wind: the maximum over {len(wind)} places ({place['entity']})", [float(place["value"])], text=[city]))
    out.append(q("fc07", "forecast", "figure", "How many months of construction do the forecast tool's parameters give for a natural gas combined-cycle plant?",
                 PARAMS, f"{PARAMS}, {eia('natural_gas', 'us')}, construction_months", [param(eia("natural_gas", "us"), "construction_months")]))
    out.append(q("fc08", "forecast", "figure", "What heat rate do the forecast tool's parameters give for a natural gas plant, in MMBtu per MWh?",
                 PARAMS, f"{PARAMS}, heat_rate (MMBtu/MWh): {gas} and {eia('natural_gas', 'us')} hold the same figure", [param(gas, "heat_rate")]))
    out.append(q("fc09", "forecast", "figure", "What natural gas fuel price do the forecast tool's parameters use by default, in USD per MMBtu?",
                 PARAMS, f"{PARAMS}, {gas}, fuel_price (USD/MMBtu, the mean of 2025)", [param(gas, "fuel_price")]))
    out.append(q("fc10", "forecast", "figure", "In the forecast tool's parameters, what share of a land-based wind project's construction cost is taxable, as JEDI's model has it?",
                 PARAMS, f"{PARAMS}, {jedi('taxable', 'land_based_wind')}, taxable_share (a ratio)", [param(jedi("taxable", "land_based_wind"), "taxable_share")]))
    out.append(q("fc11", "forecast", "figure", "In the forecast tool's parameters, what is JEDI's construction cost for a utility-scale solar PV project for the US, in USD per MW?",
                 PARAMS, f"{PARAMS}, {jedi('costs', 'utility_pv')}, construction_cost (USD/MW, 2010 dollars)", [param(jedi("costs", "utility_pv"), "construction_cost")]))
    out.append(q("fc12", "forecast", "figure", "What operating life do the forecast tool's parameters give a land-based wind plant, in years?",
                 PARAMS, f"{PARAMS}, {eia('land_based_wind', 'us')}, operating_life (year)", [param(eia("land_based_wind", "us"), "operating_life")]))
    out.append(q("fc13", "forecast", "figure", "How large is EIA's reference utility-scale solar PV plant in the forecast tool's parameters, in MW?",
                 PARAMS, f"{PARAMS}, {eia('utility_pv', 'us')}, case_mw", [param(eia("utility_pv", "us"), "case_mw")]))
    out.append(q("fc14", "forecast", "figure", "What capacity factor do the forecast tool's parameters assume for a natural gas plant?",
                 PARAMS, f"{PARAMS}, {gas}, capacity_factor (a ratio)", [param(gas, "capacity_factor")]))
    n = len(f[(f["variable"] == "overnight_cost") & (f["x_technology"] == "utility_pv")])
    out.append(q("fc15", "forecast", "figure", "For how many places do the forecast tool's parameters hold an overnight capital cost of utility-scale solar PV?",
                 PARAMS, f"{PARAMS}, overnight_cost of x_technology utility_pv: the count of rows (the US, states and cities)", [n], count=True))
    techs = sorted(set(f["x_technology"]))
    for qid, words, word in (("fc16", "offshore wind", "offshore"), ("fc17", "a battery storage plant", "battery|storage"), ("fc18", "a nuclear plant", "nuclear")):
        if any(word.split("|")[0] in t for t in techs):
            raise SystemExit(f"{PARAMS} now holds a technology like {word}: {qid} is no refusal")
        out.append(q(qid, "forecast", "outside", f"What overnight capital cost do the forecast tool's parameters hold for {words}, in USD per kW?", PARAMS,
                     f"{PARAMS} holds four technologies ({', '.join(techs)}) and none of this one: {NOT_IN}, the technology named, no figure", text=[NOT_IN, word], refuse=True))
    if any(str(y) >= "2027" for y in f["ts_utc"].astype(str).str[:4]):
        raise SystemExit(f"{PARAMS} now holds a row dated past 2026: fc19 is no refusal")
    out.append(q("fc19", "forecast", "outside", "What will the overnight capital cost of utility-scale solar PV be in 2030, according to the forecast tool's parameters?", PARAMS,
                 f"{PARAMS} holds EIA's cost of the 2025 study in 2023 dollars and no projection of a later year: {NOT_IN}, no figure", text=[NOT_IN, "2030|projection|forecast"], refuse=True))
    return out


def build_rules():
    r = frame(RULES)
    out = [q("ru01", "rules", "figure", "How many large-load connection rules of US utilities does the warehouse's utility large-load rules table hold?", RULES,
             f"{RULES}: the count of rows", [len(r)], count=True)]
    for qid, status in (("ru02", "in effect"), ("ru03", "proposed"), ("ru04", "approved")):
        out.append(q(qid, "rules", "figure", f"How many of the utility large-load rules in the warehouse have the status \"{status}\"?", RULES,
                     f"{RULES}: the count of rows whose status is {status}", [int((r["status"] == status).sum())], count=True))
    out.append(q("ru05", "rules", "figure", "How many of the utility large-load rules in the warehouse are of Texas?", RULES,
                 f"{RULES}: the count of rows whose x_state is TX", [int((r["x_state"] == "TX").sum())], count=True))
    state, n = top(r["x_state"], "the state with the most rules")
    names = {"TX": "Texas"}
    out.append(q("ru06", "rules", "figure", "Which state has the most rules in the warehouse's utility large-load rules table, and how many?", RULES,
                 f"{RULES}: the count by x_state, the highest ({state})", [n], text=[f"{names[state]}|{state}"], count=True))
    denied = one(r[r["status"] == "denied"], "the denied rule")
    out.append(q("ru07", "rules", "figure", "One utility large-load rule in the warehouse has the status \"denied\". Which utility's is it?", RULES,
                 f"{RULES}: the parties of the one row whose status is denied ({denied['x_row_id']})", text=[re.sub(r",? (LLC|Inc\.?)$", "", denied["parties"])]))
    duke = one(r[r["x_row_id"] == "duke-01"], "duke-01")
    out.append(q("ru08", "rules", "figure", "What is the status of Duke Energy Carolinas' large-load rule in the warehouse's utility large-load rules table?", RULES,
                 f"{RULES}: the status of the row of parties {duke['parties']!r} ({duke['x_row_id']})", text=[duke["status"]]))
    puct = one(r[r["x_row_id"] == "texas-01"], "texas-01")
    m = re.match(r"(\d+) MW", puct["x_threshold_mw"])
    if not m:
        raise SystemExit("texas-01's threshold no longer begins with its MW")
    out.append(q("ru09", "rules", "figure", "According to the warehouse's utility large-load rules table, from what size in MW does the Public Utility Commission of Texas's large-load interconnection rule for ERCOT apply?", RULES,
                 f"{RULES}: x_threshold_mw of the row {puct['x_row_id']} ({puct['parties']}), a phrase that begins with the size", [float(m.group(1))]))
    y26 = r[(r["event_date"] >= "2026-01-01") & (r["event_date"] < "2027-01-01")]
    out.append(q("ru10", "rules", "figure", "How many of the utility large-load rules in the warehouse are dated in 2026 (by the table's event date)?", RULES,
                 f"{RULES}: the count of rows whose event_date is in 2026", [len(y26)], count=True))
    if duke["x_queue_size"] != "not published":
        raise SystemExit("duke-01's queue size is now published: ru11 is a figure's")
    out.append(q("ru11", "rules", "unstated", "According to the warehouse's utility large-load rules table, how many MW are in Duke Energy Carolinas' large-load queue?", RULES,
                 f"{RULES}: x_queue_size of {duke['x_row_id']} is 'not published' (the documents read do not state it): the answer says so and gives no figure",
                 text=["not published|not state|not stated|no figure|not in the warehouse"]))
    for qid, who, word in (("ru12", "Indiana Michigan Power", "Indiana Michigan"), ("ru13", "Hawaiian Electric", "Hawaiian")):
        if r["parties"].str.contains(word, case=False).any():
            raise SystemExit(f"{RULES} now holds a row of {who}: {qid} is no refusal")
        out.append(q(qid, "rules", "outside", f"What minimum contract term does {who}'s large-load rule set, according to the warehouse's utility large-load rules table?", RULES,
                     f"{RULES} holds no row of {who}: {NOT_IN}, the utility named, no figure", text=[NOT_IN, word], refuse=True))
    if r["mw"].notna().any() and (r["mw"].astype(str).str.strip() != "").any() and r["mw"].astype(str).str.strip().replace("nan", "").ne("").any():
        raise SystemExit(f"{RULES} now holds a number in mw: ru14 is a figure's")
    out.append(q("ru14", "rules", "outside", "What is the average size threshold in MW across the utility large-load rules in the warehouse?", RULES,
                 f"{RULES} holds each threshold as the phrase its document prints (x_threshold_mw) and no number (mw is empty): no average can be read from it; {NOT_IN}, no figure",
                 text=[NOT_IN], refuse=True))
    return out


def build_changes():
    c = frame(CHANGES)
    out = [q("ch01", "changes", "figure", "How many changes to utilities' large-load rules does the warehouse's rule changes table hold?", CHANGES,
             f"{CHANGES}: the count of rows", [len(c)], count=True)]
    octo = c[(c["event_date"] >= "2026-10-01") & (c["event_date"] < "2026-11-01")]
    out.append(q("ch02", "changes", "figure", "How many changes to utilities' large-load rules does the warehouse hold for October 2026?", CHANGES,
                 f"{CHANGES}: the count of rows whose event_date is in October 2026", [len(octo)], count=True))
    for qid, status in (("ch03", "order issued"), ("ch04", "suspended"), ("ch05", "filed")):
        out.append(q(qid, "changes", "figure", f"How many of the changes to utilities' large-load rules in the warehouse are of the kind \"{status}\"?", CHANGES,
                     f"{CHANGES}: the count of rows whose status is {status}", [int((c["status"] == status).sum())], count=True))
    state, n = top(c["x_state"], "the state with the most changes")
    names = {"PA": "Pennsylvania"}
    out.append(q("ch06", "changes", "figure", "Which state has the most changes in the warehouse's table of changes to utilities' large-load rules, and how many?", CHANGES,
                 f"{CHANGES}: the count by x_state, the highest ({state})", [n], text=[f"{names[state]}|{state}"], count=True))
    out.append(q("ch07", "changes", "figure", "What is the date of the newest change in the warehouse's table of changes to utilities' large-load rules?", CHANGES,
                 f"{CHANGES}: the latest event_date", text=[day_words(c["event_date"].max())]))
    out.append(q("ch08", "changes", "figure", "How many of the changes to utilities' large-load rules in the warehouse are marked as affecting a new rule (\"new\")?", CHANGES,
                 f"{CHANGES}: the count of rows whose x_affects is new", [int((c["x_affects"] == "new").sum())], count=True))
    first = c["event_date"].min()
    if str(first)[:7] < "2026-08":
        raise SystemExit(f"{CHANGES} now reaches back before August 2026: ch09 is no refusal")
    out.append(q("ch09", "changes", "outside", "How many changes to utilities' large-load rules does the warehouse hold for March 2026?", CHANGES,
                 f"{CHANGES} begins on {str(first)[:10]} (the pass read 15 August to 13 November 2026) and holds no row of March 2026: {NOT_IN}, the period named, no figure given as March's",
                 text=[NOT_IN, "March|August"], refuse=True))
    out.append(q("ch10", "changes", "outside", "How many MW of load were affected by the changes to utilities' large-load rules of October 2026, according to the warehouse?", CHANGES,
                 f"{CHANGES} holds no MW of any change (mw is empty; sizes are phrases): {NOT_IN}, no figure", text=[NOT_IN], refuse=True))
    return out


def build_laws():
    l = frame(LAWS)
    out = [q("lw01", "laws", "figure", "How many state large-load laws and bills does the warehouse's state large-load laws table hold?", LAWS,
             f"{LAWS}: the count of rows", [len(l)], count=True)]
    for qid, status in (("lw02", "in effect"), ("lw03", "enacted"), ("lw04", "introduced")):
        out.append(q(qid, "laws", "figure", f"How many of the state large-load laws and bills in the warehouse have the status \"{status}\"?", LAWS,
                     f"{LAWS}: the count of rows whose status is {status}", [int((l["status"] == status).sum())], count=True))
    veto = one(l[l["status"] == "vetoed"], "the vetoed bill")
    names = {"VT": "Vermont"}
    out.append(q("lw05", "laws", "figure", "Which state's large-load bill was vetoed, according to the warehouse's state large-load laws table?", LAWS,
                 f"{LAWS}: x_state of the one row whose status is vetoed ({veto['x_bill']})", text=[f"{names[veto['x_state']]}|{veto['x_state']}"]))
    out.append(q("lw06", "laws", "figure", "How many large-load laws or bills of Missouri does the warehouse's state large-load laws table hold?", LAWS,
                 f"{LAWS}: the count of rows whose x_state is MO", [int((l["x_state"] == "MO").sum())], count=True))
    nj = one(l[l["x_state"] == "NJ"], "New Jersey's row")
    out.append(q("lw07", "laws", "figure", "What is the status of New Jersey's large-load law in the warehouse's state large-load laws table?", LAWS,
                 f"{LAWS}: the status of the one row whose x_state is NJ ({nj['x_bill']})", text=[nj["status"]]))
    idaho = one(l[l["x_state"] == "ID"], "Idaho's row")
    out.append(q("lw08", "laws", "figure", "When does Idaho's large-load law take effect, according to the warehouse's state large-load laws table?", LAWS,
                 f"{LAWS}: x_effective_date of the one row whose x_state is ID ({idaho['x_bill']})", text=[day_words(idaho["x_effective_date"])]))
    iowa = one(l[l["x_state"] == "IA"], "Iowa's row")
    if iowa["x_effective_date"] != "not published":
        raise SystemExit("Iowa's effective date is now published: lw09 is a figure's")
    out.append(q("lw09", "laws", "unstated", "When does Iowa's large-load bill take effect, according to the warehouse's state large-load laws table?", LAWS,
                 f"{LAWS}: x_effective_date of Iowa's row ({iowa['x_bill']}, introduced) is 'not published': the answer says so and gives no date",
                 text=["not published|not state|not stated|no effective date|not in the warehouse"]))
    for qid, state, code in (("lw10", "Texas", "TX"), ("lw11", "California", "CA")):
        if (l["x_state"] == code).any():
            raise SystemExit(f"{LAWS} now holds a row of {state}: {qid} is no refusal")
        out.append(q(qid, "laws", "outside", f"What is the status of {state}'s large-load law, according to the warehouse's state large-load laws table?", LAWS,
                     f"{LAWS} holds no row of {state}: {NOT_IN}, the state named, no status", text=[NOT_IN, state], refuse=True))
    return out


def build_other():
    p, s = frame(PARTIES), frame(RESERVE)
    out = [q("cp01", "counterparties", "figure", "How many companies does the warehouse's deal counterparties table hold?", PARTIES,
             f"{PARTIES}: the count of rows", [len(p)], count=True)]

    def reserve(variable):
        return float(one(s[s["variable"] == variable], f"{RESERVE} {variable}")["value"])
    out.append(q("rs01", "reserve", "figure", "What planning reserve margin did CAISO's 2026 summer assessment say was achieved, in percent, according to the warehouse's reserve margin reports?", RESERVE,
                 f"{RESERVE}, variable prm_achieved_pct: the one row (CAISO, 2026 Summer Loads and Resources Assessment)", [reserve("prm_achieved_pct")]))
    out.append(q("rs02", "reserve", "figure", "What capacity surplus in MW did CAISO's 2026 summer assessment report, according to the warehouse's reserve margin reports?", RESERVE,
                 f"{RESERVE}, variable capacity_surplus_mw: the one row", [reserve("capacity_surplus_mw")]))
    if s["x_grid"].astype(str).str.contains("ERCOT").any():
        raise SystemExit(f"{RESERVE} now holds a row of ERCOT: rs03 is no refusal")
    out.append(q("rs03", "reserve", "outside", "What planning reserve margin did ERCOT's 2026 summer assessment report, according to the warehouse's reserve margin reports?", RESERVE,
                 f"{RESERVE} holds CAISO's assessment alone: {NOT_IN}, ERCOT named, no figure", text=[NOT_IN, "ERCOT"], refuse=True))
    return out


def build():
    qs = build_forecast() + build_rules() + build_changes() + build_laws() + build_other()
    ids = [x["id"] for x in qs]
    if len(set(ids)) != len(ids):
        raise SystemExit("an id twice")
    return qs


FIELDS = ("expected", "tolerance", "text", "tables", "refuse", "hold", "count", "sector", "kind", "note")


def yaml_text(qs, at, runs):
    n = {k: sum(1 for x in qs if x["kind"] == k) for k in KINDS}
    lines = [
        f"# Energy Research Warehouse (ERW): {len(qs)} questions for the AI chat over the warehouse on the tables that landed in the week of",
        "# 9 November 2026 (session 6111, chain 280): the utilities' large-load rules, their changes, the states' laws, the forecast tool's",
        "# parameters, the deals' counterparties and the reserve margin reports.",
        f"# {n['figure']} have an answer in the table (kind figure: a number, a count or a word); {n['outside']} ask of something the table has no row or",
        f"# column for (outside: \"not in the warehouse\", the missing thing named, no figure); {n['unstated']} of a cell that says the documents read do",
        "# not state the thing (unstated: the answer says so and gives no figure).",
        f"# Every expected answer was computed before any model call from the table's own file on this machine, as restored from the archive, on {at[:10]} by",
        "# scripts/ask_eval/newtables_questions.py, which writes this file; each note names the table, the row or filter and the column.",
        "# The tables' runs: " + "; ".join(f"{t} {r}" for t, r in runs.items()) + ".",
        "# tolerance: 0.01 under 1,000, 0.5 from 1,000. A text entry with \"|\" is met by any one of its parts; count: true asks the figure apart from a clock time.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for x in qs:
        lines += [f"- id: {x['id']}", f"  sector: {x['sector']}", f"  kind: {x['kind']}", f"  grid: {x['grid']}", f"  via: {x['via']}",
                  f"  question: {json.dumps(x['question'])}", f"  expected: {json.dumps(x['expected'])}", f"  tolerance: {x['tolerance']}",
                  f"  text: {json.dumps(x['text'])}", f"  tables: {json.dumps(x['tables'])}", f"  refuse: {'true' if x['refuse'] else 'false'}",
                  f"  hold: {'true' if x['hold'] else 'false'}", f"  count: {'true' if x['count'] else 'false'}", f"  note: {json.dumps(x['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


LIVE_OUT = os.path.join(EVAL, "questions_newtables_live.yaml")
OUT_OF_REACH = "not in the warehouse|license needed|live set|Redivis|not loaded"
STATUS_WORDS = ("proposed", "in effect", "approved", "ordered", "denied", "enacted", "introduced", "passed", "vetoed", "died")


def visitor_reads():
    """{table: whether a visitor's chat can read it today}: the live catalogue's in_live_set (yes, or review), read with
    the anon key through lab_questions.py's reader. A table the catalogue does not list is not read."""
    sys.path.insert(0, HERE)
    import lab_questions as L
    cat = L.catalogue()
    return {t: (cat.get(t) or {}).get("in_live_set") in ("yes", "review") for t in TABLES}


def live(qs, reads):
    """The set as a visitor's chat can answer it today. A question of a table the chat cannot read (kinds figure and
    unstated) becomes one of kind not_readable: a refusal in the words of a table out of reach, no figure, and never the
    figure the table holds (kept as `withheld`, for the grader alone). A question of kind outside becomes one too, with
    nothing withheld. A question of a table the chat can read keeps its key."""
    out = []
    for x in qs:
        table = (x["tables"] or [None])[0] or x["note"].split(":")[0].split(",")[0].split(" ")[0]
        if reads.get(table):
            out.append(dict(x, withheld=[], withheld_text=[]))
            continue
        if x["kind"] == "outside":
            # session 6141: a question of something the table does not hold either way is, for a chat that cannot read the
            # table, a question of a table out of its reach like any other: it cannot know the table's span or its rows, so
            # the key asks for the refusal and no figure, not for the words of the readable case (ch09, asked through the
            # site's loop on 14 November 2026, refused rightly and was graded wrong for not naming the month)
            out.append(dict(x, kind="not_readable", text=[OUT_OF_REACH], withheld=[], withheld_text=[],
                            note=f"a visitor's chat cannot read {table} today: a refusal and no figure. When it can: " + x["note"]))
            continue
        out.append(dict(x, kind="not_readable", expected=[], text=[OUT_OF_REACH], tables=[], refuse=True, count=False,
                        # a word key is withheld when it is a name or a date; a status word (proposed, in effect) may stand in a
                        # refusal that leaks nothing, so it is not looked for
                        withheld=x["expected"], withheld_text=[t for t in x["text"] if t not in STATUS_WORDS] if x["kind"] == "figure" and not x["expected"] else [],
                        note=f"a visitor's chat cannot read {table} today (not in the live set): a refusal, no figure, never the table's own. When it can: " + x["note"]))
    return out


def live_yaml(qs, at, reads):
    n = {k: sum(1 for x in qs if x["kind"] == k) for k in KINDS + ("not_readable",)}
    lines = [
        f"# Energy Research Warehouse (ERW): the {len(qs)} questions of questions_newtables.yaml keyed as a visitor's chat can answer them on {at[:10]}",
        "# (session 6111, chain 280), written by scripts/ask_eval/newtables_questions.py --live. A visitor's chat reads the live set; the tables read today: "
        + (", ".join(t for t, r in reads.items() if r) or "none of the six") + ".",
        f"# {n['not_readable']} ask of a table out of its reach (kind not_readable: a refusal in one of the text entry's words, no figure, and never the figure",
        f"# the table holds, kept under withheld for the grader); {n['outside']} of something the table does not hold either way (outside); {n['figure'] + n['unstated']} keep their key.",
        f"today: '{TODAY}'",
        "questions:",
    ]
    for x in qs:
        lines += [f"- id: {x['id']}", f"  sector: {x['sector']}", f"  kind: {x['kind']}", f"  grid: {x['grid']}", f"  via: {x['via']}",
                  f"  question: {json.dumps(x['question'])}", f"  expected: {json.dumps(x['expected'])}", f"  tolerance: {x['tolerance']}",
                  f"  text: {json.dumps(x['text'])}", f"  tables: {json.dumps(x['tables'])}", f"  refuse: {'true' if x['refuse'] else 'false'}",
                  f"  hold: {'true' if x['hold'] else 'false'}", f"  count: {'true' if x['count'] else 'false'}",
                  f"  withheld: {json.dumps(x['withheld'])}", f"  withheld_text: {json.dumps(x['withheld_text'])}", f"  note: {json.dumps(x['note'])}"]
    text = "\n".join(lines) + "\n"
    if chr(0x2014) in text or chr(0x2013) in text:
        raise SystemExit("a dash in the output")
    return text


def main(argv):
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = build()
    runs = {t: run_of(t) for t in TABLES}
    if "--live" in argv:
        reads = visitor_reads()
        with open(LIVE_OUT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(live_yaml(live(qs, reads), at, reads))
        print(f"wrote {os.path.relpath(LIVE_OUT, ROOT)}: a visitor's chat reads {sum(reads.values())} of the {len(reads)} tables today ({reads})")
        return 0
    if "--check" in argv:
        import yaml
        with open(OUT, encoding="utf-8") as fh:
            stored = {x["id"]: x for x in yaml.safe_load(fh)["questions"]}
        off = [x["id"] for x in qs if x["id"] not in stored or stored[x["id"]]["expected"] != x["expected"] or stored[x["id"]]["question"] != x["question"]
               or stored[x["id"]]["text"] != x["text"]]
        off += [i for i in stored if i not in {x["id"] for x in qs}]
        print("keys on disk differ from the tables on this machine: " + ", ".join(off) if off else "keys on disk are the tables' on this machine")
        return 1 if off else 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml_text(qs, at, runs))
    with open(KEYS_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"_about": "Session 6111: the keys of questions_newtables.yaml as computed from the tables' own files by scripts/ask_eval/newtables_questions.py, not a run.",
                   "computed_at_utc": at, "source": "the tables' files on this machine (the erw package's local backend), restored from the archive by scripts/sync.py",
                   "table_runs": runs, "keys": {x["id"]: {k: x[k] for k in FIELDS} for x in qs}}, fh, indent=1)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)} and {os.path.relpath(KEYS_JSON, ROOT)}: {len(qs)} questions, keys computed at {at}")
    print("by sector:", {s: sum(1 for x in qs if x["sector"] == s) for s in SECTORS})
    print("by kind:", {k: sum(1 for x in qs if x["kind"] == k) for k in KINDS})
    for x in qs:
        print(f"  {x['id']} {x['kind']:8} {x['expected'] or x['text']}  {x['note'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
