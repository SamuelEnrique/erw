"""Session 10234 (chain 710, part D): the method note of the chat says what the number check proves and what it does not.

docs/reviews/ask-model-audit-2026-11-26.md, finding 3. docs/methods/ask.md said "Every figure in an answer must be a
figure a tool returned in that turn"; the check (warehouse/chat/ask.py unverified) also counts the question's numbers
and the model's own tool arguments as sources, and matches a figure to any number of any source, whichever row, grid,
day or sign it belongs to (tests/test_audit_ask_1.py on wip/audit-ask-1 shows each case). Words only: the note gains a
paragraph that says so. Fails on main, passes on the branch. No model, no network.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "warehouse", "chat")


def note():
    with open(os.path.join(ROOT, "docs", "methods", "ask.md"), encoding="utf-8") as f:
        return f.read()


class TheNoteSaysWhatTheCheckProves(unittest.TestCase):
    def test_the_sources_are_named(self):
        n = note()
        self.assertIn("What the check proves, and what it does not", n)
        for words in ("every tool result, every tool argument", "the question", "the earlier answers and their reads"):
            self.assertIn(words, n)

    def test_what_passes_is_named(self):
        n = note()
        self.assertIn("does not ask which row, grid, day or sign a number belongs to", n)
        self.assertIn("A figure that passes is traced to a source, not proved to be the right figure", n)

    def test_the_words_match_the_code(self):
        # the code's own behaviour, as the paragraph states it: a question's number and a tool argument are sources
        if CHAT not in sys.path:
            sys.path.insert(0, CHAT)
        import ask  # noqa: E402
        self.assertEqual(ask.unverified("It was 200 USD/MWh.", ["Was it 200 USD/MWh?"]), [])
        self.assertEqual(ask.unverified("It peaked at 512.33 USD/MWh.", ['{"threshold": {"above": 512.33}}']), [])
        self.assertEqual(ask.unverified("NYISO averaged 64.27 USD/MWh.", ['{"public_grids": [{"grid": "ERCOT", "value": 64.2746}]}']), [])


if __name__ == "__main__":
    unittest.main()
