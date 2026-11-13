"""Session 5251 (chain 238, Ask): the evaluation set widened to the whole platform, and the way it is asked.

Energy Research Warehouse (ERW). Session 5202 (chain 235) wrote the builder of a platform-wide set and stopped before it
ran; session 5251 ran it against the live set, corrected the keys that could not be computed at their source, and found
that the live set lacks whole days of its hourly tables (5 to 8 November 2026 among them). What these tests hold, with
no model and no network:

  the set      questions_platform.yaml: at least 120 questions over twelve areas and seven kinds, every key of the shape
               its kind asks, no figure keyed on a table held whole for a license, the keys file equal to the YAML
  the builder  scripts/ask_eval/platform_questions.py: a window's steps counted (a week of 168 hours, 169 over the end of
               daylight time), a gap refused once a row has arrived, a partial window refused once it is whole or empty
  the grader   eval_s1113.py grade_set: a window held in part is right only when the answer says so; a missing day is a
               refusal that names the day; a table not loaded into the live set is a refusal that says so
  the asking   eval_site.py: the run's files, this asking's cap added to the run's cost so far, the ids taken in order;
               the Node runner's own tests (site/scripts/test-eval-ask-site-loop.test.mjs)

The answers graded here are written by this file from the keys themselves: they are test inputs, not answers of the chat.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
SECTORS = ("power", "prices", "gas", "oil", "nuclear", "renewables", "storage", "transmission", "projects", "deals", "policy", "datacenters")
KINDS = ("figure", "hold", "pause", "not_live", "outside", "gap", "partial")
NIW = "not in the warehouse"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E = module("eval_s1113_for_5251", os.path.join(EVAL, "eval_s1113.py"))
S = module("eval_site_for_5251", os.path.join(EVAL, "eval_site.py"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "ask_eval"))
import platform_questions as P  # noqa: E402  no network at import


def the_set():
    return E.questions(os.path.join(EVAL, "questions_platform.yaml"))


def yes(v):
    return v in (True, "true", "True")


class TheSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qs = the_set()
        cls.by = {q["id"]: q for q in cls.qs}

    def test_at_least_120_questions_none_twice(self):
        self.assertGreaterEqual(len(self.qs), 120)
        self.assertEqual(len(self.by), len(self.qs))

    def test_twelve_areas_each_with_eight_or_more(self):
        n = {s: sum(1 for q in self.qs if q["sector"] == s) for s in SECTORS}
        self.assertEqual(sum(n.values()), len(self.qs), "a question names an area that is not one of the twelve")
        for s, c in n.items():
            self.assertGreaterEqual(c, 8, s)

    def test_seven_kinds_each_asked(self):
        n = {k: sum(1 for q in self.qs if q["kind"] == k) for k in KINDS}
        self.assertEqual(sum(n.values()), len(self.qs), "a question names a kind that is not one of the seven")
        for k, c in n.items():
            self.assertGreaterEqual(c, 2, k)
        self.assertGreaterEqual(n["figure"], 60)
        self.assertGreaterEqual(len(self.qs) - n["figure"], 40, "the questions the chat must not answer with a figure")

    def test_every_question_has_what_the_grader_reads(self):
        for q in self.qs:
            for k in ("id", "sector", "kind", "grid", "via", "question", "expected", "tolerance", "text", "tables", "refuse", "hold", "count", "note"):
                self.assertIn(k, q, f"{q['id']} {k}")
            self.assertIn(q["via"], ("general", "grid"))
            self.assertTrue(q["question"].endswith("?"), q["id"])
            self.assertIn(q["grid"], ("none", *E.GRID_SLUG), q["id"])
            if q["via"] == "grid":
                self.assertIn(q["grid"], E.GRID_SLUG, q["id"])

    def test_a_figure_key_has_a_figure_or_a_word_and_a_table(self):
        for q in self.qs:
            if q["kind"] != "figure":
                continue
            self.assertFalse(q["refuse"], q["id"])
            self.assertTrue(q["tables"], q["id"])
            self.assertTrue(len(q["expected"]) == 1 or q["text"], q["id"])
            for e in q["expected"]:
                self.assertIsInstance(e, (int, float), q["id"])
            self.assertEqual(q["tolerance"], 0.5 if q["expected"] and abs(q["expected"][0]) >= 1000 and q["id"] != "st04" else 0.01, q["id"])

    def test_no_figure_is_keyed_on_a_table_held_whole(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
        import license_hold as hold
        for q in self.qs:
            if q["kind"] in ("figure", "gap", "partial"):
                for t in q["tables"][:1]:
                    self.assertFalse(hold.license_needed(t) and hold.held_whole(t), f"{q['id']}: {t} is held whole")
        held = [q for q in self.qs if q["kind"] == "hold"]
        for q in held:
            self.assertTrue(q["tables"], q["id"])
            for t in q["tables"]:
                self.assertTrue(hold.license_needed(t), f"{q['id']}: {t} is not held")

    def test_a_refusal_key_has_no_figure_and_names_what_is_missing(self):
        for q in self.qs:
            if q["kind"] in ("figure", "partial"):
                continue
            self.assertTrue(q["refuse"], q["id"])
            self.assertEqual(q["expected"], [], q["id"])
            self.assertTrue(q["text"], q["id"])
            if q["kind"] == "hold":
                self.assertTrue(yes(q["hold"]), q["id"])
                self.assertIn("license needed", q["text"], q["id"])
            if q["kind"] == "pause":
                self.assertIn("paused", q["text"], q["id"])
            if q["kind"] in ("outside", "gap"):
                self.assertEqual(q["text"][0], NIW, q["id"])
                self.assertGreaterEqual(len(q["text"]), 2, f"{q['id']}: the missing thing is not named")
            if q["kind"] == "not_live":
                self.assertIn("live set", q["text"][0].split("|"), q["id"])
                self.assertGreaterEqual(len(q["text"]), 2, q["id"])

    def test_a_gap_names_its_day_and_a_partial_window_its_words(self):
        for q in self.qs:
            if q["kind"] == "gap":
                self.assertRegex(q["text"][1], r"\d{1,2} November\|", q["id"])
                self.assertIn("0 of ", q["note"], q["id"])
            if q["kind"] == "partial":
                self.assertFalse(q["refuse"], q["id"])
                self.assertEqual(q["expected"], [], q["id"])
                self.assertEqual(len(q["text"]), 1, q["id"])
                parts = q["text"][0].split("|")
                self.assertIn("missing", parts)
                self.assertNotIn("only", parts, "a bare 'only' would pass an answer that says nothing of the window")
                self.assertRegex(q["note"], r"\d+ of \d+ (steps held|hours|days)", q["id"])

    def test_the_keys_file_is_the_yaml(self):
        with open(os.path.join(EVAL, "keys_platform.json"), encoding="utf-8") as f:
            doc = json.load(f)
        self.assertRegex(doc["computed_at_utc"], r"^2026-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(sorted(doc["keys"]), sorted(self.by))
        for i, k in doc["keys"].items():
            q = self.by[i]
            for field in ("expected", "text", "tables", "note"):
                self.assertEqual(k[field], q[field], f"{i} {field}")
            self.assertEqual((k["sector"], k["kind"]), (q["sector"], q["kind"]), i)

    def test_no_dash_and_the_set_is_named(self):
        with open(os.path.join(EVAL, "questions_platform.yaml"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)
        self.assertEqual(os.path.basename(E.SETS["platform"]["questions"]), "questions_platform.yaml")
        with open(os.path.join(EVAL, "runs.json"), encoding="utf-8") as f:
            self.assertIn("keys_platform.json", json.load(f)["left_out"])


class TheBuilder(unittest.TestCase):
    def setUp(self):
        self.series, self.held = P.series, P.L.held
        P.L.held = lambda table, grid=None: table == "a_held_table"

    def tearDown(self):
        P.series, P.L.held = self.series, self.held

    def a_set(self):
        s = object.__new__(P.Set)
        s.qs, s.failed = [], []
        s.cat = {"t": {"in_live_set": "yes"}, "a_held_table": {"in_live_set": "yes"}, "not_loaded": {"in_live_set": "no"}}
        return s

    def test_the_windows_have_the_hours_the_clocks_give(self):
        P.series = lambda *a: []
        self.assertEqual(P.steps("t", "e", "v", P.WEEK, P.CT, 60), (0, 168))
        self.assertEqual(P.steps("t", "e", "v", P.GAP_WEEK, P.CT, 60), (0, 168))
        self.assertEqual(P.steps("t", "e", "v", ("2026-10-26", "2026-11-02"), P.CT, 60), (0, 169), "the week daylight time ends in")
        self.assertEqual(P.steps("t", "e", "v", P.DAY, P.PT, 15), (0, 96))
        self.assertEqual(P.steps("t", "e", "v", P.DAY, P.PT, 5), (0, 288))
        self.assertEqual(P.steps("t", "e", "v", P.GAP_DAY, P.UTC, 1440), (0, 1))

    def test_the_steps_held_are_distinct_times(self):
        P.series = lambda *a: [("2026-11-10T06:00:00+00:00", 1.0), ("2026-11-10T06:00:00+00:00", 2.0), ("2026-11-10T07:00:00+00:00", 3.0)]
        self.assertEqual(P.steps("t", "e", "v", P.DAY, P.CT, 60), (2, 24))

    def test_the_day_and_the_week_are_asked_in_words_that_match_them(self):
        self.assertEqual(P.DAY, ("2026-11-10", "2026-11-11"))
        self.assertIn("10 November 2026", P.DAY_WORDS)
        self.assertEqual(P.WEEK, ("2026-10-19", "2026-10-26"))
        self.assertIn("19 to Sunday 25 October 2026", P.WEEK_WORDS)
        self.assertIn("2 to Sunday 8 November 2026", P.GAP_WEEK_WORDS)

    def test_a_gap_is_a_key_only_while_no_row_of_the_day_is_held(self):
        s = self.a_set()
        P.series = lambda table, entity, variable, lo, hi: [] if lo.startswith("2026-11") else [("2026-10-13T00:00:00+00:00", 1.0)]
        s.gap("g1", "power", "ERCOT", "general", "q?", "t", "e", "v", P.GAP_DAY, P.CT, 60, [NIW, "6 November"], "t, e, v")
        self.assertEqual((len(s.qs), s.failed), (1, []))
        self.assertTrue(s.qs[0]["refuse"])
        self.assertEqual(s.qs[0]["kind"], "gap")
        self.assertIn("0 of 24 steps held", s.qs[0]["note"])
        P.series = lambda *a: [("2026-11-06T07:00:00+00:00", 1.0)]
        s.gap("g2", "power", "ERCOT", "general", "q?", "t", "e", "v", P.GAP_DAY, P.CT, 60, [NIW, "6 November"], "t, e, v")
        self.assertEqual(len(s.qs), 1)
        self.assertIn("the gap is filled", s.failed[0])

    def test_a_gap_is_not_written_for_a_series_that_is_missing_whole(self):
        s = self.a_set()
        P.series = lambda *a: []
        s.gap("g1", "power", "ERCOT", "general", "q?", "t", "e", "v", P.GAP_DAY, P.CT, 60, [NIW, "6 November"], "t, e, v")
        self.assertEqual(s.qs, [])
        self.assertIn("the series itself is missing", s.failed[0])

    def test_a_partial_window_is_a_key_only_while_it_is_held_in_part(self):
        hours = [(f"2026-11-0{d}T{h:02d}:00:00+00:00", 1.0) for d in (2, 3, 4) for h in range(24)]
        for rows, ok in ((hours, True), ([], False)):
            s = self.a_set()
            P.series = lambda *a, rows=rows: rows
            s.partial("p1", "power", "ERCOT", "general", "q?", "t", "e", "v", P.GAP_WEEK, P.UTC, 60, "t, e, v")
            self.assertEqual(len(s.qs), 1 if ok else 0)
            if ok:
                self.assertIn("72 of 168 steps held", s.qs[0]["note"])
                self.assertFalse(s.qs[0]["refuse"])
            else:
                self.assertIn("not held in part", s.failed[0])

    def test_a_month_s_row_is_partial_by_the_table_s_own_count(self):
        self.assertEqual((P.month_steps("2026-10", "hours"), P.month_steps("2026-10", "days"), P.month_steps("2026-09", "hours"), P.month_steps("2026-02", "days")),
                         (744, 31, 720, 28))
        keep = P.L.month_value
        try:
            for held, ok in ((48.0, True), (744.0, False), (0.0, False)):
                P.L.month_value = lambda table, entity, variable, month, held=held: held
                s = self.a_set()
                s.partial_row("p1", "prices", "CAISO", "general", "q?", "t", "e", "2026-10", "da_hours", "hours", "t, e, the 2026-10 row")
                self.assertEqual(len(s.qs), 1 if ok else 0, held)
                if ok:
                    self.assertEqual((s.qs[0]["kind"], s.qs[0]["expected"], s.qs[0]["refuse"]), ("partial", [], False))
                    self.assertIn("da_hours says 48 of 744 hours", s.qs[0]["note"])
                else:
                    self.assertIn("not held in part", s.failed[0])
            P.L.month_value = lambda *a: 31.0
            self.assertTrue(P.whole_month("t", "e", "2026-08", "days_held"))
            P.L.month_value = lambda *a: 27.0
            with self.assertRaises(SystemExit):
                P.whole_month("t", "e", "2026-08", "days_held")
        finally:
            P.L.month_value = keep

    def test_no_gap_or_partial_key_on_a_held_or_unloaded_table(self):
        P.series = lambda *a: []
        for table in ("a_held_table", "not_loaded", "unknown"):
            s = self.a_set()
            s.gap("g1", "power", "none", "general", "q?", table, "e", "v", P.GAP_DAY, P.UTC, 60, [NIW, "6 November"], "n")
            s.partial("p1", "power", "none", "general", "q?", table, "e", "v", P.GAP_WEEK, P.UTC, 60, "n")
            self.assertEqual((s.qs, len(s.failed)), ([], 2), table)

    def test_a_figure_key_is_refused_for_a_table_the_live_set_does_not_hold(self):
        s = self.a_set()
        s.figure("f1", "power", "none", "general", "q?", "not_loaded", 1.0, "n")
        self.assertEqual(s.qs, [])
        self.assertIn("not in the live set", s.failed[0])


def answered(text, table):
    return {"status": "answered", "answer": text, "citations": [{"table": table, "source_report": "r", "data_version": "v"}], "trace": [], "cost_usd": 0.0}


def refused(text):
    return {"status": "not_in_warehouse", "not_in_warehouse": True, "answer": text, "citations": [], "trace": [], "cost_usd": 0.0}


class TheGrader(unittest.TestCase):
    """grade_set on the set's own keys, with answers written here (the figure of a right answer is the key's own)."""

    @classmethod
    def setUpClass(cls):
        cls.by = {q["id"]: q for q in the_set()}

    def grade(self, answers):
        with tempfile.TemporaryDirectory() as d:
            run, grades = os.path.join(d, "run.json"), os.path.join(d, "grades.json")
            with open(run, "w", encoding="utf-8") as f:
                json.dump({"questions": [{"id": i, **a} for i, a in answers.items()]}, f)
            keep = dict(E.SETS["platform"])
            E.SETS["platform"]["run"], E.SETS["platform"]["grades"] = run, grades
            try:
                doc = E.grade_set("platform", E.G.RULES_5201)
            finally:
                E.SETS["platform"].update(keep)
        return doc, {r["id"]: r for r in doc["questions"]}

    def test_a_window_held_in_part(self):
        t = self.by["pt01"]["tables"][0]
        for text, right in ((f"The warehouse holds only part of that week: 5 to 8 November are missing from {t}. Over the hours held the highest was read from {t}.", True),
                            (f"That week is incomplete in {t}, so no maximum of the whole week can be given.", True),
                            (f"The highest hourly demand that week was read from {t}.", False),
                            (f"Only ERCOT was asked for. The highest hourly demand that week was read from {t}.", False)):
            _, g = self.grade({"pt01": answered(text, t)})
            self.assertEqual(g["pt01"]["ok"], right, text)
        _, g = self.grade({"pt01": refused("Not in the warehouse: the week of 2 to 8 November is not held whole, 96 hours of it are missing.")})
        self.assertTrue(g["pt01"]["ok"], "a refusal that says the window is not whole is right too")
        _, g = self.grade({"pt01": refused("Not in the warehouse.")})
        self.assertFalse(g["pt01"]["ok"])

    def test_a_day_the_series_lacks(self):
        _, g = self.grade({"gp01": refused("That figure is not in the warehouse: eia930_all_demand holds no row of ERCOT's demand for 6 November 2026.")})
        self.assertTrue(g["gp01"]["ok"])
        _, g = self.grade({"gp01": refused("That figure is not in the warehouse.")})
        self.assertFalse(g["gp01"]["ok"], "the day is not named")
        _, g = self.grade({"gp01": answered("ERCOT's average hourly demand on 6 November 2026 was read from eia930_all_demand.", "eia930_all_demand")})
        self.assertFalse(g["gp01"]["ok"], "an answer where a refusal is due")

    def test_a_figure_and_its_refusal(self):
        q = self.by["pw01"]
        v = q["expected"][0]
        _, g = self.grade({"pw01": answered(f"ERCOT's average hourly demand on 10 November 2026 was {v:,.2f} MW ({q['tables'][0]}).", q["tables"][0])})
        self.assertTrue(g["pw01"]["ok"])
        _, g = self.grade({"pw01": answered(f"ERCOT's average hourly demand on 10 November 2026 was {v * 1.02:,.2f} MW ({q['tables'][0]}).", q["tables"][0])})
        self.assertFalse(g["pw01"]["ok"])
        _, g = self.grade({"pw01": refused("That figure is not in the warehouse.")})
        self.assertFalse(g["pw01"]["ok"])

    def test_a_held_table_and_a_table_not_loaded(self):
        _, g = self.grade({"po01": refused("The policy table is license needed: its rows are held until a license is recorded.")})
        self.assertTrue(g["po01"]["ok"])
        _, g = self.grade({"po01": answered("The policy table records 212 actions for October 2026 (policy_actions).", "policy_actions")})
        self.assertFalse(g["po01"]["ok"], "a count of a held table")
        _, g = self.grade({"pw12": refused("Not in the warehouse the chat reads: retail electricity prices are a table of the record that is not loaded into the live set.")})
        self.assertTrue(g["pw12"]["ok"])
        _, g = self.grade({"pw12": refused("That figure is not in the warehouse.")})
        self.assertFalse(g["pw12"]["ok"], "the refusal does not say the table is of the record and not loaded")

    def a_held_grid_answer(self, extra=""):
        """The answer the loop is built to give a held grid's question: the hold's words, the grid, the public grids' figures."""
        rec = answered("NYISO's rows are held for a license (license needed). For the public grids, the day-ahead mean was 41.92 USD/MWh at ERCOT's hub average "
                       f"and 36.5042 USD/MWh at CAISO's SP15 (iso_trader_daily).{extra}", "iso_trader_daily")
        rec["trace"] = [{"tool": "query", "input": {"table": "iso_trader_daily", "entity": "nyiso:N.Y.C."}, "isError": False, "is_error": False,
                         "out": {"held": True, "grid": "NYISO", "public_grids": [{"grid": "ERCOT", "entity": "ercot:HB_HUBAVG", "value": 41.9229},
                                                                                  {"grid": "CAISO", "entity": "caiso:TH_SP15_GEN-APND", "value": 36.5042}]}}]
        return rec

    def grade_under(self, answers, rules):
        with tempfile.TemporaryDirectory() as d:
            run, grades = os.path.join(d, "run.json"), os.path.join(d, "grades.json")
            with open(run, "w", encoding="utf-8") as f:
                json.dump({"questions": [{"id": i, **a} for i, a in answers.items()]}, f)
            keep = dict(E.SETS["platform"])
            E.SETS["platform"]["run"], E.SETS["platform"]["grades"] = run, grades
            try:
                return {r["id"]: r for r in E.grade_set("platform", rules)["questions"]}
            finally:
                E.SETS["platform"].update(keep)

    def test_a_held_grid_answered_with_the_public_grids_figures(self):
        self.assertEqual(E.G.RULES_5251, E.G.RULES_5201 + ("hold_public_grids",))
        right = self.a_held_grid_answer()
        self.assertTrue(self.grade_under({"pr11": right}, E.G.RULES_5251)["pr11"]["ok"])
        self.assertFalse(self.grade_under({"pr11": right}, E.G.RULES_5201)["pr11"]["ok"], "the gradings before this session are what they were")
        # a figure the record does not place among the public grids' is not met, whatever the words
        self.assertFalse(self.grade_under({"pr11": self.a_held_grid_answer(" Zone J itself averaged 58.31 USD/MWh.")}, E.G.RULES_5251)["pr11"]["ok"])
        # figures with no held answer in the record
        bare = self.a_held_grid_answer()
        bare["trace"] = []
        self.assertFalse(self.grade_under({"pr11": bare}, E.G.RULES_5251)["pr11"]["ok"])
        # the hold's words are still asked for
        mute = self.a_held_grid_answer()
        mute["answer"] = mute["answer"].replace("license needed", "a license")
        self.assertFalse(self.grade_under({"pr11": mute}, E.G.RULES_5251)["pr11"]["ok"])
        # and a refusal in the hold's words with no figure is right under either
        plain = refused("NYISO's rows are held for a license: license needed.")
        for rules in (E.G.RULES_5201, E.G.RULES_5251):
            self.assertTrue(self.grade_under({"pr11": plain}, rules)["pr11"]["ok"])

    def test_a_table_held_whole_gains_nothing_from_the_rule(self):
        leak = answered("The policy table is license needed. It records 212.5 actions (policy_actions).", "policy_actions")
        self.assertFalse(self.grade_under({"po01": leak}, E.G.RULES_5251)["po01"]["ok"])

    def test_the_counts_by_kind_and_area(self):
        doc, _ = self.grade({"pt01": refused("Not in the warehouse."), "gp01": refused("Not in the warehouse: no row of 6 November 2026 is held."),
                             "po01": refused("license needed")})
        c = S.counts(doc["questions"], list(self.by.values()))
        self.assertEqual(c["by_kind"], {"hold": {"asked": 1, "right": 1}, "gap": {"asked": 1, "right": 1}, "partial": {"asked": 1, "right": 0}})
        self.assertEqual(c["by_sector"]["power"], {"asked": 2, "right": 1})


class TheAsking(unittest.TestCase):
    def test_the_files_are_named_by_session_and_set(self):
        f = S.files("5251", "platform")
        self.assertEqual(os.path.basename(f["run"]), "eval_s5251_site_platform_run.json")
        self.assertEqual(os.path.basename(f["grades"]), "eval_s5251_site_platform_grades.json")
        self.assertEqual(os.path.basename(E.SETS["platform"]["run"]), os.path.basename(f["run"]))

    def test_the_run_s_cost_so_far(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "run.json")
            self.assertEqual(S.spent(p), (0.0, 0))
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"questions": [{"id": "a", "cost_usd": 0.0712}, {"id": "b", "cost_usd": None}, {"id": "c", "cost_usd": 0.1}]}, f)
            self.assertEqual(S.spent(p), (0.1712, 3))

    def test_the_ids_an_asking_takes(self):
        qs = [{"id": i} for i in ("a", "b", "c", "d", "e")]
        self.assertEqual(S.asking(qs, {"a", "c"}), ["b", "d", "e"])
        self.assertEqual(S.asking(qs, {"a", "c"}, first=2), ["b", "d"])
        self.assertEqual(S.asking(qs, {"a", "c"}, only=["c", "e"]), ["c", "e"], "a named question is asked again")
        self.assertEqual(S.asking(qs, set()), ["a", "b", "c", "d", "e"])

    def test_the_runner_is_handed_the_session_s_cap_and_the_questions_due(self):
        cmd = S.node_command("q.json", "run.json", 2, ["pw03", "pw05"], "a label")
        self.assertEqual(cmd[:4], ["node", "--import", "./scripts/eval-register.mjs", "scripts/eval-ask-site-loop.mjs"])
        self.assertEqual(cmd[cmd.index("--cap") + 1], "2.0000")
        self.assertEqual(cmd[cmd.index("--only") + 1], "pw03,pw05")
        self.assertNotIn("--no-ledger", cmd)
        cmd = S.node_command("q.json", "run.json", 2, ["pw01"], "l", ledger=False, dry_run=True)
        self.assertIn("--no-ledger", cmd)
        self.assertIn("--dry-run", cmd)

    def test_a_session_s_asking_is_its_own_run_and_no_question_is_asked_twice(self):
        by = {q["id"]: q for q in the_set()}
        v = by["pw01"]["expected"][0]
        t = by["pw01"]["tables"][0]
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual((S.sessions_of("platform", d), S.asked_ids("platform", d)), ([], set()))
            first = {"questions": [{"id": "pw01", **answered(f"It was {v * 1.5:,.2f} MW ({t}).", t)}, {"id": "po01", **refused("license needed")}]}
            second = {"questions": [{"id": "pw01", **answered(f"It was {v:,.2f} MW ({t}).", t)}, {"id": "gp01", **refused("Not in the warehouse.")}]}
            for s, doc in (("5300", first), ("5299", second), ("10001", {"questions": []})):
                with open(S.files(s, "platform", d)["run"], "w", encoding="utf-8") as f:
                    json.dump(doc, f)
            with open(os.path.join(d, "eval_s5299_site_other_run.json"), "w", encoding="utf-8") as f:
                json.dump({"questions": [{"id": "zz99"}]}, f)
            self.assertEqual(S.sessions_of("platform", d), ["5299", "5300", "10001"], "by number, and the set's own runs only")
            self.assertEqual(S.asked_ids("platform", d), {"pw01", "po01", "gp01"})
            rows = S.grade_all(E, "platform", list(by.values()), E.G.RULES_5251, d)
            got = {r["id"]: (r["session"], r["ok"]) for r in rows}
            self.assertEqual(got, {"pw01": ("5300", False), "po01": ("5300", True), "gp01": ("5299", False)}, "a question's newest answer stands")
            self.assertEqual([r["id"] for r in rows], ["pw01", "po01", "gp01"], "in the set's order")
            for s in ("5299", "5300"):
                with open(S.files(s, "platform", d)["grades"], encoding="utf-8") as f:
                    g = json.load(f)
                self.assertEqual((g["loop"], g["asked"], g["rules"]), ("site", 2, list(E.G.RULES_5251)))
                self.assertIn("by_kind", g)
        self.assertEqual(os.path.basename(E.SETS["platform"]["run"]), "eval_s5251_site_platform_run.json", "the set's own paths are put back")

    def test_the_two_halves_each_cover_every_area_and_kind(self):
        qs = the_set()
        a, b = S.slices(qs)
        by = {q["id"]: q for q in qs}
        self.assertEqual(sorted(a + b), sorted(by))
        self.assertEqual(set(a) & set(b), set())
        self.assertLessEqual(abs(len(a) - len(b)), 16)
        for part in (a, b):
            self.assertEqual({by[i]["sector"] for i in part}, set(SECTORS))
        self.assertEqual({by[i]["kind"] for i in a}, set(KINDS))
        self.assertEqual({by[i]["kind"] for i in b}, set(KINDS) - {"gap", "partial"}, "the days and months held in part are all asked in the first half")
        # the rule itself: an odd number is in a, an even one in b, whatever the kind; a gap or a partial window is in a
        self.assertIn("pw01", a)
        self.assertIn("pw02", b)
        self.assertEqual(S.slices([{"id": "x01", "sector": "s", "kind": "figure"}, {"id": "x02", "sector": "t", "kind": "outside"}, {"id": "x03", "sector": "t", "kind": "figure"},
                                   {"id": "x04", "sector": "t", "kind": "partial"}, {"id": "g01", "sector": "s", "kind": "gap"}, {"id": "g02", "sector": "s", "kind": "gap"}]),
                         (["x01", "x03", "x04", "g01", "g02"], ["x02"]))

    def test_every_run_of_the_set_is_named_and_is_a_row_of_the_history(self):
        sessions = S.sessions_of("platform")
        self.assertIn("5251", sessions)
        with open(os.path.join(EVAL, "runs.json"), encoding="utf-8") as f:
            named = {r["file"]: r for r in json.load(f)["runs"]}
        with open(os.path.join(ROOT, "docs", "reviews", "ask-history.md"), encoding="utf-8") as f:
            history = [line for line in f.read().split("\n") if line.startswith("| 2026-") and "`questions_platform.yaml`" in line]
        self.assertEqual(len(history), len(sessions))
        for s in sessions:
            e = S.entry(s, "platform", "questions_platform.yaml")
            self.assertEqual(named.get(e["file"]), e, f"session {s}'s run is not named as eval_site.py names it")
            self.assertTrue(os.path.exists(os.path.join(EVAL, e["grades"])), s)
            with open(os.path.join(EVAL, e["file"]), encoding="utf-8") as f:
                run = json.load(f)
            for q in run["questions"]:
                self.assertEqual(q["loop"], "site", f"{s} {q['id']}")
                self.assertIsNone(q["error"], f"{s} {q['id']}: an error is in the stored run")
            self.assertLessEqual(round(sum(float(q["cost_usd"] or 0) for q in run["questions"]), 4), 2.0, f"session {s} spent more than USD 2")

    def test_the_review_file_s_scores_are_the_runs(self):
        r = subprocess.run([sys.executable, os.path.join(EVAL, "platform_scores.py"), "--check"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-500:] + (r.stderr or "")[-1500:])
        PS = module("platform_scores_for_5251", os.path.join(EVAL, "platform_scores.py"))
        qs = [{"id": "pw01", "sector": "power", "kind": "figure"}, {"id": "pw02", "sector": "power", "kind": "outside"}, {"id": "ga01", "sector": "gas", "kind": "figure"}]
        rec = lambda i, calls, cost, retried=False: {"id": i, "tool_calls": calls, "cost_usd": cost, "retried": retried, "status": "answered"}
        grade = lambda i, ok, **g: {"id": i, "ok": ok, "grade": {"ok": ok, **g}}
        runs = [("5300", [rec("pw01", 12, 0.2), rec("pw02", 3, 0.05)], {"pw01": grade("pw01", False, number=False, table=True), "pw02": grade("pw02", True)}),
                ("5301", [rec("pw01", 4, 0.1, True)], {"pw01": grade("pw01", True)})]
        text = PS.text(qs, runs)
        self.assertIn("**Asked: 2 of 3. Right: 2. Cost: USD 0.35.**", text, "a question asked again counts once, its newest answer standing; its cost counts each time")
        self.assertIn("| 5300 | 2 | 1 | USD 0.25 | 7.5, 12 | 1 | 0 |", text)
        self.assertIn("| 5301 | 1 | 1 | USD 0.10 | 4, 4 | 0 | 1 |", text)
        self.assertIn("| figure | 2 | 1 | 1 |", text)
        self.assertIn("| gas | 1 | 0 | 0 |", text)
        self.assertIn("- None.", text)
        wrong = PS.text(qs, runs[:1])
        self.assertIn("- `pw01` (figure, power; session 5300; status `answered`, 12 calls): not met: number.", wrong)
        doc = f"a\n{PS.BEGIN}\nold\n{PS.END}\nz\n"
        self.assertEqual(PS.placed(doc, text), f"a\n{text}\nz\n")
        with self.assertRaises(SystemExit):
            PS.placed("no markers", text)

    def test_no_question_is_in_two_runs_unless_asked_again_by_name(self):
        seen = {}
        for s in S.sessions_of("platform"):
            with open(S.files(s, "platform")["run"], encoding="utf-8") as f:
                for q in json.load(f)["questions"]:
                    seen.setdefault(q["id"], []).append(s)
        by = {q["id"]: q for q in the_set()}
        self.assertEqual(set(seen) - set(by), set(), "a run holds a question the set does not")
        # a question asked twice is one a later session named after a fix: its sessions are in order and differ
        for i, ss in seen.items():
            self.assertEqual(len(ss), len(set(ss)), i)

    def test_a_run_is_named_once_in_the_list(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "runs.json")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write('{\n "_about": "x",\n "runs": [\n  {\n   "file": "a_run.json"\n  }\n ],\n "left_out": {}\n}\n')
            self.assertTrue(S.register("5300", "platform", "questions_platform.yaml", p))
            self.assertFalse(S.register("5300", "platform", "questions_platform.yaml", p), "named twice")
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual([r["file"] for r in doc["runs"]], ["a_run.json", "eval_s5300_site_platform_run.json"])
            self.assertEqual(doc["runs"][1], S.entry("5300", "platform", "questions_platform.yaml"))

    def test_a_key_is_never_sent_to_the_asking(self):
        with open(os.path.join(EVAL, "eval_site.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('for k in ("id", "grid", "via", "question")', src)

    def test_the_runner_stops_on_an_error_and_numbers_its_questions(self):
        with open(os.path.join(ROOT, "site", "scripts", "eval-ask-site-loop.mjs"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('if (error && !flag("--keep-going"))', src)
        self.assertIn('questionId: crypto.randomBytes(16).toString("hex")', src)
        self.assertIn('step: "site_ask_eval"', src)
        self.assertIn("delete process.env.SUPABASE_SERVICE_KEY", src)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_runner_s_own_tests(self):
        r = subprocess.run(["node", "--test", "scripts/test-eval-ask-site-loop.test.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-500:])


if __name__ == "__main__":
    unittest.main()
