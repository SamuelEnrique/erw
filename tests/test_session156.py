"""Session 156: Ask ERCOT, to ready.

Energy Research Warehouse (ERW). What sessions 148 and 153 left open, closed in phase 1 with no model call:

  - three things the query does in one call (site/lib/chat/forms.ts, site/lib/chat/tools.ts): the average day by hour
    (24 values as one series), a date column grouped by year, the newest day held; and a series asked for by its
    entity alone;
  - the two switches of session 148 on by default (site/lib/chat/switches.ts), each still turned off by the server;
  - the owner's ruling on two sources for one figure, the sentence on Texas's curtailment share, and the closing
    words of a refusal about another grid (site/lib/chat/ready.ts).

What is held here, with no model call and no request:

  - the reads recorded from the site's database (tests/fixtures/session156/form_reads.json) are worked again in this
    file, in another language than the tool's, and give the tool's own results;
  - where the warehouse's tables are on the machine (ERW_TABLES, else this copy's warehouse/output), the two figures of
    the year's highest hourly demand are set against their tables: which is the operator's own and which is derived.
    Where the tables are not, those tests are skipped;
  - the default of the two switches lives in one place; the exported specs, the shared reader, the menu, the ceilings
    and the three open pages are not this session's;
  - the Method note says what was added;
  - the session's own tests in node (site/scripts/test-ask-ready.mjs), where node and the site's packages are.

Nothing here changes the environment at import, and nothing compares this branch with another.

    python -m unittest tests.test_session156 -v
"""

import collections
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import unittest
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DASH = chr(0x2014)
CENTRAL = ZoneInfo("America/Chicago")
CLOSE = "Ask ERCOT answers for[^.]{0,200}four pages"
NEVER = "(speaks|answers) for ERCOT only"
OTHER_GRID = ["r01", "r02", "r03", "r04", "r05", "r06", "r16", "r19", "r22", "r23", "r25"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def tables_dir():
    """Where the warehouse's tables are on this machine: ERW_TABLES, else this copy's warehouse/output."""
    return os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")


def table_rows(name):
    """A table's rows, or None when the table is not on this machine."""
    path = os.path.join(tables_dir(), f"{name}.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def fixture():
    return json.loads(src("tests", "fixtures", "session156", "form_reads.json"))


def call(fx, name):
    """A recorded call's result, and the rows of the table reads recorded for a read whose request holds every one of `has`."""
    i = next(k for k, c in enumerate(fx["calls"]) if c["id"] == name)
    return fx["calls"][i]["input"], fx["results"][i]["out"]


def read_of(fx, table, *has):
    """The one recorded read of a table whose request holds every one of the words."""
    found = []
    for url, rows in fx["reads"].items():
        q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        text = json.dumps(q)
        if q.get("table_name") == f"eq.{table}" and all(w in text for w in has):
            found.append((q, rows))
    assert len(found) == 1, (table, has, len(found))
    return found[0]


def instant(t):
    return dt.datetime.fromisoformat(t.replace("Z", "+00:00"))


class TheRecordedReads(unittest.TestCase):
    def test_the_fixture_holds_real_rows_of_the_sites_database_and_no_address_of_it(self):
        fx = fixture()
        self.assertEqual(len(fx["calls"]), 17)
        self.assertEqual(len(fx["results"]), 17)
        text = json.dumps(fx)
        self.assertNotIn("supabase.co", text)
        self.assertIsNone(re.search(r"eyJ[A-Za-z0-9_-]{20,}", text))                      # no key
        self.assertTrue(all(u.startswith("https://fixture.invalid/rest/v1/") for u in fx["reads"]))
        self.assertTrue(all(r["status"] == 200 for r in fx["requests"]))
        self.assertNotIn(DASH, text)
        # every request was a read of a table of the site: no write, no function, no model
        self.assertEqual({r["what"] for r in fx["requests"]}, {"catalogue", "series", "entities", "sources"})

    def test_the_average_day_by_hour_is_the_mean_of_each_local_hour_of_the_recorded_rows(self):
        fx = fixture()
        given, out = call(fx, "h13_hours")
        q, rows = read_of(fx, "eia930_all_storage", "net_generation_battery_mw")
        self.assertEqual(len(rows), 355)
        by = collections.defaultdict(list)
        days = collections.defaultdict(set)
        for r in rows:
            local = instant(r["t"]).astimezone(CENTRAL)
            by[f"{local.hour:02d}"].append(float(r["v"]))
            days[f"{local.hour:02d}"].add(local.date())
        self.assertEqual([x["hour_of_day"] for x in out["result"]], [f"{h:02d}" for h in range(24)])
        for x in out["result"]:
            h = x["hour_of_day"]
            self.assertAlmostEqual(x["value"], sum(by[h]) / len(by[h]), places=5, msg=h)
            self.assertEqual((x["n"], x["days"]), (len(by[h]), len(days[h])), h)
        # a short hour carries its count, and nothing is filled: the rows of the answer are the rows read
        self.assertEqual(sum(x["n"] for x in out["result"]), 355)
        self.assertEqual(out["average_day"]["days_in_period"], 15)
        self.assertEqual(out["average_day"]["short_hours"], [{"hour_of_day": h, "days": 14} for h in ("19", "20", "21", "22", "23")])
        self.assertEqual(given["group_by"], "hour_of_day")

    def test_the_24_variables_of_a_table_of_months_come_back_as_one_series_with_the_tables_own_days(self):
        fx = fixture()
        _, out = call(fx, "h24_family_month")
        q, rows = read_of(fx, "generation_mix_hourly_profile", "avg_wind_mw_h00", "2026-09-01T00:00:00.000Z", "2026-10-01T00:00:00.000Z")
        value = {r["variable"]: r["v"] for r in rows}
        self.assertEqual(len(rows), 25)                                                   # the 24 hours and the count of days, in one request
        self.assertEqual(out["result"], [{"hour_of_day": f"{h:02d}", "value": value[f"avg_wind_mw_h{h:02d}"], "n": 1, "days": value["days_held"]} for h in range(24)])
        # the family with a family of days beside it
        _, price = call(fx, "family_with_days")
        q, rows = read_of(fx, "cost_of_power_hourly_profile", "rt_mean_h00")
        value = {r["variable"]: r["v"] for r in rows}
        self.assertEqual(price["result"], [{"hour_of_day": f"{h:02d}", "value": value[f"rt_mean_h{h:02d}"], "n": 1, "days": value[f"rt_days_h{h:02d}"]} for h in range(24)])

    def test_a_date_column_by_year_is_the_megawatts_and_the_count_of_the_recorded_rows(self):
        fx = fixture()
        given, out = call(fx, "h14_by_year")
        q, rows = read_of(fx, "ercot_interconnection_queue", "Other - Battery Energy Storage")
        self.assertEqual(given["date_column"], "proposed_in_service_date")
        self.assertEqual(q["select"], "t:extra->>proposed_in_service_date,v:capacity_mw,id:entity_id")
        self.assertEqual(len(rows), 628)
        by = collections.defaultdict(list)
        for r in rows:
            self.assertRegex(r["t"], r"^\d{4}-\d{2}-\d{2}$")                             # the source's own dates
            by[r["t"][:4]].append(float(r["v"]))
        self.assertEqual([x["year"] for x in out["result"]], sorted(by))
        for x in out["result"]:
            self.assertAlmostEqual(x["value"], sum(by[x["year"]]), places=4, msg=x["year"])
            self.assertEqual(x["n"], len(by[x["year"]]), x["year"])
        self.assertEqual(sum(x["n"] for x in out["result"]), 628)
        self.assertAlmostEqual(out["summary"]["sum_of_rows"], sum(float(r["v"]) for r in rows), places=2)
        self.assertEqual(out["date_column"]["rows_without_a_date"], 0)

    def test_the_newest_whole_day_is_the_newest_central_day_that_holds_all_its_hours(self):
        fx = fixture()
        given, out = call(fx, "h03_newest_by_hour")
        q, recent = read_of(fx, "eia930_all_demand", "ts_utc.desc.nullslast")
        self.assertEqual((given["day"], given["end"], q["limit"]), ("newest", "2026-10-08", "700"))
        counts = collections.Counter(instant(r["t"]).astimezone(CENTRAL).date().isoformat() for r in recent)
        newest = max(counts)
        self.assertEqual((newest, counts[newest]), ("2026-10-04", 19))                    # held to 18:00 Central: not whole
        whole = max(d for d in counts if counts[d] == 24 and d != min(counts))            # the oldest day of a full read may be cut
        self.assertEqual(whole, "2026-10-03")
        self.assertEqual((out["newest"]["day"], out["newest"]["whole"], out["newest"]["rows"], out["newest"]["rows_in_a_whole_day"]), (whole, True, 24, 24))
        self.assertEqual(out["newest"]["newer_days_not_whole"], [{"day": "2026-10-04", "rows": 19, "of": 24}])
        self.assertEqual((out["newest"]["day_before"], out["newest"]["day_before_held"]), ("2026-10-07", False))
        # the day's own 24 rows are the answer's, hour by hour
        q, day = read_of(fx, "eia930_all_demand", "ts_utc.asc.nullslast")
        self.assertEqual(len(day), 24)
        self.assertEqual([x["value"] for x in out["result"]], [float(r["v"]) for r in day])
        _, low = call(fx, "s12_newest_min")
        self.assertEqual(low["result"][0]["value"], min(float(r["v"]) for r in day))

    def test_a_series_is_asked_for_by_its_entity_alone_and_returns_what_entity_or_node_returned(self):
        fx = fixture()
        for url in fx["reads"]:
            q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
            if urlparse(url).path.endswith("/series"):
                self.assertNotIn("or", q, url)                                            # no request asks "entity or node"
        _, west = call(fx, "west_by_day")
        old = json.loads(src("tests", "fixtures", "session143", "tool_reads.json"))
        self.assertEqual(old["calls"][0]["input"]["entity"], "ercot:HB_WEST")
        self.assertEqual(west["result"], old["results"][0]["out"]["result"])              # the 30 rows of 7 October's "entity or node" read
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertIn('const byEntity = await one("entity");', tools)
        self.assertIn('const byNode = await one("node");', tools)
        self.assertNotIn("node.eq.${quote(a.entity)})`", tools)


class TheTwoFigures(unittest.TestCase):
    """The year's highest hourly demand: which figure is the operator's own and which is derived, against the tables."""

    def test_the_pages_figure_is_ercots_own_hourly_load_and_the_other_is_derived_from_eias(self):
        own = table_rows("ercot_zone_load_hourly")
        stress = table_rows("grid_stress_yearly")
        if own is None or stress is None:
            self.skipTest("the warehouse's tables are not on this machine")
        index = json.loads(src("site", "data", "datacenter", "index.json"))
        page = index["grids"]["ercot"]["demand"]["2026"]
        self.assertTrue(index["grids"]["ercot"]["demand_source"].startswith("ercot_zone_load_hourly"))
        # ERCOT's own total, hour by hour, in the page's own year (Central standard time): the hours the page counted
        system = sorted((r for r in own if r["entity"] == "ercot:system" and r["variable"] == "load" and "2026-01-01T06:00:00Z" <= r["ts_utc"] < "2027-01-01T06:00:00Z"), key=lambda r: r["ts_utc"])
        self.assertGreaterEqual(len(system), page["hours_held"])
        counted = system[: page["hours_held"]]
        top = max(counted, key=lambda r: float(r["value"]))
        self.assertAlmostEqual(float(top["value"]), page["peak_mw"], places=1)            # 91,133.7 MW: the page's figure is the table's highest hour
        self.assertEqual(round(page["peak_mw"]), 91134)
        self.assertEqual(top["ts_utc"], "2026-07-22T22:00:00Z")                           # the hour from 17:00 Central daylight time
        self.assertEqual({r["source"] for r in counted}, {"ercot:load_hist"})             # the operator's own archive
        # the other figure: the ERW's yearly table, from EIA's hourly demand
        derived = [r for r in stress if r["entity"] == "iso:ercot" and r["variable"] == "peak_demand_mw" and r["ts_utc"].startswith("2026")]
        self.assertEqual(len(derived), 1)
        self.assertEqual(float(derived[0]["value"]), 91075.0)
        self.assertEqual(derived[0]["source"], "erw:grid_stress")
        _, recorded = call(fixture(), "peak_derived")
        self.assertEqual(recorded["result"][0]["value"], float(derived[0]["value"]))      # and it is what the site's database returned
        self.assertEqual(recorded["tier"], "derived")

    def test_the_tools_own_list_says_which_is_which(self):
        ready = src("site", "lib", "chat", "ready.ts")
        for words in ('figure: "ERCOT\'s highest hourly demand of a year"', 'operator: { table: "site/data/datacenter/index.json", tool: "page_file", view: "demand", grid: "ercot", field: "highest_hour_mw"',
                      "the operator's own: ERCOT's hourly load from its Hourly Load Data Archives (ercot_zone_load_hourly, entity ercot:system)",
                      '{ table: "grid_stress_yearly", variable: "peak_demand_mw", entity: "iso:ercot", whose: "derived by the ERW from EIA\'s hourly demand (EIA-930), not ERCOT\'s own file" }',
                      "where two sources hold a figure, the operator's own data wins over a derived file, and the answer names both", "Never average the two"):
            self.assertIn(words, ready, words)
        self.assertNotIn("import ", ready)                                                # pure: no request, no model
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn("const note = pages && !(\"error\" in marked) ? precedenceOf(name, input) : null;", e)
        self.assertIn("return note ? { ...marked, source_precedence: note } : marked;", e)
        # the operator's table is not in the site's database: the tool reads it through the page's file
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("  - ercot_zone_load_hourly", live)


class TheSwitchesAndTheLayers(unittest.TestCase):
    def test_the_default_of_the_two_switches_lives_in_one_place(self):
        switches = src("site", "lib", "chat", "switches.ts")
        self.assertIn('export const SWITCH_DEFAULTS = { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" } as const;', switches)
        self.assertNotIn("import ", switches)
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn('import { readerEffort, rulePlanOn } from "./switches";', loop)
        self.assertNotIn("process.env.ASK_RULE_PLAN", loop)
        self.assertNotIn("SWITCH_DEFAULTS", loop)
        for f in ("ercot.ts", "tools.ts", "plan.ts", "forms.ts", "ready.ts", "pagefiles.ts", "panel.ts", "rollup.ts"):
            self.assertIsNone(re.search(r"process\.env\.ASK_(RULE_PLAN|READER_EFFORT)", src("site", "lib", "chat", f)), f)
        self.assertNotRegex(src("site", "app", "api", "ask", "route.ts"), r"ASK_(RULE_PLAN|READER_EFFORT)")

    def test_the_profile_the_route_serves_is_session_153s_with_one_layer_and_one_switch_takes_it_off(self):
        e = src("site", "lib", "chat", "ercot.ts")
        for words in ("export function profile153(): Profile {\n  const p = profile148();", "export function ercotProfile(): Profile {\n  const p = profile153();\n  if (!formsOffered() || !p.scope) return p;",
                      "system: (pages ? reworded(p.system, p.scope.iso).system : p.system) + formsGuide(pages) + (pages ? readyGuide() : \"\"),",
                      "retool: (tools) => extendTools("):
            self.assertIn(words, e, words)
        self.assertIn("ercotProfile()", src("site", "app", "api", "ask", "route.ts"))
        forms = src("site", "lib", "chat", "forms.ts")
        self.assertIn('return env !== "off";', forms)
        self.assertNotIn("import ", forms)
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("tools: profile?.tools ? [...TOOLS, ...profile.tools] : TOOLS,", loop)            # as session 137 pinned it
        self.assertIn("if (profile?.retool) params.tools = profile.retool(params.tools as Anthropic.Tool[]);", loop)

    def test_the_exported_specs_the_shared_reader_the_menu_and_the_ceilings_are_not_this_sessions(self):
        spec = src("site", "lib", "chat", "spec.json")
        ercot = src("site", "lib", "chat", "spec_ercot.json")
        for words in ("hour_of_day", "date_column", "source_precedence"):
            self.assertNotIn(words, spec + ercot, words)
        self.assertIn("This chat speaks for ERCOT only: for another grid, say so and that the general chat at /ask covers the whole warehouse.", json.loads(ercot)["system"])
        for f in (("site", "lib", "supabase.ts"), ("site", "lib", "pages.ts")):
            text = src(*f)
            for words in ("session 156", "Session 156", "hour_of_day", "date_column"):
                self.assertNotIn(words, text, f"{f[-1]}: {words}")
        limits = json.loads(src("site", "lib", "chat", "limits.json"))
        self.assertEqual((limits["daily_usd"], limits["monthly_usd"], limits["per_visitor_per_day"]), (3, 30, 15))
        release = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', release)
        # session 166 (the owner's instruction of 8 October 2026): the three pages that were open are in review; no page is live
        for path in ("/cost-of-power/battery", "/network", "/storage"):
            self.assertIn(f'"{path}": "review"', release)
        self.assertEqual(re.findall(r'"(/[^"]*)":\s*"live"', release), [])
        # the three forms were made with the database's existing interface: the tool sends reads of its tables and nothing else
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertNotIn("rpc(", tools)
        self.assertIn('import { DataError, HOURLY, rest, restCount } from "@/lib/supabase";', tools)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in (("site", "lib", "chat", "forms.ts"), ("site", "lib", "chat", "ready.ts"), ("site", "lib", "chat", "switches.ts"), ("site", "lib", "chat", "tools.ts"), ("site", "lib", "chat", "ercot.ts"),
                  ("site", "lib", "chat", "ask.ts"), ("site", "scripts", "record-ask-ready.mjs"), ("site", "scripts", "eval-judge.mjs"), ("site", "app", "ask", "ercot", "page.tsx"),
                  ("docs", "methods", "ask_ercot.md"), ("warehouse", "chat", "eval_ercot_panel.json"), ("warehouse", "chat", "eval_ercot_pages.json"), ("warehouse", "chat", "eval", "ercot_pages_expected.py"),
                  ("tests", "test_session156.py")):
            self.assertNotIn(DASH, src(*f), f[-1])


class TheClosingWords(unittest.TestCase):
    def test_the_thirteen_refusals_about_another_grid_carry_the_closing_and_the_rest_do_not(self):
        old = json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))
        new = json.loads(src("warehouse", "chat", "eval_ercot_pages.json"))
        self.assertEqual(len(old["questions"]), 100)
        self.assertEqual(len(new["questions"]), 20)
        carried = [q["id"] for q in old["questions"] + new["questions"] if "close" in q or "never" in q]
        self.assertEqual(carried, OTHER_GRID + ["p19", "p20"])
        for q in old["questions"] + new["questions"]:
            if q["id"] in carried:
                self.assertEqual((q["kind"], q["close"], q["never"]), ("refuse", CLOSE, NEVER), q["id"])
        self.assertIn("rules_added_156", old)
        self.assertEqual(set(old["rules"]), {"conceptual", "chart", "sentence", "refuse"})  # session 137's rules are as they were
        self.assertEqual(collections.Counter(q["kind"] for q in old["questions"]), {"conceptual": 25, "chart": 25, "sentence": 25, "refuse": 25})
        # the tool's closing is what the judge asks for, and the old words are what it no longer takes
        ready = src("site", "lib", "chat", "ready.ts")
        closing = "Ask ERCOT answers for the Texas grid, and for the other grids only what four pages of this site show: curtailment and free energy, what a datacenter pays, the capture price and the resource layers."
        self.assertIn("export const CLOSING = `${TOOL_NAME} answers for the Texas grid, and for the other grids only what four pages of this site show: curtailment and free energy, what a datacenter pays, the capture price and the resource layers.`;", ready)
        self.assertIn('export const TOOL_NAME = "Ask ERCOT";', ready)
        self.assertRegex(closing, CLOSE)
        self.assertNotRegex(closing, NEVER)
        for words in ("This chat speaks for ERCOT only", "This panel answers for ERCOT only."):
            self.assertRegex(words, NEVER)
        judge = src("site", "scripts", "eval-judge.mjs")
        self.assertIn('if (q.close && !new RegExp(q.close, "i").test(String(r.answer ?? ""))) why.push(', judge)
        self.assertIn('if (q.never && new RegExp(q.never, "i").test(String(r.answer ?? ""))) why.push(', judge)
        script = src("warehouse", "chat", "eval", "ercot_pages_expected.py")
        self.assertIn(f'CLOSE = "{CLOSE}"', script)
        self.assertIn(f'NEVER = "{NEVER}"', script)

    def test_the_page_and_the_note_say_what_the_tool_now_answers_for(self):
        page = src("site", "app", "ask", "ercot", "page.tsx")
        self.assertNotIn("speaks for ERCOT only", page)
        self.assertIn("only what four pages show: curtailment, what a datacenter pays, the capture price and the resource layers;", page)
        note = src("docs", "methods", "ask_ercot.md")
        self.assertIn("## To ready (session 156, 8 October 2026)", note)
        for words in ("**Three things the query does in one call.**", "The average day by hour", "A date column by year", "The newest day held", "**The entity first.**", "Nothing is filled.",
                      "**The two switches are on.**", "`site/lib/chat/switches.ts`", "`ASK_RULE_PLAN=off` or `ASK_READER_EFFORT=off`",
                      "where two sources hold a figure, the operator's own data wins over a derived file, and the answer names both",
                      "**91,134 MW is the operator's own.**", "**91,075 MW is derived.**", "**Which source holds Texas's curtailment share.**", "from 28 September 2026", "from 19 September 2026 and no share",
                      "**A refusal's closing words.**", "still speaks for ERCOT only", "`ASK_FORMS=off`", "no function, no view and no change to the database"):
            self.assertIn(words, note, words)
        self.assertNotIn(DASH, note)


class TheRecord(unittest.TestCase):
    """Phase 2: the 120 questions asked once on 8 October 2026 (warehouse/chat/eval_ercot_ready_results_156.csv)."""

    def rows(self):
        with open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_ready_results_156.csv"), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(line for line in f if not line.startswith("#")))

    def median(self, values):
        v = sorted(values)
        return (v[len(v) // 2] + v[(len(v) - 1) // 2]) / 2

    def test_every_question_was_asked_once_and_none_again(self):
        rows = self.rows()
        self.assertEqual(collections.Counter(r["set"] for r in rows), {"new": 20, "old": 100})   # no question failed, so none was asked again
        self.assertEqual(len({r["id"] for r in rows}), 120)
        old = {q["id"] for q in json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))["questions"]}
        new = {q["id"] for q in json.loads(src("warehouse", "chat", "eval_ercot_pages.json"))["questions"]}
        self.assertEqual({r["id"] for r in rows if r["set"] == "old"}, old)
        self.assertEqual({r["id"] for r in rows if r["set"] == "new"}, new)
        self.assertTrue(all(r["status"] in ("answered", "not_in_warehouse") for r in rows))  # no error, no answer that could not be verified
        self.assertAlmostEqual(sum(float(r["usd"]) for r in rows), 2.2513, places=4)        # what the site's ledger holds for the 194 model calls
        self.assertLess(sum(float(r["usd"]) for r in rows), 3.70)                          # under the stop

    def test_the_counts_the_method_note_gives_are_the_records(self):
        rows = self.rows()
        note = src("docs", "methods", "ask_ercot.md")
        old = [r for r in rows if r["set"] == "old"]
        new = [r for r in rows if r["set"] == "new"]
        self.assertEqual((sum(int(r["pass"]) for r in old), sum(int(r["pass"]) for r in new)), (100, 20))
        numbers = [float(r["seconds_words"]) for r in old if r["kind"] in ("chart", "sentence")]
        ideas = [float(r["seconds_words"]) for r in old if r["kind"] == "conceptual"]
        refused = [float(r["seconds_words"]) for r in old if r["kind"] == "refuse"]
        self.assertEqual((round(self.median(numbers), 2), sum(1 for x in numbers if x < 5)), (4.6, 30))
        self.assertEqual((round(self.median(ideas), 2), sum(1 for x in ideas if x < 2)), (2.1, 8))
        self.assertEqual((round(self.median(refused), 2), sum(1 for x in refused if x < 2)), (2.1, 7))
        self.assertEqual(round(self.median([float(r["seconds_words"]) for r in old]), 2), 2.45)
        self.assertEqual(round(sum(float(r["usd"]) for r in old) / 100, 4), 0.0169)
        self.assertEqual(round(sum(float(r["usd"]) for r in new) / 20, 4), 0.0279)
        self.assertEqual(round(self.median([float(r["seconds_words"]) for r in new]), 2), 4.15)
        self.assertEqual(sum(1 for r in new if r["kind"] != "refuse" and float(r["seconds_words"]) < 5), 13)
        for words in ("| The 100, all | 100 of 100 (98, 98) | 2.45 (2.8, 4.05) | | 0.0169 (0.0171, 0.0202) |", "| About numbers (50; target 5 seconds) | 50 (48, 48) | 4.6 (4.75, 5.6) | 30 (27, 11) | |",
                      "| About an idea (25; target 2 seconds) | 25 (25, 25) | 2.1 (2.1, 2.4) | 8 (7, 3) | |", "| Refused (25) | 25 (25, 25) | 2.1 (2.0, 2.1) | 7 under 2 seconds (11, 4) | |",
                      "| The 20 of the four pages | 20 of 20 (19 in session 153) | 4.15 (5.0) | 13 of the 18 about numbers under 5 seconds (7) | 0.0279 (0.0281) |",
                      "Each question was asked once."):
            self.assertIn(words, note, words)
        # the earlier sessions' figures in brackets are those sessions' own records
        self.assertEqual((sum(int(r["s148_pass"]) for r in old), sum(int(r["s153_pass"]) for r in old), sum(int(r["s153_pass"]) for r in new)), (98, 98, 19))

    def test_the_questions_that_failed_or_were_slow_are_one_read_each_with_the_new_forms(self):
        rows = {r["id"]: r for r in self.rows()}
        want = {"h13": "query:eia930_all_storage+hour_of_day+newest", "h24": "query:generation_mix_hourly_profile+hour_of_day+newest", "h14": "query:ercot_interconnection_queue+date_column",
                "h03": "query:eia930_all_demand+newest", "s12": "query:eia930_all_demand+newest", "p14": "page_file:share"}
        for i, tools in want.items():
            r = rows[i]
            self.assertEqual((r["pass"], r["model_calls"], r["tool_calls"], r["tools"]), ("1", "2", "1", tools), i)
            self.assertLess(float(r["seconds_words"]), 6, i)
        # each took 15 to 28 seconds, or failed, in the two sessions before
        self.assertEqual([rows[i]["s148_pass"] for i in ("h14", "h24")], ["0", "0"])
        self.assertEqual([rows[i]["s153_pass"] for i in ("h13", "h14", "p14")], ["0", "0", "0"])
        for i in ("h13", "h03", "s12"):
            self.assertGreater(float(rows[i]["s148_seconds_words"]), 19, i)
        self.assertEqual((rows["h13"]["series_rows"], rows["h24"]["series_rows"], rows["h14"]["series_rows"], rows["h03"]["series_rows"]), ("24", "24", "8", "24"))
        # two sources for one figure: both were read in one turn and both are cited, the operator's own first
        s16 = rows["s16"]
        self.assertEqual((s16["pass"], s16["model_calls"], s16["tools"], s16["citations"]), ("1", "2", "page_file:demand query:grid_stress_yearly", "site/data/datacenter/index.json grid_stress_yearly"))
        # the rule planned sixteen, all pass; the thirteen refusals about another grid all pass under the stricter judge
        ruled = [r for r in rows.values() if r["planned_by"] == "rule"]
        self.assertEqual((len(ruled), sum(int(r["pass"]) for r in ruled)), (16, 16))
        self.assertTrue(all(rows[i]["pass"] == "1" and rows[i]["status"] == "not_in_warehouse" for i in OTHER_GRID + ["p19", "p20"]))
        self.assertNotIn(DASH, src("warehouse", "chat", "eval_ercot_ready_results_156.csv") + src("warehouse", "chat", "eval", "ercot_ready_results_156.py"))


class TheNodeTests(unittest.TestCase):
    def test_the_sessions_own_tests_pass_with_no_request_and_no_switch_set(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        # the switches are taken out of the child's environment only: this process's is not changed
        env = {k: v for k, v in os.environ.items() if k not in ("ASK_FORMS", "ASK_PAGES", "ASK_ROLLUP", "ASK_RULE_PLAN", "ASK_READER_EFFORT", "ASK_WRITER_EFFORT", "ASK_PLANNER", "ASK_FAST", "ASK_THINKING", "NEXT_PHASE")}
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-ready.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-2500:] + r.stderr[-1500:])
        self.assertIn("20 of 20 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
