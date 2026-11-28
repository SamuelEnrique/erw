"""Session 11200 (chain 760, part E): the large-load research tables name their run log in their header.

The package test (package/tests/test_erw.py, events provenance) failed in GitHub's daily run of 27 November on
utility_large_load_rule_changes: its header had no "Run log:" line, though the connector writes one each run.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_research as llr  # noqa: E402


class TheRunLog(unittest.TestCase):
    def test_every_kind_names_its_run_log(self):
        for kind in llr.NAMES:
            if kind not in llr.WHAT:
                continue
            lines = llr.header(kind, [], [], "20261128T120000Z")
            logs = [ln for ln in lines if ln.startswith("Run log: ")]
            self.assertEqual(logs, ["Run log: warehouse/output/logs/large_load_research_20261128T120000Z.log"], kind)


if __name__ == "__main__":
    unittest.main()
