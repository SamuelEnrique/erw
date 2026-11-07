"""Session 3702 (chain 208): Research's method note holds its replication, its cross-checks and its decisions block
(roadmap item 2). The decisions block's table is replication/analysis/assumptions.json word for word, so the note and
the package cannot drift apart. No network, no warehouse table, no model.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, "docs", "methods", "automated_analysis.md")
ASSUMPTIONS = os.path.join(ROOT, "replication", "analysis", "assumptions.json")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = read(NOTE)
        cls.a = json.loads(read(ASSUMPTIONS))

    def test_the_three_sections(self):
        for title in ("## Replication (session 3701)", "## Cross-checks", "## Decisions: every assumption, its default, its source, how to change it"):
            self.assertIn(title, self.note)

    def test_the_decisions_table_is_the_assumptions_file(self):
        rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| `(\w+)` \|.*\|$", self.note, re.M)}
        keys = [k for k in self.a if k != "_about"]
        self.assertEqual(sorted(rows), sorted(keys))
        for k in keys:
            v = self.a[k]
            value = ", ".join(v["value"]) if isinstance(v["value"], list) else str(v["value"])
            cells = [c.strip() for c in rows[k].strip("|").split(" | ")]
            self.assertEqual(cells[1], value + (f" ({v['unit']})" if v["unit"] else ""), k)
            self.assertEqual(cells[2], v["source"], k)
            self.assertEqual(cells[3], v["change"], k)

    def test_no_em_or_en_dash(self):
        for text in (self.note, read(ASSUMPTIONS), read(__file__)):
            self.assertNotIn(chr(0x2014), text)
            self.assertNotIn(chr(0x2013), text)


if __name__ == "__main__":
    unittest.main()
