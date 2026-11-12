"""Session 3757 (chain 211): the daily run's failing connectors.

ercot_as_prices under ruling 2 of 6 November 2026 (docs/state/rulings_2026-11-06.md): no request to ERCOT's /misapp or
/misdownload paths. The connector keeps the table it holds, rebuilt from the ERW's own archive when the machine has none,
and exits as a skip whose reason says "stale at source" and names the ruling (warehouse/health.py counts such a skip as
stale, not as a failure). No network: the archive's restore and the request are stood in for.
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import ercot_as_prices as ap  # noqa: E402
import health  # noqa: E402

CSV = "# Energy Research Warehouse (ERW): test\nentity,variable,ts_utc,value\nercot:RRS,mcpc_dam,2026-11-04T05:00:00Z,1.5\nercot:RRS,mcpc_dam,2026-11-05T05:00:00Z,2.5\n"


class UnderRulingTwo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = mock.patch.object(ap.ip, "OUT_DIR", self.tmp.name)
        self.patch.start()
        self.env = mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.patch.stop()
        self.tmp.cleanup()

    def write(self):
        with open(os.path.join(self.tmp.name, "ercot_as_prices.csv"), "w", encoding="utf-8") as f:
            f.write(CSV)
        return True

    def test_the_run_asks_ercot_for_nothing_and_skips_as_stale(self):
        self.write()
        with mock.patch.object(ap, "pull", side_effect=AssertionError("a request was made")), \
                mock.patch("sys.stdout.write") as out:
            code = ap.main([])
        self.assertEqual(code, 75)
        said = "".join(c.args[0] for c in out.call_args_list)
        self.assertIn("SKIPPED: stale at source", said)
        self.assertIn("ruling 2 of 6 November 2026", said)
        self.assertIn("newest hour 2026-11-05T05:00:00Z", said)
        self.assertTrue(health.STALE_MARK in said.lower())

    def test_an_absent_table_is_rebuilt_from_the_archive(self):
        path, newest = ap.held(restore=self.write)
        self.assertTrue(path.endswith("ercot_as_prices.csv"))
        self.assertEqual(newest, "2026-11-05T05:00:00Z")

    def test_no_table_anywhere_is_a_failure(self):
        with mock.patch("sys.stdout.write"):
            self.assertEqual(ap.keep_held(restore=lambda: False), 1)


if __name__ == "__main__":
    unittest.main()
