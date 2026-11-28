"""wip/ready-ask-held-heading (session 11406, chain 770, part C): the other choice of the chat audit of 26 November,
finding 8 (docs/reviews/ask-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main a question about a held grid's rows is answered with the hold's words and the public grids' figures, and its
status "answered" is headed "Answered from the warehouse" on /ask. On this branch the site's loop marks such an answer
(held_grid, set when a tool answered with the hold's words) and /ask heads it "Held for a license; the public grids'
figures". The status itself, the answer's words and every check stay as they are. Measured by the audit: 45 of the 48
stored held-grid questions ended "answered" and would take the new heading (no answer's words change). The Python loop
(warehouse/chat/ask.py, the evaluations') is not changed here."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AHeldGridsAnswerHasItsHeading(unittest.TestCase):
    def test_the_loop_marks_it(self):
        s = src("site", "lib", "chat", "ask.ts")
        self.assertIn("let heldGrid = false;", s)
        self.assertIn("if (!isError && out.held) heldGrid = true;", s)
        self.assertIn("...(heldGrid ? { held_grid: true } : {}) });", s)
        self.assertIn("held_grid?: boolean;", s)
        self.assertIn("held: true, grid: name, grid_license: LICENSE_NEEDED", src("site", "lib", "chat", "tools.ts"))   # what sets out.held

    def test_the_page_heads_it(self):
        s = src("site", "app", "ask", "AskForm.tsx")
        self.assertIn('const HELD_HEADING = "Held for a license; the public grids\' figures";', s)
        self.assertIn('{res.status === "answered" && res.held_grid ? HELD_HEADING : STATUS[res.status] ?? res.status}', s)
        self.assertIn('answered: "Answered from the warehouse",', s)   # every other answer keeps its heading


if __name__ == "__main__":
    unittest.main()
