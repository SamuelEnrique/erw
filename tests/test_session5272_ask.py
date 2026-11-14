"""Session 5272 (chain 256): a reply cut off at the model's output limit is no longer an error.

Energy Research Warehouse (ERW). The model's thinking counts toward the output limit of a call (16,000 tokens here)
whether or not its text is returned. On 14 November 2026 three askings of the platform set stopped there (gp01 once,
po05 twice: at effort high and at medium, under eleven rules and under ten), each with its figure already in a tool
result; the recorded response is one thinking block and no text. Both loops threw on it: an error for the reader, and
USD 0.27 to 0.31 spent.

Now, in both loops: the cut-off reply is dropped (a thinking block cut short is no turn of the conversation); the model
is told once, and the call after may only write; an answer written then is checked as any other; cut off a second
time, the question ends in words that say what happened, with no figure. Any other stop the loop does not know still
raises. tests/test_session1300.py holds the two loops equal on both cases, turn by turn; here, the Python loop's
conversation, the words, the exported spec and the site's source.

No model, no network: scripted turns over session 1300's fixture rows.
"""
import json
import os
import re
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import test_session1300 as T  # noqa: E402  the fixture's frames and the scripted model
import ask  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Recording(T.Scripted):
    """The scripted model, keeping the conversation each call was sent."""

    def __init__(self, turns):
        super().__init__(turns)
        self.sent = []

    def create(self, **kw):
        self.sent.append([dict(role=m["role"], content=m["content"]) for m in kw["messages"]])
        return super().create(**kw)


def turns(*kinds):
    base = next(s for s in T.load(T.TURNS)["scenarios"] if s["id"] == "answered")
    tool, text = base["turns"]
    return base["question"], [tool if k == "tools" else text if k == "text" else {"cut": True} if k == "cut" else k for k in kinds]


def run(*kinds):
    question, script = turns(*kinds)
    with T.Frames() as frames:
        client = Recording(script)
        asker = ask.Asker(model="claude-sonnet-5-5", client=client)
        frames.load()        # after the asker is made, as tests/test_session1300.py python_loop: making one clears the tools' frames
        rec = asker.ask(question, today=T.load(T.TURNS)["today"])
    return rec, client


def texts(conversation):
    return [m["content"] for m in conversation if m["role"] == "user" and isinstance(m["content"], str)]


class ACutOffReply(unittest.TestCase):
    def test_the_model_is_told_once_and_the_call_after_may_only_write(self):
        rec, client = run("tools", "cut", "text")
        self.assertEqual((rec["status"], rec["cut_off"], rec["retried"], client.n, client.choices), ("answered", 1, False, 3, ["auto", "auto", "none"]))
        self.assertIn("54.481 USD/MWh", rec["answer"])
        last = client.sent[-1]
        self.assertEqual(texts(last)[-1], ask.CUT_OFF)                        # the last thing the model was sent: the cut-off's words
        # the cut-off reply is not in the conversation: one assistant turn (the tool call), then its result, then the words
        self.assertEqual([m["role"] for m in last], ["user", "assistant", "user", "user"])
        self.assertFalse(any(getattr(b, "type", None) == "thinking" for m in last if m["role"] == "assistant" for b in m["content"]))

    def test_the_cut_off_call_is_counted_in_the_answers_usage(self):
        rec, client = run("tools", "cut", "text")
        self.assertEqual(rec["usage"]["requests"], 3)                         # the call that was cut off was paid for, and is counted
        self.assertEqual(len(rec["request_ids"]), 3)

    def test_cut_off_twice_the_question_ends_in_words_with_no_figure_and_no_error(self):
        rec, client = run("tools", "cut", "cut")
        self.assertEqual((rec["status"], rec["cut_off"], client.n, client.choices), ("refused_unverified", 2, 3, ["auto", "auto", "none"]))
        self.assertEqual((rec["answer"], rec["why"], rec["citations"], rec["not_in_warehouse"]), (ask.CUT_OFF_ANSWER, ask.CUT_OFF_WHY, [], False))
        self.assertIsNone(re.search(r"\d", rec["answer"] + rec["why"]))

    def test_a_cut_off_before_any_tool_call_is_handled_the_same(self):
        rec, client = run("cut", "tools", "text")
        # the first reply is cut off; told to write, the scripted model asks for a tool all the same: the loop allows none
        # (tool_choice none), so in the real API no tool block comes back. The script's tool turn stands for a model that
        # ignores it: its call is made only because this stand-in returns it, and the answer after it stands
        self.assertEqual(client.choices[:2], ["auto", "none"])
        self.assertEqual(texts(client.sent[1]), [texts(client.sent[0])[0], ask.CUT_OFF])
        self.assertEqual(rec["cut_off"], 1)

    def test_an_answer_after_a_cut_off_is_still_checked(self):
        question, script = turns("tools", "cut", "text")
        wrong = json.loads(json.dumps(script[2]))
        wrong["text"]["answer"] = wrong["text"]["answer"].replace("54.481", "61.25")
        with T.Frames() as frames:
            client = Recording([script[0], {"cut": True}, wrong, wrong])
            asker = ask.Asker(model="claude-sonnet-5-5", client=client)
            frames.load()
            rec = asker.ask(question, today=T.load(T.TURNS)["today"])
        self.assertEqual((rec["status"], rec["retried"], rec["cut_off"]), ("refused_unverified", True, 1))
        self.assertTrue(rec["answer"].startswith(ask.REFUSAL))                # the number check's refusal, not the cut-off's

    def test_a_stop_the_loop_does_not_know_still_raises(self):
        question, script = turns("tools")

        class Odd(T.Scripted):
            def create(self, **kw):
                if self.n == 1:
                    self.n += 1
                    return types.SimpleNamespace(stop_reason="pause_turn", content=[], usage=T.Usage(), _request_id="req_fixture")
                return super().create(**kw)
        with T.Frames() as frames:
            asker = ask.Asker(model="claude-sonnet-5-5", client=Odd(script))
            frames.load()
            with self.assertRaises(RuntimeError) as e:
                asker.ask(question, today=T.load(T.TURNS)["today"])
        self.assertIn("stop_reason pause_turn", str(e.exception))


class TheWordsAndTheSite(unittest.TestCase):
    def test_the_words_state_no_figure_and_say_what_to_do(self):
        self.assertIn("cut off at the output limit before anything was written", ask.CUT_OFF)
        self.assertIn("do not call a tool", ask.CUT_OFF)
        self.assertIn("from the tool results above", ask.CUT_OFF)
        self.assertIn('answer "not in the warehouse"', ask.CUT_OFF)
        for words in (ask.CUT_OFF, ask.CUT_OFF_ANSWER, ask.CUT_OFF_WHY):
            self.assertIsNone(re.search(r"\d", words), words)
            self.assertNotIn(chr(0x2014), words)
        self.assertTrue(ask.CUT_OFF_WHY.startswith("Why: "))                  # as the number check's reason line begins

    def test_the_sites_spec_holds_the_same_words(self):
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertEqual((spec["cut_off"], spec["cut_off_answer"], spec["cut_off_why"]), (ask.CUT_OFF, ask.CUT_OFF_ANSWER, ask.CUT_OFF_WHY))
        self.assertEqual(spec["max_tokens"], ask.MAX_TOKENS)                  # the limit itself is not changed

    def test_the_sites_loop_does_the_same(self):
        a = src("site", "lib", "chat", "ask.ts")
        block = a[a.index('if (resp.stop_reason === "max_tokens") {'):a.index('if (resp.stop_reason !== "end_turn") throw')]
        for words in ("messages.pop();", "cutOff += 1;", "messages.push({ role: \"user\", content: spec.cut_off });", "forceWrite = true;", "continue;",
                      'answer: spec.cut_off_answer, why: spec.cut_off_why, citations: [], not_in_warehouse: false, status: "refused_unverified" as const'):
            self.assertIn(words, block, words)
        self.assertIn("...(cutOff ? { cut_off: cutOff } : {})", a)             # an answer that had a cut-off says so
        self.assertIn("if (resp.stop_reason !== \"end_turn\") throw new Error(`stop_reason ${resp.stop_reason}`);", a)   # any other unknown stop still throws

    def test_the_turn_by_turn_fixture_holds_both_cases(self):
        ids = [s["id"] for s in T.load(T.TURNS)["scenarios"]]
        self.assertIn("an_answer_cut_off_then_written", ids)
        self.assertIn("an_answer_cut_off_twice", ids)
        self.assertIn('reply.cut ? "max_tokens"', src("site", "scripts", "run-ask-turns-1300.mjs"))


if __name__ == "__main__":
    unittest.main()
