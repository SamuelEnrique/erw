"""Session 1111 (chain 075): the loop finishes the question.

Held here: the tool-call limit is 12 (8 until 23 October 2026: 11 of session 320's thirty stored answers used all 8),
the same number in ask.py, the rule the model reads and the spec the site reads; a scripted loop that needs nine calls
answers (no model: a fake client replays the turns, and the tool is list_tables over the committed coverage file); an
evaluation's record holds every tool call and its result (ask.py Asker(record_tools=True), which eval.py uses; the
site's route sets it only for a request admitted as an evaluation) and a visitor's never does; a refused answer says
why in one sentence with no figure in it, the same words in both languages.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHAT = os.path.join(ROOT, "warehouse", "chat")
RUN = os.path.join(ROOT, "warehouse", "chat", "eval", "eval_s320_first_run.json")


def chat_ask():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import ask  # noqa: E402
    return ask


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Usage:
    input_tokens = output_tokens = 0
    cache_creation_input_tokens = cache_read_input_tokens = 0


def turn(stop, content):
    return types.SimpleNamespace(stop_reason=stop, content=content, usage=Usage(), _request_id="req_fixture")


class FakeClient:
    """Nine turns of one list_tables call each, then the answer."""
    def __init__(self, calls=9):
        self.calls, self.n = calls, 0
        self.messages = self

    def create(self, **kw):
        self.n += 1
        if self.n <= self.calls:
            b = types.SimpleNamespace(type="tool_use", name="list_tables", input={"sector": "power", "iso": "ERCOT"}, id=f"t{self.n}")
            return turn("tool_use", [b])
        answer = {"answer": "Not in the warehouse: it holds no such table.", "citations": [], "not_in_warehouse": True}
        return turn("end_turn", [types.SimpleNamespace(type="text", text=json.dumps(answer))])


class TheLimit(unittest.TestCase):
    def test_twelve_everywhere(self):
        ask = chat_ask()
        self.assertEqual(ask.MAX_TOOL_CALLS, 12)
        self.assertIn(f"You have at most {ask.MAX_TOOL_CALLS} tool calls.", ask.RULES)
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertEqual(spec["max_tool_calls"], 12)
        self.assertIn("You have at most 12 tool calls.", spec["system"] if isinstance(spec.get("system"), str) else json.dumps(spec))

    def test_the_stored_run_reached_the_old_limit_and_not_the_new(self):
        with open(RUN, encoding="utf-8") as f:
            qs = json.load(f)["questions"]
        counts = [q["tool_calls"] for q in qs]
        self.assertEqual(sorted(q["id"] for q in qs if q["tool_calls"] == 8),
                         ["b01", "b07", "b08", "d03", "d04", "d10", "g03", "g04", "g08", "g09", "g10"])
        self.assertLess(max(counts), chat_ask().MAX_TOOL_CALLS)

    def test_a_question_that_needs_nine_calls_is_answered(self):
        ask = chat_ask()
        rec = ask.Asker(model="claude-sonnet-5-5", client=FakeClient(9)).ask("which ERCOT tables?", today="2026-10-23")
        self.assertEqual(rec["tool_calls"], 9)
        self.assertEqual(rec["status"], "not_in_warehouse")
        self.assertNotIn("trace", rec)

    def test_an_evaluation_records_every_call_and_its_result(self):
        ask = chat_ask()
        rec = ask.Asker(model="claude-sonnet-5-5", client=FakeClient(3), record_tools=True).ask("which ERCOT tables?", today="2026-10-23")
        self.assertEqual(len(rec["trace"]), 3)
        self.assertTrue(all(t["tool"] == "list_tables" and "out" in t for t in rec["trace"]))
        self.assertIn("ask.Asker(record_tools=True)", src("warehouse", "chat", "eval", "eval.py"))

    def test_the_site_records_only_for_an_evaluation(self):
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertIn("const ledgerOpts = evaluation ? { step: EVAL_STEP, strictLedger: true, record: true } : {};", route)
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn('const tracing = process.env.ASK_RECORD_TOOLS === "1" || opts.record === true;', loop)


class TheWhy(unittest.TestCase):
    CASES = [
        ({"bad": ["81.40"]}, "Why: the draft was checked twice and a figure in it was in no tool result."),
        ({"bad": ["1", "2"], "units": ["x"]}, "Why: the draft was checked twice and figures in it were in no tool result and a figure was stated in a unit no tool gave it in."),
        ({"uncited": ["t"], "no_cite": True}, "Why: the draft was checked twice and it cited a table no tool read and it was empty or cited nothing."),
        ({"more": ["followups"]}, "Why: the draft was checked twice and it failed this chat's own checks."),
        ({}, ""),
    ]

    def test_one_sentence_with_no_figure(self):
        ask = chat_ask()
        for kw, want in self.CASES:
            got = ask.why_refused(**kw)
            self.assertEqual(got, want)
            self.assertIsNone(re.search(r"\d", got))
        self.assertTrue((ask.REFUSAL + " " + ask.why_refused(bad=["9"])).startswith("The warehouse does not hold that figure: "))

    def test_the_site_says_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        cases = [{"bad": kw.get("bad", []), "units": kw.get("units", []), "uncited": kw.get("uncited", []),
                  "noCite": kw.get("no_cite", False), "more": kw.get("more", [])} for kw, _ in self.CASES]
        script = ("const { whyRefused } = await import('./lib/chat/ask.ts');"
                  f"process.stdout.write(JSON.stringify({json.dumps(cases)}.map(whyRefused)));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [want for _, want in self.CASES])


if __name__ == "__main__":
    unittest.main()
