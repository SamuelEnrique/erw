"""The suite in batches (session 4000, chain 228; roadmap item 1): scripts/suite_batches.py runs the tests discover runs, in
its order, as several processes, and prints unittest's own summary for the whole; scripts/land_check.py uses it on a
machine with under 12 GB of memory, or when --suite-batch says. A small tests folder is made in a temporary directory:
one passing module, one failing, one that cannot be imported, one that raises SkipTest at import, one whose process
dies mid-run. No network, no key, no build."""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import suite_batches as SB  # noqa: E402
import land_check as LC  # noqa: E402

RUNNER = os.path.join(ROOT, "scripts", "suite_batches.py")

MODS = {
    "test_a_pass.py": """
        import unittest
        class A(unittest.TestCase):
            def test_one(self): self.assertTrue(True)
            def test_two(self): self.assertEqual(2, 1 + 1)
            @unittest.skip("not here")
            def test_skipped(self): pass
    """,
    "test_b_fail.py": """
        import unittest
        class B(unittest.TestCase):
            def test_wrong(self): self.assertEqual(1, 2)
            def test_right(self): pass
    """,
    "test_c_import.py": """
        import no_such_module_anywhere_4000
    """,
    "test_d_skipmod.py": """
        import unittest
        raise unittest.SkipTest("this module is skipped whole")
    """,
    "test_e_helper.py": """
        import unittest
        import helper_4000   # a plain module beside the tests, found as discover finds it (tests/ on sys.path)
        class E(unittest.TestCase):
            def test_helper(self): self.assertEqual(helper_4000.X, 4000)
    """,
    "helper_4000.py": "X = 4000\n",
    "not_a_test.py": "raise RuntimeError('never imported')\n",
}
DIES = """
    import os, unittest
    class F(unittest.TestCase):
        def test_dies(self): os._exit(3)
"""


def make(tmp, extra=None):
    d = os.path.join(tmp, "tests")
    os.makedirs(d)
    for name, body in {**MODS, **(extra or {})}.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(body))
    return d


def run(argv, cwd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, *argv], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, stdin=subprocess.DEVNULL, timeout=300)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def closing(out):
    """The last 'Ran' line's count and the last verdict line."""
    lines = out.splitlines()
    ran = [ln for ln in lines if ln.startswith("Ran ")][-1]
    verdict = [ln for ln in lines if ln.startswith(("OK", "FAILED"))][-1]
    return int(ran.split()[1]), verdict


class ThePlan(unittest.TestCase):
    def test_batches_keep_the_order_and_set_alone_modules_apart(self):
        mods = [f"test_{i:02d}" for i in range(7)]
        self.assertEqual(SB.batches(mods, 3), [mods[0:3], mods[3:6], mods[6:7]])
        self.assertEqual(SB.batches(mods, 3, {"test_04"}), [mods[0:3], ["test_03"], ["test_04"], ["test_05", "test_06"]])
        self.assertEqual(sum(SB.batches(mods, 2, {"test_00", "test_06"}), []), mods)

    def test_modules_are_discovers_files_in_name_order(self):
        tmp = tempfile.mkdtemp()
        try:
            d = make(tmp)
            self.assertEqual(SB.modules(d), ["test_a_pass", "test_b_fail", "test_c_import", "test_d_skipmod", "test_e_helper"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_summary_reads_back_as_unittests(self):
        got = SB.parse(SB.summary(12, 3.5, dict.fromkeys(SB.COUNTS, 0) | {"skipped": 2}) + ["suite_batches: peak MB 99"])
        self.assertEqual((got[0], got[2]["skipped"], got[3]), (12, 2, 99))
        fail = SB.summary(5, 1.0, dict.fromkeys(SB.COUNTS, 0) | {"failures": 1, "errors": 2})
        self.assertEqual(fail[-1], "FAILED (failures=1, errors=2)")
        self.assertIsNone(SB.parse(["....", "Traceback (most recent call last):", "MemoryError"]))

    def test_the_alone_file_takes_names_in_any_form(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "alone.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# heavy\ntest_session59\ntests.test_session1898  # the grids\ntest_session3701.py\n\n")
            self.assertEqual(SB.read_alone(p), {"test_session59", "test_session1898", "test_session3701"})
            self.assertEqual(SB.read_alone(os.path.join(tmp, "absent.txt")), set())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TheRun(unittest.TestCase):
    def test_batches_give_discovers_counts(self):
        tmp = tempfile.mkdtemp()
        try:
            make(tmp)
            c1, out1 = run(["-m", "unittest", "discover", "-s", "tests"], tmp)
            c2, out2 = run([RUNNER, "--batch", "2"], tmp)
            self.assertEqual((c1, c2), (1, 1), out2)
            self.assertEqual(closing(out1), closing(out2), out2)
            # discover: 3 + 2 + 1 (import) + 1 (skipped module) + 1 = 8 tests; 1 failure, 1 error, 2 skipped
            self.assertEqual(closing(out2), (8, "FAILED (failures=1, errors=1, skipped=2)"))
            self.assertIn("FAIL: test_wrong (test_b_fail.B.test_wrong)", out2)
            self.assertIn("in 3 processes", out2)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_passing_suite_exits_0(self):
        tmp = tempfile.mkdtemp()
        try:
            make(tmp)
            c, out = run([RUNNER, "--batch", "1", "test_a_pass", "test_e_helper"], tmp)
            self.assertEqual(c, 0, out)
            self.assertEqual(closing(out), (4, "OK (skipped=1)"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_dead_process_is_run_again_alone_and_named(self):
        tmp = tempfile.mkdtemp()
        try:
            make(tmp, {"test_c2_dies.py": DIES})
            c, out = run([RUNNER, "--batch", "10", "test_a_pass", "test_c2_dies", "test_e_helper"], tmp)
            self.assertEqual(c, 1, out)
            self.assertIn("stopped without a summary", out)
            self.assertIn("ERROR: test_c2_dies (suite_batches.test_c2_dies)", out)
            # the other two modules still counted, run alone: 3 + 1 tests, and the lost module one error
            self.assertEqual(closing(out), (4, "FAILED (errors=1, skipped=1)"))
            import suite_gate
            self.assertIn(("ERROR", "suite_batches.test_c2_dies"), suite_gate.failing(out.splitlines()))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_profile_writes_each_modules_peak(self):
        tmp = tempfile.mkdtemp()
        try:
            make(tmp)
            prof = os.path.join(tmp, "prof.csv")
            run([RUNNER, "--profile", prof, "test_a_pass", "test_e_helper"], tmp)
            with open(prof, encoding="utf-8") as f:
                rows = f.read().splitlines()
            self.assertEqual(rows[0], "module,tests,seconds,peak_mb")
            self.assertEqual(sorted(r.split(",")[0] for r in rows[1:]), ["test_a_pass", "test_e_helper"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Ops:
    def __init__(self, mb=None, exists=True):
        self.calls, self.mb, self.ex = [], mb, exists
        if mb is not None:
            self.total_mb = lambda: self.mb

    def run(self, step, argv, cwd, log, env=None, timeout=None):
        self.calls.append((step, argv))
        return 0

    def read(self, path):
        return "Ran 9 tests in 1.0s\n\nOK\n"

    def exists(self, path):
        return self.ex


class TheGate(unittest.TestCase):
    def gate(self, ops, batch=None):
        a = types.SimpleNamespace(worktree=None, port=3700, lock_as=None, suite_batch=batch)
        return LC.Gate("0123456789abcdef", a, ops, root=ROOT, main=ROOT, out=lambda *x: None)

    def suite_argv(self, ops, batch=None):
        g = self.gate(ops, batch)
        state, code, note = g.s_suite()
        return [c for c in ops.calls if c[0] == "suite"][0][1], note

    def test_an_8_gb_machine_runs_batches(self):
        argv, note = self.suite_argv(Ops(mb=8 * 1024))
        self.assertEqual(argv[1:4], [os.path.join(ROOT, "scripts", "suite_batches.py"), "--batch", str(LC.AUTO_BATCH)])
        self.assertIn("in batches of 40 modules", note)

    def test_a_16_gb_machine_and_an_unknown_one_run_one_process(self):
        for ops in (Ops(mb=16 * 1024), Ops()):
            argv, note = self.suite_argv(ops)
            self.assertEqual(argv[1:], ["-m", "unittest", "discover", "-s", "tests"])
            self.assertNotIn("batches", note)

    def test_the_flag_decides(self):
        self.assertEqual(self.suite_argv(Ops(mb=8 * 1024), batch=0)[0][1:], ["-m", "unittest", "discover", "-s", "tests"])
        self.assertEqual(self.suite_argv(Ops(mb=64 * 1024), batch=25)[0][2:4], ["--batch", "25"])
        self.assertEqual(LC.parse(["--suite-batch", "10"]).suite_batch, 10)
        self.assertIsNone(LC.parse([]).suite_batch)

    def test_the_suite_runs_its_maths_on_one_thread(self):
        # numpy's OpenBLAS commits a buffer a thread at import: 702 MB on the desktop's 20 threads, 91 MB on one
        import suite_gate
        for env in (LC.suite_env({"PATH": "x", "GH_TOKEN": "t"}), suite_gate.clean_env({"PATH": "x", "GH_TOKEN": "t"})):
            self.assertEqual(env["OPENBLAS_NUM_THREADS"], "1")
            self.assertEqual(env["OMP_NUM_THREADS"], "1")
            self.assertNotIn("GH_TOKEN", env)
        self.assertEqual(SB.ONE_THREAD, LC.ONE_THREAD)

    def test_no_runner_in_the_checkout_falls_back_to_one_process(self):
        argv, _ = self.suite_argv(Ops(mb=8 * 1024, exists=False))
        self.assertEqual(argv[1:], ["-m", "unittest", "discover", "-s", "tests"])


if __name__ == "__main__":
    unittest.main()
