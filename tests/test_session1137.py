"""Session 1137 (chain 076): what the board draws, downloadable. Held here: site/scripts/test-board-1137.mjs passes (the
rows the board draws as one CSV from the page's own file after the day's hold: a data-standard header, every figure the
file's, a held grid's row with none; the route is static and under /board, gated with the page).
No network, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheRowsCsv(unittest.TestCase):
    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-board-1137.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("4 of 4 passed", r.stdout)

    def test_the_route_is_under_the_page(self):
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "board", "rows", "route.ts")))


if __name__ == "__main__":
    unittest.main()
