"""Session 3757 (chain 211): the daily run's failing connectors.

ercot_as_prices under ruling 2 of 6 November 2026 (docs/state/rulings_2026-11-06.md): no request to ERCOT's /misapp or
/misdownload paths. The connector keeps the table it holds, rebuilt from the ERW's own archive when the machine has none,
and exits as a skip whose reason says "stale at source" and names the ruling (warehouse/health.py counts such a skip as
stale, not as a failure). No network: the archive's restore and the request are stood in for.

eia930: every BA's demand table is checked per UTC day. On 5 November 2026 EIA held no day-ahead forecast for CISO and
PJM on 1 November, and the whole-window rule failed both tables every run; now the day is a gap and the others are
written.
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import eia930  # noqa: E402
import ercot_as_prices as ap  # noqa: E402
import pandas as pd  # noqa: E402
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


class EveryDemandTablePerDay(unittest.TestCase):
    def test_every_ba_demand_is_per_day(self):
        for code in eia930.BAS:
            self.assertIn(f"eia930_{code}_demand", eia930.PER_DAY)
            self.assertIn(f"eia930_{code}_generation", eia930.PER_DAY)

    def test_a_day_without_its_forecast_is_a_gap_and_the_others_are_written(self):
        start = pd.Timestamp("2026-10-31T00:00:00Z")
        hours = pd.date_range(start, periods=72, freq="1h")
        rows = []
        for t in hours:
            rows.append(dict(variable="demand_mw", interval_start=t, value=30000.0))
            if t.date().isoformat() != "2026-11-01":
                rows.append(dict(variable="demand_forecast_mw", interval_start=t, value=31000.0))
        df = pd.DataFrame(rows)
        df["source"], df["source_url"], df["retrieved_at"] = "eia:electricity/rto/region-data", "https://api.eia.gov/", "2026-11-05T23:03:17Z"
        logged = []
        dropped, gaps = eia930.build_table(df, "ciso", start, start + pd.Timedelta(days=3), logged.append, "eia930_ciso_demand",
                                           "test", "20261105T230317Z", 3, write=False)
        self.assertEqual(dropped, [])
        self.assertEqual([d for d, _ in gaps], ["2026-11-01"])
        self.assertIn("demand_forecast_mw: 0 of 24 hours", gaps[0][1])


if __name__ == "__main__":
    unittest.main()
