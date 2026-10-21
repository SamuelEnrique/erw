"""Session 534: the runner that moves the clock forward, and the tests it found pinned to a day.

scripts/suite_shifted.py runs the suite with scripts/clock_shift/ on PYTHONPATH (a
sitecustomize that shifts time and datetime) and NODE_OPTIONS requiring a Date shim.
These tests prove the shift reaches a python child and a node child, that a child with
no shift set reads the real clock, that the runner drops the keys that write, and that
it reads unittest's FAIL and ERROR lines.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "suite_shifted.py"
SHIM_DIR = ROOT / "scripts" / "clock_shift"


def real_now(tz=None):
    """The real clock, also when this test runs inside a shifted suite."""
    return datetime.now(tz) - timedelta(seconds=float(os.environ.get("ERW_CLOCK_SHIFT_SECONDS") or 0))


def load_runner():
    spec = importlib.util.spec_from_file_location("suite_shifted_534", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ShiftReachesChildren(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()

    def _py(self, env):
        code = ("import datetime, time, pandas as pd;"
                "print(datetime.date.today().isoformat(), datetime.datetime.now(datetime.timezone.utc).date().isoformat(),"
                " time.strftime('%Y-%m-%d', time.gmtime()), pd.Timestamp.now('UTC').date().isoformat(),"
                " isinstance(datetime.datetime(2020, 1, 1), datetime.datetime))")
        return subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=120)

    def test_python_child_reads_the_clock_thirty_days_ahead(self):
        env = self.runner.child_env(30)
        r = self._py(env)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        local_want = (real_now() + timedelta(days=30)).date().isoformat()
        utc_want = (real_now(timezone.utc) + timedelta(days=30)).date().isoformat()
        got = r.stdout.split()
        self.assertEqual(got[0], local_want)
        self.assertEqual(got[1:4], [utc_want] * 3)
        self.assertEqual(got[4], "True", "a datetime built from values is still a datetime")

    def test_no_shift_reads_the_real_clock(self):
        env = self.runner.child_env(0)
        self.assertNotIn("ERW_CLOCK_SHIFT_SECONDS", env)
        self.assertNotIn(str(SHIM_DIR), env.get("PYTHONPATH", ""))
        r = self._py(env)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertEqual(r.stdout.split()[1], real_now(timezone.utc).date().isoformat())

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_node_child_reads_the_clock_seven_days_ahead(self):
        env = self.runner.child_env(7)
        r = subprocess.run(["node", "-e", "console.log(new Date().toISOString().slice(0,10), new Date(Date.now()).toISOString().slice(0,10), new Date(0).toISOString().slice(0,4), new Date() instanceof Date)"],
                           env=env, capture_output=True, text=True, timeout=60, shell=(os.name == "nt"))
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        want = (real_now(timezone.utc) + timedelta(days=7)).date().isoformat()
        self.assertEqual(r.stdout.split(), [want, want, "1970", "true"])

    def test_keys_that_write_are_dropped(self):
        saved = dict(os.environ)
        try:
            os.environ.update({"SUPABASE_SERVICE_KEY": "x", "ANTHROPIC_API_KEY": "x", "RESEND_API_KEY": "x", "GH_TOKEN": "x", "SUPABASE_URL": "u"})
            env = self.runner.child_env(7)
        finally:
            os.environ.clear()
            os.environ.update(saved)
        for k in ("SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY", "RESEND_API_KEY", "GH_TOKEN"):
            self.assertNotIn(k, env)
        self.assertEqual(env["SUPABASE_URL"], "u")
        self.assertEqual(env["ERW_LOCK_EXEMPT"], "1")
        self.assertEqual(env["ERW_CLOCK_SHIFT_SECONDS"], str(7 * 86400))

    def test_reads_unittest_failure_lines(self):
        text = ("ERROR: test_a (test_session1.A.test_a)\n----\nFAIL: test_b (test_session2.B.test_b)\n"
                "FAIL: test_b (test_session2.B.test_b)\nok\n")
        self.assertEqual(self.runner.failures(text), {"ERROR test_session1.A.test_a", "FAIL test_session2.B.test_b"})

    def test_the_shim_does_nothing_unset(self):
        text = (SHIM_DIR / "sitecustomize.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("ERW_CLOCK_SHIFT_SECONDS"', text)
        js = (SHIM_DIR / "date_shift.cjs").read_text(encoding="utf-8")
        self.assertIn("process.env.ERW_CLOCK_SHIFT_SECONDS", js)

    def test_no_em_dash_in_the_session_files(self):
        dash = chr(0x2014)
        for p in [RUNNER, SHIM_DIR / "sitecustomize.py", SHIM_DIR / "date_shift.cjs", Path(__file__)]:
            self.assertNotIn(dash, p.read_text(encoding="utf-8"), p.name)


if __name__ == "__main__":
    unittest.main()
