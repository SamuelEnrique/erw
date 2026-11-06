"""Session 2223 (chain 152, Ask): session 320's ruling 3 in the grader, as two named rules (eval_s267.py RULES_2223).

Held here, on the stored runs and with no model: under the rules a key that expects a refusal is graded on refusing and
stating no figure, not on a cited table (d10 of session 1149's run is right, as it is in session 1113's and session
2221's; a refusal that states a figure is wrong); a key's table is also met when every expected figure is in a tool
result of a cited table in the answer's own record (t06, f05, f06 and f07 of session 1114's run, which stated the right
figure from another table that holds it, are right; a cited table whose results do not hold the figure is not); with no
rules every grade is what it was (the stored gradings regrade to their stored counts); eval_s1113.py's grade passes the
rules through and names them in the grades document. (Named _ask: tests/test_session2223.py would be chain 098's number.)
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import copy
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = module("eval_s267_for_2223", os.path.join(EVAL, "eval_s267.py"))
E = module("eval_s1113_for_2223", os.path.join(EVAL, "eval_s1113.py"))


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


def by_id(doc):
    return {q["id"]: q for q in doc["questions"]}


class TheRules(unittest.TestCase):
    def setUp(self):
        E.GRADES = os.devnull   # a grading here writes nowhere: the stored grades files stay as they are

    def test_the_rules_are_named(self):
        self.assertEqual(G.RULES_2223, ("refusal_no_table", "table_by_evidence"))

    def test_a_right_refusal_is_right_whatever_it_cites(self):
        q = next(x for x in E.questions() if x["id"] == "d10")
        self.assertTrue(q["refuse"])
        for run in ("eval_s1113_run.json", "eval_s1133_s320_run.json", "eval_s2221_loop_run.json"):
            a = by_id(load(run))["d10"]
            self.assertFalse(G.grade(q, a)["ok"], run)                       # as graded on 23 October: wrong for the table
            g = G.grade(q, a, G.RULES_2223)
            self.assertEqual((g["ok"], g["table"], g["no_figure"], g["refusal"]), (True, None, True, True), run)

    def test_a_refusal_that_states_a_figure_is_wrong(self):
        q = next(x for x in E.questions() if x["id"] == "d10")
        a = dict(by_id(load("eval_s1133_s320_run.json"))["d10"])
        a["answer"] = "Not in the warehouse. PJM's Western hub real-time price for August 2026 was 45.20 USD/MWh elsewhere, but not here."
        g = G.grade(q, a, G.RULES_2223)
        self.assertEqual((g["no_figure"], g["ok"]), (False, False))
        a["answer"] = "Not in the warehouse: it holds PJM demand from 2018 to 2026 and 21 PJM tables, none of them prices."
        self.assertTrue(G.grade(q, a, G.RULES_2223)["ok"], "years and small counts are not figures")
        a["answer"] = "Not in the warehouse. The nearest figure is 21,091 rows of demand."
        self.assertFalse(G.grade(q, a, G.RULES_2223)["ok"], "a whole number of 1,000 or more is a figure")

    def test_a_right_figure_from_another_table_that_holds_it(self):
        qs = {q["id"]: q for q in E.questions(E.SETS["s1114"]["questions"])}
        run = by_id(load("eval_s1114_run.json"))
        for qid in ("t06", "f05", "f06", "f07"):
            self.assertFalse(G.grade(qs[qid], run[qid])["ok"], qid)                        # as graded on 23 October
            g = G.grade(qs[qid], run[qid], G.RULES_2223)
            self.assertEqual((g["table"], g["number"], g["ok"]), (True, True, True), qid)
        # f08 read the wrong variable: its figures are not the key's, and no rule makes it right
        self.assertFalse(G.grade(qs["f08"], run["f08"], G.RULES_2223)["ok"])
        # a cited table whose results do not hold the figure does not meet the key
        a = copy.deepcopy(run["t06"])
        for t in a["trace"]:
            if isinstance(t.get("out"), dict):
                t["out"] = {"table": "hub_price_comparison", "result": [{"value": 1.0}]}
        self.assertEqual(G.grade(qs["t06"], a, G.RULES_2223)["table"], False)

    def test_with_no_rules_every_stored_grading_is_what_it_was(self):
        for run, grades in (("eval_s1113_run.json", "eval_s1113_grades.json"), ("eval_s1133_s320_run.json", "eval_s1133_s320_grades.json")):
            stored = load(grades)
            doc = E.grade(load(run), load("eval_s1113_keys.json" if run == "eval_s1113_run.json" else "eval_s1133_s320_keys.json"))
            self.assertEqual((doc["right_now"], doc["right_under_hold"], doc["rules"]), (stored["right_now"], stored["right_under_hold"], []), run)
        E.GRADES = os.devnull

    def test_the_grade_passes_the_rules_through_and_names_them(self):
        E.GRADES = os.devnull
        doc = E.grade(load("eval_s1133_s320_run.json"), load("eval_s1133_s320_keys.json"), G.RULES_2223)
        self.assertEqual(doc["rules"], ["refusal_no_table", "table_by_evidence"])
        self.assertEqual(doc["right_under_hold"], 20, "d10 right under the rules; the ten other wrong answers stand")
        self.assertEqual(sorted(q["id"] for q in doc["questions"] if not q["held_ok"]), ["b01", "b02", "b03", "b04", "b05", "b06", "b08", "b09", "g03", "g06"])
        # session 2221's run under the rules: d10 right, the three form faults stand
        doc = E.grade(load("eval_s2221_loop_run.json"), load("eval_s2221_loop_keys.json"), G.RULES_2223)
        self.assertEqual((doc["right_under_hold"], sorted(q["id"] for q in doc["questions"] if not q["held_ok"])), (27, ["g03", "g06", "g09"]))


if __name__ == "__main__":
    unittest.main()
