"""Session 284: the tables behind the price board and Supply and trade.

Energy Research Warehouse (ERW). The board's ERCOT rows stood at 7 and 8 October 2026 on 14 October: the runner builds
the board every day but holds ERCOT's rolling window only, and warehouse/derived/page_keep.py keeps a held row that is
longer than the new build's, so no run could move them. The board is now a page file of the data machine's daily run,
which holds the history, gated by the board's Python tests as a group. Held here, with no request and no build: the
step, its place, its group and its paths.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBoardOnTheDataMachine(unittest.TestCase):
    def setUp(self):
        self.text = src("warehouse", "run_data_machine.sh")
        self.body = self.text.split("set -uo pipefail", 1)[1]

    def test_the_step_runs_page_keep_not_the_builder_alone(self):
        self.assertIn('soft_step dm_board_page "$PYTHON" warehouse/derived/page_keep.py board', self.body)
        self.assertNotIn("page_keep.py board --replace", self.body)     # a held row that is newer is never thrown away

    def test_it_runs_after_the_page_files_and_before_the_commit(self):
        b = self.body
        self.assertLess(b.index("soft_step dm_curtailment_worth"), b.index("soft_step dm_board_page"))
        self.assertLess(b.index("soft_step dm_board_page"), b.index("group dm_test_board"))
        self.assertLess(b.index("group dm_test_board"), b.index("# ---- 4. the commit"))

    def test_a_board_its_tests_refuse_is_put_back_whole(self):
        self.assertIn('group dm_test_board "dm_board_page" "tests.test_session132 tests.test_session240" -- site/data/board.json site/public/board',
                      self.body)
        for module in ("test_session132", "test_session240"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", module + ".py")), module)

    def test_the_commit_names_the_board_files_and_no_table(self):
        paths = self.text.split("PAGE_PATHS=(", 1)[1].split(")", 1)[0].split()
        self.assertIn("site/data/board.json", paths)
        self.assertIn("site/public/board", paths)
        self.assertNotIn("warehouse/output", " ".join(paths))

    def test_the_runner_still_builds_it_and_no_em_dash(self):
        self.assertIn('run_other board "$PYTHON" warehouse/health.py run --step "board" -- bash warehouse/refresh_board.sh', src("warehouse", "run_daily.sh"))
        self.assertIn("page_keep.py board", src("warehouse", "refresh_board.sh"))
        self.assertNotIn(EM, self.text)
        self.assertNotIn(EM, src("tests", "test_session284.py"))


if __name__ == "__main__":
    unittest.main()
