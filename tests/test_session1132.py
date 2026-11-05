"""Session 1132 (chain 076): the refusal and the nearest table. Held here: site/scripts/test-ask-1132.mjs passes (a refusal of the general chat names the tables it looked at with what each holds; each answer carries what
its queries read, the table and the window, never a figure; the panel draws the reads, the time the answer took and the
refusal in its own words). No network, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheNearest(unittest.TestCase):
    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1132.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("3 of 3 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
