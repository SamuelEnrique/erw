"""Session 2913 (chain 151): the runner's board is held to the board's own tests, as the data machine's is.

Energy Research Warehouse (ERW). On 6 November 2026 the daily run's catch-up (run 42120465428) committed a board that
failed tests 1118 and 1139; the next run's merge tests would have stopped it, as they stopped every run from 31 October.
warehouse/run_daily.sh now runs the board's tests right after the board step and puts the board's files back as
committed when they fail, as warehouse/run_data_machine.sh does (dm_test_board). No request, no model call.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRunnersBoard(unittest.TestCase):
    def setUp(self):
        self.run = src("warehouse", "run_daily.sh")

    def test_the_tests_follow_the_board_step(self):
        step = self.run.index('run_other board "$PYTHON" warehouse/health.py run --step "board" -- bash warehouse/refresh_board.sh')
        tests = self.run.index("tests.test_session132 tests.test_session240 tests.test_session1118 tests.test_session1139")
        self.assertLess(step, tests)
        self.assertLess(tests, self.run.index("echo \"== connector status\""))

    def test_a_refused_board_is_put_back_and_recorded(self):
        block = self.run[self.run.index('BOARD_PATHS="site/data/board.json site/public/board"'):]
        block = block[:block.index("\nfi\n")]
        self.assertIn("git checkout -- $BOARD_PATHS", block)
        self.assertIn("git clean -fdq -- site/public/board", block)
        self.assertIn('--step "board_tests" --status failed', block)
        self.assertIn("|| true", block)

    def test_the_four_test_files_exist(self):
        for n in ("132", "240", "1118", "1139"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", f"test_session{n}.py")), n)


if __name__ == "__main__":
    unittest.main()
