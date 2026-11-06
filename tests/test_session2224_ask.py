"""Session 2224 (chain 152, Ask): the third set, twenty questions a lab's energy team asks, and what was found on the way.

Held here, with no model and no network: the set's file (questions_s2224.yaml) is what scripts/ask_eval/lab_questions.py
writes (twenty ids l01 to l20 in order, each key a figure computed or a refusal with its words, the keys file beside it
equal key for key); a key marked hold: true (a table held whole for a license) is met by an answer in the hold's words
with no figure, whatever its status, and not by one that states a figure (eval_s1113.py grade_set, hold_answer); the set
is in the asking's SETS; and the package's live backend admits the catalogue's review tables only with
ERW_LIVE_REVIEW=on, which the chat's tools set at first use and never at import. (Named _ask: tests/test_session2224.py
is chain 098's.)
"""
import importlib.util
import json
import os
import sys
import unittest
from unittest import mock

import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
sys.path.insert(0, os.path.join(ROOT, "package", "src"))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E = module("eval_s1113_for_2224", os.path.join(EVAL, "eval_s1113.py"))


def load_set():
    with open(os.path.join(EVAL, "questions_s2224.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


class TheSet(unittest.TestCase):
    def test_twenty_in_order_each_a_figure_or_a_refusal_with_its_words(self):
        qs = load_set()["questions"]
        self.assertEqual([q["id"] for q in qs], [f"l{i:02d}" for i in range(1, 21)])
        for q in qs:
            self.assertIn(q["via"], ("grid", "general"), q["id"])
            if q["refuse"]:
                self.assertEqual(q["expected"], [], q["id"])
                self.assertTrue(q["text"], q["id"])
            else:
                self.assertEqual(len(q["expected"]), 1, q["id"])
                self.assertEqual(q["tolerance"], 0.5 if abs(q["expected"][0]) >= 1000 else 0.01, q["id"])
                self.assertEqual(len(q["tables"]), 1, q["id"])
            self.assertIn("hold", q)
            if q["hold"]:
                self.assertTrue(q["refuse"] and q["text"] == ["license needed"], q["id"])
        # no figure key names a table the site holds for a license, whole or for the question's grid (the script checks the status file)
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
        import license_hold as hold
        for q in qs:
            if not q["refuse"]:
                t = q["tables"][0]
                self.assertFalse(hold.held_whole(t), q["id"])
                if q["grid"] != "none":
                    self.assertFalse(hold.held_row(t, f"{hold.GRID_PREFIX[q['grid']]}:x"), q["id"])
        self.assertEqual(sorted(q["id"] for q in qs if q["hold"]), ["l01", "l02", "l03", "l04", "l08"])   # l08: ISO-NE's queue, held by grid
        self.assertEqual([q["id"] for q in qs if q["refuse"] and not q["hold"]], ["l10", "l20"])
        self.assertEqual(sum(1 for q in qs if not q["refuse"]), 13)

    def test_the_keys_file_is_the_set_key_for_key(self):
        qs = {q["id"]: q for q in load_set()["questions"]}
        with open(os.path.join(EVAL, "keys_s2224.json"), encoding="utf-8") as f:
            keys = json.load(f)
        self.assertEqual(sorted(keys["keys"]), sorted(qs))
        for qid, k in keys["keys"].items():
            for field in ("expected", "tolerance", "text", "tables", "refuse", "hold", "note"):
                self.assertEqual(k[field], qs[qid][field], (qid, field))
        self.assertRegex(keys["computed_at_utc"], r"^2026-11-06T\d\d:\d\d:\d\dZ$")

    def test_the_script_writes_the_file_it_describes(self):
        with open(os.path.join(ROOT, "scripts", "ask_eval", "lab_questions.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('"questions_s2224.yaml"', src)
        self.assertIn('"keys_s2224.json"', src)
        for qid in (f"l{i:02d}" for i in range(1, 21)):
            self.assertIn(f'"{qid}"', src)
        self.assertNotIn(chr(0x2014), src)

    def test_the_set_is_in_the_askings_sets(self):
        self.assertIn("s2224", E.SETS)
        self.assertTrue(E.SETS["s2224"]["questions"].endswith("questions_s2224.yaml"))
        self.assertEqual(len(E.questions(E.SETS["s2224"]["questions"])), 20)


class TheHoldsAnswer(unittest.TestCase):
    def q(self):
        return {"id": "l01", "refuse": True, "hold": True, "expected": [], "tolerance": 0.01, "text": ["license needed"], "tables": ["energy_deals"]}

    def test_an_answer_in_the_holds_words_with_no_figure_is_right_whatever_its_status(self):
        q = self.q()
        a = {"status": "answered", "not_in_warehouse": False, "answer": "energy_deals is held for a license (license needed): no PPA price can be given.", "citations": []}
        self.assertFalse(E.G.grade(q, a, E.G.RULES_2223)["ok"])      # the grader alone wants a refusal
        self.assertTrue(E.hold_answer(q, a))
        self.assertTrue(E.hold_answer(q, {"status": "not_in_warehouse", "answer": "Not in the warehouse: license needed for energy_deals since 21 October 2026."}))

    def test_a_figure_or_other_words_are_not_the_holds_answer(self):
        q = self.q()
        self.assertFalse(E.hold_answer(q, {"status": "answered", "answer": "The average solar PPA was 42.17 USD/MWh (license needed)."}))
        self.assertFalse(E.hold_answer(q, {"status": "answered", "answer": "The largest was 1,250 MW; license needed."}))
        self.assertFalse(E.hold_answer(q, {"status": "answered", "answer": "The deals table is internal."}))


class TheReviewTables(unittest.TestCase):
    def test_the_live_backend_admits_review_only_with_the_flag(self):
        import erw.remote as R
        cat = pd.DataFrame([{"table_name": "a_yes", "in_live_set": "yes"}, {"table_name": "b_review", "in_live_set": "review"}, {"table_name": "c_no", "in_live_set": "no"}])
        b = R.SupabaseBackend.__new__(R.SupabaseBackend)
        b._cache = {"_catalogue": cat}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ERW_LIVE_REVIEW", None)
            self.assertEqual(b.list_tables(), ["a_yes"])
            os.environ["ERW_LIVE_REVIEW"] = "on"
            self.assertEqual(b.list_tables(), ["a_yes", "b_review"])
            os.environ["ERW_LIVE_REVIEW"] = "off"
            self.assertEqual(b.list_tables(), ["a_yes"])

    def test_the_chat_sets_the_flag_at_first_use_not_at_import(self):
        with open(os.path.join(ROOT, "warehouse", "chat", "tools.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('os.environ.setdefault("ERW_LIVE_REVIEW", "on")', src)
        head = src[:src.index("def ")]
        self.assertNotIn("ERW_LIVE_REVIEW", head)
        with open(os.path.join(ROOT, "site", "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn('c.in_live_set !== "yes" && c.in_live_set !== "review"', ts)   # the site's rule the chat now follows


if __name__ == "__main__":
    unittest.main()
