"""Session 3712 (chain 208): scripts/suite_gate.py runs the whole suite as GitHub's runner does and names the failing
tests, so a gate or a bot's push can say which tests stopped it (docs/state/main_red_2026-11-06.md). No network, no
model; the end-to-end case runs a two-test suite in a temporary folder.
"""
import importlib.util
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def module():
    spec = importlib.util.spec_from_file_location("suite_gate", os.path.join(ROOT, "scripts", "suite_gate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = module()

    def test_both_forms_of_unittests_line(self):
        lines = ["FAIL: test_a (tests.test_x.Things.test_a)", "ERROR: test_b (tests.test_y.More)",
                 "ERROR: setUpClass (tests.test_z.Tables)", "ERROR: test_w (unittest.loader._FailedTest.test_w)",
                 "FAIL: test_a (tests.test_x.Things.test_a)", "some other line"]
        self.assertEqual(self.g.failing(lines), [("FAIL", "tests.test_x.Things.test_a"), ("ERROR", "tests.test_y.More.test_b"),
                                                 ("ERROR", "tests.test_z.Tables.setUpClass"), ("ERROR", "test_w (the module could not be imported)")])

    def test_the_verdict(self):
        self.assertEqual(self.g.verdict(["Ran 12 tests in 1.0s", "", "OK (skipped=2)"]), (12, "OK"))
        self.assertEqual(self.g.verdict(["Ran 12 tests in 1.0s", "", "FAILED (failures=1)"]), (12, "FAILED"))
        self.assertEqual(self.g.verdict(["no summary"]), (None, None))

    def test_no_key_reaches_the_suite(self):
        env = self.g.clean_env({"SUPABASE_SERVICE_KEY": "x", "ANTHROPIC_API_KEY": "y", "GH_TOKEN": "z", "PATH": "p"})
        self.assertEqual(env["PATH"], "p")
        self.assertEqual(env["ERW_LOCK_EXEMPT"], "1")
        for k in ("SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY", "GH_TOKEN"):
            self.assertNotIn(k, env)


class TheRun(unittest.TestCase):
    def test_a_failing_suite_is_named_and_exits_1(self):
        g = module()
        tmp = tempfile.mkdtemp(prefix="erw-s3712-")
        try:
            os.makedirs(os.path.join(tmp, "tests"))
            with open(os.path.join(tmp, "tests", "__init__.py"), "w") as f:
                f.write("")
            with open(os.path.join(tmp, "tests", "test_pair.py"), "w") as f:
                f.write("import unittest\n\nclass Pair(unittest.TestCase):\n    def test_good(self):\n        self.assertTrue(True)\n\n"
                        "    def test_bad(self):\n        self.assertEqual(1, 2)\n")
            code, lines = g.run_suite(tmp, os.path.join(tmp, "out.log"), python=sys.executable)
            names = os.path.join(tmp, "names.txt")
            self.assertEqual(g.report(code, lines, names=names), 1)
            with open(names) as f:
                self.assertEqual(f.read().split(), ["test_pair.Pair.test_bad"])   # discover -s tests: the module is named from inside tests/
            # the passing half alone passes
            with open(os.path.join(tmp, "tests", "test_pair.py"), "w") as f:
                f.write("import unittest\n\nclass Pair(unittest.TestCase):\n    def test_good(self):\n        self.assertTrue(True)\n")
            code, lines = g.run_suite(tmp, os.path.join(tmp, "out.log"), python=sys.executable)
            self.assertEqual(g.report(code, lines), 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


class ThePushGuard(unittest.TestCase):
    """Session 3713: a bot's push to main goes ahead only when the suite passed on its commit; on a failure the tests
    are named, the commit goes to a wip/ branch and the step is recorded failed (the email rule's daily red reads it)."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("push_guard", os.path.join(ROOT, "scripts", "push_guard.py"))
        cls.p = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.p)

    def stand_ins(self, code, names):
        calls = {"push": [], "record": []}

        def run(sha, path, python):
            with open(path, "w", encoding="utf-8") as f:
                f.write("".join(n + "\n" for n in names))
            return code
        return calls, run, (lambda step, why, python: calls["record"].append((step, why))), (lambda sha, br: calls["push"].append(br) or 0)

    def test_a_green_suite_lets_the_push_go(self):
        calls, run, record, push = self.stand_ins(0, [])
        self.assertEqual(self.p.guard("HEAD", "daily prices", "commit", "wip/red-x", run=run, record=record, push=push), 0)
        self.assertEqual(calls, {"push": [], "record": []})

    def test_a_red_suite_refuses_names_and_records(self):
        names = [f"test_session{i}.T.test_{i}" for i in range(8)]
        calls, run, record, push = self.stand_ins(1, names)
        self.assertEqual(self.p.guard("HEAD", "daily prices", "commit", "wip/red-x", run=run, record=record, push=push), 1)
        self.assertEqual(calls["push"], ["wip/red-x"])
        step, why = calls["record"][0]
        self.assertEqual(step, "commit")
        self.assertTrue(why.startswith("push to main refused: 8 failing tests: test_session0.T.test_0"))
        self.assertIn("and 2 more", why)

    def test_never_main_never_task(self):
        calls, run, record, push = self.stand_ins(1, ["a.b.c"])
        for bad in ("main", "task/x"):
            self.assertEqual(self.p.guard("HEAD", "x", None, bad, run=run, record=record, push=push), 2)
        self.assertEqual(calls["push"], [])

    def test_a_dry_run_pushes_and_records_nothing(self):
        calls, run, record, push = self.stand_ins(1, ["a.b.c"])
        self.assertEqual(self.p.guard("HEAD", "x", "commit", "wip/red-x", dry_run=True, run=run, record=record, push=push), 1)
        self.assertEqual(calls, {"push": [], "record": []})
