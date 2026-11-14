"""Sessions 6161 to 6165 (chain 282): the platform set whole under rule 12, and twelve questions about other tables of
the record a visitor's chat cannot read.

Energy Research Warehouse (ERW).

Rule 12 ("Write for the reader, not about how you worked", session 6136) changed the prompt of every answer. Chain 281
asked 55 of the platform set's 134 questions under it; sessions 6161 to 6164 asked the other 79. The set under rule 12,
each question's newest answer: 85 correct, 49 correctly refused, no unsupported number, none wrong.

The loop's refusal by name of a table the site cannot read was measured on the six tables of the week of 9 November.
Session 6165 asked about twelve others (questions_unlisted.yaml): 12 of 12 refused, no figure. Ten have names of three
words or more and the loop found the table for each; two have names of two words, which the word match does not look
for by design, and their refusals do not say that the record holds the table.

No model, no network.
"""
import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402
import tools  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class ThePlatformSetUnderRuleTwelve(unittest.TestCase):
    SESSIONS = ["6139", "6142", "6143", "6161", "6162", "6163", "6164"]

    def test_every_question_was_asked_under_twelve_rules(self):
        asked = {}
        for s in self.SESSIONS:
            for q in load(f"eval_s{s}_site_platform_run.json")["questions"]:
                self.assertEqual(q["asked_under"]["rules"], 12, (s, q["id"]))
                asked[q["id"]] = q
        self.assertEqual(len(asked), 134)

    def test_the_classes(self):
        C = module("class_scores_6165", os.path.join(EVAL, "class_scores.py"))
        sys.path.insert(0, EVAL)
        import eval_s1113 as E
        import replay
        qs = E.questions(E.SETS["platform"]["questions"])
        rows, counts = C.score(qs, C.newest("platform", self.SESSIONS), replay.check)
        self.assertEqual(len(rows), 134)
        self.assertEqual(counts, {"correct": 85, "correctly refused": 49, "unsupported number": 0, "wrong": 0})

    def test_no_day_is_written_as_the_tool_writes_it(self):
        for s in self.SESSIONS:
            for q in load(f"eval_s{s}_site_platform_run.json")["questions"]:
                self.assertEqual(ask.plain_dates(q["answer"] or ""), q["answer"] or "", (s, q["id"]))


class OtherTablesTheSiteCannotRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import yaml
        with open(os.path.join(EVAL, "questions_unlisted.yaml"), encoding="utf-8") as f:
            cls.qs = yaml.safe_load(f)["questions"]
        cls.answers = {q["id"]: q for q in load("eval_s6165_site_unlisted_run.json")["questions"]}
        cls.grades = {g["id"]: g for g in load("eval_s6165_site_unlisted_grades.json")["questions"]}
        cls.L = module("unlisted_questions_6165", os.path.join(ROOT, "scripts", "ask_eval", "unlisted_questions.py"))

    def test_twelve_refusal_keys_each_of_a_table_of_the_record(self):
        self.assertEqual(len(self.qs), 12)
        verdicts = tools.verdicts()
        for (qid, table, question), q in zip(self.L.ASKED, self.qs):
            self.assertEqual((q["id"], q["question"], q["kind"], q["expected"]), (qid, question, "not_readable", []))
            self.assertIn(table, verdicts, table)

    def test_twelve_of_twelve_refused_with_no_figure(self):
        self.assertEqual(sorted(self.answers), [q["id"] for q in self.qs])
        for i, q in self.answers.items():
            self.assertEqual(q["status"], "not_in_warehouse", i)
            self.assertTrue(self.grades[i]["ok"], i)
            self.assertEqual(ask.refusal_figures(q["answer"], q["question"]), [], i)

    def test_the_word_match_finds_the_table_of_a_name_of_three_words(self):
        names = [t for _, t, _ in self.L.ASKED]
        found = {qid: ask.unlisted_named(question, names) for qid, _, question in self.L.ASKED}
        for qid, table, _ in self.L.ASKED:
            if len(table.split("_")) >= 3:
                self.assertIn(table, found[qid], qid)
            else:
                self.assertEqual(found[qid], [], qid)   # two words: not looked for, by design

    def test_a_table_found_is_named_in_its_refusal_and_asked_in_few_calls(self):
        """Nine of the ten named tables are refused in two to four calls; ul05's question also fits tables the chat can
        read (CAISO's curtailment by day), and it looked there first."""
        named = [qid for qid, table, _ in self.L.ASKED if len(table.split("_")) >= 3]
        for qid, table, _ in self.L.ASKED:
            if qid in named and qid not in ("ul05", "ul10"):   # ul10: NYISO's own table, refused in the hold's words; ul05: below
                self.assertIn(table, self.answers[qid]["answer"], qid)
        # ul05 listed CAISO's tables alone, and the loop then could not tell what the site lacks (ten calls, the table not
        # named). Session 6166: the loop asks the tools what the catalogue lists whatever the list's filter; asked again,
        # the refusal names the table in three calls
        again = {q["id"]: q for q in load("eval_s6166_site_unlisted_run.json")["questions"]}
        self.assertNotIn("caiso_curtailment_intervals", self.answers["ul05"]["answer"])
        self.assertIn("caiso_curtailment_intervals", again["ul05"]["answer"])
        self.assertEqual((self.answers["ul05"]["tool_calls"], again["ul05"]["tool_calls"]), (10, 3))
        self.assertTrue(all(q["status"] == "not_in_warehouse" for q in again.values()))
        self.assertEqual(sorted(i for i in named if self.answers[i]["tool_calls"] > 4), ["ul05", "ul10"])


if __name__ == "__main__":
    unittest.main()
