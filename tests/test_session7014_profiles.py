"""Session 7014 (chain 301): the mix and curtailment profiles are built on the data machine, not by the runner's
monthly job. The runner built them from its restored tables, which lack months the history holds; session 2885 put
the files of 6 November back, demand growth's file (the monthly mark) stayed, and neither page was built again that
month: on 16 November /curtailment's profile read 5 October and /mix/v2 19 October. No request, no model call."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import scheduled  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSteps(unittest.TestCase):
    def test_both_are_steps_of_the_data_machine_and_not_of_the_monthly_job(self):
        for name in ("mix_profile", "curtailment_profile"):
            self.assertIn(name, scheduled.DATA_MACHINE)
            self.assertNotIn(name, scheduled.JOBS)
            self.assertIn(name, scheduled.STEPS)
        loop = [ln for ln in src("warehouse", "run_monthly.sh").splitlines() if ln.startswith("for name in")]
        self.assertEqual(len(loop), 1)
        self.assertNotIn("mix_profile", loop[0])
        self.assertNotIn("curtailment_profile", loop[0])

    def test_the_runner_skips_them_and_builds_nothing(self):
        called = []
        env = dict(os.environ, GITHUB_ACTIONS="true")
        why = scheduled.where(env=env, role="data", held=lambda t: True)
        self.assertIn("GitHub runner", why)
        old = os.environ.get("GITHUB_ACTIONS")
        os.environ["GITHUB_ACTIONS"] = "true"
        try:
            rc = scheduled.step("curtailment_profile", run=lambda *a, **k: called.append(a), restore=lambda t: called.append(t))
        finally:
            if old is None:
                os.environ.pop("GITHUB_ACTIONS", None)
            else:
                os.environ["GITHUB_ACTIONS"] = old
        self.assertEqual(called, [])
        self.assertEqual(rc, 0)

    def test_the_data_machine_builds_tests_puts_back_and_stores_them(self):
        s = src("warehouse", "run_data_machine.sh")
        self.assertIn('soft_step dm_mix_profile "$PYTHON" warehouse/scheduled.py mix_profile', s)
        self.assertIn('soft_step dm_curtailment_profile "$PYTHON" warehouse/scheduled.py curtailment_profile', s)
        self.assertIn('group dm_monthly_profiles "dm_mix_profile dm_curtailment_profile"', s)
        self.assertIn("tests.test_session94 tests.test_session98 tests.test_session133 tests.test_session144_page", s)
        self.assertIn('PROFILES="generation_mix_hourly_profile generation_mix_records caiso_curtailment_profile"', s)
        self.assertIn("site/data/curtailment_profile.json site/data/mix)", s)
        self.assertLess(s.index("dm_monthly_profiles"), s.index("# ---- 4. the commit"))
        if os.name != "nt" or os.path.exists(r"C:\Program Files\Git\bin\bash.exe"):
            bash = r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "bash"
            r = subprocess.run([bash, "-n", os.path.join(ROOT, "warehouse", "run_data_machine.sh")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
