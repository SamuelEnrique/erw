"""Session 5003 (chain 233): /cost-of-power, "if perfectly foreseen" takes the rule's hour budget in a partial year.

Energy Research Warehouse (ERW). The owner's ruling of 12 October 2026 (docs/roadmap.md, "Rulings"), applied in
site/lib/datacenter.ts's weights(). What is held to:

  site/scripts/test-foreseen-5003.mjs passes (a year held in part gets the rule's budget, never more than its hours held);
  the decisions line "foreseen" and the note's section 12 line 7 state the ruling, word for word;
  the note's section 10, item 15, reads closed;
  no em or en dash in what the session wrote.

    python -m unittest tests.test_session5003 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))
LINE = "\"If perfectly foreseen\" chooses the rule's budget of hours knowing the year's prices, in a year held in part as in a whole one, never more than the hours held."


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRuling(unittest.TestCase):
    @unittest.skipIf(shutil.which("node") is None, "node is not installed")
    def test_the_node_test_passes(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-foreseen-5003.mjs")], cwd=os.path.join(ROOT, "site"),
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("8 assertions passed", r.stdout)

    def test_the_library(self):
        lib = src("site", "lib", "datacenter.ts")
        self.assertIn("const k = Math.min(held.length, shedBudget(x, p.length));", lib)
        self.assertNotIn("(x.n * held.length) / p.length", lib)

    def test_the_decision_and_the_note(self):
        lib = src("site", "lib", "decisions.ts")
        self.assertIn('{ key: "foreseen", session: "sessions 138 and 5003", ruling: "the owner\'s ruling of 12 October 2026",', lib)
        self.assertIn(LINE.replace('"', '\\"'), lib)
        note = src("docs", "methods", "datacenter_pays_algorithm.md")
        self.assertIn("7. " + LINE + " (sessions 138 and 5003; the owner's ruling of 12 October 2026)", note)
        self.assertIn("| 15 | A year held in part: the rule's hours and the foreseen load's differ | new | Closed: the owner ruled on 12 October 2026", note)
        self.assertNotIn("waits for a ruling)", note[note.index("## 12."):])

    def test_no_dash(self):
        for parts in (("tests", "test_session5003.py"), ("site", "scripts", "test-foreseen-5003.mjs"), ("site", "lib", "datacenter.ts")):
            for d in DASHES:
                self.assertNotIn(d, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
