"""Session 5276 (chain 256): the general chat's effort is medium; a refusal's fixed words are the loop's; a window with
no row in it is said not held on a table of more than one step.

Energy Research Warehouse (ERW).

The effort. It sets how much the model thinks and how many tool calls it makes. Measured on 14 November 2026 through the
site's loop, set for each asking by the loop's own switch: 61 questions at medium, 60 right, USD 4.53 where the same
questions had cost USD 7.35 at high (docs/reviews/ask-eval-2026-11-13.md). Ask ERCOT has run at medium since session
143. The server's ASK_WRITER_EFFORT still decides when it is set, so `high` is one variable away, with no deploy.

The refusal's words. The one answer of the 61 that was not right was a refusal that was right in substance and began
"The warehouse does not hold this figure" where rule 3 asks for "not in the warehouse". Two of the 135 refusals for want
of a figure in the stored runs carry none of the fixed words. Both loops now put the fixed sentence before such a
refusal, and change nothing of the model's.

No model, no network.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402
import ercot  # noqa: E402
import window as W  # noqa: E402

EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheEffort(unittest.TestCase):
    def test_the_general_chat_asks_at_medium_in_both_loops(self):
        self.assertEqual(ask.EFFORT, "medium")
        self.assertEqual(ask.Asker.effort, "medium")
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertEqual(spec["effort"], "medium")
        self.assertIn("effort: effortOf(role, profile ? profile.effort : spec.effort)", src("site", "lib", "chat", "ask.ts"))

    def test_the_way_back_is_the_servers_switch(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("return env.ASK_WRITER_EFFORT || own;", loop)         # set to high on the server, every writing call is at high again

    def test_ask_ercot_is_as_it_was_and_the_limits_are_not_changed(self):
        self.assertEqual(ercot.EFFORT, "medium")
        self.assertEqual(json.loads(src("site", "lib", "chat", "spec_ercot.json"))["effort"], "medium")
        self.assertEqual((ask.MAX_TOOL_CALLS, ask.MAX_TOKENS), (12, 16000))

    def test_the_measure_is_in_the_stored_answers(self):
        # every answer asked at medium says so; the five askings the choice rests on hold 61 questions between them
        asked = {}
        for name in ("eval_s5271_site_platform_run.json", "eval_s5272_site_platform_run.json", "eval_s5273_site_platform_run.json",
                     "eval_s5274_site_platform_run.json", "eval_s5275_site_trader_run.json"):
            with open(os.path.join(EVAL, name), encoding="utf-8") as f:
                doc = json.load(f)
            for q in doc["questions"] + (doc.get("superseded") or []):
                self.assertEqual((q["asked_under"]["effort"], q["asked_under"]["rules"]), ("medium", 11), f"{name} {q['id']}")
                self.assertIsNone(q.get("error"), f"{name} {q['id']}")
            for q in doc["questions"]:
                asked[q["id"]] = name
        self.assertEqual(len(asked), 12 + 8 + 19 + 20)                      # po05 is one of the twelve; gp02 one of the eight
        right = 0
        for name in set(asked.values()):
            with open(os.path.join(EVAL, name.replace("_run.json", "_grades.json")), encoding="utf-8") as f:
                grades = {g["id"]: g["ok"] for g in json.load(f)["questions"]}
            right += sum(1 for i, n in asked.items() if n == name and grades[i])
        self.assertEqual(right, len(asked) - 1)                             # all but gp02, the refusal without its fixed words


class TheRefusalsWords(unittest.TestCase):
    def test_a_refusal_with_none_of_them_is_given_the_first(self):
        gp02 = "The warehouse does not hold this figure. The CAISO SP15 hub has no 15-minute real-time rows for 7 November 2026 Pacific time."
        self.assertEqual(ask.with_refusal_words(gp02), "Not in the warehouse. " + gp02)
        self.assertEqual(ask.with_refusal_words("  The table holds no row.  "), "Not in the warehouse. The table holds no row.")
        self.assertEqual(ask.with_refusal_words(""), "Not in the warehouse.")

    def test_a_refusal_that_has_them_is_left_as_written(self):
        for kept in ("Not in the warehouse. The table holds no hours for that day.", "Not in the warehouse this chat reads: x is on Redivis and not in the live set.",
                     "not in the warehouse: no table holds futures.", "License needed. The only table that holds deals is held.",
                     'NYISO\'s rows are held for a license ("license needed").', "MISO is paused while terms are reviewed, so no MISO figure is shown."):
            self.assertEqual(ask.with_refusal_words(kept), kept)

    def test_the_words_are_the_sites(self):
        ts = src("site", "lib", "chat", "refused.ts")
        self.assertIn('export const REFUSAL_WORDS = ["not in the warehouse", "license needed", "paused"];', ts)
        self.assertEqual(list(ask.REFUSAL_WORDS), ["not in the warehouse", "license needed", "paused"])
        self.assertIn(f'export const REFUSAL_FIRST = "{ask.REFUSAL_FIRST}";', ts)
        self.assertIsNone(re.search(r"\d", ask.REFUSAL_FIRST))

    def test_only_the_general_chats_refusals_and_only_refusals(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("if (!profile && draft.not_in_warehouse) draft = { ...draft, answer: withRefusalWords(draft.answer) };", loop)
        self.assertIn("const answer = plain(nodash(draft.answer));", loop)       # session 168's line, as its own test holds it
        py = src("warehouse", "chat", "ask.py")
        self.assertIn('if draft.get("not_in_warehouse") and type(self) is Asker:', py)
        self.assertIn('final = dict(draft, answer=with_refusal_words(draft["answer"]))', py)

    def test_the_two_stored_refusals_without_them_would_have_had_them(self):
        found = []
        for name in ("eval_s5253_site_platform_run.json", "eval_s5273_site_platform_run.json"):
            with open(os.path.join(EVAL, name), encoding="utf-8") as f:
                for q in json.load(f)["questions"]:
                    if q["status"] == "not_in_warehouse" and not any(w in (q["answer"] or "").lower() for w in ask.REFUSAL_WORDS):
                        found.append(q["id"])
                        self.assertTrue(ask.with_refusal_words(q["answer"]).startswith("Not in the warehouse. "))
        self.assertEqual(found, ["oi09", "gp02"])


class AWindowWithNoRow(unittest.TestCase):
    def test_a_table_of_two_steps_and_no_row_is_said_not_held(self):
        w = W.window_of("2026-11-07T08:00:00Z", "2026-11-08T08:00:00Z", ["PT15M", "PT5M"], {"caiso:TH_SP15_GEN-APND|lmp_rtm_15m_mean": []})
        self.assertEqual((w["step"], w["steps_held"], w["steps_in_window"], w["whole"], w["note"]), (None, 0, None, False, W.NONE_HELD_ANY_STEP))
        self.assertNotIn("steps_missing", w)                                 # the window's steps are not counted: which step is not known

    def test_it_is_still_not_told_where_it_cannot_be(self):
        # a row held (which step, and how many should there be?), a window with no step of one of the table's steps, a week's grid
        self.assertIsNone(W.window_of("2026-11-07T08:00:00Z", "2026-11-08T08:00:00Z", ["PT15M", "PT5M"], {"x|y": ["2026-11-07T09:00:00Z"]})["whole"])
        self.assertIsNone(W.window_of("2026-11-10T08:10:00Z", "2026-11-10T08:40:00Z", ["PT1H", "PT5M"], {"x|y": []})["whole"])
        self.assertIsNone(W.window_of("2026-11-02T00:00:00Z", "2026-11-09T00:00:00Z", ["PT1H", "P1W"], {"x|y": []})["whole"])
        self.assertIsNone(W.window_of("2026-11-07T08:00:00Z", "2026-11-08T08:00:00Z", [], {"x|y": []})["whole"])

    def test_the_site_says_the_same(self):
        ts = src("site", "lib", "chat", "window.ts")
        self.assertIn(json.dumps(W.NONE_HELD_ANY_STEP), ts)
        self.assertIn("const note = noneAtAnyStep ? WINDOW_NONE_HELD_ANY_STEP : n === null ? WINDOW_UNKNOWN", ts)


class WhatIsWrittenDown(unittest.TestCase):
    def test_the_method_note(self):
        note = src("docs", "methods", "ask.md")
        self.assertIn("## The chat's effort is medium, and a refusal's fixed words are the loop's (14 November 2026, session 5276)", note)
        self.assertIn("ASK_WRITER_EFFORT=high", note)


if __name__ == "__main__":
    unittest.main()
