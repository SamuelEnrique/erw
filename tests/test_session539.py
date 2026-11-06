"""Session 539: session 320's thirty questions to Ask, graded again offline (chain 024). What is held to:

  the stored answers graded with session 267's grader: 17 of 30 right on the keys of 19 October and on the keys now;
  the keys that moved are b08 and b09 alone, and each answer's USD per MW figure is the key now times 1,000;
  the four questions whose rows are held since 21 October (g07, g08, d05, d07) are refusals now;
  every wrong answer has one of the four causes, with the counts of the review note (8, 0, 0, 5);
  each cause rests on what the stored answer says;
  the review note names every wrong answer under its cause and every key that moved; no em dash.

No request, no model call: the regrade reads only files (the keys were read once by --keys); the environment is read, never set."""
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
NOTE = os.path.join(ROOT, "docs", "reviews", "ask-thirty-2026-10-21.md")
FILES = ["warehouse/chat/eval/regrade_s539.py", "warehouse/chat/eval/eval_s539_keys.json", "warehouse/chat/eval/eval_s539_regrade.json",
         "docs/reviews/ask-thirty-2026-10-21.md", "tests/test_session539.py"]


def module():
    spec = importlib.util.spec_from_file_location("regrade_s539", os.path.join(EVAL, "regrade_s539.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def src(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


class TheThirtyGradedAgain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = module()
        cls.doc = cls.m.regrade()
        cls.by = {r["id"]: r for r in cls.doc["questions"]}
        with open(cls.m.FIRST_RUN, encoding="utf-8") as f:
            cls.answers = {q["id"]: q for q in json.load(f)["questions"]}
        with open(cls.m.KEYS, encoding="utf-8") as f:
            cls.keys = json.load(f)

    def test_seventeen_right_then_and_now(self):
        self.assertEqual(len(self.doc["questions"]), 30)
        self.assertEqual(self.doc["right_then"], 17)
        self.assertEqual(self.doc["right_now"], 17)
        # the grade on the keys of 19 October is the one the run stored
        for qid, r in self.by.items():
            self.assertEqual(r["then_ok"], self.answers[qid]["verdict"] == "right", qid)

    def test_only_b08_and_b09_moved_and_the_answers_hold_the_table_now(self):
        self.assertEqual(self.doc["moved"], ["b08", "b09"])
        k = self.keys["keys"]
        self.assertEqual(len(k), 28)
        for qid, stated in (("b08", "79308.31"), ("b09", "42,503.77")):
            self.assertIn(stated, self.answers[qid]["answer"], qid)
            self.assertAlmostEqual(k[qid]["table_unit_value"], float(stated.replace(",", "")), delta=0.01)
            self.assertAlmostEqual(k[qid]["expected"][0] * 1000, k[qid]["table_unit_value"], delta=0.1)
        self.assertEqual(self.keys["extra"]["b09_days_left_out"], 3.0)
        self.assertIn("3 days left out", self.answers["b09"]["answer"])

    def test_the_held_rows_are_refusals_now(self):
        self.assertEqual(self.doc["held"], ["g07", "g08", "d05", "d07"])
        self.assertEqual(self.doc["right_under_hold"], 14)
        self.assertFalse(self.m.held_row("battery_stack_monthly", "ercot:HB_HUBAVG", "2026-10-21"))
        self.assertTrue(self.m.held_row("cost_of_power_monthly", "nyiso:N.Y.C.", "2026-10-21"))
        self.assertFalse(self.m.held_row("cost_of_power_monthly", "nyiso:N.Y.C.", "2026-10-20"))
        self.assertFalse(self.m.held_row("cost_of_power_monthly", "spp:SPPNORTH_HUB", "2026-10-21"))

    def test_every_wrong_answer_has_one_of_the_four_causes(self):
        bc = self.doc["by_cause"]
        self.assertEqual(list(bc), list(self.m.FOURS))
        self.assertEqual(bc[self.m.TOOL], ["b01", "b02", "b03", "b04", "b05", "b06", "b08", "b09"])
        self.assertEqual(bc[self.m.STATED], [])
        self.assertEqual(bc[self.m.REACH], [])
        self.assertEqual(bc[self.m.KEY], ["g03", "g06", "g08", "g09", "d10"])
        for qid, r in self.by.items():
            self.assertEqual(r["cause"] is None, r["now_ok"], qid)
        self.assertEqual(self.doc["right_if_ruled"], 30)

    def test_each_cause_rests_on_the_stored_answer(self):
        k = self.keys["keys"]
        for qid in self.doc["by_cause"][self.m.TOOL]:
            a = self.answers[qid]["answer"]
            self.assertIn("USD per MW", a, qid)
            self.assertTrue(self.answers[qid]["retried"], qid)
            # the per-MW figure the table holds now is written in the answer, to the cent
            want = k[qid]["table_unit_value"]
            self.assertTrue(any(abs(v - want) <= 0.01 for v, _ in self.m.grader().numbers(a)), qid)
        for qid in ("g03", "g06", "g09"):
            a = self.answers[qid]["answer"]
            self.assertIn("about", a, qid)
            self.assertTrue(any(abs(v - k[qid]["expected"][0]) <= 0.5 and dec == 0 for v, dec in self.m.grader().numbers(a)), qid)
        self.assertEqual([c["table"] for c in self.answers["g08"]["citations"]], ["cost_of_power_monthly"])
        self.assertAlmostEqual(self.keys["extra"]["g08_cost_of_power_rt_simple_mean"], k["g08"]["expected"][0], delta=0.0001)
        self.assertEqual(self.answers["d10"]["citations"], [])
        self.assertTrue(self.answers["d10"]["not_in_warehouse"])
        # no final answer was refused for an untraced number: every one passed the number check
        self.assertTrue(all(q["status"] in ("answered", "not_in_warehouse") for q in self.answers.values()))

    def test_the_review_note(self):
        n = src("docs/reviews/ask-thirty-2026-10-21.md")
        for qid in ("b01", "b02", "b03", "b04", "b05", "b06", "b08", "b09", "g03", "g06", "g08", "g09", "d10", "g07", "d05", "d07"):
            self.assertIn(f"| {qid} |" if qid not in ("g07", "d05", "d07") else qid, n, qid)
        for words in ("17 of 30", "14 of 30", "30 of 30", "79.3083", "42.5038", "No model call", "license needed"):
            self.assertIn(words, n)
        for c in self.m.FOURS:
            self.assertIn(c[0].upper() + c[1:], n, c)

    def test_the_stored_regrade_is_what_the_files_give(self):
        with open(self.m.REGRADE, encoding="utf-8") as f:
            stored = json.load(f)
        self.assertEqual(stored, json.loads(json.dumps(self.doc)))

    def test_no_em_dash(self):
        for rel in FILES:
            self.assertNotIn(EM, src(rel), rel)


if __name__ == "__main__":
    unittest.main()
