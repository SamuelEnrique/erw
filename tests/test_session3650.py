"""Session 3650: the problem sets an instructor can assign (site/lib/problemkit.ts, site/lib/problems.ts, /learn/problems).

Energy Research Warehouse (ERW). No network, no model, no build. Runs the node tests of site/scripts/test-problemkit.mjs
(each set's outcome line, grids, tables and skills; the worked example and the five in a rising order; each question's
one-line computation with no typed number; every figure's source as its hover; the CSV of each set's figures, public
rows only; the instructors' hover on the index) and reads their exit code.

    python -m unittest tests.test_session3650 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class ProblemKit(unittest.TestCase):
    def test_node_tests_pass(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        r = subprocess.run([node, "--no-warnings", "--test", "scripts/test-problemkit.mjs"], cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-4000:])


if __name__ == "__main__":
    unittest.main()
