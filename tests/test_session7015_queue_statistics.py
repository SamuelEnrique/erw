"""Session 7015 (chain 301, done-line requests 16 and 17): the queue statistics. A status with no position is 0 MW, not
"not held" (93 cells of CAISO, ERCOT and SPP read "not held" where the count was 0); the builder can build from the six
queues as the runner last pulled them (rebuilt from the archive), and the data machine runs it weekly. No request, no
model call."""
import os
import sys
import types
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import queue_statistics as qs  # noqa: E402


class ZeroMw(unittest.TestCase):
    def test_a_status_with_no_position_is_zero_mw_and_one_without_figures_is_unwritten(self):
        q = pd.DataFrame(dict(status=["active", "active", "completed"], capacity_mw=["100", "50", ""],
                              queue_date=["2020-01-01"] * 3, actual_in_service_date=["", "", "2022-01-01"]))
        got = qs.stats(q, "caiso")
        self.assertEqual(got["positions_withdrawn"][0], 0.0)
        self.assertEqual(got["mw_withdrawn"], (0.0, "MW"))                 # no position: 0 MW
        self.assertEqual(got["mw_waiting"], (150.0, "MW"))
        self.assertEqual(got["positions_operating"][0], 1.0)
        self.assertNotIn("mw_operating", got)                              # a position with no figure: not written
        self.assertEqual(got["mw_status_not_stated"], (0.0, "MW"))


class Restore(unittest.TestCase):
    def test_each_queue_is_rebuilt_from_the_archive_into_its_own_folder(self):
        calls = []
        out = qs.restore_inputs(run=lambda args, cwd=None: calls.append(args) or types.SimpleNamespace(returncode=0))
        self.assertTrue(out.endswith(os.path.join("runs", "queue_inputs")))
        self.assertEqual([c[2] for c in calls], [f"{iso}_interconnection_queue" for iso in qs.ISOS])
        for c in calls:
            self.assertIn("--from-bucket", c)
            self.assertEqual(c[c.index("--out") + 1], os.path.join(out, c[2] + ".csv"))   # never warehouse/output

    def test_one_that_cannot_be_rebuilt_stops_the_build(self):
        with self.assertRaises(SystemExit):
            qs.restore_inputs(run=lambda args, cwd=None: types.SimpleNamespace(returncode=1))

    def test_the_data_machine_runs_it_weekly_and_loads_it(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine_tables.sh"), encoding="utf-8") as f:
            t = f.read()
        self.assertIn('"dm_queue_statistics|iso_queue_statistics|weekly|warehouse/derived/queue_statistics.py --restore"', t)
        live = [ln for ln in t.splitlines() if ln.startswith("WEEKLY_LIVE=")][0]
        self.assertIn("iso_queue_statistics", live)


if __name__ == "__main__":
    unittest.main()
