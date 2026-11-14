"""Session 6106 (chain 280): the whole platform set asked once more, scored in four classes; a refusal states no figure;
an answer written after a held table carries the hold's words.

Energy Research Warehouse (ERW).

The asking. 134 questions through the site's own loop on 14 November 2026 (sessions 6101 to 6106, the chat as chain 256
left it): 85 correct, 47 correctly refused, no unsupported number, 2 wrong (warehouse/chat/eval/class_scores.py, from the
stored runs). The two:

  pw13  a refusal that was right and went on to state a fetched figure of something else (ERCOT's 2025 peak, asked the
        peak of 2028). Rule 3 says a refusal states no numbers. Both loops now send such a draft back once.
  pj08  ISO New England's queue: its own table refused (license needed), the answer written from Berkeley Lab's public
        table, with the hold said in other words. Both loops now put the fixed words before such an answer.

No model, no network.
"""
import glob
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402

EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
PW13 = ("Not in the warehouse. It holds no forecast of ERCOT's summer 2028 peak demand, and I won't estimate one. The only peak figure I found is a "
        "past one: ERCOT's 2025 peak demand was 83,597 MW (grid_peak_vs_capacity, derived).")
PJ08 = ("I can't give a figure from ISO-NE's own queue table. isone_interconnection_queue is held because it needs a license. Berkeley Lab's national "
        "queue file is a separate public source.")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


def scores():
    import importlib.util
    spec = importlib.util.spec_from_file_location("class_scores_6106", os.path.join(EVAL, "class_scores.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ARefusalStatesNoFigure(unittest.TestCase):
    def test_the_figure_of_pw13_is_found(self):
        self.assertEqual(ask.refusal_figures(PW13, "What will ERCOT's peak demand be in the summer of 2028, in MW?"), ["83,597"])

    def test_dates_hours_names_and_list_markers_are_not_figures(self):
        self.assertEqual(ask.refusal_figures("Not in the warehouse. The table has no rows from 5 to 8 November 2026; it holds 72 of 168 hours and EIA-930 begins in 2018."), [])
        self.assertEqual(ask.refusal_figures("Not in the warehouse:\n1. no table holds futures\n2. none holds forwards"), [])
        self.assertEqual(ask.refusal_figures(""), [])

    def test_a_number_of_the_question_is_the_askers(self):
        self.assertEqual(ask.refusal_figures("Not in the warehouse: no plant of 1,227 MW is listed.", "Is there a 1,227 MW plant in the queue?"), [])
        self.assertEqual(ask.refusal_figures("Not in the warehouse. The nearest price is 41.81 USD/MWh, and the table holds 38,201 rows."), ["41.81", "38,201"])

    def test_the_words_sent_back_are_the_sites(self):
        words = ask.REFUSAL_FIGURE.format(figures="83,597")
        ts = src("site", "lib", "chat", "refused.ts")
        self.assertIn("a refusal that states a figure (${figures.join(\", \")}): rule 3 says a refusal states no numbers. Remove it, or, if a tool result holds "
                      "what the question asks for, answer the question with not_in_warehouse false", ts)
        self.assertTrue(words.startswith("a refusal that states a figure (83,597): rule 3 says a refusal states no numbers."))
        self.assertTrue(words.endswith("answer the question with not_in_warehouse false"))

    def test_only_the_general_chats_refusals(self):
        py, ts = src("warehouse", "chat", "ask.py"), src("site", "lib", "chat", "ask.ts")
        self.assertIn('if draft.get("not_in_warehouse") and type(self) is Asker:\n                # session 6106', py)
        self.assertIn("if (!profile && draft.not_in_warehouse) {\n      const figures = refusalFigures(draft.answer, question);", ts)

    def test_of_the_stored_refusals_of_the_sites_loop_only_pw13_states_a_figure(self):
        """The measure before the rule: every refusal the site's loop let through in the stored runs, read by the rule.
        One of them states a figure, pw13 of session 6101, and it was graded not right: no right refusal is sent back."""
        hits, n = [], 0
        for path in sorted(glob.glob(os.path.join(EVAL, "eval_s*_site_*_run.json"))):
            session = re.search(r"eval_s(\d+)_site_", os.path.basename(path)).group(1)
            grades_path = path.replace("_run.json", "_grades.json")
            grades = {g["id"]: g["ok"] for g in load(os.path.basename(grades_path))["questions"]} if os.path.exists(grades_path) else {}
            for q in load(os.path.basename(path)).get("questions") or []:
                if q.get("status") != "not_in_warehouse" or not q.get("answer"):
                    continue
                n += 1
                if ask.refusal_figures(q["answer"], q.get("question") or ""):
                    hits.append((session, q["id"], grades.get(q["id"])))
        self.assertGreaterEqual(n, 134)   # 134 on 14 November 2026, after session 6106
        self.assertEqual([h for h in hits if h[2]], [], "a refusal graded right would be sent back")
        self.assertIn(("6101", "pw13", False), hits)


class AnAnswerAfterAHeldTable(unittest.TestCase):
    WORDS = {"isone_interconnection_queue": "table isone_interconnection_queue is license needed: ISO-NE: the publisher's own page asks for permission; none is recorded yet.",
             "eia_crude_imports_by_country": "table eia_crude_imports_by_country is not in this site's live set; its full history is on Redivis."}

    def test_only_a_table_refused_as_license_needed_is_held(self):
        self.assertEqual(ask.held_tables(self.WORDS), ["isone_interconnection_queue"])
        self.assertEqual(ask.held_tables({}), [])
        self.assertEqual(ask.held_tables({"b": "table b is license needed: x", "a": "table a is license needed: y"}), ["a", "b"])

    def test_the_fixed_sentence_goes_before_the_models_own(self):
        self.assertEqual(ask.with_hold_words(PJ08, ask.held_tables(self.WORDS)),
                         "isone_interconnection_queue: license needed, so no figure of it is given here. " + PJ08)
        self.assertEqual(ask.with_hold_words(PJ08, ["a", "b"]), "a, b: license needed, so no figure of them is given here. " + PJ08)

    def test_an_answer_that_has_the_words_and_one_with_no_held_table_are_left(self):
        for kept in ("energy_deals is held (license needed), so no price is given. ERCOT's was 54.481 USD/MWh.", "License needed for the deals table."):
            self.assertEqual(ask.with_hold_words(kept, ["energy_deals"]), kept)
        self.assertEqual(ask.with_hold_words(PJ08, []), PJ08)

    def test_the_sentence_is_the_sites(self):
        ts = src("site", "lib", "chat", "refused.ts")
        self.assertIn('return `${held.join(", ")}: ${HOLD_WORDS}, so no figure of ${held.length === 1 ? "it" : "them"} is given here. ${(answer ?? "").trim()}`.trim();', ts)
        self.assertEqual(ask.HOLD_WORDS, "license needed")
        self.assertIn(ask.HOLD_WORDS, ask.REFUSAL_WORDS)

    def test_the_stored_answer_of_pj08_would_have_had_them(self):
        q = next(x for x in load("eval_s6104_site_platform_run.json")["questions"] if x["id"] == "pj08")
        self.assertEqual(q["status"], "answered")
        self.assertNotIn("license needed", q["answer"].lower())
        refused = {t["input"]["table"]: t["out"]["error"] for t in q["trace"] if t.get("isError") and isinstance(t.get("out"), dict) and "table" in (t.get("input") or {})}
        self.assertTrue(ask.with_hold_words(q["answer"], ask.held_tables(refused)).startswith("isone_interconnection_queue: license needed, so no figure of it is given here."))


class TheFourClasses(unittest.TestCase):
    def test_the_whole_set_as_asked_in_sessions_6101_to_6106(self):
        m = scores()
        sys.path.insert(0, EVAL)
        import eval_s1113 as E
        import replay
        qs = E.questions(E.SETS["platform"]["questions"])
        rows, counts = m.score(qs, m.newest("platform", ["6101", "6102", "6103", "6104", "6105", "6106"]), replay.check)
        self.assertEqual(len(rows), 134)
        self.assertEqual(counts, {"correct": 85, "correctly refused": 47, "unsupported number": 0, "wrong": 2})
        self.assertEqual(sorted(r["id"] for r in rows if r["class"] == "wrong"), ["pj08", "pw13"])

    def test_a_class_is_told_from_the_key_the_grade_and_the_checks(self):
        m = scores()
        figure, refusal, part = {"kind": "figure"}, {"kind": "outside"}, {"kind": "partial"}
        ok = {"status": "answered", "answer": "x"}
        self.assertEqual(m.class_of(figure, ok, True), "correct")
        self.assertEqual(m.class_of(figure, ok, False), "wrong")
        self.assertEqual(m.class_of(refusal, {"status": "not_in_warehouse", "answer": "x"}, True), "correctly refused")
        self.assertEqual(m.class_of(part, {"status": "not_in_warehouse", "answer": "x"}, True), "correctly refused")
        self.assertEqual(m.class_of(part, ok, True), "correct")
        # a number in no tool result is the worst class whatever the grade; so is the loop's fixed refusal after two such drafts
        self.assertEqual(m.class_of(figure, ok, True, {"numbers": ["12.5"], "units": []}), "unsupported number")
        self.assertEqual(m.class_of(figure, {"status": "refused_unverified", "answer": "x", "refused": True}, False), "unsupported number")
        self.assertEqual(m.class_of(figure, {"status": "error", "answer": None}, False), "wrong")
        # a set with no kinds: its marks
        self.assertEqual(m.class_of({"refuse": True}, {"status": "not_in_warehouse", "answer": "x"}, True), "correctly refused")
        self.assertEqual(m.class_of({"hold": "true"}, ok, True), "correctly refused")


class AHeldGridAnsweredFromAnotherPublishersTable(unittest.TestCase):
    """Session 6107: the grader's rule hold_public_table (eval_s267.py RULES_6107). pj08 as re-asked on the mended chat:
    ISO-NE's own table refused, the hold's words, Berkeley Lab's public figure named as Berkeley Lab's."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, EVAL)
        import eval_s1113 as E
        cls.E = E
        cls.key = next(q for q in E.questions(E.SETS["platform"]["questions"]) if q["id"] == "pj08")
        cls.new = next(x for x in load("eval_s6107_site_platform_run.json")["questions"] if x["id"] == "pj08")
        cls.old = next(x for x in load("eval_s6104_site_platform_run.json")["questions"] if x["id"] == "pj08")

    def test_the_rule_set(self):
        G = self.E.G
        self.assertEqual(G.RULES_6107, G.RULES_5251 + ("hold_public_table",))

    def test_the_answer_with_the_holds_words_and_a_public_tables_figure_is_met(self):
        G = self.E.G
        self.assertEqual((self.key["kind"], self.key["text"]), ("hold", ["license needed"]))
        self.assertTrue(self.E.hold_answer(self.key, self.new, G.RULES_6107))
        self.assertFalse(self.E.hold_answer(self.key, self.new, G.RULES_5251), "the rule before counted the public table's figure as the held table's")

    def test_without_the_holds_words_it_is_not(self):
        self.assertFalse(self.E.hold_answer(self.key, self.old, self.E.G.RULES_6107))

    def test_a_figure_no_public_result_holds_is_not_met(self):
        made_up = dict(self.new, answer=self.new["answer"] + " ISO-NE's own list holds 15,902.4 MW.")
        self.assertFalse(self.E.hold_answer(self.key, made_up, self.E.G.RULES_6107))

    def test_a_figure_of_a_held_tables_result_is_not_met(self):
        """The same record with its public table's result moved to the held grid's own table: the figure is then the held
        table's, and the key stays wrong."""
        trace = [dict(t, input=dict(t["input"], table="isone_interconnection_queue")) if (t.get("input") or {}).get("table") == "lbnl_interconnection_queue" else t
                 for t in self.new["trace"]]
        self.assertFalse(self.E.hold_answer(self.key, dict(self.new, trace=trace), self.E.G.RULES_6107))

    def test_which_tables_are_held(self):
        self.assertTrue(self.E.table_held("isone_interconnection_queue"))
        self.assertTrue(self.E.table_held("miso_interconnection_queue"))
        self.assertTrue(self.E.table_held("energy_deals"))
        self.assertFalse(self.E.table_held("lbnl_interconnection_queue"))
        self.assertFalse(self.E.table_held("cost_of_power_monthly"))

    def test_the_whole_set_with_the_two_classes_asked_again(self):
        m = scores()
        import replay
        qs = self.E.questions(self.E.SETS["platform"]["questions"])
        rows, counts = m.score(qs, m.newest("platform", ["6101", "6102", "6103", "6104", "6105", "6106", "6107"]), replay.check)
        self.assertEqual(counts, {"correct": 85, "correctly refused": 49, "unsupported number": 0, "wrong": 0})


if __name__ == "__main__":
    unittest.main()
