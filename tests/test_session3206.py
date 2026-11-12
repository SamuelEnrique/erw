"""Session 3206 (chain 185): the data machine's run puts back a refresh that breaks the replication and cross-check tests.

The run of 6 November 2026 (e475f7069) committed the datacenter and findings files with about four days of new hours.
Four tests that hold those committed files to recorded figures failed on main: test_session190_replication (the
hourly CSV's hub against the page's, one hour apart at the window's end once the hub's October was complete),
test_session1491 (the replication against page_figures.json), test_session538 (the cross-check rows against the
cards) and test_session720 (the siting cards against the tab's figures). Chain 184 put the files back. The run now
holds them in a group: a refresh that fails any of the four is put back whole, as the board's is. Text only: the run
file is read, nothing is run.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUN = os.path.join(ROOT, "warehouse", "run_data_machine.sh")


def text():
    with open(RUN, encoding="utf-8") as f:
        return f.read()


def joined():
    return re.sub(r"\\\n\s*", " ", text())


class TheGroup(unittest.TestCase):
    def test_the_group_names_the_steps_the_tests_and_the_files(self):
        line = next(l for l in joined().split("\n") if l.startswith("group dm_test_replication "))
        steps, tests, paths = re.match(r'group dm_test_replication\s+"([^"]+)"\s+"([^"]+)"\s+--\s+(.+)$', line.strip()).groups()
        # session 3779: the siting cards and the replication's page figures are written from the page's code in the run
        self.assertEqual(steps.split(), ["dm_datacenter_page", "dm_datacenter_export", "dm_datacenter_carbon", "dm_siting_card",
                                         "dm_datacenter_figures", "dm_findings_recompute", "dm_cross_check_rows", "dm_analysis_figures"])
        # session 3803: test 3701 (Research's replication) joined, with the step that writes its page figures
        self.assertEqual(tests.split(), ["tests.test_session190_replication", "tests.test_session1491", "tests.test_session538", "tests.test_session720",
                                         "tests.test_session3701"])
        self.assertEqual(paths.split(), ["site/data/datacenter", "site/public/datacenter", "site/data/findings", "site/public/findings",
                                         "replication/datacenter/page_figures.json", "replication/datacenter/page_figures.csv",
                                         "docs/methods/automated_analysis_findings.md",
                                         "replication/analysis/page_figures.json", "replication/analysis/page_figures.csv"])

    def test_each_step_and_test_exists(self):
        t = text()
        for step in ("dm_datacenter_page", "dm_datacenter_export", "dm_datacenter_carbon", "dm_siting_card", "dm_datacenter_figures",
                     "dm_findings_recompute", "dm_cross_check_rows", "dm_analysis_figures"):
            self.assertRegex(t, rf"soft_step {step} ")
        for mod in ("test_session190_replication", "test_session1491", "test_session538", "test_session720", "test_session3701"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", mod + ".py")), mod)

    def test_the_group_runs_after_its_steps_and_before_the_commit(self):
        t = text()
        at = t.index("group dm_test_replication ")
        for step in ("soft_step dm_datacenter_export ", "soft_step dm_datacenter_carbon ", "soft_step dm_findings_recompute ",
                     "group() {"):
            self.assertLess(t.index(step), at, step)
        self.assertLess(at, t.index("# ---- 4. the commit"))


if __name__ == "__main__":
    unittest.main()
