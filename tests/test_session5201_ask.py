"""Session 5201 (chain 235, Ask): the faults file's open rows.

Energy Research Warehouse (ERW). docs/reviews/ask-faults-2026-11-05.md gives every row a state; the two answers of the
second thirty still graded wrong in its newest asking (t09, f09) are met by the grader's rules, with no model:

  t09   the right figure read from another table that holds it: the rule table_by_evidence of session 2223
  f09   a negative difference written as its magnitude with the direction in words: the rule sign_in_words of this
        session (eval_s267.py RULES_5201)

No stored grading is changed: the rule only adds, and a grading made under RULES_2223 is what it was.
"""
import importlib.util
import json
import os
import re
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = module("eval_s267_for_5201", os.path.join(EVAL, "eval_s267.py"))


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


def key(expected, tolerance=0.5):
    return {"expected": expected, "tolerance": tolerance, "text": [], "tables": [], "refuse": False}


def body(answer):
    return {"answer": answer, "citations": [{"table": "t", "source_report": "r", "data_version": "v"}], "status": "answered"}


class TheRule(unittest.TestCase):
    def test_the_rules_are_the_2223_rules_and_one_more(self):
        self.assertEqual(G.RULES_2223, ("refusal_no_table", "table_by_evidence"))
        self.assertEqual(G.RULES_5201, G.RULES_2223 + ("sign_in_words",))

    def test_a_negative_difference_in_words(self):
        for words in ("The difference is 3,369.62 USD/MW less at ERCOT.", "ERCOT was 3,369.62 USD/MW lower than CAISO.",
                      "ERCOT stood 3,369.62 USD/MW below CAISO.", "Revenue fell by 3,369.62 USD/MW.", "The spread was minus 3,369.62."):
            self.assertFalse(G.grade(key([-3369.6241]), body(words), G.RULES_2223)["ok"], words)
            self.assertTrue(G.grade(key([-3369.6241]), body(words), G.RULES_5201)["ok"], words)

    def test_the_sign_written_is_met_as_before(self):
        self.assertTrue(G.grade(key([-3369.6241]), body("The difference is -3,369.62 USD/MW."), G.RULES_2223)["ok"])

    def test_no_word_of_the_direction_is_not_met(self):
        self.assertFalse(G.grade(key([-3369.6241]), body("The difference is 3,369.62 USD/MW."), G.RULES_5201)["ok"])
        self.assertFalse(G.grade(key([-3369.6241]), body("ERCOT earned 3,369.62 USD/MW more than CAISO."), G.RULES_5201)["ok"])

    def test_the_word_must_stand_in_the_figures_own_sentence(self):
        text = "The difference is 3,369.62 USD/MW. CAISO's price was lower in the spring."
        self.assertFalse(G.grade(key([-3369.6241]), body(text), G.RULES_5201)["ok"])

    def test_a_positive_figure_is_never_met_by_a_negative_one(self):
        self.assertFalse(G.grade(key([3369.6241]), body("The difference is -3,369.62 USD/MW, less at ERCOT."), G.RULES_5201)["ok"])
        self.assertFalse(G.said_in_words(3369.6241, "3,369.62 less", 0.5))

    def test_a_word_inside_another_word_is_no_direction(self):
        # "underlying", "download", "lesson": the words are matched whole
        self.assertFalse(G.grade(key([-12.5]), body("The underlying spread is 12.5 USD/MWh."), G.RULES_5201)["ok"])

    def test_a_decimal_point_does_not_end_a_sentence(self):
        spans = G.sentences_with("It was 3.5 less. Then 2.0 more.")
        self.assertEqual(len(spans), 2)


class TheSecondThirty(unittest.TestCase):
    """The newest asking of questions_s1114.yaml (eval_s1133_s1114_run.json): 28 of 30 as stored (no rules), 29 under the
    2223 rules (t09), 30 under RULES_5201 (f09)."""

    def grade(self, rules):
        E = module("eval_s1113_for_5201", os.path.join(EVAL, "eval_s1113.py"))
        with tempfile.TemporaryDirectory() as tmp:
            E.SETS["t5201"] = {"questions": E.SETS["s1133"]["questions"], "run": E.SETS["s1133"]["run"], "grades": os.path.join(tmp, "g.json")}
            return E.grade_set("t5201", rules)

    def test_as_stored(self):
        stored = load("eval_s1133_s1114_grades.json")
        self.assertEqual((stored["right"], stored["asked"]), (28, 30))
        self.assertEqual([q["id"] for q in stored["questions"] if not q["ok"]], ["t09", "f09"])
        doc = self.grade(())
        self.assertEqual([q["id"] for q in doc["questions"] if not q["ok"]], ["t09", "f09"])

    def test_t09_is_met_by_the_2223_rule(self):
        doc = self.grade(G.RULES_2223)
        self.assertEqual([q["id"] for q in doc["questions"] if not q["ok"]], ["f09"])

    def test_f09_is_met_by_the_new_rule(self):
        doc = self.grade(G.RULES_5201)
        self.assertEqual((doc["right"], doc["asked"]), (30, 30))
        self.assertEqual(doc["rules"], list(G.RULES_5201))

    def test_the_stored_regrade_is_what_the_grader_gives(self):
        stored = load("eval_s5201_regrade_s1133_grades.json")
        doc = self.grade(G.RULES_5201)
        self.assertEqual((stored["right"], stored["asked"]), (30, 30))
        self.assertEqual([(q["id"], q["ok"]) for q in stored["questions"]], [(q["id"], q["ok"]) for q in doc["questions"]])
        self.assertIn("eval_s5201_regrade_s1133_grades.json", load("runs.json")["left_out"])

    def test_f09s_answer_states_the_three_figures(self):
        a = {q["id"]: q for q in load("eval_s1133_s1114_run.json")["questions"]}["f09"]["answer"]
        for figure in ("7,503.01", "10,872.64", "3,369.62"):
            self.assertIn(figure, a)
        self.assertRegex(a, r"3,369\.62 USD/MW less at ERCOT")


class NothingElseMoves(unittest.TestCase):
    """The rule only adds: over every stored run that carries its question's key in a set file, no answer right under the
    2223 rules is wrong under RULES_5201, and f09 is the only answer the rule turns."""

    SETS = (("questions_s1114.yaml", "eval_s1114_run.json"), ("eval_s1133_s1114_questions.yaml", "eval_s1133_s1114_run.json"),
            ("questions_s2224.yaml", "eval_s2968_loop_s2224_run.json"), ("questions_trader.yaml", "eval_s3280_loop_trader_run.json"),
            ("questions_investor.yaml", "eval_s3281_loop_investor_run.json"))

    def test_only_f09_turns(self):
        E = module("eval_s1113_for_5201_b", os.path.join(EVAL, "eval_s1113.py"))
        turned = []
        for qfile, rfile in self.SETS:
            run = {q["id"]: q for q in load(rfile)["questions"]}
            for q in E.questions(os.path.join(EVAL, qfile)):
                if q["id"] not in run:
                    continue
                old, new = G.grade(q, run[q["id"]], G.RULES_2223), G.grade(q, run[q["id"]], G.RULES_5201)
                self.assertFalse(old["ok"] and not new["ok"], (rfile, q["id"]))
                if new["ok"] and not old["ok"]:
                    turned.append((rfile, q["id"]))
        self.assertEqual(turned, [("eval_s1133_s1114_run.json", "f09")])


class TheLoopsGrading(unittest.TestCase):
    def test_eval_loop_grades_under_the_new_rules_by_default(self):
        with open(os.path.join(EVAL, "eval_loop.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("E.G.RULES_5201", src)
        self.assertRegex(src, r'how == "2223"')


class TheFormClass(unittest.TestCase):
    """Items 9 and 10 (session 2222's fix) had no test of their own: rule 1's words in both loops' prompt, and the stored
    askings since, where the three sums of five digits stand to the cent."""

    WORDS = "to the cent when the result has cents, never rounded to the unit"

    def test_rule_1_says_it_in_both_loops(self):
        with open(os.path.join(ROOT, "warehouse", "chat", "ask.py"), encoding="utf-8") as f:
            self.assertIn(self.WORDS, f.read())
        with open(os.path.join(ROOT, "site", "lib", "chat", "spec.json"), encoding="utf-8") as f:
            self.assertIn(self.WORDS, json.load(f)["system"])

    def test_the_sums_stand_to_the_cent_in_every_asking_since(self):
        for tag in ("eval_s2222_loop", "eval_s2223_loop", "eval_s2968_loop", "eval_s3769_loop"):
            run = {q["id"]: q for q in load(tag + "_run.json")["questions"]}
            keys = load(tag + "_keys.json")["keys"]
            for qid in ("g03", "g06", "g09"):
                k = keys[qid]
                expected = k["expected"] if isinstance(k, dict) else k
                figure = f"{float(expected[0]):,.2f}"
                self.assertIn(figure, run[qid]["answer"], (tag, qid))

    def test_before_the_fix_they_were_rounded(self):
        run = {q["id"]: q for q in load("eval_s2221_loop_run.json")["questions"]}
        self.assertIn("50,424", run["g03"]["answer"])
        self.assertNotIn("50,424.07", run["g03"]["answer"])


class TheFaultsFile(unittest.TestCase):
    """Every row of the faults file has a state, and none is open."""

    def setUp(self):
        with open(os.path.join(ROOT, "docs", "reviews", "ask-faults-2026-11-05.md"), encoding="utf-8") as f:
            self.text = f.read()

    def rows(self):
        part = self.text.split("## The state of every row", 1)[1]
        return [[c.strip() for c in line.strip().strip("|").split("|")] for line in part.splitlines()
                if re.match(r"\|\s*(\d|t09|f09|f08|second)", line)]

    def test_every_item_has_a_state(self):
        rows = self.rows()
        named = set()
        for r in rows:
            first = r[0]
            for a, b in re.findall(r"(\d+) to (\d+)", first):
                named.update(range(int(a), int(b) + 1))
            named.update(int(x) for x in re.findall(r"\b(\d+)\b", first))
        self.assertTrue(set(range(1, 22)) <= named, sorted(set(range(1, 22)) - named))
        states = {r[2].split(":")[0].split(" (")[0] for r in rows}
        self.assertTrue(states <= {"fixed", "no fault", "the key's, fixed in the grader"}, states)

    def test_the_tests_named_exist(self):
        part = self.text.split("## The state of every row", 1)[1]
        for name in set(re.findall(r"tests/(test_session\w+\.py)", part)):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", name)), name)

    def test_no_dash(self):
        self.assertNotIn(chr(0x2014), self.text)
        self.assertNotIn(chr(0x2013), self.text)


if __name__ == "__main__":
    unittest.main()
