"""Session 1486 (chain 158): the board's k03 route fault. A compare call without one of its two queries threw a
TypeError ("Cannot read properties of undefined (reading 'aggregation')") that ended /api/ask with a 502 (session 2918's
grading of session 2886's asking); site/scripts/test-ask-1486.mjs holds that it is now a tool error the model sees. The
board's five, asked again on main's build of 6 November 2026 08:30 UTC, are graded 5 of 5 on session 2918's keys.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


class TheRouteFault(unittest.TestCase):
    def test_compare_without_a_side_is_a_tool_error(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1486.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("4 passed", r.stdout)

    def test_the_guard_is_in_the_tool(self):
        with open(os.path.join(SITE, "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn("compare needs ${side}: the arguments of a query", ts)
        self.assertIn("query needs its arguments as an object", ts)


class TheBoardsFiveAgain(unittest.TestCase):
    def test_five_of_five_on_session_2918s_keys(self):
        with open(os.path.join(EVAL, "eval_s1486_grades.json"), encoding="utf-8") as f:
            g = json.load(f)
        with open(os.path.join(EVAL, "eval_s1486_run.json"), encoding="utf-8") as f:
            run = json.load(f)
        self.assertEqual(sorted(q["id"] for q in run["questions"]), ["k01", "k02", "k03", "k04", "k05"])
        self.assertTrue(all(q["status"] == "answered" and not q.get("error") for q in run["questions"]))
        self.assertEqual((g["right"], g["asked"]), (5, 5))


if __name__ == "__main__":
    unittest.main()
