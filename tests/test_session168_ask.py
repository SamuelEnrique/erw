"""Session 168, part C: Ask ERCOT's times in plain local words, and the question without a stray quote mark.

No model call. The functions are tested by site/scripts/test-ask-168.mjs and the loop, with a stand-in for the model
and the recorded reads of tests/fixtures/session143, by site/scripts/test-ask-speed.mjs; both are run here when node
and the site's modules are present. Asserts on file contents and behaviour, never on a branch.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class PlainTimes(unittest.TestCase):
    def test_the_tool_gives_local_words_and_the_answer_shows_no_stamp(self):
        self.assertIn('if (shape === "series") addLocalTimes(out, dated, tz !== "UTC" ? tz : zoneOfEntity(', src("site", "lib", "chat", "tools.ts"))
        ask = src("site", "lib", "chat", "ask.ts")
        self.assertIn("const answer = plain(nodash(draft.answer));", ask)
        self.assertIn("answer: plain(nodash(words))", ask)
        self.assertIn('zone: "America/Chicago",', src("site", "lib", "chat", "ercot.ts"))

    def test_the_question_is_cleaned_where_it_is_asked_and_echoed(self):
        self.assertIn("const asked = cleanQuestion(question);", src("site", "app", "api", "ask", "route.ts"))
        self.assertIn("const question = cleanQuestion(typed);", src("site", "components", "ask", "AskPanel.tsx"))

    def test_the_node_tests(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(SITE, "node_modules")):
            self.skipTest("node or the site's modules are absent: node --import ./scripts/alias-register.mjs scripts/test-ask-168.mjs")
        for script in ("scripts/test-ask-168.mjs", "scripts/test-ask-speed.mjs"):
            r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", script], cwd=SITE, capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, (script, (r.stdout + r.stderr)[-2000:]))

    def test_no_em_dash(self):
        for parts in (("site", "lib", "chat", "plaintime.ts"), ("site", "scripts", "test-ask-168.mjs"), ("tests", "test_session168_ask.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
