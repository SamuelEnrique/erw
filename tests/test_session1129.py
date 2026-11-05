"""Session 1129 (chain 076): a conversation on the general chat. Held here: site/scripts/test-ask-1129.mjs passes (the general chat holds the last three turns as Ask ERCOT does, its first message unchanged with none; each answer carries what
its queries read, the table and the window, never a figure; the panel draws the reads, the time the answer took and the
refusal in its own words). No network, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class AConversation(unittest.TestCase):
    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1129.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("4 of 4 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
