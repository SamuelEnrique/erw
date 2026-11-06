"""Session 1193 (chain 089): the board says a group's held grid once. Held here: site/scripts/test-board-1193.mjs passes
(lib/board.ts heldLines on the site's own file after the day's hold: every row kept, a held line one grid's rows, the
shown rows' order unchanged; the board draws the line with its count, the hold's words and a toggle, its rows hidden
until asked), and site/scripts/check-board.mjs checks the drawn lines on a build.
No network, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheHeldLines(unittest.TestCase):
    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-board-1193.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("5 of 5 passed", r.stdout)

    def test_the_build_check_reads_the_lines(self):
        with open(os.path.join(SITE, "scripts", "check-board.mjs"), encoding="utf-8") as f:
            body = f.read()
        self.assertIn("b.heldLines(", body)
        self.assertIn("data-held-line=", body)


if __name__ == "__main__":
    unittest.main()
