"""Audit of the Thesis Builder, finding 13 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the method note
(docs/methods/thesis.md, /data/methods/thesis) said "A number is written only if it appears in a fetched source that its
row cites. A figure that could not be found there is not shown." warehouse/thesis/build.py, check_numbers, replaces a
text under 40 characters (or one with no cited source) by "not confirmed", but a longer text keeps every number and is
followed by "(not confirmed: <the numbers>)". The five runs saved on 6 October 2026 print 80 numbers in 49 texts so,
drawn in the report's tabs as they are.

1. check_numbers keeps a long text's numbers and marks them. Passes on main.
2. The fix on this branch, words only: the note says what the code does. Fails on main. Whether such a sentence is shown
   at all is for Samuel's ruling (wip/audit-home-16, a test only).
Nothing here sets the environment, reads a table or makes a request."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheLiteralNumberCheck(unittest.TestCase):
    def test_a_long_text_keeps_its_numbers(self):
        b = src("warehouse", "thesis", "build.py")
        self.assertIn('return "not confirmed" if len(text) < 40 or not pool else text + f" (not confirmed: {\', \'.join(bad[:4])})"', b)
        self.assertIn("return {\"text\": clean(tb.check_numbers(r, t or \"\", ids, log, where)), \"sources\": ids}", src("warehouse", "thesis", "run.py"))

    def test_the_note_says_so(self):
        note = flat(src("docs", "methods", "thesis.md"))
        self.assertNotIn("A figure that could not be found there is not shown.", note)
        self.assertIn("A sentence (40 characters or more) keeps its words and its numbers and is followed by \"(not confirmed: ...)\", naming each number no cited source holds", note)
        self.assertIn("After a sentence, \"(not confirmed: ...)\" names the numbers in it that no cited source holds", note)


if __name__ == "__main__":
    unittest.main()
