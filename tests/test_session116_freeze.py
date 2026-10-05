"""Session 116: the freeze rule (CLAUDE.md rule 9, scripts/freeze.py).

Energy Research Warehouse (ERW). The dated line "Current freeze: 3 October 2026 to 6 October 2026" became a rule: a
freeze begins when a file named REVIEW_FREEZE exists in the repository root, holding its start and end dates, and until
then a deploy with a snapshot is allowed. Every freeze file here is written in a temporary folder: no test creates one
in the repository, and none asserts that the repository has none (a person may declare a freeze any day).

    python -m unittest tests.test_session116_freeze -v
"""

import datetime as dt
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import freeze  # noqa: E402

D = dt.date


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFreezeFile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)

    def root(self, text=None):
        if text is not None:
            with open(os.path.join(self.d.name, "REVIEW_FREEZE"), "w", encoding="utf-8") as f:
                f.write(text)
        return self.d.name

    def test_no_file_is_no_freeze_and_a_deploy_with_a_snapshot_is_allowed(self):
        code, line = freeze.status(self.root(), today=D(2026, 10, 4))
        self.assertEqual(code, 0)
        self.assertIn("no freeze", line)
        self.assertIn("snapshot", line)
        self.assertIsNone(freeze.read(self.root()))

    def test_the_file_freezes_from_its_start_to_its_end_both_included(self):
        root = self.root("start: 2026-10-03\nend: 2026-10-06\n")
        self.assertEqual(freeze.read(root), (D(2026, 10, 3), D(2026, 10, 6)))
        for day, code in ((D(2026, 10, 2), 0), (D(2026, 10, 3), 1), (D(2026, 10, 4), 1), (D(2026, 10, 6), 1), (D(2026, 10, 7), 0)):
            self.assertEqual(freeze.status(root, today=day)[0], code, day)
        self.assertIn("FROZEN from 2026-10-03 to 2026-10-06", freeze.status(root, today=D(2026, 10, 4))[1])
        self.assertIn("To finish", freeze.status(root, today=D(2026, 10, 4))[1])
        self.assertIn("no freeze yet", freeze.status(root, today=D(2026, 10, 2))[1])
        self.assertIn("ended on 2026-10-06", freeze.status(root, today=D(2026, 10, 7))[1])

    def test_notes_and_other_lines_are_allowed(self):
        root = self.root("# a reviewer is using the live site\nreviewer: someone\n\n  Start : 2026-11-01  \nEND: 2026-11-01\n")
        self.assertEqual(freeze.read(root), (D(2026, 11, 1), D(2026, 11, 1)))
        self.assertEqual(freeze.status(root, today=D(2026, 11, 1))[0], 1)

    def test_a_file_that_cannot_be_read_as_two_dates_is_a_freeze_until_a_person_corrects_it(self):
        for what, text in (("empty", ""), ("no end", "start: 2026-10-03\n"), ("no start", "end: 2026-10-06\n"), ("words", "frozen until Tuesday\n"),
                           ("not a date", "start: 3 October 2026\nend: 2026-10-06\n"), ("end before start", "start: 2026-10-06\nend: 2026-10-03\n"),
                           ("twice", "start: 2026-10-03\nstart: 2026-10-04\nend: 2026-10-06\n")):
            code, line = freeze.status(self.root(text), today=D(2030, 1, 1))
            self.assertEqual(code, 2, what)
            self.assertTrue(line.startswith("FROZEN"), what)
            self.assertIn("until a person corrects or removes it", line, what)
        os.remove(os.path.join(self.d.name, "REVIEW_FREEZE"))
        os.mkdir(os.path.join(self.d.name, "REVIEW_FREEZE"))   # there, and not a file
        self.assertEqual(freeze.status(self.d.name, today=D(2030, 1, 1))[0], 2)

    def test_as_a_command_the_exit_code_is_the_answer(self):
        run = lambda: subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "freeze.py"), "status", "--root", self.d.name],  # noqa: E731
                                     capture_output=True, text=True, timeout=60)
        r = run()
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertIn("no freeze", r.stdout)
        self.root("start: 2000-01-01\nend: 2999-12-31\n")
        r = run()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(r.stdout.strip().splitlines()), 1)
        self.root("start: soon\n")
        self.assertEqual(run().returncode, 2)


class TheRule(unittest.TestCase):
    def test_claude_md_states_the_rule_and_no_dated_freeze(self):
        rule = [ln for ln in src("CLAUDE.md").splitlines() if ln.startswith("9. ")]
        self.assertEqual(len(rule), 1)
        rule = rule[0]
        self.assertIn("**A freeze is honoured by every session.**", rule)
        for words in ("`REVIEW_FREEZE`", "repository root", "`start: YYYY-MM-DD`", "`end: YYYY-MM-DD`", "unless its prompt names the one deploy that may",
                      "`wip/` branches", "\"To finish\"", "Until that file exists there is no freeze", "rule 8's snapshot", "python scripts/freeze.py status",
                      "until a person corrects or removes it"):
            self.assertIn(words, rule)
        self.assertNotIn("Current freeze", src("CLAUDE.md"))
        self.assertNotIn("until 6 October", src("CLAUDE.md"))

    def test_the_script_reads_one_file_and_needs_only_the_standard_library(self):
        s = src("scripts", "freeze.py")
        imports = {ln.split()[1].split(".")[0] for ln in s.splitlines() if ln.startswith(("import ", "from "))}
        self.assertEqual(imports - {"argparse", "datetime", "os", "sys"}, set())
        self.assertEqual(freeze.NAME, "REVIEW_FREEZE")
        self.assertNotIn("open(path, \"w\"", s)
        for rel in ("scripts/freeze.py", "tests/test_session116_freeze.py", "CLAUDE.md"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
