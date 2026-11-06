"""Session 1311 (chain 095): the board's rows' CSV says the held rows as the page's lines do. Held here:
site/scripts/test-board-1311.mjs passes (the header counts the held rows by grid; each held line carries the hold's
words in its last column, `hold`, and no other line does), on the site's own file after the day's hold.
No network, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheCsv(unittest.TestCase):
    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-board-1311.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("2 of 2 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
