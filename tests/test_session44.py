"""Session 44: the problem sets (site/lib/problems.ts).

Energy Research Warehouse (ERW). No network, no model. The answers are computed on the server from Supabase and checked
by site/scripts/check-values.mjs; this test checks the definitions: three sets of five questions, each question with
tables, an answer, steps and a why, and no answer written as a number literal (every number in an answer is a
computed V, so a typed figure cannot slip in).

    python -m unittest tests.test_session44 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with open(os.path.join(ROOT, "site", "lib", "problems.ts"), encoding="utf-8") as f:
    SRC = f.read()


class ProblemSets(unittest.TestCase):
    def test_three_sets_of_five(self):
        self.assertEqual(len(re.findall(r'\{ slug: "', SRC)), 4)  # session 46: set D, storage and taxes
        for s in "abcd":
            ids = re.findall(rf'(?:id: |billQ\()"{s}(\d)"', SRC)
            self.assertEqual(sorted(ids), ["1", "2", "3", "4", "5"], s)

    def test_every_question_has_its_parts(self):
        for block in re.split(r"const q\d: Question = |billQ = \(", SRC)[1:]:
            for part in ("tables:", "q:", "answer:", "steps:", "why:"):
                self.assertIn(part, block[:3000], part)

    def test_answers_carry_no_typed_numbers(self):
        for m in re.finditer(r"answer: \[(.*?)\],\n", SRC, flags=re.S):
            body = m.group(1)
            # strings may hold dates and hours from the data (template literals); outside strings, no numeric literal
            outside = re.sub(r'`[^`]*`|"[^"]*"', "", body)
            self.assertIsNone(re.search(r"(?<![\w.])\d+(\.\d+)?(?![\w])", outside), body[:120])


if __name__ == "__main__":
    unittest.main()
