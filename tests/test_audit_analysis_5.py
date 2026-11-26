"""Audit of Automated Analysis, finding 5 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the deep
hunt, the engine of every draft in docs/findings/ and of all forty of the sheet, had no method note.

docs/methods/automated_analysis_findings.md now has a section "The deep hunt (chains 164 and 502)" that says what
warehouse/analysis/findings/deep/builder.py does. Held to the code: the two caps the section names are the builder's
own constants, the tests are hunt.test_claim's, the held-grid check is by the region's name, and no statistics block is
built. Words only: no figure moves. Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class DeepHuntHasItsNote(unittest.TestCase):
    def section(self):
        note = text("docs", "methods", "automated_analysis_findings.md")
        m = re.search(r"^## The deep hunt \(chains 164 and 502\)\n(.*?)(?=^## )", note, re.M | re.S)
        self.assertIsNotNone(m, "the note has no section on the deep hunt")
        return m.group(1)

    def test_section_names_the_code(self):
        s = self.section()
        for words in ("warehouse/analysis/findings/deep/builder.py", "hunt.test_claim", "scan-deep-", "hunt.grid_of(region)",
                      "No `statistics` block", "not a test against chance"):
            self.assertIn(words, s)

    def test_caps_are_the_builders(self):
        s = self.section()
        b = text("warehouse", "analysis", "findings", "deep", "builder.py")
        per = int(re.search(r"^MAX_PER_CANDIDATE = (\d+)", b, re.M).group(1))
        most = int(re.search(r"^MAX_DRAFTS = (\d+)", b, re.M).group(1))
        words = {1: "one", 2: "two", 3: "three", 10: "ten", 12: "twelve"}
        self.assertIn(f"at most {words[per]} regions of one candidate (`MAX_PER_CANDIDATE`)", s)
        self.assertIn(f"{words[most]} drafts a family's session (`MAX_DRAFTS`)", s)
        self.assertIn("hunt.grid_of(region) in blocked", b)
        for name in ("step_or_trend", "trend_p", "q_bh"):
            self.assertNotIn(name, b)

    def test_no_em_dash(self):
        for p in (("docs", "methods", "automated_analysis_findings.md"), ("tests", "test_audit_analysis_5.py")):
            self.assertNotIn(chr(0x2014), text(*p))


if __name__ == "__main__":
    unittest.main()
