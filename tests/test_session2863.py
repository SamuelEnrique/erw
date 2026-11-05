"""Session 2863: the daily run's merge tests, repaired (5 November 2026).

Energy Research Warehouse (ERW). From 31 October 2026 the daily run stopped at its first step, "merge tests", every day:
tests that held a page file to a dated figure or a fixed count failed once the data machine wrote the files again (the
twelve months rolled on 1 November, node_basis_daily's day-ahead days stopped at 20 October, the hub and CAISO's
curtailment lagged the stopped run). Those tests now hold the files to their rules (test_session144_page,
test_session190_replication, test_session422, test_session701, test_session709; the two siting cards written again).
This file holds the run's own part: a manual run can pull more than three operating days, so the week the run missed is
pulled back while ERCOT's real-time list still keeps it. No request, no model call.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDays(unittest.TestCase):
    def setUp(self):
        self.wf = src(".github", "workflows", "daily-prices.yml")

    def test_a_manual_run_names_its_days_and_the_schedule_keeps_three(self):
        m = re.search(r"\n      days:\n        description: \"([^\"]+)\"\n        required: false\n        default: \"3\"\n", self.wf)
        self.assertIsNotNone(m, "the days input, default 3")
        self.assertIn("DAYS: ${{ github.event.inputs.days || '3' }}", self.wf)
        self.assertNotIn('DAYS: "3"', self.wf)

    def test_the_run_passes_its_days_to_every_iso_connector(self):
        run = src("warehouse", "run_daily.sh")
        self.assertIn('DAYS="${DAYS:-3}"', run)
        self.assertIn('warehouse/connectors/iso_prices.py "$iso" --days "$DAYS"', run)

    def test_the_merge_tests_still_come_first_and_gate_the_lock(self):
        wf = self.wf
        self.assertLess(wf.index("- name: Merge tests"), wf.index("- name: Take the data lock"))
        self.assertIn("if: steps.tests.outputs.status == 'ok' || steps.tests.outputs.status == 'retried'", wf)


class NoTestWasSkipped(unittest.TestCase):
    """The repaired tests keep their assertions; none is skipped or marked an expected failure."""

    def test_no_skip_or_expected_failure_in_the_repaired_tests(self):
        # the skips each file held before session 2863 (a served site, a report not yet written); none was added
        before = {"test_session144_page": 1, "test_session190_replication": 0, "test_session422": 1, "test_session701": 0, "test_session709": 0}
        for name, n in before.items():
            text = src("tests", name + ".py")
            self.assertIn("ession 2863", text, name)
            self.assertNotIn("expectedFailure", text, name)
            self.assertEqual(len(re.findall(r"self\.skipTest\(|@unittest\.skip", text)), n, name)


if __name__ == "__main__":
    unittest.main()
