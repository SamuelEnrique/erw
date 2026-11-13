"""Session 1744 (chain 195): Research's method note says how to run its replication, and has a block to sign in.

docs/methods/automated_analysis_findings.md had neither: the mirror (site/public/findings/erw_2026_research_replication.py,
session 381) was named only in the review pack and in the cross-checks' prose. This test holds the note's "Replication"
section to the mirror's own list of cards and to the files it names, and the "Sign-off" block to the three decision
tools' form: empty lines to fill. The mirror's run against the cards' JSON is tests/test_session381.py's and 422's.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import ast
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, "docs", "methods", "automated_analysis_findings.md")
FINDINGS = os.path.join(ROOT, "site", "public", "findings")
MIRROR = os.path.join(FINDINGS, "erw_2026_research_replication.py")


def section(text, title):
    m = re.search(r"^## " + re.escape(title) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else None


def mirror_cards():
    with open(MIRROR, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CARDS" for t in node.targets):
            return [elt.elts[0].value for elt in node.value.elts]
    raise AssertionError("CARDS not found in the mirror")


class ResearchNoteReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(NOTE, encoding="utf-8") as f:
            cls.note = f.read()

    def test_sections_present_once_and_before_cross_checks(self):
        for title in ("Replication", "Sign-off"):
            self.assertEqual(len(re.findall(r"^## " + title + r"\n", self.note, re.M)), 1, title)
        self.assertLess(self.note.index("\n## Replication\n"), self.note.index("\n## Sign-off\n"))
        self.assertLess(self.note.index("\n## Sign-off\n"), self.note.index("\n## Cross-checks\n"))

    def test_the_cards_named_are_the_mirrors(self):
        s = section(self.note, "Replication")
        cards = mirror_cards()
        self.assertEqual(len(cards), 10)
        self.assertIn("ten current cards", s)
        for c in cards:
            self.assertIn("`%s`" % c, s)
            self.assertTrue(os.path.exists(os.path.join(FINDINGS, c + ".do")), c)
        self.assertNotIn("batteries_lunch", cards)
        self.assertTrue(os.path.exists(os.path.join(FINDINGS, "batteries_lunch.do")))

    def test_the_cards_py_downloads_still_need_findings_common(self):
        # the section says the generators are not the replication because findings_common is not served beside them
        self.assertFalse(os.path.exists(os.path.join(FINDINGS, "findings_common.py")))
        with open(os.path.join(FINDINGS, "gas_sets_price.py"), encoding="utf-8") as f:
            self.assertIn("from findings_common import", f.read())
        self.assertIn("findings_common", section(self.note, "Replication"))

    def test_sign_off_block_is_empty(self):
        s = section(self.note, "Sign-off")
        for line in ("- Signed off by:", "- Date:", "- Items left open ruled, and how:"):
            self.assertRegex(s, r"(?m)^" + re.escape(line) + r"\s*$")

    def test_no_dashes(self):
        for ch in (chr(0x2014), chr(0x2013)):
            self.assertNotIn(ch, self.note)


if __name__ == "__main__":
    unittest.main()
