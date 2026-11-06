"""Session 2927 (chain 153): the monthly builds' page files held to their own tests, as session 2913 holds the board's.

Energy Research Warehouse (ERW). On 6 November 2026 the runner's catch-up run (run 42120465428) rebuilt site/data/mix/
and site/data/curtailment_profile.json from tables shorter than the history and committed them (CAISO's mix lost 2019
and 2020); chain 147's session 2885 put them back. warehouse/run_monthly.sh now runs the tests of the mix and curtailment
pages (sessions 94, 98, 133, 144) right after its builders and puts those files back as committed when they fail.
Session 2927 ran the four tests on the runner's thinned files of 6 November: 3 failures and 1 error, so the guard would
have refused them. No request, no model call.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheMonthlyPageFiles(unittest.TestCase):
    def setUp(self):
        self.run = src("warehouse", "run_monthly.sh")

    def test_the_tests_follow_the_builders(self):
        loop = self.run.index('soft_step "$name" "$PYTHON" warehouse/scheduled.py "$name"')
        tests = self.run.index("tests.test_session94 tests.test_session98 tests.test_session133 tests.test_session144_page")
        self.assertLess(loop, tests)
        self.assertLess(tests, self.run.index('echo "== monthly builds done"'))

    def test_refused_files_are_put_back_and_recorded(self):
        block = self.run[self.run.index('MONTHLY_PAGE_PATHS="site/data/mix site/data/curtailment_profile.json"'):]
        block = block[:block.index("\nfi\n") + 4]
        self.assertIn("git checkout -- $MONTHLY_PAGE_PATHS", block)
        self.assertIn("git clean -fdq -- site/data/mix", block)
        self.assertIn('--step "monthly_page_tests" --status failed', block)
        self.assertIn('echo "monthly_page_tests ok" >> "$status"', block)
        self.assertNotIn("exit", block)          # the run goes on

    def test_the_daily_run_starts_the_monthly_job(self):
        self.assertIn("bash warehouse/run_monthly.sh", src("warehouse", "run_daily.sh"))

    def test_the_tests_named_exist(self):
        for t in ("94", "98", "133", "144_page"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", f"test_session{t}.py")), t)


if __name__ == "__main__":
    unittest.main()
