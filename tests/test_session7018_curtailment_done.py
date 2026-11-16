"""Session 7018 (chain 301): /curtailment at the done line. Its decisions are one list (site/lib/decisions.ts, CURTAILMENT_DECISIONS),
drawn at the foot of the page by the shared block with each choice's default and source on hover, and written word for
word in docs/methods/curtailment.md; the note carries the replication, the cross-checks, what waits for the owner and a
sign-off. No request, no model call."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
from test_session7402_trackers import decisions, line_of, note_lines, src  # noqa: E402

NAME, NOTE, PAGE = "CURTAILMENT_DECISIONS", ("docs", "methods", "curtailment.md"), ("site", "app", "curtailment", "page.tsx")


class TheCurtailment(unittest.TestCase):
    def test_every_choice_has_its_session_default_and_source(self):
        rows = decisions(NAME)
        self.assertGreaterEqual(len(rows), 8)
        self.assertLessEqual(len(rows), 14)
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        s = src("site", "lib", "decisions.ts")
        part = s[s.index(f"export const {NAME}"):]
        self.assertEqual(part[:part.index("\n];")].count("{ key: "), len(rows))
        for key, session, ruling, text, d, source in rows:
            self.assertRegex(session, r"^sessions? \d{2,4}", key)
            self.assertGreater(len(text), 60, key)
            self.assertGreater(len(d), 15, key)
            self.assertGreater(len(source), 25, key)

    def test_the_note_carries_the_list_word_for_word(self):
        rows = decisions(NAME)
        self.assertEqual(note_lines(*NOTE), [line_of(i, r) for i, r in enumerate(rows, 1)])

    def test_the_page_draws_the_block_once_before_the_downloads(self):
        p = src(*PAGE)
        self.assertEqual(p.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="7018-curtailment" title="Decisions on this page (each with its default and its source on hover)" items={CURTAILMENT_DECISIONS} />', p)
        self.assertLess(p.index("<DecisionsBlock "), p.index("<TableDownloads "))
        self.assertIn('import { CURTAILMENT_DECISIONS } from "@/lib/decisions";', p)

    def test_the_note_has_the_done_lines_parts(self):
        n = src(*NOTE)
        for head in ("## The replication (session 7014, chain 301)", "## The cross-checks (session 7018, chain 301)",
                     "## The decisions on the page (session 7018, chain 301)", "## What waits for the owner (session 7018)", "## Sign-off"):
            self.assertIn("\n" + head + "\n", n, head)
        for line in ("- Signed off by:", "- Date:", "- Items of the section above ruled, and how:"):
            self.assertIn("\n" + line, n)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "replication", "curtailment", "replicate.py")))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "replication", "curtailment", "replicate.do")))
        cross = n[n.index("## The cross-checks (session 7018"):n.index("## The decisions on the page (session 7018")]
        self.assertIn("| CAISO's wind and solar curtailed, 2024 | 3.4 million MWh | 3,423,377 MWh", cross)
        self.assertIn("11,515 of 11,515", cross)
        self.assertNotIn(chr(0x2014), n)


if __name__ == "__main__":
    unittest.main()
