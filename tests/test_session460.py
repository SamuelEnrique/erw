"""Session 460: warehouse/archive/prove.py judged a copy against the archive's replay, which keeps every key any run ever
wrote. For a table whose keys leave (policy_reads_evidence, price_board_spreads) the replay held rows the latest run no
longer had, the copy read "this machine behind", and session 454 took the replay (5,143 rows against the latest run's
3,362). A copy whose data is the latest run's own, by the run log's data SHA-256, is now equal."""

import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
import prove  # noqa: E402


class LatestRunsOwn(unittest.TestCase):
    def run_prove(self, local_sha, run_sha, local_hashes, archive_hashes):
        with tempfile.TemporaryDirectory() as d:
            out_dir, scratch = os.path.join(d, "output"), os.path.join(d, "scratch")
            os.makedirs(out_dir), os.makedirs(scratch)
            open(os.path.join(out_dir, "t_table.csv"), "w").close()

            def fake_stats(path):
                h = np.array(local_hashes if path.startswith(out_dir) else archive_hashes, dtype=np.uint64)
                return len(h), "2026-10-20T00:00:00Z", h
            run = {"run_id": "20261020T011604Z-github", "archived_at": "2026-10-20T01:16:04Z", "runner": "github",
                   "table_rows": len(local_hashes), "data_sha256": run_sha}
            with mock.patch.object(prove.A, "OUT", out_dir), mock.patch.object(prove, "SCRATCH", scratch), \
                    mock.patch.object(prove, "rebuild_to", return_value=len(local_hashes)), \
                    mock.patch.object(prove, "last_run", return_value=run), \
                    mock.patch.object(prove, "stats", side_effect=fake_stats), \
                    mock.patch.object(prove.A, "data_sha256", return_value=local_sha):
                return prove.prove("t_table", bucket=None)

    def test_the_latest_runs_own_copy_is_equal_though_the_replay_holds_more(self):
        rec = self.run_prove("abc", "abc", [1, 2, 3], [1, 2, 3, 4, 5])
        self.assertEqual(rec["status"], "equal")
        self.assertIn("the latest run's own", rec["cause"])
        self.assertIn("2 rows beyond it", rec["cause"])

    def test_an_older_copy_is_still_behind(self):
        rec = self.run_prove("old", "abc", [1, 2, 3], [1, 2, 3, 4, 5])
        self.assertEqual(rec["status"], "this machine behind")

    def test_a_run_without_a_recorded_sha_is_judged_as_before(self):
        rec = self.run_prove("abc", "", [1, 2, 3], [1, 2, 3, 4])
        self.assertEqual(rec["status"], "this machine behind")

    def test_the_same_rows_are_equal_as_before(self):
        rec = self.run_prove("x", "y", [1, 2, 3], [1, 2, 3])
        self.assertEqual((rec["status"], rec["cause"]), ("equal", ""))


if __name__ == "__main__":
    unittest.main()
