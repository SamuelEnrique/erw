"""Session 6113 (chain 280): a visitor's chat and the tables it cannot reach; a table of the record the catalogue does
not list; a bill's number is a name.

Energy Research Warehouse (ERW).

The week's new tables are in no copy a visitor's chat reads (14 November 2026): the three large-load research tables'
license is not settled, and the forecast tool's parameters are not loaded. The same 58 questions are keyed twice: as the
table answers them (questions_newtables.yaml, asked through the Python loop over the tables' files: 58 of 58 once the
grader read a bill's number as a name and one answer's form is taken as below), and as a visitor's chat can answer them
on the day (questions_newtables_live.yaml, kind not_readable: a refusal, no figure, and never the figure the table
holds; a slice asked through the site's loop: 6 of 6, three of them at the limit of 12 tool calls).

No model, no network.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import tools  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E = module("eval_s1113_for_6113", os.path.join(EVAL, "eval_s1113.py"))


class ATableOfTheRecordNotListed(unittest.TestCase):
    def test_the_license_records_word(self):
        self.assertEqual(tools.verdict_of("utility_large_load_rules"), "unsettled")
        self.assertEqual(tools.verdict_of("forecast_tool_parameters"), "public")
        self.assertIsNone(tools.verdict_of("no_such_table_anywhere"))

    def test_the_words_say_what_it_is_and_how_to_answer(self):
        held = tools.not_listed_words("utility_large_load_rules", "unsettled")
        self.assertTrue(held.startswith("table utility_large_load_rules is not in this site's live set: it is a table of the ERW's record whose license is not settled (license needed)"))
        self.assertIn("never answer for utility_large_load_rules from a table that holds something else", held)
        new = tools.not_listed_words("forecast_tool_parameters", "public")
        self.assertIn("is a table of the ERW's record that is not loaded here", new)
        self.assertNotIn("license needed", new)
        for w in (held, new):
            self.assertNotIn("Redivis", w)

    def test_the_loop_counts_it_refused_whole(self):
        import ask
        w = tools.not_listed_words("utility_large_load_rules", "unsettled")
        self.assertEqual(ask.refused_whole(w, ["utility_large_load_rules"]), "utility_large_load_rules")
        self.assertTrue(ask.refused_read(w))
        # not a held table in the loop's sense: the hold's sentence is for a table refused as license needed by name
        self.assertEqual(ask.held_tables({"utility_large_load_rules": w}), [])

    def test_only_a_backend_that_reads_the_live_set_says_so(self):
        py = open(os.path.join(ROOT, "warehouse", "chat", "tools.py"), encoding="utf-8").read()
        self.assertIn("if live_only() and verdict_of(name):", py)
        self.assertIn('**({"not_listed": NOT_LISTED_NOTE} if live_only() else {}),', py)

    def test_the_site_says_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        register = "./scripts/alias-register.mjs"
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            other = os.environ.get("ERW_NODE_MODULES_SITE") or os.path.join(os.path.dirname(ROOT), "erw", "site")
            if not os.path.isdir(os.path.join(other, "node_modules")) or not os.path.exists(os.path.join(SITE, "scripts", "eval-register.mjs")):
                raise unittest.SkipTest("the site's packages are not installed in this copy")
            register = "./scripts/eval-register.mjs"
        r = subprocess.run([exe, "--import", register, "scripts/test-ask-6113.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        got = json.loads(next(x for x in r.stdout.splitlines() if x.startswith("{")))
        self.assertEqual(got["unsettled"], tools.not_listed_words("utility_large_load_rules", "unsettled"))
        self.assertEqual(got["internal"], tools.not_listed_words("large_load_waits", "internal"))
        self.assertEqual(got["public"], tools.not_listed_words("forecast_tool_parameters", "public"))
        self.assertEqual(got["note"], tools.NOT_LISTED_NOTE)


class AVisitorsChatToday(unittest.TestCase):
    KEY = {"text": ["not in the warehouse|license needed|live set|Redivis|not loaded"], "withheld": "[52.0]", "withheld_text": "[]", "tolerance": 0.01}

    def grade(self, answer, status="not_in_warehouse", key=None):
        return E.not_readable_grade(key or self.KEY, {"answer": answer, "status": status})

    def test_a_refusal_with_no_figure_is_right(self):
        self.assertTrue(self.grade("Not in the warehouse this chat reads: utility_large_load_rules is not loaded. Checked on 14 November 2026.")["ok"])
        self.assertTrue(self.grade("License needed: the table's license is not settled, as of 2026-11-14.")["ok"])

    def test_the_tables_own_figure_is_never_right(self):
        g = self.grade("Not in the warehouse, though I believe 52 are in effect.")
        self.assertEqual((g["ok"], g["not_stated"]), (False, False))
        self.assertFalse(self.grade("52 rules are in effect.", status="answered")["ok"])

    def test_a_withheld_name_or_date_is_looked_for_and_a_status_word_is_not(self):
        named = dict(self.KEY, withheld="[]", withheld_text='["Duke Energy Florida"]')
        self.assertFalse(self.grade("Not in the warehouse. It is Duke Energy Florida's, I think.", key=named)["ok"])
        self.assertTrue(self.grade("Not in the warehouse: the rules table is not loaded.", key=named)["ok"])
        L = module("newtables_questions_for_6113", os.path.join(ROOT, "scripts", "ask_eval", "newtables_questions.py"))
        self.assertIn("proposed", L.STATUS_WORDS)
        self.assertIn("in effect", L.STATUS_WORDS)

    def test_the_days_set_refuses_every_question_of_a_table_out_of_reach(self):
        qs = E.questions(E.SETS["newtables_live"]["questions"])
        own = {q["id"]: q for q in E.questions(E.SETS["newtables"]["questions"])}
        self.assertEqual([q["id"] for q in qs], list(own))
        for q in qs:
            self.assertIn(q["kind"], ("not_readable", "outside", "figure", "unstated"), q["id"])
            if q["kind"] == "not_readable":
                self.assertEqual((q["expected"], str(q["refuse"]).lower()), ([], "true"), q["id"])
                self.assertEqual(json.loads(q["withheld"]), own[q["id"]]["expected"], q["id"])

    def test_the_slice_asked_through_the_sites_loop(self):
        run = json.load(open(os.path.join(EVAL, "eval_s6113_site_newtables_live_run.json"), encoding="utf-8"))["questions"]
        grades = {g["id"]: g for g in json.load(open(os.path.join(EVAL, "eval_s6113_site_newtables_live_grades.json"), encoding="utf-8"))["questions"]}
        self.assertEqual(len(run), 6)
        self.assertTrue(all(q["status"] == "not_in_warehouse" for q in run))
        self.assertTrue(all(grades[q["id"]]["ok"] for q in run))
        self.assertEqual(sorted(q["id"] for q in run if q["tool_calls"] == 12), ["fc06", "ru07", "ru09"])   # the cost this session's mend is for


class ABillsNumberIsAName(unittest.TestCase):
    KEY = {"text": ["not published|not state|not stated|no effective date|not in the warehouse"]}

    def test_the_stored_answer_of_lw09(self):
        run = json.load(open(os.path.join(EVAL, "eval_s6112_loop_newtables_run.json"), encoding="utf-8"))["questions"]
        a = next(q for q in run if q["id"] == "lw09")
        self.assertIn("H.F. 2690", a["answer"])
        self.assertTrue(E.unstated_grade(self.KEY, a)["ok"])

    def test_identifiers_of_bills_acts_and_dockets(self):
        for name in ("H.F. 2690 (successor to H.F. 2447)", "S.B. 4", "SB 270", "H.B. 1834", "A. 796", "Act 2026-610", "Docket 25-055-P", "Public Act 207", "Chapter 353", "No. 3061", "H 911"):
            self.assertTrue(E.unstated_grade(self.KEY, {"answer": f"Not published: the table reads {name} and states no date."})["ok"], name)

    def test_a_figure_is_still_a_figure(self):
        for wrong in ("Not published, though news reports put the pipeline at 15.4 GW.", "Not published. H.F. 2690 covers 12,500 MW.", "Not published; it applies from 100 MW."):
            self.assertFalse(E.unstated_grade(self.KEY, {"answer": wrong})["ok"], wrong)


if __name__ == "__main__":
    unittest.main()
