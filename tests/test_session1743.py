"""Session 1743 (chain 195): the Grid tool's method note says how to run its replication, and has a block to sign in.

docs/methods/grid_network.md had neither: the package (site/public/grid/erw_2026_grid_replication.{csv,do,py}, session
266) was named only in the review pack. This test holds the note's "Replication" section to the files it names, runs the
Python mirror on the committed CSV, and checks that every value the do-file's header lists is printed unchanged. The
"Sign-off" block is in the three decision tools' form: empty lines to fill.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, "docs", "methods", "grid_network.md")
GRID = os.path.join(ROOT, "site", "public", "grid")
PY = os.path.join(GRID, "erw_2026_grid_replication.py")
DO = os.path.join(GRID, "erw_2026_grid_replication.do")
CSV = os.path.join(GRID, "erw_2026_grid_replication.csv")


def section(text, title):
    m = re.search(r"^## " + re.escape(title) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else None


class GridNoteReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(NOTE, encoding="utf-8") as f:
            cls.note = f.read()

    def test_sections_present_once_and_before_cross_checks(self):
        for title in ("Replication", "Sign-off"):
            self.assertEqual(len(re.findall(r"^## " + title + r"\n", self.note, re.M)), 1, title)
        self.assertLess(self.note.index("\n## Replication\n"), self.note.index("\n## Sign-off\n"))
        self.assertLess(self.note.index("\n## Sign-off\n"), self.note.index("\n## Cross-checks\n"))
        self.assertIn('<a id="replication"></a>', self.note)

    def test_named_files_exist(self):
        s = section(self.note, "Replication")
        for name in ("erw_2026_grid_replication.csv", "erw_2026_grid_replication.do", "erw_2026_grid_replication.py"):
            self.assertIn(name, s)
            self.assertTrue(os.path.exists(os.path.join(GRID, name)), name)
        for script in ("write-grid-replication.mjs", "check-grid-replication.mjs"):
            self.assertIn(script, s)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "scripts", script)), script)
        self.assertIn('data-decisions="299"', s)
        with open(os.path.join(ROOT, "site", "app", "grid", "page.tsx"), encoding="utf-8") as f:
            self.assertIn('data-decisions="299"', f.read())

    def test_sign_off_block_is_empty(self):
        s = section(self.note, "Sign-off")
        for line in ("- Signed off by:", "- Date:", "- Items left open ruled, and how:"):
            self.assertRegex(s, r"(?m)^" + re.escape(line) + r"\s*$")

    def test_mirror_prints_the_do_files_expected_values(self):
        out = subprocess.run([sys.executable, PY, CSV], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = dict(l.split(" = ", 1) for l in out.stdout.splitlines() if " = " in l)
        self.assertEqual(len(got), 55)
        with open(DO, encoding="utf-8") as f:
            expected = re.findall(r"(?m)^\*\s+([a-z][a-zA-Z_0-9]*) = (\S+)\s*$", f.read())
        self.assertEqual(len(expected), 16)
        for k, v in expected:
            self.assertEqual(got.get(k), v, k)

    def test_no_dashes(self):
        for ch in (chr(0x2014), chr(0x2013)):
            self.assertNotIn(ch, self.note)


if __name__ == "__main__":
    unittest.main()
