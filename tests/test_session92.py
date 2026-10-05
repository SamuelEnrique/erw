"""Session 92: Ask ERCOT, the reference version (warehouse/chat/ercot.py).

Energy Research Warehouse (ERW). No test here calls a model: the loop runs against a stand-in client whose replies
are scripted, and the tools run for real on this machine's tables (the tests that need a table skip where it is
absent).

    python -m unittest tests.test_session92 -v
"""

import json
import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat", "eval"))
import ask  # noqa: E402
import ercot  # noqa: E402
import tools  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def held(*tables):
    return all(os.path.exists(os.path.join(OUT, t + ".csv")) for t in tables)


class Reply:
    """One scripted reply of the stand-in model: tool calls, or a final answer."""
    def __init__(self, calls=None, final=None):
        self.usage = types.SimpleNamespace(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        self._request_id = "req_test"
        if calls:
            self.stop_reason = "tool_use"
            self.content = [types.SimpleNamespace(type="tool_use", id=f"t{i}", name=n, input=a) for i, (n, a) in enumerate(calls)]
        else:
            self.stop_reason = "end_turn"
            self.content = [types.SimpleNamespace(type="text", text=json.dumps(final))]


class Client:
    def __init__(self, script):
        self.script, self.requests = list(script), []
        self.messages = types.SimpleNamespace(create=self.create)

    def create(self, **kw):
        self.requests.append({**kw, "messages": list(kw["messages"])})  # the loop appends to one list: keep it as sent
        r = self.script.pop(0)
        return r(kw) if callable(r) else r


BUILDOUT = {"table": "storage_buildout_monthly", "entity": "iso:ercot", "variable": "battery_operating_mw", "aggregation": "max", "group_by": "year", "start": "2020-01-01"}
ONE = {"table": "storage_buildout_monthly", "entity": "iso:ercot", "variable": "battery_operating_mw", "aggregation": "latest"}
CITE = [{"table": "storage_buildout_monthly", "source_report": "x", "data_version": "y", "tier": "source"}]
UPS = ["How long can the fleet run?", "How much is planned?"]


def final(answer, series=(), followups=UPS, citations=CITE, missing=False):
    # session 121: the schema gained nearest (a refusal names the tables that come closest) and premise
    return Reply(final={"answer": answer, "citations": citations, "not_in_warehouse": missing, "series": list(series), "followups": list(followups),
                        "nearest": ["storage_buildout_monthly"] if missing else [], "premise": ""})


@unittest.skipUnless(held("storage_buildout_monthly"), "storage_buildout_monthly is not on this machine")
class TheLoop(unittest.TestCase):
    def run_script(self, script, question="How has the fleet grown?", context=None):
        c = Client(script)
        rec = ercot.ErcotAsker(model="stand-in", client=c).ask(question, today="2026-10-04", context=context)
        return rec, c

    def value(self, args):
        tools.SCOPE = ercot.SCOPE
        return tools.query(**args)

    def test_every_query_result_carries_an_id_the_answer_can_name(self):
        rec, c = self.run_script([Reply(calls=[("query", BUILDOUT)]), Reply(calls=[("compare", {"a": ONE, "b": BUILDOUT})]), lambda kw: final("It grew.", ["r1"])])
        first = json.loads(c.requests[1]["messages"][-1]["content"][0]["content"])
        second = json.loads(c.requests[2]["messages"][-1]["content"][0]["content"])
        self.assertEqual(first["result_id"], "r1")
        self.assertEqual((second["a"]["result_id"], second["b"]["result_id"]), ("r2a", "r2b"))
        self.assertEqual(rec["status"], "answered")
        self.assertEqual([s["result_id"] for s in rec["series"]], ["r1"])

    def test_the_series_is_the_tools_rows_with_their_source_never_the_models_text(self):
        truth = self.value(BUILDOUT)
        rec, _ = self.run_script([Reply(calls=[("query", BUILDOUT)]), final("The fleet grew every year.", ["r1"])])
        s = rec["series"][0]
        self.assertEqual([(r["key"], r["value"]) for r in s["rows"]], [(r["year"], r["value"]) for r in truth["result"]])
        self.assertGreaterEqual(len(s["rows"]), 6)
        self.assertEqual((s["table"], s["kind"], s["unit"], s["group_by"]), ("storage_buildout_monthly", "line", "MW", "year"))
        self.assertEqual((s["source_report"], s["tier"], s["license"]), (truth["source_report"], truth["tier"], truth["license"]))
        self.assertTrue(s["source_report"])
        self.assertEqual(s["chosen_by"], "the answer")
        self.assertIn("battery_operating_mw", s["title"])

    def test_an_answer_that_rests_on_a_series_returns_it_even_when_the_model_names_none(self):
        rec, _ = self.run_script([Reply(calls=[("query", BUILDOUT)]), final("The fleet grew every year.", [])])
        self.assertEqual(len(rec["series"]), 1)
        self.assertTrue(rec["series"][0]["chosen_by"].startswith("default"))
        # one number is not a series
        rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final("See storage_buildout_monthly.", [])])
        self.assertEqual(rec["series"], [])

    def test_a_series_the_tools_never_returned_is_sent_back_and_then_refused(self):
        rec, c = self.run_script([Reply(calls=[("query", BUILDOUT)]), final("It grew.", ["r7"]), final("It grew.", ["r7"])])
        self.assertEqual(rec["status"], "refused_unverified")
        self.assertEqual(rec["series"], [])
        self.assertIn("series names result ids no tool returned: r7", rec["first_violations"])
        self.assertIn("r7", c.requests[2]["messages"][-1]["content"])
        # a single value named as a series is sent back too, and a correction passes
        rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final("See the table.", ["r1"]), final("See the table.", [])])
        self.assertEqual((rec["status"], rec["retried"]), ("answered", True))

    def test_follow_ups_are_two_or_three_questions_with_no_number_the_tools_did_not_return(self):
        for ups, ok in (([], False), (["One?"], False), (UPS, True), (UPS + ["A third?"], True), (UPS + ["A third?", "A fourth?"], False),
                        (["What happened in 2021?", "And in 2030?"], True), (["Why did prices reach 9000?", "How much is planned?"], False)):
            rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final("See the table.", [], ups), final("See the table.", [], UPS)])
            self.assertEqual(rec["retried"], not ok, ups)
            self.assertEqual(rec["followups"], ups if ok else UPS)
        # a number the tools did return may be asked about
        v = self.value(ONE)["result"][0]["value"]
        rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final("See the table.", [], [f"Is {v} MW the peak?", "How much is planned?"])])
        self.assertFalse(rec["retried"])

    def test_the_number_check_is_the_loops_own(self):
        rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final("The fleet is 99999 MW."), final("The fleet is 99999 MW.")])
        self.assertEqual(rec["status"], "refused_unverified")
        self.assertEqual((rec["series"], rec["followups"]), ([], []))
        v = self.value(ONE)["result"][0]["value"]
        rec, _ = self.run_script([Reply(calls=[("query", ONE)]), final(f"The fleet is {v} MW (storage_buildout_monthly).")])
        self.assertEqual(rec["status"], "answered")

    def test_not_in_the_warehouse_keeps_its_follow_ups_and_has_no_series(self):
        rec, _ = self.run_script([final("Not in the warehouse: the tables hold no load zone.", [], UPS, citations=[], missing=True)])
        self.assertEqual((rec["status"], rec["series"], rec["followups"]), ("not_in_warehouse", [], UPS))

    def test_the_view_the_reader_came_from_is_in_the_first_message_and_its_numbers_count_as_given(self):
        ctx = {"view": "/cost-of-power/battery", "title": "What a battery earns", "settings": {"duration": "8 hours", "strategy": "dayahead"}}
        rec, c = self.run_script([final("For the 8-hour battery see battery_stack_monthly.", citations=[], missing=True)], "What did this battery earn?", ctx)
        first = c.requests[0]["messages"][0]["content"]
        self.assertIn("The reader opened this chat from the site's page /cost-of-power/battery (What a battery earns), set to: duration 8 hours; strategy dayahead.", first)
        self.assertTrue(first.startswith("Today is 2026-10-04 (UTC)."))
        self.assertTrue(first.endswith("Question: What did this battery earn?"))
        self.assertFalse(rec["retried"])
        # without a context the first message is the general chat's own
        _, c = self.run_script([final("Not held.", citations=[], missing=True)], "Q?")
        self.assertEqual(c.requests[0]["messages"][0]["content"], "Today is 2026-10-04 (UTC).\n\nQuestion: Q?")

    def test_the_request_is_the_profiles(self):
        _, c = self.run_script([final("Not held.", citations=[], missing=True)])
        kw = c.requests[0]
        self.assertEqual(kw["output_config"], {"effort": "medium", "format": {"type": "json_schema", "schema": ercot.SCHEMA}})
        self.assertEqual(kw["tools"], tools.TOOLS)
        self.assertEqual(len(kw["system"]), 1)
        self.assertTrue(kw["system"][0]["text"].startswith("You are Ask ERCOT."))
        self.assertIn("# The ERCOT tables", kw["system"][0]["text"])
        self.assertEqual(kw["system"][0]["cache_control"], {"type": "ephemeral"})


class TheScope(unittest.TestCase):
    def setUp(self):
        tools.SCOPE = ercot.SCOPE
        tools._frames.clear()

    def tearDown(self):
        tools.set_scope(None)

    def test_it_names_every_table_the_session_asked_for(self):
        for t in ("ercot_all_hub_prices_history", "ercot_as_prices", "eia930_all_demand", "eia930_all_generation", "eia930_all_storage", "battery_stack_monthly",
                  "storage_buildout_monthly", "storage_owners_monthly", "shoulder_hours_monthly", "event_window_daily", "event_study_estimates",
                  "lbnl_interconnection_queue", "ferc_eqr_contracts"):
            self.assertIn(t, ercot.SCOPE["tables"])
        self.assertEqual(ercot.SCOPE["tables"], [t for t, _ in ercot.CARDS])
        self.assertEqual(len(set(ercot.SCOPE["tables"])), len(ercot.SCOPE["tables"]))
        self.assertIn("INTERNAL", dict(ercot.CARDS)["ferc_eqr_contracts"])

    def test_each_table_is_read_for_ercots_rows_only(self):
        checks = {
            "lbnl_interconnection_queue": lambda d: set(d["region"]) == {"ERCOT"},
            "storage_owners_monthly": lambda d: set(d["x_grid"]) == {"ercot"},
            "storage_buildout_monthly": lambda d: set(d["entity"]) == {"iso:ercot"},
            "shoulder_hours_monthly": lambda d: set(d["entity"]) == {"iso:ercot"},
            "battery_stack_monthly": lambda d: set(d["entity"]) == {"ercot:HB_HUBAVG"},
            "event_window_daily": lambda d: set(d["entity"]) == {"eia930:ERCO", "ercot:HB_HUBAVG"},
            "ferc_eqr_contracts": lambda d: set(d["x_point_of_delivery_balancing_authority"]) == {"ERCO"},
            "cost_of_power_monthly": lambda d: set(d["entity"]) == {"ercot:HB_HUBAVG"},
            "iso_rtm_hub_prices": lambda d: all(e.startswith("ercot:") for e in set(d["entity"])),
            "eia930_all_demand": lambda d: set(d["entity"]) == {"eia930:ERCO"},
            "storage_capacity": lambda d: set(d["iso"]) == {"ERCOT"},
        }
        ran = 0
        for t, ok in checks.items():
            if not held(t):
                continue
            df = tools._table(t)
            self.assertGreater(len(df), 0, t)
            self.assertTrue(ok(df), f"{t} holds rows that are not ERCOT's")
            ran += 1
        if not ran:
            self.skipTest("none of the tables is on this machine")

    def test_a_table_outside_the_scope_is_refused(self):
        out, err = tools.run("query", {"table": "eia_fuel_spot_prices", "aggregation": "latest"})
        self.assertTrue(err)
        self.assertIn("does not carry ERCOT", out["error"])

    @unittest.skipUnless(held("shoulder_hours_monthly"), "shoulder_hours_monthly is not on this machine")
    def test_a_month_per_row_since_2019_fits_one_result(self):
        r = tools.query(table="shoulder_hours_monthly", variable="shoulder_hours", aggregation="mean", group_by="month")
        self.assertGreater(len(r["result"]), 60)
        self.assertLessEqual(len(r["result"]), ercot.MAX_GROUPS)
        tools.set_scope(None)
        r = tools.query(table="shoulder_hours_monthly", entity="iso:ercot", variable="shoulder_hours", aggregation="mean", group_by="month")
        self.assertEqual(len(r["result"]), tools.MAX_GROUPS, "the general chat's cap moved")


class TheTrapsTheFirstRunFound(unittest.TestCase):
    """The first run of the evaluation: half the answers were sent back once by the literal number check, two were
    refused, and one was wrong by a month. What was changed for each."""

    def tearDown(self):
        tools.set_scope(None)

    @unittest.skipUnless(held("carbon_intensity_monthly"), "carbon_intensity_monthly is not on this machine")
    def test_a_month_or_a_year_is_grouped_by_its_own_label_whatever_tz_says(self):
        q = dict(table="carbon_intensity_monthly", variable="intensity_generation", aggregation="count", group_by="year", tz="America/Chicago")
        tools.SCOPE = ercot.SCOPE
        tools._frames.clear()
        mine = {r["year"]: r["count"] for r in tools.query(**q)["result"]}
        plain = {r["year"]: r["count"] for r in tools.query(**{**q, "tz": "UTC"})["result"]}
        self.assertEqual(mine, plain, "a monthly row moved to another year when a time zone was passed")
        self.assertEqual(sum(mine.values()), tools.query(table="carbon_intensity_monthly", variable="intensity_generation", aggregation="count")["result"][0]["count"])
        # session 103, on Samuel's instruction: the general chat groups such rows by their own label too (it lost each
        # year's January until then; this assertion used to hold that the trap was still there)
        tools.set_scope(None)
        general = {r["year"]: r["count"] for r in tools.query(**{**q, "entity": "eia930:ERCO"})["result"]}
        self.assertEqual(general, plain)

    def test_a_name_asked_by_counts_as_fetched(self):
        self.assertEqual(ercot.spelled({"variable": "foresight_4h_revenue_total_usd_per_mw", "entity": "ercot:HB_HUBAVG", "where": {"event": "uri_2021"}, "start": "2021-02-07"}),
                         "foresight 4 h revenue total usd per mw ercot HB HUBAVG uri 2021")
        self.assertEqual(ercot.spelled({"a": {"variable": "dayahead_8h_days_held"}, "b": {"entity": "ercot:REGUP"}}), "dayahead 8 h days held ercot REGUP")
        self.assertEqual(ercot.spelled({"start": "2024-01-01", "percentile": 99}), "")
        self.assertEqual(ask.unverified("a 4-hour battery", ["q", ercot.spelled({"variable": "foresight_4h_revenue_total_usd_per_mw"})]), [])
        self.assertEqual(ask.unverified("a 6-hour battery", ["q", ercot.spelled({"variable": "foresight_4h_revenue_total_usd_per_mw"})]), ["6"])
        js = node("const e = await import('./lib/chat/ercot.ts');"
                  "console.log(JSON.stringify([e.spelled({ variable: 'foresight_4h_revenue_total_usd_per_mw', entity: 'ercot:HB_HUBAVG', where: { event: 'uri_2021' }, start: '2021-02-07' }),"
                  " e.spelled({ a: { variable: 'dayahead_8h_days_held' }, b: { entity: 'ercot:REGUP' } }), e.spelled({ start: '2024-01-01', percentile: 99 })]));")
        self.assertEqual(js, ["foresight 4 h revenue total usd per mw ercot HB HUBAVG uri 2021", "dayahead 8 h days held ercot REGUP", ""])

    def test_the_model_is_told_the_check_is_literal_and_the_guide_names_no_form_number(self):
        self.assertIn("The check on your answer is literal", ercot.RULES)
        self.assertIn("must contain no digit other than a year", ercot.RULES)
        for _, text in ercot.CARDS:
            self.assertNotRegex(text, r"EIA-\d", "a card names a source by its form number, which the model then repeats and the check refuses")


class TheGeneralChatIsAsItWas(unittest.TestCase):
    def test_its_exported_spec_is_the_committed_one(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec.json")
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                ask.export_spec(p)
            self.assertEqual(open(p, encoding="utf-8").read(), src("site", "lib", "chat", "spec.json"))

    def test_its_loop_has_the_defaults_it_had(self):
        a = ask.Asker.__new__(ask.Asker)
        self.assertIs(a.schema, ask.ANSWER_SCHEMA)
        self.assertEqual((a.effort, a.retry), (ask.EFFORT, ask.RETRY))
        self.assertIs(a.tool_list(), tools.TOOLS)
        self.assertEqual(a.opening("Q?", "2026-10-04"), "Today is 2026-10-04 (UTC).\n\nQuestion: Q?")
        self.assertEqual(a.opening("Q?", "2026-10-04", {"view": "/x"}), "Today is 2026-10-04 (UTC).\n\nQuestion: Q?")
        out = {"result": [1]}
        self.assertIs(a.tag("query", {}, out, 1), out)
        self.assertEqual((a.extra_problems({}, []), a.extra_sources({"view": "/x"})), ([], []))

    @unittest.skipUnless(held("storage_buildout_monthly"), "storage_buildout_monthly is not on this machine")
    def test_a_grid_page_chat_gets_no_id_no_series_and_no_follow_up(self):
        c = Client([Reply(calls=[("query", {"table": "storage_capacity", "aggregation": "count"})]),
                    Reply(final={"answer": "See storage_capacity.", "citations": [{"table": "storage_capacity", "source_report": "x", "data_version": "y", "tier": "derived"}], "not_in_warehouse": False})])
        try:
            rec = ask.Asker(model="stand-in", client=c, grid="ercot").ask("How many units?", today="2026-10-04")
        finally:
            tools.set_scope(None)
        sent = json.loads(c.requests[1]["messages"][-1]["content"][0]["content"])
        self.assertNotIn("result_id", sent)
        self.assertNotIn("series", rec)
        self.assertNotIn("followups", rec)
        self.assertEqual(c.requests[0]["output_config"]["format"]["schema"], ask.ANSWER_SCHEMA)
        self.assertEqual(c.requests[0]["output_config"]["effort"], "high")


class TheEvaluationSet(unittest.TestCase):
    def setUp(self):
        import yaml
        self.spec = yaml.safe_load(src("warehouse", "chat", "eval", "questions_ercot.yaml"))
        self.qs = self.spec["questions"]

    def test_at_least_forty_questions_from_lookups_to_joins(self):
        kinds = {}
        for q in self.qs:
            kinds[q["kind"]] = kinds.get(q["kind"], 0) + 1
        self.assertGreaterEqual(len(self.qs), 40)
        self.assertEqual(set(kinds), {"lookup", "series", "join", "refuse", "context"})
        self.assertGreaterEqual(kinds["join"], 6)
        self.assertGreaterEqual(kinds["lookup"], 15)
        for q in self.qs:
            if q["kind"] == "join":
                self.assertTrue(len(q["tables"]) >= 2 or "cost_of_power_monthly" in q["note"], q["id"])
            if q["kind"] == "refuse":
                self.assertTrue(q["refuse"] and not q["expected"])
            if q["kind"] == "context":
                self.assertTrue(q["context"]["view"].startswith("/"))
            if q["kind"] == "series":
                self.assertTrue(q["series"])
            self.assertTrue(q["refuse"] or (q["expected"] and q["tables"] and q["note"]), q["id"])
            # a question may also accept a table only the old chat reads (it gave the right number from one); the first
            # table named is always one Ask ERCOT reads
            if q["tables"]:
                self.assertIn(q["tables"][0], ercot.SCOPE["tables"], f"{q['id']} expects a table Ask ERCOT cannot read")
        self.assertTrue(any(q["internal"] for q in self.qs))
        self.assertEqual(len({q["question"] for q in self.qs}), len(self.qs))

    @unittest.skipUnless(held("storage_buildout_monthly", "shoulder_hours_monthly", "battery_stack_monthly"), "the tables are not on this machine")
    def test_the_tools_give_the_expected_numbers(self):
        # the set's numbers come from pandas on the files; the tools must agree, or a right answer would be marked wrong
        tools.SCOPE = ercot.SCOPE
        tools._frames.clear()
        try:
            by = {q["question"]: q for q in self.qs}
            q = by["How many MW of batteries are operating in ERCOT in the newest inventory held?"]
            r = tools.query(table="storage_buildout_monthly", variable="battery_operating_mw", aggregation="latest")
            self.assertAlmostEqual(r["result"][0]["value"], q["expected"][0], places=3)
            q = by["On the ten worst evenings of 2026, how many hours of storage did ERCOT's shoulder ask for on average?"]
            r = tools.query(table="shoulder_hours_monthly", variable="year_worst10_mean_shoulder_hours_needed", aggregation="latest")
            self.assertAlmostEqual(r["result"][0]["value"], q["expected"][0], places=3)
            q = [x for x in self.qs if x["question"].startswith("Year by year since 2018")][0]
            r = tools.query(table="battery_stack_monthly", variable="foresight_4h_revenue_total_usd_per_mw", aggregation="sum", group_by="year")
            self.assertAlmostEqual(max(x["value"] for x in r["result"]), q["expected"][0], places=1)
        finally:
            tools.set_scope(None)

    def test_the_scorer_marks_what_the_reference_version_adds(self):
        import ercot_eval
        q = {"series": True, "tables": ["storage_buildout_monthly"]}
        rows = [{"key": str(y), "value": 1.0} for y in (2023, 2024, 2025)]
        good = {"followups": ["A?", "B?"], "series": [{"rows": rows, "table": "storage_buildout_monthly", "source_report": "EIA-860M"}]}
        self.assertEqual(ercot_eval.extras(q, good), {"followups": True, "series": True})
        self.assertEqual(ercot_eval.extras(q, {**good, "followups": ["A?"]})["followups"], False)
        self.assertEqual(ercot_eval.extras(q, {**good, "followups": ["A", "B?"]})["followups"], False)
        self.assertEqual(ercot_eval.extras(q, {**good, "series": []})["series"], False)
        self.assertEqual(ercot_eval.extras(q, {**good, "series": [{**good["series"][0], "table": "another"}]})["series"], False)
        self.assertNotIn("series", ercot_eval.extras({"series": False, "tables": []}, good))


def node(js, alias=True):
    import shutil
    import subprocess
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    # session 102: the site's modules import its packages (lib/chat/ask.ts imports @anthropic-ai/sdk). GitHub's workflow
    # runs tests/ before `npm ci`, so there the packages are absent and these three tests failed the first deploy of the
    # landing; without the packages the test is skipped, and the site's own build and checks cover the module
    if not os.path.isdir(os.path.join(ROOT, "site", "node_modules", "@anthropic-ai", "sdk")):
        raise unittest.SkipTest("the site's packages are not installed on this machine (npm ci)")
    cmd = [exe] + (["--import", "./scripts/alias-register.mjs"] if alias else []) + ["--input-type=module", "-e", js]
    r = subprocess.run(cmd, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheSite(unittest.TestCase):
    """The site's profile (site/lib/chat/ercot.ts) is the Python one: the same spec, and the same answers on the same
    tool results."""

    def test_the_sites_spec_is_the_one_the_profile_exports(self):
        import contextlib
        import io
        import tempfile
        if not held("storage_buildout_monthly"):
            self.skipTest("the coverage of this machine is not the one the spec was exported from")
        tools.set_scope(None)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec_ercot.json")
            with contextlib.redirect_stdout(io.StringIO()):
                ercot.export_spec(p)
            new, old = json.load(open(p, encoding="utf-8")), json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        # the guide's one line of facts per table moves with every daily run (a table's last time); the rest is fixed
        strip = lambda s: "\n".join(ln for ln in s.splitlines() if not ln.startswith("## "))  # noqa: E731
        self.assertEqual(strip(new.pop("system")), strip(old.pop("system")))
        self.assertEqual(new, old)
        self.assertEqual(old["tables"], ercot.SCOPE["tables"])

    def test_the_profile_marks_checks_and_finishes_as_the_python_one(self):
        rows = [{"year": str(y), "value": float(v), "n": 12} for y, v in ((2021, 10), (2022, 20), (2023, 30))]
        q_out = {"aggregation": "max", "value_column": "value", "rows_matched": 36, "units": ["MW"], "result": rows, "table": "storage_buildout_monthly",
                 "source_report": "EIA-860M", "license": "public", "tier": "source", "data_version": "v"}
        one = {**q_out, "result": [{"value": 30.0, "at": "2023-12-01T00:00:00Z"}]}
        args = {"table": "storage_buildout_monthly", "variable": "battery_operating_mw", "aggregation": "max", "group_by": "year", "entity": "iso:ercot"}
        a = ercot.ErcotAsker.__new__(ercot.ErcotAsker)
        tagged = [a.tag("query", args, dict(q_out), 1), a.tag("compare", {"a": {**args, "group_by": None}, "b": args}, {"a": dict(one), "b": dict(q_out)}, 2)]
        results = [{"tool": "query", "input": args, "out": tagged[0], "is_error": False},
                   {"tool": "compare", "input": {"a": {k: v for k, v in args.items() if k != "group_by"}, "b": args}, "out": tagged[1], "is_error": False}]
        drafts = [
            {"answer": "x", "citations": CITE, "not_in_warehouse": False, "series": ["r1"], "followups": UPS},
            {"answer": "x", "citations": CITE, "not_in_warehouse": False, "series": ["r9", "r2a"], "followups": ["Only one?"]},
            {"answer": "x", "citations": CITE, "not_in_warehouse": False, "series": [], "followups": ["Why 9000 in 2021?", "And 30 MW?"]},
            {"answer": "x", "citations": CITE, "not_in_warehouse": False, "series": ["r1", "r2b", "r1"], "followups": UPS + ["Third?"]},
        ]
        py = []
        for d in drafts:
            rec = {**d, "status": "answered"}
            problems = a.extra_problems(d, results)
            a.finish(rec, results)
            py.append({"problems": problems, "series": rec["series"], "followups": rec["followups"]})
        js = node("const { ercotProfile } = await import('./lib/chat/ercot.ts');"
                  "const p = ercotProfile();"
                  f"const q = {json.dumps(q_out)}, one = {json.dumps(one)}, args = {json.dumps(args)};"
                  "const t1 = p.tag('query', args, { ...q }, 1), t2 = p.tag('compare', {}, { a: { ...one }, b: { ...q } }, 2);"
                  "const { group_by, ...flat } = args;"
                  "const results = [{ tool: 'query', input: args, out: t1, isError: false }, { tool: 'compare', input: { a: flat, b: args }, out: t2, isError: false }];"
                  f"const drafts = {json.dumps(drafts)};"
                  "console.log(JSON.stringify({ ids: [t1.result_id, t2.a.result_id, t2.b.result_id], out: drafts.map((d) => ({ problems: p.extraProblems(d, results), ...p.finish('answered', d, results) })) }));")
        self.assertEqual(js["ids"], ["r1", "r2a", "r2b"])
        self.assertEqual([tagged[0]["result_id"], tagged[1]["a"]["result_id"], tagged[1]["b"]["result_id"]], js["ids"])
        for i, (p, j) in enumerate(zip(py, js["out"])):
            self.assertEqual(p["problems"], j["problems"], f"draft {i}: the checks differ")
            self.assertEqual(p["followups"], j["followups"], f"draft {i}")
            self.assertEqual(json.loads(json.dumps(p["series"])), j["series"], f"draft {i}: the series differ")
        self.assertEqual(py[0]["problems"], [])
        self.assertEqual(len(py[1]["problems"]), 3)
        self.assertIn("9000", py[2]["problems"][0])
        self.assertTrue(py[2]["series"][0]["chosen_by"].startswith("default"))
        self.assertEqual(len(py[3]["series"]), 2)

    def test_a_view_opens_the_chat_with_its_settings_and_only_a_site_path_is_a_view(self):
        d = node("import { askHref, contextOf } from './lib/askContext.ts';"
                 "const c = { view: '/cost-of-power/battery', title: 'What a battery earns', settings: { grid: 'ERCOT', duration: '8 hours', empty: ' ' } };"
                 "const href = askHref(c, 'What did it earn?'); const sp = Object.fromEntries(new URL('http://x' + href).searchParams);"
                 "console.log(JSON.stringify({ href, back: contextOf(sp), none: contextOf({}), bad: contextOf({ from: 'https://evil.example/x' }), odd: contextOf({ from: '/a b' }),"
                 " cut: contextOf({ from: '/x', s_k: 'v'.repeat(200), title: 't'.repeat(200) }) }));", alias=False)
        self.assertTrue(d["href"].startswith("/ask/ercot?from=%2Fcost-of-power%2Fbattery&title="))
        self.assertIn("q=What+did+it+earn", d["href"])
        self.assertEqual(d["back"], {"view": "/cost-of-power/battery", "title": "What a battery earns", "settings": {"grid": "ERCOT", "duration": "8 hours"}})
        self.assertEqual((d["none"], d["bad"], d["odd"]), (None, None, None))
        self.assertEqual((len(d["cut"]["settings"]["k"]), len(d["cut"]["title"])), (60, 80))
        # the server cleans what it is sent again, and the sentence is the Python one's
        s = node("const e = await import('./lib/chat/ercot.ts');"
                 "const c = e.cleanContext({ view: '/shoulder', title: 'The shoulder hours', settings: { grid: 'ERCOT', month: '2025-01' }, other: 1 });"
                 "console.log(JSON.stringify({ c, line: e.contextLine(c), bad: e.cleanContext({ view: 'javascript:x' }), none: e.contextLine(null) }));")
        ctx = {"view": "/shoulder", "title": "The shoulder hours", "settings": {"grid": "ERCOT", "month": "2025-01"}}
        self.assertEqual(s["c"], ctx)
        self.assertEqual(s["line"], ercot.context_line(ctx))
        self.assertEqual((s["bad"], s["none"]), (None, ""))

    def test_the_page_is_in_review_and_a_live_page_shows_a_visitor_nothing_new(self):
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify({ a: statusOf('/ask/ercot'), b: statusOf('/ask'), c: statusOf('/cost-of-power/battery') }));", alias=False)
        self.assertEqual(d, {"a": "review", "b": "review", "c": "live"})
        link = src("site", "components", "AskErcotLink.tsx")
        self.assertIn('if (!internal && statusOf("/ask/ercot") !== "live") return null;', link)
        self.assertIn("prefetch={false}", link)   # the battery page promises that nothing typed is sent
        views = ["app/cost-of-power/battery/page.tsx", "app/cost-of-power/seller/page.tsx", "app/shoulder/page.tsx", "app/storage/buildout/page.tsx",
                 "app/storage/owners/page.tsx", "app/grid/[iso]/page.tsx", "app/explorer/ercot-peak-premium/page.tsx", "app/events/uri-2021/page.tsx"]
        for v in views:
            page = src("site", *v.split("/"))
            self.assertIn("<AskErcotLink context={{", page, v)
            self.assertNotRegex(page, r'href="/ask/ercot', f"{v} links Ask ERCOT outside the gated component")
        for v in views[:6]:
            if "peak-premium" in v or "uri-2021" in v:
                continue
            self.assertRegex(src("site", *v.split("/")), r'=== "ercot"( && \w+)? \? <AskErcotLink', f"{v}: the link is not kept to the ERCOT view")

    def test_the_general_chat_and_the_grid_chats_take_the_route_they_took(self):
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertIn('await ask(question.trim(), undefined, typeof grid === "string" && grid ? grid : null)', route)
        self.assertIn('profile === "ercot"', route)
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("profile ? profile.system : spec.system", loop)
        self.assertIn("profile ? profile.schema : spec.answer_schema", loop)
        self.assertIn("profile ? profile.effort : spec.effort", loop)
        self.assertIn("if (scope && !profile) {", loop)
        form = src("site", "app", "ask", "AskForm.tsx")
        self.assertNotIn("profile", form)
        self.assertNotIn("followups", form)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("tests/test_session92.py", "warehouse/chat/ercot.py", "warehouse/chat/eval/ercot_expected.py", "warehouse/chat/eval/ercot_eval.py",
                    "warehouse/chat/eval/questions_ercot.yaml"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
